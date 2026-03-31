#!/usr/bin/env python3
"""Build bilingual concept bridge between GEE (ES) and TG/BD (EN).

Matches GEE Spanish entries with their English TG/BD counterparts by slug
similarity and title matching. Outputs a JSON mapping file used by the
definition lookup for cross-language queries.

Usage:
    python scripts/build_bilingual_bridge.py [--dry-run]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_ROOT / "corpus"
OUTPUT_FILE = CORPUS_DIR / "bilingual-concept-bridge.json"


def _normalize(s: str) -> str:
    """Normalize for fuzzy matching."""
    s = s.lower().strip()
    for src, dst in {"\u00e1": "a", "\u00e9": "e", "\u00ed": "i", "\u00f3": "o",
                     "\u00fa": "u", "\u00f1": "n", "\u00fc": "u"}.items():
        s = s.replace(src, dst)
    return re.sub(r"[^\w\s]", "", s).strip()


def _load_entries(directory: Path) -> dict[str, str]:
    """Load slug -> title mapping from .meta.json files."""
    entries = {}
    if not directory.exists():
        return entries
    for meta_file in directory.glob("*.meta.json"):
        if meta_file.name.startswith("_"):
            continue
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            title = meta.get("title", "")
            if title and title.lower() != "introduction":
                entries[meta_file.stem.replace(".meta", "")] = title
        except (json.JSONDecodeError, OSError):
            pass
    return entries


def build_bridge(dry_run: bool = False) -> dict:
    """Build the bilingual concept mapping."""
    # Load all sources
    gee_es = _load_entries(CORPUS_DIR / "es" / "study-aids" / "guide-to-scriptures")
    gee_en = _load_entries(CORPUS_DIR / "en" / "study-aids" / "guide-to-scriptures")
    tg_en = _load_entries(CORPUS_DIR / "en" / "study-aids" / "topical-guide")
    bd_en = _load_entries(CORPUS_DIR / "en" / "study-aids" / "bible-dictionary")

    print(f"GEE ES: {len(gee_es)} entries")
    print(f"GEE EN: {len(gee_en)} entries")
    print(f"TG EN: {len(tg_en)} entries")
    print(f"BD EN: {len(bd_en)} entries")

    # Strategy 1: Match GEE ES -> GEE EN by slug (same slug = same concept)
    bridge = []
    matched_slugs = set()

    for slug, es_title in gee_es.items():
        matches = []

        # Direct slug match in GEE EN
        if slug in gee_en:
            matches.append({"source": "gee-en", "slug": slug, "title": gee_en[slug]})

        # Direct slug match in TG
        if slug in tg_en:
            matches.append({"source": "tg", "slug": slug, "title": tg_en[slug]})

        # Direct slug match in BD
        if slug in bd_en:
            matches.append({"source": "bd", "slug": slug, "title": bd_en[slug]})

        if matches:
            bridge.append({
                "es_slug": slug,
                "es_title": es_title,
                "en_matches": matches,
            })
            matched_slugs.add(slug)

    unmatched = len(gee_es) - len(matched_slugs)

    print(f"\nMatched: {len(matched_slugs)} concepts")
    print(f"Unmatched: {unmatched} GEE ES entries (no slug match)")

    # Stats
    tg_matches = sum(1 for b in bridge if any(m["source"] == "tg" for m in b["en_matches"]))
    bd_matches = sum(1 for b in bridge if any(m["source"] == "bd" for m in b["en_matches"]))
    gee_matches = sum(1 for b in bridge if any(m["source"] == "gee-en" for m in b["en_matches"]))

    print(f"\nCross-references:")
    print(f"  GEE ES <-> GEE EN: {gee_matches}")
    print(f"  GEE ES <-> TG EN: {tg_matches}")
    print(f"  GEE ES <-> BD EN: {bd_matches}")

    if not dry_run:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(bridge, f, ensure_ascii=False, indent=2)
        print(f"\nWritten to: {OUTPUT_FILE}")

    return {"total": len(bridge), "unmatched": unmatched}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    build_bridge(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
