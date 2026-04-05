#!/usr/bin/env python3
"""Download books from BYU Studies into the Alejandría corpus.

Uses the RSC (React Server Components) streaming payload to extract
chapter HTML without a headless browser.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --book history-of-the-church-volume-7
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --list-books
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from html import unescape
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://byustudies.byu.edu"
CORPUS_ROOT = Path(__file__).resolve().parent.parent / "corpus"

RSC_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
    "Accept": "text/x-component",
    "RSC": "1",
}

# Rate limit: be polite to BYU
REQUEST_DELAY = 1.5  # seconds between requests


# ---------------------------------------------------------------------------
# Book configurations
# ---------------------------------------------------------------------------

BOOK_CONFIGS: dict[str, dict] = {
    "history-of-the-church-volume-7": {
        "slug": "history-of-the-church-vol7",
        "byu_book_path": "online-book/history-of-the-church-volume-7",
        "author": "Joseph Smith",
        "category": "books",
        "tags": ["church-history", "prophet-history", "brigham-young", "nauvoo", "exodus"],
        "authority": 40,
        "chapters": [
            ("volume-7-title-page", "Title Page"),
            ("volume-7-introduction", "Introduction"),
        ] + [
            (f"volume-7-chapter-{i}", f"Chapter {i}")
            for i in range(1, 42)
        ],
        "skip_chapters": ["volume-7-title-page"],  # Title page has no useful content
        "note": "Period II: From the manuscript history of Brigham Young. "
                "Edited by B. H. Roberts. Published 1932. 41 chapters. "
                "Source: BYU Studies online.",
    },
}


# ---------------------------------------------------------------------------
# RSC content extraction
# ---------------------------------------------------------------------------

def fetch_rsc_content(url: str, ca_bundle: str | None = None) -> str:
    """Fetch a BYU Studies page via RSC and extract the HTML content."""
    verify = ca_bundle if ca_bundle else True
    resp = requests.get(url, headers=RSC_HEADERS, verify=verify, timeout=30)
    resp.raise_for_status()

    # Extract the T-blob containing HTML content
    m = re.search(r"[0-9a-f]+:T[0-9a-f]+,(<.+)", resp.text, re.DOTALL)
    if not m:
        logger.warning("No T-blob found in RSC response for %s", url)
        return ""
    return m.group(1)


def html_to_text(html: str) -> str:
    """Convert HTML to clean plain text, preserving paragraph structure."""
    # Remove script/style tags entirely
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)

    # Convert block elements to double newlines
    for tag in ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
                "blockquote", "li", "tr", "br"):
        text = re.sub(rf"</?{tag}[^>]*>", "\n\n", text, flags=re.IGNORECASE)

    # Remove all remaining tags
    text = re.sub(r"<[^>]+>", "", text)

    # Unescape HTML entities
    text = unescape(text)

    # Clean up whitespace
    text = re.sub(r"[ \t]+", " ", text)  # collapse horizontal whitespace
    text = re.sub(r"\n[ \t]+", "\n", text)  # strip leading whitespace on lines
    text = re.sub(r"[ \t]+\n", "\n", text)  # strip trailing whitespace on lines
    text = re.sub(r"\n{3,}", "\n\n", text)  # max 2 consecutive newlines
    text = text.strip()

    # Remove [Page N] markers (artifact from print edition)
    text = re.sub(r"\[Page \d+\]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def reflow_paragraphs(text: str) -> str:
    """Join lines within paragraphs, keeping paragraph breaks."""
    paragraphs = text.split("\n\n")
    result = []
    for para in paragraphs:
        # Join lines within a paragraph
        lines = para.strip().split("\n")
        joined = " ".join(line.strip() for line in lines if line.strip())
        if joined:
            result.append(joined)
    return "\n\n".join(result)


# ---------------------------------------------------------------------------
# Download logic
# ---------------------------------------------------------------------------

def download_book(book_key: str, ca_bundle: str | None = None,
                  dry_run: bool = False) -> dict:
    """Download a BYU Studies book into the corpus."""
    config = BOOK_CONFIGS.get(book_key)
    if not config:
        logger.error("Unknown book: %s", book_key)
        return {"error": f"Unknown book: {book_key}"}

    slug = config["slug"]
    author = config["author"]
    book_path = config["byu_book_path"]
    skip = set(config.get("skip_chapters", []))

    logger.info("=" * 60)
    logger.info("Book: %s by %s", slug, author)

    if dry_run:
        logger.info("[DRY RUN] Would download %d chapters", len(config["chapters"]))
        return {"book": slug, "dry_run": True, "chapters": len(config["chapters"])}

    # Output directory
    output_dir = CORPUS_ROOT / "en" / config.get("category", "books") / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    errors = 0

    for ch_idx, (ch_slug, ch_title) in enumerate(config["chapters"]):
        if ch_slug in skip:
            logger.info("  [--] Skipping: %s", ch_title)
            skipped += 1
            continue

        # Determine chapter number
        ch_num = ch_idx  # 0 = title page, 1 = intro, 2+ = chapters
        filename = f"{ch_num:02d}-chapter-{ch_num}"
        txt_path = output_dir / f"{filename}.txt"
        meta_path = output_dir / f"{filename}.meta.json"

        if txt_path.exists():
            logger.info("  [%02d] Already exists: %s", ch_num, ch_title)
            skipped += 1
            continue

        # Fetch chapter
        url = f"{BASE_URL}/{book_path}/{ch_slug}"
        try:
            html = fetch_rsc_content(url, ca_bundle)
            if not html:
                logger.warning("  [%02d] Empty content: %s", ch_num, ch_title)
                errors += 1
                continue

            body = html_to_text(html)
            body = reflow_paragraphs(body)

            # Remove Gutenberg-style end markers if present
            for marker in ("End of the Project Gutenberg",
                           "End of Project Gutenberg"):
                idx = body.find(marker)
                if idx >= 0:
                    body = body[:idx].rstrip()

            logger.info("  [%02d] %s — %d chars", ch_num, ch_title[:50], len(body))

            # Write text
            txt_path.write_text(body, encoding="utf-8")

            # Write metadata
            meta = {
                "title": ch_title,
                "author": author,
                "book": slug.replace("-", " ").title(),
                "chapter": ch_num,
                "category": config.get("category", "books"),
                "subcategory": slug,
                "tags": config.get("tags", []),
                "authority": config.get("authority", 30),
                "lang": "eng",
                "source_url": url,
                "source": "BYU Studies",
            }
            if config.get("note"):
                meta["note"] = config["note"]

            meta_path.write_text(
                json.dumps(meta, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            written += 1

        except Exception as e:
            logger.error("  [%02d] Error fetching %s: %s", ch_num, ch_title, e)
            errors += 1

        # Rate limiting
        time.sleep(REQUEST_DELAY)

    logger.info("Done: %s — %d written, %d skipped, %d errors",
                slug, written, skipped, errors)
    return {
        "book": slug,
        "written": written,
        "skipped": skipped,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Download BYU Studies books")
    parser.add_argument("--book", type=str, help="Book key to download")
    parser.add_argument("--list-books", action="store_true",
                        help="List available books")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be downloaded")
    args = parser.parse_args()

    ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE")

    if args.list_books:
        for key, cfg in BOOK_CONFIGS.items():
            print(f"  {key}: {cfg['slug']} by {cfg['author']} "
                  f"({len(cfg['chapters'])} chapters)")
        return

    if not args.book:
        parser.error("--book is required (use --list-books to see options)")

    download_book(args.book, ca_bundle=ca_bundle, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
