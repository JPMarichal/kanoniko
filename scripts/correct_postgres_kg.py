"""Apply the KG noise corrections to the live Postgres IONOS instance.

This is the Postgres equivalent of the Neo4j scripts:
  - purge_kg_noise.py        -> purge stage (is_garbage filters)
  - entity_resolution.py     -> merge stage (variant patterns)
  - backfill_family_relations.py -> family backfill stage

Combined here because Postgres lets us do everything in one transaction
per stage with simple SQL — no APOC needed.

Run:
    docker run --rm --network host \
        -e ALEJANDRIA_POSTGRES_HOST=127.0.0.1 \
        -e ALEJANDRIA_POSTGRES_PORT=15432 \
        -e ALEJANDRIA_POSTGRES_USER=... \
        -e ALEJANDRIA_POSTGRES_PASSWORD=... \
        -e ALEJANDRIA_POSTGRES_DB=alejandria \
        -v /mnt/c/own/alejandria:/repo \
        python:3.11-slim bash -c \
        "pip install -q psycopg[binary] && \
         python /repo/scripts/correct_postgres_kg.py --stage all --dry-run"
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

import psycopg

sys.path.insert(0, "/repo/src")
from alejandria.knowledge.gazetteer_lookup import is_garbage
from alejandria.knowledge.family_patterns import extract_family_hits

OUT_DIR = "/repo/data/kg-diagnostic"
os.makedirs(OUT_DIR, exist_ok=True)

PURGE_REASONS = {
    "scripture_ref", "mojibake", "html_fragment",
    "leading_punct", "sentence_fragment_es", "lowercase_token",
    "markdown_heading", "measurement",
}
SCRIPTURE_LEGITIMATE_TYPES = {"scripture", "scripture_reference"}
TYPE_PRIORITY = ["person", "people", "concept", "place"]
_CONTAINER_BLACKLIST = {n.lower() for n in (
    "Old Testament", "New Testament", "Bible", "Holy Bible",
    "Antiguo Testamento", "Nuevo Testamento", "Biblia", "Santa Biblia",
    "Book of Mormon", "Libro de Mormón", "Libro de Mormon",
    "Doctrine and Covenants", "Doctrina y Convenios",
    "Pearl of Great Price", "Perla de Gran Precio",
    "Scripture", "Scriptures", "Escritura", "Escrituras",
    "Himself", "Herself", "God", "Lord", "Señor", "Dios",
    "Father", "Mother", "Son", "Daughter", "Child",
    "Padre", "Madre", "Hijo", "Hija",
    "Man", "Woman", "Hombre", "Mujer", "MAN", "WOMAN",
)}

# Variant strippers for entity resolution.
_BULLET_PREFIX_RE = re.compile(r"^[\u2022\u2023\u25e6\u2043\u2219\u00b7]\s+")
_ARROW_PREFIX_RE = re.compile(r"^[\u21a9\u2190-\u21ff]\s+")
_POSSESSIVE_RE = re.compile(r"['\u2019]s$", flags=re.IGNORECASE)
_TRAILING_PUNCT_RE = re.compile(r"[,;:\.\s]+$")
_LEADING_QUOTE_RE = re.compile(r'^["\u201c\u201d\u2018\u2019]+\s*')
_DUP_WORD_RE = re.compile(r"^(\w+)\s+\1\s*$", flags=re.IGNORECASE)
_PRONUNCIATION_TAIL_RE = re.compile(
    r"^(\w+)\s+\w*['\u2019]\w*[\-\u2010\u2014]\w+$|"
    r"^(\w+)\s+\w+[\-\u2010\u2014]\w*['\u2019]\w*$"
)


def strip_to_canonical(name: str) -> tuple[str, str] | None:
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
        stripped = n[: m.start()]
        if stripped != n and len(stripped) >= 3:
            return stripped, "trailing_punct"
    return None


def connect():
    return psycopg.connect(
        host=os.environ["ALEJANDRIA_POSTGRES_HOST"],
        port=int(os.environ["ALEJANDRIA_POSTGRES_PORT"]),
        user=os.environ["ALEJANDRIA_POSTGRES_USER"],
        password=os.environ["ALEJANDRIA_POSTGRES_PASSWORD"],
        dbname=os.environ["ALEJANDRIA_POSTGRES_DB"],
    )


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


# --- STAGE 1: PURGE -----------------------------------------------------------

def stage_purge(conn, dry_run: bool) -> None:
    print("\n=== STAGE 1: PURGE ===\n")
    print("Scanning entities...", flush=True)
    ids_to_delete: dict[str, list[int]] = defaultdict(list)
    samples: dict[str, list[str]] = defaultdict(list)
    audit_rows = []
    n = 0

    with conn.cursor(name="purge_scan") as cur:
        cur.itersize = 5000
        cur.execute("SELECT id, name, entity_type FROM entities")
        for eid, name, etype in cur:
            n += 1
            if n % 100_000 == 0:
                print(f"  scanned {n:,}", flush=True)
            reason = is_garbage(name)
            if reason not in PURGE_REASONS:
                continue
            if reason == "scripture_ref" and etype in SCRIPTURE_LEGITIMATE_TYPES:
                continue
            ids_to_delete[reason].append(eid)
            audit_rows.append((eid, name, etype, reason))
            if len(samples[reason]) < 5:
                samples[reason].append(f"[{etype}] {name!r}")

    total = sum(len(v) for v in ids_to_delete.values())
    print(f"\nScanned {n:,} entities, matched for delete: {total:,}\n")
    for reason in sorted(PURGE_REASONS):
        cnt = len(ids_to_delete.get(reason, []))
        print(f"  {reason}: {cnt:,}")
        for s in samples[reason]:
            print(f"     sample: {s}")

    audit = f"{OUT_DIR}/pg_purge_audit_{stamp()}.csv"
    with open(audit, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entity_id", "name", "entity_type", "reason"])
        w.writerows(audit_rows)
    print(f"\nAudit log: {audit}")

    if dry_run:
        print("DRY RUN — no deletes.")
        return

    print(f"\nDeleting {total:,} rows from entities (relations cascade)...",
          flush=True)
    deleted = 0
    with conn.cursor() as cur:
        for reason, ids in ids_to_delete.items():
            for i in range(0, len(ids), 5000):
                batch = ids[i:i + 5000]
                cur.execute(
                    "DELETE FROM entities WHERE id = ANY(%s)", (batch,)
                )
                deleted += len(batch)
                if deleted % 25_000 < 5000 or deleted == total:
                    print(f"  {reason}: {deleted:,} / {total:,}", flush=True)
        conn.commit()
    print(f"\nDeleted {deleted:,} entity rows.")


# --- STAGE 2: ENTITY RESOLUTION (merge variants into canonicals) --------------

def stage_resolve(conn, dry_run: bool) -> None:
    print("\n=== STAGE 2: ENTITY RESOLUTION ===\n")
    print("Loading entity index...", flush=True)
    idx: dict[tuple[str, str], list[tuple[int, str]]] = defaultdict(list)
    all_rows: list[tuple[int, str, str]] = []
    with conn.cursor(name="resolve_scan") as cur:
        cur.itersize = 5000
        cur.execute("SELECT id, name, entity_type FROM entities")
        for eid, name, etype in cur:
            all_rows.append((eid, name, etype))
            idx[(name.strip().lower(), etype)].append((eid, name))
    print(f"  indexed {len(all_rows):,} entities", flush=True)

    merges: list[tuple[int, str, int, str, str, str]] = []
    stats = Counter()
    skipped = Counter()
    for eid, name, etype in all_rows:
        result = strip_to_canonical(name)
        if not result:
            continue
        candidate, pattern = result
        if not candidate or len(candidate) < 3:
            skipped[f"{pattern}:too_short"] += 1
            continue
        if candidate.lower() == name.strip().lower():
            continue
        targets = [
            (tid, tname) for (tid, tname) in idx.get((candidate.lower(), etype), [])
            if tid != eid
        ]
        if len(targets) != 1:
            skipped[f"{pattern}:{'no_canonical' if not targets else 'ambiguous'}"] += 1
            continue
        clean_id, clean_name = targets[0]
        merges.append((eid, name, clean_id, clean_name, etype, pattern))
        stats[pattern] += 1

    print(f"\nMerge candidates: {len(merges):,}\n")
    for k, v in stats.most_common():
        print(f"  {k}: {v:,}")
    print("\nSkipped:")
    for k, v in skipped.most_common(10):
        print(f"  {k}: {v:,}")

    audit = f"{OUT_DIR}/pg_resolution_audit_{stamp()}.csv"
    with open(audit, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dirty_id", "dirty_name", "clean_id", "clean_name",
                    "entity_type", "pattern"])
        w.writerows(merges)
    print(f"\nAudit log: {audit}")

    if dry_run:
        print("DRY RUN — no merges.")
        return

    print(f"\nMerging {len(merges):,} variants (per-row, skip-on-error)...",
          flush=True)
    # Drop merges where the dirty_id is also some other merge's clean_id —
    # those would create chained dependencies inside one transaction.
    clean_ids = {m[2] for m in merges}
    safe_merges = [m for m in merges if m[0] not in clean_ids]
    skipped_chain = len(merges) - len(safe_merges)
    if skipped_chain:
        print(f"  skipping {skipped_chain:,} chained merges "
              f"(target of one is source of another)", flush=True)

    merged = 0
    failed = 0
    with conn.cursor() as cur:
        for (dirty_id, _dn, clean_id, _cn, _t, _p) in safe_merges:
            try:
                cur.execute("BEGIN")
                # Redirect outgoing relations
                cur.execute(
                    "UPDATE relations SET src_id = %s "
                    "WHERE src_id = %s "
                    "  AND NOT EXISTS ("
                    "    SELECT 1 FROM relations r2 "
                    "    WHERE r2.src_id = %s AND r2.dst_id = relations.dst_id "
                    "      AND r2.rel_type = relations.rel_type"
                    "  )",
                    (clean_id, dirty_id, clean_id),
                )
                # Drop any remaining (would-be duplicates) outgoing
                cur.execute("DELETE FROM relations WHERE src_id = %s",
                            (dirty_id,))
                # Redirect incoming relations
                cur.execute(
                    "UPDATE relations SET dst_id = %s "
                    "WHERE dst_id = %s "
                    "  AND NOT EXISTS ("
                    "    SELECT 1 FROM relations r2 "
                    "    WHERE r2.dst_id = %s AND r2.src_id = relations.src_id "
                    "      AND r2.rel_type = relations.rel_type"
                    "  )",
                    (clean_id, dirty_id, clean_id),
                )
                cur.execute("DELETE FROM relations WHERE dst_id = %s",
                            (dirty_id,))
                # Delete the dirty entity
                cur.execute("DELETE FROM entities WHERE id = %s", (dirty_id,))
                cur.execute("COMMIT")
                merged += 1
                if merged % 500 == 0 or merged == len(safe_merges):
                    print(f"  merged {merged:,} / {len(safe_merges):,}",
                          flush=True)
            except Exception as e:
                cur.execute("ROLLBACK")
                failed += 1
                if failed <= 5:
                    print(f"  FAIL dirty={dirty_id} clean={clean_id}: {e}",
                          flush=True)
    print(f"\nMerged {merged}, failed {failed}, chained-skipped {skipped_chain}.")


# --- STAGE 3: FAMILY BACKFILL -------------------------------------------------

def stage_family(conn, dry_run: bool) -> None:
    print("\n=== STAGE 3: FAMILY BACKFILL ===\n")
    print("Loading entity index...", flush=True)
    idx: dict[str, list[tuple[int, str, str]]] = defaultdict(list)
    with conn.cursor(name="fam_idx") as cur:
        cur.itersize = 5000
        cur.execute("SELECT id, name, entity_type FROM entities")
        for eid, name, etype in cur:
            idx[name.strip().lower()].append((eid, name, etype))
    print(f"  indexed {sum(len(v) for v in idx.values()):,} entities", flush=True)

    def best_match(name: str):
        cands = idx.get(name.strip().lower())
        if not cands:
            return None
        if len(cands) == 1:
            return cands[0]
        by_type = {c[2]: c for c in cands}
        for pref in TYPE_PRIORITY:
            if pref in by_type:
                return by_type[pref]
        return cands[0]

    print("Scanning chunks...", flush=True)
    edges: list[tuple[int, str, str, int, str, str]] = []
    edge_keys: set[tuple[int, str, int]] = set()
    stats = Counter()
    n = 0
    with conn.cursor(name="fam_chunks") as cur:
        cur.itersize = 5000
        cur.execute("SELECT id, text FROM chunks WHERE text IS NOT NULL")
        for cid, text in cur:
            n += 1
            if n % 25_000 == 0:
                print(f"  scanned {n:,} chunks, candidates: {len(edges):,}",
                      flush=True)
            for hit in extract_family_hits(text):
                stats["hits_total"] += 1
                if (hit.from_name.lower() in _CONTAINER_BLACKLIST
                        or hit.to_name.lower() in _CONTAINER_BLACKLIST):
                    stats["blacklisted"] += 1
                    continue
                f = best_match(hit.from_name)
                t = best_match(hit.to_name)
                if not f:
                    stats["unresolved_from"] += 1
                    continue
                if not t:
                    stats["unresolved_to"] += 1
                    continue
                if f[0] == t[0]:
                    stats["self_loop"] += 1
                    continue
                key = (f[0], hit.relation, t[0])
                if key in edge_keys:
                    continue
                edge_keys.add(key)
                edges.append((f[0], f[1], hit.relation, t[0], t[1], f[2]))

    print(f"\nScanned {n:,} chunks. Candidate edges: {len(edges):,}\n")
    for k, v in stats.most_common():
        print(f"  {k}: {v:,}")

    audit = f"{OUT_DIR}/pg_family_backfill_audit_{stamp()}.csv"
    with open(audit, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["src_id", "src_name", "rel_type", "dst_id", "dst_name", "src_type"])
        w.writerows(edges)
    print(f"\nAudit log: {audit}")

    if dry_run:
        print("DRY RUN — no edges created.")
        return

    print(f"\nInserting {len(edges):,} edges (ON CONFLICT DO NOTHING)...",
          flush=True)
    # Use ON CONFLICT to avoid duplicates if the same edge already exists.
    inserted = 0
    with conn.cursor() as cur:
        for i in range(0, len(edges), 1000):
            batch = edges[i:i + 1000]
            params = [(e[0], e[3], e[2], "family", "curated",
                       "family_pattern_backfill") for e in batch]
            cur.executemany(
                "INSERT INTO relations (src_id, dst_id, rel_type, category, "
                "confidence, source) "
                "SELECT %s, %s, %s, %s, %s, %s "
                "WHERE NOT EXISTS ("
                "  SELECT 1 FROM relations r WHERE r.src_id = %s "
                "    AND r.dst_id = %s AND r.rel_type = %s"
                ")",
                [(*p, p[0], p[1], p[2]) for p in params],
            )
            inserted += len(batch)
            if inserted % 1000 == 0 or inserted == len(edges):
                print(f"  inserted/checked {inserted:,} / {len(edges):,}",
                      flush=True)
        conn.commit()
    print(f"\nDone. Final family-edge counts will reflect upserts only.")


# --- MAIN ---------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["purge", "resolve", "family", "all"],
                    required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not args.dry_run and not args.apply:
        ap.error("choose --dry-run or --apply")

    conn = connect()
    print(f"Connected to Postgres {conn.info.dbname}@{conn.info.host}")
    try:
        if args.stage in ("purge", "all"):
            stage_purge(conn, dry_run=args.dry_run)
        if args.stage in ("resolve", "all"):
            stage_resolve(conn, dry_run=args.dry_run)
        if args.stage in ("family", "all"):
            stage_family(conn, dry_run=args.dry_run)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
