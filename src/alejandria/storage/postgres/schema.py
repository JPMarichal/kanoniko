"""Idempotent schema application for Postgres.

Design:
    * ``ddl.sql`` holds the canonical DDL (mirrors docs/postgres-migration.md §2.2).
    * ``SCHEMA_VERSION`` is bumped whenever ``ddl.sql`` changes.
    * ``apply_schema()`` runs the DDL (all CREATEs are ``IF NOT EXISTS``), then
      stamps the ``schema_version`` table.
    * ``ensure_hnsw_index()`` is kept separate: HNSW is expensive to build and
      should be created *after* bulk load during migration, not at schema apply.

Why not Alembic yet? The migration is still pre-production and the schema is
under active design. A single idempotent apply keeps iteration fast. Alembic
is added in Phase 3 when the schema stabilizes and real migrations accumulate.
"""
from __future__ import annotations

import logging
from pathlib import Path

import psycopg

from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)

# Bump this whenever ddl.sql is modified in a way that requires re-apply.
# v1 — initial schema (migration Fase 2).
# v2 — entity_document_mentions added (kg-client-port-audit §6.1 decision A,
#      2026-04-18). Unlocks get_documents_for_entity* and related methods.
# v3 — entities UNIQUE(name, entity_type, disambiguator) switched to NULLS
#      NOT DISTINCT so ON CONFLICT works when disambiguator IS NULL
#      (Approach B step 3, 2026-04-19). See docs/postgres-migration-status.md.
#      Migration script: scripts/migrate_pg_schema_v3.py.
SCHEMA_VERSION = 3

_DDL_PATH = Path(__file__).with_name("ddl.sql")


def _read_ddl() -> str:
    return _DDL_PATH.read_text(encoding="utf-8")


def current_version(conn: psycopg.Connection | None = None) -> int | None:
    """Return the highest applied schema version, or None if table missing."""
    close_after = conn is None
    if conn is None:
        cm = get_connection()
        conn = cm.__enter__()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT EXISTS ("
                "  SELECT 1 FROM information_schema.tables "
                "  WHERE table_schema='public' AND table_name='schema_version'"
                ")"
            )
            exists = cur.fetchone()[0]
            if not exists:
                return None
            cur.execute("SELECT MAX(version) FROM schema_version")
            row = cur.fetchone()
            return row[0] if row and row[0] is not None else None
    finally:
        if close_after:
            conn.close()


def apply_schema(conn: psycopg.Connection | None = None, notes: str | None = None) -> int:
    """Apply ``ddl.sql`` and stamp ``schema_version``.

    Returns the version just stamped. Safe to re-run: CREATEs are IF NOT EXISTS
    and the version stamp uses ON CONFLICT DO NOTHING.
    """
    ddl = _read_ddl()
    close_after = conn is None
    if conn is None:
        cm = get_connection()
        conn = cm.__enter__()
    try:
        with conn.cursor() as cur:
            cur.execute(ddl)
            cur.execute(
                "INSERT INTO schema_version (version, notes) VALUES (%s, %s) "
                "ON CONFLICT (version) DO NOTHING",
                (SCHEMA_VERSION, notes),
            )
        conn.commit()
        logger.info("Schema applied; version=%s", SCHEMA_VERSION)
        return SCHEMA_VERSION
    finally:
        if close_after:
            conn.close()


def ensure_hnsw_index(
    conn: psycopg.Connection | None = None,
    m: int = 16,
    ef_construction: int = 64,
) -> None:
    """Create the HNSW cosine index on ``chunk_embeddings.embedding`` if missing.

    Call this AFTER the bulk migration writes embeddings — HNSW build cost
    scales roughly linearly with row count and is wasted if rebuilt per insert.

    Requires ``shm_size >= 1 GB`` (see docs/postgres-migration.md §3, Fase 0).
    """
    close_after = conn is None
    if conn is None:
        cm = get_connection()
        conn = cm.__enter__()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_indexes "
                "WHERE schemaname='public' AND indexname='chunk_embeddings_hnsw'"
            )
            if cur.fetchone():
                logger.info("HNSW index already present")
                return
            cur.execute(
                f"CREATE INDEX chunk_embeddings_hnsw ON chunk_embeddings "
                f"USING hnsw (embedding vector_cosine_ops) "
                f"WITH (m = {m}, ef_construction = {ef_construction})"
            )
        conn.commit()
        logger.info("HNSW index created (m=%s, ef_construction=%s)", m, ef_construction)
    finally:
        if close_after:
            conn.close()
