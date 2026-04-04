"""Load scripture cross-references into Neo4j (P6 Phase 8).

Core logic extracted from scripts/load_cross_refs_neo4j.py for pipeline integration.
Creates ScriptureVerse nodes and CROSS_REF relationships from cross_references.json.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
XREF_PATH = PROJECT_ROOT / "data" / "scripture_structure" / "cross_references.json"

VOLUME_NAMES = {
    "ot": "Old Testament",
    "nt": "New Testament",
    "bom": "Book of Mormon",
    "dc": "Doctrine and Covenants",
    "pgp": "Pearl of Great Price",
}

BATCH_SIZE = 5000


def _parse_canonical_key(key: str) -> dict:
    """Parse 'volume/book/chapter:verse[-end]' into components."""
    if ":" in key:
        path_part, verse_part = key.rsplit(":", 1)
    else:
        path_part = key
        verse_part = "0"

    parts = path_part.split("/")
    volume = parts[0] if parts else ""
    book = parts[1] if len(parts) > 1 else ""
    chapter = parts[2] if len(parts) > 2 else ""

    if "-" in verse_part:
        vs, ve = verse_part.split("-", 1)
        verse_start = int(vs)
        verse_end = int(ve)
    else:
        verse_start = int(verse_part)
        verse_end = verse_start

    return {
        "volume": volume,
        "book": book,
        "chapter": int(chapter) if chapter.isdigit() else 0,
        "verse_start": verse_start,
        "verse_end": verse_end,
    }


def load_cross_refs(driver) -> dict[str, int]:
    """Load scripture cross-references into Neo4j using an existing driver.

    Reads cross_references.json and creates:
      - ScriptureVerse nodes (canonical_key as unique ID)
      - CROSS_REF relationships between verses
      - IN_CHAPTER links from verses to Document nodes

    Returns counts dict: {verse_nodes, relationships, doc_links}.
    """
    counts: dict[str, int] = {"verse_nodes": 0, "relationships": 0, "doc_links": 0}

    if not XREF_PATH.exists():
        logger.warning("Cross-references file not found: %s", XREF_PATH)
        return counts

    logger.info("Loading cross-references from %s ...", XREF_PATH.name)
    with open(XREF_PATH, encoding="utf-8") as f:
        data = json.load(f)

    refs = data["references"]
    stats = data.get("stats", {})
    logger.info(
        "  %d references to load (lang split: %s)",
        len(refs),
        stats.get("per_lang", "unknown"),
    )

    # --- Indexes and constraints ---
    with driver.session() as session:
        session.run(
            "CREATE CONSTRAINT sv_unique IF NOT EXISTS "
            "FOR (v:ScriptureVerse) REQUIRE v.canonical_key IS UNIQUE"
        )
        session.run(
            "CREATE INDEX sv_volume_idx IF NOT EXISTS "
            "FOR (v:ScriptureVerse) ON (v.volume)"
        )
        session.run(
            "CREATE INDEX sv_book_idx IF NOT EXISTS "
            "FOR (v:ScriptureVerse) ON (v.book)"
        )
        session.run(
            "CREATE INDEX sv_chapter_idx IF NOT EXISTS "
            "FOR (v:ScriptureVerse) ON (v.chapter_key)"
        )

    # --- Collect unique verse keys ---
    verse_keys: set[str] = set()
    for ref in refs:
        verse_keys.add(ref["source"])
        verse_keys.add(ref["target"])

    verse_list = list(verse_keys)
    logger.info("  Creating %d ScriptureVerse nodes ...", len(verse_list))

    # --- Batch create verse nodes ---
    t0 = time.time()
    for i in range(0, len(verse_list), BATCH_SIZE):
        batch = verse_list[i : i + BATCH_SIZE]
        nodes = []
        for key in batch:
            parsed = _parse_canonical_key(key)
            nodes.append(
                {
                    "canonical_key": key,
                    "volume": parsed["volume"],
                    "volume_name": VOLUME_NAMES.get(parsed["volume"], parsed["volume"]),
                    "book": parsed["book"],
                    "chapter": parsed["chapter"],
                    "chapter_key": f"{parsed['volume']}/{parsed['book']}/{parsed['chapter']}",
                    "verse_start": parsed["verse_start"],
                    "verse_end": parsed["verse_end"],
                }
            )

        with driver.session() as session:
            session.run(
                "UNWIND $nodes AS n "
                "MERGE (v:ScriptureVerse {canonical_key: n.canonical_key}) "
                "SET v.volume = n.volume, "
                "    v.volume_name = n.volume_name, "
                "    v.book = n.book, "
                "    v.chapter = n.chapter, "
                "    v.chapter_key = n.chapter_key, "
                "    v.verse_start = n.verse_start, "
                "    v.verse_end = n.verse_end",
                nodes=nodes,
            )

        if (i // BATCH_SIZE) % 10 == 0:
            elapsed = time.time() - t0
            logger.info(
                "    [%d/%d] %.1fs", i + len(batch), len(verse_list), elapsed
            )

    counts["verse_nodes"] = len(verse_list)
    logger.info("  Verse nodes created in %.1fs", time.time() - t0)

    # --- Batch create relationships ---
    logger.info("  Creating %d CROSS_REF relationships ...", len(refs))
    t0 = time.time()

    for i in range(0, len(refs), BATCH_SIZE):
        batch = refs[i : i + BATCH_SIZE]
        edges = [
            {
                "source": ref["source"],
                "target": ref["target"],
                "direction": ref["direction"],
                "lang": ref["lang"],
                "footnote_id": ref["footnote_id"],
                "has_reciprocal": ref["has_reciprocal"],
            }
            for ref in batch
        ]

        with driver.session() as session:
            session.run(
                "UNWIND $edges AS e "
                "MATCH (src:ScriptureVerse {canonical_key: e.source}) "
                "MATCH (tgt:ScriptureVerse {canonical_key: e.target}) "
                "MERGE (src)-[r:CROSS_REF]->(tgt) "
                "SET r.direction = e.direction, "
                "    r.lang = e.lang, "
                "    r.footnote_id = e.footnote_id, "
                "    r.has_reciprocal = e.has_reciprocal",
                edges=edges,
            )

        if (i // BATCH_SIZE) % 10 == 0:
            elapsed = time.time() - t0
            logger.info("    [%d/%d] %.1fs", i + len(batch), len(refs), elapsed)

    counts["relationships"] = len(refs)
    logger.info("  Relationships created in %.1fs", time.time() - t0)

    # --- Link ScriptureVerse nodes to Document nodes ---
    logger.info("  Linking verses to Document nodes ...")
    with driver.session() as session:
        result = session.run(
            "MATCH (v:ScriptureVerse) "
            "WITH DISTINCT v.chapter_key AS ck "
            "MATCH (d:Document) "
            "WHERE d.file_path CONTAINS ck "
            "MATCH (v2:ScriptureVerse {chapter_key: ck}) "
            "MERGE (v2)-[:IN_CHAPTER]->(d) "
            "RETURN count(*) AS linked"
        )
        linked = result.single()["linked"]
        counts["doc_links"] = linked

    # --- Final verification ---
    with driver.session() as session:
        verse_count = session.run(
            "MATCH (v:ScriptureVerse) RETURN count(v) AS c"
        ).single()["c"]
        rel_count = session.run(
            "MATCH ()-[r:CROSS_REF]->() RETURN count(r) AS c"
        ).single()["c"]

    logger.info(
        "Cross-references loaded: %d verse nodes, %d relationships, %d doc links",
        verse_count,
        rel_count,
        counts["doc_links"],
    )
    return counts
