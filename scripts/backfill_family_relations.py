"""Corrective pass: scan corpus chunks for explicit family formulas and
backfill FATHER_OF / SPOUSE_OF edges in Neo4j.

Complements the preventive change in `KGExtractor._emit_family_relations`
(applies on next ingest). This script applies the same logic NOW to the
existing chunk text, so we don't have to wait for a 7+ h reindex to fix
the Amaleki/Abinadom-style gaps.

For each hit:
    1. The detected (parent, child) names are looked up in the live Neo4j
       Entity index (case-insensitive, any type — preferring `person`).
    2. If both sides resolve to a node, MERGE the typed edge.
    3. If a side is ambiguous (multiple types), prefer person > people > other.

Run inside the API container:
    docker exec alejandria-api python /app/scripts/backfill_family_relations.py --dry-run
    docker exec alejandria-api python /app/scripts/backfill_family_relations.py --apply
"""
from __future__ import annotations

import argparse
import csv
import os
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

from neo4j import GraphDatabase

sys.path.insert(0, "/app/src")
from alejandria.knowledge.family_patterns import extract_family_hits

URI = os.environ.get("ALEJANDRIA_NEO4J_URI", "bolt://neo4j:7687")
USER = os.environ.get("ALEJANDRIA_NEO4J_USER", "neo4j")
PASS = os.environ.get("ALEJANDRIA_NEO4J_PASSWORD", "alejandria")
SQLITE = os.environ.get("ALEJANDRIA_SQLITE_PATH",
                         "/app/data/sqlite/alejandria.db")

OUT_DIR = "/app/data/kg-diagnostic"

# Type preference when a name resolves to multiple Entity nodes.
TYPE_PRIORITY = ["person", "people", "concept", "place"]

# Names that NER promoted as "people" or "person" but are container concepts —
# they should never participate in a family relation. Found via dry-run sample
# inspection (Adam → OLD TESTAMENT, etc., from index/TOC chunks).
_CONTAINER_BLACKLIST = {
    n.lower() for n in (
        "Old Testament", "New Testament", "Bible", "Holy Bible",
        "Antiguo Testamento", "Nuevo Testamento", "Biblia", "Santa Biblia",
        "Book of Mormon", "Libro de Mormón", "Libro de Mormon",
        "Doctrine and Covenants", "Doctrina y Convenios",
        "Pearl of Great Price", "Perla de Gran Precio",
        "Scripture", "Scriptures", "Escritura", "Escrituras",
        "Himself", "Herself", "God", "Lord", "Señor", "Dios",
        "Father", "Mother", "Son", "Daughter", "Child",
        "Padre", "Madre", "Hijo", "Hija",
        "Man", "Woman", "Hombre", "Mujer",
        "MAN", "WOMAN",
    )
}


def load_entity_index(driver) -> dict[str, list[tuple[str, str]]]:
    """name.lower() -> [(canonical_name, type), ...]"""
    print("Loading entity index from Neo4j...", flush=True)
    idx: dict[str, list[tuple[str, str]]] = defaultdict(list)
    with driver.session() as s:
        for r in s.run("MATCH (e:Entity) RETURN e.name AS n, e.type AS t"):
            idx[r["n"].strip().lower()].append((r["n"], r["t"]))
    print(f"  loaded {sum(len(v) for v in idx.values()):,} entities into "
          f"{len(idx):,} keys", flush=True)
    return idx


def best_match(idx, name: str) -> tuple[str, str] | None:
    """Pick the best (name, type) for a captured name string."""
    candidates = idx.get(name.strip().lower())
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    # Multiple candidates — apply type priority.
    by_type = {t: (n, t) for (n, t) in candidates}
    for pref in TYPE_PRIORITY:
        if pref in by_type:
            return by_type[pref]
    return candidates[0]


def stream_chunks(sqlite_path: str):
    """Yield (chunk_id, text) from SQLite chunks table."""
    con = sqlite3.connect(sqlite_path)
    con.row_factory = sqlite3.Row
    cur = con.execute("SELECT id, text FROM chunks WHERE text IS NOT NULL")
    for row in cur:
        yield row["id"], row["text"]
    con.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0,
                    help="Process at most N chunks (0 = all)")
    args = ap.parse_args()
    if not args.dry_run and not args.apply:
        ap.error("choose --dry-run or --apply")

    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    idx = load_entity_index(driver)

    print(f"Scanning chunks from {SQLITE} ...", flush=True)
    edges_to_create: list[tuple[str, str, str, str, str]] = []
    # (from_name, from_type, relation, to_name, to_type)
    edge_keys: set[tuple[str, str, str]] = set()
    stats = Counter()
    chunks_scanned = 0
    for chunk_id, text in stream_chunks(SQLITE):
        chunks_scanned += 1
        if chunks_scanned % 25_000 == 0:
            print(f"  scanned {chunks_scanned:,} chunks, candidates so far: "
                  f"{len(edges_to_create):,}", flush=True)
        if args.limit and chunks_scanned >= args.limit:
            break
        for hit in extract_family_hits(text):
            stats["hits_total"] += 1
            if (hit.from_name.lower() in _CONTAINER_BLACKLIST
                    or hit.to_name.lower() in _CONTAINER_BLACKLIST):
                stats["blacklisted"] += 1
                continue
            f = best_match(idx, hit.from_name)
            t = best_match(idx, hit.to_name)
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
            edges_to_create.append((f[0], f[1], hit.relation, t[0], t[1]))

    print(f"\nScanned {chunks_scanned:,} chunks. "
          f"Resolved family edges: {len(edges_to_create):,}\n")
    for k, v in stats.most_common():
        print(f"  {k}: {v:,}")

    # Existence pre-check in Neo4j: don't insert edges that already exist.
    print("\nChecking existing edges in Neo4j...", flush=True)
    rels_by_type: dict[str, list[tuple[str, str, str, str, str]]] = defaultdict(list)
    for e in edges_to_create:
        rels_by_type[e[2]].append(e)

    new_edges: list[tuple[str, str, str, str, str]] = []
    with driver.session() as s:
        for rel, rows in rels_by_type.items():
            params = [
                {"f": r[0], "ft": r[1], "t": r[3], "tt": r[4]}
                for r in rows
            ]
            existing_keys = set()
            for chunk in (params[i:i + 1000] for i in range(0, len(params), 1000)):
                cypher = (
                    "UNWIND $rows AS row "
                    "MATCH (a:Entity {name: row.f, type: row.ft}) "
                    f"MATCH (a)-[r:{rel}]->(b:Entity {{name: row.t, type: row.tt}}) "
                    "RETURN row.f AS f, row.t AS t"
                )
                for hit in s.run(cypher, rows=chunk):
                    existing_keys.add((hit["f"], hit["t"]))
            for r in rows:
                if (r[0], r[3]) not in existing_keys:
                    new_edges.append(r)
            print(f"  {rel}: {len(rows):,} candidate, "
                  f"{len(rows) - sum(1 for r in rows if (r[0], r[3]) not in existing_keys):,} "
                  f"already exist, {sum(1 for r in rows if (r[0], r[3]) not in existing_keys):,} new",
                  flush=True)

    print(f"\nNet new edges to create: {len(new_edges):,}")

    # Audit log
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    audit = f"{OUT_DIR}/family_backfill_audit_{stamp}.csv"
    with open(audit, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["from_name", "from_type", "relation", "to_name", "to_type"])
        w.writerows(new_edges)
    print(f"Audit log: {audit}\n")

    print("Sample (first 20):")
    for e in new_edges[:20]:
        print(f"  ({e[0]} [{e[1]}]) -[{e[2]}]-> ({e[3]} [{e[4]}])")

    if args.dry_run:
        print("\nDRY RUN — no edges created.")
        return

    print(f"\nCreating {len(new_edges):,} edges in Neo4j...", flush=True)
    created = 0
    with driver.session() as s:
        for rel, rows in rels_by_type.items():
            new_rows = [r for r in rows if (r[0], r[3]) in {(e[0], e[3]) for e in new_edges}]
            for chunk in (new_rows[i:i + 500] for i in range(0, len(new_rows), 500)):
                cypher = (
                    "UNWIND $rows AS row "
                    "MATCH (a:Entity {name: row.f, type: row.ft}) "
                    "MATCH (b:Entity {name: row.t, type: row.tt}) "
                    f"MERGE (a)-[r:{rel}]->(b) "
                    "ON CREATE SET r.source = 'family_pattern_backfill', "
                    "r.created_at = datetime() "
                    "RETURN count(r) AS n"
                )
                params = [
                    {"f": r[0], "ft": r[1], "t": r[3], "tt": r[4]}
                    for r in chunk
                ]
                rec = s.run(cypher, rows=params).single()
                created += rec["n"] if rec else 0
                print(f"  {rel}: {created:,} created", flush=True)
    print(f"\nCreated {created} new family edges.")
    driver.close()


if __name__ == "__main__":
    main()
