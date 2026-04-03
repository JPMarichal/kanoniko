#!/usr/bin/env python3
"""Download the Christmas Study Plan from churchofjesuschrist.org.

The plan is annual (year-suffixed slug) with 9 pages:
- Intro + Light the World overview
- 7 daily readings (Dec 19–25)

Each page includes: devotional prose, scripture passages with discussion
prompts, video links, children's activities, and service ideas.
Footnotes are sparse (1 per chapter) but always captured.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_christmas_study_plan.py
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_christmas_study_plan.py --year 2024
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_christmas_study_plan.py --lang spa
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_christmas_study_plan.py --dry-run

Requires: pandoc, requests, beautifulsoup4
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.church_scraper import (
    ChurchSession, TocEntry, fetch_api_page,
    discover_toc_api, html_to_structured_text,
    extract_footnotes_api, format_footnotes_text, footnotes_to_meta,
    extract_scripture_refs_from_html, write_corpus_file,
    build_source_url, add_common_args, get_languages,
    DownloadStats, CORPUS_ROOT,
)
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

LANG_MAP = {"eng": "en", "spa": "es"}
DEFAULT_YEAR = 2024

# Known slug order — the TOC omits the intro and light-the-world from
# the manifest link list in some languages; keeping a full ordered map
# ensures both are always captured.
SLUG_ORDER = [
    "01",
    "light-the-world",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
]

SLUG_TITLES_EN = {
    "01":               "About the Christmas Study Plan",
    "light-the-world":  "Light the World: Serving, Sharing, and Giving",
    "02":               "Dec 19 — Prophets Foretold the Birth of Jesus",
    "03":               "Dec 20 — An Angel Appeared to Mary and to Joseph",
    "04":               "Dec 21 — Elisabeth Bore John, and Zacharias Testified",
    "05":               "Dec 22 — Angels Announced Jesus's Birth to the Shepherds",
    "06":               "Dec 23 — The Lord Provides a Night Without Darkness",
    "07":               "Dec 24 — Jesus Christ Was Born and Presented in the Temple",
    "08":               "Dec 25 — The Wise Men Worshipped Jesus and Gave Gifts",
}

# Dec 19–25 + special pages
SLUG_DATE = {
    "01":               None,
    "light-the-world":  None,
    "02":               "Dec 19",
    "03":               "Dec 20",
    "04":               "Dec 21",
    "05":               "Dec 22",
    "06":               "Dec 23",
    "07":               "Dec 24",
    "08":               "Dec 25",
}


def fallback_pages(manual_uri: str) -> list[TocEntry]:
    """Generate pages from known slugs when TOC discovery fails."""
    return [
        TocEntry(
            uri=f"{manual_uri}/{slug}",
            slug=slug,
            title=SLUG_TITLES_EN.get(slug, slug),
        )
        for slug in SLUG_ORDER
    ]


def build_meta(page, slug: str, year: int, lang: str, manual_uri: str,
               footnotes_meta: dict, scripture_refs: list[str]) -> dict:
    date_label = SLUG_DATE.get(slug)
    meta = {
        "title":        page.title,
        "book":         f"Christmas Study Plan {year}",
        "category":     "manuals",
        "subcategory":  f"christmas-study-plan-{year}",
        "tags":         ["christmas", "nativity", "jesus-birth", "seasonal", "devotional"],
        "authority":    60,
        "official":     True,
        "lang":         lang,
        "source_url":   build_source_url(f"{manual_uri}/{slug}", lang),
        "year":         year,
    }
    if date_label:
        meta["date_label"] = date_label
    if slug == "light-the-world":
        meta["tags"].append("light-the-world")
        meta["note"] = "Overview page: external links to LightTheWorld.org and service resources"
    meta.update(footnotes_meta)
    if scripture_refs:
        existing = meta.get("scripture_refs", [])
        merged = list({r: None for r in (existing + scripture_refs)}.keys())
        meta["scripture_refs"] = merged
    return meta


def download_plan(year: int, lang: str, dry_run: bool = False) -> DownloadStats:
    stats = DownloadStats()
    corpus_lang = LANG_MAP.get(lang, lang)
    manual_uri = f"/manual/christmas-study-plan-{year}"
    output_dir = CORPUS_ROOT / corpus_lang / "manuals" / f"christmas-study-plan-{year}"

    session = ChurchSession()

    # Discover pages
    pages = discover_toc_api(
        session, manual_uri, lang,
        link_contains=f"christmas-study-plan-{year}",
        slug_filter=set(SLUG_ORDER),
    )

    # Fallback: use known slugs if TOC parsing missed pages
    discovered_slugs = {p.slug for p in pages}
    missing = [s for s in SLUG_ORDER if s not in discovered_slugs]
    if missing:
        logger.info("TOC discovery missed %d slugs, using fallback: %s", len(missing), missing)
        fallback = {p.slug: p for p in fallback_pages(manual_uri)}
        pages = [fallback.get(s, next((p for p in pages if p.slug == s), None))
                 for s in SLUG_ORDER if s in discovered_slugs or s in missing]
        pages = [p for p in pages if p is not None]

    # Re-order to canonical order
    slug_index = {s: i for i, s in enumerate(SLUG_ORDER)}
    pages.sort(key=lambda p: slug_index.get(p.slug, 99))

    stats.pages = len(pages)
    logger.info("Christmas Study Plan %d (%s): %d pages", year, lang, len(pages))

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    for i, page_entry in enumerate(pages, 1):
        slug = page_entry.slug
        filename = f"{SLUG_ORDER.index(slug):02d}-{slug}" if slug in SLUG_ORDER else slug
        txt_path = output_dir / f"{filename}.txt"

        logger.info("[%d/%d] %s → %s", i, len(pages), page_entry.title[:60], filename)

        if dry_run:
            stats.downloaded += 1
            continue

        if txt_path.exists():
            logger.info("  Already exists, skipping")
            stats.skipped += 1
            continue

        page = fetch_api_page(session, page_entry.uri, lang)
        if page is None:
            logger.warning("  No content returned for %s", slug)
            stats.errors += 1
            continue

        # Convert HTML to text
        text = html_to_structured_text(page.body_html)
        if not text.strip():
            logger.warning("  Empty text after conversion for %s", slug)
            stats.errors += 1
            continue

        # Extract footnotes — always
        footnotes = extract_footnotes_api(page.footnotes)
        endnotes = format_footnotes_text(footnotes, header="Notas")
        if endnotes:
            text += endnotes
        footnotes_meta = footnotes_to_meta(footnotes)
        stats.footnotes_total += footnotes_meta.get("note_count", 0)

        # Extract scripture refs from HTML links
        soup = BeautifulSoup(page.body_html, "html.parser")
        scripture_refs = []
        for a in soup.find_all("a", href=True):
            if "/study/scriptures/" in a["href"]:
                ref = a.get_text(strip=True)
                if ref and ref not in scripture_refs:
                    scripture_refs.append(ref)
        stats.scripture_refs_total += len(scripture_refs)

        meta = build_meta(page, slug, year, lang, f"/manual/christmas-study-plan-{year}",
                          footnotes_meta, scripture_refs)

        write_corpus_file(output_dir, filename, text, meta)
        stats.downloaded += 1
        logger.info("  Saved: %s (%d chars, %d footnotes, %d refs)",
                    filename, len(text),
                    footnotes_meta.get("note_count", 0), len(scripture_refs))

    stats.log_summary(f"Christmas {year} {lang}")
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Download the Christmas Study Plan"
    )
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR,
                        help=f"Plan year (default: {DEFAULT_YEAR})")
    add_common_args(parser)
    args = parser.parse_args()

    languages = get_languages(args)
    for lang in languages:
        download_plan(args.year, lang, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
