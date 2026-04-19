"""Retroactive KG noise purge.

Applies the THREE new filters added in commit 08230ae6c
(scripture_ref, mojibake, html_fragment) to the live Neo4j graph.
Pre-existing filter reasons (archaic_verb, url_like, etc.) already
ran via R0 cleanup, so we don't re-sweep those.

Usage:
    python /app/scripts/purge_kg_noise.py --dry-run
    python /app/scripts/purge_kg_noise.py --apply
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter, defaultdict

from neo4j import GraphDatabase

sys.path.insert(0, "/app/src")
from alejandria.knowledge.gazetteer_lookup import is_garbage

URI = os.environ.get("ALEJANDRIA_NEO4J_URI", "bolt://neo4j:7687")
USER = os.environ.get("ALEJANDRIA_NEO4J_USER", "neo4j")
PASS = os.environ.get("ALEJANDRIA_NEO4J_PASSWORD", "alejandria")

# Filters added post-R0 cleanup. Re-runnable: subsequent purges only act
# on whatever passed the gate before but fails the gate now.
TARGET_REASONS = {
    "scripture_ref", "mojibake", "html_fragment",
    "leading_punct", "sentence_fragment_es", "lowercase_token",
    "markdown_heading", "measurement",
}

# Scripture refs are legitimate when the node's declared type is one of these.
# The filter exists to catch scripture refs *mis-classified* as person/concept/
# object — not to delete canonical scripture nodes.
SCRIPTURE_LEGITIMATE_TYPES = {"scripture", "scripture_reference"}

BATCH_SIZE = 25


def stream_all_entities(driver):
    q = "MATCH (e:Entity) RETURN elementId(e) AS id, e.name AS name, e.type AS type"
    with driver.session() as s:
        for r in s.run(q):
            yield r["id"], r["name"], r["type"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not args.dry_run and not args.apply:
        ap.error("choose --dry-run or --apply")

    driver = GraphDatabase.driver(URI, auth=(USER, PASS))

    ids_by_reason: dict[str, list[str]] = defaultdict(list)
    type_by_reason: dict[str, Counter] = defaultdict(Counter)
    samples: dict[str, list[str]] = defaultdict(list)
    # audit log: (id, name, type, reason) for every deletion
    audit_rows: list[tuple[str, str, str, str]] = []
    scanned = 0

    print("Scanning all Entity nodes...", flush=True)
    for nid, name, ntype in stream_all_entities(driver):
        scanned += 1
        if scanned % 100_000 == 0:
            print(f"  scanned {scanned:,}", flush=True)
        reason = is_garbage(name)
        if reason not in TARGET_REASONS:
            continue
        # Exempt legitimate scripture nodes from the scripture_ref filter.
        if reason == "scripture_ref" and ntype in SCRIPTURE_LEGITIMATE_TYPES:
            continue
        ids_by_reason[reason].append(nid)
        type_by_reason[reason][ntype] += 1
        audit_rows.append((nid, name, ntype, reason))
        if len(samples[reason]) < 5:
            samples[reason].append(f"[{ntype}] {name!r}")

    total_to_delete = sum(len(v) for v in ids_by_reason.values())
    print(f"\nScanned {scanned:,} nodes. Matched for deletion: {total_to_delete:,}\n")
    for reason in sorted(TARGET_REASONS):
        count = len(ids_by_reason.get(reason, []))
        print(f"  {reason}: {count:,}")
        for t, c in type_by_reason[reason].most_common(5):
            print(f"     by type: {t}={c:,}")
        for s in samples[reason]:
            print(f"     sample: {s}")
        print()

    # Always write audit log so the set is reproducible / restorable.
    import csv
    from datetime import datetime, timezone
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    audit_path = f"/app/data/kg-diagnostic/purge_audit_{stamp}.csv"
    with open(audit_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["neo4j_id", "name", "type", "reason"])
        w.writerows(audit_rows)
    print(f"Audit log: {audit_path} ({len(audit_rows):,} rows)\n")

    if args.dry_run:
        print("DRY RUN — no changes made.")
        return

    print(f"Applying deletion in batches of {BATCH_SIZE} (with retry-shrink)...",
          flush=True)
    import time as _time
    deleted = 0
    failed = 0
    with driver.session() as s:
        for reason, ids in ids_by_reason.items():
            i = 0
            current_batch = BATCH_SIZE
            while i < len(ids):
                batch = ids[i:i + current_batch]
                try:
                    s.run(
                        "MATCH (e:Entity) WHERE elementId(e) IN $ids DETACH DELETE e",
                        ids=batch,
                    ).consume()
                    deleted += len(batch)
                    i += len(batch)
                    if current_batch < BATCH_SIZE and i % (BATCH_SIZE * 4) == 0:
                        current_batch = min(BATCH_SIZE, current_batch * 2)
                    if deleted % 2500 < BATCH_SIZE or deleted == total_to_delete:
                        print(f"  {reason}: {deleted:,} / {total_to_delete:,}",
                              flush=True)
                except Exception as e:
                    if current_batch <= 1:
                        # single-node failure; skip and continue
                        print(f"  SKIP id={batch[0]}: {e!r}", flush=True)
                        failed += 1
                        i += 1
                        continue
                    current_batch = max(1, current_batch // 4)
                    print(f"  shrink batch -> {current_batch} after error",
                          flush=True)
                    _time.sleep(2)
    print(f"\nDeleted {deleted:,} nodes. Failed: {failed}.")
    driver.close()


if __name__ == "__main__":
    main()
