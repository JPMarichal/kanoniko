#!/usr/bin/env python3
"""Download articles from Interpreter: A Journal of Latter-day Saint Faith
and Scholarship (interpreterfoundation.org) into the Alejandria corpus.

Discovery: journal-sitemap.xml lists all article URLs (~650).
Extraction: each article page has full HTML text, footnotes, metadata.

Usage:
    # List all articles from sitemap (prints slug, no download)
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_interpreter.py --list

    # Download all articles (Articles + Essays only, skip Book Reviews)
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_interpreter.py --all

    # Download a single article by slug
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_interpreter.py --article the-book-of-mormon-witnesses-and-their-challenge-to-secularism

    # Dry run
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_interpreter.py --all --dry-run

    # Include book reviews (excluded by default)
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_interpreter.py --all --include-reviews
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

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

BASE_URL = "https://interpreterfoundation.org"
SITEMAP_URL = f"{BASE_URL}/journal-sitemap.xml"
CORPUS_ROOT = Path(__file__).resolve().parent.parent / "corpus"
OUTPUT_DIR = CORPUS_ROOT / "en" / "books" / "interpreter-journal"
AUTHORITY = 25

# Categories to exclude by default
EXCLUDE_CATEGORIES = {"book review", "review essay"}

# Rate limit: be respectful
REQUEST_DELAY = 1.5  # seconds between requests

# Sitemap XML namespace
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

_session: requests.Session | None = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
        })
        ca = os.environ.get("REQUESTS_CA_BUNDLE")
        if ca:
            _session.verify = ca
    return _session


def _get(url: str) -> requests.Response:
    """GET with CA bundle, timeout, and session reuse."""
    session = _get_session()
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp


def _soup(url: str) -> BeautifulSoup:
    """Fetch URL and return parsed BeautifulSoup."""
    resp = _get(url)
    return BeautifulSoup(resp.text, "html.parser")


# ---------------------------------------------------------------------------
# Sitemap discovery
# ---------------------------------------------------------------------------

def fetch_article_urls() -> list[dict]:
    """Parse journal-sitemap.xml and return list of {slug, url}."""
    resp = _get(SITEMAP_URL)
    root = ET.fromstring(resp.content)

    articles = []
    for url_el in root.findall("sm:url", SITEMAP_NS):
        loc = url_el.find("sm:loc", SITEMAP_NS)
        if loc is None or loc.text is None:
            continue
        article_url = loc.text.strip()
        # Extract slug from URL
        path = urlparse(article_url).path
        # Pattern: /journal/{slug} or /journal/{slug}/
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 2 and parts[0] == "journal":
            slug = parts[1]
            # Skip index pages and non-article URLs
            if slug in ("indexes", "volume", "all-papers"):
                continue
            articles.append({"slug": slug, "url": article_url})

    logger.info("Sitemap: found %d article URLs", len(articles))
    return articles


# ---------------------------------------------------------------------------
# Article extraction
# ---------------------------------------------------------------------------

def _clean_text(el: Tag) -> str:
    """Extract clean text from an HTML element, preserving paragraph breaks."""
    lines = []
    for child in el.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                lines.append(text)
        elif isinstance(child, Tag):
            if child.name in ("p", "div", "blockquote", "h1", "h2", "h3",
                              "h4", "h5", "h6"):
                text = child.get_text(separator=" ", strip=True)
                if text:
                    lines.append(text)
                    lines.append("")  # blank line after block elements
            elif child.name in ("ul", "ol"):
                for li in child.find_all("li", recursive=False):
                    li_text = li.get_text(separator=" ", strip=True)
                    if li_text:
                        lines.append(f"  - {li_text}")
                lines.append("")
            elif child.name == "table":
                lines.append("[Table omitted]")
                lines.append("")
            elif child.name == "hr":
                lines.append("---")
                lines.append("")
            elif child.name in ("sup", "sub", "span", "em", "strong", "a",
                                "i", "b"):
                # Inline elements — will be captured by parent
                pass
            else:
                text = child.get_text(separator=" ", strip=True)
                if text:
                    lines.append(text)
    return "\n".join(lines).strip()


def _extract_footnotes(soup: BeautifulSoup) -> list[str]:
    """Extract footnotes from the article.

    Interpreter uses various footnote patterns:
    - sdfootnote{N}anc anchors
    - footnote{N}anc anchors
    - <ol> at the end with <li> elements
    """
    footnotes = []

    # Pattern 1: sdfootnote anchors
    for i in range(1, 500):
        fn = soup.find(id=f"sdfootnote{i}anc")
        if fn is None:
            fn = soup.find(id=f"footnote{i}anc")
        if fn is None:
            # Try parent <p> or <div> containing the anchor
            anchor = soup.find("a", attrs={"name": f"sdfootnote{i}anc"})
            if anchor:
                fn = anchor.find_parent(["p", "div", "li"])
        if fn is None:
            break
        text = fn.get_text(separator=" ", strip=True)
        # Remove the footnote number prefix if present
        text = re.sub(r"^\[?\d+\]?\s*", "", text)
        if text:
            footnotes.append(text)

    # Pattern 2: ordered list at end of article
    if not footnotes:
        # Look for the last <ol> which is typically footnotes
        all_ols = soup.find_all("ol")
        if all_ols:
            last_ol = all_ols[-1]
            # Heuristic: footnotes ol usually has many items with links
            items = last_ol.find_all("li", recursive=False)
            if len(items) >= 3:
                for li in items:
                    text = li.get_text(separator=" ", strip=True)
                    text = re.sub(r"^\[?\d+\]?\s*", "", text)
                    if text:
                        footnotes.append(text)

    return footnotes


def _is_footnote_element(el: Tag) -> bool:
    """Check if an element is a footnote (contains sdfootnote{N}anc anchor).

    Interpreter articles interleave footnote paragraphs with body text.
    Footnotes contain an <a name="sdfootnote{N}anc"> anchor, while body
    paragraphs may contain <a name="sdfootnote{N}sym"> reference marks.
    The key distinction: 'anc' = footnote text, 'sym' = inline reference.
    """
    # Check for 'anc' anchors (footnote text) — by name or id attribute
    anc = el.find("a", attrs={"name": re.compile(r"(sdfootnote|footnote)\d+anc")})
    if anc:
        return True
    anc = el.find("a", id=re.compile(r"(sdfootnote|footnote)\d+anc"))
    if anc:
        return True
    return False


def _strip_footnote_refs(text: str) -> str:
    """Remove inline footnote reference numbers like ' 1 ' or ' 32 '
    that appear at the end of sentences in the body text."""
    # Pattern: space + 1-3 digit number at end, or before period/comma
    text = re.sub(r"\s+\d{1,3}\s*$", "", text)
    return text


def _extract_body(cms_div: Tag) -> tuple[str, str, list[str]]:
    """Extract body text, abstract, and footnotes from the cmstext div.

    The cmstext div contains the full article with footnotes interleaved.
    We separate them by checking each block element: if it contains an
    'anc' anchor, it's a footnote; otherwise it's body text.

    Returns (body_text, abstract, footnotes_list).
    """
    abstract = ""
    body_parts: list[str] = []
    footnotes: list[str] = []

    # Iterate over direct children (block elements) of cmstext
    # Using recursive=False on find_all won't work because some articles
    # have wrapper divs. Instead, find all block elements and check ancestry.
    for el in cms_div.find_all(
        ["p", "h2", "h3", "h4", "h5", "h6", "blockquote",
         "ul", "ol", "table", "hr"],
        recursive=True,
    ):
        # Skip <p> nested inside blockquote (handled when we process blockquote)
        if el.name == "p" and el.find_parent("blockquote"):
            continue

        text = el.get_text(separator=" ", strip=True)
        if not text:
            continue

        # --- Footnote separation ---
        if _is_footnote_element(el):
            fn_text = re.sub(r"^\[?\d+\]?\s*", "", text)
            if fn_text:
                footnotes.append(fn_text)
            continue

        # Also check if a parent blockquote is a footnote
        if el.name == "blockquote" and _is_footnote_element(el):
            fn_text = re.sub(r"^\[?\d+\]?\s*", "", text)
            if fn_text:
                footnotes.append(fn_text)
            continue

        # --- Abstract detection ---
        if not abstract and not body_parts and el.name == "p":
            children = [c for c in el.children
                        if not (isinstance(c, NavigableString) and not c.strip())]
            if (len(children) == 1
                    and hasattr(children[0], "name")
                    and children[0].name in ("em", "i")
                    and len(text) > 80):
                abstract = text
                body_parts.append(text)
                body_parts.append("")
                continue

        # --- Body content ---
        if el.name in ("h2", "h3", "h4", "h5", "h6"):
            body_parts.append(f"\n## {text}\n")
        elif el.name == "blockquote":
            body_parts.append(f"> {text}\n")
        elif el.name in ("ul", "ol"):
            for li in el.find_all("li", recursive=False):
                li_text = li.get_text(separator=" ", strip=True)
                if li_text:
                    body_parts.append(f"  - {li_text}")
            body_parts.append("")
        elif el.name == "table":
            body_parts.append("[Table omitted]")
            body_parts.append("")
        elif el.name == "hr":
            body_parts.append("---")
            body_parts.append("")
        else:
            body_parts.append(text)
            body_parts.append("")

    body_text = "\n".join(body_parts).strip()

    # Append footnotes to body
    if footnotes:
        body_text += "\n\n---\nNotes\n\n"
        for i, fn in enumerate(footnotes, 1):
            body_text += f"[{i}] {fn}\n\n"

    return body_text, abstract, footnotes


def extract_article(url: str, slug: str = "") -> dict | None:
    """Fetch an article page and extract all content.

    The Interpreter site uses Next.js with this DOM structure:
        div.journalArticleMainContainer
          div.article-dark-container  (nav + citation line)
          div.journalArticleContent.container.ssr
            div.imgContentOuter
              div.leftAuthor          (author sidebar + download links)
              div.imgContent
                div.textContent.cmstext   <-- article body here
            div.aboutAuthorWrapper
            div.commentWrapper

    Returns dict with keys:
        title, author, author_slug, abstract, body_text, footnotes,
        footnote_count, volume, year, pages, category, pdf_url,
        source_url
    Returns None if the page cannot be parsed.
    """
    soup = _soup(url)

    # --- Title ---
    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)

    if not title:
        logger.warning("No title found at %s", url)
        return None

    # --- Author ---
    author = ""
    author_slug_val = ""
    # Author link in the aboutAuthorWrapper or leftAuthor
    author_link = soup.find("a", href=re.compile(r"/(?:all|journal)/author/"))
    if author_link:
        author = author_link.get_text(strip=True)
        href = author_link.get("href", "")
        parts = href.rstrip("/").split("/")
        author_slug_val = parts[-1] if parts else ""

    # Fallback: aboutAuthorWrapper often has the name
    if not author:
        about = soup.find("div", class_="aboutAuthorWrapper")
        if about:
            # First strong or bold text is usually the name
            name_el = about.find(["strong", "b", "h3", "h4"])
            if name_el:
                author = name_el.get_text(strip=True)

    # --- Category detection ---
    # Primary: slug prefix (most reliable)
    category = "article"
    if slug.startswith("book-review"):
        category = "book review"
    elif slug.startswith("review-essay") or slug.startswith("review-of-"):
        category = "review essay"
    # Secondary: title prefix
    title_lower = title.lower()
    if title_lower.startswith("book review"):
        category = "book review"
    elif title_lower.startswith("review essay") or title_lower.startswith("review of"):
        category = "review essay"

    # --- Citation line: volume, year, pages ---
    # Located in article-dark-container, pattern:
    # "Interpreter: A Journal of ... Scripture|Scholarship NN (YYYY) : pages"
    volume = 0
    year = 0
    pages = ""

    dark = soup.find("div", class_="article-dark-container")
    cite_text = dark.get_text() if dark else soup.get_text()[:2000]
    vol_match = re.search(
        r"(?:Scholarship|Scripture)\s+(\d+)\s+\((\d{4})\)\s*:\s*([\divxlc]+[-–][\divxlc]+|[\divxlc]+)",
        cite_text,
    )
    if vol_match:
        volume = int(vol_match.group(1))
        year = int(vol_match.group(2))
        pages = vol_match.group(3)

    # --- PDF URL ---
    pdf_url = ""
    left = soup.find("div", class_="leftAuthor")
    if left:
        pdf_link = left.find("a", href=re.compile(r"cdn\.interpreterfoundation\.org.*PDF"))
        if pdf_link:
            pdf_url = pdf_link["href"]
    if not pdf_url:
        pdf_link = soup.find("a", href=re.compile(r"cdn\.interpreterfoundation\.org.*PDF"))
        if pdf_link:
            pdf_url = pdf_link["href"]

    # --- Body text, abstract, footnotes ---
    cms_div = soup.find("div", class_="cmstext")
    if not cms_div:
        # Fallback: try textContent
        cms_div = soup.find("div", class_="textContent")
    if not cms_div:
        logger.warning("No cmstext/textContent div at %s", url)
        return None

    body_text, abstract, footnotes = _extract_body(cms_div)

    if not body_text or len(body_text) < 100:
        logger.warning("Very short body (%d chars) at %s", len(body_text), url)

    return {
        "title": title,
        "author": author,
        "author_slug": author_slug_val,
        "abstract": abstract,
        "body_text": body_text,
        "footnotes": footnotes,
        "footnote_count": len(footnotes),
        "volume": volume,
        "year": year,
        "pages": pages,
        "category": category,
        "pdf_url": pdf_url,
        "source_url": url,
    }


# ---------------------------------------------------------------------------
# Download pipeline
# ---------------------------------------------------------------------------

def download_article(slug: str, url: str, dry_run: bool = False) -> str:
    """Download a single article and save to corpus.

    Returns: "written", "skipped", "excluded", or "error".
    """
    txt_path = OUTPUT_DIR / f"{slug}.txt"
    meta_path = OUTPUT_DIR / f"{slug}.meta.json"

    if txt_path.exists():
        logger.info("  Already exists: %s", slug[:60])
        return "skipped"

    if dry_run:
        logger.info("  [DRY RUN] Would download: %s", slug[:60])
        return "written"

    try:
        data = extract_article(url, slug=slug)
        if data is None:
            logger.warning("  Could not parse: %s", slug[:60])
            return "error"

        # Check category filter
        if data["category"].lower() in EXCLUDE_CATEGORIES:
            logger.info("  Excluded (%s): %s", data["category"], slug[:60])
            return "excluded"

        body = data["body_text"]
        if not body or len(body) < 200:
            logger.warning("  Very short content (%d chars): %s",
                           len(body), slug[:60])

        # Write text
        txt_path.write_text(body, encoding="utf-8")

        # Write metadata
        meta = {
            "title": data["title"],
            "author": data["author"],
            "author_slug": data["author_slug"],
            "volume": data["volume"],
            "year": data["year"],
            "pages": data["pages"],
            "category": data["category"],
            "source_url": data["source_url"],
            "source": "Interpreter Foundation",
            "authority": AUTHORITY,
            "lang": "eng",
            "tags": ["interpreter", "academic", "peer-reviewed"],
        }
        if data["abstract"]:
            meta["abstract"] = data["abstract"]
        if data["pdf_url"]:
            meta["pdf_url"] = data["pdf_url"]
        if data["footnote_count"]:
            meta["note_count"] = data["footnote_count"]

        meta_path.write_text(
            json.dumps(meta, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        logger.info("  [OK] %s — %d chars, %d notes, vol %d (%d)",
                     data["title"][:50], len(body),
                     data["footnote_count"], data["volume"], data["year"])
        return "written"

    except Exception as e:
        logger.error("  Error on %s: %s", slug[:60], e)
        return "error"


def download_all(dry_run: bool = False, include_reviews: bool = False,
                 limit: int = 0) -> dict:
    """Download all articles from the journal sitemap.

    Args:
        dry_run: if True, only log what would be downloaded
        include_reviews: if True, include Book Reviews and Review Essays
        limit: if > 0, stop after this many downloads (for testing)

    Returns summary dict.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    articles = fetch_article_urls()
    logger.info("Starting download of %d articles (dry_run=%s, reviews=%s)",
                len(articles), dry_run, include_reviews)

    stats = {"written": 0, "skipped": 0, "excluded": 0, "error": 0}

    for i, art in enumerate(articles, 1):
        slug = art["slug"]
        url = art["url"]

        logger.info("[%d/%d] %s", i, len(articles), slug[:70])
        result = download_article(slug, url, dry_run=dry_run)
        stats[result] = stats.get(result, 0) + 1

        if not dry_run and result in ("written", "error"):
            time.sleep(REQUEST_DELAY)

        if limit and stats["written"] >= limit:
            logger.info("Reached limit of %d downloads, stopping", limit)
            break

    logger.info("=== DONE === Written: %d | Skipped: %d | Excluded: %d | Errors: %d",
                stats["written"], stats["skipped"], stats["excluded"], stats["error"])
    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Download Interpreter Journal articles into the Alejandria corpus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true",
                       help="List all article slugs from sitemap (no download)")
    group.add_argument("--all", action="store_true",
                       help="Download all articles")
    group.add_argument("--article", type=str, metavar="SLUG",
                       help="Download a single article by slug")

    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be downloaded without writing files")
    parser.add_argument("--include-reviews", action="store_true",
                        help="Include Book Reviews and Review Essays (excluded by default)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Stop after N downloads (for testing)")

    args = parser.parse_args()

    if args.list:
        articles = fetch_article_urls()
        for art in articles:
            print(f"{art['slug']}")
        print(f"\nTotal: {len(articles)} articles in sitemap")
        return

    if args.article:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        url = f"{BASE_URL}/journal/{args.article}"
        result = download_article(args.article, url, dry_run=args.dry_run)
        print(f"Result: {result}")
        return

    if args.all:
        if args.include_reviews:
            EXCLUDE_CATEGORIES.clear()
        stats = download_all(
            dry_run=args.dry_run,
            include_reviews=args.include_reviews,
            limit=args.limit,
        )
        return


if __name__ == "__main__":
    main()
