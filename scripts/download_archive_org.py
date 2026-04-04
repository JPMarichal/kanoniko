#!/usr/bin/env python3
"""Download and split books from Internet Archive into corpus-ready chapters.

Fetches DjVuTXT (OCR text) from archive.org items, cleans OCR artifacts,
splits into chapters, reflows paragraphs, and writes .txt + .meta.json
per chapter.

Usage:
    python scripts/download_archive_org.py --item-id risefallofnauvoo00byu2robe
    python scripts/download_archive_org.py --item-id risefallofnauvoo00byu2robe --dry-run
    python scripts/download_archive_org.py --list-books
    python scripts/download_archive_org.py --item-id historyofchurcho01robe historyofchurcho02robe

API pattern:
    Metadata: https://archive.org/metadata/{identifier}
    Text:     https://archive.org/download/{identifier}/{identifier}_djvu.txt
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import ssl
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CORPUS_ROOT = Path(__file__).resolve().parent.parent / "corpus"

# ---------------------------------------------------------------------------
# Pre-configured book metadata
# ---------------------------------------------------------------------------

BOOK_CONFIGS: dict[str, dict] = {
    "risefallofnauvoo00byu2robe": {
        "slug": "rise-and-fall-of-nauvoo",
        "author": "B. H. Roberts",
        "title": "The Rise and Fall of Nauvoo",
        "category": "books",
        "tags": ["church-history", "seventy-authored", "nauvoo", "persecution"],
        "authority": 35,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC]+)\.?\s*$",
        "title_offset": 2,
        "has_toc": True,
        "note": "Published 1900. Companion to The Missouri Persecutions. "
                "Chronicles the Nauvoo period from settlement through the exodus.",
    },
    "StudiesOfTheBookOfMormon": {
        "slug": "studies-of-book-of-mormon",
        "author": "B. H. Roberts",
        "title": "Studies of the Book of Mormon",
        "category": "books",
        "tags": ["doctrine", "seventy-authored", "book-of-mormon", "critical-analysis"],
        "authority": 30,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC\d]+)\.?\s*$",
        "title_offset": 2,
        "has_toc": True,
        "note": "Written c. 1922, published posthumously 1985. Roberts' critical examination "
                "of Book of Mormon evidences and parallels with View of the Hebrews.",
    },
    # History of the Church (Joseph Smith, edited by Roberts), 6 volumes
    "historyofchurcho01robe": {
        "slug": "history-of-the-church-vol1",
        "author": "Joseph Smith",
        "title": "History of the Church, Vol. 1",
        "category": "books",
        "tags": ["church-history", "prophet-history", "joseph-smith"],
        "authority": 40,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC]+)\.?\s*$",
        "title_offset": 2,
        "has_toc": True,
        "note": "Edited by B. H. Roberts. Published 1902. Period I: History of Joseph Smith, "
                "the Prophet, by himself. Deseret News, Salt Lake City.",
    },
    "historyofchurcho02robe": {
        "slug": "history-of-the-church-vol2",
        "author": "Joseph Smith",
        "title": "History of the Church, Vol. 2",
        "category": "books",
        "tags": ["church-history", "prophet-history", "joseph-smith"],
        "authority": 40,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC]+)\.?\s*$",
        "title_offset": 2,
        "has_toc": True,
        "note": "Edited by B. H. Roberts. Published 1904.",
    },
    "historyofchurcho03robe": {
        "slug": "history-of-the-church-vol3",
        "author": "Joseph Smith",
        "title": "History of the Church, Vol. 3",
        "category": "books",
        "tags": ["church-history", "prophet-history", "joseph-smith"],
        "authority": 40,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC]+)\.?\s*$",
        "title_offset": 2,
        "has_toc": True,
        "note": "Edited by B. H. Roberts. Published 1905.",
    },
    "historyofchurcho04robe": {
        "slug": "history-of-the-church-vol4",
        "author": "Joseph Smith",
        "title": "History of the Church, Vol. 4",
        "category": "books",
        "tags": ["church-history", "prophet-history", "joseph-smith"],
        "authority": 40,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC]+)\.?\s*$",
        "title_offset": 2,
        "has_toc": True,
        "note": "Edited by B. H. Roberts. Published 1908.",
    },
    "historyofchurcho05robe": {
        "slug": "history-of-the-church-vol5",
        "author": "Joseph Smith",
        "title": "History of the Church, Vol. 5",
        "category": "books",
        "tags": ["church-history", "prophet-history", "joseph-smith"],
        "authority": 40,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC]+)\.?\s*$",
        "title_offset": 2,
        "has_toc": True,
        "note": "Edited by B. H. Roberts. Published 1909.",
    },
    "historyofchurcho06robe": {
        "slug": "history-of-the-church-vol6",
        "author": "Joseph Smith",
        "title": "History of the Church, Vol. 6",
        "category": "books",
        "tags": ["church-history", "prophet-history", "joseph-smith"],
        "authority": 40,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC]+)\.?\s*$",
        "title_offset": 2,
        "has_toc": True,
        "note": "Edited by B. H. Roberts. Published 1912.",
    },
}


# ---------------------------------------------------------------------------
# Roman numeral conversion (shared with Gutenberg script)
# ---------------------------------------------------------------------------

def roman_to_int(s: str) -> int:
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    prev = 0
    for c in reversed(s.upper()):
        v = vals.get(c, 0)
        if v < prev:
            total -= v
        else:
            total += v
        prev = v
    return total


def chapter_sort_key(num_str: str) -> int:
    num_str = num_str.strip()
    if num_str.isdigit():
        return int(num_str)
    return roman_to_int(num_str)


# ---------------------------------------------------------------------------
# Archive.org API
# ---------------------------------------------------------------------------

def _ssl_context(ca_bundle: str | None = None) -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    if ca_bundle:
        ctx.load_verify_locations(ca_bundle)
    return ctx


def fetch_item_metadata(item_id: str, ca_bundle: str | None = None) -> dict:
    """Fetch item metadata from archive.org."""
    url = f"https://archive.org/metadata/{item_id}"
    ctx = _ssl_context(ca_bundle)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_djvu_text(item_id: str, ca_bundle: str | None = None) -> str:
    """Download the DjVuTXT (OCR text) for an archive.org item."""
    url = f"https://archive.org/download/{item_id}/{item_id}_djvu.txt"
    ctx = _ssl_context(ca_bundle)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        raw = resp.read()
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1")


def has_djvu_text(item_id: str, ca_bundle: str | None = None) -> bool:
    """Check if an item has a DjVuTXT file available."""
    try:
        meta = fetch_item_metadata(item_id, ca_bundle)
        files = meta.get("files", [])
        return any(f.get("format") == "DjVuTXT" for f in files)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# OCR text cleaning
# ---------------------------------------------------------------------------

def clean_ocr_text(text: str) -> str:
    """Clean common OCR artifacts from archive.org DjVuTXT output.

    DjVuTXT is generated by ABBYY FineReader from page scans and has
    systematic artifacts that differ from Gutenberg's clean transcriptions.
    """
    # Remove page-break markers (form feed)
    text = text.replace("\x0c", "\n\n")

    # Remove scan artifacts: isolated symbols from misread characters
    text = re.sub(r"^[^\w\s]{1,3}$", "", text, flags=re.MULTILINE)

    # Fix common OCR letter substitutions
    # These are the most systematic ones; uncommon substitutions are left
    # for manual review since aggressive replacement risks false positives.
    replacements = [
        (r"(?<=[a-z])tli(?=[a-z])", "th"),   # "tlie" → "the"
        (r"\bwliich\b", "which"),
        (r"\bwlien\b", "when"),
        (r"\bwliere\b", "where"),
        (r"\bwliat\b", "what"),
        (r"\bwliole\b", "whole"),
        (r"\btlie\b", "the"),
        (r"\bTlie\b", "The"),
        (r"\bfaitli\b", "faith"),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)

    # Fix broken hyphenation across lines: "Resur-\nrection" → "Resurrection"
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)

    # Remove repeated whitespace on a line
    text = re.sub(r"[ \t]{3,}", "  ", text)

    # Collapse excessive blank lines (OCR often inserts many)
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    # Remove lines that are just page numbers
    text = re.sub(r"(?m)^\s*\d{1,4}\s*$", "", text)

    # Remove common library stamps / header lines
    stamp_patterns = [
        r"(?m)^.*BRIGHAM\s+YOUNG\s+UNIVERSITY.*$",
        r"(?m)^.*HAROLD\s+B\.\s+LEE\s+LIBRARY.*$",
        r"(?m)^.*PROVO[,.]?\s+UTAH.*$",
    ]
    for pat in stamp_patterns:
        text = re.sub(pat, "", text)

    return text.strip()


# ---------------------------------------------------------------------------
# Reflow paragraphs (adapted from Gutenberg script for OCR quirks)
# ---------------------------------------------------------------------------

def reflow_paragraphs(text: str) -> str:
    """Re-join lines that were hard-wrapped, handling OCR spacing."""
    lines = text.split("\n")
    result = []
    buffer = []

    def flush():
        if buffer:
            result.append(" ".join(buffer))
            buffer.clear()

    for line in lines:
        stripped = line.rstrip()

        if not stripped:
            flush()
            result.append("")
            continue

        is_new_block = (
            stripped.startswith(("CHAPTER ", "SECTION ", "PART "))
            or re.match(r"^[IVXLC]+\.\s", stripped)
            or stripped.startswith(("  ", "\t"))
            or (stripped.isupper() and len(stripped) > 3)
        )

        if is_new_block:
            flush()
            result.append(stripped)
            continue

        buffer.append(stripped)

    flush()

    text = "\n".join(result)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text


# ---------------------------------------------------------------------------
# Chapter splitting (same logic as Gutenberg script)
# ---------------------------------------------------------------------------

def split_into_chapters(text: str, config: dict) -> list[dict]:
    pattern = config["chapter_pattern"]
    title_offset = config.get("title_offset", 2)
    has_toc = config.get("has_toc", False)
    sequential = config.get("sequential_numbering", False)

    lines = text.split("\n")

    boundaries = []
    for i, line in enumerate(lines):
        m = re.match(pattern, line.strip())
        if m:
            boundaries.append((i, m.group(1)))

    if not boundaries:
        logger.warning("No chapter boundaries found with pattern: %s", pattern)
        return [{"number": "1", "title": "Full Text", "body": text}]

    if has_toc and len(boundaries) > 1:
        first_ch = boundaries[0][1]
        second_occurrence = None
        for idx, (line_num, ch_num) in enumerate(boundaries[1:], 1):
            if ch_num == first_ch:
                second_occurrence = idx
                break
        if second_occurrence:
            boundaries = boundaries[second_occurrence:]

    chapters = []
    for i, (line_num, ch_num) in enumerate(boundaries):
        title = ""
        for offset in range(1, title_offset + 2):
            if line_num + offset < len(lines):
                candidate = lines[line_num + offset].strip()
                if candidate and not re.match(pattern, candidate):
                    title = candidate
                    break

        title = re.sub(r"^_(.+)_$", r"\1", title)
        title = title.strip(".")

        body_start = line_num + 1
        if i + 1 < len(boundaries):
            body_end = boundaries[i + 1][0]
        else:
            body_end = len(lines)

        body = "\n".join(lines[body_start:body_end]).strip()

        chapters.append({
            "number": ch_num,
            "title": title,
            "body": body,
        })

    return chapters


# ---------------------------------------------------------------------------
# Main download logic
# ---------------------------------------------------------------------------

def download_book(item_id: str, dry_run: bool = False, ca_bundle: str | None = None) -> dict:
    config = BOOK_CONFIGS.get(item_id, {})
    slug = config.get("slug", item_id)
    title = config.get("title", slug.replace("-", " ").title())
    author = config.get("author", "Unknown")

    if not config:
        logger.info("No pre-configured metadata for %s, fetching from API...", item_id)
        try:
            meta = fetch_item_metadata(item_id, ca_bundle)
            md = meta.get("metadata", {})
            title = md.get("title", title)
            creator = md.get("creator", [])
            if isinstance(creator, list) and creator:
                author = creator[0]
            elif isinstance(creator, str):
                author = creator
        except Exception as e:
            logger.warning("Could not fetch metadata: %s", e)

    logger.info("Book: %s by %s [%s]", title, author, item_id)

    if dry_run:
        has_text = has_djvu_text(item_id, ca_bundle)
        logger.info("[DRY RUN] DjVuTXT available: %s", has_text)
        return {"item_id": item_id, "title": title, "author": author,
                "dry_run": True, "has_text": has_text}

    # Download text
    logger.info("Downloading DjVuTXT...")
    raw_text = fetch_djvu_text(item_id, ca_bundle)
    logger.info("Downloaded %d chars (%.1f KB)", len(raw_text), len(raw_text) / 1024)

    # Clean OCR
    text = clean_ocr_text(raw_text)
    logger.info("After OCR cleanup: %d chars", len(text))

    # Split into chapters
    if config.get("chapter_pattern"):
        chapters = split_into_chapters(text, config)
    else:
        chapters = [{"number": "1", "title": title, "body": text}]

    logger.info("Split into %d chapters", len(chapters))

    # Output directory
    output_dir = CORPUS_ROOT / "en" / config.get("category", "books") / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    use_sequential = config.get("sequential_numbering", False)
    written = 0
    skipped = 0

    for seq_idx, ch in enumerate(chapters, 1):
        ch_num = seq_idx if use_sequential else chapter_sort_key(ch["number"])
        filename = f"{ch_num:02d}-chapter-{ch_num}"

        txt_path = output_dir / f"{filename}.txt"
        meta_path = output_dir / f"{filename}.meta.json"

        if txt_path.exists():
            logger.info("  [%02d] Already exists, skipping: %s", ch_num, ch["title"][:50])
            skipped += 1
            continue

        body = ch["body"]
        body = reflow_paragraphs(body)
        body = re.sub(r"\n{3,}", "\n\n", body)

        meta = {
            "title": ch["title"] or f"Chapter {ch_num}",
            "author": author,
            "book": title,
            "chapter": ch_num,
            "category": config.get("category", "books"),
            "subcategory": slug,
            "tags": config.get("tags", []),
            "authority": config.get("authority", 30),
            "lang": "eng",
            "source_url": f"https://archive.org/details/{item_id}",
            "source": "Internet Archive",
            "archive_org_id": item_id,
            "ocr_source": True,
        }

        if config.get("note"):
            meta["note"] = config["note"]

        txt_path.write_text(body + "\n", encoding="utf-8")
        meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        logger.info("  [%02d] %s — %d chars",
                     ch_num, ch["title"][:50], len(body))
        written += 1

    stats = {
        "item_id": item_id,
        "title": title,
        "author": author,
        "chapters": len(chapters),
        "written": written,
        "skipped": skipped,
        "output_dir": str(output_dir),
    }
    logger.info("Done: %s — %d written, %d skipped", title, written, skipped)
    return stats


def list_books():
    print("\nPre-configured Archive.org books:\n")
    print(f"  {'Identifier':<40} {'Title':<45} {'Author':<20} {'Auth'}")
    print(f"  {'—'*40} {'—'*45} {'—'*20} {'—'*4}")
    for item_id, cfg in sorted(BOOK_CONFIGS.items()):
        print(f"  {item_id:<40} {cfg['title'][:44]:<45} {cfg['author'][:19]:<20} {cfg['authority']}")
    print(f"\nUsage: python {Path(__file__).name} --item-id <IDENTIFIER> [<IDENTIFIER> ...]")


def main():
    parser = argparse.ArgumentParser(
        description="Download books from Internet Archive into the Alejandría corpus"
    )
    parser.add_argument("--item-id", nargs="+",
                        help="Archive.org item identifier(s) to download")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be downloaded without writing files")
    parser.add_argument("--list-books", action="store_true",
                        help="List pre-configured books and exit")
    parser.add_argument("--ca-bundle", default=None,
                        help="Path to CA certificate bundle (for corporate proxies)")
    args = parser.parse_args()

    if args.list_books:
        list_books()
        return

    if not args.item_id:
        parser.error("--item-id is required (or use --list-books)")

    ca_bundle = args.ca_bundle
    if not ca_bundle:
        default_ca = Path(__file__).resolve().parent.parent / "docker" / "ca-certificates.crt"
        if default_ca.exists():
            ca_bundle = str(default_ca)

    all_stats = []
    for item_id in args.item_id:
        logger.info("=" * 60)
        stats = download_book(item_id, dry_run=args.dry_run, ca_bundle=ca_bundle)
        all_stats.append(stats)

    logger.info("=" * 60)
    logger.info("Summary:")
    for s in all_stats:
        if "error" in s:
            logger.error("  %s: ERROR — %s", s["item_id"], s["error"])
        elif s.get("dry_run"):
            logger.info("  %s: %s [DRY RUN, text=%s]",
                        s["item_id"], s["title"], s.get("has_text"))
        else:
            logger.info("  %s: %s — %d chapters, %d written, %d skipped",
                        s["item_id"], s["title"], s["chapters"],
                        s["written"], s["skipped"])


if __name__ == "__main__":
    main()
