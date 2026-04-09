#!/usr/bin/env python3
"""Download the Journal of Discourses from journalofdiscourses.com.

Fetches all 26 volumes (1,426 discourses) as .txt + .meta.json files.
Metadata is extracted from volume TOC pages (speaker, date, location, pages).

Usage:
    python scripts/download_jod.py
    python scripts/download_jod.py --volume 1
    python scripts/download_jod.py --volume 1 --volume 2
    python scripts/download_jod.py --dry-run
    python scripts/download_jod.py --resume
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
BASE_URL = "https://journalofdiscourses.com"
AUTHORITY = 20
DELAY = 0.5  # seconds between requests


# ---------------------------------------------------------------------------
# HTML Parsers (stdlib only — no BeautifulSoup dependency)
# ---------------------------------------------------------------------------

class VolumeTOCParser(HTMLParser):
    """Parse a volume page to extract discourse metadata from div.media-body."""

    def __init__(self):
        super().__init__()
        self.discourses: list[dict] = []
        self._in_media_body = False
        self._in_h4 = False
        self._in_a_h4 = False
        self._in_p = False
        self._p_count = 0
        self._current_href = ""
        self._current_title: list[str] = []
        self._current_desc: list[str] = []
        self._current_meta: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = d.get("class", "")
        if tag == "div" and "media-body" in cls:
            self._in_media_body = True
            self._p_count = 0
            self._current_desc = []
            self._current_meta = []
        elif self._in_media_body:
            if tag == "h4":
                self._in_h4 = True
                self._current_title = []
            elif tag == "a" and self._in_h4:
                self._in_a_h4 = True
                self._current_href = d.get("href", "")
            elif tag == "p":
                self._in_p = True
                self._p_count += 1

    def handle_endtag(self, tag):
        if tag == "a" and self._in_a_h4:
            self._in_a_h4 = False
        elif tag == "h4" and self._in_h4:
            self._in_h4 = False
        elif tag == "p" and self._in_p:
            self._in_p = False
        elif tag == "div" and self._in_media_body:
            self._in_media_body = False
            title = "".join(self._current_title).strip()
            desc = "".join(self._current_desc).strip()
            meta = "".join(self._current_meta).strip()
            if self._current_href:
                self.discourses.append(
                    _parse_toc_entry(self._current_href, title, desc, meta)
                )
            self._current_href = ""

    def handle_data(self, data):
        if self._in_a_h4:
            self._current_title.append(data)
        elif self._in_p and self._in_media_body:
            if self._p_count == 1:
                self._current_desc.append(data)
            elif self._p_count == 2:
                self._current_meta.append(data)

    def handle_entityref(self, name):
        import html as html_mod
        char = html_mod.unescape(f"&{name};")
        if self._in_a_h4:
            self._current_title.append(char)
        elif self._in_p and self._in_media_body:
            if self._p_count == 1:
                self._current_desc.append(char)


class DiscourseParser(HTMLParser):
    """Parse a discourse page to extract title, speaker, and paragraphs."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.speaker = ""
        self.paragraphs: list[str] = []
        self._in_h1 = False
        self._in_small = False
        self._in_paragraph = False
        self._current_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "h1":
            self._in_h1 = True
            self._current_text = []
        elif tag == "small" and self._in_h1:
            self._in_small = True
            self.title = "".join(self._current_text).strip()
            self._current_text = []
        elif tag == "div" and d.get("class") == "paragraph":
            self._in_paragraph = True
            self._current_text = []

    def handle_endtag(self, tag):
        if tag == "small" and self._in_small:
            self._in_small = False
            self.speaker = "".join(self._current_text).strip()
            self._current_text = []
        elif tag == "h1":
            self._in_h1 = False
        elif tag == "div" and self._in_paragraph:
            self._in_paragraph = False
            text = re.sub(r"\s+", " ", "".join(self._current_text)).strip()
            if text:
                self.paragraphs.append(text)

    def handle_data(self, data):
        if self._in_h1 or self._in_paragraph:
            self._current_text.append(data)

    def handle_entityref(self, name):
        import html as html_mod
        char = html_mod.unescape(f"&{name};")
        if self._in_h1 or self._in_paragraph:
            self._current_text.append(char)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_toc_entry(href: str, title: str, desc: str, meta: str) -> dict:
    """Extract structured metadata from a TOC entry."""
    parts = href.strip("/").split("/")
    volume = int(parts[0]) if len(parts) >= 1 else 0
    disc_num = int(parts[1]) if len(parts) >= 2 else 0

    # Speaker from description
    speaker = ""
    sp_m = re.search(
        r"by (?:President |Elder |Brother |Bishop |Sister )?(.+?),\s+[Dd]eliver",
        desc,
    )
    if sp_m:
        speaker = sp_m.group(1).strip()

    # Speaker role
    role = ""
    role_m = re.search(r"by (President|Elder|Brother|Bishop|Sister) ", desc)
    if role_m:
        role = role_m.group(1)

    # Date
    date_str = ""
    date_m = re.search(r"(\w+ \d{1,2},?\s*\d{4})", desc)
    if date_m:
        date_str = _normalize_date(date_m.group(1))

    # Location
    location = ""
    loc_m = re.search(r"[Dd]elivered (?:in |at )(.+?),\s+\w+ \d", desc)
    if loc_m:
        location = loc_m.group(1).strip()

    # Pages
    pages = ""
    pg_m = re.search(r"pages? (\d+-\d+)", meta)
    if pg_m:
        pages = pg_m.group(1)

    return {
        "href": href,
        "volume": volume,
        "discourse_number": disc_num,
        "title": title,
        "speaker": speaker,
        "speaker_role": role,
        "date": date_str,
        "location": location,
        "pages": pages,
        "description": desc,
    }


def _normalize_date(raw: str) -> str:
    """Convert 'January 16, 1853' to '1853-01-16'."""
    import datetime
    raw = raw.replace(",", "").strip()
    for fmt in ("%B %d %Y", "%b %d %Y"):
        try:
            dt = datetime.datetime.strptime(raw, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw  # return as-is if unparseable


def _slugify(text: str, max_len: int = 60) -> str:
    """Create a filesystem-safe slug from a title."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:max_len].rstrip("-")


def _fix_encoding(raw_bytes: bytes) -> str:
    """Decode and fix encoding issues from the site."""
    # Site declares iso-8859-1 but serves mixed encoding
    text = raw_bytes.decode("latin-1", errors="replace")
    # Fix em-dashes encoded as \x97 (Windows-1252 em-dash)
    text = text.replace("\x97", "\u2014")
    # Fix other common Windows-1252 chars
    text = text.replace("\x93", "\u201c")  # left double quote
    text = text.replace("\x94", "\u201d")  # right double quote
    text = text.replace("\x91", "\u2018")  # left single quote
    text = text.replace("\x92", "\u2019")  # right single quote
    text = text.replace("\x96", "\u2013")  # en-dash
    # Clean stray \xC2 (UTF-8 lead byte orphaned in latin-1 decode)
    text = text.replace("\u00c2\u00a0", " ")  # Â + NBSP → space
    text = text.replace("\u00c2", "")  # stray Â
    text = re.sub(r"\u00a0", " ", text)  # NBSP → space
    return text


def _fetch(url: str) -> str:
    """Fetch a URL and return decoded text."""
    req = Request(url, headers={"User-Agent": "Alejandria-Corpus/1.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            return _fix_encoding(resp.read())
    except (HTTPError, URLError) as e:
        logger.error("Failed to fetch %s: %s", url, e)
        raise


# ---------------------------------------------------------------------------
# Core download logic
# ---------------------------------------------------------------------------

def fetch_volume_toc(volume: int) -> list[dict]:
    """Fetch and parse the TOC for a volume."""
    url = f"{BASE_URL}/{volume}"
    html = _fetch(url)
    parser = VolumeTOCParser()
    parser.feed(html)
    logger.info("Volume %d: %d discourses", volume, len(parser.discourses))
    return parser.discourses


def fetch_discourse(volume: int, disc_num: int) -> tuple[str, str, list[str]]:
    """Fetch and parse a single discourse. Returns (title, speaker, paragraphs)."""
    url = f"{BASE_URL}/{volume}/{disc_num}"
    html = _fetch(url)
    parser = DiscourseParser()
    parser.feed(html)
    return parser.title, parser.speaker, parser.paragraphs


def download_volume(volume: int, out_dir: Path, dry_run: bool, resume: bool) -> int:
    """Download all discourses in a volume. Returns count of downloaded files."""
    vol_dir = out_dir / f"vol{volume:02d}"
    vol_dir.mkdir(parents=True, exist_ok=True)

    toc = fetch_volume_toc(volume)
    time.sleep(DELAY)

    downloaded = 0
    for entry in toc:
        disc_num = entry["discourse_number"]
        slug = _slugify(entry["title"]) or f"discourse-{disc_num}"
        prefix = f"{disc_num:02d}-{slug}"
        txt_path = vol_dir / f"{prefix}.txt"
        meta_path = vol_dir / f"{prefix}.meta.json"

        if resume and txt_path.exists() and meta_path.exists():
            logger.debug("Skipping %d/%d (already exists)", volume, disc_num)
            continue

        if dry_run:
            logger.info("[DRY RUN] Would download %d/%d → %s", volume, disc_num, txt_path.name)
            downloaded += 1
            continue

        try:
            title, speaker, paragraphs = fetch_discourse(volume, disc_num)
        except Exception as e:
            logger.error("Failed to download %d/%d: %s", volume, disc_num, e)
            continue

        # Write text
        text = "\n\n".join(paragraphs) + "\n"
        txt_path.write_text(text, encoding="utf-8")

        # Write metadata
        meta = {
            "title": entry["title"],
            "speaker": entry["speaker"] or speaker,
            "speaker_role": entry["speaker_role"],
            "date": entry["date"],
            "location": entry["location"],
            "volume": volume,
            "discourse_number": disc_num,
            "pages": entry["pages"],
            "source": "Journal of Discourses",
            "source_url": f"{BASE_URL}/{volume}/{disc_num}",
            "language": "en",
            "authority": AUTHORITY,
            "accuracy_caveat": (
                "Published text may differ significantly from words actually spoken. "
                "See Carruth/Dirkmaat research on shorthand vs. published discrepancies."
            ),
        }
        meta_path.write_text(
            json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        words = sum(len(p.split()) for p in paragraphs)
        logger.info(
            "  %d/%d %s — %s (%d words)",
            volume, disc_num, entry["title"][:50], entry["speaker"][:30], words,
        )
        downloaded += 1
        time.sleep(DELAY)

    return downloaded


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Download Journal of Discourses")
    parser.add_argument(
        "--volume", type=int, action="append",
        help="Volume(s) to download (default: all 1-26). Can be repeated.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be downloaded")
    parser.add_argument("--resume", action="store_true", help="Skip already-downloaded files")
    args = parser.parse_args()

    volumes = args.volume or list(range(1, 27))
    out_dir = CORPUS_ROOT / "en" / "books" / "journal-of-discourses"
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Downloading Journal of Discourses: volumes %s", volumes)
    logger.info("Output: %s", out_dir)
    if args.dry_run:
        logger.info("DRY RUN — no files will be written")

    total = 0
    t0 = time.time()
    for vol in volumes:
        n = download_volume(vol, out_dir, args.dry_run, args.resume)
        total += n
        elapsed = time.time() - t0
        logger.info(
            "Volume %d done (%d files). Total so far: %d files, %.0fs elapsed",
            vol, n, total, elapsed,
        )

    elapsed = time.time() - t0
    logger.info("Complete: %d files in %.0f seconds", total, elapsed)


if __name__ == "__main__":
    main()
