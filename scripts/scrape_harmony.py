#!/usr/bin/env python3
"""Download the Harmony of the Gospels from churchofjesuschrist.org.

The Harmony presents the life of Jesus Christ organized chronologically,
comparing parallel accounts across Matthew, Mark, Luke, John, AND
latter-day scripture (Book of Mormon, D&C, PGP) — a unique LDS resource.

Produces per section per language:
  corpus/{lang}/study-aids/harmony-of-the-gospels/{slug}.txt
  corpus/{lang}/study-aids/harmony-of-the-gospels/{slug}.meta.json

The meta.json includes a structured `parallel_events` list — each event
with its cross-references per gospel column. This enables the KG pipeline
to create PARALLEL_ACCOUNT_OF relations between passages from different volumes.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_harmony.py
    python scripts/scrape_harmony.py --dry-run
    python scripts/scrape_harmony.py --lang eng
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

from lib.church_scraper import (
    BASE_URL, CORPUS_ROOT, LANG_MAP, ChurchSession,
    write_corpus_file, fetch_api_page, html_to_structured_text,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_SUBDIR = "study-aids/harmony-of-the-gospels"

# All sections of the Harmony, in order
SECTIONS = [
    {
        "slug": "introduction",
        "uri": "/scriptures/harmony/introduction",
        "title_en": "Introduction to the Harmony of the Gospels",
        "title_es": "Introducción a la Armonía de los Evangelios",
        "is_table": False,
    },
    {
        "slug": "harmony-1",
        "uri": "/scriptures/harmony/harmony-1",
        "title_en": "Part I: Preparation for the Messianic Ministry",
        "title_es": "Parte I: Preparación para el Ministerio Mesiánico",
        "is_table": True,
    },
    {
        "slug": "harmony-2",
        "uri": "/scriptures/harmony/harmony-2",
        "title_en": "Part II: The Ministry of an Elias — John the Baptist",
        "title_es": "Parte II: El Ministerio de un Elías — Juan el Bautista",
        "is_table": True,
    },
    {
        "slug": "harmony-3",
        "uri": "/scriptures/harmony/harmony-3",
        "title_en": "Part III.A: An Early Galilean Ministry",
        "title_es": "Parte III.A: Un Ministerio Temprano en Galilea",
        "is_table": True,
    },
    {
        "slug": "harmony-4",
        "uri": "/scriptures/harmony/harmony-4",
        "title_en": "Part III.B: The Early Judean Ministry",
        "title_es": "Parte III.B: El Ministerio Temprano en Judea",
        "is_table": True,
    },
    {
        "slug": "harmony-5",
        "uri": "/scriptures/harmony/harmony-5",
        "title_en": "Part III.C: A Second Galilean Ministry",
        "title_es": "Parte III.C: Un Segundo Ministerio en Galilea",
        "is_table": True,
    },
    {
        "slug": "harmony-6",
        "uri": "/scriptures/harmony/harmony-6",
        "title_en": "Part III.D: North Galilean Ministry",
        "title_es": "Parte III.D: Ministerio en el Norte de Galilea",
        "is_table": True,
    },
    {
        "slug": "harmony-7",
        "uri": "/scriptures/harmony/harmony-7",
        "title_en": "Part III.E: The Perean and Later Judean Ministry",
        "title_es": "Parte III.E: El Ministerio en Perea y Judea Posterior",
        "is_table": True,
    },
    {
        "slug": "harmony-8",
        "uri": "/scriptures/harmony/harmony-8",
        "title_en": "Part IV: The Last Week — Atonement and Resurrection",
        "title_es": "Parte IV: La Última Semana — Expiación y Resurrección",
        "is_table": True,
    },
]

# Column header patterns for the 6 gospel columns
# The table headers vary slightly by language and edition
_COLUMN_PATTERNS = {
    "event": re.compile(r"event|evento|inciden", re.I),
    "location": re.compile(r"location|place|lugar|sitio", re.I),
    "matthew": re.compile(r"mat+h|mat\.", re.I),
    "mark": re.compile(r"mark|marcos|marc\.", re.I),
    "luke": re.compile(r"luke|lucas|luc\.", re.I),
    "john_lds": re.compile(r"john|juan|latter.day|latter day|revelaci", re.I),
}

# Scripture reference pattern for individual cells
_REF_RE = re.compile(
    r"(?:(?:\d\s+)?(?:"
    r"Gen(?:esis)?|Ex(?:od)?|Lev(?:iticus)?|Num(?:bers)?|Deut(?:eronomy)?|"
    r"Josh(?:ua)?|Judg(?:es)?|Ruth|(?:1|2)\s*Sam(?:uel)?|(?:1|2)\s*Kings?|"
    r"(?:1|2)\s*Chr(?:on)?|Ezra|Neh(?:emiah)?|Esth(?:er)?|Job|Ps(?:alms?)?|"
    r"Prov(?:erbs)?|Eccl(?:es)?|Song|Isa(?:iah)?|Jer(?:emiah)?|Lam(?:entations)?|"
    r"Ezek(?:iel)?|Dan(?:iel)?|Hosea|Joel|Amos|Obad(?:iah)?|Jonah|Mic(?:ah)?|"
    r"Nah(?:um)?|Hab(?:akkuk)?|Zeph(?:aniah)?|Haggai|Zech(?:ariah)?|Mal(?:achi)?|"
    r"Matt(?:hew)?|Mark|Luke|John|Acts|Rom(?:ans)?|(?:1|2)\s*Cor(?:inthians)?|"
    r"Gal(?:atians)?|Eph(?:esians)?|Phil(?:ippians)?|Col(?:ossians)?|"
    r"(?:1|2)\s*Thess(?:alonians)?|(?:1|2)\s*Tim(?:othy)?|Titus|Philem(?:on)?|"
    r"Heb(?:rews)?|Jas(?:tes)?|(?:1|2|3)\s*Pet(?:er)?|(?:1|2|3)\s*John|"
    r"Jude|Rev(?:elation)?|"
    r"(?:1|2|3|4)\s*Nep(?:hi)?|Jacob|Enos|Jarom|Omni|W\s*of\s*M|Mosiah|Alma|"
    r"Hel(?:aman)?|(?:3|4)\s*Nep(?:hi)?|Morm(?:on)?|Ether|Moro(?:ni)?|"
    r"D&C|Doctrine\s+and\s+Covenants|Moses|Abr(?:aham)?|JS[–—-]H|JS[–—-]M|"
    r"A\s*of\s*F|Articles?\s+of\s+Faith|"
    r"Nef(?:i)?|DyC|Doctrina|Moisés|Helamán|Moroni|"
    r"Gén(?:esis)?|Éxodo|Salmos?|Isaías?|Ezequiel|Mateo|Marcos|Luc(?:as)?|"
    r"Hechos|Romanos|Corintios|Gálatas|Efesios|Filipenses|Colosenses|"
    r"Tesalonicenses|Timoteo|Filemón|Hebreos|Apocalipsis|Abraham|Abrahán"
    r")"
    r")\s+\d+(?::\d+(?:[–—\-]\d+)?)?(?:\s*,\s*\d+(?::\d+(?:[–—\-]\d+)?)?)*",
    re.I,
)


@dataclass
class HarmonyEvent:
    """One row in the Harmony table."""
    event: str
    location: str
    refs: dict[str, list[str]] = field(default_factory=dict)
    # keys: "matthew", "mark", "luke", "john_lds"


def _extract_refs_from_cell(cell_text: str) -> list[str]:
    """Extract all scripture references from a cell's text."""
    refs = []
    for m in _REF_RE.finditer(cell_text):
        ref = re.sub(r"\s+", " ", m.group(0)).strip()
        if ref and ref not in refs:
            refs.append(ref)
    return refs


def _identify_column(header_text: str) -> Optional[str]:
    """Map a column header text to our canonical column key."""
    h = header_text.strip()
    for key, pattern in _COLUMN_PATTERNS.items():
        if pattern.search(h):
            return key
    return None


def parse_harmony_table(soup) -> list[HarmonyEvent]:
    """Parse a Harmony section's table into structured events.

    The table has 5–6 columns:
      Event | Location | Matthew | Mark | Luke | John/LDS Revelation
    (some sections may combine John+LDS into one column)
    """
    events: list[HarmonyEvent] = []

    for table in soup.find_all("table"):
        # Determine column mapping from header row
        col_map: dict[int, str] = {}  # col_index → canonical_key
        header_row = table.find("tr")
        if header_row:
            headers = header_row.find_all(["th", "td"])
            for i, h in enumerate(headers):
                key = _identify_column(h.get_text())
                if key:
                    col_map[i] = key

        # If we couldn't determine columns from headers, use positional defaults
        if not col_map:
            col_map = {0: "event", 1: "location", 2: "matthew",
                       3: "mark", 4: "luke", 5: "john_lds"}

        # Parse data rows (skip first row if it was the header)
        rows = table.find_all("tr")
        start = 1 if header_row else 0
        for row in rows[start:]:
            cells = row.find_all(["td", "th"])
            if not cells:
                continue

            ev_text = ""
            loc_text = ""
            refs: dict[str, list[str]] = {}

            for i, cell in enumerate(cells):
                cell_text = re.sub(r"\s+", " ", cell.get_text()).strip()
                col = col_map.get(i, "")

                if col == "event":
                    ev_text = cell_text
                elif col == "location":
                    loc_text = cell_text
                elif col in ("matthew", "mark", "luke", "john_lds"):
                    cell_refs = _extract_refs_from_cell(cell_text)
                    if cell_refs:
                        refs[col] = cell_refs

            if ev_text and len(ev_text) > 3:
                events.append(HarmonyEvent(
                    event=ev_text,
                    location=loc_text,
                    refs=refs,
                ))

    return events


def events_to_text(events: list[HarmonyEvent], title: str) -> str:
    """Render Harmony events as readable plain text for FTS/semantic indexing.

    Format designed to be searchable: event name + all gospel references
    in one block. Keeps the parallel nature visible.
    """
    lines = [title, "=" * len(title), ""]
    for ev in events:
        if ev.location:
            lines.append(f"{ev.event} ({ev.location})")
        else:
            lines.append(ev.event)

        col_labels = {
            "matthew": "Matthew", "mark": "Mark",
            "luke": "Luke", "john_lds": "John / Latter-day Scripture",
        }
        for col, label in col_labels.items():
            if col in ev.refs and ev.refs[col]:
                refs_str = "; ".join(ev.refs[col])
                lines.append(f"  {label}: {refs_str}")
        lines.append("")
    return "\n".join(lines)


def download_section(section: dict, lang: str, session: ChurchSession,
                     dry_run: bool) -> bool:
    """Download and save one Harmony section."""
    corpus_lang = LANG_MAP.get(lang, lang)
    output_dir = CORPUS_ROOT / corpus_lang / OUTPUT_SUBDIR
    slug = section["slug"]
    title = section["title_en"] if lang == "eng" else section["title_es"]
    url = f"{BASE_URL}/study{section['uri']}?lang={lang}"

    logger.info("  [%s] %s", lang, title)

    if dry_run:
        logger.info("    [dry-run] Would save %s/%s.txt", output_dir, slug)
        return True

    meta: dict = {
        "title": title,
        "category": "study-aids",
        "subcategory": "harmony-of-the-gospels",
        "authority": 80,
        "lang": corpus_lang,
        "source_url": url,
        "tags": ["harmony", "gospels", "jesus-christ", "parallel-accounts"],
    }

    if not section.get("is_table"):
        # Introduction: fetch as prose
        api_page = fetch_api_page(session, section["uri"], lang)
        if api_page and api_page.body_html:
            text = html_to_structured_text(api_page.body_html)
        else:
            try:
                soup = session.fetch_html(url)
                body = soup.find("div", class_="body-block") or soup.find("article")
                paragraphs = []
                if body:
                    for el in body.find_all(["p", "h2", "h3"]):
                        t = re.sub(r"\s+", " ", el.get_text()).strip()
                        if t:
                            paragraphs.append(t)
                text = "\n\n".join(paragraphs)
            except Exception as e:
                logger.error("    Fetch failed: %s", e)
                return False
    else:
        # Table section: fetch HTML and parse
        try:
            soup = session.fetch_html(url)
        except Exception as e:
            logger.error("    Fetch failed: %s", e)
            return False

        events = parse_harmony_table(soup)
        if not events:
            # Fallback: try API
            api_page = fetch_api_page(session, section["uri"], lang)
            if api_page and api_page.body_html:
                from bs4 import BeautifulSoup
                api_soup = BeautifulSoup(api_page.body_html, "html.parser")
                events = parse_harmony_table(api_soup)

        if not events:
            logger.warning("    No events parsed from table — saving prose fallback")
            try:
                api_page = fetch_api_page(session, section["uri"], lang)
                text = html_to_structured_text(api_page.body_html) if api_page else ""
            except Exception:
                text = ""
        else:
            text = events_to_text(events, title)
            meta["event_count"] = len(events)

            # Collect all unique refs across all columns for KG enrichment
            all_refs: list[str] = []
            for ev in events:
                for col_refs in ev.refs.values():
                    for r in col_refs:
                        if r not in all_refs:
                            all_refs.append(r)
            if all_refs:
                meta["scripture_refs"] = all_refs

            # Structured parallel events for KG pipeline
            # Each event: name, location, refs by gospel column
            # This is the input for PARALLEL_ACCOUNT_OF relations
            meta["parallel_events"] = [
                {
                    "event": ev.event,
                    **({"location": ev.location} if ev.location else {}),
                    **{
                        col: refs
                        for col, refs in ev.refs.items()
                        if refs
                    },
                }
                for ev in events
                if ev.refs  # only events with at least one reference
            ]

            logger.info("    Parsed %d events, %d total refs",
                        len(events), len(all_refs))

    if not text.strip():
        logger.error("    Empty text — skipping")
        return False

    write_corpus_file(output_dir, slug, text, meta)
    logger.info("    Saved: %s/%s.txt (%d chars)", output_dir, slug, len(text))
    return True


def main():
    parser = argparse.ArgumentParser(description="Download Harmony of the Gospels")
    parser.add_argument("--lang", choices=["eng", "spa", "both"], default="both")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--section", help="Download only this slug (e.g. harmony-8)")
    args = parser.parse_args()

    session = ChurchSession(delay=0.5)
    langs = ["eng", "spa"] if args.lang == "both" else [args.lang]
    sections = [s for s in SECTIONS if args.section is None or s["slug"] == args.section]

    if args.section and not sections:
        logger.error("Unknown section slug: %s", args.section)
        sys.exit(1)

    total = len(sections) * len(langs)
    ok = 0
    for lang in langs:
        logger.info("=== Language: %s ===", lang)
        for section in sections:
            if download_section(section, lang, session, args.dry_run):
                ok += 1

    logger.info("Done: %d/%d sections", ok, total)
    sys.exit(0 if ok == total else 1)


if __name__ == "__main__":
    main()
