"""Load scripture hierarchy into Neo4j (P6 Phase 6).

Core logic extracted from scripts/load_hierarchy_neo4j.py for pipeline integration.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_local_data = Path(__file__).resolve().parent.parent.parent.parent / "data" / "scripture_structure"
_container_data = Path("/app/data/scripture_structure")
DATA_DIR = _container_data if _container_data.exists() else _local_data


def _load_json(name: str) -> list[dict]:
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def load_hierarchy(driver, corpus_path: Path | None = None) -> dict[str, int]:
    """Load scripture hierarchy into Neo4j using an existing driver.

    Returns counts dict.
    """
    volumes = _load_json("volumes.json")
    divisions = _load_json("divisions.json")
    books = _load_json("books.json")
    parts = _load_json("parts.json")
    chapters = _load_json("chapters.json")

    div_by_name = {(d["volume_slug"], d["name_es"]): d for d in divisions}
    counts = {"volumes": 0, "divisions": 0, "books": 0, "parts": 0,
              "chapters": 0, "contains": 0, "next_prev": 0, "chapter_meta": 0}

    with driver.session() as session:
        # Schema
        for label in ("Volume", "Division", "Book", "Part", "Chapter"):
            session.run(
                f"CREATE CONSTRAINT {label.lower()}_unique IF NOT EXISTS "
                f"FOR (n:{label}) REQUIRE n.slug IS UNIQUE"
            )

        # Volumes
        for v in volumes:
            session.run(
                "MERGE (n:Volume {slug: $slug}) "
                "SET n.name_en = $name_en, n.name_es = $name_es, "
                "    n.abbreviation_en = $abbr_en, n.abbreviation_es = $abbr_es",
                slug=v["slug"], name_en=v["name_en"], name_es=v["name_es"],
                abbr_en=v.get("abbreviation_en", ""), abbr_es=v.get("abbreviation_es", ""),
            )
            counts["volumes"] += 1

        # Divisions
        for d in divisions:
            slug = f"{d['volume_slug']}/{d['name_en'].lower().replace(' ', '-').replace('(', '').replace(')', '')}"
            session.run(
                "MERGE (n:Division {slug: $slug}) "
                "SET n.name_en = $name_en, n.name_es = $name_es, n.volume_slug = $vol",
                slug=slug, name_en=d["name_en"], name_es=d["name_es"], vol=d["volume_slug"],
            )
            session.run(
                "MATCH (v:Volume {slug: $vol}) "
                "MATCH (d:Division {slug: $slug}) "
                "MERGE (v)-[:CONTAINS]->(d)",
                vol=d["volume_slug"], slug=slug,
            )
            counts["divisions"] += 1
            counts["contains"] += 1

        # Books
        for b in books:
            slug = f"{b['volume_slug']}/{b['book_slug']}"
            div_slug = None
            if b.get("division_name_es"):
                div_key = (b["volume_slug"], b["division_name_es"])
                if div_key in div_by_name:
                    d = div_by_name[div_key]
                    div_slug = f"{d['volume_slug']}/{d['name_en'].lower().replace(' ', '-').replace('(', '').replace(')', '')}"

            session.run(
                "MERGE (n:Book {slug: $slug}) "
                "SET n.name_en = $name_en, n.name_es = $name_es, "
                "    n.abbreviation_en = $abbr_en, n.abbreviation_es = $abbr_es, "
                "    n.volume_slug = $vol, n.book_slug = $book_slug",
                slug=slug, name_en=b["name_en"], name_es=b["name_es"],
                abbr_en=b.get("abbreviation_en", ""), abbr_es=b.get("abbreviation_es", ""),
                vol=b["volume_slug"], book_slug=b["book_slug"],
            )

            if div_slug:
                session.run(
                    "MATCH (d:Division {slug: $div_slug}) "
                    "MATCH (b:Book {slug: $slug}) "
                    "MERGE (d)-[:CONTAINS]->(b)",
                    div_slug=div_slug, slug=slug,
                )
            else:
                session.run(
                    "MATCH (v:Volume {slug: $vol}) "
                    "MATCH (b:Book {slug: $slug}) "
                    "MERGE (v)-[:CONTAINS]->(b)",
                    vol=b["volume_slug"], slug=slug,
                )
            counts["books"] += 1
            counts["contains"] += 1

        # Parts
        part_slugs = {}
        for p in parts:
            slug = f"{p['volume_slug']}/{p['book_slug']}/part-{p.get('mysql_id', p.get('order', 0))}"
            part_slugs[p.get("mysql_id")] = slug

            session.run(
                "MERGE (n:Part {slug: $slug}) "
                "SET n.name_en = $name_en, n.name_es = $name_es, "
                "    n.volume_slug = $vol, n.book_slug = $book_slug",
                slug=slug, name_en=p.get("name_en", ""), name_es=p.get("name_es", ""),
                vol=p["volume_slug"], book_slug=p["book_slug"],
            )

            book_slug = f"{p['volume_slug']}/{p['book_slug']}"
            session.run(
                "MATCH (b:Book {slug: $book_slug}) "
                "MATCH (p:Part {slug: $slug}) "
                "MERGE (b)-[:CONTAINS]->(p)",
                book_slug=book_slug, slug=slug,
            )
            counts["parts"] += 1
            counts["contains"] += 1

        # Chapters
        chapters_by_book: dict[str, list[dict]] = {}
        for ch in chapters:
            key = f"{ch['volume_slug']}/{ch['book_slug']}"
            chapters_by_book.setdefault(key, []).append(ch)

        for book_key, book_chapters in chapters_by_book.items():
            book_chapters.sort(key=lambda c: c["chapter_num"])

            for i, ch in enumerate(book_chapters):
                if not ch.get("corpus_path"):
                    continue
                slug = ch["corpus_path"].replace(".txt", "")
                session.run(
                    "MERGE (n:Chapter {slug: $slug}) "
                    "SET n.chapter_num = $num, n.reference_en = $ref_en, "
                    "    n.reference_es = $ref_es, n.chapter_type = $ctype, "
                    "    n.volume_slug = $vol, n.book_slug = $book_slug, "
                    "    n.corpus_path = $corpus_path, "
                    "    n.part_name_en = $part_en, n.part_name_es = $part_es",
                    slug=slug, num=ch["chapter_num"],
                    ref_en=ch.get("reference_en", ""), ref_es=ch.get("reference_es", ""),
                    ctype=ch.get("chapter_type", "standard"),
                    vol=ch["volume_slug"], book_slug=ch["book_slug"],
                    corpus_path=ch["corpus_path"],
                    part_en=ch.get("part_name_en", ""), part_es=ch.get("part_name_es", ""),
                )
                counts["chapters"] += 1

                if ch.get("part_mysql_id") and ch["part_mysql_id"] in part_slugs:
                    session.run(
                        "MATCH (p:Part {slug: $part_slug}) "
                        "MATCH (c:Chapter {slug: $slug}) "
                        "MERGE (p)-[:CONTAINS]->(c)",
                        part_slug=part_slugs[ch["part_mysql_id"]], slug=slug,
                    )
                else:
                    session.run(
                        "MATCH (b:Book {slug: $book_key}) "
                        "MATCH (c:Chapter {slug: $slug}) "
                        "MERGE (b)-[:CONTAINS]->(c)",
                        book_key=book_key, slug=slug,
                    )
                counts["contains"] += 1

                for lang in ("en", "es"):
                    fp = f"{lang}/scriptures/{ch['corpus_path']}"
                    session.run(
                        "MATCH (c:Chapter {slug: $slug}) "
                        "MATCH (d:Document {file_path: $fp}) "
                        "MERGE (c)-[:HAS_DOCUMENT]->(d)",
                        slug=slug, fp=fp,
                    )

                if i > 0 and book_chapters[i - 1].get("corpus_path"):
                    prev_slug = book_chapters[i - 1]["corpus_path"].replace(".txt", "")
                    session.run(
                        "MATCH (prev:Chapter {slug: $prev_slug}) "
                        "MATCH (curr:Chapter {slug: $slug}) "
                        "MERGE (prev)-[:NEXT]->(curr) "
                        "MERGE (curr)-[:PREVIOUS]->(prev)",
                        prev_slug=prev_slug, slug=slug,
                    )
                    counts["next_prev"] += 1

        # Load .meta.json onto Chapter nodes
        _local_corpus = Path(__file__).resolve().parent.parent.parent.parent / "corpus"
        _container_corpus = Path("/app/corpus")
        corpus_root = corpus_path or (_container_corpus if _container_corpus.exists() else _local_corpus)

        for ch in chapters:
            if not ch.get("corpus_path"):
                continue
            slug = ch["corpus_path"].replace(".txt", "")
            for lang in ("en", "es"):
                meta_path = corpus_root / lang / "scriptures" / ch["corpus_path"].replace(".txt", ".meta.json")
                if not meta_path.exists():
                    continue
                try:
                    with open(meta_path, encoding="utf-8") as f:
                        meta = json.load(f)
                except (json.JSONDecodeError, OSError):
                    continue

                props = {}
                for field in ("summary", "study_intro", "subtitle", "source_url"):
                    val = meta.get("metadata", {}).get(field) or meta.get(field)
                    if val:
                        props[f"{field}_{lang}"] = val

                headings = meta.get("metadata", {}).get("section_headings") or meta.get("section_headings")
                if headings:
                    props[f"section_headings_{lang}"] = json.dumps(headings, ensure_ascii=False)

                if props:
                    session.run(
                        "MATCH (c:Chapter {slug: $slug}) SET c += $props",
                        slug=slug, props=props,
                    )
                    counts["chapter_meta"] += 1

    logger.info(
        "Hierarchy loaded: %d vol, %d div, %d books, %d parts, %d chapters, "
        "%d contains, %d next/prev, %d meta",
        counts["volumes"], counts["divisions"], counts["books"], counts["parts"],
        counts["chapters"], counts["contains"], counts["next_prev"], counts["chapter_meta"],
    )
    return counts
