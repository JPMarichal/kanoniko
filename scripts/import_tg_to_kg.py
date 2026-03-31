#!/usr/bin/env python3
"""Import Topical Guide entries into the Knowledge Graph.

Parses TG .txt files and creates:
  - Entity nodes (type=concept) for each TG topic
  - RELATED_TO relations from "See also" cross-references
  - REFERENCED_IN relations linking concepts to scripture passages

This is a one-time import script, not part of the regular ingestion pipeline.
The TG is a curated cross-canonical index — its structure IS the knowledge graph.

Usage:
    python scripts/import_tg_to_kg.py [--dry-run] [--lang eng|spa] [--limit N]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── Project root on sys.path ──
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Config imported lazily in import_to_neo4j() — not needed for dry-run

# ── Constants ──

CORPUS_DIR = PROJECT_ROOT / "corpus"

TG_DIRS = {
    "eng": CORPUS_DIR / "en" / "study-aids" / "topical-guide",
    "spa": CORPUS_DIR / "es" / "study-aids" / "topical-guide",
}

# Scripture reference pattern — matches the citation at the end of a TG line
# Examples:
#   "Gen. 1:26 (Moses 2:26-27)."
#   "Matt. 23:12 (Luke 14:11; D&C 101:42; 112:3)."
#   "1 Ne. 3:7."
#   "D&C 4:5."
_SCRIPTURE_REF = re.compile(
    r",\s+"                          # comma + space before reference
    r"("
    r"(?:\d\s+)?"                    # optional leading number (1 Ne., 2 Chr., etc.)
    r"[A-Z][A-Za-z&\u00e9\u00f3]+\.?"  # book name (Gen., Matt., D&C, JS\u2014M, etc.)
    r"(?:\s+[A-Za-z&\u2014]+\.?)?"  # multi-word book names (of, the, etc.)
    r"\s+\d+:\d+"                    # chapter:verse
    r"(?:[,\u2013\-]\d+)*"          # verse ranges (1-3, 1,3)
    r")"
    r"("
    r"\s*\([^)]+\)"                 # optional parenthetical cross-refs
    r")?"
    r"\.?\s*$"                       # trailing period and whitespace
)

# Simpler: just grab everything after the last comma that looks like a reference
_REF_SIMPLE = re.compile(
    r",\s+"
    r"((?:\d\s+)?[A-Z][\w&\u00e9\u00f3\u2014.]+(?:\s+[\w&\u2014.]+)*\s+\d+[:\d,\u2013\-]*"
    r"(?:\s*\([^)]+\))?)"
    r"\.?\s*$"
)

# Book abbreviation patterns for validation
_BOOK_NAMES = re.compile(
    r"^(?:\d\s+)?"
    r"(?:Gen|Ex|Lev|Num|Deut|Josh|Judg|Ruth|Sam|Kgs|Chr|Ezra|Neh|Esth|Job|"
    r"Ps|Prov|Eccl|Song|Isa|Jer|Lam|Ezek|Dan|Hosea|Joel|Amos|Obad|Jonah|"
    r"Micah|Nah|Hab|Zeph|Hag|Zech|Mal|"
    r"Matt|Mark|Luke|John|Acts|Rom|Cor|Gal|Eph|Philip|Col|Thes|Tim|Titus|"
    r"Philem|Heb|James|Pet|Jude|Rev|"
    r"Ne|Nephi|Jacob|Enos|Jarom|Omni|Mosiah|Alma|Hel|Morm|Ether|Moro|"
    r"D&C|DC|OD|Moses|Abr|Abrah|JS[\u2014—-]M|JS[\u2014—-]H|A\s+of\s+F|"
    r"W\s+of\s+M|"
    # Spanish
    r"G[eé]n|[EÉ]x|Lev|N[uú]m|Deut|Josu[eé]|Juec|Rut|Reyes|Cr[oó]n|Esd|"
    r"Neh|Est|Sal|Prov|Ecl|Cant|Isa[ií]|Jer|Lam|Ezeq|Dan|Oseas|Am[oó]s|"
    r"Abd|Jon[aá]s|Miq|Nah|Hab|Sof|Hag|Zac|Mal|"
    r"Mateo|Marcos|Lucas|Juan|Hech|Rom|Corintios|G[aá]l|Efes|Filip|Col|Tes|"
    r"Timoteo|Tito|Filem|Hebr|Santiago|Pedro|Judas|Apoc|"
    r"Nefi|Jacob|En[oó]s|Jar[oó]m|Omni|Mos[ií]|Alma|Hel|Morm|[EÉ]ter|Moro|"
    r"DyC|Mois[eé]s|Abr)"
    r"\b",
    re.IGNORECASE,
)


def parse_tg_entry(txt_path: Path) -> dict:
    """Parse a single TG .txt file.

    Returns:
        {
            "title": str,
            "slug": str,
            "see_also": [str, ...],       # Related topic names
            "bd_refs": [str, ...],         # Bible Dictionary cross-refs
            "references": [                # Scripture references
                {"snippet": str, "ref": str, "xrefs": [str, ...]},
                ...
            ],
        }
    """
    meta_path = txt_path.with_suffix(".meta.json")
    slug = txt_path.stem

    title = slug.replace("-", " ").title()
    see_also_raw = []

    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        title = meta.get("title", title)
        see_also_raw = meta.get("see_also", [])

    text = txt_path.read_text(encoding="utf-8").strip()
    if not text:
        return {"title": title, "slug": slug, "see_also": [],
                "bd_refs": [], "references": []}

    # ── Parse See Also ──
    see_also = []
    bd_refs = []
    for sa_line in see_also_raw:
        # Remove "See also " / "See " prefix
        content = re.sub(r"^See\s+(?:also\s+)?", "", sa_line, flags=re.IGNORECASE).strip()
        # Split by semicolons
        for item in content.split(";"):
            item = item.strip().rstrip(".")
            if not item:
                continue
            if item.startswith("BD ") or item.startswith("BD\u00a0"):
                bd_refs.append(item[3:].strip())
            else:
                see_also.append(item)

    # ── Parse scripture references ──
    references = []
    seen_refs = set()  # deduplicate (faith.txt has duplicated content)
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip "See also" lines (already parsed from meta)
        if line.lower().startswith("see also") or line.lower().startswith("see "):
            if line.lower().startswith("see also"):
                continue
            # "See BD Aaron" type redirects
            if re.match(r"^See\s+BD\s+", line, re.IGNORECASE):
                continue
            # "See [Topic]" redirects — skip
            if not re.search(r"\d+:\d+", line):
                continue

        # Try to extract reference from end of line
        ref_match = _REF_SIMPLE.search(line)
        if ref_match:
            ref_text = ref_match.group(1).strip().rstrip(".")
            snippet = line[:ref_match.start()].strip().rstrip(",").strip()

            # Validate it looks like a real scripture ref
            if _BOOK_NAMES.match(ref_text):
                # Parse cross-refs from parentheses
                xrefs = []
                paren_match = re.search(r"\(([^)]+)\)", ref_text)
                main_ref = ref_text
                if paren_match:
                    main_ref = ref_text[:paren_match.start()].strip()
                    xref_text = paren_match.group(1)
                    xrefs = [x.strip() for x in xref_text.split(";") if x.strip()]

                dedup_key = (snippet[:40], main_ref)
                if dedup_key not in seen_refs:
                    seen_refs.add(dedup_key)
                    references.append({
                        "snippet": snippet,
                        "ref": main_ref,
                        "xrefs": xrefs,
                    })

    return {
        "title": title,
        "slug": slug,
        "see_also": see_also,
        "bd_refs": bd_refs,
        "references": references,
    }


def import_to_neo4j(entries: list[dict], dry_run: bool = False) -> dict:
    """Import parsed TG entries into Neo4j.

    Returns stats dict.
    """
    if dry_run:
        stats = {"concepts": 0, "related_to": 0, "referenced_in": 0, "bd_links": 0}
        for entry in entries:
            if entry["references"] or entry["see_also"]:
                stats["concepts"] += 1
            stats["related_to"] += len(entry["see_also"])
            stats["referenced_in"] += len(entry["references"])
            stats["bd_links"] += len(entry["bd_refs"])
        return stats

    from alejandria.config import settings
    from alejandria.knowledge.neo4j_client import Neo4jClient

    client = Neo4jClient(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )

    stats = {"concepts": 0, "related_to": 0, "referenced_in": 0, "bd_links": 0}

    for entry in entries:
        title = entry["title"]
        has_content = entry["references"] or entry["see_also"]

        if not has_content:
            continue

        # Create concept node
        client.merge_entity(title, "concept")
        stats["concepts"] += 1

        # Create RELATED_TO relations for "See also" topics
        for related in entry["see_also"]:
            client.merge_entity(related, "concept")
            client.merge_relation(
                from_name=title,
                from_type="concept",
                rel_type="RELATED_TO",
                to_name=related,
                to_type="concept",
                properties={
                    "confidence": "curated",
                    "source": "topical_guide",
                },
            )
            stats["related_to"] += 1

        # Create RELATED_TO for BD cross-refs
        for bd_topic in entry["bd_refs"]:
            client.merge_entity(bd_topic, "concept")
            client.merge_relation(
                from_name=title,
                from_type="concept",
                rel_type="RELATED_TO",
                to_name=bd_topic,
                to_type="concept",
                properties={
                    "confidence": "curated",
                    "source": "topical_guide_bd_xref",
                },
            )
            stats["bd_links"] += 1

        # Create REFERENCED_IN relations for scripture passages
        for ref_entry in entry["references"]:
            ref = ref_entry["ref"]
            # Create a scripture node for the reference
            client.merge_entity(ref, "scripture")
            client.merge_relation(
                from_name=title,
                from_type="concept",
                rel_type="REFERENCED_IN",
                to_name=ref,
                to_type="scripture",
                properties={
                    "confidence": "curated",
                    "source": "topical_guide",
                    "snippet": ref_entry["snippet"][:200],
                },
            )
            stats["referenced_in"] += 1

    client.close()
    return stats


def main():
    parser = argparse.ArgumentParser(description="Import Topical Guide into KG")
    parser.add_argument("--lang", default="eng", choices=["eng", "spa"])
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse and count without writing to Neo4j")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit number of entries to process")
    parser.add_argument("--show-sample", type=int, default=0,
                        help="Print N sample entries for inspection")
    args = parser.parse_args()

    tg_dir = TG_DIRS.get(args.lang)
    if not tg_dir or not tg_dir.exists():
        print(f"TG directory not found: {tg_dir}")
        return

    # Collect all .txt files (skip meta.json and mappings)
    txt_files = sorted(
        f for f in tg_dir.glob("*.txt")
        if not f.name.startswith("_")
    )

    if args.limit > 0:
        txt_files = txt_files[:args.limit]

    print(f"=== Topical Guide -> KG ({args.lang}) ===")
    print(f"  Source: {tg_dir}")
    print(f"  Files: {len(txt_files)}")
    if args.dry_run:
        print("  Mode: DRY RUN (parse only)")
    print()

    # Parse all entries
    entries = []
    empty = 0
    for txt_file in txt_files:
        entry = parse_tg_entry(txt_file)
        if entry["references"] or entry["see_also"]:
            entries.append(entry)
        else:
            empty += 1

    print(f"  Parsed: {len(entries)} entries with content, {empty} empty/redirect-only")

    # Show samples
    if args.show_sample > 0:
        print(f"\n  === Sample entries ===")
        for entry in entries[:args.show_sample]:
            print(f"\n  [{entry['title']}]")
            if entry["see_also"]:
                print(f"    See also: {'; '.join(entry['see_also'][:5])}")
            if entry["bd_refs"]:
                print(f"    BD refs: {'; '.join(entry['bd_refs'])}")
            print(f"    References: {len(entry['references'])}")
            for ref in entry["references"][:3]:
                xr = f" ({'; '.join(ref['xrefs'])})" if ref["xrefs"] else ""
                print(f"      - {ref['snippet'][:60]}... -> {ref['ref']}{xr}")
        print()

    # Import
    stats = import_to_neo4j(entries, dry_run=args.dry_run)

    print(f"\n=== Results ===")
    print(f"  Concept nodes: {stats['concepts']}")
    print(f"  RELATED_TO edges: {stats['related_to']}")
    print(f"  REFERENCED_IN edges: {stats['referenced_in']}")
    print(f"  BD cross-links: {stats['bd_links']}")
    total = stats["related_to"] + stats["referenced_in"] + stats["bd_links"]
    print(f"  Total new edges: {total}")


if __name__ == "__main__":
    main()
