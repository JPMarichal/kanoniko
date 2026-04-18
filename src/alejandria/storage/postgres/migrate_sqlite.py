"""Migrate the live SQLite DB (FTS5 + sqlite-vec) to the Postgres backend.

Tables migrated:
    * document_registry
    * chunks                     (language column derived from metadata.lang)
    * chunk_embeddings           (via sqlite-vec vec0 virtual table)
    * entity_profiles
    * ner_candidates

The Neo4j-backed KG (entities + relations) is handled separately by
``migrate_neo4j.py``.

Design:
    * All writes use ``COPY FROM STDIN`` for maximum throughput.
    * chunks.id is preserved (explicit column in COPY) so that chunk_embeddings
      FKs stay valid; the ``chunks_id_seq`` is reset at the end.
    * Orphan vectors (present in chunk_vectors but missing from chunks) are
      silently skipped — they are residue of deleted chunks.
    * ``--reset`` TRUNCATEs the five target tables before loading; otherwise
      the migrator aborts if any target table already contains rows.

Run as a module::

    python -m alejandria.storage.postgres.migrate_sqlite \
        --sqlite /app/data/sqlite/alejandria.db --reset
"""
from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import struct
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import psycopg

from alejandria.storage.postgres.connection import get_connection
from alejandria.storage.postgres.schema import apply_schema

logger = logging.getLogger(__name__)


TARGET_TABLES_IN_FK_ORDER = (
    "document_registry",
    "chunks",
    "chunk_embeddings",
    "entity_profiles",
    "ner_candidates",
)


@dataclass
class MigrationReport:
    rows: dict[str, int] = field(default_factory=dict)
    seconds: dict[str, float] = field(default_factory=dict)
    skipped_orphan_vectors: int = 0

    def record(self, table: str, rows: int, seconds: float) -> None:
        self.rows[table] = rows
        self.seconds[table] = seconds

    def summary(self) -> str:
        lines = ["Migration summary:"]
        for t in TARGET_TABLES_IN_FK_ORDER:
            if t in self.rows:
                r = self.rows[t]
                s = self.seconds[t]
                rps = r / s if s > 0 else 0
                lines.append(f"  {t:25s}  {r:>10,} rows  {s:7.1f}s  ({rps:>8,.0f} rows/s)")
        if self.skipped_orphan_vectors:
            lines.append(f"  (skipped {self.skipped_orphan_vectors:,} orphan vectors)")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# SQLite helpers
# --------------------------------------------------------------------------- #

@contextmanager
def open_sqlite(path: Path) -> Iterator[sqlite3.Connection]:
    """Open the live SQLite DB with sqlite-vec loaded (needed to read vectors)."""
    import sqlite_vec  # lazy — only needed for the embeddings table

    conn = sqlite3.connect(str(path), timeout=30)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _strip_nuls(s: str | None) -> str | None:
    """Postgres TEXT cannot hold NUL (0x00) bytes. Some corpus files (PDF
    extraction residue) leak them in; drop them before COPY."""
    if s is None:
        return None
    if "\x00" not in s:
        return s
    return s.replace("\x00", "")


def _derive_language(metadata_json: str, file_path: str) -> str:
    """Return 'es' or 'en' using metadata.lang first, file_path prefix second."""
    try:
        meta = json.loads(metadata_json) if metadata_json else {}
        lang = meta.get("lang")
        if lang in ("es", "en"):
            return lang
    except Exception:
        pass
    if file_path.startswith("en/"):
        return "en"
    return "es"


def _unpack_f32_blob(blob: bytes) -> list[float]:
    """Decode a sqlite-vec float[N] embedding stored as packed float32."""
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


def _vector_to_pg_text(vec: list[float]) -> str:
    """pgvector text format: '[v1,v2,...,vN]'."""
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"


# --------------------------------------------------------------------------- #
# Reset / precondition
# --------------------------------------------------------------------------- #

def _reset_or_verify(pg: psycopg.Connection, reset: bool) -> None:
    with pg.cursor() as cur:
        if reset:
            cur.execute(
                "TRUNCATE " + ", ".join(TARGET_TABLES_IN_FK_ORDER) + " RESTART IDENTITY CASCADE"
            )
            logger.info("Target tables truncated (reset=True)")
            pg.commit()
            return
        for t in TARGET_TABLES_IN_FK_ORDER:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            n = cur.fetchone()[0]
            if n > 0:
                raise RuntimeError(
                    f"Target table {t!r} has {n} rows; re-run with --reset to truncate."
                )


# --------------------------------------------------------------------------- #
# Per-table migrators
# --------------------------------------------------------------------------- #

def migrate_document_registry(sl: sqlite3.Connection, pg: psycopg.Connection) -> tuple[int, float]:
    t0 = time.perf_counter()
    cur = sl.execute(
        "SELECT file_path, sha256, file_size, chunk_count, last_indexed, status "
        "FROM document_registry"
    )
    count = 0
    with pg.cursor().copy(
        "COPY document_registry (file_path, sha256, file_size, chunk_count, last_indexed, status) "
        "FROM STDIN"
    ) as cp:
        for row in cur:
            cp.write_row((
                row["file_path"],
                row["sha256"],
                row["file_size"],
                row["chunk_count"],
                row["last_indexed"],           # ISO-8601 parses natively to TIMESTAMPTZ
                row["status"],
            ))
            count += 1
    pg.commit()
    return count, time.perf_counter() - t0


def migrate_chunks(sl: sqlite3.Connection, pg: psycopg.Connection) -> tuple[int, float]:
    t0 = time.perf_counter()
    cur = sl.execute(
        "SELECT id, file_path, chunk_index, text, reference, start_char, end_char, metadata "
        "FROM chunks"
    )
    count = 0
    with pg.cursor().copy(
        "COPY chunks (id, file_path, chunk_index, text, reference, start_char, end_char, "
        "metadata, language) FROM STDIN"
    ) as cp:
        for row in cur:
            lang = _derive_language(row["metadata"], row["file_path"])
            cp.write_row((
                row["id"],
                row["file_path"],
                row["chunk_index"],
                _strip_nuls(row["text"]),
                _strip_nuls(row["reference"]),
                row["start_char"],
                row["end_char"],
                _strip_nuls(row["metadata"]) or "{}",  # JSONB accepts TEXT via implicit cast
                lang,
            ))
            count += 1
    # keep the sequence in sync with the manual id inserts
    with pg.cursor() as c:
        c.execute("SELECT setval('chunks_id_seq', COALESCE((SELECT MAX(id) FROM chunks), 1), true)")
    pg.commit()
    return count, time.perf_counter() - t0


def migrate_chunk_embeddings(sl: sqlite3.Connection, pg: psycopg.Connection) -> tuple[int, float, int]:
    """Migrate vectors, skipping orphans (ids not present in chunks).

    Returns (migrated_count, elapsed_seconds, skipped_orphans).
    """
    t0 = time.perf_counter()
    # Load valid chunk ids into a set for fast membership check. 300k ints is
    # cheap (~10 MB in Python), and the alternative — checking per-row via SQL —
    # defeats the purpose of COPY streaming.
    valid_ids: set[int] = {row[0] for row in sl.execute("SELECT id FROM chunks")}
    logger.info("Loaded %d valid chunk ids", len(valid_ids))

    cur = sl.execute("SELECT id, embedding FROM chunk_vectors")
    count = 0
    skipped = 0
    with pg.cursor().copy(
        "COPY chunk_embeddings (chunk_id, embedding) FROM STDIN"
    ) as cp:
        for row in cur:
            vid = row["id"]
            if vid not in valid_ids:
                skipped += 1
                continue
            vec = _unpack_f32_blob(row["embedding"])
            cp.write_row((vid, _vector_to_pg_text(vec)))
            count += 1
            if count % 25_000 == 0:
                logger.info("  … %d embeddings migrated", count)
    pg.commit()
    return count, time.perf_counter() - t0, skipped


def migrate_entity_profiles(sl: sqlite3.Connection, pg: psycopg.Connection) -> tuple[int, float]:
    """Migrate SQLite entity_profiles. Note: current Postgres schema keys profiles
    by ``entity_id`` (FK to entities). Since entities are migrated from Neo4j
    separately, this function stages profiles into a temp table keyed by
    (entity_name, entity_type) which the Neo4j migrator will resolve to ids.
    For now, with 0 profiles in SQLite, this is effectively a no-op stub."""
    t0 = time.perf_counter()
    count = sl.execute("SELECT COUNT(*) FROM entity_profiles").fetchone()[0]
    if count == 0:
        logger.info("entity_profiles empty — nothing to stage")
        return 0, time.perf_counter() - t0

    # Stage to a temp table; migrate_neo4j will JOIN on entity name/type to
    # populate the real entity_profiles after entities exist.
    with pg.cursor() as cur:
        cur.execute(
            "CREATE TEMPORARY TABLE IF NOT EXISTS _staging_profiles ("
            "  entity_name TEXT, entity_type TEXT, mention_count INT, document_count INT, "
            "  books JSONB, key_passages JSONB, aliases JSONB, disambiguator TEXT, "
            "  summary_en TEXT, summary_es TEXT, disambiguation_notes TEXT, "
            "  disambiguated_counts JSONB, profile_version INT, status TEXT"
            ") ON COMMIT PRESERVE ROWS"
        )
    cur = sl.execute(
        "SELECT entity_name, entity_type, mention_count, document_count, books, key_passages, "
        "aliases, disambiguator, summary_en, summary_es, disambiguation_notes, "
        "disambiguated_counts, profile_version, status FROM entity_profiles"
    )
    n = 0
    with pg.cursor().copy("COPY _staging_profiles FROM STDIN") as cp:
        for row in cur:
            cp.write_row(tuple(row))
            n += 1
    pg.commit()
    return n, time.perf_counter() - t0


def migrate_ner_candidates(sl: sqlite3.Connection, pg: psycopg.Connection) -> tuple[int, float]:
    t0 = time.perf_counter()
    cur = sl.execute(
        "SELECT name, type, frequency, sample_files, status, created_at, updated_at "
        "FROM ner_candidates"
    )
    n = 0
    with pg.cursor().copy(
        "COPY ner_candidates (name, entity_type, frequency, sample_files, status, "
        "first_seen, last_seen) FROM STDIN"
    ) as cp:
        for row in cur:
            cp.write_row((
                row["name"],
                row["type"],                 # SQLite col 'type' → Postgres 'entity_type'
                row["frequency"],
                row["sample_files"] or "[]",
                row["status"],
                row["created_at"],
                row["updated_at"],
            ))
            n += 1
    pg.commit()
    return n, time.perf_counter() - t0


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #

def migrate_all(
    sqlite_path: Path,
    pg_conn: psycopg.Connection | None = None,
    reset: bool = False,
    apply_ddl: bool = True,
) -> MigrationReport:
    """Run the full SQLite→Postgres migration in FK-safe order.

    If ``pg_conn`` is None, a new connection is opened from settings and closed
    on exit. If provided, the caller owns the connection lifecycle.
    """
    report = MigrationReport()
    close_after = pg_conn is None
    if pg_conn is None:
        cm = get_connection()
        pg_conn = cm.__enter__()
    try:
        if apply_ddl:
            apply_schema(pg_conn, notes="sqlite migration")
        _reset_or_verify(pg_conn, reset)

        with open_sqlite(sqlite_path) as sl:
            n, s = migrate_document_registry(sl, pg_conn)
            report.record("document_registry", n, s)
            logger.info("document_registry: %d rows in %.1fs", n, s)

            n, s = migrate_chunks(sl, pg_conn)
            report.record("chunks", n, s)
            logger.info("chunks: %d rows in %.1fs", n, s)

            n, s, skipped = migrate_chunk_embeddings(sl, pg_conn)
            report.record("chunk_embeddings", n, s)
            report.skipped_orphan_vectors = skipped
            logger.info("chunk_embeddings: %d rows in %.1fs (skipped %d orphans)", n, s, skipped)

            n, s = migrate_entity_profiles(sl, pg_conn)
            report.record("entity_profiles", n, s)
            logger.info("entity_profiles (staged): %d rows in %.1fs", n, s)

            n, s = migrate_ner_candidates(sl, pg_conn)
            report.record("ner_candidates", n, s)
            logger.info("ner_candidates: %d rows in %.1fs", n, s)
    finally:
        if close_after:
            pg_conn.close()
    return report


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Migrate live SQLite DB to Postgres.")
    parser.add_argument(
        "--sqlite", type=Path, required=True,
        help="Path to the live SQLite DB (e.g. /app/data/sqlite/alejandria.db)",
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="TRUNCATE target tables before load (required if any target already has rows).",
    )
    parser.add_argument(
        "--no-schema", action="store_true",
        help="Skip apply_schema() — assume DDL is already applied.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if not args.sqlite.exists():
        print(f"error: SQLite file not found: {args.sqlite}", file=sys.stderr)
        return 2

    report = migrate_all(
        sqlite_path=args.sqlite,
        reset=args.reset,
        apply_ddl=not args.no_schema,
    )
    print(report.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
