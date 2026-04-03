#!/usr/bin/env python3
"""Download "Jesus the Christ" by James E. Talmage from churchofjesuschrist.org.

Downloads all 42 chapters + preface bilingual (EN/ES), converting HTML to
structured plain text with heading hierarchy preserved. Each chapter produces
a .txt and .meta.json file.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_jesus_the_christ.py
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_jesus_the_christ.py --dry-run
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_jesus_the_christ.py --lang eng

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
MANUAL_URI = "/manual/jesus-the-christ"
REQUEST_DELAY = 0.5

LANG_MAP = {"eng": "en", "spa": "es"}

# Slug → corpus filename mapping.
# Discovered from the TOC manifest; sequential numbering for sort order.
SLUG_TO_FILENAME = {
    "preface": "00-preface",
    "chapter-1": "01-introduction",
    "chapter-2": "02-preexistence-and-foreordination",
    "chapter-3": "03-the-need-of-a-redeemer",
    "chapter-4": "04-the-antemortal-godship-of-christ",
    "chapter-5": "05-earthly-advent-predicted",
    "chapter-6": "06-the-meridian-of-time",
    "chapter-7": "07-gabriels-annunciation",
    "chapter-8": "08-the-babe-of-bethlehem",
    "chapter-9": "09-the-boy-of-nazareth",
    "chapter-10": "10-in-the-wilderness-of-judea",
    "chapter-11": "11-from-judea-to-galilee",
    "chapter-12": "12-early-public-ministry",
    "chapter-13": "13-honored-by-strangers-rejected-by-his-own",
    "chapter-14": "14-continuation-of-ministry-in-galilee",
    "chapter-15": "15-lord-of-the-sabbath",
    "chapter-16": "16-the-chosen-twelve",
    "chapter-17": "17-the-sermon-on-the-mount",
    "chapter-18": "18-as-one-having-authority",
    "chapter-19": "19-he-spake-in-parables",
    "chapter-20": "20-peace-be-still",
    "chapter-21": "21-the-apostolic-mission",
    "chapter-22": "22-a-period-of-darkening-opposition",
    "chapter-23": "23-the-transfiguration",
    "chapter-24": "24-from-sunshine-to-shadow",
    "chapter-25": "25-jesus-again-in-jerusalem",
    "chapter-26": "26-ministry-in-perea-and-judea",
    "chapter-27": "27-continuation-perean-judean-ministry",
    "chapter-28": "28-the-last-winter",
    "chapter-29": "29-on-to-jerusalem",
    "chapter-30": "30-jesus-returns-to-the-temple-daily",
    "chapter-31": "31-close-of-public-ministry",
    "chapter-32": "32-further-instruction-to-the-apostles",
    "chapter-33": "33-the-last-supper-and-the-betrayal",
    "chapter-34": "34-the-trial-and-condemnation",
    "chapter-35": "35-death-and-burial",
    "chapter-36": "36-in-the-realm-of-disembodied-spirits",
    "chapter-37": "37-the-resurrection-and-the-ascension",
    "chapter-38": "38-the-apostolic-ministry",
    "chapter-39": "39-ministry-on-the-western-hemisphere",
    "chapter-40": "40-the-long-night-of-apostasy",
    "chapter-41": "41-personal-manifestations-in-modern-times",
    "chapter-42": "42-jesus-the-christ-to-return",
}


def fetch_toc(lang: str) -> list[dict]:
    """Fetch table of contents and return list of content page URIs."""
    r = requests.get(API_URL, params={"lang": lang, "uri": MANUAL_URI}, timeout=30)
    r.raise_for_status()
    body = r.json().get("content", {}).get("body", "")
    soup = BeautifulSoup(body, "html.parser")

    pages = []
    seen_slugs = set()
    for a in soup.select('a[href*="jesus-the-christ"]'):
        href = a.get("href", "").split("?")[0]
        title = a.get_text(strip=True)
        if "/study/" in href:
            uri = href.split("/study")[1]
            slug = uri.rstrip("/").split("/")[-1]
            if slug in SLUG_TO_FILENAME and slug not in seen_slugs:
                seen_slugs.add(slug)
                pages.append({"uri": uri, "slug": slug, "title": title})

    logger.info("Found %d content pages for Jesus the Christ (%s)", len(pages), lang)
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
    """Convert chapter HTML to structured plain text.

    Preserves heading hierarchy with markdown-style markers:
    - h1 → # Title
    - h2 → ## Section
    - h3 → ### Subsection
    - h4 → #### Sub-subsection

    Endnotes are appended as a numbered list at the end.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove images, nav, reference metadata, footnote markers
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


def format_footnotes(footnotes: dict | list | None) -> str:
    """Format structured footnotes as a plain-text endnotes section."""
    if not isinstance(footnotes, dict) or not footnotes:
        return ""

    lines = ["\n\n---\nNotas\n"]
    for key in sorted(footnotes.keys(), key=lambda k: int(k) if k.isdigit() else k):
        note = footnotes[key]
        if isinstance(note, dict):
            marker = note.get("marker", key)
            text = note.get("text", "")
            if text:
                # Strip HTML from footnote text
                text = BeautifulSoup(text, "html.parser").get_text(strip=True)
                lines.append(f"  {marker}. {text}")

    return "\n".join(lines) if len(lines) > 1 else ""


def build_meta(page_data: dict, uri: str, slug: str, lang: str) -> dict:
    """Build .meta.json for a chapter."""
    return {
        "title": page_data["title"],
        "author": "James E. Talmage",
        "book": "Jesus the Christ",
        "category": "manuals",
        "subcategory": "jesus-the-christ",
        "tags": ["christology", "gospels", "life-of-christ", "apostle-authored"],
        "authority": 45,
        "lang": lang,
        "source_url": f"{BASE_URL}/study{uri}?lang={lang}",
        "note_count": len(page_data.get("footnotes", {})) if isinstance(page_data.get("footnotes"), dict) else 0,
    }


def download_book(lang: str, dry_run: bool = False) -> dict:
    """Download all chapters for one language."""
    corpus_lang = LANG_MAP.get(lang, lang)
    output_dir = CORPUS_ROOT / corpus_lang / "manuals" / "jesus-the-christ"

    pages = fetch_toc(lang)
    if not pages:
        logger.warning("No pages found for %s — trying fallback with known slugs", lang)
        pages = _fallback_pages()

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    skipped = 0
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
            skipped += 1
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

            # Append footnotes as endnotes
            endnotes = format_footnotes(page_data["footnotes"])
            if endnotes:
                text += endnotes

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

    stats = {"lang": lang, "pages": len(pages), "downloaded": downloaded, "skipped": skipped, "errors": errors}
    logger.info("Stats: %s", json.dumps(stats))
    return stats


def _fallback_pages() -> list[dict]:
    """Generate page list from known slugs if TOC parsing fails."""
    pages = []
    for slug, filename in sorted(SLUG_TO_FILENAME.items(), key=lambda x: x[1]):
        uri = f"{MANUAL_URI}/{slug}"
        title = slug.replace("-", " ").title()
        pages.append({"uri": uri, "slug": slug, "title": title})
    return pages


def main():
    parser = argparse.ArgumentParser(description="Download Jesus the Christ by James E. Talmage")
    parser.add_argument("--lang", help="Language: eng or spa (default: both)")
    parser.add_argument("--dry-run", action="store_true", help="List pages without downloading")
    args = parser.parse_args()

    languages = [args.lang] if args.lang else ["eng", "spa"]

    all_stats = []
    for lang in languages:
        stats = download_book(lang, dry_run=args.dry_run)
        all_stats.append(stats)

    logger.info("=" * 60)
    for s in all_stats:
        logger.info(
            "%s: %d pages, %d downloaded, %d skipped, %d errors",
            s["lang"], s["pages"], s["downloaded"], s["skipped"], s["errors"],
        )


if __name__ == "__main__":
    main()
