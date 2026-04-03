#!/usr/bin/env python3
"""Download Preach My Gospel (2023 edition) from churchofjesuschrist.org.

Downloads all chapters bilingual (EN/ES), converting HTML to structured
plain text with heading hierarchy preserved. Each chapter produces a .txt
and .meta.json file.

Chapter 3 is split into 6 sub-pages (intro, invitation, 4 lessons) on
the site; each becomes its own file in the corpus.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_pme.py
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_pme.py --dry-run
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_pme.py --lang eng

Requires: pandoc, requests, beautifulsoup4
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CORPUS_ROOT = Path(__file__).resolve().parent.parent / "corpus"
BASE_URL = "https://www.churchofjesuschrist.org"
API_URL = f"{BASE_URL}/study/api/v3/language-pages/type/content"
REQUEST_DELAY = 0.5

LANG_MAP = {"eng": "en", "spa": "es"}

# Manual slug → corpus filename mapping.
# Preserves chapter numbering and readable names.
SLUG_TO_FILENAME = {
    "01-first-presidency-message": "00-first-presidency-message",
    "02-intro": "00-introduction",
    "03-chapter-1": "01-fulfill-your-missionary-purpose",
    "04-chapter-2": "02-search-the-scriptures",
    "06-chapter-3-intro": "03-00-study-and-teach-intro",
    "07-chapter-3-invite": "03-01-invitation-to-be-baptized",
    "08-chapter-3-lesson-1": "03-02-message-of-the-restoration",
    "09-chapter-3-lesson-2": "03-03-plan-of-salvation",
    "10-chapter-3-lesson-3": "03-04-gospel-of-jesus-christ",
    "11-chapter-3-lesson-4": "03-05-becoming-lifelong-disciples",
    "12-chapter-4": "04-seek-and-rely-on-the-spirit",
    "13-chapter-5": "05-power-of-the-book-of-mormon",
    "14-chapter-6": "06-christlike-attributes",
    "15-chapter-7": "07-learn-your-mission-language",
    "16-chapter-8": "08-goals-and-plans",
    "17-chapter-9": "09-find-people-to-teach",
    "18-chapter-10": "10-teach-to-build-faith",
    "19-chapter-11": "11-help-people-make-commitments",
    "20-chapter-12": "12-prepare-for-baptism-and-confirmation",
    "21-chapter-13": "13-unite-with-leaders-and-members",
}


def fetch_toc(lang: str) -> list[dict]:
    """Fetch table of contents and return list of content page URIs."""
    r = requests.get(API_URL, params={"lang": lang, "uri": "/manual/preach-my-gospel-2023"}, timeout=30)
    r.raise_for_status()
    body = r.json().get("content", {}).get("body", "")
    soup = BeautifulSoup(body, "html.parser")

    pages = []
    for a in soup.select('a[href*="preach-my-gospel-2023"]'):
        href = a.get("href", "").split("?")[0]
        title = a.get_text(strip=True)
        if "/study/" in href:
            uri = href.split("/study")[1]
            # Extract slug (last part of URI)
            slug = uri.rstrip("/").split("/")[-1]
            if slug in SLUG_TO_FILENAME:
                pages.append({"uri": uri, "slug": slug, "title": title})

    logger.info("Found %d content pages for PME (%s)", len(pages), lang)
    return pages


def fetch_page(uri: str, lang: str) -> dict | None:
    """Fetch a single content page and return parsed data."""
    r = requests.get(API_URL, params={"lang": lang, "uri": uri}, timeout=30)
    r.raise_for_status()
    data = r.json()

    body = data.get("content", {}).get("body", "")
    if not body or len(body) < 200:
        return None

    meta_title = data.get("meta", {}).get("title", "")
    footnotes = data.get("content", {}).get("footnotes", {})

    return {
        "body_html": body,
        "title": meta_title,
        "footnotes": footnotes,
    }


def html_to_structured_text(html: str) -> str:
    """Convert PME chapter HTML to structured plain text.

    Preserves heading hierarchy with markdown-style markers:
    - h1 → # Title
    - h2 → ## Section
    - h3 → ### Subsection
    - h4 → #### Sub-subsection

    Sidebars are marked with [SIDEBAR] ... [/SIDEBAR] blocks.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove images, nav, reference/short-reference
    for sel in ("img", "nav", "figure", ".manifest", "p.reference",
                "p.short-reference", "sup.marker", ".study-note-ref"):
        for el in soup.select(sel):
            el.decompose()

    # Convert headings to markdown-style markers BEFORE pandoc
    heading_map = {"h1": "#", "h2": "##", "h3": "###", "h4": "####"}
    for tag_name, marker in heading_map.items():
        for h in soup.find_all(tag_name):
            text = h.get_text(strip=True)
            h.replace_with(f"\n\n{marker} {text}\n\n")

    # Convert sidebars to marked blocks
    for aside in soup.find_all("aside"):
        inner_html = aside.decode_contents()
        aside.replace_with(f'\n\n[SIDEBAR]\n{inner_html}\n[/SIDEBAR]\n\n')

    # Convert to text via pandoc
    result = subprocess.run(
        ["pandoc", "-f", "html", "-t", "plain", "--wrap=none"],
        input=str(soup).encode("utf-8"),
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pandoc failed: {result.stderr.decode('utf-8', errors='replace')}")

    text = result.stdout.decode("utf-8").strip()

    # Clean up excessive whitespace
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    return text


def _extract_scripture_refs_from_footnotes(footnotes: dict) -> list[str]:
    """Extract scripture reference URIs from API footnote dict."""
    refs = []
    if not isinstance(footnotes, dict):
        return refs
    for _key, note in footnotes.items():
        for uri in note.get("referenceUris", []):
            if uri not in refs:
                refs.append(uri)
    return refs


def build_meta(page_data: dict, uri: str, slug: str, lang: str) -> dict:
    """Build .meta.json for a PME chapter."""
    footnotes = page_data.get("footnotes", {})
    scripture_refs = _extract_scripture_refs_from_footnotes(footnotes)
    note_count = len(footnotes) if isinstance(footnotes, dict) else 0

    meta: dict = {
        "title": page_data["title"],
        "book": "Preach My Gospel",
        "manual": "Preach My Gospel",
        "edition": "2023",
        "category": "manuals",
        "subcategory": "preach-my-gospel",
        "tags": ["missionary", "teaching", "gospel"],
        "authority": 60,
        "lang": lang,
        "source_url": f"{BASE_URL}/study{uri}?lang={lang}",
        "note_count": note_count,
    }
    if scripture_refs:
        meta["scripture_refs"] = scripture_refs
    return meta


def download_pme(lang: str, dry_run: bool = False) -> dict:
    """Download all PME chapters for one language."""
    corpus_lang = LANG_MAP.get(lang, lang)
    output_dir = CORPUS_ROOT / corpus_lang / "manuals" / "preach-my-gospel"

    pages = fetch_toc(lang)
    if not pages:
        logger.warning("No pages found for %s", lang)
        return {"lang": lang, "pages": 0, "downloaded": 0, "errors": 0}

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    errors = 0

    for i, page in enumerate(pages, 1):
        filename = SLUG_TO_FILENAME[page["slug"]]
        txt_path = output_dir / f"{filename}.txt"
        meta_path = output_dir / f"{filename}.meta.json"

        logger.info("[%d/%d] %s → %s", i, len(pages), page["title"][:60], filename)

        if dry_run:
            downloaded += 1
            continue

        if txt_path.exists():
            logger.info("  Already exists, skipping")
            downloaded += 1
            continue

        time.sleep(REQUEST_DELAY)

        try:
            page_data = fetch_page(page["uri"], lang)
            if page_data is None:
                logger.warning("  No content returned")
                errors += 1
                continue

            # Convert to structured text
            text = html_to_structured_text(page_data["body_html"])
            if not text.strip():
                logger.warning("  Empty text after conversion")
                errors += 1
                continue

            # Build metadata
            meta = build_meta(page_data, page["uri"], page["slug"], lang)

            # Write files
            txt_path.write_text(text + "\n", encoding="utf-8")
            meta_path.write_text(
                json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            downloaded += 1
            logger.info("  Saved: %s (%d chars)", filename, len(text))

        except Exception:
            logger.exception("  Failed to download %s", page["uri"])
            errors += 1

    stats = {"lang": lang, "pages": len(pages), "downloaded": downloaded, "errors": errors}
    logger.info("Stats: %s", json.dumps(stats))
    return stats


def main():
    parser = argparse.ArgumentParser(description="Download Preach My Gospel (2023)")
    parser.add_argument("--lang", help="Language: eng or spa (default: both)")
    parser.add_argument("--dry-run", action="store_true", help="List pages without downloading")
    args = parser.parse_args()

    languages = [args.lang] if args.lang else ["eng", "spa"]

    all_stats = []
    for lang in languages:
        stats = download_pme(lang, dry_run=args.dry_run)
        all_stats.append(stats)

    logger.info("=" * 60)
    for s in all_stats:
        logger.info("%s: %d pages, %d downloaded, %d errors", s["lang"], s["pages"], s["downloaded"], s["errors"])


if __name__ == "__main__":
    main()
