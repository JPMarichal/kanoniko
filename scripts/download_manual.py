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
    2023: ("come-follow-me-for-individuals-and-families-new-testament-2023", "New Testament"),
    # 2019-2023: "for-individuals-and-families" branding (earlier naming convention)
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
        slug="our-heritage",
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

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP A: Complete manuals (multi-chapter, API v3)
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="preach-my-gospel",
        slug="preach-my-gospel-2023",
        book="Preach My Gospel: A Guide to Sharing the Gospel of Jesus Christ",
        output_subdir="manuals/preach-my-gospel",
        authority=65,
        tags=["missionary", "doctrine", "teaching", "conversion", "preach-my-gospel"],
        notes="2nd edition (2023), FP+Q12 commissioned; expanded to all members",
    ),
    ManualConfig(
        key="old-testament-stories",
        slug="old-testament-stories-2022",
        book="Old Testament Stories",
        output_subdir="manuals/old-testament-stories",
        authority=50,
        tags=["children", "old-testament", "scripture-stories", "primary"],
        notes="2022 refresh: 50 stories, 350+ new illustrations, 63 languages",
    ),
    ManualConfig(
        key="teaching-in-the-saviors-way",
        slug="teaching-in-the-saviors-way-2022",
        book="Teaching in the Savior's Way",
        output_subdir="manuals/teaching-in-the-saviors-way",
        authority=60,
        tags=["teaching", "pedagogy", "christlike-teaching", "teacher-development"],
        notes="2022 edition; Church-wide manual for all gospel teachers",
    ),
    ManualConfig(
        key="for-parents-covenant-path",
        slug="for-parents-preparing-your-children-for-a-lifetime-on-gods-covenant-path",
        book="For Parents: Preparing Your Children for a Lifetime on God's Covenant Path",
        output_subdir="manuals/for-parents-covenant-path",
        authority=55,
        tags=["parents", "covenant-path", "ordinances", "children", "family"],
        bilingual=False,
        notes="CFM Appendix A (standalone); EN only",
    ),
    ManualConfig(
        key="for-primary-covenant-path",
        slug="for-primary-preparing-children-for-a-lifetime-on-gods-covenant-path",
        book="For Primary: Preparing Children for a Lifetime on God's Covenant Path",
        output_subdir="manuals/for-primary-covenant-path",
        authority=55,
        tags=["primary", "covenant-path", "ordinances", "children", "teaching"],
        bilingual=False,
        notes="CFM Appendix B (standalone); EN only",
    ),

    # ── Teaching Pamphlets (8 individual pamphlets, each is a short manual) ──
    ManualConfig(
        key="pamphlet-restoration",
        slug="the-restoration",
        book="The Restoration of the Gospel of Jesus Christ",
        output_subdir="manuals/teaching-pamphlets",
        authority=60,
        tags=["missionary", "restoration", "pamphlet", "teaching"],
        link_contains="the-restoration",
    ),
    ManualConfig(
        key="pamphlet-plan-of-salvation",
        slug="the-plan-of-salvation",
        book="The Plan of Salvation",
        output_subdir="manuals/teaching-pamphlets",
        authority=60,
        tags=["missionary", "plan-of-salvation", "pamphlet", "teaching"],
        link_contains="the-plan-of-salvation",
    ),
    ManualConfig(
        key="pamphlet-gospel",
        slug="the-gospel",
        book="The Gospel of Jesus Christ",
        output_subdir="manuals/teaching-pamphlets",
        authority=60,
        tags=["missionary", "gospel", "pamphlet", "teaching"],
        link_contains="the-gospel",
    ),
    ManualConfig(
        key="pamphlet-chastity",
        slug="chastity",
        book="Chastity",
        output_subdir="manuals/teaching-pamphlets",
        authority=60,
        tags=["missionary", "chastity", "pamphlet", "teaching"],
    ),
    ManualConfig(
        key="pamphlet-word-of-wisdom",
        slug="the-word-of-wisdom",
        book="The Word of Wisdom",
        output_subdir="manuals/teaching-pamphlets",
        authority=60,
        tags=["missionary", "word-of-wisdom", "pamphlet", "teaching"],
        link_contains="the-word-of-wisdom",
    ),
    ManualConfig(
        key="pamphlet-tithing",
        slug="tithing-and-fast-offerings",
        book="Tithing and Fast Offerings",
        output_subdir="manuals/teaching-pamphlets",
        authority=60,
        tags=["missionary", "tithing", "fast-offerings", "pamphlet", "teaching"],
        link_contains="tithing-and-fast-offerings",
    ),
    ManualConfig(
        key="pamphlet-families-temples",
        slug="families-and-temples",
        book="Families and Temples",
        output_subdir="manuals/teaching-pamphlets",
        authority=60,
        tags=["missionary", "family", "temple", "pamphlet", "teaching"],
        link_contains="families-and-temples",
    ),
    ManualConfig(
        key="pamphlet-learning-serving",
        slug="learning-and-serving-in-the-church",
        book="Learning and Serving in the Church",
        output_subdir="manuals/teaching-pamphlets",
        authority=60,
        tags=["missionary", "church-membership", "pamphlet", "teaching"],
        link_contains="learning-and-serving",
    ),

    # ── Mission materials ────────────────────────────────────────────────────
    ManualConfig(
        key="missionary-standards-service",
        slug="missionary-standards-service-missionaries-2025",
        book="Missionary Standards: Service Missionaries",
        output_subdir="manuals/missionary-standards-service",
        authority=55,
        tags=["missionary", "service-mission", "standards", "conduct"],
        notes="2025 edition; EN+ES",
    ),
    ManualConfig(
        key="on-holy-ground",
        slug="on-holy-ground",
        book="On Holy Ground",
        output_subdir="manuals/on-holy-ground",
        authority=55,
        tags=["missionary", "historic-sites", "restoration", "teaching"],
        notes="Teaching manual for historic-site missionaries",
        bilingual=False,
    ),
    ManualConfig(
        key="safeguards-technology",
        slug="safeguards-for-using-technology",
        book="Safeguards for Using Technology",
        output_subdir="manuals/safeguards-technology",
        authority=50,
        tags=["missionary", "technology", "safety", "youth"],
    ),
    ManualConfig(
        key="missionary-interview-questions",
        slug="missionary-interview-questions",
        book="Missionary Interview Questions",
        output_subdir="manuals/missionary-interview-questions",
        authority=70,
        tags=["missionary", "interviews", "worthiness", "leadership"],
        notes="FP-issued standard protocol (Oct 2017)",
    ),
    ManualConfig(
        key="adjusting-service-missionary",
        slug="adjusting-to-service-missionary-life-resource-booklet",
        book="Adjusting to Service Missionary Life",
        output_subdir="manuals/adjusting-to-service-missionary-life",
        authority=50,
        tags=["missionary", "service-mission", "mental-health", "adjustment"],
    ),

    # ── Support materials ────────────────────────────────────────────────────
    ManualConfig(
        key="counseling-resources",
        slug="counseling-resources",
        book="Counseling Resources",
        output_subdir="manuals/counseling-resources",
        authority=55,
        tags=["pastoral", "counseling", "atonement", "mental-health", "leadership"],
        notes="15 challenge areas; 5 Atonement-based pastoral principles",
    ),
    ManualConfig(
        key="providing-in-the-lords-way",
        slug="providing-in-the-lords-way-summary",
        book="Providing in the Lord's Way: A Leader's Guide to Welfare",
        output_subdir="manuals/providing-in-the-lords-way",
        authority=60,
        tags=["welfare", "self-reliance", "consecration", "fast-offerings", "leadership"],
    ),
    ManualConfig(
        key="experiences-relief-society",
        slug="experiences-supported-by-relief-society-2025",
        book="Experiences Supported by Relief Society",
        output_subdir="manuals/experiences-relief-society",
        authority=55,
        tags=["relief-society", "women", "covenants", "spiritual-experiences"],
        notes="2025 edition; 14 spiritual experiences with scripture + prophetic quotes",
    ),
    ManualConfig(
        key="children-youth-intro-guide",
        slug="introductory-guide-for-children-and-youth",
        book="Introductory Guide for Children and Youth",
        output_subdir="manuals/children-youth-intro",
        authority=50,
        tags=["children-and-youth", "development", "goal-setting", "covenant-path"],
        notes="2019 program launch guide; Luke 2:52 framework",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP C: Leadership Instruction (text summaries only)
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="leadership-instruction-apr-2023",
        slug="leadership-instruction-april-2023",
        book="Leadership Instruction: April 2023",
        output_subdir="manuals/leadership-instruction",
        authority=75,
        tags=["leadership", "training", "rising-generation", "temple-covenants"],
        notes="Bednar, Gong, Uchtdorf, Cordon, Christofferson — rising generation + temple",
    ),
    ManualConfig(
        key="leadership-instruction-oct-2023",
        slug="leadership-instruction-october-2023",
        book="Leadership Instruction: October 2023",
        output_subdir="manuals/leadership-instruction",
        authority=75,
        tags=["leadership", "training", "sabbath", "worship", "home-centered"],
        notes="Bednar — connection between worship at home and church (Jacob 5:75)",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP D: Seminaries & Institutes materials
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="charted-course",
        slug="the-charted-course-of-the-church-in-education",
        book="The Charted Course of the Church in Education",
        output_subdir="manuals/seminaries-and-institutes/charted-course",
        authority=72,
        tags=["education", "seminary", "institute", "philosophy", "first-presidency"],
        notes="J. Reuben Clark, 1938 — foundational for all S&I; required annual reading",
    ),
    ManualConfig(
        key="by-study-and-also-by-faith",
        slug="by-study-and-also-by-faith",
        book="By Study and Also by Faith: One Hundred Years of Seminaries and Institutes",
        output_subdir="manuals/seminaries-and-institutes/by-study-and-also-by-faith",
        authority=50,
        tags=["education", "seminary", "institute", "history", "centennial"],
        notes="2015 official institutional history; D&C 88:118",
    ),
    ManualConfig(
        key="teacher-development-skills",
        slug="teacher-development-skills",
        book="Teacher Development Skills",
        output_subdir="manuals/seminaries-and-institutes/teacher-development-skills",
        authority=55,
        tags=["education", "teaching", "seminary", "institute", "pedagogy"],
        notes="Companion to Teaching in the Savior's Way; S&I-specific training modules",
    ),
    ManualConfig(
        key="answering-my-gospel-questions",
        slug="answering-my-gospel-questions",
        book="Answering My Gospel Questions (Religion 280)",
        output_subdir="manuals/seminaries-and-institutes/answering-my-gospel-questions",
        authority=55,
        tags=["institute", "faith", "questions", "epistemology", "gospel-topics"],
        notes="2022 institute course; student-directed approach to difficult questions",
    ),
    ManualConfig(
        key="additional-teacher-resources",
        slug="additional-teacher-resources",
        book="Additional Teacher Resources",
        output_subdir="manuals/seminaries-and-institutes/additional-teacher-resources",
        authority=50,
        tags=["education", "teaching", "seminary", "institute"],
    ),
    ManualConfig(
        key="teacher-support-training",
        slug="teacher-support-and-training-resources",
        book="Teacher Support and Training Resources",
        output_subdir="manuals/seminaries-and-institutes/teacher-support-training",
        authority=50,
        tags=["education", "teaching", "seminary", "institute", "training"],
    ),
    ManualConfig(
        key="si-teacher-calling",
        slug="my-calling-as-a-stake-seminary-and-institute-teacher",
        book="My Calling as a Stake Seminary and Institute Teacher",
        output_subdir="manuals/seminaries-and-institutes/si-teacher-calling",
        authority=55,
        tags=["education", "seminary", "institute", "calling", "teaching"],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP E: Temple Preparation
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="preparing-to-enter-the-holy-temple",
        slug="preparing-to-enter-the-holy-temple",
        book="Preparing to Enter the Holy Temple",
        output_subdir="manuals/temple-preparation",
        authority=60,
        tags=["temple", "covenants", "ordinances", "preparation"],
        notes="2002; 12 topical sections on temple doctrine, worthiness, symbolism",
    ),
    ManualConfig(
        key="endowed-from-on-high",
        slug="endowed-from-on-high",
        book="Endowed from on High: Temple Preparation Seminar Teacher's Manual",
        output_subdir="manuals/temple-preparation",
        authority=60,
        tags=["temple", "covenants", "ordinances", "teacher", "preparation"],
        notes="2003; 7-lesson teacher's manual for temple prep seminars",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP F: Scripture Helps & Teaching Skills
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="scripture-helps-ot",
        slug="scripture-helps-old-testament",
        book="Scripture Helps: Old Testament",
        output_subdir="manuals/scripture-helps",
        authority=57,
        tags=["scripture-study", "old-testament", "study-aids"],
        notes="Study aids companion for OT reading",
    ),
    ManualConfig(
        key="scripture-helps-nt",
        slug="scripture-helps-new-testament",
        book="Scripture Helps: New Testament",
        output_subdir="manuals/scripture-helps",
        authority=57,
        tags=["scripture-study", "new-testament", "study-aids"],
        notes="Study aids companion for NT reading",
    ),
    ManualConfig(
        key="scripture-study-skills",
        slug="scripture-study-skills",
        book="Scripture Study Skills Teacher Manual",
        output_subdir="manuals/scripture-study-skills",
        authority=55,
        tags=["scripture-study", "teaching", "pedagogy"],
    ),
    ManualConfig(
        key="principles-of-christlike-teaching",
        slug="principles-of-christlike-teaching",
        book="Principles of Christlike Teaching",
        output_subdir="manuals/principles-of-christlike-teaching",
        authority=55,
        tags=["teaching", "pedagogy", "christlike-teaching"],
        bilingual=False,
        notes="EN-only; teaching principles companion",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP G: RS & Elders Quorum / General Conference
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="learning-from-general-conference",
        slug="learning-from-general-conference",
        book="Teaching, Learning, and Applying Messages from General Conference",
        output_subdir="manuals/learning-from-general-conference",
        authority=60,
        tags=["general-conference", "relief-society", "elders-quorum", "teaching"],
        notes="RS/EQ resource for applying conference messages in quorum/RS meetings",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP H: About the Hymns (pilot)
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="about-the-hymns",
        slug="sacred-music-gospel-study-resource-pilot",
        book="About the Hymns: Sacred Music Gospel Study Resource",
        output_subdir="manuals/about-the-hymns",
        authority=55,
        tags=["music", "hymns", "gospel-study", "pilot"],
        bilingual=False,
        notes="Pilot resource (~70 entries); tied to new hymnbook; EN-only; content grows over time",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP I: Family Resources
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="marriage-and-family-relations",
        slug="marriage-and-family-relations-instructors-manual",
        book="Marriage and Family Relations Instructor's Manual",
        output_subdir="manuals/family-resources",
        authority=55,
        tags=["family", "marriage", "teaching", "relationships"],
        notes="Only the instructor's manual is web-hosted; participant guide is 404",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP J: Interfaith & Religious Freedom
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="muslims-and-latter-day-saints",
        slug="muslims-and-latter-day-saints",
        book="Muslims and Latter-day Saints: Beliefs, Values, and Lifestyles",
        output_subdir="manuals/interfaith",
        authority=45,
        tags=["interfaith", "islam", "dialogue", "beliefs"],
        notes="Unique interfaith dialogue resource; official Church publication",
    ),
    ManualConfig(
        key="religious-freedom",
        slug="religious-freedom",
        book="Religious Freedom",
        output_subdir="manuals/religious-freedom",
        authority=50,
        tags=["religious-freedom", "liberty", "civic", "public-affairs"],
        bilingual=False,
        notes="Official Church position on religious liberty; EN-only",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP K: Succeed in School
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="succeed-in-school",
        slug="succeed-in-school-study-and-life-skills",
        book="Succeed in School: Study and Life Skills",
        output_subdir="manuals/succeed-in-school",
        authority=45,
        tags=["education", "youth", "life-skills", "study-skills"],
        notes="2021; 44 lessons for youth; global education initiative",
    ),
    ManualConfig(
        key="succeed-in-school-parent-guide",
        slug="help-your-children-succeed-in-school-parent-guide",
        book="Help Your Children Succeed in School: Parent Guide",
        output_subdir="manuals/succeed-in-school",
        authority=45,
        tags=["education", "parents", "children", "school"],
        notes="2021; 10-chapter guide for parents",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP L: Church History — missing from /study/books-and-lessons/church-history
    # ══════════════════════════════════════════════════════════════════════════

    # Priority 1: Church History Topics (encyclopedia, ~280 articles A-Z)
    ManualConfig(
        key="church-history-topics",
        slug="topics",
        book="Church History Topics",
        output_subdir="manuals/church-history-topics",
        authority=65,
        tags=["history", "church-history", "encyclopedia", "topics", "saints-companion"],
        uri_prefix="/history",
        link_contains="topics/",
        notes="300+ articles A-Z; companion to Saints series; expanded with each Saints volume since 2018",
    ),

    # Priority 2: Revelations in Context
    ManualConfig(
        key="revelations-in-context",
        slug="revelations-in-context",
        book="Revelations in Context",
        output_subdir="manuals/revelations-in-context",
        authority=65,
        tags=["history", "doctrine-and-covenants", "revelation", "context"],
        notes="55 essays; ed. Matthew McBride & James Goldberg (CH Dept) 2016; recommended by SS Gen Pres for CFM D&C; narrative backstory for each D&C section",
    ),

    # Priority 3: Daughters in My Kingdom
    ManualConfig(
        key="daughters-in-my-kingdom",
        slug="daughters-in-my-kingdom-the-history-and-work-of-relief-society",
        book="Daughters in My Kingdom: The History and Work of Relief Society",
        output_subdir="manuals/daughters-in-my-kingdom",
        authority=65,
        tags=["history", "relief-society", "women", "organization", "first-presidency"],
        notes="2011; FP-directed; sent to every woman in the Church; announced Oct 2010 GC by Julie B. Beck",
    ),

    # Priority 4: D&C Historical Resources 2025
    ManualConfig(
        key="dc-historical-resources-2025",
        slug="doctrine-and-covenants-historical-resources-2025",
        book="Doctrine and Covenants Historical Resources",
        output_subdir="manuals/dc-historical-resources",
        authority=60,
        tags=["history", "doctrine-and-covenants", "study-companion", "biographies"],
        uri_prefix="/history",
        notes="51 weekly lessons + ~170 biographical entries + chronology; meta-resource aggregating Revelations in Context, CH Topics, JSP; CFM D&C 2025",
    ),

    # Priority 5: At the Pulpit
    ManualConfig(
        key="at-the-pulpit",
        slug="at-the-pulpit",
        book="At the Pulpit: 185 Years of Discourses by Latter-day Saint Women",
        output_subdir="manuals/at-the-pulpit",
        authority=55,
        tags=["history", "women", "discourses", "relief-society", "illustration"],
        uri_prefix="/church-historians-press",
        notes="54 discourses 1831-2016; ed. Jennifer Reeder & Kate Holbrook; Church Historians Press 2017; first major scholarly collection of LDS women's discourses",
        author="Jennifer Reeder, Kate Holbrook (eds.)",
    ),

    # Priority 6: The First Fifty Years of Relief Society
    ManualConfig(
        key="first-fifty-years-rs",
        slug="the-first-fifty-years-of-relief-society",
        book="The First Fifty Years of Relief Society",
        output_subdir="manuals/first-fifty-years-rs",
        authority=55,
        tags=["history", "women", "relief-society", "primary-documents"],
        uri_prefix="/church-historians-press",
        bilingual=False,
        notes="78 primary docs 1842-1892; ed. Derr, Madsen, Holbrook, Grow; 2016; includes complete unabridged Nauvoo RS Minute Book + 6 Joseph Smith sermons to RS; EN-only",
    ),

    # Priority 7: JSP Revelations (D&C Study Companion)
    ManualConfig(
        key="jsp-revelations",
        slug="jsp-revelations",
        book="Joseph Smith's Revelations: A D&C Study Companion from the Joseph Smith Papers",
        output_subdir="manuals/jsp-revelations",
        authority=60,
        tags=["history", "doctrine-and-covenants", "joseph-smith", "joseph-smith-papers"],
        uri_prefix="/church-historians-press",
        bilingual=False,
        notes="137 entries; ed. Esplin, Grow, Godfrey; ebook 2016, updated 2024 for CFM D&C 2025; earliest manuscript versions + textual variants; EN-only",
    ),

    # Priority 8: Global Histories (83 countries)
    ManualConfig(
        key="global-histories",
        slug="global-histories",
        book="Global Histories",
        output_subdir="manuals/global-histories",
        authority=50,
        tags=["history", "global", "international", "illustration", "didactic"],
        uri_prefix="/history",
        notes="99+ countries (growing); stories+chronologies; first Church survey of intl history since 2018; didactic illustration value",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP M: Seminary Teacher Manuals — missing counterparts to student manuals
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="ot-seminary-teacher",
        slug="old-testament-seminary-manual-2026",
        book="Old Testament Seminary Teacher Manual",
        output_subdir="manuals/seminary/old-testament-teacher",
        authority=60,
        tags=["seminary", "old-testament", "scripture-study", "teacher", "cfm-aligned"],
        link_contains="old-testament-seminary-manual-2026",
        notes="2026; S&I 'Seminary 2.0' format — 4 lesson types (Scripture, Life Prep, Doctrinal Mastery, "
              "Assessment); CFM-aligned; announced Dec 2025; companion to OT Student Manual 2026",
    ),
    ManualConfig(
        key="bom-seminary-teacher",
        slug="book-of-mormon-seminary-teacher-manual-2024",
        book="Book of Mormon Seminary Teacher Manual",
        output_subdir="manuals/seminary/book-of-mormon-teacher",
        authority=60,
        tags=["seminary", "book-of-mormon", "scripture-study", "teacher", "cfm-aligned"],
        link_contains="book-of-mormon-seminary-teacher-manual",
        notes="2024; 160+ lessons; CFM-aligned; 2nd gen of current format; 32 home-study class lessons; "
              "companion to BofM Student Manual 2024",
    ),
    ManualConfig(
        key="nt-seminary-teacher",
        slug="new-testament-seminary-teacher-manual-2023",
        book="New Testament Seminary Teacher Manual",
        output_subdir="manuals/seminary/new-testament-teacher",
        authority=60,
        tags=["seminary", "new-testament", "scripture-study", "teacher", "cfm-aligned"],
        link_contains="new-testament-seminary-teacher-manual",
        notes="2023; inaugural manual of current S&I format; CFM-aligned; companion to NT Student Manual 2023",
    ),
    ManualConfig(
        key="dc-seminary-home-study",
        slug="doctrine-and-covenants-and-church-history-study-guide-for-home-study-seminary-students-2014",
        book="D&C and Church History Study Guide for Home-Study Seminary Students",
        output_subdir="manuals/seminary/doctrine-and-covenants-home-study",
        authority=55,
        tags=["seminary", "doctrine-and-covenants", "home-study", "youth"],
        link_contains="doctrine-and-covenants-and-church-history-study-guide",
        notes="2014 LEGACY format (pre-CFM, pre-Doctrinal Mastery); 32 units × 4 daily lessons = 128; "
              "student-facing guide for home-study; functionally superseded by D&C 2025 materials but not withdrawn",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP N: Family Resources — strengthening marriage/family manuals
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="families-and-temples",
        slug="families-and-temples",
        book="Families and Temples",
        output_subdir="manuals/teaching-pamphlets",
        authority=60,
        tags=["missionary", "family", "temple", "sealing", "pamphlet", "teaching"],
        link_contains="families-and-temples",
        notes="Missionary teaching pamphlet (Missionary Dept); PME ch3 lesson 5; 14 sections incl. "
              "full Proclamation text; NOT a family enrichment course",
    ),
    ManualConfig(
        key="marriage-family-instructor",
        slug="marriage-and-family-relations-instructors-manual",
        book="Marriage and Family Relations Instructor's Manual",
        output_subdir="manuals/family-resources",
        authority=55,
        tags=["family", "marriage", "teaching", "instructor", "sunday-school"],
        link_contains="marriage-and-family-relations-instructors-manual",
        notes="2000; Church Curriculum Dept; announced by pres. Boyd K. Packer; 16 lessons in 2 parts "
              "(marriage + parenting); doctrinal/scriptural focus; for Sunday meetings; companion to "
              "participant's study guide (already in corpus as family-resources/)",
    ),
    ManualConfig(
        key="strengthening-marriage-instructor",
        slug="strengthening-marriage-instructors-guide",
        book="Strengthening Marriage: Instructor's Guide",
        output_subdir="manuals/family-resources",
        authority=55,
        tags=["family", "marriage", "counseling", "instructor", "family-services"],
        link_contains="strengthening-marriage-instructors-guide",
        notes="2006; LDS Family Services; 6 sessions × 90 min; weekday use (not Sunday); "
              "therapeutic+doctrinal; role-playing and professional insights; complements M&FR (2000)",
    ),
    ManualConfig(
        key="strengthening-marriage-couples",
        slug="strengthening-marriage-resource-guide-for-couples",
        book="Strengthening Marriage: Resource Guide for Couples",
        output_subdir="manuals/family-resources",
        authority=55,
        tags=["family", "marriage", "counseling", "couples"],
        link_contains="strengthening-marriage-resource-guide",
        bilingual=False,
        notes="Companion to instructor guide; 6 sessions; EN-only (404 in spa)",
    ),
    ManualConfig(
        key="strengthening-family-instructor",
        slug="strengthening-the-family-instructors-guide",
        book="Strengthening the Family: Instructor's Guide",
        output_subdir="manuals/family-resources",
        authority=55,
        tags=["family", "parenting", "counseling", "instructor", "family-services"],
        link_contains="strengthening-the-family-instructors-guide",
        notes="2006; LDS Family Services; 9 sessions × 90 min; weekday use; therapeutic+doctrinal; "
              "parenting counterpart to Strengthening Marriage",
    ),
    ManualConfig(
        key="strengthening-family-parents",
        slug="strengthening-the-family-resource-guide-for-parents",
        book="Strengthening the Family: Resource Guide for Parents",
        output_subdir="manuals/family-resources",
        authority=55,
        tags=["family", "parenting", "counseling", "parents"],
        link_contains="strengthening-the-family-resource-guide",
        bilingual=False,
        notes="EN-only (404 in spa)",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP O: Self-Reliance secondary manuals
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="sr-self-reliance-plan",
        slug="self-reliance-plan-and-bishops-guide-explanation",
        book="Self-Reliance Plan and Bishop's Guide",
        output_subdir="manuals/self-reliance/self-reliance-plan",
        authority=50,
        tags=["self-reliance", "welfare", "bishop", "leadership", "operational"],
        notes="~2012 rev. 2024; Self-Reliance Services / Presiding Bishopric; operational forms — "
              "member assessment worksheet + bishop tracking companion; ref. General Handbook §22",
    ),
    ManualConfig(
        key="sr-perpetual-education",
        slug="perpetual-education-fund-for-self-reliance",
        book="Perpetual Education Fund for Self-Reliance",
        output_subdir="manuals/self-reliance/perpetual-education-fund",
        authority=50,
        tags=["self-reliance", "education", "perpetual-education-fund", "operational"],
        notes="2017; single lesson (~60 min) post-'Education for Better Work' course; explains PEF "
              "loans and repayment covenant; PEF announced by pres. Hinckley Apr 2001 GC; 110K+ beneficiaries",
    ),
    ManualConfig(
        key="sr-my-path",
        slug="my-path-for-self-reliance",
        book="My Path for Self-Reliance",
        output_subdir="manuals/self-reliance/my-path",
        authority=55,
        tags=["self-reliance", "welfare", "assessment", "on-ramp"],
        notes="2016; ~20-page devotional/assessment booklet; mandatory entry point to SR program; "
              "doctrine of self-reliance + self-assessment + course selection; 'Mi camino a la autosuficiencia'",
    ),
    ManualConfig(
        key="sr-facilitating-groups",
        slug="facilitating-groups-for-self-reliance-2018",
        book="Facilitating Groups for Self-Reliance",
        output_subdir="manuals/self-reliance/facilitating-groups",
        authority=50,
        tags=["self-reliance", "welfare", "facilitator", "groups"],
        notes="2018; trainer guide for group facilitators",
    ),
    ManualConfig(
        key="sr-leaders-guide",
        slug="leaders-guide-for-the-self-reliance-initiative",
        book="Leader's Guide for the Self-Reliance Initiative",
        output_subdir="manuals/self-reliance/leaders-guide",
        authority=55,
        tags=["self-reliance", "welfare", "leadership", "administration"],
        notes="2017; master admin guide for stake/ward leaders; covers doctrine, priesthood framework, "
              "stake committee, SR specialist callings, group methodology; ref. General Handbook",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP P: Institute new materials
    # ══════════════════════════════════════════════════════════════════════════

    ManualConfig(
        key="institute-student-readings",
        slug="institute-student-readings",
        book="Institute Student Readings",
        output_subdir="manuals/institute/student-readings",
        authority=60,
        tags=["institute", "scripture-study", "readings", "curriculum"],
        bilingual=False,
        notes="~2024; S&I reading compilation for ~35 courses (4 Cornerstone + 9 Scripture + 22+ other); "
              "readings are graduation requirement (100% for scripture, 75% for others); EN-only (404 in spa)",
    ),
    ManualConfig(
        key="institute-elevate",
        slug="institute-elevate-learning-experience",
        book="Institute Elevate Learning Experience",
        output_subdir="manuals/institute/elevate",
        authority=55,
        tags=["institute", "learning", "assessment", "cornerstone"],
        notes="2016; S&I assessment/enrichment framework (NOT a 2024 pilot); 3 options per course: "
              "Elevate Questions, Study Journal, Personal Project; mandatory for course credit",
    ),
]


# ── Self-Reliance courses ────────────────────────────────────────────────────
# All share the same structure: 10-12 lesson workbooks, group-facilitated,
# produced by Self-Reliance Services. Authority=55 (practical, not doctrinal).

def _self_reliance_config(slug: str, book: str,
                          tags: list[str] | None = None) -> ManualConfig:
    """Build a ManualConfig for a Self-Reliance course."""
    safe = slug.replace("-for-self-reliance", "").replace("-for-self-reliance", "")
    return ManualConfig(
        key=f"sr-{safe}",
        slug=slug,
        book=book,
        output_subdir=f"manuals/self-reliance/{safe}",
        authority=55,
        tags=["self-reliance", "welfare"] + (tags or []),
    )


_SELF_RELIANCE: list[ManualConfig] = [
    _self_reliance_config(
        "personal-finances-for-self-reliance",
        "Personal Finances for Self-Reliance",
        ["finances", "budgeting"],
    ),
    _self_reliance_config(
        "starting-and-growing-my-business-for-self-reliance",
        "Starting and Growing My Business for Self-Reliance",
        ["business", "entrepreneurship"],
    ),
    _self_reliance_config(
        "find-a-better-job-for-self-reliance",
        "Find a Better Job for Self-Reliance",
        ["employment", "job-search"],
    ),
    _self_reliance_config(
        "education-for-better-work-for-self-reliance",
        "Education for Better Work for Self-Reliance",
        ["education", "career"],
    ),
    _self_reliance_config(
        "emotional-resilience-for-self-reliance",
        "Finding Strength in the Lord: Emotional Resilience",
        ["mental-health", "emotional-resilience", "atonement"],
    ),
    _self_reliance_config(
        "my-foundation-for-self-reliance",
        "My Foundation for Self-Reliance",
        ["foundation", "principles"],
    ),
]


# ── Group B: "My Calling" single-page guides ────────────────────────────────
# Each guide is a small manual with sub-sections (Welcome, Getting Started,
# Focus, Resources).  They share authority=50, audience=leadership, and are
# EN-only (confirmed: spa returns 404 for most slugs).

def _calling_config(slug: str, book: str, level: str,
                    tags: list[str] | None = None) -> ManualConfig:
    """Build a ManualConfig for a 'My Calling' guide."""
    safe_slug = slug.replace("my-calling-as-a-", "").replace("my-calling-as-an-", "")
    return ManualConfig(
        key=f"calling-{safe_slug}",
        slug=slug,
        book=book,
        output_subdir=f"manuals/callings/{level}/{safe_slug}",
        authority=50,
        tags=["calling", level] + (tags or []),
        bilingual=False,
    )


_CALLING_GUIDES: list[ManualConfig] = [
    # ── Ward: Primary ────────────────────────────────────────────────────────
    _calling_config("my-calling-as-a-primary-president", "My Calling as a Primary President", "ward", ["primary"]),
    _calling_config("my-calling-as-a-counselor-in-the-primary-presidency", "My Calling as a Counselor in the Primary Presidency", "ward", ["primary"]),
    _calling_config("my-calling-as-a-primary-secretary", "My Calling as a Primary Secretary", "ward", ["primary"]),
    _calling_config("my-calling-as-a-primary-teacher", "My Calling as a Primary Teacher", "ward", ["primary"]),
    _calling_config("my-calling-as-a-nursery-leader", "My Calling as a Nursery Leader", "ward", ["primary"]),
    # ── Ward: Sunday School ──────────────────────────────────────────────────
    _calling_config("my-calling-as-a-sunday-school-president", "My Calling as a Sunday School President", "ward", ["sunday-school"]),
    _calling_config("my-calling-as-a-counselor-in-the-sunday-school-presidency", "My Calling as a Counselor in the Sunday School Presidency", "ward", ["sunday-school"]),
    _calling_config("my-calling-as-a-sunday-school-secretary", "My Calling as a Sunday School Secretary", "ward", ["sunday-school"]),
    _calling_config("my-calling-as-a-sunday-school-teacher", "My Calling as a Sunday School Teacher", "ward", ["sunday-school"]),
    # ── Ward: Relief Society ─────────────────────────────────────────────────
    _calling_config("my-calling-as-a-relief-society-president", "My Calling as a Relief Society President", "ward", ["relief-society"]),
    _calling_config("my-calling-as-a-counselor-in-the-relief-society-presidency", "My Calling as a Counselor in the Relief Society Presidency", "ward", ["relief-society"]),
    _calling_config("my-calling-as-a-relief-society-secretary", "My Calling as a Relief Society Secretary", "ward", ["relief-society"]),
    _calling_config("my-calling-as-a-relief-society-teacher", "My Calling as a Relief Society Teacher", "ward", ["relief-society"]),
    # ── Ward: Elders Quorum ──────────────────────────────────────────────────
    _calling_config("my-calling-as-an-elders-quorum-president", "My Calling as an Elders Quorum President", "ward", ["elders-quorum"]),
    _calling_config("my-calling-as-a-counselor-in-the-elders-quorum-presidency", "My Calling as a Counselor in the Elders Quorum Presidency", "ward", ["elders-quorum"]),
    _calling_config("my-calling-as-an-elders-quorum-secretary", "My Calling as an Elders Quorum Secretary", "ward", ["elders-quorum"]),
    # ── Ward: Young Women ────────────────────────────────────────────────────
    _calling_config("my-calling-as-a-young-women-class-president", "My Calling as a Young Women Class President", "ward", ["young-women"]),
    _calling_config("my-calling-as-a-young-women-class-counselor", "My Calling as a Young Women Class Counselor", "ward", ["young-women"]),
    _calling_config("my-calling-as-a-young-women-class-secretary", "My Calling as a Young Women Class Secretary", "ward", ["young-women"]),
    _calling_config("my-calling-as-a-young-women-president", "My Calling as a Young Women President", "ward", ["young-women"]),
    _calling_config("my-calling-as-a-counselor-in-the-young-women-presidency", "My Calling as a Counselor in the Young Women Presidency", "ward", ["young-women"]),
    _calling_config("my-calling-as-a-young-women-secretary", "My Calling as a Young Women Secretary", "ward", ["young-women"]),
    _calling_config("my-calling-as-a-young-women-adviser-or-specialist", "My Calling as a Young Women Adviser or Specialist", "ward", ["young-women"]),
    # ── Ward: Aaronic Priesthood ─────────────────────────────────────────────
    _calling_config("my-calling-as-a-priests-quorum-assistant", "My Calling as a Priests Quorum Assistant", "ward", ["aaronic-priesthood"]),
    _calling_config("my-calling-as-a-priests-quorum-secretary-2024", "My Calling as a Priests Quorum Secretary", "ward", ["aaronic-priesthood"]),
    _calling_config("my-calling-as-a-teachers-quorum-president-2024", "My Calling as a Teachers Quorum President", "ward", ["aaronic-priesthood"]),
    _calling_config("my-calling-as-a-teachers-quorum-secretary-2024", "My Calling as a Teachers Quorum Secretary", "ward", ["aaronic-priesthood"]),
    _calling_config("my-calling-as-a-counselor-in-the-teachers-quorum", "My Calling as a Counselor in the Teachers Quorum", "ward", ["aaronic-priesthood"]),
    _calling_config("my-calling-as-a-deacons-quorum-president", "My Calling as a Deacons Quorum President", "ward", ["aaronic-priesthood"]),
    _calling_config("my-calling-as-a-deacons-quorum-counselor", "My Calling as a Deacons Quorum Counselor", "ward", ["aaronic-priesthood"]),
    _calling_config("my-calling-as-a-deacons-quorum-secretary", "My Calling as a Deacons Quorum Secretary", "ward", ["aaronic-priesthood"]),
    _calling_config("my-calling-as-an-aaronic-priesthood-quorum-adviser-or-specialist", "My Calling as an Aaronic Priesthood Quorum Adviser", "ward", ["aaronic-priesthood"]),
    _calling_config("my-calling-as-an-aaronic-priesthood-quorum-specialist", "My Calling as an Aaronic Priesthood Quorum Specialist", "ward", ["aaronic-priesthood"]),
    # ── Ward: Bishopric ──────────────────────────────────────────────────────
    _calling_config("my-calling-as-a-bishop", "My Calling as a Bishop", "ward", ["bishopric"]),
    _calling_config("my-calling-as-a-counselor-in-the-bishopric", "My Calling as a Counselor in the Bishopric", "ward", ["bishopric"]),
    _calling_config("my-calling-as-a-ward-clerk", "My Calling as a Ward Clerk", "ward", ["bishopric"]),
    _calling_config("my-calling-as-an-executive-secretary", "My Calling as an Executive Secretary", "ward", ["bishopric"]),
    # ── Ward: Music ──────────────────────────────────────────────────────────
    _calling_config("my-calling-as-a-ward-music-coordinator", "My Calling as a Ward Music Coordinator", "ward", ["music"]),
    _calling_config("my-calling-as-a-ward-music-leader", "My Calling as a Ward Music Leader", "ward", ["music"]),
    _calling_config("my-calling-as-a-ward-accompanist", "My Calling as a Ward Accompanist", "ward", ["music"]),
    _calling_config("my-calling-as-a-ward-choir-director", "My Calling as a Ward Choir Director", "ward", ["music"]),
    _calling_config("my-calling-as-a-ward-choir-accompanist", "My Calling as a Ward Choir Accompanist", "ward", ["music"]),
    _calling_config("my-calling-as-a-ward-music-specialist", "My Calling as a Ward Music Specialist", "ward", ["music"]),
    # ── Ward: Temple & Family History ────────────────────────────────────────
    _calling_config("my-calling-as-a-temple-and-family-history-leader", "My Calling as a Temple and Family History Leader", "ward", ["temple", "family-history"]),
    _calling_config("my-calling-as-a-temple-and-family-history-consultant", "My Calling as a Temple and Family History Consultant", "ward", ["temple", "family-history"]),
    # ── Ward: Additional ─────────────────────────────────────────────────────
    _calling_config("my-calling-as-a-ward-disability-specialist", "My Calling as a Ward Disability Specialist", "ward", ["disability"]),

    # ── Stake: Primary ───────────────────────────────────────────────────────
    _calling_config("my-calling-as-a-stake-primary-president", "My Calling as a Stake Primary President", "stake", ["primary"]),
    _calling_config("my-calling-as-a-counselor-in-the-stake-primary-presidency", "My Calling as a Counselor in the Stake Primary Presidency", "stake", ["primary"]),
    _calling_config("my-calling-as-a-stake-primary-secretary", "My Calling as a Stake Primary Secretary", "stake", ["primary"]),
    # ── Stake: Sunday School ─────────────────────────────────────────────────
    _calling_config("my-calling-as-a-stake-sunday-school-president", "My Calling as a Stake Sunday School President", "stake", ["sunday-school"]),
    _calling_config("my-calling-as-a-stake-sunday-school-counselor", "My Calling as a Stake Sunday School Counselor", "stake", ["sunday-school"]),
    _calling_config("my-calling-as-a-stake-sunday-school-secretary", "My Calling as a Stake Sunday School Secretary", "stake", ["sunday-school"]),
    # ── Stake: Relief Society ────────────────────────────────────────────────
    _calling_config("my-calling-as-a-stake-relief-society-president", "My Calling as a Stake Relief Society President", "stake", ["relief-society"]),
    _calling_config("my-calling-as-a-counselor-in-the-stake-relief-society-presidency", "My Calling as a Counselor in the Stake Relief Society Presidency", "stake", ["relief-society"]),
    _calling_config("my-calling-as-a-stake-relief-society-secretary", "My Calling as a Stake Relief Society Secretary", "stake", ["relief-society"]),
    # ── Stake: Young Women ───────────────────────────────────────────────────
    _calling_config("my-calling-as-a-stake-young-women-president", "My Calling as a Stake Young Women President", "stake", ["young-women"]),
    _calling_config("my-calling-as-a-stake-young-women-counselor", "My Calling as a Stake Young Women Counselor", "stake", ["young-women"]),
    _calling_config("my-calling-as-a-stake-young-women-secretary", "My Calling as a Stake Young Women Secretary", "stake", ["young-women"]),
    # ── Stake: Young Men ─────────────────────────────────────────────────────
    _calling_config("my-calling-as-a-stake-young-men-president", "My Calling as a Stake Young Men President", "stake", ["young-men"]),
    _calling_config("my-calling-as-a-counselor-in-the-stake-young-men-presidency", "My Calling as a Counselor in the Stake Young Men Presidency", "stake", ["young-men"]),
    _calling_config("my-calling-as-a-stake-young-men-secretary", "My Calling as a Stake Young Men Secretary", "stake", ["young-men"]),
    # ── Stake: Music ─────────────────────────────────────────────────────────
    _calling_config("my-calling-as-a-stake-music-coordinator", "My Calling as a Stake Music Coordinator", "stake", ["music"]),
    _calling_config("my-calling-as-a-stake-music-specialist", "My Calling as a Stake Music Specialist", "stake", ["music"]),
    # ── Stake: Temple & Family History ───────────────────────────────────────
    _calling_config("my-calling-as-a-stake-temple-and-family-history-consultant", "My Calling as a Stake Temple and Family History Consultant", "stake", ["temple", "family-history"]),
    # ── Stake: Additional ────────────────────────────────────────────────────
    _calling_config("my-calling-as-a-stake-technology-specialist", "My Calling as a Stake Technology Specialist", "stake", ["technology"]),
]


def _all_configs() -> dict[str, ManualConfig]:
    configs: dict[str, ManualConfig] = {}
    for m in _STATIC_MANUALS:
        configs[m.key] = m
    for pk, _ps, _pn in _PROPHETS:
        c = _prophet_config(pk)
        if c:
            configs[pk] = c
    for cg in _CALLING_GUIDES:
        configs[cg.key] = cg
    for sr in _SELF_RELIANCE:
        configs[sr.key] = sr
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
    parser.add_argument("--all-callings", action="store_true",
                        help="Download all My Calling guides in sequence")
    parser.add_argument("--all-self-reliance", action="store_true",
                        help="Download all Self-Reliance courses in sequence")

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
    elif args.all_callings:
        targets = list(_CALLING_GUIDES)
    elif args.all_self_reliance:
        targets = list(_SELF_RELIANCE)
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
            if lang == "spa" and not config.bilingual:
                logger.info("[spa] Skipping %s (EN-only)", config.book)
                continue
            stats = download_manual(config, lang, session,
                                    dry_run=args.dry_run, limit=args.limit)
            total_downloaded += stats["downloaded"]
            total_errors += stats["errors"]

    logger.info("=== Total: %d pages downloaded, %d errors ===",
                total_downloaded, total_errors)
    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()
