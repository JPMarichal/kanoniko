"""
P2 Phase 1 — Extract Spanish verses from MySQL dump into corpus files.

Reads:
  - proj/P1-scripture-structure/recursos/dump-scriptures_db-202603281925.sql (versiculos table)
  - data/scripture_structure/pericopae.json (pericopa → chapter mapping)
  - data/scripture_structure/chapters.json (chapter → corpus_path mapping)

Writes:
  - corpus/es/scriptures/{volume}/{book_es_slug}/{chapter}.txt

The MySQL dump contains 42,699 Spanish verses linked to chapters via pericopae.
This script reassembles them into the corpus file format: "N Verse text.\n"

ES corpus uses Spanish slugs (e.g., "1-nefi" not "1-nephi"), derived by slugifying
the Spanish book names from the MySQL data.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DUMP_PATH = PROJECT_ROOT / "proj" / "P1-scripture-structure" / "recursos" / "dump-scriptures_db-202603281925.sql"
STRUCTURE_DIR = PROJECT_ROOT / "data" / "scripture_structure"
CORPUS_ES_DIR = PROJECT_ROOT / "corpus" / "es" / "scriptures"


# ── EN slug → ES slug mapping ───────────────────────────────────────────────
# Derived from Spanish book names. The convention for ES corpus is to slugify
# the Spanish name: lowercase, strip accents, spaces/special → hyphens.

EN_TO_ES_SLUG = {
    # OT
    "genesis": "genesis",
    "exodus": "exodo",
    "leviticus": "levitico",
    "numbers": "numeros",
    "deuteronomy": "deuteronomio",
    "joshua": "josue",
    "judges": "jueces",
    "ruth": "rut",
    "1-samuel": "1-samuel",
    "2-samuel": "2-samuel",
    "1-kings": "1-reyes",
    "2-kings": "2-reyes",
    "1-chronicles": "1-cronicas",
    "2-chronicles": "2-cronicas",
    "ezra": "esdras",
    "nehemiah": "nehemias",
    "esther": "ester",
    "job": "job",
    "psalms": "salmos",
    "proverbs": "proverbios",
    "ecclesiastes": "eclesiastes",
    "song-of-solomon": "cantares",
    "isaiah": "isaias",
    "jeremiah": "jeremias",
    "lamentations": "lamentaciones",
    "ezekiel": "ezequiel",
    "daniel": "daniel",
    "hosea": "oseas",
    "joel": "joel",
    "amos": "amos",
    "obadiah": "abdias",
    "jonah": "jonas",
    "micah": "miqueas",
    "nahum": "nahum",
    "habakkuk": "habacuc",
    "zephaniah": "sofonias",
    "haggai": "hageo",
    "zechariah": "zacarias",
    "malachi": "malaquias",
    # NT
    "matthew": "mateo",
    "mark": "marcos",
    "luke": "lucas",
    "john": "juan",
    "acts": "hechos",
    "romans": "romanos",
    "1-corinthians": "1-corintios",
    "2-corinthians": "2-corintios",
    "galatians": "galatas",
    "ephesians": "efesios",
    "philippians": "filipenses",
    "colossians": "colosenses",
    "1-thessalonians": "1-tesalonicenses",
    "2-thessalonians": "2-tesalonicenses",
    "1-timothy": "1-timoteo",
    "2-timothy": "2-timoteo",
    "titus": "tito",
    "philemon": "filemon",
    "hebrews": "hebreos",
    "james": "santiago",
    "1-peter": "1-pedro",
    "2-peter": "2-pedro",
    "1-john": "1-juan",
    "2-john": "2-juan",
    "3-john": "3-juan",
    "jude": "judas",
    "revelation": "apocalipsis",
    # BoM
    "1-nephi": "1-nefi",
    "2-nephi": "2-nefi",
    "jacob": "jacob",
    "enos": "enos",
    "jarom": "jarom",
    "omni": "omni",
    "words-of-mormon": "palabras-de-mormon",
    "mosiah": "mosiah",
    "alma": "alma",
    "helaman": "helaman",
    "3-nephi": "3-nefi",
    "4-nephi": "4-nefi",
    "mormon": "mormon",
    "ether": "eter",
    "moroni": "moroni",
    # D&C
    "sections": "secciones",
    "official-declarations": "declaraciones-oficiales",
    # PGP
    "moses": "moises",
    "abraham": "abraham",
    "js-matthew": "jose-smith-mateo",
    "js-history": "jose-smith-historia",
    "articles-of-faith": "articulos-de-fe",
}


def en_to_es_corpus_path(en_path: str) -> str:
    """Convert an EN corpus_path like 'ot/genesis/1.txt' to ES path 'ot/genesis/1.txt'
    (volume slugs are the same, book slugs differ)."""
    parts = en_path.split("/")
    volume = parts[0]
    book_en = parts[1]
    filename = parts[2]
    book_es = EN_TO_ES_SLUG.get(book_en, book_en)
    return f"{volume}/{book_es}/{filename}"


# ── SQL parsing (reused from P1's extract_scripture_structure.py) ────────────

def parse_row_values(row_str: str) -> list:
    """Parse a single row's comma-separated values, handling quoted strings and NULL."""
    values = []
    current = ""
    in_string = False
    escape_next = False

    for ch in row_str:
        if escape_next:
            current += ch
            escape_next = False
            continue
        if ch == "\\":
            escape_next = True
            continue
        if ch == "'" and not in_string:
            in_string = True
            continue
        if ch == "'" and in_string:
            in_string = False
            continue
        if ch == "," and not in_string:
            values.append(parse_value(current.strip()))
            current = ""
            continue
        current += ch

    values.append(parse_value(current.strip()))
    return values


def parse_value(val: str):
    """Convert a SQL value string to Python type."""
    if val == "NULL":
        return None
    try:
        return int(val)
    except ValueError:
        pass
    return val


def parse_values_string(values_str: str) -> list[tuple]:
    """Parse the VALUES portion of an INSERT statement into row tuples."""
    rows = []
    current = ""
    in_string = False
    escape_next = False
    depth = 0

    for ch in values_str:
        if escape_next:
            current += ch
            escape_next = False
            continue
        if ch == "\\":
            escape_next = True
            if in_string:
                current += ch
            continue
        if ch == "'" and not escape_next:
            in_string = not in_string
            current += ch
            continue
        if not in_string:
            if ch == "(":
                depth += 1
                if depth == 1:
                    current = ""
                    continue
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    rows.append(parse_row_values(current))
                    current = ""
                    continue
        current += ch

    return rows


def extract_versiculos() -> list[list]:
    """Stream the MySQL dump and extract only the versiculos table rows."""
    rows = []
    print(f"Streaming versiculos from {DUMP_PATH.name}...")
    with open(DUMP_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("INSERT INTO `versiculos`"):
                continue
            m = re.match(r"INSERT INTO `versiculos` VALUES\s*", line)
            if not m:
                continue
            values_str = line[m.end():].rstrip(";\n")
            rows.extend(parse_values_string(values_str))
    print(f"  Extracted {len(rows)} verses")
    return rows


# ── Main assembly ────────────────────────────────────────────────────────────

def main():
    # Load P1 structure
    with open(STRUCTURE_DIR / "pericopae.json", encoding="utf-8") as f:
        pericopae = json.load(f)
    with open(STRUCTURE_DIR / "chapters.json", encoding="utf-8") as f:
        chapters = json.load(f)

    # Build lookup: pericopa mysql_id → pericopa record
    pericopa_by_id = {p["mysql_id"]: p for p in pericopae}

    # Build lookup: chapter mysql_id → chapter record
    chapter_by_id = {c["mysql_id"]: c for c in chapters if c["mysql_id"] is not None}

    # Extract verses from MySQL dump
    # Columns: Id, Referencia, PericopaId, NumVersiculo, Contenido, created_at, updated_at
    verse_rows = extract_versiculos()

    # Group verses by chapter
    # verse → pericopa → chapter_mysql_id → chapter record → corpus_path
    chapters_verses: dict[str, list[tuple[int, str]]] = defaultdict(list)
    skipped_no_pericopa = 0
    skipped_no_chapter = 0
    skipped_facsimile = 0

    for row in verse_rows:
        verse_id = row[0]
        referencia = row[1]
        pericopa_id = row[2]
        num_versiculo = row[3]
        contenido = row[4]

        # Find pericopa
        pericopa = pericopa_by_id.get(pericopa_id)
        if not pericopa:
            skipped_no_pericopa += 1
            continue

        chapter_mysql_id = pericopa["chapter_mysql_id"]
        chapter = chapter_by_id.get(chapter_mysql_id)
        if not chapter:
            skipped_no_chapter += 1
            continue

        # Skip facsimiles (no corpus_path)
        if chapter["chapter_type"] == "facsimile" or not chapter.get("corpus_path"):
            skipped_facsimile += 1
            continue

        es_path = en_to_es_corpus_path(chapter["corpus_path"])
        chapters_verses[es_path].append((num_versiculo, contenido))

    print(f"\n  Verses grouped into {len(chapters_verses)} chapter files")
    if skipped_no_pericopa:
        print(f"  WARNING: {skipped_no_pericopa} verses skipped (pericopa not found)")
    if skipped_no_chapter:
        print(f"  WARNING: {skipped_no_chapter} verses skipped (chapter not found)")
    if skipped_facsimile:
        print(f"  Skipped {skipped_facsimile} facsimile verses (expected)")

    # Write corpus files
    stats = {"new": 0, "modified": 0, "unchanged": 0}

    for es_path, verses in sorted(chapters_verses.items()):
        # Sort by verse number
        verses.sort(key=lambda v: v[0])

        # Assemble content
        lines = []
        for num, text in verses:
            lines.append(f"{num} {text}")
        content = "\n".join(lines) + "\n"

        # Target file
        target = CORPUS_ES_DIR / es_path.replace("/", "\\") if sys.platform == "win32" else CORPUS_ES_DIR / es_path
        target = CORPUS_ES_DIR / Path(es_path)

        # Compare with existing
        if target.exists():
            existing = target.read_text(encoding="utf-8")
            if existing == content:
                stats["unchanged"] += 1
                continue
            else:
                stats["modified"] += 1
        else:
            stats["new"] += 1

        # Write
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    # Report
    total = stats["new"] + stats["modified"] + stats["unchanged"]
    print(f"\n{'='*60}")
    print(f"P2 Phase 1 — ES Corpus Write Report")
    print(f"{'='*60}")
    print(f"  Total chapter files: {total}")
    print(f"  New files written:   {stats['new']}")
    print(f"  Modified files:      {stats['modified']}")
    print(f"  Unchanged files:     {stats['unchanged']}")
    print(f"{'='*60}")

    # Detail: per-volume breakdown
    volume_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "verses": 0})
    for es_path, verses in chapters_verses.items():
        vol = es_path.split("/")[0]
        volume_counts[vol]["files"] += 1
        volume_counts[vol]["verses"] += len(verses)

    print(f"\nPer-volume breakdown:")
    for vol in ["ot", "nt", "bom", "dc", "pgp"]:
        if vol in volume_counts:
            vc = volume_counts[vol]
            print(f"  {vol}: {vc['files']} files, {vc['verses']} verses")

    return stats


if __name__ == "__main__":
    main()
