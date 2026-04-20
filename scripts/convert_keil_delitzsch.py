#!/usr/bin/env python
"""
Convert raw Keil & Delitzsch HTML pages (data/raw/keil-delitzsch/) into
the Alejandria corpus format under corpus/en/books/keil-delitzsch/.

Input:  data/raw/keil-delitzsch/{book-slug}/{NNN}.html
Output: corpus/en/books/keil-delitzsch/{book-slug}/{NNN}.txt
        corpus/en/books/keil-delitzsch/{book-slug}/{NNN}.meta.json

Each commentary chapter aggregates one or more "commentaries-entry-div" blocks,
where each block covers one verse or a verse range (e.g., data-entry="verses-1-3").
Block markers become "## Verses 1-3" headings; <p> becomes a blank-line-separated
paragraph; everything else is stripped.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from html import unescape
from html.parser import HTMLParser
from typing import List, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "keil-delitzsch")
OUT_DIR = os.path.join(PROJECT_ROOT, "corpus", "en", "books", "keil-delitzsch")

BASE_URL = "https://www.studylight.org/commentaries/eng/kdo"

# Display name for each book slug.
BOOK_DISPLAY = {
    "genesis": "Genesis", "exodus": "Exodus", "leviticus": "Leviticus",
    "numbers": "Numbers", "deuteronomy": "Deuteronomy", "joshua": "Joshua",
    "judges": "Judges", "ruth": "Ruth", "1-samuel": "1 Samuel",
    "2-samuel": "2 Samuel", "1-kings": "1 Kings", "2-kings": "2 Kings",
    "1-chronicles": "1 Chronicles", "2-chronicles": "2 Chronicles",
    "ezra": "Ezra", "nehemiah": "Nehemiah", "esther": "Esther", "job": "Job",
    "psalms": "Psalms", "proverbs": "Proverbs", "ecclesiastes": "Ecclesiastes",
    "song-of-solomon": "Song of Solomon", "isaiah": "Isaiah",
    "jeremiah": "Jeremiah", "lamentations": "Lamentations", "ezekiel": "Ezekiel",
    "daniel": "Daniel", "hosea": "Hosea", "joel": "Joel", "amos": "Amos",
    "obadiah": "Obadiah", "jonah": "Jonah", "micah": "Micah", "nahum": "Nahum",
    "habakkuk": "Habakkuk", "zephaniah": "Zephaniah", "haggai": "Haggai",
    "zechariah": "Zechariah", "malachi": "Malachi",
}

# Authorship: K&D was written jointly. Keil covered most historical/legal books;
# Delitzsch covered poetry and most prophets. We tag both as default authors.
AUTHORS = "Carl Friedrich Keil; Franz Delitzsch"

# Per-block authorship (best-effort attribution by primary writer).
PRIMARY_AUTHOR = {
    "genesis": "Keil", "exodus": "Keil", "leviticus": "Keil", "numbers": "Keil",
    "deuteronomy": "Keil", "joshua": "Keil", "judges": "Keil", "ruth": "Keil",
    "1-samuel": "Keil", "2-samuel": "Keil", "1-kings": "Keil", "2-kings": "Keil",
    "1-chronicles": "Keil", "2-chronicles": "Keil", "ezra": "Keil",
    "nehemiah": "Keil", "esther": "Keil",
    "job": "Delitzsch", "psalms": "Delitzsch", "proverbs": "Delitzsch",
    "ecclesiastes": "Delitzsch", "song-of-solomon": "Delitzsch",
    "isaiah": "Delitzsch", "jeremiah": "Keil", "lamentations": "Keil",
    "ezekiel": "Keil", "daniel": "Keil",
    "hosea": "Keil", "joel": "Keil", "amos": "Keil", "obadiah": "Keil",
    "jonah": "Keil", "micah": "Keil", "nahum": "Keil", "habakkuk": "Keil",
    "zephaniah": "Keil", "haggai": "Keil", "zechariah": "Keil", "malachi": "Keil",
}


# --- HTML extraction --------------------------------------------------------

ENTRY_DIV_RE = re.compile(
    r'<div class="commentaries-entry-div">(.*?)</div>\s*(?=<div class="commentaries-entry-div">|<!--\s*end of commentary|<div class="(?:other-tabs|adsfree|jump-com))',
    re.DOTALL | re.IGNORECASE,
)
DATA_ENTRY_RE = re.compile(r'data-entry="([^"]+)"')


class TextExtractor(HTMLParser):
    """Extract plain text from a commentary block, preserving paragraph breaks."""

    BLOCK_TAGS = {"p", "div", "br", "li", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6"}
    SKIP_TAGS = {"script", "style", "noscript"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return
        # The verse-marker <h3> wraps an <a> we already capture via data-entry,
        # so suppress duplicating it here.
        attrs_d = dict(attrs)
        if tag == "h3" and "commentaries-entry-number" in attrs_d.get("class", ""):
            self.skip_depth += 1
            return
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if tag == "h3":
            self.skip_depth = max(0, self.skip_depth - 1)

    def handle_data(self, data):
        if self.skip_depth:
            return
        self.parts.append(data)

    def text(self) -> str:
        raw = "".join(self.parts)
        # Strip site boilerplate.
        raw = re.sub(r"return to 'Top of Page'", "", raw, flags=re.IGNORECASE)
        # Collapse internal whitespace.
        raw = re.sub(r"[ \t]+", " ", raw)
        # Collapse 3+ blank lines to 2.
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


def humanize_marker(marker: str) -> str:
    """`verse-1` -> `Verse 1`; `verses-1-3` -> `Verses 1-3`."""
    parts = marker.split("-")
    if not parts:
        return marker
    head = parts[0].capitalize()
    nums = "-".join(parts[1:])
    return f"{head} {nums}".strip()


def extract_blocks(html: str) -> List[Tuple[str, str]]:
    """Return [(marker, text), ...] for one chapter HTML file."""
    out = []
    # Use a robust loop: find each entry-div, then walk to its matching </div>.
    pos = 0
    open_re = re.compile(r'<div class="commentaries-entry-div"[^>]*>')
    while True:
        m = open_re.search(html, pos)
        if not m:
            break
        start = m.end()
        # Walk to matching </div> by counting div nesting.
        depth = 1
        i = start
        for tok in re.finditer(r"<(/?)div\b[^>]*>", html[start:]):
            if tok.group(1) == "":
                depth += 1
            else:
                depth -= 1
                if depth == 0:
                    i = start + tok.start()
                    break
        block_html = html[m.start():i]
        marker_m = DATA_ENTRY_RE.search(block_html)
        marker = marker_m.group(1) if marker_m else ""
        ext = TextExtractor()
        ext.feed(block_html)
        text = ext.text()
        if text:
            out.append((marker, text))
        pos = i + len("</div>")
    return out


def convert_chapter(book_slug: str, chapter: int, raw_path: str) -> Tuple[str, str]:
    with open(raw_path, encoding="utf-8") as f:
        html = f.read()
    blocks = extract_blocks(html)
    if not blocks:
        return "", ""

    book_name = BOOK_DISPLAY[book_slug]
    title = f"{book_name} {chapter} — Keil & Delitzsch Commentary"
    body_parts = [f"# {title}", ""]
    for marker, text in blocks:
        heading = humanize_marker(marker) if marker else ""
        if heading:
            body_parts.append(f"## {heading}")
            body_parts.append("")
        body_parts.append(text)
        body_parts.append("")
    body = "\n".join(body_parts).rstrip() + "\n"

    primary = PRIMARY_AUTHOR.get(book_slug, "Keil")
    meta = {
        "title": title,
        "author": AUTHORS,
        "primary_author": "Carl Friedrich Keil" if primary == "Keil" else "Franz Delitzsch",
        "book": f"Keil & Delitzsch — {book_name}",
        "series": "Biblical Commentary on the Old Testament",
        "chapter": chapter,
        "category": "books",
        "subcategory": "keil-delitzsch",
        "tags": [
            "biblical-commentary",
            "old-testament",
            "non-lds-scholarship",
            "hebrew-philology",
            "lutheran",
            "19th-century",
            book_slug,
        ],
        "authority": 25,
        "lang": "eng",
        "source_url": f"{BASE_URL}/{book_slug}-{chapter}.html",
        "source": "StudyLight (public domain text, Clark FTL 1864-1892)",
        "rigor": 80,
        "importance": "consulta",
        "official": False,
        "current": False,
        "context": "non-lds-scholarship",
        "audience": "scholar",
        "note": (
            "19th-century Protestant Hebrew commentary; not LDS doctrine, but "
            "rigorous philological treatment widely compatible with Restoration "
            "scriptural exegesis. Use as scholarly cross-reference, not as "
            "authoritative interpretation."
        ),
    }
    return body, json.dumps(meta, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", help="Convert only this book slug")
    ap.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = ap.parse_args()

    if not os.path.isdir(RAW_DIR):
        print(f"No raw dir: {RAW_DIR}", file=sys.stderr)
        return 2

    book_dirs = sorted(d for d in os.listdir(RAW_DIR) if os.path.isdir(os.path.join(RAW_DIR, d)))
    if args.book:
        book_dirs = [d for d in book_dirs if d == args.book]
        if not book_dirs:
            print(f"Book not found in raw: {args.book}", file=sys.stderr)
            return 2

    counts = {"ok": 0, "empty": 0, "skip": 0}
    for slug in book_dirs:
        if slug not in BOOK_DISPLAY:
            print(f"  WARN unknown slug: {slug}")
            continue
        src_dir = os.path.join(RAW_DIR, slug)
        dst_dir = os.path.join(OUT_DIR, slug)
        os.makedirs(dst_dir, exist_ok=True)

        for fname in sorted(os.listdir(src_dir)):
            if not fname.endswith(".html"):
                continue
            try:
                chapter = int(fname[:-5])
            except ValueError:
                continue
            base = f"{chapter:03d}"
            txt_path = os.path.join(dst_dir, f"{base}.txt")
            meta_path = os.path.join(dst_dir, f"{base}.meta.json")
            if os.path.exists(txt_path) and not args.force:
                counts["skip"] += 1
                continue
            body, meta = convert_chapter(slug, chapter, os.path.join(src_dir, fname))
            if not body:
                counts["empty"] += 1
                print(f"  EMPTY {slug}/{fname}")
                continue
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(body)
            with open(meta_path, "w", encoding="utf-8") as f:
                f.write(meta)
            counts["ok"] += 1
        print(f"[{slug}] processed")

    print()
    print(f"Summary: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
