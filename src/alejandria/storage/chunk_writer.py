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
from typing import Any, Protocol, runtime_checkable


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

    # ----- Read-ish helpers (counts) ---------------------------------- #
    #
    # Pragmatic inclusion: the public API exposes these counts and they
    # are trivial to implement per backend. Separating into a
    # ChunkReader for two methods would be overengineered.

    def count_chunks(self) -> int:
        ...

    def count_documents(self) -> int:
        ...


def make_chunk_writer() -> ChunkWriter:
    """Return the chunk writer selected by ``settings.storage_backend``.

    * ``"postgres"`` — :class:`PostgresChunkWriter`.
    * anything else (transitional) — :class:`LegacyChunkWriter` over the
      existing SQLite FTS5 + sqlite-vec stack.
    """
    from alejandria.config import settings

    backend = (settings.storage_backend or "sqlite").lower()
    if backend == "postgres":
        from alejandria.storage.postgres_chunk_writer import PostgresChunkWriter

        return PostgresChunkWriter()
    from alejandria.storage.legacy_chunk_writer import LegacyChunkWriter

    return LegacyChunkWriter()
