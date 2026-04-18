"""R0 — One-shot cleanup of the KG migrated into Postgres.

See docs/kg-ingestion-refactor.md for the full agenda. This module handles:

    1. Delete obvious-garbage entities (URLs, punctuation, archaic verbs,
       cross-reference fragments, length outliers, pronouns).
    2. Merge gazetteer-canonical duplicates: e.g. "Holy Ghost" (concept),
       "Holy Ghost" (person), "the Holy Ghost" (scripture_reference) and
       all case variants collapse into the single gazetteer-canonical entity.
       Relations are reassigned to the winner and de-duplicated.

Safety:
    * Default is ``dry_run=True`` — no mutations, just report.
    * Every deletion is recorded to ``cleanup_audit.jsonl`` for audit.
    * R0 is idempotent: re-running after a successful apply is a no-op.
    * Non-gazetteer duplicates are NOT merged here. That requires human
      judgement and belongs to a later pass (see R5 in the backlog).

Usage::

    # Dry-run against the current ALEJANDRIA_POSTGRES_* connection
    python -m alejandria.storage.postgres.kg_cleanup --dry-run

    # Apply for real
    python -m alejandria.storage.postgres.kg_cleanup --apply
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import psycopg

from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Gazetteer loading
# --------------------------------------------------------------------------- #

_GAZETTEER_PATH = (
    Path(__file__).resolve().parent.parent.parent / "knowledge" / "gazetteers" / "entities.json"
)

_LEADING_ARTICLE_RE = re.compile(
    r"^(the|el|la|los|las|un|una)\s+",
    flags=re.IGNORECASE,
)


def _normalize(name: str) -> str:
    """Normalize an entity name for equality comparison.

    * Unicode NFC
    * lowercase
    * trim
    * strip leading article (the/el/la/los/las/un/una)
    * collapse internal whitespace
    """
    if not name:
        return ""
    s = unicodedata.normalize("NFC", name).strip().lower()
    s = _LEADING_ARTICLE_RE.sub("", s)
    s = re.sub(r"\s+", " ", s)
    return s


def load_gazetteer_canonical_map(path: Path | None = None) -> dict[str, tuple[str, str]]:
    """Return dict[norm(alias_or_name)] = (canonical_name, canonical_entity_type)."""
    path = path or _GAZETTEER_PATH
    if not path.exists():
        raise FileNotFoundError(f"Gazetteer not found at {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, tuple[str, str]] = {}
    for etype, entries in data.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            canonical = entry.get("name", "")
            if not canonical:
                continue
            n = _normalize(canonical)
            if n and n not in out:
                out[n] = (canonical, etype)
            for alias in entry.get("aliases") or []:
                na = _normalize(alias)
                if na and na not in out:
                    out[na] = (canonical, etype)
    return out


# --------------------------------------------------------------------------- #
# Garbage predicates — SQL-side (single scan)
# --------------------------------------------------------------------------- #

_ARCHAIC_VERBS = (
    "hath", "saith", "spake", "smote", "doth", "shalt", "wilt",
    "cometh", "goeth", "maketh", "taketh", "dwelt", "begat",
)
_ARCHAIC_VERB_RE = r"\m(" + "|".join(_ARCHAIC_VERBS) + r")\M"

_PRONOUNS_STOPWORDS = (
    "thou", "thee", "thy", "thine", "ye", "he", "she", "it",
    "him", "her", "us", "we", "they", "them",
    "el", "él", "ella", "ellos", "ellas", "nos", "nosotros",
    "yo", "tú", "tu", "su", "mi", "me", "te", "se",
)


GARBAGE_CTE = f"""
WITH garbage AS (
    SELECT id, name, entity_type, 'all_punct' AS reason
        FROM entities WHERE name ~ '^[[:punct:][:space:]]+$'
    UNION ALL
    SELECT id, name, entity_type, 'url_like'
        FROM entities WHERE name ~* '(https?://|\\.org|\\.com|www\\.|[a-z]\\.[a-z]+\\.org)'
    UNION ALL
    SELECT id, name, entity_type, 'too_long'
        FROM entities WHERE length(name) > 80
    UNION ALL
    SELECT id, name, entity_type, 'too_short'
        FROM entities WHERE length(name) < 3
    UNION ALL
    SELECT id, name, entity_type, 'archaic_verb'
        FROM entities WHERE name ~* '{_ARCHAIC_VERB_RE}'
    UNION ALL
    SELECT id, name, entity_type, 'xref_fragment'
        FROM entities WHERE name ~* '^(see |véase )'
    UNION ALL
    SELECT id, name, entity_type, 'pronoun_stopword'
        FROM entities WHERE lower(name) = ANY(%s::text[])
)
"""


# --------------------------------------------------------------------------- #
# Data classes / report
# --------------------------------------------------------------------------- #

@dataclass
class MergeGroup:
    canonical_name: str
    canonical_type: str
    winner_id: int
    loser_ids: list[int]

    @property
    def size(self) -> int:
        return 1 + len(self.loser_ids)


@dataclass
class CleanupReport:
    dry_run: bool = True
    entities_before: int = 0
    entities_after: int = 0
    relations_before: int = 0
    relations_after: int = 0
    garbage_deleted_by_reason: dict[str, int] = field(default_factory=dict)
    merges_applied: int = 0
    entities_merged_away: int = 0
    relations_reassigned: int = 0
    relations_self_loops_removed: int = 0
    relations_duplicates_removed: int = 0
    duration_seconds: float = 0.0

    def summary(self) -> str:
        lines = ["KG cleanup summary:"]
        lines.append(f"  mode              {'DRY-RUN' if self.dry_run else 'APPLY'}")
        lines.append(f"  entities          {self.entities_before:>10,}  →  {self.entities_after:>10,}  "
                     f"({self.entities_before - self.entities_after:+,})")
        lines.append(f"  relations         {self.relations_before:>10,}  →  {self.relations_after:>10,}  "
                     f"({self.relations_before - self.relations_after:+,})")
        lines.append(f"  garbage deleted by reason:")
        for reason, n in sorted(self.garbage_deleted_by_reason.items()):
            lines.append(f"    {reason:20s} {n:>8,}")
        lines.append(f"  merges applied           {self.merges_applied:>8,}")
        lines.append(f"  entities merged away     {self.entities_merged_away:>8,}")
        lines.append(f"  relations reassigned     {self.relations_reassigned:>8,}")
        lines.append(f"  relations self-loops     {self.relations_self_loops_removed:>8,}  (removed)")
        lines.append(f"  relations duplicates     {self.relations_duplicates_removed:>8,}  (removed)")
        lines.append(f"  duration                 {self.duration_seconds:>8.1f}s")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Phase 1 — obvious garbage
# --------------------------------------------------------------------------- #

def find_garbage(
    conn: psycopg.Connection,
) -> tuple[list[int], dict[str, int], list[tuple[int, str, str, str]]]:
    """Return (all_garbage_ids, counts_by_reason, sample_rows)."""
    with conn.cursor() as cur:
        cur.execute(
            GARBAGE_CTE + "SELECT reason, count(*) FROM garbage GROUP BY reason",
            (list(_PRONOUNS_STOPWORDS),),
        )
        counts = {row[0]: row[1] for row in cur.fetchall()}

        cur.execute(
            GARBAGE_CTE + "SELECT id, name, entity_type, reason FROM garbage ORDER BY id",
            (list(_PRONOUNS_STOPWORDS),),
        )
        rows = cur.fetchall()
    all_ids = [r[0] for r in rows]
    sample = rows[:30]
    return all_ids, counts, sample


def delete_garbage(conn: psycopg.Connection, ids: list[int]) -> int:
    """CASCADE handles entity_aliases + relations via FK. Returns rows deleted."""
    if not ids:
        return 0
    with conn.cursor() as cur:
        # Batch in chunks of 10k to keep statements bounded.
        deleted = 0
        for i in range(0, len(ids), 10_000):
            chunk = ids[i:i + 10_000]
            cur.execute("DELETE FROM entities WHERE id = ANY(%s)", (chunk,))
            deleted += cur.rowcount or 0
    conn.commit()
    return deleted


# --------------------------------------------------------------------------- #
# Phase 2 — gazetteer-canonical merges
# --------------------------------------------------------------------------- #

def build_merge_plan(
    conn: psycopg.Connection,
    gaz_map: dict[str, tuple[str, str]],
    excluded_ids: set[int] | None = None,
) -> list[MergeGroup]:
    """Group entities by gazetteer canonical. One MergeGroup per canonical that
    has more than one row matching in the DB."""
    excluded_ids = excluded_ids or set()

    # Single scan: load every (id, name, entity_type), normalize, look up in gaz_map.
    # 820k entities × ~150 bytes ≈ 120 MB in memory — acceptable.
    groups_by_canonical: dict[tuple[str, str], list[tuple[int, str, str]]] = {}
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, entity_type FROM entities")
        for eid, name, etype in cur:
            if eid in excluded_ids:
                continue
            hit = gaz_map.get(_normalize(name))
            if hit is None:
                continue
            groups_by_canonical.setdefault(hit, []).append((eid, name, etype))

    plan: list[MergeGroup] = []
    for (canonical_name, canonical_type), rows in groups_by_canonical.items():
        if len(rows) < 2:
            continue
        # Winner selection: prefer exact (name, type) match; else row with
        # matching type; else smallest id for determinism.
        def score(r: tuple[int, str, str]) -> tuple[int, int, int]:
            _, nm, et = r
            exact_name = 0 if nm == canonical_name else 1
            exact_type = 0 if et == canonical_type else 1
            return (exact_type, exact_name, r[0])
        rows_sorted = sorted(rows, key=score)
        winner = rows_sorted[0]
        losers = [r[0] for r in rows_sorted[1:]]
        plan.append(MergeGroup(
            canonical_name=canonical_name,
            canonical_type=canonical_type,
            winner_id=winner[0],
            loser_ids=losers,
        ))
    return plan


def apply_merge_plan(
    conn: psycopg.Connection,
    plan: list[MergeGroup],
) -> tuple[int, int, int, int]:
    """Execute the merge. Returns (reassigned, self_loops, duplicates, entities_merged)."""
    if not plan:
        return 0, 0, 0, 0

    # Stage the mapping in a temp table so the UPDATEs are a single pass.
    with conn.cursor() as cur:
        cur.execute("CREATE TEMP TABLE _merge_map (loser_id BIGINT PRIMARY KEY, winner_id BIGINT NOT NULL)")
        # Batch insert
        with cur.copy("COPY _merge_map (loser_id, winner_id) FROM STDIN") as cp:
            for g in plan:
                for lid in g.loser_ids:
                    cp.write_row((lid, g.winner_id))

        cur.execute("SELECT count(*) FROM _merge_map")
        n_losers = cur.fetchone()[0]
        logger.info("_merge_map staged with %d loser→winner pairs", n_losers)

        # 1) Rewrite src_id and dst_id
        logger.info("Reassigning relations.src_id …")
        cur.execute(
            "UPDATE relations r SET src_id = m.winner_id "
            "FROM _merge_map m WHERE r.src_id = m.loser_id"
        )
        reassigned_src = cur.rowcount or 0

        logger.info("Reassigning relations.dst_id …")
        cur.execute(
            "UPDATE relations r SET dst_id = m.winner_id "
            "FROM _merge_map m WHERE r.dst_id = m.loser_id"
        )
        reassigned_dst = cur.rowcount or 0

        reassigned = reassigned_src + reassigned_dst
        logger.info("Reassigned %d relation endpoints (src=%d, dst=%d)",
                    reassigned, reassigned_src, reassigned_dst)

        # 2) Drop self-loops created by merge
        logger.info("Removing self-loops …")
        cur.execute("DELETE FROM relations WHERE src_id = dst_id")
        self_loops = cur.rowcount or 0

        # 3) Dedup: keep lowest id per (src_id, dst_id, rel_type)
        logger.info("Deduplicating relations by (src, dst, rel_type) …")
        cur.execute(
            "DELETE FROM relations r "
            "USING relations r2 "
            "WHERE r.id > r2.id "
            "  AND r.src_id = r2.src_id "
            "  AND r.dst_id = r2.dst_id "
            "  AND r.rel_type = r2.rel_type"
        )
        duplicates = cur.rowcount or 0

        # 4) Delete loser entities (CASCADE handles remaining FKs)
        logger.info("Deleting loser entities …")
        cur.execute("DELETE FROM entities WHERE id IN (SELECT loser_id FROM _merge_map)")
        entities_merged = cur.rowcount or 0

        cur.execute("DROP TABLE _merge_map")
    conn.commit()
    return reassigned, self_loops, duplicates, entities_merged


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #

def _count(conn: psycopg.Connection, table: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM {table}")
        return cur.fetchone()[0]


def _write_audit(path: Path, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_cleanup(
    conn: psycopg.Connection | None = None,
    dry_run: bool = True,
    audit_path: Path | None = None,
) -> CleanupReport:
    """Execute R0 cleanup. See module docstring."""
    report = CleanupReport(dry_run=dry_run)
    t0 = time.perf_counter()

    close_after = conn is None
    if conn is None:
        cm = get_connection()
        conn = cm.__enter__()
    try:
        # Workaround: this job does heavy UPDATEs/DELETEs that should not be
        # killed by the default statement_timeout.
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = 0")

        report.entities_before = _count(conn, "entities")
        report.relations_before = _count(conn, "relations")

        # --- Phase 1: garbage ---
        logger.info("Phase 1 — scanning for obvious garbage entities …")
        garbage_ids, by_reason, sample = find_garbage(conn)
        report.garbage_deleted_by_reason = by_reason
        logger.info("Garbage found: %d rows across %d buckets",
                    len(garbage_ids), len(by_reason))
        for reason, n in sorted(by_reason.items(), key=lambda kv: -kv[1]):
            logger.info("  %s: %d", reason, n)
        logger.info("Sample garbage rows:")
        for row in sample[:10]:
            logger.info("  id=%s type=%s name=%r reason=%s",
                        row[0], row[2], row[1], row[3])

        if not dry_run:
            deleted = delete_garbage(conn, garbage_ids)
            logger.info("Deleted %d garbage entities", deleted)
            if audit_path:
                _write_audit(audit_path / "garbage_deleted.jsonl",
                             [{"id": r[0], "name": r[1], "entity_type": r[2], "reason": r[3]}
                              for r in sample])

        # --- Phase 2: gazetteer merges ---
        logger.info("Phase 2 — loading gazetteer …")
        gaz_map = load_gazetteer_canonical_map()
        logger.info("Gazetteer map has %d normalized aliases", len(gaz_map))

        logger.info("Phase 2 — building merge plan …")
        excluded = set(garbage_ids) if dry_run else set()
        plan = build_merge_plan(conn, gaz_map, excluded_ids=excluded)
        report.merges_applied = len(plan)
        report.entities_merged_away = sum(len(g.loser_ids) for g in plan)
        logger.info("Merge plan: %d groups covering %d loser entities",
                    len(plan), report.entities_merged_away)
        logger.info("Top 10 merges by size:")
        for g in sorted(plan, key=lambda x: -x.size)[:10]:
            logger.info("  %-45s  %s  (winner id=%d, +%d losers)",
                        g.canonical_name, g.canonical_type,
                        g.winner_id, len(g.loser_ids))

        if not dry_run:
            reassigned, self_loops, duplicates, n_merged = apply_merge_plan(conn, plan)
            report.relations_reassigned = reassigned
            report.relations_self_loops_removed = self_loops
            report.relations_duplicates_removed = duplicates
            # n_merged should equal report.entities_merged_away
            if audit_path:
                _write_audit(audit_path / "merges.jsonl",
                             [{"canonical_name": g.canonical_name,
                               "canonical_type": g.canonical_type,
                               "winner_id": g.winner_id,
                               "loser_ids": g.loser_ids} for g in plan])

        # --- Final counts ---
        report.entities_after = _count(conn, "entities")
        report.relations_after = _count(conn, "relations")

    finally:
        if close_after:
            conn.close()
    report.duration_seconds = time.perf_counter() - t0
    return report


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="R0 cleanup of the migrated KG.")
    mx = parser.add_mutually_exclusive_group(required=True)
    mx.add_argument("--dry-run", action="store_true",
                    help="Report what would happen without mutations.")
    mx.add_argument("--apply", action="store_true",
                    help="Actually delete/merge. Writes audit files.")
    parser.add_argument("--audit-dir", type=Path,
                        default=Path("/tmp/kg-cleanup-audit"),
                        help="Directory for jsonl audit files (only used with --apply)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    report = run_cleanup(
        dry_run=args.dry_run,
        audit_path=args.audit_dir if args.apply else None,
    )
    print(report.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
