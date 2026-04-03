#!/usr/bin/env python3
"""Download the Easter / Holy Week Study Plan from churchofjesuschrist.org.

The plan has an evergreen slug (`easter-plan`) and 18 pages organized in
two parallel tracks that run simultaneously through Holy Week:

  Track NT  — New Testament chronology (Palm Sunday through Easter Monday)
  Track BoM — Book of Mormon parallel narratives for the same week

Both tracks cover the same 8 calendar days from different scriptural
perspectives, making this the most structurally unique manual in the corpus
and a rich source of intertextuality relations for the KG.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_easter_study_plan.py
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_easter_study_plan.py --lang spa
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_easter_study_plan.py --dry-run

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
    write_corpus_file, build_source_url,
    add_common_args, get_languages, DownloadStats, CORPUS_ROOT,
)
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

LANG_MAP = {"eng": "en", "spa": "es"}
MANUAL_URI = "/manual/easter-plan"

# Canonical slug order, with track metadata.
# Two parallel tracks (nt/bom) run through the same 8 days of Holy Week.
# day_key: canonical day name for cross-track KG relations.
PAGES = [
    # slug              filename prefix      track   day_key
    ("01-about",        "00-about",          None,   None),
    # NT track
    ("02-sunday",       "nt-01-palm-sunday", "nt",   "palm-sunday"),
    ("03-monday",       "nt-02-monday",      "nt",   "monday"),
    ("04-tuesday",      "nt-03-tuesday",     "nt",   "tuesday"),
    ("05-wednesday",    "nt-04-wednesday",   "nt",   "wednesday"),
    ("06-thursday",     "nt-05-thursday",    "nt",   "thursday"),
    ("07-friday",       "nt-06-good-friday", "nt",   "good-friday"),
    ("08-saturday",     "nt-07-saturday",    "nt",   "saturday"),
    ("09-sunday",       "nt-08-easter",      "nt",   "easter-sunday"),
    ("09a-monday",      "nt-09-easter-mon",  "nt",   "easter-monday"),
    # BoM track
    ("10-sunday",       "bom-01-palm-sunday","bom",  "palm-sunday"),
    ("11-monday",       "bom-02-monday",     "bom",  "monday"),
    ("12-tuesday",      "bom-03-tuesday",    "bom",  "tuesday"),
    ("13-wednesday",    "bom-04-wednesday",  "bom",  "wednesday"),
    ("14-thursday",     "bom-05-thursday",   "bom",  "thursday"),
    ("15-friday",       "bom-06-good-friday","bom",  "good-friday"),
    ("16-saturday",     "bom-07-saturday",   "bom",  "saturday"),
    ("17-sunday",       "bom-08-easter",     "bom",  "easter-sunday"),
]

SLUG_TO_PAGE = {slug: (fn, track, day) for slug, fn, track, day in PAGES}
SLUG_ORDER = [slug for slug, *_ in PAGES]

TITLES_EN = {
    "01-about":     "About the Holy Week Study Experience",
    "02-sunday":    "Palm Sunday — Hosanna in the Highest",
    "03-monday":    "Monday — The House of Prayer",
    "04-tuesday":   "Tuesday — Love Thy Neighbour",
    "05-wednesday": "Wednesday — A Good Work",
    "06-thursday":  "Thursday — In Remembrance of Me",
    "07-friday":    "Good Friday — Forgive Them",
    "08-saturday":  "Saturday — I Am the Light",
    "09-sunday":    "Easter Sunday — He Is Risen",
    "09a-monday":   "Easter Monday — Peace Be unto You",
    "10-sunday":    "Palm Sunday — Prophecies of Christ's Birth",
    "11-monday":    "Monday — Christ's Appearance in Ancient Americas",
    "12-tuesday":   "Tuesday — Repentance and Baptism",
    "13-wednesday": "Wednesday — The Higher Law",
    "14-thursday":  "Thursday — One Fold and One Shepherd",
    "15-friday":    "Good Friday — Healing the People",
    "16-saturday":  "Saturday — Ministering to Children",
    "17-sunday":    "Easter Sunday — Institution of the Sacrament",
}


def fallback_pages() -> list[TocEntry]:
    return [
        TocEntry(
            uri=f"{MANUAL_URI}/{slug}",
            slug=slug,
            title=TITLES_EN.get(slug, slug),
        )
        for slug in SLUG_ORDER
    ]


def build_meta(page, slug: str, lang: str,
               footnotes_meta: dict, scripture_refs: list[str]) -> dict:
    fn, track, day_key = SLUG_TO_PAGE.get(slug, (slug, None, None))

    tags = ["easter", "holy-week", "atonement", "resurrection", "seasonal", "devotional"]
    if track == "nt":
        tags += ["new-testament", "gospels"]
    elif track == "bom":
        tags += ["book-of-mormon", "3-nephi"]

    meta = {
        "title":        page.title,
        "book":         "Easter Holy Week Study Experience",
        "category":     "manuals",
        "subcategory":  "easter-plan",
        "tags":         tags,
        "authority":    60,
        "official":     True,
        "lang":         lang,
        "source_url":   build_source_url(f"{MANUAL_URI}/{slug}", lang),
    }

    if track:
        meta["track"] = track   # "nt" or "bom"
    if day_key:
        meta["day_key"] = day_key  # same value across both tracks → KG cross-track link

    meta.update(footnotes_meta)
    if scripture_refs:
        existing = meta.get("scripture_refs", [])
        merged = list({r: None for r in (existing + scripture_refs)}.keys())
        meta["scripture_refs"] = merged

    return meta


def download_plan(lang: str, dry_run: bool = False) -> DownloadStats:
    stats = DownloadStats()
    corpus_lang = LANG_MAP.get(lang, lang)
    output_dir = CORPUS_ROOT / corpus_lang / "manuals" / "easter-plan"

    session = ChurchSession()

    pages = discover_toc_api(
        session, MANUAL_URI, lang,
        link_contains="easter-plan",
        slug_filter=set(SLUG_ORDER),
    )

    # Fallback for any missing slugs
    discovered_slugs = {p.slug for p in pages}
    if len(discovered_slugs) < len(SLUG_ORDER):
        missing = [s for s in SLUG_ORDER if s not in discovered_slugs]
        logger.info("TOC missed %d slugs, adding from fallback: %s", len(missing), missing)
        fb_map = {p.slug: p for p in fallback_pages()}
        for slug in missing:
            pages.append(fb_map[slug])

    # Canonical order
    slug_index = {s: i for i, s in enumerate(SLUG_ORDER)}
    pages.sort(key=lambda p: slug_index.get(p.slug, 99))

    stats.pages = len(pages)
    logger.info("Easter Study Plan (%s): %d pages (%d NT + %d BoM + 1 intro)",
                lang, len(pages),
                sum(1 for s, *_ in PAGES if _[0] == "nt"),
                sum(1 for s, *_ in PAGES if _[0] == "bom"))

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    for i, page_entry in enumerate(pages, 1):
        slug = page_entry.slug
        fn, track, day_key = SLUG_TO_PAGE.get(slug, (slug, None, None))
        filename = fn

        track_label = f" [{track.upper()}]" if track else ""
        logger.info("[%d/%d]%s %s → %s", i, len(pages), track_label,
                    page_entry.title[:55], filename)

        if dry_run:
            stats.downloaded += 1
            continue

        txt_path = output_dir / f"{filename}.txt"
        if txt_path.exists():
            logger.info("  Already exists, skipping")
            stats.skipped += 1
            continue

        page = fetch_api_page(session, page_entry.uri, lang)
        if page is None:
            logger.warning("  No content for %s", slug)
            stats.errors += 1
            continue

        text = html_to_structured_text(page.body_html)
        if not text.strip():
            logger.warning("  Empty text after conversion for %s", slug)
            stats.errors += 1
            continue

        # Footnotes — always capture (sparse here but structurally important)
        footnotes = extract_footnotes_api(page.footnotes)
        endnotes = format_footnotes_text(footnotes, header="Notas")
        if endnotes:
            text += endnotes
        footnotes_meta = footnotes_to_meta(footnotes)
        stats.footnotes_total += footnotes_meta.get("note_count", 0)

        # Scripture refs from hyperlinks
        soup = BeautifulSoup(page.body_html, "html.parser")
        scripture_refs = []
        for a in soup.find_all("a", href=True):
            if "/study/scriptures/" in a["href"]:
                ref = a.get_text(strip=True)
                if ref and ref not in scripture_refs:
                    scripture_refs.append(ref)
        stats.scripture_refs_total += len(scripture_refs)

        meta = build_meta(page, slug, lang, footnotes_meta, scripture_refs)

        write_corpus_file(output_dir, filename, text, meta)
        stats.downloaded += 1
        logger.info("  Saved: %s (%d chars, %d refs)", filename, len(text), len(scripture_refs))

    stats.log_summary(f"Easter {lang}")
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Download the Easter / Holy Week Study Plan"
    )
    add_common_args(parser)
    args = parser.parse_args()

    languages = get_languages(args)
    for lang in languages:
        download_plan(lang, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
