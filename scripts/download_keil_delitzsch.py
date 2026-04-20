#!/usr/bin/env python
"""
Download Keil & Delitzsch Old Testament Commentary HTML pages from
StudyLight (studylight.org/commentaries/eng/kdo/) into data/raw/keil-delitzsch/.

Phase 1: download only. Conversion to corpus format is a separate step.

URL pattern: https://www.studylight.org/commentaries/eng/kdo/{book-slug}-{chapter}.html

Usage:
    python scripts/download_keil_delitzsch.py
    python scripts/download_keil_delitzsch.py --book genesis
    python scripts/download_keil_delitzsch.py --resume      (default: skips existing files)
    python scripts/download_keil_delitzsch.py --force        (re-download)
"""

import argparse
import os
import ssl
import sys
import time
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "keil-delitzsch")

BASE_URL = "https://www.studylight.org/commentaries/eng/kdo"
USER_AGENT = "Mozilla/5.0 (Alejandria corpus ingest; contact jpmarichal.laboral@gmail.com)"
DELAY = 0.6  # seconds between requests

# (slug, chapter_count) — standard Protestant OT chapter counts.
BOOKS = [
    ("genesis", 50),
    ("exodus", 40),
    ("leviticus", 27),
    ("numbers", 36),
    ("deuteronomy", 34),
    ("joshua", 24),
    ("judges", 21),
    ("ruth", 4),
    ("1-samuel", 31),
    ("2-samuel", 24),
    ("1-kings", 22),
    ("2-kings", 25),
    ("1-chronicles", 29),
    ("2-chronicles", 36),
    ("ezra", 10),
    ("nehemiah", 13),
    ("esther", 10),
    ("job", 42),
    ("psalms", 150),
    ("proverbs", 31),
    ("ecclesiastes", 12),
    ("song-of-solomon", 8),
    ("isaiah", 66),
    ("jeremiah", 52),
    ("lamentations", 5),
    ("ezekiel", 48),
    ("daniel", 12),
    ("hosea", 14),
    ("joel", 3),
    ("amos", 9),
    ("obadiah", 1),
    ("jonah", 4),
    ("micah", 7),
    ("nahum", 3),
    ("habakkuk", 3),
    ("zephaniah", 3),
    ("haggai", 2),
    ("zechariah", 14),
    ("malachi", 4),
]

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=60) as r:
        return r.read()


def download_chapter(slug: str, chapter: int, force: bool) -> str:
    out_dir = os.path.join(RAW_DIR, slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{chapter:03d}.html")

    if os.path.exists(out_path) and not force:
        return "skip"

    url = f"{BASE_URL}/{slug}-{chapter}.html"
    for attempt in range(3):
        try:
            data = fetch(url)
            if len(data) < 500:
                return f"too-small ({len(data)}b)"
            with open(out_path, "wb") as f:
                f.write(data)
            return "ok"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "404"
            if attempt == 2:
                return f"http {e.code}"
            time.sleep(2 * (attempt + 1))
        except Exception as e:
            if attempt == 2:
                return f"err {e.__class__.__name__}"
            time.sleep(2 * (attempt + 1))
    return "fail"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", help="Download only this book slug (e.g., genesis)")
    ap.add_argument("--force", action="store_true", help="Re-download existing files")
    args = ap.parse_args()

    books = [b for b in BOOKS if (not args.book or b[0] == args.book)]
    if not books:
        print(f"Unknown book: {args.book}", file=sys.stderr)
        return 2

    total_chapters = sum(c for _, c in books)
    print(f"Target: {len(books)} book(s), {total_chapters} chapter(s)")
    print(f"Output: {RAW_DIR}")
    print(f"Rate: {DELAY}s between requests (~{total_chapters * DELAY / 60:.1f} min)")
    print()

    counts = {"ok": 0, "skip": 0, "404": 0, "fail": 0}
    for slug, n_chapters in books:
        for ch in range(1, n_chapters + 1):
            status = download_chapter(slug, ch, args.force)
            tag = status if status in counts else "fail"
            counts[tag] = counts.get(tag, 0) + 1
            if status != "skip":
                print(f"  {slug}-{ch}: {status}")
                time.sleep(DELAY)
        print(f"[{slug}] done")

    print()
    print(f"Summary: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
