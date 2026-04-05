#!/usr/bin/env python3
"""Download books from BYU Studies into the Alejandria corpus.

Uses the RSC (React Server Components) streaming payload to extract
chapter HTML without a headless browser.

Usage:
    # List all online books
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --list-books

    # Download a specific book
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --book history-of-the-church-volume-7

    # Dry run
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --book history-of-the-church-volume-7 --dry-run

    # Override corpus category and authority
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --book the-testimony-of-luke --corpus-category books --authority 35

    # Download specific chapters only (by slug substring)
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --book history-of-the-church-volume-1 --filter chapter
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from copy import deepcopy
from html import unescape
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag

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

HTML_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
}

# Rate limit: be polite to BYU
REQUEST_DELAY = 1.5  # seconds between requests

# Series metadata (known series with shared attributes)
SERIES_META = {
    "history-of-the-church": {
        "author": "Joseph Smith",
        "editor": "B. H. Roberts",
        "tags": ["church-history", "prophet-history"],
        "authority": 40,
        "note": "History of the Church of Jesus Christ of Latter-day Saints. "
                "Edited by B. H. Roberts. Source: BYU Studies online.",
    },
    "byu-nt-commentary": {
        "tags": ["new-testament", "commentary", "academic"],
        "authority": 35,
        "note": "BYU New Testament Commentary series. Source: BYU Studies online.",
    },
    "byu-nt-rendition": {
        "tags": ["new-testament", "translation", "academic"],
        "authority": 30,
        "note": "BYU New Testament Commentary: New Renditions. Source: BYU Studies online.",
    },
    "charting": {
        "tags": ["scripture-study", "charts", "reference"],
        "authority": 30,
        "note": "Charting the Scriptures series. Source: BYU Studies online.",
    },
}


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _get_html(url: str, ca_bundle: str | None = None) -> BeautifulSoup:
    """Fetch URL as regular HTML and return parsed BeautifulSoup."""
    verify = ca_bundle if ca_bundle else True
    resp = requests.get(url, headers=HTML_HEADERS, verify=verify, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def _get_rsc(url: str, ca_bundle: str | None = None) -> str:
    """Fetch via RSC headers and extract the HTML content from T-blob."""
    verify = ca_bundle if ca_bundle else True
    resp = requests.get(url, headers=RSC_HEADERS, verify=verify, timeout=30)
    resp.raise_for_status()

    # Extract the T-blob containing HTML content
    m = re.search(r"[0-9a-f]+:T[0-9a-f]+,(<.+)", resp.text, re.DOTALL)
    if not m:
        return ""
    return m.group(1)


# ---------------------------------------------------------------------------
# Catalog discovery
# ---------------------------------------------------------------------------

def list_online_books(ca_bundle: str | None = None) -> list[dict]:
    """Discover all online books from the BYU Studies catalog page.

    Returns list of dicts with keys: slug, title, series, url.
    """
    url = f"{BASE_URL}/online-books"
    soup = _get_html(url, ca_bundle)

    books = []
    current_series = ""

    # The page has headings (h2/h3) for series and links for books
    for el in soup.find_all(["h2", "h3", "h4", "a"]):
        if el.name in ("h2", "h3", "h4"):
            current_series = el.get_text(strip=True)
            continue

        href = el.get("href", "")
        if "/online-book/" not in href:
            continue

        title = el.get_text(strip=True)
        if not title:
            continue

        slug = href.rstrip("/").split("/")[-1]
        books.append({
            "slug": slug,
            "title": title,
            "series": current_series,
            "url": f"{BASE_URL}/online-book/{slug}",
        })

    # Deduplicate by slug
    seen = set()
    unique = []
    for b in books:
        if b["slug"] not in seen:
            seen.add(b["slug"])
            unique.append(b)

    return unique


def get_book_chapters(slug: str, ca_bundle: str | None = None) -> list[dict]:
    """Fetch a book's page and extract the chapter list.

    Returns list of dicts with keys: slug, title, url.
    """
    url = f"{BASE_URL}/online-book/{slug}"
    soup = _get_html(url, ca_bundle)

    chapters = []
    prefix = f"/online-book/{slug}/"

    for a in soup.find_all("a", href=re.compile(re.escape(prefix))):
        ch_href = a["href"]
        ch_title = a.get_text(strip=True)
        ch_slug = ch_href.replace(prefix, "").rstrip("/")

        if ch_title and ch_slug:
            chapters.append({
                "slug": ch_slug,
                "title": ch_title,
                "url": f"{BASE_URL}{ch_href}",
            })

    # Deduplicate
    seen = set()
    unique = []
    for ch in chapters:
        if ch["slug"] not in seen:
            seen.add(ch["slug"])
            unique.append(ch)

    return unique


# ---------------------------------------------------------------------------
# Content extraction (RSC + HTML fallback)
# ---------------------------------------------------------------------------

def extract_chapter(url: str, ca_bundle: str | None = None) -> dict:
    """Extract chapter text and metadata from a BYU Studies chapter page.

    Tries RSC payload first, falls back to regular HTML scraping.
    Returns dict with keys: body_text, footnote_count.
    """
    # Try RSC first
    html_content = _get_rsc(url, ca_bundle)

    if html_content:
        return _parse_html_content(html_content)

    # Fallback: regular HTML
    soup = _get_html(url, ca_bundle)
    # Look for main content area
    main = (soup.find("main")
            or soup.find("article")
            or soup.find("div", class_=re.compile(r"content|body|article")))
    if main:
        return _parse_soup_content(main)

    return {"body_text": "", "footnote_count": 0}


def _parse_html_content(html: str) -> dict:
    """Parse raw HTML string from RSC payload into text + notes."""
    soup = BeautifulSoup(html, "html.parser")
    return _parse_soup_content(soup)


def _parse_soup_content(element: Tag) -> dict:
    """Extract text with footnotes from a BeautifulSoup element."""
    el = deepcopy(element)

    # Remove script/style
    for tag in el.find_all(["script", "style", "nav", "header", "footer"]):
        tag.decompose()

    # Count and convert footnote references
    footnote_refs = el.find_all("a", class_=re.compile(r"ref|footnote"))
    footnote_count = len(footnote_refs)

    # Try to find footnote/endnote sections
    notes_parts: list[str] = []

    # Pattern 1: p.p-note elements (like RSC BYU)
    note_items = el.find_all("p", class_=re.compile(r"note|footnote"))
    for ni in note_items:
        text = ni.get_text(strip=True)
        if text and len(text) > 5:
            notes_parts.append(text)
            ni.decompose()

    # Pattern 2: <ol> or <ul> with footnote class
    for fn_list in el.find_all(["ol", "ul"], class_=re.compile(r"note|footnote")):
        for li in fn_list.find_all("li"):
            text = li.get_text(strip=True)
            if text:
                notes_parts.append(text)
        fn_list.decompose()

    # Pattern 3: div with footnotes/endnotes class
    for fn_div in el.find_all("div", class_=re.compile(r"note|footnote|endnote")):
        # Extract individual notes from paragraphs or list items
        for child in fn_div.find_all(["p", "li"]):
            text = child.get_text(strip=True)
            if text:
                notes_parts.append(text)
        fn_div.decompose()

    # Insert paragraph breaks before block elements
    block_tags = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
                  "blockquote", "li", "tr", "ul", "ol", "table", "section"}
    for tag in el.find_all(block_tags):
        tag.insert_before("\n\n")
        tag.insert_after("\n\n")

    text = el.get_text()

    # Clean up whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove [Page N] markers (artifact from print edition)
    text = re.sub(r"\[Page \d+\]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Reflow paragraphs
    paragraphs = text.strip().split("\n\n")
    body_parts: list[str] = []
    for para in paragraphs:
        joined = " ".join(line.strip() for line in para.split("\n") if line.strip())
        if joined:
            body_parts.append(joined)

    # Assemble: body + notes
    result = "\n\n".join(body_parts)

    if notes_parts:
        result += "\n\nNotes\n\n"
        result += "\n\n".join(notes_parts)

    # Update footnote count from what we actually found
    if notes_parts and not footnote_count:
        footnote_count = len(notes_parts)

    return {
        "body_text": result.strip(),
        "footnote_count": footnote_count,
    }


# ---------------------------------------------------------------------------
# Series detection
# ---------------------------------------------------------------------------

def _detect_series(slug: str, title: str) -> str:
    """Detect which series a book belongs to based on slug/title."""
    if "history-of-the-church" in slug:
        return "history-of-the-church"
    if "new-rendition" in slug:
        return "byu-nt-rendition"
    if slug.startswith(("the-testimony-of-", "the-gospel-according-",
                        "pauls-", "the-revelation-of-", "the-epistle-to-",
                        "epistle-to-the-hebrews")):
        if "rendition" not in slug:
            return "byu-nt-commentary"
    if "charting" in slug:
        return "charting"
    return ""


# ---------------------------------------------------------------------------
# Download logic
# ---------------------------------------------------------------------------

def download_book(slug: str, ca_bundle: str | None = None,
                  dry_run: bool = False, corpus_category: str = "books",
                  authority: int | None = None,
                  tags: list[str] | None = None,
                  chapter_filter: str | None = None,
                  skip_chapters: list[str] | None = None) -> dict:
    """Download a BYU Studies book into the corpus."""
    logger.info("=" * 60)
    logger.info("Fetching chapter list: %s", slug)

    chapters = get_book_chapters(slug, ca_bundle)
    if not chapters:
        logger.error("No chapters found for %s", slug)
        return {"slug": slug, "error": "no chapters found"}

    # Apply filter
    if chapter_filter:
        chapters = [ch for ch in chapters if chapter_filter in ch["slug"]]
        logger.info("Filtered to %d chapters matching '%s'", len(chapters), chapter_filter)

    # Apply skip list
    skip_set = set(skip_chapters or [])
    if skip_set:
        chapters = [ch for ch in chapters if ch["slug"] not in skip_set]

    # Detect series for defaults
    series = _detect_series(slug, "")
    series_meta = SERIES_META.get(series, {})

    auth_value = authority or series_meta.get("authority", 30)
    tag_list = tags or series_meta.get("tags", ["byu-studies", "academic"])
    author = series_meta.get("author", "")
    editor = series_meta.get("editor", "")
    note = series_meta.get("note", "Source: BYU Studies online.")

    logger.info("Book: %s (%d chapters, authority=%d)", slug, len(chapters), auth_value)
    if series:
        logger.info("Series: %s", series)

    if dry_run:
        logger.info("[DRY RUN] Would download %d chapters:", len(chapters))
        for ch in chapters:
            logger.info("  %s: %s", ch["slug"], ch["title"][:60])
        return {"slug": slug, "dry_run": True, "chapters": len(chapters)}

    # Output directory
    output_dir = CORPUS_ROOT / "en" / corpus_category / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    errors = 0

    for ch_idx, ch in enumerate(chapters, 1):
        filename = f"{ch_idx:02d}-{ch['slug']}"
        txt_path = output_dir / f"{filename}.txt"
        meta_path = output_dir / f"{filename}.meta.json"

        if txt_path.exists():
            logger.info("  [%02d] Already exists: %s", ch_idx, ch["title"][:50])
            skipped += 1
            continue

        try:
            ch_data = extract_chapter(ch["url"], ca_bundle)
            body = ch_data["body_text"]

            if not body or len(body) < 50:
                logger.warning("  [%02d] Very short content (%d chars): %s",
                               ch_idx, len(body), ch["title"][:50])

            logger.info("  [%02d] %s — %d chars, %d notes",
                        ch_idx, ch["title"][:50], len(body),
                        ch_data["footnote_count"])

            # Write text
            txt_path.write_text(body, encoding="utf-8")

            # Write metadata
            meta = {
                "title": ch["title"],
                "book": slug.replace("-", " ").title(),
                "chapter": ch_idx,
                "category": corpus_category,
                "subcategory": slug,
                "tags": tag_list,
                "authority": auth_value,
                "lang": "eng",
                "source_url": ch["url"],
                "source": "BYU Studies",
            }
            if author:
                meta["author"] = author
            if editor:
                meta["editor"] = editor
            if note:
                meta["note"] = note
            if ch_data["footnote_count"]:
                meta["note_count"] = ch_data["footnote_count"]
            if series:
                meta["series"] = series

            meta_path.write_text(
                json.dumps(meta, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            written += 1

        except Exception as e:
            logger.error("  [%02d] Error fetching %s: %s", ch_idx, ch["title"][:50], e)
            errors += 1

        # Rate limiting
        time.sleep(REQUEST_DELAY)

    logger.info("Done: %s — %d written, %d skipped, %d errors",
                slug, written, skipped, errors)
    return {
        "slug": slug,
        "written": written,
        "skipped": skipped,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Download BYU Studies books into the Alejandria corpus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--book", type=str, help="Book slug to download")
    parser.add_argument("--list-books", action="store_true",
                        help="List all available online books")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be downloaded")
    parser.add_argument("--corpus-category", type=str, default="books",
                        help="Corpus category (default: books)")
    parser.add_argument("--authority", type=int, default=None,
                        help="Authority value override")
    parser.add_argument("--tags", type=str, nargs="*",
                        help="Tags for metadata")
    parser.add_argument("--filter", type=str, default=None,
                        help="Only download chapters whose slug contains this string")
    parser.add_argument("--skip", type=str, nargs="*",
                        help="Chapter slugs to skip")
    args = parser.parse_args()

    ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE")

    if args.list_books:
        books = list_online_books(ca_bundle)
        current_series = ""
        print(f"\nBYU Studies Online Books — {len(books)} titles:\n")
        for b in books:
            if b["series"] != current_series:
                current_series = b["series"]
                if current_series:
                    print(f"\n  [{current_series}]")
            print(f"    {b['slug']:60s} {b['title'][:55]}")
        return

    if not args.book:
        parser.error("--book is required (use --list-books to see options)")

    download_book(
        args.book,
        ca_bundle=ca_bundle,
        dry_run=args.dry_run,
        corpus_category=args.corpus_category,
        authority=args.authority,
        tags=args.tags,
        chapter_filter=args.filter,
        skip_chapters=args.skip,
    )


if __name__ == "__main__":
    main()
