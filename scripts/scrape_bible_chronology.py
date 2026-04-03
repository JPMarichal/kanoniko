#!/usr/bin/env python3
"""Download the Bible Chronology from churchofjesuschrist.org.

Covers Old Testament (~3,000 years, from Adam to 6 B.C.) and
New Testament (A.D. 1–96). Two pages plus an introduction.

Produces per page per language:
  corpus/{lang}/study-aids/bible-chronology/{slug}.txt
  corpus/{lang}/study-aids/bible-chronology/{slug}.meta.json

The meta.json includes a structured `events` list with date, description,
and external synchronisms — used by the KG pipeline to create Period and
Event nodes with temporal PRECEDED_BY / OCCURRED_DURING relations.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_bible_chronology.py
    python scripts/scrape_bible_chronology.py --dry-run
    python scripts/scrape_bible_chronology.py --lang eng
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
    BASE_URL, CORPUS_ROOT, LANG_MAP, ChurchSession, write_corpus_file,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_SUBDIR = "study-aids/bible-chronology"

PAGES = [
    {
        "slug": "introduction",
        "uri": "/scriptures/bible-chron/introduction",
        "title_en": "Bible Chronology — Introduction",
        "title_es": "Cronología Bíblica — Introducción",
        "is_table": False,
    },
    {
        "slug": "old-testament",
        "uri": "/scriptures/bible-chron/old-testament",
        "title_en": "Chronology of the Old Testament",
        "title_es": "Cronología del Antiguo Testamento",
        "is_table": True,
        "testament": "OT",
    },
    {
        "slug": "new-testament",
        "uri": "/scriptures/bible-chron/new-testament",
        "title_en": "Chronology of the New Testament",
        "title_es": "Cronología del Nuevo Testamento",
        "is_table": True,
        "testament": "NT",
    },
]


@dataclass
class ChronEvent:
    """A single event from the chronology table."""
    date: str           # e.g. "1095 B.C." or "A.D. 33"
    date_sort: Optional[int]  # year as int (negative = B.C.), for ordering
    event: str          # main event description
    synchronisms: list[str] = field(default_factory=list)   # external/parallel events
    persons: list[str] = field(default_factory=list)        # key figures mentioned


def _parse_date_sort(date_str: str) -> Optional[int]:
    """Convert date string to sortable int (negative = B.C.)."""
    date_str = date_str.strip()
    m = re.search(r"(\d+)", date_str)
    if not m:
        return None
    year = int(m.group(1))
    if "B.C." in date_str or "a.C." in date_str:
        return -year
    return year


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_chronology_table(soup) -> list[ChronEvent]:
    """Parse chronology HTML tables into structured events.

    The Church site uses tables with columns like:
      Date | Event (main) | Jewish History | External synchronisms
    or similar multi-column layouts. We capture:
    - All date-like cells
    - Main event text
    - Everything else as synchronisms
    """
    events: list[ChronEvent] = []

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue

            texts = [_clean(c.get_text()) for c in cells]

            # Skip header rows
            if all(t.isupper() or len(t) < 3 for t in texts):
                continue

            # Identify the date cell: contains a year pattern
            date_cell = ""
            event_cells = []
            for t in texts:
                if re.search(r"\d{2,4}\s*(B\.C\.|A\.D\.|a\.C\.)?", t) and len(t) < 30:
                    if not date_cell:
                        date_cell = t
                        continue
                event_cells.append(t)

            if not date_cell and not event_cells:
                continue

            # Main event is the longest non-date cell
            if event_cells:
                main = max(event_cells, key=len)
                synchs = [t for t in event_cells if t != main and len(t) > 2]
            else:
                main = date_cell
                date_cell = ""
                synchs = []

            if not main or len(main) < 4:
                continue

            # Extract person names from the event text (capitalized multi-word names)
            persons = re.findall(
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", main + " " + " ".join(synchs)
            )

            events.append(ChronEvent(
                date=date_cell,
                date_sort=_parse_date_sort(date_cell) if date_cell else None,
                event=main,
                synchronisms=[s for s in synchs if s],
                persons=list(dict.fromkeys(persons)),  # deduplicate preserving order
            ))

    return events


def events_to_text(events: list[ChronEvent], title: str) -> str:
    """Render events as readable plain text for FTS/semantic indexing."""
    lines = [title, "=" * len(title), ""]
    for ev in events:
        if ev.date:
            lines.append(f"{ev.date}: {ev.event}")
        else:
            lines.append(ev.event)
        for s in ev.synchronisms:
            lines.append(f"    [{s}]")
        lines.append("")
    return "\n".join(lines)


def download_page(page: dict, lang: str, session: ChurchSession,
                  dry_run: bool) -> bool:
    """Download and save a single chronology page."""
    corpus_lang = LANG_MAP.get(lang, lang)
    output_dir = CORPUS_ROOT / corpus_lang / OUTPUT_SUBDIR
    slug = page["slug"]
    title = page["title_en"] if lang == "eng" else page["title_es"]
    url = f"{BASE_URL}/study{page['uri']}?lang={lang}"

    logger.info("  [%s] %s", lang, title)

    if dry_run:
        logger.info("    [dry-run] Would save %s/%s.txt", output_dir, slug)
        return True

    # Fetch page HTML
    try:
        soup = session.fetch_html(url)
    except Exception as e:
        logger.error("    Fetch failed: %s", e)
        return False

    meta: dict = {
        "title": title,
        "category": "study-aids",
        "subcategory": "bible-chronology",
        "authority": 80,
        "lang": corpus_lang,
        "source_url": url,
        "tags": ["chronology", "timeline", "history"],
    }

    if page.get("is_table"):
        events = parse_chronology_table(soup)
        if not events:
            logger.warning("    No events parsed from table — falling back to prose")

        text = events_to_text(events, title)
        meta["testament"] = page.get("testament", "")
        meta["event_count"] = len(events)

        # Structured events for KG: date, description, synchronisms
        meta["events"] = [
            {
                "date": ev.date,
                **({"date_sort": ev.date_sort} if ev.date_sort is not None else {}),
                "event": ev.event,
                **({"synchronisms": ev.synchronisms} if ev.synchronisms else {}),
                **({"persons": ev.persons} if ev.persons else {}),
            }
            for ev in events
        ]

        logger.info("    Parsed %d events", len(events))
    else:
        # Prose introduction — extract with pandoc via API
        from lib.church_scraper import fetch_api_page, html_to_structured_text
        api_page = fetch_api_page(session, page["uri"], lang)
        if api_page and api_page.body_html:
            text = html_to_structured_text(api_page.body_html)
        else:
            # Fallback to direct HTML extraction
            body = soup.find("div", class_="body-block") or soup.find("article")
            paragraphs = []
            if body:
                for el in body.find_all(["p", "h2", "h3"]):
                    t = _clean(el.get_text())
                    if t:
                        paragraphs.append(t)
            text = "\n\n".join(paragraphs)

    if not text.strip():
        logger.error("    Empty text after extraction")
        return False

    write_corpus_file(output_dir, slug, text, meta)
    logger.info("    Saved: %s/%s.txt (%d chars)", output_dir, slug, len(text))
    return True


def main():
    parser = argparse.ArgumentParser(description="Download Bible Chronology study aid")
    parser.add_argument("--lang", choices=["eng", "spa", "both"], default="both")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    session = ChurchSession(delay=0.5)
    langs = ["eng", "spa"] if args.lang == "both" else [args.lang]

    total = len(PAGES) * len(langs)
    ok = 0
    for lang in langs:
        logger.info("=== Language: %s ===", lang)
        for page in PAGES:
            if download_page(page, lang, session, args.dry_run):
                ok += 1

    logger.info("Done: %d/%d pages", ok, total)
    sys.exit(0 if ok == total else 1)


if __name__ == "__main__":
    main()
