#!/usr/bin/env python3
"""Download JST Appendix from churchofjesuschrist.org.

The JST has a two-level structure: book index pages → chapter verse pages.
Some chapters are just redirects to PGP content (already in corpus); those
produce a study-intro note only. Others have actual JST verse text.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_jst.py --lang eng
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_jst.py --lang spa
    python scripts/scrape_jst.py --lang eng --dry-run
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

JST_PREFIX = "/study/scriptures/jst"


def get_session(ca_bundle: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; AlejandriaBot/1.0; scripture-study)"
    })
    session.verify = ca_bundle or True
    return session


def fetch_page(url: str, session: requests.Session) -> Optional[BeautifulSoup]:
    try:
        r = session.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = "utf-8"
        return BeautifulSoup(r.text, "lxml")
    except requests.RequestException as e:
        print(f"    ERROR: {e}", file=sys.stderr)
        return None


def get_book_slugs(lang: str, session: requests.Session) -> list[str]:
    """Get JST book slugs (jst-gen, jst-ex, jst-matt, etc.)."""
    url = f"{BASE_URL}{JST_PREFIX}?lang={lang}"
    soup = fetch_page(url, session)
    if not soup:
        return []

    slugs = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].split("?")[0]
        if f"{JST_PREFIX}/" not in href:
            continue
        slug = href.split(f"{JST_PREFIX}/")[-1].strip("/")
        if not slug or "/" in slug or slug in seen or slug == "introduction":
            continue
        seen.add(slug)
        slugs.append(slug)

    return slugs


def get_chapter_urls(book_slug: str, lang: str,
                     session: requests.Session) -> list[tuple[str, str]]:
    """Get chapter sub-page URLs for a JST book. Returns (slug, title) pairs."""
    url = f"{BASE_URL}{JST_PREFIX}/{book_slug}?lang={lang}"
    soup = fetch_page(url, session)
    if not soup:
        return []

    chapters = []
    seen = set()
    prefix = f"{JST_PREFIX}/{book_slug}/"

    for a in soup.find_all("a", href=True):
        href = a["href"].split("?")[0]
        if prefix not in href:
            continue
        ch_slug = href.split(prefix)[-1].strip("/")
        if not ch_slug or ch_slug in seen:
            continue
        seen.add(ch_slug)
        title = a.get_text().strip()
        chapters.append((ch_slug, title))

    return chapters


def scrape_chapter(book_slug: str, ch_slug: str, lang: str,
                   session: requests.Session) -> Optional[dict]:
    """Scrape a single JST chapter page."""
    url = f"{BASE_URL}{JST_PREFIX}/{book_slug}/{ch_slug}?lang={lang}"
    soup = fetch_page(url, session)
    if not soup:
        return None

    metadata = {}

    # Title
    h1 = soup.find("h1")
    if h1:
        metadata["title"] = h1.get_text().strip()

    # Section heading (h2 with compare info)
    h2 = soup.find("h2")
    if h2:
        metadata["heading"] = h2.get_text().strip()

    # Study intro
    intro = soup.find("p", class_=lambda c: c and "study-intro" in str(c))
    if intro:
        metadata["study_intro"] = intro.get_text().strip()

    # Summary
    summary = soup.find("p", class_=lambda c: c and "study-summary" in str(c))
    if summary:
        metadata["summary"] = summary.get_text().strip()

    metadata["source_url"] = url

    # Extract verses
    verses = []
    for vel in soup.find_all("p", class_=lambda c: c and "verse" in str(c)):
        # Get verse number
        vn_span = vel.find("span", class_="verse-number")
        if vn_span:
            try:
                vnum = int(vn_span.get_text().strip())
            except ValueError:
                vnum = None
            vn_span.decompose()
        else:
            vnum = None

        # Remove footnote markers
        for sup in vel.find_all("sup", class_="marker"):
            sup.decompose()

        text = re.sub(r"\s+", " ", vel.get_text()).strip()
        if text:
            verses.append((vnum, text))

    # Build text
    if verses:
        lines = []
        for vnum, vtext in verses:
            if vnum is not None:
                lines.append(f"{vnum} {vtext}")
            else:
                lines.append(vtext)
        text = "\n".join(lines)
    else:
        # No verses — might be a redirect/reference page
        # Extract any prose from body-block
        body = soup.find("div", class_="body-block")
        parts = []
        if body:
            for el in body.find_all(["p", "h2"]):
                if el.find_parent("nav") or el.find_parent("footer"):
                    continue
                t = re.sub(r"\s+", " ", el.get_text()).strip()
                if t:
                    parts.append(t)
        text = "\n\n".join(parts)

    return {"text": text, "metadata": metadata, "verse_count": len(verses)}


def main():
    parser = argparse.ArgumentParser(description="Scrape JST Appendix")
    parser.add_argument("--lang", required=True, choices=["eng", "spa"])
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    lang_dir = "en" if args.lang == "eng" else "es"
    corpus_dir = CORPUS_DIR / lang_dir / "study-aids" / "jst-appendix"

    ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE", "")
    session = get_session(ca_bundle)

    print(f"=== JST Appendix ({args.lang}) ===")
    print(f"  Output dir: {corpus_dir}")

    # Get book slugs
    books = get_book_slugs(args.lang, session)
    print(f"  Found {len(books)} JST books: {', '.join(books)}")

    stats = {"files": 0, "verses": 0, "reference_only": 0, "errors": 0}

    for book_slug in books:
        time.sleep(args.delay)
        chapters = get_chapter_urls(book_slug, args.lang, session)
        print(f"\n  {book_slug}: {len(chapters)} chapters")

        for ch_slug, ch_title in chapters:
            time.sleep(args.delay)
            label = f"{book_slug}/{ch_slug}"
            print(f"    {label} ...", end=" ", flush=True)

            result = scrape_chapter(book_slug, ch_slug, args.lang, session)
            if not result:
                print("ERROR")
                stats["errors"] += 1
                continue

            text = result["text"]
            metadata = result["metadata"]
            vc = result["verse_count"]

            if not text.strip():
                print("EMPTY")
                continue

            if vc > 0:
                print(f"OK ({vc} verses, {len(text)} chars)")
                stats["verses"] += vc
            else:
                print(f"REF ({len(text)} chars) — {text[:60]}...")
                stats["reference_only"] += 1

            if args.dry_run:
                print(f"      [DRY RUN] Would write: {corpus_dir / book_slug / ch_slug}.txt")
            else:
                out_dir = corpus_dir / book_slug
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / f"{ch_slug}.txt").write_text(text, encoding="utf-8")
                (out_dir / f"{ch_slug}.meta.json").write_text(
                    json.dumps(metadata, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

            stats["files"] += 1

    print(f"\n=== Summary ===")
    action = "would be written" if args.dry_run else "written"
    print(f"  Files {action}: {stats['files']}")
    print(f"  Total verses: {stats['verses']}")
    print(f"  Reference-only pages: {stats['reference_only']}")
    print(f"  Errors: {stats['errors']}")


if __name__ == "__main__":
    main()
