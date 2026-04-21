"""Storage backends for Alejandría.

Ingestion writes flow through three Protocols defined here (SRP + ISP per
ADR 0001 v2):

* :class:`ChunkWriter` — text (FTS) and vector persistence.
* :class:`KnowledgeGraphWriter` — entity/relation/mention writes.
* :class:`KnowledgeGraphReader` — narrow read surface for Phase 4 profile
  consolidation.

Each Protocol has a ``make_*`` factory that dispatches on
``settings.storage_backend``. Transitional ``Legacy*`` implementations
wrap the current SQLite + Neo4j stack without behavior change; the
``Postgres*`` implementations write to Postgres IONOS (the target store
per ``docs/postgres-migration.md`` and ``docs/ingestion-workflow.md``).

Infra-level Postgres helpers (connection pool, DDL, migrators) live in
the :mod:`alejandria.storage.postgres` subpackage.
"""
from alejandria.storage.chunk_writer import (
    ChunkRecord,
    ChunkWriter,
    make_chunk_writer,
)
from alejandria.storage.kg_reader import KnowledgeGraphReader, make_kg_reader
from alejandria.storage.kg_writer import KnowledgeGraphWriter, make_kg_writer

__all__ = [
    "ChunkRecord",
    "ChunkWriter",
    "KnowledgeGraphReader",
    "KnowledgeGraphWriter",
    "make_chunk_writer",
    "make_kg_reader",
    "make_kg_writer",
]
