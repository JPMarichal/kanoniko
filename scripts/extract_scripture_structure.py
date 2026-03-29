from __future__ import annotations

"""
Extract scripture structure from MySQL dump (Laravel conventions) into JSON files.

Reads: proj/P1-scripture-structure/recursos/dump-scriptures_db-202603281925.sql
Writes: data/scripture_structure/*.json

The MySQL dump contains Spanish-only data. This script:
1. Parses INSERT statements to extract table data
2. Maps MySQL references to Alejandría corpus file paths
3. Restructures D&C (1 division, 2 books, renamed parts)
4. Adds facsimile placeholders
5. Validates pericope coverage (no gaps, no overlaps)
6. Produces JSON with mysql_id for traceability
"""

import json
import re
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DUMP_PATH = PROJECT_ROOT / "proj" / "P1-scripture-structure" / "recursos" / "dump-scriptures_db-202603281925.sql"
OUTPUT_DIR = PROJECT_ROOT / "data" / "scripture_structure"
CORPUS_DIR = PROJECT_ROOT / "corpus" / "en" / "scriptures"

# ── MySQL book name → corpus slug mapping (88 books) ──────────────────────

BOOK_SLUG_MAP = {
    # OT - La Ley
    "Génesis": ("ot", "genesis"),
    "Éxodo": ("ot", "exodus"),
    "Levítico": ("ot", "leviticus"),
    "Números": ("ot", "numbers"),
    "Deuteronomio": ("ot", "deuteronomy"),
    # OT - Libros históricos
    "Josué": ("ot", "joshua"),
    "Jueces": ("ot", "judges"),
    "Rut": ("ot", "ruth"),
    "1 Samuel": ("ot", "1-samuel"),
    "2 Samuel": ("ot", "2-samuel"),
    "1 Reyes": ("ot", "1-kings"),
    "2 Reyes": ("ot", "2-kings"),
    "1 Crónicas": ("ot", "1-chronicles"),
    "2 Crónicas": ("ot", "2-chronicles"),
    "Esdras": ("ot", "ezra"),
    "Nehemías": ("ot", "nehemiah"),
    "Ester": ("ot", "esther"),
    # OT - Libros poéticos
    "Job": ("ot", "job"),
    "Salmos": ("ot", "psalms"),
    "Proverbios": ("ot", "proverbs"),
    "Eclesiastés": ("ot", "ecclesiastes"),
    "Cantares": ("ot", "song-of-solomon"),
    # OT - Profetas mayores
    "Isaías": ("ot", "isaiah"),
    "Jeremías": ("ot", "jeremiah"),
    "Lamentaciones": ("ot", "lamentations"),
    "Ezequiel": ("ot", "ezekiel"),
    "Daniel": ("ot", "daniel"),
    # OT - Profetas menores
    "Oseas": ("ot", "hosea"),
    "Joel": ("ot", "joel"),
    "Amós": ("ot", "amos"),
    "Abdías": ("ot", "obadiah"),
    "Jonás": ("ot", "jonah"),
    "Miqueas": ("ot", "micah"),
    "Nahúm": ("ot", "nahum"),
    "Habacuc": ("ot", "habakkuk"),
    "Sofonías": ("ot", "zephaniah"),
    "Hageo": ("ot", "haggai"),
    "Zacarías": ("ot", "zechariah"),
    "Malaquías": ("ot", "malachi"),
    # NT - Evangelios
    "Mateo": ("nt", "matthew"),
    "Marcos": ("nt", "mark"),
    "Lucas": ("nt", "luke"),
    "Juan": ("nt", "john"),
    # NT - Libros históricos
    "Hechos": ("nt", "acts"),
    # NT - Epístolas paulinas
    "Romanos": ("nt", "romans"),
    "1 Corintios": ("nt", "1-corinthians"),
    "2 Corintios": ("nt", "2-corinthians"),
    "Gálatas": ("nt", "galatians"),
    "Efesios": ("nt", "ephesians"),
    "Filipenses": ("nt", "philippians"),
    "Colosenses": ("nt", "colossians"),
    "1 Tesalonicenses": ("nt", "1-thessalonians"),
    "2 Tesalonicenses": ("nt", "2-thessalonians"),
    "1 Timoteo": ("nt", "1-timothy"),
    "2 Timoteo": ("nt", "2-timothy"),
    "Tito": ("nt", "titus"),
    "Filemón": ("nt", "philemon"),
    "Hebreos": ("nt", "hebrews"),
    # NT - Epístolas universales
    "Santiago": ("nt", "james"),
    "1 Pedro": ("nt", "1-peter"),
    "2 Pedro": ("nt", "2-peter"),
    "1 Juan": ("nt", "1-john"),
    "2 Juan": ("nt", "2-john"),
    "3 Juan": ("nt", "3-john"),
    "Judas": ("nt", "jude"),
    # NT - Libros proféticos
    "Apocalipsis": ("nt", "revelation"),
    # BoM - Planchas menores
    "1 Nefi": ("bom", "1-nephi"),
    "2 Nefi": ("bom", "2-nephi"),
    "Jacob": ("bom", "jacob"),
    "Enós": ("bom", "enos"),
    "Jarom": ("bom", "jarom"),
    "Omni": ("bom", "omni"),
    # BoM - Puente editorial
    "Palabras de Mormón": ("bom", "words-of-mormon"),
    # BoM - Planchas mayores
    "Mosíah": ("bom", "mosiah"),
    "Alma": ("bom", "alma"),
    "Helamán": ("bom", "helaman"),
    "3 Nefi": ("bom", "3-nephi"),
    "4 Nefi": ("bom", "4-nephi"),
    # BoM - Escritos de Mormón
    "Mormón": ("bom", "mormon"),
    # BoM - Adiciones de Moroni
    "Éter": ("bom", "ether"),
    "Moroni": ("bom", "moroni"),
    # D&C - handled specially (book name "Secciones" and "Declaraciones oficiales")
    "Secciones": ("dc", "sections"),
    "Declaraciones oficiales": ("dc", "official-declarations"),
    # PGP
    "Moisés": ("pgp", "moses"),
    "Abraham": ("pgp", "abraham"),
    "José Smith-Mateo": ("pgp", "js-matthew"),
    "José Smith-Historia": ("pgp", "js-history"),
    "Artículos de Fe": ("pgp", "articles-of-faith"),
}

# ── Volume slug mapping ───────────────────────────────────────────────────

VOLUME_SLUG_MAP = {
    1: "ot",
    2: "nt",
    3: "bom",
    4: "dc",
    5: "pgp",
}

# ── D&C part renaming ────────────────────────────────────────────────────

DC_PART_RENAME = {
    "Nueva York": "Periodo de Nueva York",
    "Ohio": "Periodo de Ohio",
    "Misuri": "Periodo de Misuri",
    "Illinois": "Periodo de Illinois",
    "El oeste": "El Oeste",
    "La Iglesia en la actualidad": "La Iglesia moderna",
}


# ── SQL parsing ───────────────────────────────────────────────────────────


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
    # Try integer
    try:
        return int(val)
    except ValueError:
        pass
    # It's a string (quotes already stripped)
    return val


# ── Main extraction ───────────────────────────────────────────────────────

def extract_tables_streaming() -> dict:
    """Extract all relevant tables by streaming the dump line by line (memory-safe)."""
    target_tables = {"volumenes", "divisiones", "libros", "partes", "capitulos", "pericopas"}
    tables = {t: [] for t in target_tables}

    print(f"Streaming dump from {DUMP_PATH}...")
    with open(DUMP_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("INSERT INTO"):
                continue
            # Match: INSERT INTO `tablename` VALUES ...;
            m = re.match(r"INSERT INTO `(\w+)` VALUES\s*", line)
            if not m:
                continue
            table = m.group(1)
            if table not in target_tables:
                continue

            # Extract the values portion (rest of the line after "VALUES ")
            values_start = m.end()
            values_str = line[values_start:].rstrip(";\n")

            # Parse rows from this line
            rows = parse_values_string(values_str)
            tables[table].extend(rows)

    for t in target_tables:
        print(f"  {t}: {len(tables[t])} rows")

    return tables


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
            current += ch
            escape_next = True
            continue
        if ch == "'" and not in_string:
            in_string = True
            current += ch
            continue
        if ch == "'" and in_string:
            in_string = False
            current += ch
            continue
        if in_string:
            current += ch
            continue
        if ch == "(":
            depth += 1
            if depth == 1:
                current = ""
                continue
            current += ch
            continue
        if ch == ")":
            depth -= 1
            if depth == 0:
                values = parse_row_values(current)
                rows.append(tuple(values))
                current = ""
                continue
            current += ch
            continue
        current += ch

    return rows


def build_volumes(rows: list[tuple]) -> list[dict]:
    """Build volumes JSON. Schema: (Id, Nombre, Abreviatura, Descripcion, created, updated)"""
    volumes = []
    for row in rows:
        vol_id, nombre, abrev, desc, *_ = row
        volumes.append({
            "mysql_id": vol_id,
            "slug": VOLUME_SLUG_MAP[vol_id],
            "name_es": nombre,
            "name_en": None,  # Phase 2
            "abbreviation_es": abrev,
            "abbreviation_en": None,
            "description_es": desc,
        })
    return volumes


def build_divisions(rows: list[tuple], volumes: list[dict]) -> list[dict]:
    """Build divisions JSON with D&C restructuring.
    MySQL schema: (Id, Nombre, VolumenId, created, updated)
    D&C transformation: collapse mysql divisions 16+17 into 1 division.
    """
    vol_slug = {v["mysql_id"]: v["slug"] for v in volumes}
    divisions = []

    for row in rows:
        div_id, nombre, vol_id, *_ = row
        slug = vol_slug.get(vol_id, "unknown")

        # D&C: skip the two MySQL divisions, we'll add our own
        if slug == "dc":
            continue

        divisions.append({
            "mysql_id": div_id,
            "volume_slug": slug,
            "name_es": nombre,
            "name_en": None,
        })

    # Add the single D&C division
    divisions.append({
        "mysql_id": None,  # New, not from dump
        "mysql_source_ids": [16, 17],  # Traceability: collapsed from these two
        "volume_slug": "dc",
        "name_es": "Revelaciones de los últimos días",
        "name_en": "Latter-day Revelations",
    })

    return divisions


def build_books(rows: list[tuple], div_rows: list[tuple], divisions: list[dict]) -> list[dict]:
    """Build books JSON with D&C restructuring.
    MySQL schema: (Id, Nombre, DivisionId, Abreviatura, created, updated)
    D&C: MySQL books 82 (Secciones) and 83 (Declaraciones oficiales) become books
    under the single D&C division.
    """
    # Map MySQL division IDs to our division entries
    mysql_div_to_volume = {}
    for drow in div_rows:
        d_id, _, vol_id, *_ = drow
        mysql_div_to_volume[d_id] = vol_id

    # For non-DC divisions, map mysql_id → division name_es
    div_by_mysql_id = {d["mysql_id"]: d for d in divisions if d["mysql_id"] is not None}

    books = []
    for row in rows:
        book_id, nombre, div_id, abrev, *_ = row
        vol_id = mysql_div_to_volume.get(div_id)
        vol_slug = VOLUME_SLUG_MAP.get(vol_id, "unknown")

        # Resolve corpus slug
        slug_info = BOOK_SLUG_MAP.get(nombre)
        if slug_info is None:
            print(f"  WARNING: No slug mapping for book '{nombre}' (mysql_id={book_id})")
            continue
        corpus_volume, corpus_book = slug_info

        # D&C books: assign to the single D&C division
        if vol_slug == "dc":
            division_ref = "Revelaciones de los últimos días"
        else:
            div_entry = div_by_mysql_id.get(div_id)
            division_ref = div_entry["name_es"] if div_entry else f"unknown_div_{div_id}"

        books.append({
            "mysql_id": book_id,
            "division_name_es": division_ref,
            "volume_slug": corpus_volume,
            "book_slug": corpus_book,
            "name_es": nombre,
            "name_en": None,
            "abbreviation_es": abrev,
            "abbreviation_en": None,
        })

    return books


def build_parts(rows: list[tuple], books: list[dict]) -> list[dict]:
    """Build parts JSON with D&C renaming.
    MySQL schema: (Id, Nombre, LibroId, Orden, created, updated)
    """
    book_by_mysql_id = {b["mysql_id"]: b for b in books}

    parts = []
    for row in rows:
        part_id, nombre, libro_id, orden, *_ = row
        book = book_by_mysql_id.get(libro_id)
        if book is None:
            print(f"  WARNING: Part '{nombre}' references unknown book mysql_id={libro_id}")
            continue

        # Rename D&C parts
        if book["volume_slug"] == "dc":
            nombre = DC_PART_RENAME.get(nombre, nombre)

        parts.append({
            "mysql_id": part_id,
            "book_mysql_id": libro_id,
            "book_slug": book["book_slug"],
            "volume_slug": book["volume_slug"],
            "order": orden,
            "name_es": nombre,
            "name_en": None,
        })

    return parts


def resolve_chapter_path(reference: str, book_by_id: dict, part_id: int, parts: list[dict]) -> dict | None:
    """Map a MySQL chapter reference like 'Génesis 1' or 'Doctrina y Convenios 20' to corpus path info."""
    # Find the part → book
    part = next((p for p in parts if p["mysql_id"] == part_id), None)
    if part is None:
        return None

    book = book_by_id.get(part["book_mysql_id"])
    if book is None:
        return None

    vol_slug = book["volume_slug"]
    book_slug = book["book_slug"]

    # Extract chapter number from reference
    # D&C: "Doctrina y Convenios 20" → 20
    # OD: "Declaración oficial 1" → 1
    # Standard: "Génesis 1" → 1, "1 Nefi 22" → 22
    if reference.startswith("Doctrina y Convenios"):
        num_str = reference.replace("Doctrina y Convenios ", "")
        chapter_num = int(num_str)
        corpus_path = f"{vol_slug}/{book_slug}/{chapter_num}.txt"
        chapter_type = "standard"
    elif reference.startswith("Declaración oficial"):
        num_str = reference.replace("Declaración oficial ", "")
        chapter_num = int(num_str)
        corpus_path = f"{vol_slug}/official-declarations/{chapter_num}.txt"
        chapter_type = "prose"
    else:
        # Standard: last space-separated token is the number
        parts_ref = reference.rsplit(" ", 1)
        if len(parts_ref) == 2:
            chapter_num = int(parts_ref[1])
        else:
            return None
        corpus_path = f"{vol_slug}/{book_slug}/{chapter_num}.txt"
        chapter_type = "standard"

    return {
        "volume_slug": vol_slug,
        "book_slug": book_slug,
        "chapter_num": chapter_num,
        "corpus_path": corpus_path,
        "chapter_type": chapter_type,
    }


def build_chapters(rows: list[tuple], books: list[dict], parts: list[dict]) -> list[dict]:
    """Build chapters JSON.
    MySQL schema: (Id, Referencia, ParteId, created, updated)
    """
    book_by_id = {b["mysql_id"]: b for b in books}

    chapters = []
    for row in rows:
        ch_id, referencia, parte_id, *_ = row

        path_info = resolve_chapter_path(referencia, book_by_id, parte_id, parts)
        if path_info is None:
            print(f"  WARNING: Cannot resolve chapter '{referencia}' (mysql_id={ch_id})")
            continue

        part = next((p for p in parts if p["mysql_id"] == parte_id), None)

        chapters.append({
            "mysql_id": ch_id,
            "part_mysql_id": parte_id,
            "reference_es": referencia,
            "chapter_num": path_info["chapter_num"],
            "chapter_type": path_info["chapter_type"],
            "corpus_path": path_info["corpus_path"],
            "volume_slug": path_info["volume_slug"],
            "book_slug": path_info["book_slug"],
            "part_name_es": part["name_es"] if part else None,
        })

    return chapters


def add_facsimile_placeholders(chapters: list[dict], parts: list[dict]) -> tuple[list[dict], list[dict]]:
    """Add facsimile placeholders as a new part + 3 chapters under Book of Abraham."""
    # Find Abraham book mysql_id
    abraham_book_id = None
    for p in parts:
        if p["book_slug"] == "abraham":
            abraham_book_id = p["book_mysql_id"]
            break

    if abraham_book_id is None:
        print("  WARNING: Cannot find Abraham book for facsimile placeholders")
        return chapters, parts

    # Find max order for Abraham parts
    abraham_parts = [p for p in parts if p["book_mysql_id"] == abraham_book_id]
    max_order = max(p["order"] for p in abraham_parts) if abraham_parts else 0

    # Add new part
    fac_part = {
        "mysql_id": None,
        "book_mysql_id": abraham_book_id,
        "book_slug": "abraham",
        "volume_slug": "pgp",
        "order": max_order + 1,
        "name_es": "Facsímiles del Libro de Abraham",
        "name_en": "Facsimiles of the Book of Abraham",
    }
    parts.append(fac_part)

    # Add 3 facsimile chapters
    facsimiles = [
        {"num": 1, "name_es": "Facsímile 1", "name_en": "Facsimile 1", "figures": 12},
        {"num": 2, "name_es": "Facsímile 2", "name_en": "Facsimile 2", "figures": 22},
        {"num": 3, "name_es": "Facsímile 3", "name_en": "Facsimile 3", "figures": 6},
    ]

    for fac in facsimiles:
        chapters.append({
            "mysql_id": None,
            "part_mysql_id": None,
            "reference_es": f"Abraham, {fac['name_es']}",
            "chapter_num": fac["num"],
            "chapter_type": "facsimile",
            "corpus_path": None,  # No corpus file yet
            "volume_slug": "pgp",
            "book_slug": "abraham",
            "part_name_es": "Facsímiles del Libro de Abraham",
            "figure_count": fac["figures"],
        })

    return chapters, parts


def build_pericopae(rows: list[tuple], chapters: list[dict]) -> list[dict]:
    """Build pericopae JSON.
    MySQL schema: (Id, Nombre, CapituloId, VersiculoInicial, VersiculoFinal, created, updated)
    """
    ch_by_id = {c["mysql_id"]: c for c in chapters if c["mysql_id"] is not None}

    pericopae = []
    for row in rows:
        per_id, nombre, cap_id, v_start, v_end, *_ = row

        ch = ch_by_id.get(cap_id)
        if ch is None:
            print(f"  WARNING: Pericope '{nombre}' references unknown chapter mysql_id={cap_id}")
            continue

        pericopae.append({
            "mysql_id": per_id,
            "chapter_mysql_id": cap_id,
            "corpus_path": ch["corpus_path"],
            "volume_slug": ch["volume_slug"],
            "book_slug": ch["book_slug"],
            "chapter_num": ch["chapter_num"],
            "verse_start": v_start,
            "verse_end": v_end,
            "name_es": nombre,
            "name_en": None,
        })

    return pericopae


# ── Pericope coverage validation ──────────────────────────────────────────

def validate_pericope_coverage(pericopae: list[dict], chapters: list[dict]) -> dict:
    """Validate that pericopae cover all verses in each chapter without gaps or overlaps.

    Returns a report dict with gaps and overlaps per chapter.
    We need verse counts from the corpus to validate fully.
    """
    # Group pericopae by chapter
    by_chapter = {}
    for p in pericopae:
        key = p["corpus_path"]
        if key is None:
            continue
        by_chapter.setdefault(key, []).append(p)

    # Sort each chapter's pericopae by verse_start
    for key in by_chapter:
        by_chapter[key].sort(key=lambda x: x["verse_start"])

    report = {"gaps": [], "overlaps": [], "chapters_checked": 0, "chapters_clean": 0}

    # Check standard chapters that have pericopae
    standard_chapters = [c for c in chapters if c["chapter_type"] == "standard" and c["corpus_path"] is not None]

    for ch in standard_chapters:
        path = ch["corpus_path"]
        pericopes = by_chapter.get(path, [])
        report["chapters_checked"] += 1

        if not pericopes:
            # Count verses from corpus file
            verse_count = count_verses_in_file(path)
            if verse_count and verse_count > 0:
                report["gaps"].append({
                    "corpus_path": path,
                    "gap_start": 1,
                    "gap_end": verse_count,
                    "type": "entire_chapter_uncovered",
                })
            continue

        # Get verse count from corpus
        verse_count = count_verses_in_file(path)

        issues = False

        # Check for gap at start
        if pericopes[0]["verse_start"] > 1:
            report["gaps"].append({
                "corpus_path": path,
                "gap_start": 1,
                "gap_end": pericopes[0]["verse_start"] - 1,
            })
            issues = True

        # Check consecutive pericopae
        for i in range(len(pericopes) - 1):
            curr_end = pericopes[i]["verse_end"]
            next_start = pericopes[i + 1]["verse_start"]

            if next_start > curr_end + 1:
                report["gaps"].append({
                    "corpus_path": path,
                    "gap_start": curr_end + 1,
                    "gap_end": next_start - 1,
                })
                issues = True
            elif next_start <= curr_end:
                report["overlaps"].append({
                    "corpus_path": path,
                    "pericope_a": pericopes[i]["name_es"],
                    "pericope_a_range": f"{pericopes[i]['verse_start']}-{pericopes[i]['verse_end']}",
                    "pericope_b": pericopes[i + 1]["name_es"],
                    "pericope_b_range": f"{pericopes[i + 1]['verse_start']}-{pericopes[i + 1]['verse_end']}",
                })
                issues = True

        # Check for gap at end
        if verse_count and pericopes[-1]["verse_end"] < verse_count:
            report["gaps"].append({
                "corpus_path": path,
                "gap_start": pericopes[-1]["verse_end"] + 1,
                "gap_end": verse_count,
            })
            issues = True

        if not issues:
            report["chapters_clean"] += 1

    return report


def count_verses_in_file(corpus_path: str) -> int | None:
    """Count numbered verses in a corpus file."""
    full_path = CORPUS_DIR.parent.parent / "en" / "scriptures" / corpus_path
    if not full_path.exists():
        return None

    count = 0
    with open(full_path, "r", encoding="utf-8") as f:
        for line in f:
            # Verses start with a number followed by space
            if re.match(r"^\d+\s", line):
                count += 1
    return count if count > 0 else None


# ── Corpus validation ─────────────────────────────────────────────────────

def validate_corpus(chapters: list[dict]) -> dict:
    """Validate that chapter corpus paths exist."""
    report = {"found": 0, "missing": [], "skipped": 0}

    for ch in chapters:
        path = ch.get("corpus_path")
        if path is None:
            report["skipped"] += 1
            continue

        full_path = CORPUS_DIR.parent.parent / "en" / "scriptures" / path
        if full_path.exists():
            report["found"] += 1
        else:
            report["missing"].append({
                "corpus_path": path,
                "reference_es": ch["reference_es"],
                "mysql_id": ch["mysql_id"],
            })

    return report


# ── Output ────────────────────────────────────────────────────────────────

def write_json(data, filename: str):
    """Write JSON file to output directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Wrote {path} ({len(data)} entries)")


def main():
    tables = extract_tables_streaming()

    print("\n== Building structures ==")

    print("Volumes...")
    volumes = build_volumes(tables["volumenes"])

    print("Divisions (with D&C restructuring)...")
    divisions = build_divisions(tables["divisiones"], volumes)

    print("Books (with D&C restructuring)...")
    books = build_books(tables["libros"], tables["divisiones"], divisions)

    print("Parts (with D&C renaming)...")
    parts = build_parts(tables["partes"], books)

    print("Chapters...")
    chapters = build_chapters(tables["capitulos"], books, parts)

    print("Facsimile placeholders...")
    chapters, parts = add_facsimile_placeholders(chapters, parts)

    print("Pericopae...")
    pericopae = build_pericopae(tables["pericopas"], chapters)

    print("\n== Writing JSON files ==")
    write_json(volumes, "volumes.json")
    write_json(divisions, "divisions.json")
    write_json(books, "books.json")
    write_json(parts, "parts.json")
    write_json(chapters, "chapters.json")
    write_json(pericopae, "pericopae.json")

    print("\n== Validating corpus paths ==")
    corpus_report = validate_corpus(chapters)
    print(f"  Found: {corpus_report['found']}")
    print(f"  Missing: {len(corpus_report['missing'])}")
    print(f"  Skipped (no corpus path): {corpus_report['skipped']}")
    if corpus_report["missing"]:
        print("  Missing files:")
        for m in corpus_report["missing"][:20]:
            print(f"    {m['corpus_path']} ({m['reference_es']})")
        if len(corpus_report["missing"]) > 20:
            print(f"    ... and {len(corpus_report['missing']) - 20} more")

    print("\n== Validating pericope coverage ==")
    coverage_report = validate_pericope_coverage(pericopae, chapters)
    print(f"  Chapters checked: {coverage_report['chapters_checked']}")
    print(f"  Chapters clean (no gaps/overlaps): {coverage_report['chapters_clean']}")
    print(f"  Total gaps: {len(coverage_report['gaps'])}")
    print(f"  Total overlaps: {len(coverage_report['overlaps'])}")

    if coverage_report["gaps"]:
        print("  Sample gaps:")
        for g in coverage_report["gaps"][:20]:
            t = g.get("type", "")
            print(f"    {g['corpus_path']} vv.{g['gap_start']}-{g['gap_end']} {t}")

    if coverage_report["overlaps"]:
        print("  Sample overlaps:")
        for o in coverage_report["overlaps"][:10]:
            print(f"    {o['corpus_path']}: '{o['pericope_a']}' ({o['pericope_a_range']}) vs '{o['pericope_b']}' ({o['pericope_b_range']})")

    # Write reports
    write_json(corpus_report, "_report_corpus.json")
    write_json(coverage_report, "_report_coverage.json")

    print("\n== Done ==")
    has_issues = len(corpus_report["missing"]) > 0 or len(coverage_report["gaps"]) > 0 or len(coverage_report["overlaps"]) > 0
    if has_issues:
        print("WARNING: Issues found — review reports in data/scripture_structure/")
        return 1
    else:
        print("OK: All validations passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
