#!/usr/bin/env python3
"""General-purpose downloader for Church manual content.

Covers all prose manuals accessible via the Church API v3:
  Gospel Principles, True to the Faith, Come Follow Me (all years/versions),
  Teachings of Presidents (all 17 prophets), Our Heritage, For the Strength
  of Youth, Gospel Topics Essays, First Vision Accounts, and more.

Each page → corpus/{lang}/manuals/{subdir}/{slug}.txt + .meta.json
KG fields set per manual: `book` (PART_OF), `author` (AUTHORED_BY for ToP),
  `scripture_refs` (CITES) from footnotes.

Usage:
    # List available manuals
    python scripts/download_manual.py --list

    # Download a single manual (both languages)
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt \\
        python scripts/download_manual.py --manual gospel-principles

    # Download one language
    python scripts/download_manual.py --manual true-to-the-faith --lang eng

    # Download Come Follow Me for a specific year
    python scripts/download_manual.py --manual come-follow-me --cfm-year 2024

    # Download all Teachings of Presidents in sequence
    python scripts/download_manual.py --manual teachings-of-presidents --all-prophets

    # Dry run
    python scripts/download_manual.py --manual our-heritage --dry-run
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bs4 import BeautifulSoup

from lib.church_scraper import (
    BASE_URL, CORPUS_ROOT, LANG_MAP, ChurchSession,
    fetch_api_page, html_to_structured_text,
    extract_footnotes_api, footnotes_to_meta,
    extract_scripture_refs_from_html,
    discover_toc_api, discover_toc_html,
    write_corpus_file, build_source_url,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)


# ── Manual configuration ─────────────────────────────────────────────────────

@dataclass
class ManualConfig:
    """Configuration for a single downloadable manual."""
    key: str                       # CLI identifier
    slug: str                      # site URI slug (last segment)
    book: str                      # display name → meta.json `book` (PART_OF)
    output_subdir: str             # corpus/{lang}/{output_subdir}/
    authority: int
    tags: list[str] = field(default_factory=list)
    author: str = ""               # prophet name for Teachings of Presidents (AUTHORED_BY)
    link_contains: str = ""        # TOC link filter; defaults to slug
    uri_prefix: str = "/manual"    # URI prefix; override for /history, /scriptures, etc.
    bilingual: bool = True
    notes: str = ""

    def __post_init__(self):
        if not self.link_contains:
            self.link_contains = self.slug

    @property
    def manual_uri(self) -> str:
        return f"{self.uri_prefix}/{self.slug}"


# ── Come Follow Me helper ────────────────────────────────────────────────────

_CFM_SLUGS = {
    # year → (slug, standard_work)
    # 2023-2026: "for-home-and-church" branding
    2026: ("come-follow-me-for-home-and-church-old-testament-2026", "Old Testament"),
    2025: ("come-follow-me-for-home-and-church-doctrine-and-covenants-2025", "Doctrine and Covenants"),
    2024: ("come-follow-me-for-home-and-church-book-of-mormon-2024", "Book of Mormon"),
    2023: ("come-follow-me-for-home-and-church-new-testament-2023", "New Testament"),
    # 2019-2022: "for-individuals-and-families" branding (earlier naming convention)
    2022: ("come-follow-me-for-individuals-and-families-old-testament-2022", "Old Testament"),
    2021: ("come-follow-me-for-individuals-and-families-doctrine-and-covenants-2021", "Doctrine and Covenants"),
    2020: ("come-follow-me-for-individuals-and-families-book-of-mormon-2020", "Book of Mormon"),
    2019: ("come-follow-me-for-individuals-and-families-new-testament-2019", "New Testament"),
}


def _cfm_config(year: int) -> ManualConfig:
    if year not in _CFM_SLUGS:
        raise ValueError(f"Unknown CFM year {year}. Available: {sorted(_CFM_SLUGS)}")
    slug, work = _CFM_SLUGS[year]
    return ManualConfig(
        key=f"come-follow-me-{year}",
        slug=slug,
        book=f"Come, Follow Me {year}: {work}",
        output_subdir=f"manuals/come-follow-me/{year}",
        authority=60,
        tags=["come-follow-me", "study", work.lower().replace(" ", "-"), str(year)],
        link_contains=slug,
    )


# ── Teachings of Presidents ───────────────────────────────────────────────────

_PROPHETS = [
    # (key, site-slug, prophet-name)
    ("teachings-joseph-smith",
     "teachings-joseph-smith",
     "Joseph Smith"),
    ("teachings-brigham-young",
     "teachings-brigham-young",
     "Brigham Young"),
    ("teachings-john-taylor",
     "teachings-john-taylor",
     "John Taylor"),
    ("teachings-wilford-woodruff",
     "teachings-wilford-woodruff",
     "Wilford Woodruff"),
    ("teachings-lorenzo-snow",
     "teachings-of-presidents-of-the-church-lorenzo-snow",
     "Lorenzo Snow"),
    ("teachings-joseph-f-smith",
     "teachings-joseph-f-smith",
     "Joseph F. Smith"),
    ("teachings-heber-j-grant",
     "teachings-heber-j-grant",
     "Heber J. Grant"),
    ("teachings-george-albert-smith",
     "teachings-george-albert-smith",
     "George Albert Smith"),
    ("teachings-david-o-mckay",
     "teachings-david-o-mckay",
     "David O. McKay"),
    ("teachings-joseph-fielding-smith",
     "teachings-of-presidents-of-the-church-joseph-fielding-smith",
     "Joseph Fielding Smith"),
    ("teachings-harold-b-lee",
     "teachings-harold-b-lee",
     "Harold B. Lee"),
    ("teachings-spencer-w-kimball",
     "teachings-spencer-w-kimball",
     "Spencer W. Kimball"),
    ("teachings-ezra-taft-benson",
     "teachings-of-presidents-of-the-church-ezra-taft-benson",
     "Ezra Taft Benson"),
    ("teachings-howard-w-hunter",
     "teachings-of-presidents-of-the-church-howard-w-hunter",
     "Howard W. Hunter"),
    ("teachings-gordon-b-hinckley",
     "teachings-of-presidents-of-the-church-gordon-b-hinckley",
     "Gordon B. Hinckley"),
    ("teachings-thomas-s-monson",
     "teachings-of-presidents-of-the-church-thomas-s-monson",
     "Thomas S. Monson"),
    ("teachings-russell-m-nelson",
     "teachings-of-presidents-of-the-church-russell-m-nelson",
     "Russell M. Nelson"),
]


def _prophet_config(key: str) -> Optional[ManualConfig]:
    for pk, pslug, pname in _PROPHETS:
        if pk == key:
            safe = pk.replace("teachings-", "")
            return ManualConfig(
                key=pk,
                slug=pslug,
                book=f"Teachings of Presidents of the Church: {pname}",
                author=pname,
                output_subdir=f"manuals/teachings-of-presidents/{safe}",
                authority=60,
                tags=["teachings", "presidents", "prophets", safe],
                link_contains=pslug,
            )
    return None


# ── Static manual registry ────────────────────────────────────────────────────

_STATIC_MANUALS: list[ManualConfig] = [
    ManualConfig(
        key="gospel-principles",
        slug="gospel-principles",
        book="Gospel Principles",
        output_subdir="manuals/gospel-principles",
        authority=60,
        tags=["doctrine", "new-members", "plan-of-salvation"],
    ),
    ManualConfig(
        key="true-to-the-faith",
        slug="true-to-the-faith",
        book="True to the Faith",
        output_subdir="manuals/true-to-the-faith",
        authority=60,
        tags=["reference", "doctrine", "gospel-topics", "missionaries"],
    ),
    ManualConfig(
        key="our-heritage",
        slug="our-heritage-a-brief-history-of-the-church",
        book="Our Heritage: A Brief History of the Church",
        output_subdir="manuals/our-heritage",
        authority=60,
        tags=["history", "restoration", "church-history"],
        link_contains="our-heritage",
    ),
    ManualConfig(
        key="for-the-strength-of-youth",
        slug="for-the-strength-of-youth",
        book="For the Strength of Youth",
        output_subdir="manuals/for-the-strength-of-youth",
        authority=60,
        tags=["youth", "standards", "principles"],
        link_contains="for-the-strength-of-youth",
    ),
    ManualConfig(
        key="gospel-topics-essays",
        slug="gospel-topics-essays",
        book="Gospel Topics Essays",
        output_subdir="manuals/gospel-topics-essays",
        authority=70,
        tags=["gospel-topics", "history", "doctrine", "apologetics"],
        notes="Official essays on sensitive topics; authority=70 (First Presidency approved)",
    ),
    ManualConfig(
        key="first-vision-accounts",
        slug="first-vision-accounts",
        book="First Vision Accounts",
        output_subdir="manuals/first-vision-accounts",
        authority=75,
        tags=["first-vision", "joseph-smith", "restoration", "history"],
        notes="Primary documents: multiple accounts of the First Vision (1832, 1835, 1838, 1842)",
    ),
    ManualConfig(
        key="missionary-preparation",
        slug="missionary-preparation-teacher-manual-2025",
        book="Missionary Preparation: A Teaching Resource",
        output_subdir="manuals/missionary-preparation",
        authority=60,
        tags=["missionary", "preparation", "teaching"],
        link_contains="missionary-preparation",
    ),
    ManualConfig(
        key="doctrines-of-the-gospel",
        slug="doctrines-of-the-gospel-student-manual",
        book="Doctrines of the Gospel Student Manual",
        output_subdir="manuals/doctrines-of-the-gospel",
        authority=60,
        tags=["doctrine", "institute", "theology"],
        link_contains="doctrines-of-the-gospel-student",
    ),

    # ── Institute Scripture Course manuals ───────────────────────────────────
    ManualConfig(
        key="bom-institute-student",
        slug="book-of-mormon-student-manual",
        book="Book of Mormon Student Manual (Institute)",
        output_subdir="manuals/institute/book-of-mormon-student",
        authority=60,
        tags=["institute", "book-of-mormon", "scripture-study"],
        link_contains="book-of-mormon-student-manual",
    ),
    ManualConfig(
        key="dc-institute-student",
        slug="doctrine-and-covenants-student-manual-2017",
        book="Doctrine and Covenants Student Manual (Institute)",
        output_subdir="manuals/institute/doctrine-and-covenants-student",
        authority=60,
        tags=["institute", "doctrine-and-covenants", "scripture-study"],
        link_contains="doctrine-and-covenants-student-manual",
    ),
    ManualConfig(
        key="pgp-institute-student",
        slug="the-pearl-of-great-price-student-manual-2018",
        book="Pearl of Great Price Student Manual (Institute)",
        output_subdir="manuals/institute/pearl-of-great-price-student",
        authority=60,
        tags=["institute", "pearl-of-great-price", "scripture-study"],
        link_contains="pearl-of-great-price-student-manual",
    ),
    ManualConfig(
        key="nt-institute-teacher",
        slug="new-testament-institute-teacher-manual-2024",
        book="New Testament Institute Teacher Manual",
        output_subdir="manuals/institute/new-testament-teacher",
        authority=60,
        tags=["institute", "new-testament", "scripture-study"],
        link_contains="new-testament-institute-teacher-manual",
    ),

    # ── Institute Cornerstone Courses ────────────────────────────────────────
    ManualConfig(
        key="eternal-family",
        slug="the-eternal-family-class-prep-material-2022",
        book="The Eternal Family (Institute Class Prep)",
        output_subdir="manuals/institute/eternal-family",
        authority=60,
        tags=["institute", "family", "eternal-family", "cornerstone"],
        link_contains="eternal-family-class-prep",
    ),
    ManualConfig(
        key="foundations-restoration",
        slug="foundations-of-the-restoration-class-preparation-material-2019",
        book="Foundations of the Restoration (Institute Class Prep)",
        output_subdir="manuals/institute/foundations-of-restoration",
        authority=60,
        tags=["institute", "restoration", "cornerstone", "history"],
        link_contains="foundations-of-the-restoration-class-preparation",
    ),
    ManualConfig(
        key="jesus-christ-everlasting-gospel",
        slug="jesus-christ-and-his-everlasting-gospel-class-prep-material-2023",
        book="Jesus Christ and His Everlasting Gospel (Institute Class Prep)",
        output_subdir="manuals/institute/jesus-christ-everlasting-gospel",
        authority=60,
        tags=["institute", "jesus-christ", "atonement", "cornerstone"],
        link_contains="jesus-christ-and-his-everlasting-gospel-class-prep",
    ),
    ManualConfig(
        key="teachings-doctrine-bom",
        slug="teachings-and-doctrine-of-the-book-of-mormon-class-prep-material-2021",
        book="Teachings and Doctrine of the Book of Mormon (Institute Class Prep)",
        output_subdir="manuals/institute/teachings-doctrine-bom",
        authority=60,
        tags=["institute", "book-of-mormon", "doctrine", "cornerstone"],
        link_contains="teachings-and-doctrine-of-the-book-of-mormon-class-prep",
    ),

    # ── Seminary Student Manuals ─────────────────────────────────────────────
    ManualConfig(
        key="bom-seminary-student",
        slug="book-of-mormon-seminary-student-manual-2024",
        book="Book of Mormon Seminary Student Manual",
        output_subdir="manuals/seminary/book-of-mormon-student",
        authority=60,
        tags=["seminary", "book-of-mormon", "scripture-study", "youth"],
        link_contains="book-of-mormon-seminary-student-manual",
    ),
    ManualConfig(
        key="nt-seminary-student",
        slug="new-testament-seminary-student-manual-2023",
        book="New Testament Seminary Student Manual",
        output_subdir="manuals/seminary/new-testament-student",
        authority=60,
        tags=["seminary", "new-testament", "scripture-study", "youth"],
        link_contains="new-testament-seminary-student-manual",
    ),
    ManualConfig(
        key="ot-seminary-student",
        slug="old-testament-seminary-student-manual-2026",
        book="Old Testament Seminary Student Manual",
        output_subdir="manuals/seminary/old-testament-student",
        authority=60,
        tags=["seminary", "old-testament", "scripture-study", "youth"],
        link_contains="old-testament-seminary-student-manual",
    ),
    # NOTE: D&C Seminary STUDENT manual (2025) is PDF-only — never published as
    # a web manual. Only the teacher manual has a web slug. Use teacher manual
    # as fallback, or download PDFs manually from:
    #   https://content-preview.churchofjesuschrist.org/si/bc/si/seminary/pdf/
    #       Seminary-Student-Manual-2025/eng_DC-Seminary-Student-Manual_2025.pdf
    ManualConfig(
        key="dc-seminary-teacher",
        slug="doctrine-and-covenants-seminary-teacher-manual-2025",
        book="Doctrine and Covenants Seminary Teacher Manual",
        output_subdir="manuals/seminary/doctrine-and-covenants-teacher",
        authority=60,
        tags=["seminary", "doctrine-and-covenants", "scripture-study", "teacher"],
        notes="Student manual is PDF-only (not web-hosted). This is the teacher manual fallback.",
        link_contains="doctrine-and-covenants-seminary-teacher",
    ),
    ManualConfig(
        key="doctrinal-mastery",
        slug="doctrinal-mastery-core-document-2023",
        book="Doctrinal Mastery Core Document",
        output_subdir="manuals/seminary/doctrinal-mastery",
        authority=65,
        tags=["seminary", "doctrinal-mastery", "key-passages", "youth"],
        notes="100 designated mastery passages across all standard works — high KG priority",
    ),

    # ── Saints: The Story of the Church (Vols 1–4) ───────────────────────────
    # NOTE: URI prefix is /history, not /manual
    ManualConfig(
        key="saints-v1",
        slug="saints-v1",
        book="Saints: The Story of the Church of Jesus Christ in the Latter Days, Vol. 1 (1815–1851)",
        output_subdir="manuals/saints/vol-1",
        authority=65,
        tags=["history", "saints", "restoration", "early-church"],
        uri_prefix="/history",
        link_contains="saints-v1",
    ),
    ManualConfig(
        key="saints-v2",
        slug="saints-v2",
        book="Saints: The Story of the Church of Jesus Christ in the Latter Days, Vol. 2 (1846–1893)",
        output_subdir="manuals/saints/vol-2",
        authority=65,
        tags=["history", "saints", "pioneer", "utah"],
        uri_prefix="/history",
        link_contains="saints-v2",
    ),
    ManualConfig(
        key="saints-v3",
        slug="saints-v3",
        book="Saints: The Story of the Church of Jesus Christ in the Latter Days, Vol. 3 (1893–1955)",
        output_subdir="manuals/saints/vol-3",
        authority=65,
        tags=["history", "saints", "expansion", "twentieth-century"],
        uri_prefix="/history",
        link_contains="saints-v3",
    ),
    ManualConfig(
        key="saints-v4",
        slug="saints-v4",
        book="Saints: The Story of the Church of Jesus Christ in the Latter Days, Vol. 4 (1955–present)",
        output_subdir="manuals/saints/vol-4",
        authority=65,
        tags=["history", "saints", "global-church", "modern"],
        uri_prefix="/history",
        link_contains="saints-v4",
    ),

    # ── Gospel Topics encyclopedia ────────────────────────────────────────────
    ManualConfig(
        key="gospel-topics",
        slug="gospel-topics",
        book="Gospel Topics",
        output_subdir="manuals/gospel-topics",
        authority=65,
        tags=["reference", "doctrine", "gospel-topics", "encyclopedia"],
        notes="~400 entries; large volume — consider --limit for testing",
    ),
]


def _all_configs() -> dict[str, ManualConfig]:
    configs: dict[str, ManualConfig] = {}
    for m in _STATIC_MANUALS:
        configs[m.key] = m
    for pk, _ps, _pn in _PROPHETS:
        c = _prophet_config(pk)
        if c:
            configs[pk] = c
    return configs


# ── Core download logic ───────────────────────────────────────────────────────

def _build_meta(config: ManualConfig, page_title: str, uri: str,
                lang: str, corpus_lang: str,
                footnotes_meta: dict) -> dict:
    meta: dict = {
        "title": page_title,
        "book": config.book,
        "category": "manuals",
        "authority": config.authority,
        "lang": corpus_lang,
        "source_url": build_source_url(uri, lang),
        "tags": config.tags,
    }
    if config.author:
        meta["author"] = config.author
    if config.notes:
        meta["notes"] = config.notes

    # Merge footnote data (note_count, scripture_refs, footnotes)
    meta.update(footnotes_meta)
    return meta


def download_manual(config: ManualConfig, lang: str,
                    session: ChurchSession, dry_run: bool = False,
                    limit: int = 0) -> dict:
    """Download all pages of a manual for one language.

    Returns stats: {pages_found, downloaded, skipped, errors}
    """
    corpus_lang = LANG_MAP.get(lang, lang)
    output_dir = CORPUS_ROOT / corpus_lang / config.output_subdir
    manual_uri = config.manual_uri

    logger.info("[%s] %s → %s", lang, config.book, output_dir)

    # Discover TOC
    entries = discover_toc_api(
        session, manual_uri, lang, link_contains=config.link_contains,
    )
    if not entries:
        # Fallback: HTML-based TOC discovery
        toc_url = f"{BASE_URL}/study{manual_uri}?lang={lang}"
        entries = discover_toc_html(session, toc_url, link_contains=config.link_contains)

    if not entries:
        logger.error("  No TOC entries found for %s (%s)", config.slug, lang)
        return {"pages_found": 0, "downloaded": 0, "skipped": 0, "errors": 1}

    if limit:
        entries = entries[:limit]

    logger.info("  Found %d pages", len(entries))
    if dry_run:
        for e in entries:
            logger.info("    [dry-run] %s — %s", e.slug, e.title)
        return {"pages_found": len(entries), "downloaded": 0, "skipped": 0, "errors": 0}

    output_dir.mkdir(parents=True, exist_ok=True)
    stats = {"pages_found": len(entries), "downloaded": 0, "skipped": 0, "errors": 0}

    for i, entry in enumerate(entries, 1):
        slug = entry.slug
        txt_path = output_dir / f"{slug}.txt"

        if txt_path.exists():
            logger.debug("  [%d/%d] skip (exists): %s", i, len(entries), slug)
            stats["skipped"] += 1
            continue

        logger.info("  [%d/%d] %s — %s", i, len(entries), slug, entry.title[:60])

        page = fetch_api_page(session, entry.uri, lang)
        if not page:
            logger.warning("    No content returned")
            stats["errors"] += 1
            continue

        text = html_to_structured_text(page.body_html)
        if not text.strip():
            logger.warning("    Empty text after conversion")
            stats["errors"] += 1
            continue

        footnotes = extract_footnotes_api(page.footnotes)
        fn_meta = footnotes_to_meta(footnotes)

        # CFM (and some other manuals) embed scripture refs as inline HTML links
        # rather than API footnotes.  Merge both sources so nothing is lost.
        if page.body_html:
            soup = BeautifulSoup(page.body_html, "html.parser")
            inline_refs = extract_scripture_refs_from_html(soup)
            if inline_refs:
                existing = set(fn_meta.get("scripture_refs", []))
                fn_meta["scripture_refs"] = sorted(existing | set(inline_refs))

        title = page.title or entry.title
        meta = _build_meta(config, title, entry.uri, lang, corpus_lang, fn_meta)

        write_corpus_file(output_dir, slug, text, meta)
        stats["downloaded"] += 1
        logger.debug("    Saved: %s (%d chars)", slug, len(text))

    logger.info("  Done: %d downloaded, %d skipped, %d errors",
                stats["downloaded"], stats["skipped"], stats["errors"])
    return stats


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    all_configs = _all_configs()

    parser = argparse.ArgumentParser(
        description="Download Church manuals to corpus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run with --list to see all available manuals.",
    )
    parser.add_argument("--manual", metavar="KEY",
                        help="Manual key to download (use --list to see options)")
    parser.add_argument("--lang", choices=["eng", "spa", "both"], default="both")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max pages to download per language (for testing)")
    parser.add_argument("--list", action="store_true",
                        help="List all available manual keys and exit")

    # Come Follow Me options
    parser.add_argument("--cfm-year", type=int, choices=sorted(_CFM_SLUGS),
                        help="Year for Come Follow Me manual")

    # Teachings of Presidents options
    parser.add_argument("--all-prophets", action="store_true",
                        help="Download all Teachings of Presidents in sequence")

    args = parser.parse_args()

    if args.list:
        print("\nAvailable manuals:")
        print(f"  {'KEY':<45} {'AUTHORITY':<10} BOOK")
        print("  " + "-" * 80)
        for key, cfg in sorted(all_configs.items()):
            print(f"  {key:<45} {cfg.authority:<10} {cfg.book}")
        print("\nCome Follow Me (use --cfm-year YYYY):")
        for year, (slug, work) in sorted(_CFM_SLUGS.items()):
            print(f"  come-follow-me --cfm-year {year:<6}  {work}")
        print()
        sys.exit(0)

    # Resolve which manuals to download
    targets: list[ManualConfig] = []

    if args.all_prophets:
        targets = [_prophet_config(pk) for pk, _, _ in _PROPHETS]
        targets = [t for t in targets if t]
    elif args.cfm_year:
        targets = [_cfm_config(args.cfm_year)]
    elif args.manual == "come-follow-me":
        if not args.cfm_year:
            parser.error("--manual come-follow-me requires --cfm-year YYYY")
    elif args.manual:
        cfg = all_configs.get(args.manual)
        if not cfg:
            logger.error("Unknown manual key: %s  (use --list to see options)", args.manual)
            sys.exit(1)
        targets = [cfg]
    else:
        parser.print_help()
        sys.exit(1)

    session = ChurchSession(delay=0.5)
    langs = ["eng", "spa"] if args.lang == "both" else [args.lang]

    total_downloaded = 0
    total_errors = 0

    for config in targets:
        for lang in langs:
            stats = download_manual(config, lang, session,
                                    dry_run=args.dry_run, limit=args.limit)
            total_downloaded += stats["downloaded"]
            total_errors += stats["errors"]

    logger.info("=== Total: %d pages downloaded, %d errors ===",
                total_downloaded, total_errors)
    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()
