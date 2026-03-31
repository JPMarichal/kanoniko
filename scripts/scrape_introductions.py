#!/usr/bin/env python3
"""Download introductory/prefatory materials for all 5 standard works.

These are the pages that exist in the official site but are NOT chapter/verse
pages: title pages, introductions, testimonies, explanations, etc.

Outputs both .txt (prose) and .meta.json (metadata) files, following the same
corpus conventions as scrape_scriptures.py.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_introductions.py --lang eng
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_introductions.py --lang spa
    python scripts/scrape_introductions.py --lang eng --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup, Tag

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_ROOT / "corpus"
BASE_URL = "https://www.churchofjesuschrist.org"
REQUEST_DELAY = 0.5

# ── Pages to download ───────────────────────────────────────────────────────
# Each entry: (volume_slug, site_path_suffix, corpus_filename)
# site_path_suffix is appended to /study/scriptures/{site_volume}/
# corpus_filename is the output filename (without extension) under the volume dir.

INTRO_PAGES = [
    # Book of Mormon
    ("bom", "bofm-title", "bofm-title"),
    ("bom", "introduction", "introduction"),
    ("bom", "three", "testimony-three-witnesses"),
    ("bom", "eight", "testimony-eight-witnesses"),
    ("bom", "js", "testimony-joseph-smith"),
    ("bom", "explanation", "explanation"),
    # Doctrine & Covenants
    ("dc", "introduction", "introduction"),
    ("dc", "chron-order", "chronological-order"),
    # Pearl of Great Price
    ("pgp", "introduction", "introduction"),
    # Old Testament
    ("ot", "title-page", "title-page"),
    ("ot", "dedication", "epistle-dedicatory"),
    # New Testament
    ("nt", "title-page", "title-page"),
    # Title pages for remaining volumes
    ("bom", "title-page", "title-page"),
    ("dc", "title-page", "title-page"),
    ("pgp", "title-page", "title-page"),
]

SITE_VOLUME_MAP = {
    "ot": "ot",
    "nt": "nt",
    "bom": "bofm",
    "dc": "dc-testament",
    "pgp": "pgp",
}

# Corpus directory slug per volume — EN uses English, ES uses Spanish
CORPUS_VOLUME_SLUG = {
    "ot": "ot",
    "nt": "nt",
    "bom": "bom",
    "dc": "dc",
    "pgp": "pgp",
}


def build_url(volume_slug: str, page_suffix: str, lang: str) -> str:
    site_vol = SITE_VOLUME_MAP[volume_slug]
    return f"{BASE_URL}/study/scriptures/{site_vol}/{page_suffix}?lang={lang}"


def extract_prose(soup: BeautifulSoup) -> str:
    """Extract prose text from a non-verse page.

    Collects text from the body-block div: regular paragraphs, signature blocks,
    and list items. Preserves paragraph separation with double newlines.
    """
    body = soup.find("div", class_="body-block")
    if not body:
        # Fallback: try article
        body = soup.find("article")
    if not body:
        return ""

    paragraphs = []

    for el in body.find_all(["p", "li", "h2", "h3", "h4"]):
        # Skip elements nested inside footnotes
        if el.find_parent("footer"):
            continue
        if el.find_parent("nav"):
            continue

        # Remove footnote markers
        for sup in el.find_all("sup", class_="marker"):
            sup.decompose()

        text = el.get_text()
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue

        # Mark signatures specially
        classes = el.get("class", [])
        if isinstance(classes, list) and "signature" in classes:
            text = f"— {text}"

        paragraphs.append(text)

    return "\n\n".join(paragraphs)


def extract_metadata(soup: BeautifulSoup) -> dict:
    """Extract metadata from an introductory page."""
    metadata = {}

    h1 = soup.find("h1")
    if h1:
        metadata["title"] = h1.get_text().strip()

    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        metadata["meta_description"] = meta_desc.get("content", "")

    # Summary if present
    summary_el = soup.find("p", class_=lambda c: c and "study-summary" in str(c))
    if summary_el:
        metadata["summary"] = summary_el.get_text().strip()

    return metadata


def scrape_page(url: str, session: requests.Session,
                ca_bundle: str) -> Optional[dict]:
    """Scrape a single introductory page. Returns dict with text and metadata."""
    try:
        r = session.get(url, timeout=30, verify=ca_bundle or True)
        r.raise_for_status()
        r.encoding = "utf-8"
    except requests.RequestException as e:
        print(f"    ERROR fetching {url}: {e}", file=sys.stderr)
        return None

    soup = BeautifulSoup(r.text, "lxml")
    text = extract_prose(soup)
    metadata = extract_metadata(soup)
    metadata["source_url"] = url

    return {"text": text, "metadata": metadata}


def main():
    parser = argparse.ArgumentParser(
        description="Scrape introductory materials from churchofjesuschrist.org"
    )
    parser.add_argument("--lang", required=True, choices=["eng", "spa"],
                        help="Language to scrape")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY,
                        help="Delay between requests (seconds)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch and show content but don't write files")
    args = parser.parse_args()

    lang_dir = "en" if args.lang == "eng" else "es"
    corpus_scriptures = CORPUS_DIR / lang_dir / "scriptures"

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; AlejandriaBot/1.0; scripture-study)"
    })
    ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE", "")

    stats = {"downloaded": 0, "skipped": 0, "errors": 0}
    total = len(INTRO_PAGES)

    print(f"Scraping {total} introductory pages in {args.lang}...")
    print(f"  Corpus dir: {corpus_scriptures}")
    print(f"  Delay: {args.delay}s between requests")
    print()

    for i, (vol_slug, page_suffix, corpus_filename) in enumerate(INTRO_PAGES):
        url = build_url(vol_slug, page_suffix, args.lang)
        vol_dir = corpus_scriptures / CORPUS_VOLUME_SLUG[vol_slug]
        txt_path = vol_dir / f"{corpus_filename}.txt"
        meta_path = vol_dir / f"{corpus_filename}.meta.json"

        label = f"{vol_slug}/{corpus_filename}"
        print(f"  [{i+1}/{total}] {label} ...", end=" ", flush=True)

        # Respect rate limit
        if i > 0:
            time.sleep(args.delay)

        result = scrape_page(url, session, ca_bundle)

        if result is None:
            print("ERROR")
            stats["errors"] += 1
            continue

        text = result["text"]
        metadata = result["metadata"]

        if not text.strip():
            print(f"EMPTY (no text extracted)")
            stats["skipped"] += 1
            continue

        # Show preview
        preview = text[:120].replace("\n", " ")
        print(f"OK ({len(text)} chars)")
        print(f"    Title: {metadata.get('title', '(none)')}")
        print(f"    Preview: {preview}...")

        if args.dry_run:
            print(f"    [DRY RUN] Would write: {txt_path}")
            print(f"    [DRY RUN] Would write: {meta_path}")
        else:
            vol_dir.mkdir(parents=True, exist_ok=True)
            txt_path.write_text(text, encoding="utf-8")
            meta_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"    Wrote: {txt_path}")

        stats["downloaded"] += 1

    print(f"\n=== Summary ===")
    action = "would be written" if args.dry_run else "written"
    print(f"  Downloaded: {stats['downloaded']} pages {action}")
    print(f"  Skipped (empty): {stats['skipped']}")
    print(f"  Errors: {stats['errors']}")


if __name__ == "__main__":
    main()
