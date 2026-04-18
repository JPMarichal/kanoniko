"""R7 — Kill low-value noise relations from the migrated KG.

See docs/kg-ingestion-refactor.md §3 R7. The rationale: ~60 % of the 54.5M
relations after R0 are llm_low co-occurrence-style edges (CO_OCCURS_WITH,
ASSOCIATED_WITH, RELATED_TO) that inflate the graph without improving search
quality. They can be reconstructed on-demand via pgvector similarity between
entity profile embeddings when truly needed — no need to persist them.

Two tiers:

    * --conservative (default)
        Deletes:
            rel_type = 'CO_OCCURS_WITH'    (all, ~27.8M)
            rel_type = 'ASSOCIATED_WITH' AND confidence = 'llm_low' (~5.0M)
            rel_type = 'RELATED_TO'     AND confidence = 'llm_low' (~550k)
        Preserves potentially-semantic llm_low rel_types (TEACHES, BELONGS_TO,
        LIVED_DURING, REFERENCED_IN). Total ~33M rows removed.

    * --aggressive
        All of the above PLUS:
            rel_type IN ('BELONGS_TO', 'LIVED_DURING', 'EXISTS_DURING',
                         'REFERENCED_IN', 'TEACHES') AND confidence = 'llm_low'
        Total ~53M rows removed. Only ~1.5M curated + metadata edges remain.

Safety:
    * Always NEVER touch confidence IN ('curated', 'metadata', 'llm_high') or
      verified = true rows. Those are preserved regardless of tier.
    * Default is --dry-run. Requires --apply to mutate.
    * VACUUM FULL is optional (--vacuum) because it locks and can take time.

Usage::

    python -m alejandria.storage.postgres.kg_r7_kill_noise --dry-run
    python -m alejandria.storage.postgres.kg_r7_kill_noise --apply
    python -m alejandria.storage.postgres.kg_r7_kill_noise --apply --aggressive --vacuum
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from dataclasses import dataclass, field

import psycopg

from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Predicate builders
# --------------------------------------------------------------------------- #

# Relations that are always preserved regardless of tier. These carry real
# signal (curated seeds, metadata-derived, high-confidence LLM, or manually
# verified).
PRESERVE_ALWAYS = (
    "confidence IN ('curated', 'metadata', 'llm_high') OR verified = TRUE"
)

_CONSERVATIVE_TARGETS: list[tuple[str, str]] = [
    # (rel_type, extra condition)
    ("CO_OCCURS_WITH", "TRUE"),                      # all, regardless of confidence
    ("ASSOCIATED_WITH", "confidence = 'llm_low'"),
    ("RELATED_TO",      "confidence = 'llm_low'"),
]

_AGGRESSIVE_EXTRA: list[tuple[str, str]] = [
    ("BELONGS_TO",    "confidence = 'llm_low'"),
    ("LIVED_DURING",  "confidence = 'llm_low'"),
    ("EXISTS_DURING", "confidence = 'llm_low'"),
    ("REFERENCED_IN", "confidence = 'llm_low'"),
    ("TEACHES",       "confidence = 'llm_low'"),
]


def _build_delete_where(aggressive: bool) -> tuple[str, list]:
    """Return SQL WHERE snippet + params for the rel_type/confidence matrix."""
    targets = list(_CONSERVATIVE_TARGETS)
    if aggressive:
        targets.extend(_AGGRESSIVE_EXTRA)
    # Compose: (rel_type = X AND cond) OR (rel_type = Y AND cond) ...
    clauses = []
    params: list = []
    for rel_type, cond in targets:
        clauses.append(f"(rel_type = %s AND {cond})")
        params.append(rel_type)
    joined = " OR ".join(clauses)
    # Exclude always-preserved even if they matched above (defense in depth).
    where = f"({joined}) AND NOT ({PRESERVE_ALWAYS})"
    return where, params


@dataclass
class R7Report:
    dry_run: bool = True
    aggressive: bool = False
    relations_before: int = 0
    relations_after: int = 0
    deletions_by_type: dict[str, int] = field(default_factory=dict)
    duration_seconds: float = 0.0
    db_size_before: str = ""
    db_size_after: str = ""

    @property
    def deleted(self) -> int:
        return self.relations_before - self.relations_after

    def summary(self) -> str:
        lines = ["R7 noise-relation killer summary:"]
        lines.append(f"  mode       {'DRY-RUN' if self.dry_run else 'APPLY'}  "
                     f"({'aggressive' if self.aggressive else 'conservative'})")
        lines.append(f"  relations  {self.relations_before:>12,}  →  {self.relations_after:>12,}  "
                     f"({-self.deleted:+,})")
        if self.db_size_before:
            lines.append(f"  db size    {self.db_size_before:>12s}  →  {self.db_size_after:>12s}")
        lines.append("  would delete by rel_type:" if self.dry_run else "  deleted by rel_type:")
        for rel_type, n in sorted(self.deletions_by_type.items(), key=lambda kv: -kv[1]):
            lines.append(f"    {rel_type:22s} {n:>12,}")
        lines.append(f"  duration   {self.duration_seconds:>8.1f}s")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _count(conn: psycopg.Connection, sql: str, params=None) -> int:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()[0]


def _db_size(conn: psycopg.Connection) -> str:
    with conn.cursor() as cur:
        cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
        return cur.fetchone()[0]


# --------------------------------------------------------------------------- #
# Main runner
# --------------------------------------------------------------------------- #

def run_r7(
    conn: psycopg.Connection | None = None,
    dry_run: bool = True,
    aggressive: bool = False,
    vacuum: bool = False,
) -> R7Report:
    report = R7Report(dry_run=dry_run, aggressive=aggressive)
    t0 = time.perf_counter()
    close_after = conn is None
    if conn is None:
        cm = get_connection()
        conn = cm.__enter__()
    try:
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = 0")

        where, params = _build_delete_where(aggressive)
        logger.info("Tier: %s", "aggressive" if aggressive else "conservative")
        logger.debug("WHERE clause: %s", where)

        report.relations_before = _count(conn, "SELECT count(*) FROM relations")
        report.db_size_before = _db_size(conn)

        # --- Preview per rel_type (SELECT only — works in dry-run too) ---
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT rel_type, count(*) FROM relations WHERE {where} GROUP BY rel_type",
                params,
            )
            report.deletions_by_type = {row[0]: row[1] for row in cur.fetchall()}
        total_would_delete = sum(report.deletions_by_type.values())
        logger.info("Target rows: %d across %d rel_types",
                    total_would_delete, len(report.deletions_by_type))

        if not dry_run:
            # --- Do the delete in batches of 2M to keep WAL bounded ---
            # We can't batch by id alone because DELETE ... LIMIT is not supported
            # in a single statement; use ctid tie-break. Simpler: rely on
            # statement_timeout=0 and do the full DELETE once per rel_type.
            logger.info("Deleting rows per rel_type …")
            total_deleted = 0
            for rel_type in list(report.deletions_by_type.keys()):
                # Build a narrower predicate per rel_type for smaller WAL chunks.
                per_type_where, per_type_params = _build_per_type_where(rel_type, aggressive)
                t_start = time.perf_counter()
                with conn.cursor() as cur:
                    cur.execute(
                        f"DELETE FROM relations WHERE {per_type_where}",
                        per_type_params,
                    )
                    deleted = cur.rowcount or 0
                conn.commit()
                total_deleted += deleted
                logger.info("  %-22s  deleted=%d  (%.1fs)",
                            rel_type, deleted, time.perf_counter() - t_start)
            logger.info("Total deleted: %d", total_deleted)

        if not dry_run and vacuum:
            logger.info("VACUUM FULL ANALYZE relations … (this can take minutes)")
            # VACUUM FULL cannot run in a transaction.
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("VACUUM FULL ANALYZE relations")
            conn.autocommit = False

        report.relations_after = _count(conn, "SELECT count(*) FROM relations")
        report.db_size_after = _db_size(conn)

    finally:
        if close_after:
            conn.close()

    report.duration_seconds = time.perf_counter() - t0
    return report


def _build_per_type_where(rel_type: str, aggressive: bool) -> tuple[str, list]:
    """Per-type WHERE clause for chunked DELETE."""
    # Find the specific condition for this rel_type.
    targets = _CONSERVATIVE_TARGETS + (_AGGRESSIVE_EXTRA if aggressive else [])
    for rt, cond in targets:
        if rt == rel_type:
            # Always respect global preserve filter.
            return f"rel_type = %s AND ({cond}) AND NOT ({PRESERVE_ALWAYS})", [rel_type]
    raise ValueError(f"rel_type {rel_type!r} not in targets for tier")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="R7 — kill low-value noise relations.")
    mx = parser.add_mutually_exclusive_group(required=True)
    mx.add_argument("--dry-run", action="store_true")
    mx.add_argument("--apply", action="store_true")
    parser.add_argument("--aggressive", action="store_true",
                        help="Also delete llm_low BELONGS_TO/LIVED_DURING/EXISTS_DURING/"
                             "REFERENCED_IN/TEACHES. Default is conservative.")
    parser.add_argument("--vacuum", action="store_true",
                        help="Run VACUUM FULL ANALYZE relations after deleting. "
                             "Required to reclaim disk space. Locks table briefly.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    report = run_r7(
        dry_run=args.dry_run,
        aggressive=args.aggressive,
        vacuum=args.vacuum,
    )
    print(report.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
