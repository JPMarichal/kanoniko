#!/usr/bin/env python3
"""Download Grandpa Bill's General Authority Pages from the Wayback Machine.

Recovers ~552 GA biographies from archived gapages.com (site went offline 2023).
Preserves the calling classification structure as metadata.

Usage:
    python scripts/download_gapages.py
    python scripts/download_gapages.py --dry-run
    python scripts/download_gapages.py --resume
    python scripts/download_gapages.py --page hinckgb1.htm
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import time
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CORPUS_ROOT = Path(__file__).resolve().parent.parent / "corpus"
WAYBACK_BASE = "http://web.archive.org/web/2021"
SITE_URL = "http://www.gapages.com"
AUTHORITY = 15  # community/secondary source
DELAY = 1.0  # polite delay between Wayback requests

# Category index pages → calling classification
CATEGORY_PAGES = {
    "1steld.htm": "First and Second Elders",
    "1stpres.htm": "First Presidency",
    "3wit.htm": "Three Witnesses",
    "q12.htm": "Quorum of the Twelve Apostles",
    "12-Pres.htm": "Presidents of the Quorum of the Twelve",
    "12-current.htm": "Current Quorum of the Twelve",
    "patriarch.htm": "Patriarch to the Church",
    "70.htm": "The Seventy",
    "1c70.htm": "First Council of the Seventy",
    "70-pres.htm": "Presidency of the Seventy",
    "1q70.htm": "First Quorum of the Seventy",
    "1q-restored.htm": "First Quorum Restored (1975)",
    "1q-restructured.htm": "First Quorum Restructured",
    "2q70.htm": "Second Quorum of the Seventy",
    "2q-organized.htm": "Second Quorum Organized",
    "asst-12.htm": "Assistants to the Twelve",
    "bishop.htm": "Presiding Bishopric",
    "discourses.htm": "Discourses and Writings",
}


# ---------------------------------------------------------------------------
# HTML Parsers
# ---------------------------------------------------------------------------

class MenuParser(HTMLParser):
    """Parse menu.htm to extract all individual biography page links."""

    def __init__(self):
        super().__init__()
        self.bio_pages: list[tuple[str, str]] = []  # (filename, display_name)
        self._in_a = False
        self._current_href = ""
        self._current_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            d = dict(attrs)
            href = d.get("href", "")
            if href.endswith(".htm") and "/" not in href:
                self._in_a = True
                self._current_href = href
                self._current_text = []

    def handle_endtag(self, tag):
        if tag == "a" and self._in_a:
            self._in_a = False
            name = " ".join("".join(self._current_text).split()).strip()
            if self._current_href and name:
                self.bio_pages.append((self._current_href, name))

    def handle_data(self, data):
        if self._in_a:
            self._current_text.append(data)


class CategoryParser(HTMLParser):
    """Parse a category index page to extract which GA pages it links to."""

    def __init__(self):
        super().__init__()
        self.linked_pages: set[str] = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            d = dict(attrs)
            href = d.get("href", "")
            if href.endswith(".htm") and "/" not in href:
                self.linked_pages.add(href)


class BiographyParser(HTMLParser):
    """Parse a GA biography page to extract structured data.

    Structure:
    - <title>: "Name, General Authority"
    - <li> items: vital facts (born, married, callings, ordination)
    - <blockquote> text: biography narrative (old-school HTML with <p> as separator, no </p>)
    - <td> items: conference talk entries

    The HTML uses <p> as a paragraph *separator* (no closing </p>), so we
    collect all text inside <blockquote> and split on <p> boundaries.
    """

    def __init__(self):
        super().__init__()
        self.title = ""
        self.vital_facts: list[str] = []
        self.paragraphs: list[str] = []
        self.talk_entries: list[str] = []

        self._in_title = False
        self._in_li = False
        self._in_blockquote = False
        self._in_td = False
        self._in_script = False
        self._in_style = False
        self._current_text: list[str] = []
        self._bq_paragraphs: list[list[str]] = []  # list of paragraph chunks
        self._bq_current: list[str] = []  # current paragraph accumulator
        self._past_hr = False  # biography text starts after first <hr>
        self._hr_count = 0

    def _flush_bq_para(self):
        """Flush the current blockquote paragraph accumulator."""
        text = _clean_text("".join(self._bq_current))
        if text and len(text) > 15:
            self._bq_paragraphs.append(text)
        self._bq_current = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self._in_script = True
        elif tag == "style":
            self._in_style = True
        elif self._in_script or self._in_style:
            return
        elif tag == "title":
            self._in_title = True
            self._current_text = []
        elif tag == "hr":
            self._hr_count += 1
            if self._hr_count == 1:
                self._past_hr = True
            elif self._in_blockquote:
                # Second <hr> inside blockquote often ends biography section
                pass
        elif tag == "li" and self._past_hr and not self._in_blockquote:
            self._in_li = True
            self._current_text = []
        elif tag == "blockquote" and self._past_hr:
            self._in_blockquote = True
            self._in_li = False  # reset — old HTML may not close <li>
            self._in_td = False  # reset — old HTML may not close <td>
            self._bq_current = []
            self._bq_paragraphs = []
        elif tag == "p" and self._in_blockquote:
            # <p> acts as paragraph separator (no </p> in old-school HTML)
            self._flush_bq_para()
        elif tag == "br" and self._in_blockquote:
            # <br> adds a soft break — just add a space
            self._bq_current.append(" ")
        elif tag == "td":
            self._in_td = True
            self._current_text = []

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_script = False
        elif tag == "style":
            self._in_style = False
        elif self._in_script or self._in_style:
            return
        elif tag == "title" and self._in_title:
            self._in_title = False
            self.title = " ".join("".join(self._current_text).split()).strip()
        elif tag == "li" and self._in_li:
            self._in_li = False
            text = _clean_text("".join(self._current_text))
            if text and len(text) > 3:
                self.vital_facts.append(text)
        elif tag == "blockquote" and self._in_blockquote:
            self._flush_bq_para()  # flush last paragraph
            self._in_blockquote = False
            self.paragraphs.extend(self._bq_paragraphs)
        elif tag == "td" and self._in_td:
            self._in_td = False
            text = _clean_text("".join(self._current_text))
            if text and "Conference" in text:
                self.talk_entries.append(text)

    def handle_data(self, data):
        if self._in_script or self._in_style:
            return
        if self._in_title:
            self._current_text.append(data)
        elif self._in_li:
            self._current_text.append(data)
        elif self._in_blockquote:
            self._bq_current.append(data)
        elif self._in_td:
            self._current_text.append(data)

    def handle_entityref(self, name):
        import html as html_mod
        char = html_mod.unescape(f"&{name};")
        if self._in_script or self._in_style:
            return
        if self._in_title or self._in_li or self._in_td:
            self._current_text.append(char)
        elif self._in_blockquote:
            self._bq_current.append(char)

    def handle_charref(self, name):
        import html as html_mod
        char = html_mod.unescape(f"&#{name};")
        if self._in_script or self._in_style:
            return
        if self._in_title or self._in_li or self._in_td:
            self._current_text.append(char)
        elif self._in_blockquote:
            self._bq_current.append(char)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_text(text: str) -> str:
    """Clean up extracted HTML text."""
    # Fix common encoding artifacts
    text = text.replace("\xa0", " ")  # NBSP
    text = text.replace("\u00a0", " ")
    text = text.replace("\x97", "\u2014")  # em-dash
    text = text.replace("\x93", "\u201c")  # left double quote
    text = text.replace("\x94", "\u201d")  # right double quote
    text = text.replace("\x91", "\u2018")  # left single quote
    text = text.replace("\x92", "\u2019")  # right single quote
    text = text.replace("\x96", "\u2013")  # en-dash
    text = text.replace("\u00c2", "")  # stray Â
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Filter out common noise phrases from the site
    noise = [
        "Hosted by The Dimension's Edge",
        "Grampa Bill's General Authority Pages",
        "Grampa Bill believes this to be",
        "Please email the Grampa",
    ]
    for n in noise:
        if n in text:
            return ""
    return text


def _slugify(text: str, max_len: int = 60) -> str:
    """Create a filesystem-safe slug from a name."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:max_len].rstrip("-")


def _extract_name_from_title(title: str) -> str:
    """Extract person name from page title like 'David A. Bednar, General Authority'."""
    if "," in title:
        return title.split(",")[0].strip()
    return title.strip()


def _fetch(url: str, retries: int = 3) -> str:
    """Fetch a URL from the Wayback Machine with retries."""
    for attempt in range(retries):
        try:
            req = Request(url, headers={
                "User-Agent": "Alejandria-Corpus/1.0 (scholarly research)",
            })
            with urlopen(req, timeout=30) as resp:
                raw = resp.read()
                # Try UTF-8 first, fall back to latin-1
                try:
                    return raw.decode("utf-8")
                except UnicodeDecodeError:
                    return raw.decode("latin-1", errors="replace")
        except (HTTPError, URLError) as e:
            if attempt < retries - 1:
                logger.warning("Retry %d for %s: %s", attempt + 1, url, e)
                time.sleep(DELAY * 2)
            else:
                raise
    return ""  # unreachable


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def fetch_menu() -> list[tuple[str, str]]:
    """Fetch menu.htm and return list of (filename, display_name) for all bio pages."""
    url = f"{WAYBACK_BASE}/{SITE_URL}/menu.htm"
    html = _fetch(url)
    parser = MenuParser()
    parser.feed(html)

    # Filter out category/index pages
    category_files = set(CATEGORY_PAGES.keys())
    bio_pages = [
        (fn, name) for fn, name in parser.bio_pages
        if fn not in category_files
    ]
    logger.info("Menu: %d biography pages found", len(bio_pages))
    return bio_pages


def build_calling_map() -> dict[str, list[str]]:
    """Build a mapping of filename → list of callings by parsing category pages."""
    calling_map: dict[str, list[str]] = {}

    for cat_page, calling_name in CATEGORY_PAGES.items():
        if cat_page == "discourses.htm":
            continue  # not a calling classification

        url = f"{WAYBACK_BASE}/{SITE_URL}/{cat_page}"
        try:
            html = _fetch(url)
        except Exception as e:
            logger.warning("Could not fetch category %s: %s", cat_page, e)
            continue

        parser = CategoryParser()
        parser.feed(html)

        # Filter to only individual biography pages (not other category pages)
        category_files = set(CATEGORY_PAGES.keys())
        for linked in parser.linked_pages:
            if linked not in category_files:
                calling_map.setdefault(linked, [])
                if calling_name not in calling_map[linked]:
                    calling_map[linked].append(calling_name)

        logger.info("Category '%s': %d GA links", calling_name, len(parser.linked_pages - category_files))
        time.sleep(DELAY)

    return calling_map


def download_biography(filename: str, display_name: str, callings: list[str],
                       out_dir: Path, dry_run: bool) -> bool:
    """Download and parse a single biography page. Returns True if successful."""
    slug = _slugify(display_name) or filename.replace(".htm", "")
    txt_path = out_dir / f"{slug}.txt"
    meta_path = out_dir / f"{slug}.meta.json"

    if dry_run:
        logger.info("[DRY RUN] %s → %s (callings: %s)", filename, txt_path.name, ", ".join(callings))
        return True

    url = f"{WAYBACK_BASE}/{SITE_URL}/{filename}"
    try:
        html = _fetch(url)
    except Exception as e:
        logger.error("Failed to download %s: %s", filename, e)
        return False

    parser = BiographyParser()
    parser.feed(html)

    name = _extract_name_from_title(parser.title) or display_name

    # Build text content
    lines: list[str] = []
    lines.append(f"# {name}\n")

    if parser.vital_facts:
        lines.append("## Biographical Summary\n")
        for fact in parser.vital_facts:
            lines.append(f"- {fact}")
        lines.append("")

    if parser.paragraphs:
        lines.append("## Biography\n")
        for para in parser.paragraphs:
            lines.append(para)
            lines.append("")

    if parser.talk_entries:
        # Deduplicate while preserving order
        seen = set()
        unique_talks = []
        for t in parser.talk_entries:
            if t not in seen:
                seen.add(t)
                unique_talks.append(t)
        lines.append("## Conference Talks\n")
        for talk in unique_talks:
            lines.append(f"- {talk}")
        lines.append("")

    text = "\n".join(lines)

    if len(text.strip()) < 50:
        logger.warning("Skipping %s — too little content extracted", filename)
        return False

    txt_path.write_text(text, encoding="utf-8")

    # Metadata
    meta = {
        "title": name,
        "display_name": display_name,
        "callings": callings,
        "vital_facts": parser.vital_facts,
        "source": "Grandpa Bill's General Authority Pages",
        "source_url": f"{SITE_URL}/{filename}",
        "source_author": "William O. Lewis III",
        "wayback_url": f"{WAYBACK_BASE}/{SITE_URL}/{filename}",
        "language": "en",
        "authority": AUTHORITY,
        "talk_count": len(parser.talk_entries),
        "accuracy_caveat": (
            "Community-compiled biographies from gapages.com (offline since 2023). "
            "Recovered from the Wayback Machine. Cross-reference with official Church sources."
        ),
    }
    meta_path.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    words = len(text.split())
    logger.info("  %s — %s (%d words, %d callings, %d talks)",
                filename, name[:40], words, len(callings), len(parser.talk_entries))
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Download Grandpa Bill's GA Pages from Wayback Machine"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be downloaded")
    parser.add_argument("--resume", action="store_true",
                        help="Skip already-downloaded files")
    parser.add_argument("--page", type=str, action="append",
                        help="Download specific page(s) only (e.g., hinckgb1.htm)")
    parser.add_argument("--skip-callings", action="store_true",
                        help="Skip building calling map (faster, no calling metadata)")
    args = parser.parse_args()

    out_dir = CORPUS_ROOT / "en" / "biographies" / "general-authorities"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Phase 1: Build calling classification map
    if args.skip_callings:
        calling_map: dict[str, list[str]] = {}
        logger.info("Skipping calling map (--skip-callings)")
    else:
        logger.info("Phase 1: Building calling classification map...")
        calling_map = build_calling_map()
        logger.info("Calling map: %d GAs have calling data", len(calling_map))
        # Save the calling map for reference
        map_path = out_dir / "_calling_map.json"
        map_path.write_text(
            json.dumps(calling_map, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        logger.info("Calling map saved to %s", map_path)

    # Phase 2: Fetch biography list
    logger.info("Phase 2: Fetching biography index...")
    if args.page:
        # Download specific pages
        bio_pages = [(p, p.replace(".htm", "")) for p in args.page]
    else:
        bio_pages = fetch_menu()
    time.sleep(DELAY)

    # Phase 3: Download biographies
    logger.info("Phase 3: Downloading %d biographies...", len(bio_pages))
    t0 = time.time()
    downloaded = 0
    skipped = 0
    failed = 0

    for i, (filename, display_name) in enumerate(bio_pages):
        slug = _slugify(display_name) or filename.replace(".htm", "")
        txt_path = out_dir / f"{slug}.txt"

        if args.resume and txt_path.exists():
            skipped += 1
            continue

        callings = calling_map.get(filename, [])
        ok = download_biography(filename, display_name, callings, out_dir, args.dry_run)

        if ok:
            downloaded += 1
        else:
            failed += 1

        # Progress report every 50
        if (i + 1) % 50 == 0:
            elapsed = time.time() - t0
            rate = downloaded / elapsed if elapsed > 0 else 0
            logger.info(
                "Progress: %d/%d (%.0f/s) — %d downloaded, %d skipped, %d failed",
                i + 1, len(bio_pages), rate, downloaded, skipped, failed,
            )

        time.sleep(DELAY)

    elapsed = time.time() - t0
    logger.info(
        "Complete: %d downloaded, %d skipped, %d failed in %.0f seconds",
        downloaded, skipped, failed, elapsed,
    )


if __name__ == "__main__":
    main()
