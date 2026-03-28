#!/usr/bin/env python3
"""Download LDS scriptures from public domain sources and generate corpus files.

Sources:
  - English (all standard works): beandog/lds-scriptures SQLite database (public domain)
  - Spanish (Book of Mormon): janKaje/Languages-of-the-Book-of-Mormon JSON

Usage:
    python scripts/download_scriptures.py                  # download all available
    python scripts/download_scriptures.py --lang en        # English only
    python scripts/download_scriptures.py --lang es        # Spanish only
    python scripts/download_scriptures.py --dry-run        # show what would be created
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# URLs
# ---------------------------------------------------------------------------
ENGLISH_SQLITE_URL = (
    "https://raw.githubusercontent.com/beandog/lds-scriptures/master/sqlite/lds-scriptures-sqlite.db"
)
SPANISH_BOM_JSON_URL = (
    "https://raw.githubusercontent.com/janKaje/Languages-of-the-Book-of-Mormon/main/data/spa.json"
)

# ---------------------------------------------------------------------------
# Book slug mappings  (DB title -> directory slug)
# ---------------------------------------------------------------------------
# These map the book_title values in the beandog SQLite DB to our directory slugs.

_BOOK_TITLE_TO_SLUG: dict[str, str] = {
    # Book of Mormon
    "1 Nephi": "1-nephi",
    "2 Nephi": "2-nephi",
    "Jacob": "jacob",
    "Enos": "enos",
    "Jarom": "jarom",
    "Omni": "omni",
    "Words of Mormon": "words-of-mormon",
    "Mosiah": "mosiah",
    "Alma": "alma",
    "Helaman": "helaman",
    "3 Nephi": "3-nephi",
    "4 Nephi": "4-nephi",
    "Mormon": "mormon",
    "Ether": "ether",
    "Moroni": "moroni",
    # Old Testament
    "Genesis": "genesis",
    "Exodus": "exodus",
    "Leviticus": "leviticus",
    "Numbers": "numbers",
    "Deuteronomy": "deuteronomy",
    "Joshua": "joshua",
    "Judges": "judges",
    "Ruth": "ruth",
    "1 Samuel": "1-samuel",
    "2 Samuel": "2-samuel",
    "1 Kings": "1-kings",
    "2 Kings": "2-kings",
    "1 Chronicles": "1-chronicles",
    "2 Chronicles": "2-chronicles",
    "Ezra": "ezra",
    "Nehemiah": "nehemiah",
    "Esther": "esther",
    "Job": "job",
    "Psalms": "psalms",
    "Proverbs": "proverbs",
    "Ecclesiastes": "ecclesiastes",
    "Song of Solomon": "song-of-solomon",
    "Isaiah": "isaiah",
    "Jeremiah": "jeremiah",
    "Lamentations": "lamentations",
    "Ezekiel": "ezekiel",
    "Daniel": "daniel",
    "Hosea": "hosea",
    "Joel": "joel",
    "Amos": "amos",
    "Obadiah": "obadiah",
    "Jonah": "jonah",
    "Micah": "micah",
    "Nahum": "nahum",
    "Habakkuk": "habakkuk",
    "Zephaniah": "zephaniah",
    "Haggai": "haggai",
    "Zechariah": "zechariah",
    "Malachi": "malachi",
    # New Testament
    "Matthew": "matthew",
    "Mark": "mark",
    "Luke": "luke",
    "John": "john",
    "Acts": "acts",
    "Romans": "romans",
    "1 Corinthians": "1-corinthians",
    "2 Corinthians": "2-corinthians",
    "Galatians": "galatians",
    "Ephesians": "ephesians",
    "Philippians": "philippians",
    "Colossians": "colossians",
    "1 Thessalonians": "1-thessalonians",
    "2 Thessalonians": "2-thessalonians",
    "1 Timothy": "1-timothy",
    "2 Timothy": "2-timothy",
    "Titus": "titus",
    "Philemon": "philemon",
    "Hebrews": "hebrews",
    "James": "james",
    "1 Peter": "1-peter",
    "2 Peter": "2-peter",
    "1 John": "1-john",
    "2 John": "2-john",
    "3 John": "3-john",
    "Jude": "jude",
    "Revelation": "revelation",
    # D&C
    "Doctrine and Covenants": "sections",
    # Pearl of Great Price
    "Moses": "moses",
    "Abraham": "abraham",
    "Joseph Smith-Matthew": "js-matthew",
    "Joseph Smith-History": "js-history",
    "Joseph Smith--Matthew": "js-matthew",
    "Joseph Smith--History": "js-history",
    "Joseph Smith\u2014Matthew": "js-matthew",
    "Joseph Smith\u2014History": "js-history",
    "Articles of Faith": "articles-of-faith",
    # Alternate DB titles
    "The Song of Solomon": "song-of-solomon",
    "Revelation of John": "revelation",
}

# Volume title in DB -> our volume slug
_VOLUME_TITLE_TO_SLUG: dict[str, str] = {
    "Book of Mormon": "bom",
    "Old Testament": "ot",
    "New Testament": "nt",
    "Doctrine and Covenants": "dc",
    "Pearl of Great Price": "pgp",
}

# Spanish BOM abbreviation (janKaje JSON key prefix) -> directory slug
_SPANISH_BOM_ABBREV_TO_SLUG: dict[str, str] = {
    "1-ne": "1-nefi",
    "2-ne": "2-nefi",
    "jacob": "jacob",
    "enos": "enos",
    "jarom": "jarom",
    "omni": "omni",
    "w-of-m": "palabras-de-mormon",
    "mosiah": "mosiah",
    "alma": "alma",
    "hel": "helaman",
    "3-ne": "3-nefi",
    "4-ne": "4-nefi",
    "morm": "mormon",
    "ether": "eter",
    "moro": "moroni",
}

# Keys to skip (front matter, not chapters)
_SPANISH_BOM_SKIP = {"title-page", "bofm-title", "introduction", "three", "eight", "js", "explanation"}


# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------

def download_file(url: str, dest: Path, description: str = "") -> bool:
    """Download a file with progress indication."""
    log.info("Downloading %s from %s", description or dest.name, url)
    try:
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    pct = downloaded * 100 // total
                    print(f"\r  {pct}% ({downloaded:,} / {total:,} bytes)", end="", flush=True)
        print()
        log.info("  Downloaded: %s (%s bytes)", dest, downloaded)
        return True
    except Exception as e:
        log.error("  Download failed: %s", e)
        return False


# ---------------------------------------------------------------------------
# English scriptures from beandog/lds-scriptures SQLite
# ---------------------------------------------------------------------------

def process_english_sqlite(db_path: Path, corpus_dir: Path, dry_run: bool) -> int:
    """Extract English scriptures from the SQLite DB. Returns file count."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Discover schema
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    log.info("  DB tables: %s", tables)

    # Try to understand the schema
    # Common schemas: (volumes, books, chapters, verses) or flat
    if "verses" in tables:
        return _process_english_relational(conn, corpus_dir, dry_run)
    else:
        log.error("  Unknown schema. Tables: %s", tables)
        conn.close()
        return 0


def _process_english_relational(conn: sqlite3.Connection, corpus_dir: Path, dry_run: bool) -> int:
    """Process relational schema with volumes/books/chapters/verses tables."""
    # Get column info
    verse_cols = [r[1] for r in conn.execute("PRAGMA table_info(verses)").fetchall()]
    log.info("  Verse columns: %s", verse_cols)

    # Detect column names (they vary between DB versions)
    # Common: verse_id, volume_id, book_id, chapter_id, verse_number, scripture_text
    # Also possible: verse_title, verse_short_title
    text_col = None
    for candidate in ("scripture_text", "verse_text", "text", "content"):
        if candidate in verse_cols:
            text_col = candidate
            break
    if not text_col:
        log.error("  Cannot find text column in verses table. Columns: %s", verse_cols)
        return 0

    verse_num_col = None
    for candidate in ("verse_number", "verse_num", "number"):
        if candidate in verse_cols:
            verse_num_col = candidate
            break
    if not verse_num_col:
        log.error("  Cannot find verse number column. Columns: %s", verse_cols)
        return 0

    # Check if we have volume/book/chapter info in verses or need joins
    if "volume_title" in verse_cols:
        # Flat/denormalized schema
        return _process_flat_schema(conn, corpus_dir, dry_run, text_col, verse_num_col)
    else:
        # Need joins
        return _process_joined_schema(conn, corpus_dir, dry_run, text_col, verse_num_col)


def _process_flat_schema(
    conn: sqlite3.Connection, corpus_dir: Path, dry_run: bool,
    text_col: str, verse_num_col: str,
) -> int:
    """Process denormalized schema where verses table has all info."""
    rows = conn.execute(f"""
        SELECT volume_title, book_title, chapter_number, {verse_num_col}, {text_col}
        FROM verses
        ORDER BY volume_id, book_id, chapter_id, {verse_num_col}
    """).fetchall()

    return _write_chapter_files(rows, corpus_dir, dry_run, "en")


def _process_joined_schema(
    conn: sqlite3.Connection, corpus_dir: Path, dry_run: bool,
    text_col: str, verse_num_col: str,
) -> int:
    """Process normalized schema requiring joins."""
    # Check what tables and columns exist
    book_cols = [r[1] for r in conn.execute("PRAGMA table_info(books)").fetchall()]
    vol_cols = [r[1] for r in conn.execute("PRAGMA table_info(volumes)").fetchall()]

    book_title_col = "book_title" if "book_title" in book_cols else "title"
    vol_title_col = "volume_title" if "volume_title" in vol_cols else "title"

    chapter_num_col = "chapter_number"
    ch_cols = [r[1] for r in conn.execute("PRAGMA table_info(chapters)").fetchall()]
    if "chapter_number" not in ch_cols:
        chapter_num_col = "number" if "number" in ch_cols else ch_cols[1]  # fallback

    query = f"""
        SELECT v.{vol_title_col} as volume_title,
               b.{book_title_col} as book_title,
               ch.{chapter_num_col} as chapter_number,
               ve.{verse_num_col} as verse_number,
               ve.{text_col} as scripture_text
        FROM verses ve
        JOIN chapters ch ON ve.chapter_id = ch.id
        JOIN books b ON ch.book_id = b.id
        JOIN volumes v ON b.volume_id = v.id
        ORDER BY v.id, b.id, ch.id, ve.{verse_num_col}
    """
    rows = conn.execute(query).fetchall()
    return _write_chapter_files(rows, corpus_dir, dry_run, "en")


def _write_chapter_files(
    rows: list, corpus_dir: Path, dry_run: bool, lang: str,
) -> int:
    """Write verse rows to chapter files. Returns count of files created."""
    # Group by (volume, book, chapter)
    chapters: dict[tuple[str, str, int], list[tuple[int, str]]] = {}
    for row in rows:
        vol_title = row["volume_title"]
        book_title = row["book_title"]
        chapter_num = int(row["chapter_number"])
        verse_num = int(row["verse_number"])
        verse_text = row["scripture_text"]

        key = (vol_title, book_title, chapter_num)
        if key not in chapters:
            chapters[key] = []
        chapters[key].append((verse_num, verse_text))

    file_count = 0
    for (vol_title, book_title, chapter_num), verses in chapters.items():
        vol_slug = _VOLUME_TITLE_TO_SLUG.get(vol_title)
        if not vol_slug:
            log.warning("  Unknown volume: %s", vol_title)
            continue

        book_slug = _BOOK_TITLE_TO_SLUG.get(book_title)
        if not book_slug:
            log.warning("  Unknown book: %s", book_title)
            continue

        # Build path
        if vol_slug == "dc":
            chapter_dir = corpus_dir / lang / "scriptures" / vol_slug / book_slug
        else:
            chapter_dir = corpus_dir / lang / "scriptures" / vol_slug / book_slug

        file_path = chapter_dir / f"{chapter_num}.txt"

        if dry_run:
            log.info("  [DRY RUN] Would create: %s (%d verses)", file_path, len(verses))
        else:
            chapter_dir.mkdir(parents=True, exist_ok=True)
            verses.sort(key=lambda v: v[0])
            with open(file_path, "w", encoding="utf-8") as f:
                for vnum, vtext in verses:
                    # Clean HTML entities and extra whitespace
                    vtext = vtext.strip()
                    f.write(f"{vnum} {vtext}\n")

        file_count += 1

    return file_count


# ---------------------------------------------------------------------------
# Spanish Book of Mormon from janKaje JSON
# ---------------------------------------------------------------------------

def _strip_bbcode(text: str) -> str:
    """Remove BBCode-style markup tags like [center], [font_size=26], [i], etc."""
    return re.sub(r"\[/?[a-z_]+(=[^\]]+)?\]", "", text)


def _extract_verses_from_chapter_text(text: str) -> list[tuple[int, str]]:
    """Extract numbered verses from a chapter text block.

    The text may contain BBCode markup and chapter headers before the verses.
    Verse format: each verse starts with its number at the beginning of a line.
    """
    # Strip BBCode
    clean = _strip_bbcode(text)

    # Find verses: lines starting with a number
    verses: list[tuple[int, str]] = []
    # Split by verse markers — a number at start of line followed by space
    parts = re.split(r"\n(?=\d{1,3}\s)", clean)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(\d{1,3})\s+(.+)", part, re.DOTALL)
        if m:
            vnum = int(m.group(1))
            vtext = m.group(2).replace("\n", " ").strip()
            # Clean up multiple spaces
            vtext = re.sub(r"\s+", " ", vtext)
            verses.append((vnum, vtext))

    return verses


def process_spanish_bom(json_path: Path, corpus_dir: Path, dry_run: bool) -> int:
    """Extract Spanish Book of Mormon from JSON. Returns file count.

    The janKaje JSON uses:
    - Keys like "1-ne 1", "alma 32", "moro 10"
    - Values are full chapter text strings with BBCode markup
    - Verses are numbered within the text: "1 Yo, Nefi..."
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    file_count = 0

    for key, chapter_text in data.items():
        # Parse key: "abbrev chapter_num"
        match = re.match(r"^(.+?)\s+(\d+)$", key)
        if not match:
            continue

        book_abbrev = match.group(1)
        chapter_num = int(match.group(2))

        # Skip front matter
        if book_abbrev in _SPANISH_BOM_SKIP:
            continue

        book_slug = _SPANISH_BOM_ABBREV_TO_SLUG.get(book_abbrev)
        if not book_slug:
            log.warning("  Unknown Spanish BOM abbreviation: %s", book_abbrev)
            continue

        # Extract verses from the text
        verses = _extract_verses_from_chapter_text(chapter_text)
        if not verses:
            log.warning("  No verses found in %s", key)
            continue

        chapter_dir = corpus_dir / "es" / "scriptures" / "bom" / book_slug
        file_path = chapter_dir / f"{chapter_num}.txt"

        if dry_run:
            log.info("  [DRY RUN] Would create: %s (%d verses)", file_path, len(verses))
        else:
            chapter_dir.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                for vnum, vtext in verses:
                    f.write(f"{vnum} {vtext}\n")

        file_count += 1

    return file_count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Download LDS scriptures for Alejandría corpus")
    parser.add_argument("--lang", choices=["en", "es", "all"], default="all",
                        help="Language to download (default: all)")
    parser.add_argument("--corpus-dir", type=Path, default=None,
                        help="Corpus root directory (default: ../corpus relative to script)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be created without writing files")
    args = parser.parse_args()

    if args.corpus_dir:
        corpus_dir = args.corpus_dir.resolve()
    else:
        corpus_dir = (Path(__file__).parent.parent / "corpus").resolve()

    log.info("Corpus directory: %s", corpus_dir)
    corpus_dir.mkdir(parents=True, exist_ok=True)

    total_files = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # English
        if args.lang in ("en", "all"):
            log.info("\n=== English Scriptures (all standard works) ===")
            db_path = tmpdir / "lds-scriptures.db"
            if download_file(ENGLISH_SQLITE_URL, db_path, "English scriptures SQLite"):
                count = process_english_sqlite(db_path, corpus_dir, args.dry_run)
                log.info("  English: %d chapter files %s", count,
                         "would be created" if args.dry_run else "created")
                total_files += count
            else:
                log.error("  Failed to download English scriptures")

        # Spanish
        if args.lang in ("es", "all"):
            log.info("\n=== Spanish Book of Mormon ===")
            json_path = tmpdir / "spa.json"
            if download_file(SPANISH_BOM_JSON_URL, json_path, "Spanish BOM JSON"):
                count = process_spanish_bom(json_path, corpus_dir, args.dry_run)
                log.info("  Spanish BOM: %d chapter files %s", count,
                         "would be created" if args.dry_run else "created")
                total_files += count
            else:
                log.error("  Failed to download Spanish Book of Mormon")

            log.info("\n  NOTE: Spanish OT, NT, D&C, and PGP are not yet available from")
            log.info("  public sources. Use the python-scripture-scraper tool or add them")
            log.info("  manually to corpus/es/scriptures/{ot,nt,dc,pgp}/")

    log.info("\n=== Summary ===")
    action = "would be created" if args.dry_run else "created"
    log.info("Total: %d chapter files %s in %s", total_files, action, corpus_dir)


if __name__ == "__main__":
    main()
