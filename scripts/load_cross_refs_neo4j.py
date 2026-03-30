"""P2 Phase 3 — Load scripture cross-references into Neo4j knowledge graph.

Reads cross_references.json and creates:
  - ScriptureVerse nodes (canonical_key as unique ID)
  - CROSS_REF relationships between verses (with direction, lang, footnote metadata)

Prerequisites:
  - Neo4j running (docker compose up neo4j)
  - cross_references.json exists (run parse_cross_references.py first)

Usage:
  python scripts/load_cross_refs_neo4j.py [--uri bolt://localhost:7687] [--batch-size 1000] [--dry-run]
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
XREF_PATH = PROJECT_ROOT / "data" / "scripture_structure" / "cross_references.json"

# Volume display names for node properties
VOLUME_NAMES = {
    "ot": "Old Testament",
    "nt": "New Testament",
    "bom": "Book of Mormon",
    "dc": "Doctrine and Covenants",
    "pgp": "Pearl of Great Price",
}


def _parse_canonical_key(key: str) -> dict:
    """Parse 'volume/book/chapter:verse[-end]' into components."""
    # Split chapter:verse from path
    if ":" in key:
        path_part, verse_part = key.rsplit(":", 1)
    else:
        path_part = key
        verse_part = "0"

    parts = path_part.split("/")
    volume = parts[0] if parts else ""
    book = parts[1] if len(parts) > 1 else ""
    chapter = parts[2] if len(parts) > 2 else ""

    # Parse verse range
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


def load_to_neo4j(
    uri: str = "bolt://localhost:7687",
    user: str = "neo4j",
    password: str = "alejandria",
    batch_size: int = 500,
    dry_run: bool = False,
):
    """Load cross-references into Neo4j."""
    # Load data
    print(f"Loading cross-references from {XREF_PATH.name}...")
    with open(XREF_PATH, encoding="utf-8") as f:
        data = json.load(f)

    refs = data["references"]
    stats = data["stats"]
    print(f"  {len(refs)} references to load")
    print(f"  Stats: {json.dumps(stats, indent=2)}")

    if dry_run:
        # Just report what would be done
        verse_keys = set()
        for ref in refs:
            verse_keys.add(ref["source"])
            verse_keys.add(ref["target"])
        print(f"\n  [DRY RUN]")
        print(f"  Would create {len(verse_keys)} ScriptureVerse nodes")
        print(f"  Would create {len(refs)} CROSS_REF relationships")
        return

    # Connect to Neo4j
    from neo4j import GraphDatabase
    print(f"\nConnecting to Neo4j at {uri}...")
    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        with driver.session() as session:
            # Verify connection
            result = session.run("RETURN 1 AS n")
            result.single()
            print("  Connected successfully")

            # Create indexes and constraints
            print("  Creating indexes...")
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

        # Collect unique verse keys
        verse_keys = set()
        for ref in refs:
            verse_keys.add(ref["source"])
            verse_keys.add(ref["target"])

        print(f"\n  Creating {len(verse_keys)} ScriptureVerse nodes...")
        verse_list = list(verse_keys)

        # Batch create verse nodes
        t0 = time.time()
        for i in range(0, len(verse_list), batch_size):
            batch = verse_list[i:i + batch_size]
            nodes = []
            for key in batch:
                parsed = _parse_canonical_key(key)
                nodes.append({
                    "canonical_key": key,
                    "volume": parsed["volume"],
                    "volume_name": VOLUME_NAMES.get(parsed["volume"], parsed["volume"]),
                    "book": parsed["book"],
                    "chapter": parsed["chapter"],
                    "chapter_key": f"{parsed['volume']}/{parsed['book']}/{parsed['chapter']}",
                    "verse_start": parsed["verse_start"],
                    "verse_end": parsed["verse_end"],
                })

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

            if (i // batch_size) % 10 == 0:
                elapsed = time.time() - t0
                print(f"    [{i + len(batch)}/{len(verse_list)}] {elapsed:.1f}s")

        elapsed = time.time() - t0
        print(f"  Verse nodes created in {elapsed:.1f}s")

        # Batch create relationships
        print(f"\n  Creating {len(refs)} CROSS_REF relationships...")
        t0 = time.time()

        for i in range(0, len(refs), batch_size):
            batch = refs[i:i + batch_size]
            edges = []
            for ref in batch:
                edges.append({
                    "source": ref["source"],
                    "target": ref["target"],
                    "direction": ref["direction"],
                    "lang": ref["lang"],
                    "footnote_id": ref["footnote_id"],
                    "has_reciprocal": ref["has_reciprocal"],
                })

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

            if (i // batch_size) % 10 == 0:
                elapsed = time.time() - t0
                print(f"    [{i + len(batch)}/{len(refs)}] {elapsed:.1f}s")

        elapsed = time.time() - t0
        print(f"  Relationships created in {elapsed:.1f}s")

        # Link ScriptureVerse nodes to Document nodes (if they exist)
        print("\n  Linking verses to Document nodes...")
        with driver.session() as session:
            # For each chapter_key, link verse nodes to the corresponding Document
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
            print(f"  Linked {linked} verse-document connections")

        # Final stats
        with driver.session() as session:
            verse_count = session.run(
                "MATCH (v:ScriptureVerse) RETURN count(v) AS c"
            ).single()["c"]
            rel_count = session.run(
                "MATCH ()-[r:CROSS_REF]->() RETURN count(r) AS c"
            ).single()["c"]

        print(f"\n{'='*60}")
        print("Neo4j Cross-Reference Load Complete")
        print(f"{'='*60}")
        print(f"  ScriptureVerse nodes: {verse_count}")
        print(f"  CROSS_REF relationships: {rel_count}")
        print(f"{'='*60}")

    finally:
        driver.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Load cross-references into Neo4j")
    parser.add_argument("--uri", default="bolt://localhost:7687",
                        help="Neo4j bolt URI (default: bolt://localhost:7687)")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="alejandria")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be done without connecting to Neo4j")
    args = parser.parse_args()

    load_to_neo4j(
        uri=args.uri,
        user=args.user,
        password=args.password,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
