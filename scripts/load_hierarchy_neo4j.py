#!/usr/bin/env python3
"""P6 Phase 6 -- Load scripture hierarchy into Neo4j knowledge graph.

Reads volumes.json, divisions.json, books.json, parts.json, chapters.json
and creates a full hierarchy in Neo4j:

  Volume -> Division -> Book -> Part -> Chapter

With CONTAINS / PART_OF relations and NEXT/PREVIOUS sequential navigation.

Usage:
  python scripts/load_hierarchy_neo4j.py [--dry-run] [--uri bolt://neo4j:7687]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Try both local and container paths
_local_data = Path(__file__).resolve().parent.parent / "data" / "scripture_structure"
_container_data = Path("/app/data/scripture_structure")
DATA_DIR = _container_data if _container_data.exists() else _local_data


def load_json(name: str) -> list[dict]:
    path = DATA_DIR / name
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dry_run_report() -> None:
    volumes = load_json("volumes.json")
    divisions = load_json("divisions.json")
    books = load_json("books.json")
    parts = load_json("parts.json")
    chapters = load_json("chapters.json")

    print(f"  Volumes: {len(volumes)}")
    print(f"  Divisions: {len(divisions)}")
    print(f"  Books: {len(books)}")
    print(f"  Parts: {len(parts)}")
    print(f"  Chapters: {len(chapters)}")

    for v in volumes:
        div_count = sum(1 for d in divisions if d["volume_slug"] == v["slug"])
        book_count = sum(1 for b in books if b["volume_slug"] == v["slug"])
        ch_count = sum(1 for c in chapters if c["volume_slug"] == v["slug"])
        print(f"    {v['name_en']}: {div_count} divisions, {book_count} books, {ch_count} chapters")

    # Count NEXT/PREVIOUS pairs
    prev_ch = {}
    for ch in chapters:
        key = (ch["volume_slug"], ch["book_slug"])
        if key in prev_ch:
            pass  # would create NEXT/PREVIOUS
        prev_ch[key] = ch
    print(f"\n  NEXT/PREVIOUS pairs: ~{len(chapters) - len(set((c['volume_slug'], c['book_slug']) for c in chapters))}")


def load_to_neo4j(uri: str, user: str, password: str) -> dict:
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(user, password))
    counts = {"volumes": 0, "divisions": 0, "books": 0, "parts": 0, "chapters": 0,
              "contains": 0, "next_prev": 0, "chapter_meta": 0}

    volumes = load_json("volumes.json")
    divisions = load_json("divisions.json")
    books = load_json("books.json")
    parts = load_json("parts.json")
    chapters = load_json("chapters.json")

    # Build lookups
    div_by_name = {(d["volume_slug"], d["name_es"]): d for d in divisions}
    book_by_key = {(b["volume_slug"], b["book_slug"]): b for b in books}

    with driver.session() as session:
        # --- Schema ---
        for label in ("Volume", "Division", "Book", "Part", "Chapter"):
            session.run(
                f"CREATE CONSTRAINT {label.lower()}_unique IF NOT EXISTS "
                f"FOR (n:{label}) REQUIRE n.slug IS UNIQUE"
            )

        # --- Volumes ---
        for v in volumes:
            session.run(
                "MERGE (n:Volume {slug: $slug}) "
                "SET n.name_en = $name_en, n.name_es = $name_es, "
                "    n.abbreviation_en = $abbr_en, n.abbreviation_es = $abbr_es",
                slug=v["slug"], name_en=v["name_en"], name_es=v["name_es"],
                abbr_en=v.get("abbreviation_en", ""), abbr_es=v.get("abbreviation_es", ""),
            )
            counts["volumes"] += 1

        # --- Divisions ---
        for d in divisions:
            slug = f"{d['volume_slug']}/{d['name_en'].lower().replace(' ', '-').replace('(', '').replace(')', '')}"
            session.run(
                "MERGE (n:Division {slug: $slug}) "
                "SET n.name_en = $name_en, n.name_es = $name_es, n.volume_slug = $vol",
                slug=slug, name_en=d["name_en"], name_es=d["name_es"], vol=d["volume_slug"],
            )
            # Volume CONTAINS Division
            session.run(
                "MATCH (v:Volume {slug: $vol}) "
                "MATCH (d:Division {slug: $slug}) "
                "MERGE (v)-[:CONTAINS]->(d)",
                vol=d["volume_slug"], slug=slug,
            )
            counts["divisions"] += 1
            counts["contains"] += 1

        # --- Books ---
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

            # Division CONTAINS Book (if division found)
            if div_slug:
                session.run(
                    "MATCH (d:Division {slug: $div_slug}) "
                    "MATCH (b:Book {slug: $slug}) "
                    "MERGE (d)-[:CONTAINS]->(b)",
                    div_slug=div_slug, slug=slug,
                )
            else:
                # Fallback: Volume CONTAINS Book directly
                session.run(
                    "MATCH (v:Volume {slug: $vol}) "
                    "MATCH (b:Book {slug: $slug}) "
                    "MERGE (v)-[:CONTAINS]->(b)",
                    vol=b["volume_slug"], slug=slug,
                )
            counts["books"] += 1
            counts["contains"] += 1

        # --- Parts ---
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

            # Book CONTAINS Part
            book_slug = f"{p['volume_slug']}/{p['book_slug']}"
            session.run(
                "MATCH (b:Book {slug: $book_slug}) "
                "MATCH (p:Part {slug: $slug}) "
                "MERGE (b)-[:CONTAINS]->(p)",
                book_slug=book_slug, slug=slug,
            )
            counts["parts"] += 1
            counts["contains"] += 1

        # --- Chapters ---
        # Group by book for NEXT/PREVIOUS
        chapters_by_book: dict[str, list[dict]] = {}
        for ch in chapters:
            key = f"{ch['volume_slug']}/{ch['book_slug']}"
            chapters_by_book.setdefault(key, []).append(ch)

        for book_key, book_chapters in chapters_by_book.items():
            book_chapters.sort(key=lambda c: c["chapter_num"])

            for i, ch in enumerate(book_chapters):
                if not ch.get("corpus_path"):
                    continue
                slug = ch["corpus_path"].replace(".txt", "")  # e.g., "ot/genesis/1"
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

                # Part CONTAINS Chapter (if part exists)
                if ch.get("part_mysql_id") and ch["part_mysql_id"] in part_slugs:
                    session.run(
                        "MATCH (p:Part {slug: $part_slug}) "
                        "MATCH (c:Chapter {slug: $slug}) "
                        "MERGE (p)-[:CONTAINS]->(c)",
                        part_slug=part_slugs[ch["part_mysql_id"]], slug=slug,
                    )
                else:
                    # Fallback: Book CONTAINS Chapter
                    session.run(
                        "MATCH (b:Book {slug: $book_key}) "
                        "MATCH (c:Chapter {slug: $slug}) "
                        "MERGE (b)-[:CONTAINS]->(c)",
                        book_key=book_key, slug=slug,
                    )
                counts["contains"] += 1

                # Link Chapter to existing Document node
                for lang in ("en", "es"):
                    fp = f"{lang}/scriptures/{ch['corpus_path']}"
                    session.run(
                        "MATCH (c:Chapter {slug: $slug}) "
                        "MATCH (d:Document {file_path: $fp}) "
                        "MERGE (c)-[:HAS_DOCUMENT]->(d)",
                        slug=slug, fp=fp,
                    )

                # NEXT / PREVIOUS
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

        # --- Load .meta.json properties onto Chapter nodes ---
        logger.info("Loading metadata onto Chapter nodes...")
        for ch in chapters:
            if not ch.get("corpus_path"):
                continue
            slug = ch["corpus_path"].replace(".txt", "")
            for lang in ("en", "es"):
                _local_corpus = Path(__file__).resolve().parent.parent / "corpus"
                _container_corpus = Path("/app/corpus")
                corpus_root = _container_corpus if _container_corpus.exists() else _local_corpus
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

    driver.close()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Load scripture hierarchy into Neo4j")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="alejandria")
    args = parser.parse_args()

    if args.dry_run:
        print("\n=== DRY RUN: Scripture Hierarchy ===\n")
        dry_run_report()
        return

    logger.info("Loading scripture hierarchy into Neo4j...")
    counts = load_to_neo4j(args.uri, args.user, args.password)

    print(f"\n=== Scripture Hierarchy Loaded ===")
    for k, v in counts.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
