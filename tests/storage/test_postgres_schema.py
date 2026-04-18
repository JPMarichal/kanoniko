"""Integration test: apply schema to a live Postgres and verify the surface.

Skipped automatically when Postgres is not reachable. Use it against the
benchmark container (``benchmarks/postgres-migration/docker-compose.yml``):

    ALEJANDRIA_POSTGRES_HOST=localhost \
    ALEJANDRIA_POSTGRES_PORT=5433 \
    ALEJANDRIA_POSTGRES_USER=bench \
    ALEJANDRIA_POSTGRES_PASSWORD=bench \
    ALEJANDRIA_POSTGRES_DB=alejandria_bench \
    ALEJANDRIA_POSTGRES_SSLMODE=disable \
    pytest tests/storage/test_postgres_schema.py -v
"""
from __future__ import annotations

import pytest

psycopg = pytest.importorskip("psycopg")


def _pg_reachable() -> bool:
    from alejandria.storage.postgres.connection import get_connection

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _pg_reachable(),
    reason="Postgres not reachable — set ALEJANDRIA_POSTGRES_* envs against dev DB",
)


EXPECTED_TABLES = {
    "schema_version",
    "document_registry",
    "chunks",
    "chunk_embeddings",
    "entities",
    "entity_aliases",
    "relations",
    "entity_profiles",
    "ner_candidates",
}


def test_apply_schema_is_idempotent() -> None:
    from alejandria.storage.postgres.schema import (
        SCHEMA_VERSION,
        apply_schema,
        current_version,
    )

    v1 = apply_schema(notes="smoke test")
    v2 = apply_schema(notes="smoke test re-run")  # must not error
    assert v1 == v2 == SCHEMA_VERSION
    assert current_version() == SCHEMA_VERSION


def test_all_expected_tables_exist() -> None:
    from alejandria.storage.postgres.connection import get_connection

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public'"
            )
            present = {row[0] for row in cur.fetchall()}
    missing = EXPECTED_TABLES - present
    assert not missing, f"Missing tables: {missing}"


def test_extensions_installed() -> None:
    from alejandria.storage.postgres.connection import get_connection

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT extname FROM pg_extension WHERE extname IN ('vector','pg_trgm','unaccent')"
            )
            exts = {row[0] for row in cur.fetchall()}
    assert exts == {"vector", "pg_trgm", "unaccent"}


def test_immutable_unaccent_usable_in_expression() -> None:
    """Regression for Phase 1 finding: unaccent() cannot be used directly in
    GENERATED STORED columns; the immutable wrapper must exist and work."""
    from alejandria.storage.postgres.connection import get_connection

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT immutable_unaccent('áéíóú')")
            assert cur.fetchone()[0] == "aeiou"
