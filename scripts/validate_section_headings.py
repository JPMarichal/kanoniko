"""
Validate section heading selectors across all scripture chapters.

Fetches every chapter from churchofjesuschrist.org and reports which ones
have intro, study-intro, and subtitle elements.  Runs one language at a time
to avoid throttling.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/validate_section_headings.py --lang eng
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/validate_section_headings.py --lang spa
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STRUCTURE_DIR = PROJECT_ROOT / "data" / "scripture_structure"

SITE_VOLUME_MAP = {"ot": "ot", "nt": "nt", "bom": "bofm", "dc": "dc-testament", "pgp": "pgp"}

# Same slug mappings as scrape_scriptures.py
with open(PROJECT_ROOT / "scripts" / "scrape_scriptures.py", encoding="utf-8") as _f:
    _src = _f.read()

# Import the book slug map by loading the scraper module
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from scrape_scriptures import build_chapter_url

_INTRO_RE = re.compile(r"^intro\d+$")


def check_chapter(url: str, session: requests.Session, ca: str) -> dict:
    """Fetch a chapter and detect intro/study-intro/subtitle/study-summary elements."""
    try:
        r = session.get(url, timeout=30, verify=ca or True)
        r.raise_for_status()
        r.encoding = "utf-8"
    except requests.RequestException as e:
        return {"error": str(e)}

    soup = BeautifulSoup(r.text, "lxml")
    article = soup.find("article")
    if not article:
        return {"error": "NO ARTICLE"}

    result = {}

    # study-summary
    el = article.find("p", class_=lambda c: c and "study-summary" in str(c))
    if el:
        result["study_summary"] = el.get_text().strip()[:120]

    # study-intro
    el = article.find("p", class_=lambda c: c and "study-intro" in str(c))
    if el:
        result["study_intro"] = el.get_text().strip()[:120]

    # subtitle
    el = article.find("p", class_=lambda c: c and "subtitle" in str(c))
    if el:
        result["subtitle"] = el.get_text().strip()[:120]

    # intro (id=intro1, intro2, etc.)
    intros = []
    for p in article.find_all("p", id=_INTRO_RE):
        text = re.sub(r"\s+", " ", p.get_text()).strip()
        if text:
            intros.append(text[:120])
    if intros:
        result["intro"] = intros

    # h2 section headings in body
    h2s = []
    for h2 in article.find_all("h2"):
        text = re.sub(r"\s+", " ", h2.get_text()).strip()
        if text:
            h2s.append(text[:80])
    if h2s:
        result["h2_headings"] = h2s

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate section heading selectors")
    parser.add_argument("--lang", required=True, choices=["eng", "spa"])
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--volume", help="Only check this volume")
    args = parser.parse_args()

    with open(STRUCTURE_DIR / "chapters.json", encoding="utf-8") as f:
        chapters = json.load(f)

    chapters = [c for c in chapters if c.get("corpus_path")]
    if args.volume:
        chapters = [c for c in chapters if c["volume_slug"] == args.volume]

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; AlejandriaBot/1.0; scripture-study)"})
    ca = os.environ.get("REQUESTS_CA_BUNDLE", "")

    # Counters per volume
    vol_stats = {}
    errors = []
    total = len(chapters)

    print(f"Validating {total} chapters ({args.lang}), delay={args.delay}s")
    print()

    for i, ch in enumerate(chapters):
        vol = ch["volume_slug"]
        ref = ch["reference_en"]
        url = build_chapter_url(vol, ch["book_slug"], ch["chapter_num"],
                                args.lang, ch["chapter_type"])

        result = check_chapter(url, session, ca)

        if vol not in vol_stats:
            vol_stats[vol] = {
                "total": 0, "study_summary": 0, "study_intro": 0,
                "subtitle": 0, "intro": 0, "h2_headings": 0, "errors": 0,
                "intro_refs": [], "study_intro_refs": [], "subtitle_refs": [],
                "h2_refs": [], "missing_summary": [],
            }
        s = vol_stats[vol]
        s["total"] += 1

        if "error" in result:
            s["errors"] += 1
            errors.append((ref, result["error"]))
        else:
            if "study_summary" in result:
                s["study_summary"] += 1
            else:
                s["missing_summary"].append(ref)
            if "study_intro" in result:
                s["study_intro"] += 1
                s["study_intro_refs"].append(ref)
            if "subtitle" in result:
                s["subtitle"] += 1
                s["subtitle_refs"].append(ref)
            if "intro" in result:
                s["intro"] += 1
                s["intro_refs"].append((ref, result["intro"]))
            if "h2_headings" in result:
                s["h2_headings"] += 1
                s["h2_refs"].append((ref, result["h2_headings"]))

        if (i + 1) % 100 == 0:
            print(f"  [{i+1}/{total}] {ref}...")

        time.sleep(args.delay)

    # Report
    print(f"\n{'='*80}")
    print(f"SECTION HEADING VALIDATION REPORT — {args.lang}")
    print(f"{'='*80}\n")

    for vol in ["ot", "nt", "bom", "dc", "pgp"]:
        if vol not in vol_stats:
            continue
        s = vol_stats[vol]
        print(f"--- {vol.upper()} ({s['total']} chapters) ---")
        print(f"  study_summary:  {s['study_summary']}/{s['total']}")
        print(f"  study_intro:    {s['study_intro']}")
        print(f"  subtitle:       {s['subtitle']}")
        print(f"  intro:          {s['intro']}")
        print(f"  h2_headings:    {s['h2_headings']}")
        print(f"  errors:         {s['errors']}")

        if s["missing_summary"]:
            print(f"  MISSING summary: {s['missing_summary'][:10]}")

        if s["study_intro_refs"]:
            refs = s["study_intro_refs"]
            print(f"  study_intro chapters: {refs[:5]}{'...' if len(refs) > 5 else ''}")

        if s["subtitle_refs"]:
            refs = s["subtitle_refs"]
            print(f"  subtitle chapters: {refs[:5]}{'...' if len(refs) > 5 else ''}")

        if s["intro_refs"]:
            print(f"  intro chapters ({len(s['intro_refs'])}):")
            for ref, texts in s["intro_refs"][:10]:
                print(f"    {ref}: {texts[0][:80]}")
            if len(s["intro_refs"]) > 10:
                print(f"    ... and {len(s['intro_refs'])-10} more")

        if s["h2_refs"]:
            print(f"  h2 chapters ({len(s['h2_refs'])}):")
            for ref, texts in s["h2_refs"][:5]:
                print(f"    {ref}: {texts}")
            if len(s["h2_refs"]) > 5:
                print(f"    ... and {len(s['h2_refs'])-5} more")

        print()

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for ref, err in errors[:20]:
            print(f"  {ref}: {err}")

    print(f"\nTotal: {total} chapters checked")


if __name__ == "__main__":
    main()
