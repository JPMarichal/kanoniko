#!/usr/bin/env python3
"""Download the official scripture abbreviations table from churchofjesuschrist.org.

Produces two files per language (EN + ES):
  corpus/{lang}/study-aids/abbreviations/abbreviations.txt
  corpus/{lang}/study-aids/abbreviations/abbreviations.meta.json

The meta.json includes a structured `abbreviations` dict mapping short form →
full name, directly usable by the scripture reference normalizer/parser.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_abbreviations.py
    python scripts/scrape_abbreviations.py --dry-run
    python scripts/scrape_abbreviations.py --lang eng
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.church_scraper import (
    BASE_URL, CORPUS_ROOT, LANG_MAP, ChurchSession, write_corpus_file,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# The abbreviation page lives at /scriptures/quad, not under /manual/
# It is NOT accessible via the JSON API — must be fetched as HTML.
PAGE_URL_TEMPLATE = f"{BASE_URL}/study/scriptures/quad?lang={{lang}}"

OUTPUT_SUBDIR = "study-aids/abbreviations"


def parse_abbreviations(soup) -> dict[str, str]:
    """Parse abbreviation tables from the page soup.

    Returns dict: {"1 Ne.": "1 Nephi", "D&C": "Doctrine and Covenants", ...}
    """
    abbrv: dict[str, str] = {}

    # Tables on this page list abbreviations as:
    #   <td>Abbr.</td><td>Full Name</td>  (in columns of 4 per row)
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            # Tables have 4 cells per row: abbr, name, abbr, name (two columns)
            i = 0
            while i + 1 < len(cells):
                abbr = cells[i].strip(".")
                full = cells[i + 1].strip()
                if abbr and full and len(abbr) <= 20 and len(full) >= 2:
                    # Store with and without trailing period
                    abbrv[cells[i]] = full   # e.g. "1 Ne." → "1 Nephi"
                    if abbr != cells[i]:
                        abbrv[abbr] = full   # e.g. "1 Ne" → "1 Nephi"
                i += 2

    # Also look for definition list patterns (dt/dd)
    for dl in soup.find_all("dl"):
        terms = dl.find_all("dt")
        defs = dl.find_all("dd")
        for dt, dd in zip(terms, defs):
            abbr = dt.get_text(strip=True)
            full = dd.get_text(strip=True)
            if abbr and full:
                abbrv[abbr] = full

    return abbrv


def build_text(abbrv: dict[str, str], lang: str) -> str:
    """Build the plain-text representation for FTS/semantic indexing."""
    lines = [
        "Scripture Abbreviations" if lang == "eng" else "Abreviaturas de las Escrituras",
        "=" * 40,
        "",
        "This reference lists the official abbreviations for all scripture volumes.",
        "",
    ]
    current_section = ""
    for short, full in abbrv.items():
        lines.append(f"{short}  —  {full}")
    return "\n".join(lines)


def download_abbreviations(lang: str, session: ChurchSession, dry_run: bool = False) -> bool:
    """Download and save abbreviations for one language."""
    corpus_lang = LANG_MAP.get(lang, lang)
    output_dir = CORPUS_ROOT / corpus_lang / OUTPUT_SUBDIR

    url = PAGE_URL_TEMPLATE.format(lang=lang)
    logger.info("Fetching abbreviations page: %s", url)

    if dry_run:
        logger.info("  [dry-run] Would save to %s", output_dir)
        return True

    soup = session.fetch_html(url)

    abbrv = parse_abbreviations(soup)
    if not abbrv:
        logger.error("No abbreviations parsed from page — check HTML structure")
        return False

    logger.info("  Parsed %d abbreviations", len(abbrv))

    text = build_text(abbrv, lang)

    meta = {
        "title": "Scripture Abbreviations" if lang == "eng" else "Abreviaturas de las Escrituras",
        "category": "study-aids",
        "subcategory": "abbreviations",
        "authority": 80,
        "lang": corpus_lang,
        "source_url": url,
        "abbreviations": abbrv,
        "tags": ["reference", "abbreviations", "scripture-refs"],
    }

    write_corpus_file(output_dir, "abbreviations", text, meta)
    logger.info("  Saved: %s/abbreviations.txt (%d chars, %d entries)",
                output_dir, len(text), len(abbrv))
    return True


def main():
    parser = argparse.ArgumentParser(description="Download scripture abbreviations")
    parser.add_argument("--lang", choices=["eng", "spa", "both"], default="both",
                        help="Language to download (default: both)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be done without writing files")
    args = parser.parse_args()

    session = ChurchSession(delay=0.5)
    langs = ["eng", "spa"] if args.lang == "both" else [args.lang]

    ok = 0
    for lang in langs:
        if download_abbreviations(lang, session, dry_run=args.dry_run):
            ok += 1

    logger.info("Done: %d/%d languages", ok, len(langs))
    sys.exit(0 if ok == len(langs) else 1)


if __name__ == "__main__":
    main()
