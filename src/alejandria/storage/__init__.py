"""Storage backends for Alejandría.

Historical: SQLite (FTS5 + sqlite-vec) and Neo4j coexist as the live stack.
In flight: ``alejandria.storage.postgres`` is the unified Postgres + pgvector
target defined in ``docs/postgres-migration.md`` (feature/postgres-migration).
"""
