#!/usr/bin/env python3
"""Download books and articles from RSC BYU (rsc.byu.edu) into the Alejandría corpus.

The Religious Studies Center at BYU publishes scholarly books and the
Religious Educator journal.  Older/out-of-print books are freely available
online; recent ones are purchase-only.

Site stack: Drupal, server-rendered HTML — no headless browser needed.

Usage:
    # List all online books
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_rsc.py --list-books

    # List books in a specific category
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_rsc.py --list-books --category 2

    # Download a specific book
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_rsc.py --book foundations-restoration

    # Dry run (show what would be downloaded)
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_rsc.py --book foundations-restoration --dry-run

Categories:
    1  Scripture Study          8  Doctrine and Covenants
    2  Church History           9  Pearl of Great Price
    3  Self-Help               10  Bible Studies
    7  Book of Mormon          11  Teaching
    12  Gospel Questions       13  Church History Symposium
    14  Easter Conference      15  Sidney B. Sperry Symposium
    16  Other Conferences      17  World Religions & Traditions
    309 Book of Mormon Symposium
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
from urllib.parse import urljoin

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

BASE_URL = "https://rsc.byu.edu"
CORPUS_ROOT = Path(__file__).resolve().parent.parent / "corpus"

CATEGORIES = {
    1: "Scripture Study",
    2: "Church History",
    3: "Self-Help",
    7: "Book of Mormon",
    8: "Doctrine and Covenants",
    9: "Pearl of Great Price",
    10: "Bible Studies",
    11: "Teaching",
    12: "Gospel Questions",
    13: "Church History Symposium",
    14: "Easter Conference",
    15: "Sidney B. Sperry Symposium",
    16: "Other Conferences",
    17: "World Religions & Traditions",
    309: "Book of Mormon Symposium",
}

# Rate limit: be respectful
REQUEST_DELAY = 1.5  # seconds between requests

# Default authority by category
CATEGORY_AUTHORITY = {
    1: 30,   # scripture study — academic
    2: 30,   # church history — academic
    3: 25,   # self-help
    7: 30,   # book of mormon
    8: 30,   # d&c
    9: 30,   # pgp
    10: 30,  # bible studies
    11: 25,  # teaching
    12: 30,  # gospel questions
    13: 30,  # church history symposium
    14: 30,  # easter conference
    15: 30,  # sperry symposium
    16: 25,  # other conferences
    17: 25,  # world religions
    309: 30, # bom symposium
}


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _get(url: str, ca_bundle: str | None = None) -> requests.Response:
    """GET with CA bundle and timeout."""
    verify = ca_bundle if ca_bundle else True
    return requests.get(
        url,
        verify=verify,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0"},
    )


def _soup(url: str, ca_bundle: str | None = None) -> BeautifulSoup:
    """Fetch URL and return parsed BeautifulSoup."""
    resp = _get(url, ca_bundle)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


# ---------------------------------------------------------------------------
# Catalog discovery
# ---------------------------------------------------------------------------

def list_online_books(ca_bundle: str | None = None,
                      category: int | None = None) -> list[dict]:
    """Discover all books available for online reading.

    Returns list of dicts with keys: slug, title, url.
    """
    if category:
        url = f"{BASE_URL}/books/by-category/{category}"
    else:
        url = f"{BASE_URL}/books/online"

    soup = _soup(url, ca_bundle)
    book_links = soup.find_all("a", href=re.compile(r"^/book/"))

    # Deduplicate — each book appears twice (image link + title link)
    seen: dict[str, str] = {}
    for a in book_links:
        href = a["href"]
        slug = href.replace("/book/", "")
        if slug not in seen:
            title = a.get_text(strip=True) or a.get("title", slug)
            # Skip image-only links with no text
            if not title or title == slug:
                continue
            seen[slug] = title

    return [
        {"slug": slug, "title": title, "url": f"{BASE_URL}/book/{slug}"}
        for slug, title in seen.items()
    ]


def get_book_metadata(slug: str, ca_bundle: str | None = None) -> dict | None:
    """Fetch book page and extract metadata + chapter list.

    Parses the structured TOC (toc-item-basic list items) to correctly
    extract per-chapter authors and subtitles.  Works for both single-
    author books and multi-author conference proceedings.

    Returns None if the book is not available for online reading.
    """
    url = f"{BASE_URL}/book/{slug}"
    soup = _soup(url, ca_bundle)

    page_text = soup.get_text().lower()

    # Check if book is available online
    if "not been released for online reading" in page_text:
        return None

    # ------------------------------------------------------------------
    # Book-level metadata
    # Book page uses div.pub-title-block:
    #   <h2>Title</h2>
    #   <h4>Subtitle</h4>  (optional)
    #   <div class="in-italic top-half">
    #     <a href="/node/ID">Author</a>, Editor
    #   </div>
    # ------------------------------------------------------------------
    title_block = (soup.find("div", class_="pub-title-block")
                   or soup.find("div", class_="pub-title-pane"))
    title = ""
    subtitle = ""
    if title_block:
        # Title — first heading found (h1..h4)
        for tag in ("h1", "h2", "h3", "h4"):
            h = title_block.find(tag)
            if h:
                title = h.get_text(strip=True)
                break
        # Subtitle — look for a smaller heading that isn't the title
        for tag in ("h3", "h4", "h5", "h6"):
            candidates = title_block.find_all(tag)
            for c in candidates:
                t = c.get_text(strip=True)
                if t and t != title and "Editor" not in t:
                    subtitle = t
                    break
            if subtitle:
                break

    # Authors/editors — extract from links to /node/ID
    authors = []
    is_edited = False
    if title_block:
        for a in title_block.find_all("a"):
            href = a.get("href", "")
            if "/node/" in href or "/author/" in href:
                authors.append(a.get_text(strip=True))
        # Detect "Editor(s)" marker near author names
        block_text = title_block.get_text()
        if re.search(r"\bEditors?\b", block_text):
            is_edited = True

    # ------------------------------------------------------------------
    # Chapter list from structured TOC (toc-item-basic list items)
    # Each <li class="toc-item-basic"> can contain:
    #   div.toc-title    → <a href="...">Chapter Title</a>
    #   div.toc-subtitle → <a href="...">Subtitle</a>  (same href)
    #   div.toc-author   → <a href="/node/ID">Author Name</a>
    # Section headers have class "toc-super" and no link.
    # ------------------------------------------------------------------
    chapters = []
    toc_items = soup.find_all("li", class_=re.compile(r"toc-item"))

    if toc_items:
        current_section = ""
        for li in toc_items:
            classes = " ".join(li.get("class", []))

            # Section header (e.g., "Doctrine", "Historical Content")
            if "toc-super" in classes:
                title_div = li.find("div", class_="toc-title")
                if title_div:
                    current_section = title_div.get_text(strip=True)
                continue

            # Regular chapter entry
            title_div = li.find("div", class_="toc-title")
            if not title_div:
                continue
            title_link = title_div.find("a")
            if not title_link:
                continue

            ch_href = title_link.get("href", "")
            ch_title = title_link.get_text(strip=True)
            ch_slug_parts = ch_href.rstrip("/").split("/")
            ch_slug = ch_slug_parts[-1] if ch_slug_parts else ""

            if not ch_title or not ch_slug:
                continue

            # Subtitle
            ch_subtitle = ""
            subtitle_div = li.find("div", class_="toc-subtitle")
            if subtitle_div:
                sub_link = subtitle_div.find("a")
                if sub_link:
                    ch_subtitle = sub_link.get_text(strip=True)
                else:
                    ch_subtitle = subtitle_div.get_text(strip=True)

            # Per-chapter author(s) — may be multiple links
            ch_author = ""
            author_div = li.find("div", class_="toc-author")
            if author_div:
                author_links = author_div.find_all("a")
                if author_links:
                    names = [a.get_text(strip=True) for a in author_links]
                    ch_author = ", ".join(names)
                else:
                    ch_author = author_div.get_text(strip=True)

            chapters.append({
                "slug": ch_slug,
                "title": ch_title,
                "subtitle": ch_subtitle,
                "author": ch_author,
                "section": current_section,
                "url": f"{BASE_URL}{ch_href}",
            })

    # ------------------------------------------------------------------
    # Fallback: if no TOC items found, scan for plain chapter links
    # (older pages may not use the toc-item structure)
    # ------------------------------------------------------------------
    if not chapters:
        seen_slugs: set[str] = set()
        for a in soup.find_all("a", href=re.compile(rf"^/{re.escape(slug)}/")):
            ch_href = a["href"]
            ch_title = a.get_text(strip=True)
            ch_slug = ch_href.rstrip("/").split("/")[-1]
            if ch_title and ch_slug and ch_slug not in seen_slugs:
                seen_slugs.add(ch_slug)
                chapters.append({
                    "slug": ch_slug,
                    "title": ch_title,
                    "subtitle": "",
                    "author": "",
                    "section": "",
                    "url": f"{BASE_URL}{ch_href}",
                })

    return {
        "slug": slug,
        "title": title,
        "subtitle": subtitle,
        "authors": authors,
        "is_edited": is_edited,
        "chapters": chapters,
        "url": url,
    }


# ---------------------------------------------------------------------------
# Chapter content extraction
# ---------------------------------------------------------------------------

def extract_chapter(url: str, ca_bundle: str | None = None) -> dict:
    """Extract chapter content from a chapter page.

    Returns dict with keys: title, subtitle, author, body_html, body_text,
    citation, footnote_count.
    """
    soup = _soup(url, ca_bundle)

    # Title
    title_pane = soup.find("div", class_="content-title-pane")
    title = ""
    subtitle = ""
    author = ""
    if title_pane:
        h3 = title_pane.find("h3")
        if h3:
            title = h3.get_text(strip=True)
        h4 = title_pane.find("h4")
        if h4:
            subtitle = h4.get_text(strip=True)
        # Author(s) — usually in <h5><a href="/node/ID">Name</a></h5>
        # Multi-author chapters may have multiple links.
        author_links = [
            a for a in title_pane.find_all("a")
            if "/node/" in a.get("href", "") or "/author/" in a.get("href", "")
        ]
        if author_links:
            author = ", ".join(a.get_text(strip=True) for a in author_links)
        # No plain-text fallback — too error-prone.  Per-chapter author
        # is reliably extracted from TOC (toc-author div) and will be
        # used by download_book() when the chapter page lacks it.

    # Body content
    body_pane = soup.find("div", class_="content-body-pane")
    body_html = ""
    body_text = ""
    citation = ""
    footnote_count = 0

    if body_pane:
        body_html = str(body_pane)

        # Extract citation (first paragraph is usually the formal citation)
        first_p = body_pane.find("p")
        if first_p:
            fp_text = first_p.get_text(strip=True)
            # Citations typically contain "in" + book title + publisher
            if "Religious Studies Center" in fp_text or "Deseret Book" in fp_text:
                citation = fp_text

        # Count footnotes
        footnotes = body_pane.find_all("a", class_="a-ref")
        footnote_count = len(footnotes)

        # Convert to plain text
        body_text = _html_to_text(body_pane)

    return {
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "body_html": body_html,
        "body_text": body_text,
        "citation": citation,
        "footnote_count": footnote_count,
    }


def _html_to_text(element: Tag) -> str:
    """Convert a BeautifulSoup element to clean plain text.

    Produces well-separated paragraphs and a clearly delimited Notes
    section at the end (when footnotes are present).
    """
    from copy import deepcopy
    el = deepcopy(element)

    # Remove script/style
    for tag in el.find_all(["script", "style"]):
        tag.decompose()

    # Remove collapsed toggle-boxes (citation + author bio)
    for tb in el.find_all("div", class_=re.compile(r"toggle-box")):
        tb.decompose()

    # Convert inline footnote references to [N]
    for a in el.find_all("a", class_="a-ref"):
        a.replace_with(f" [{a.get_text(strip=True)}]")

    # Replace back-link anchors in footnote text (a.a-note) with plain [N]
    # The anchor text already includes brackets: "[1]", "[2]", etc.
    for a in el.find_all("a", class_="a-note"):
        a.replace_with(f"{a.get_text(strip=True)} ")

    # ------------------------------------------------------------------
    # Extract body paragraphs and notes separately
    # ------------------------------------------------------------------
    body_parts: list[str] = []
    notes_parts: list[str] = []

    # Notes header (p.p-notes) and note items (p.p-note)
    notes_header = el.find("p", class_="p-notes")
    note_items = el.find_all("p", class_="p-note")

    # Remove notes from DOM so they don't appear in body text
    if notes_header:
        notes_header.decompose()
    for ni in note_items:
        text = ni.get_text(strip=True)
        if text:
            notes_parts.append(text)
        ni.decompose()

    # ------------------------------------------------------------------
    # Process body: insert paragraph breaks before block elements
    # ------------------------------------------------------------------
    _BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
                   "blockquote", "li", "tr", "ul", "ol", "table", "section"}

    for tag in el.find_all(_BLOCK_TAGS):
        tag.insert_before("\n\n")
        tag.insert_after("\n\n")

    text = el.get_text()

    # Clean up whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Split into paragraphs and reflow each one
    paragraphs = text.strip().split("\n\n")
    for para in paragraphs:
        joined = " ".join(line.strip() for line in para.split("\n") if line.strip())
        if joined:
            body_parts.append(joined)

    # Remove leading citation paragraph (formal reference)
    if body_parts and ("Religious Studies Center" in body_parts[0]
                       or "Deseret Book" in body_parts[0]):
        body_parts = body_parts[1:]

    # Remove author bio paragraph
    if body_parts and re.search(
            r"(?:is|was)\s+(?:a\s+)?(?:professor|associate|assistant|dean|chair|"
            r"instructor|lecturer|researcher|director)",
            body_parts[0]):
        body_parts = body_parts[1:]

    # ------------------------------------------------------------------
    # Assemble final text: body + notes
    # ------------------------------------------------------------------
    result = "\n\n".join(body_parts)

    if notes_parts:
        result += "\n\nNotes\n\n"
        result += "\n\n".join(notes_parts)

    return result.strip()


# ---------------------------------------------------------------------------
# Download logic
# ---------------------------------------------------------------------------

def download_book(slug: str, ca_bundle: str | None = None,
                  dry_run: bool = False, corpus_category: str = "books",
                  authority: int | None = None,
                  tags: list[str] | None = None) -> dict:
    """Download all chapters of an RSC book into the corpus."""
    logger.info("=" * 60)
    logger.info("Fetching book metadata: %s", slug)

    meta = get_book_metadata(slug, ca_bundle)
    if meta is None:
        logger.error("Book '%s' is not available for online reading", slug)
        return {"slug": slug, "error": "not available online"}

    title = meta["title"]
    authors = meta["authors"]
    chapters = meta["chapters"]
    author_str = ", ".join(authors) if authors else "Various"

    logger.info("Book: %s by %s", title, author_str)
    logger.info("Chapters: %d", len(chapters))

    if not chapters:
        logger.warning("No chapters found — book may not be released online")
        return {"slug": slug, "error": "no chapters found"}

    is_edited = meta.get("is_edited", False)
    if is_edited:
        logger.info("Multi-author (edited volume): editor(s) = %s", author_str)

    if dry_run:
        logger.info("[DRY RUN] Would download %d chapters:", len(chapters))
        for ch in chapters:
            ch_auth = ch.get("author", "")
            auth_note = f" [{ch_auth}]" if ch_auth else ""
            section = f" ({ch['section']})" if ch.get("section") else ""
            logger.info("  %s: %s%s%s", ch["slug"], ch["title"][:50],
                        auth_note, section)
        return {"slug": slug, "dry_run": True, "chapters": len(chapters)}

    # Output directory
    output_dir = CORPUS_ROOT / "en" / corpus_category / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    errors = 0

    auth_value = authority or 30
    tag_list = tags or ["rsc-byu", "academic"]

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
            if not body or len(body) < 100:
                logger.warning("  [%02d] Very short content (%d chars): %s",
                               ch_idx, len(body), ch["title"][:50])

            logger.info("  [%02d] %s — %d chars, %d notes",
                        ch_idx, ch["title"][:50], len(body),
                        ch_data["footnote_count"])

            # Write text
            txt_path.write_text(body, encoding="utf-8")

            # Resolve chapter author:
            # 1. Chapter page h5 author (most authoritative)
            # 2. TOC per-chapter author (from book page)
            # 3. Book-level author/editor string (fallback)
            ch_author = (ch_data["author"]
                         or ch.get("author", "")
                         or author_str)

            # Write metadata
            ch_meta = {
                "title": ch_data["title"] or ch["title"],
                "author": ch_author,
                "book": title,
                "chapter": ch_idx,
                "category": corpus_category,
                "subcategory": slug,
                "tags": tag_list,
                "authority": auth_value,
                "lang": "eng",
                "source_url": ch["url"],
                "source": "Religious Studies Center, BYU",
            }
            # Subtitle (prefer chapter page, fall back to TOC)
            ch_sub = ch_data["subtitle"] or ch.get("subtitle", "")
            if ch_sub:
                ch_meta["subtitle"] = ch_sub
            # Editor info for multi-author volumes
            if is_edited:
                ch_meta["editor"] = author_str
            # Section within the book (e.g., "Doctrine", "Historical Content")
            if ch.get("section"):
                ch_meta["section"] = ch["section"]
            if ch_data["citation"]:
                ch_meta["citation"] = ch_data["citation"]
            if ch_data["footnote_count"]:
                ch_meta["note_count"] = ch_data["footnote_count"]
            if meta.get("subtitle"):
                ch_meta["book_subtitle"] = meta["subtitle"]

            meta_path.write_text(
                json.dumps(ch_meta, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            written += 1

        except Exception as e:
            logger.error("  [%02d] Error: %s — %s", ch_idx, ch["title"][:50], e)
            errors += 1

        time.sleep(REQUEST_DELAY)

    logger.info("Done: %s — %d written, %d skipped, %d errors",
                slug, written, skipped, errors)
    return {
        "slug": slug,
        "title": title,
        "written": written,
        "skipped": skipped,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Download RSC BYU books into the Alejandría corpus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--list-books", action="store_true",
                        help="List books available online")
    parser.add_argument("--category", type=int, default=None,
                        help="Filter by category ID (see --help for IDs)")
    parser.add_argument("--book", type=str,
                        help="Book slug to download (from /book/{slug})")
    parser.add_argument("--corpus-category", type=str, default="books",
                        help="Corpus category (default: books)")
    parser.add_argument("--authority", type=int, default=None,
                        help="Authority value (default: 30)")
    parser.add_argument("--tags", type=str, nargs="*",
                        help="Tags for metadata")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be downloaded")
    args = parser.parse_args()

    ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE")

    if args.list_books:
        books = list_online_books(ca_bundle, args.category)
        cat_name = CATEGORIES.get(args.category, "All online") if args.category else "All online"
        print(f"\n{cat_name} -- {len(books)} books:\n")
        for b in books:
            safe_title = b['title'][:60].encode('ascii', 'replace').decode('ascii')
            print(f"  {b['slug']:50s} {safe_title}")
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
    )


if __name__ == "__main__":
    main()
