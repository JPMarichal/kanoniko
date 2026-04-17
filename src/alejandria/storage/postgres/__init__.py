"""Postgres 16 + pgvector backend (migration target).

Public API:
    get_connection()  — open a psycopg3 Connection using ``alejandria.config.settings``
    apply_schema()    — apply the canonical DDL idempotently
    SCHEMA_VERSION    — integer tracked in the ``schema_version`` table

See ``docs/postgres-migration.md`` for design and ``benchmarks/postgres-migration/``
for the Phase 1 validation benchmark.
"""

from alejandria.storage.postgres.connection import get_connection
from alejandria.storage.postgres.schema import SCHEMA_VERSION, apply_schema, current_version

__all__ = ["get_connection", "apply_schema", "current_version", "SCHEMA_VERSION"]
