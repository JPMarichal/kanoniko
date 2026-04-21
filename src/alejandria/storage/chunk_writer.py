"""Chunk persistence Protocol — text (FTS) + vectors together.

The two layers are consolidated because they are always written together
per chunk during ingestion; separating them would create implicit
synchronization between two Protocols without operational benefit.

Concrete implementations:

* :mod:`alejandria.storage.postgres_chunk_writer` — Postgres IONOS
  (chunks + tsvector + pgvector) — target.
* :mod:`alejandria.storage.legacy_chunk_writer` — adapter over
  :class:`TextualSearch` (SQLite FTS5) + :class:`SemanticSearch`
  (sqlite-vec), transitional, retired in §3.4.

Transaction management is **internal** to each implementation. Callers
do not see connection objects — a contract we need for Postgres, where
leaking ``sqlite3.Connection`` would be a category error.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Protocol, runtime_checkable


@dataclass
class ChunkRecord:
    """One chunk ready to persist.

    Shape is backend-neutral — the driver maps fields to its schema. All
    fields are required except those marked Optional.
    """

    file_path: str
    chunk_index: int
    text: str
    language: str
    reference: str | None = None
    start_char: int | None = None
    end_char: int | None = None
    metadata: dict[str, Any] | None = None


@runtime_checkable
class ChunkWriter(Protocol):
    """Writes and removes chunks in the textual + semantic indices."""

    # ----- Write API -------------------------------------------------- #

    def delete_by_file(self, file_path: str) -> None:
        """Remove all chunks and embeddings belonging to ``file_path``."""
        ...

    def insert_chunks(self, chunks: list[ChunkRecord]) -> list[int]:
        """Insert chunks atomically and return the generated chunk ids.

        Ordering of the returned ids matches the input list so callers
        can correlate ids with the ``(file_path, chunk_index)`` they
        provided. Implementations MUST commit before returning.
        """
        ...

    def upsert_embeddings(
        self,
        ids: list[int],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
    ) -> None:
        """Attach embeddings to previously-inserted chunk ids.

        ``ids``, ``vectors`` and ``payloads`` must be parallel lists of
        equal length. Payloads carry the metadata consumed by the
        semantic reranker (reference, source, language, etc.).
        """
        ...

    def drop_all(self) -> None:
        """Wipe all chunks and embeddings. Used at the start of a full reindex."""
        ...

    # ----- Read API --------------------------------------------------- #
    #
    # Pragmatic inclusion: the ingestion pipeline performs three kinds of
    # read over chunks (full iteration for rebuild_vectors / rebuild_kg,
    # and filtered search for Phase 4 profile consolidation). Separating
    # into a dedicated ChunkReader would mean two Protocols touching the
    # same table — not worth the indirection during migration. Postgres
    # implementations can still route reads to a replica internally.

    def count_chunks(self) -> int:
        ...

    def count_documents(self) -> int:
        ...

    def iter_all_chunks(self) -> Iterable[dict[str, Any]]:
        """Yield every chunk as a dict.

        Keys: ``id``, ``file_path``, ``chunk_index``, ``text``,
        ``metadata`` (parsed dict), ``reference``. Ordered by
        ``(file_path, chunk_index)`` for deterministic processing.
        """
        ...

    def find_chunks_with_patterns(
        self,
        file_paths: list[str],
        text_patterns: list[str],
    ) -> list[dict[str, Any]]:
        """Return chunks whose ``file_path`` is in ``file_paths`` AND whose
        ``text`` matches any of ``text_patterns`` (case-insensitive substring).

        Each item has keys: ``file_path``, ``chunk_index``, ``text``,
        ``reference``. Used by Phase 4 profile building to surface
        supporting passages per entity.
        """
        ...


def make_chunk_writer() -> ChunkWriter:
    """Return the chunk writer selected by ``settings.storage_backend``.

    * ``"postgres"`` — :class:`PostgresChunkWriter`.
    * anything else (transitional) — :class:`LegacyChunkWriter` over the
      existing SQLite FTS5 + sqlite-vec stack.
    """
    from alejandria.config import settings

    backend = (settings.storage_backend or "postgres").lower()
    if backend == "postgres":
        from alejandria.storage.postgres_chunk_writer import PostgresChunkWriter

        return PostgresChunkWriter()
    from alejandria.storage.legacy_chunk_writer import LegacyChunkWriter

    return LegacyChunkWriter()
