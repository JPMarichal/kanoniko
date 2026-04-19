"""Entity resolution: merge malformed variants into canonical nodes.

For each "dirty" entity that fits a known variant pattern, compute the
implied canonical name. If exactly one clean entity exists with that
canonical (name, type), merge the dirty node into the clean one via
apoc.refactor.mergeNodes — relationships transfer automatically.

Variant patterns handled (conservative subset):
  bullet_prefix       "• Amaleki"             -> "Amaleki"
  arrow_prefix        "↩ Speiser"             -> "Speiser"
  possessive_en       "William Harris's"      -> "William Harris"
  possessive_es       "del Hermano Juárez"    -> "Hermano Juárez"
  duplicated_word     "Lydia LYDIA"           -> "Lydia"
  trailing_punct      "Vincent,"              -> "Vincent"
  leading_quote       '"Petroline ...'        -> "Petroline ..."
  pronunciation       "Lebana le-ba'-na"      -> "Lebana"

Run inside the API container:
    docker exec alejandria-api python /app/scripts/entity_resolution.py --dry-run
    docker exec alejandria-api python /app/scripts/entity_resolution.py --apply
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

from neo4j import GraphDatabase

URI = os.environ.get("ALEJANDRIA_NEO4J_URI", "bolt://neo4j:7687")
USER = os.environ.get("ALEJANDRIA_NEO4J_USER", "neo4j")
PASS = os.environ.get("ALEJANDRIA_NEO4J_PASSWORD", "alejandria")

OUT_DIR = "/app/data/kg-diagnostic"

# --- Variant strippers --------------------------------------------------------

_BULLET_PREFIX_RE = re.compile(r"^[\u2022\u2023\u25e6\u2043\u2219\u00b7]\s+")
_ARROW_PREFIX_RE = re.compile(r"^[\u21a9\u2190-\u21ff]\s+")
_POSSESSIVE_RE = re.compile(r"['\u2019]s$", flags=re.IGNORECASE)
_TRAILING_PUNCT_RE = re.compile(r"[,;:\.\s]+$")
_LEADING_QUOTE_RE = re.compile(r'^["\u201c\u201d\u2018\u2019]+\s*')
_DUP_WORD_RE = re.compile(r"^(\w+)\s+\1\s*$", flags=re.IGNORECASE)
_PRONUNCIATION_TAIL_RE = re.compile(
    # Pronunciation guides look like "Lebana le-ba'-na" or "Poratha po-ra'-tha":
    # the tail must contain BOTH a hyphen and an apostrophe to qualify.
    r"^(\w+)\s+\w*['\u2019]\w*[\-\u2010\u2014]\w+$|"
    r"^(\w+)\s+\w+[\-\u2010\u2014]\w*['\u2019]\w*$"
)


def strip_to_canonical(name: str) -> tuple[str, str] | None:
    """Return (canonical_candidate, pattern_name) or None if no pattern matches."""
    n = name.strip()
    if (m := _BULLET_PREFIX_RE.match(n)):
        return n[m.end():].strip(), "bullet_prefix"
    if (m := _ARROW_PREFIX_RE.match(n)):
        return n[m.end():].strip(), "arrow_prefix"
    if (m := _POSSESSIVE_RE.search(n)):
        return n[: m.start()].strip(), "possessive"
    if (m := _LEADING_QUOTE_RE.match(n)):
        return n[m.end():].strip(), "leading_quote"
    if (m := _DUP_WORD_RE.match(n)):
        return m.group(1), "duplicated_word"
    if (m := _PRONUNCIATION_TAIL_RE.match(n)):
        return (m.group(1) or m.group(2)), "pronunciation_tail"
    if (m := _TRAILING_PUNCT_RE.search(n)) and m.start() > 0:
        # Only useful when stripping changes something meaningful
        stripped = n[: m.start()]
        if stripped != n and len(stripped) >= 3:
            return stripped, "trailing_punct"
    return None


def find_merge_candidates(driver):
    """Stream entities, find dirty -> clean pairs.

    Returns:
        merges: list of (dirty_id, dirty_name, clean_id, clean_name, type, pattern)
        stats:  Counter of pattern -> count
        skipped: Counter of skip-reason -> count
    """
    # Build clean-name index in memory: (lowered_name, type) -> [(id, name), ...]
    print("Building canonical index from all entities...", flush=True)
    clean_idx: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    all_rows: list[tuple[str, str, str]] = []  # (id, name, type)
    with driver.session() as s:
        for r in s.run("MATCH (e:Entity) RETURN elementId(e) AS id, e.name AS name, e.type AS type"):
            nid, name, ntype = r["id"], r["name"], r["type"]
            all_rows.append((nid, name, ntype))
            key = (name.strip().lower(), ntype)
            clean_idx[key].append((nid, name))
    print(f"  indexed {len(all_rows):,} entities into {len(clean_idx):,} (name,type) keys",
          flush=True)

    merges = []
    stats = Counter()
    skipped = Counter()
    for nid, name, ntype in all_rows:
        result = strip_to_canonical(name)
        if not result:
            continue
        candidate, pattern = result
        if not candidate or len(candidate) < 3:
            skipped[f"{pattern}:too_short_after_strip"] += 1
            continue
        if candidate.lower() == name.strip().lower():
            skipped[f"{pattern}:no_change"] += 1
            continue
        key = (candidate.lower(), ntype)
        targets = clean_idx.get(key, [])
        # Skip if no clean match or ambiguous (multiple matches)
        if len(targets) == 0:
            skipped[f"{pattern}:no_canonical_match"] += 1
            continue
        # Filter out the dirty node itself (in case its canonical IS itself)
        targets = [(tid, tname) for tid, tname in targets if tid != nid]
        if len(targets) == 0:
            skipped[f"{pattern}:self_only"] += 1
            continue
        if len(targets) > 1:
            skipped[f"{pattern}:ambiguous_canonical"] += 1
            continue
        clean_id, clean_name = targets[0]
        merges.append((nid, name, clean_id, clean_name, ntype, pattern))
        stats[pattern] += 1
    return merges, stats, skipped


def apply_merges(driver, merges, batch_size=10):
    """Use APOC to merge dirty -> clean. The clean node keeps its name/properties;
    relationships from the dirty node transfer; dirty node is deleted."""
    cypher = """
    UNWIND $pairs AS pair
    MATCH (dirty:Entity) WHERE elementId(dirty) = pair.dirty_id
    MATCH (clean:Entity) WHERE elementId(clean) = pair.clean_id
    CALL apoc.refactor.mergeNodes([clean, dirty], {
        properties: 'discard',
        mergeRels: true
    })
    YIELD node
    RETURN count(node) AS merged
    """
    merged_total = 0
    failed = 0
    with driver.session() as s:
        i = 0
        current = batch_size
        while i < len(merges):
            batch = merges[i:i + current]
            pairs = [
                {"dirty_id": d_id, "clean_id": c_id}
                for (d_id, _, c_id, _, _, _) in batch
            ]
            try:
                rec = s.run(cypher, pairs=pairs).single()
                merged_total += rec["merged"] if rec else 0
                i += len(batch)
                if merged_total % 500 < current or i == len(merges):
                    print(f"  merged {merged_total:,} / {len(merges):,}", flush=True)
                if current < batch_size:
                    current = min(batch_size, current * 2)
            except Exception as e:
                if current <= 1:
                    print(f"  SKIP merge {batch[0]}: {e!r}", flush=True)
                    failed += 1
                    i += 1
                    continue
                current = max(1, current // 4)
                print(f"  shrink merge batch -> {current}", flush=True)
    return merged_total, failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not args.dry_run and not args.apply:
        ap.error("choose --dry-run or --apply")

    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    merges, stats, skipped = find_merge_candidates(driver)

    print(f"\nFound {len(merges):,} merge candidates.\n")
    print("By pattern:")
    for pattern, n in stats.most_common():
        print(f"  {pattern}: {n:,}")
    print("\nSkipped (no merge):")
    for reason, n in skipped.most_common(15):
        print(f"  {reason}: {n:,}")

    # Audit log
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    audit = f"{OUT_DIR}/entity_resolution_audit_{stamp}.csv"
    with open(audit, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dirty_id", "dirty_name", "clean_id", "clean_name", "type", "pattern"])
        w.writerows(merges)
    print(f"\nAudit log: {audit} ({len(merges):,} rows)")

    # Sample
    print("\nSample merges (first 15):")
    for m in merges[:15]:
        d_id, d_name, c_id, c_name, t, p = m
        print(f"  [{t}] {d_name!r} -> {c_name!r} ({p})")

    if args.dry_run:
        print("\nDRY RUN — no changes made.")
        return

    print(f"\nApplying merges via apoc.refactor.mergeNodes...")
    merged, failed = apply_merges(driver, merges)
    print(f"\nMerged {merged:,} dirty nodes into clean canonicals. Failed: {failed}.")
    driver.close()


if __name__ == "__main__":
    main()
