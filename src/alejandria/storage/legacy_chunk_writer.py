"""Transitional adapter: :class:`ChunkWriter` over SQLite FTS5 + sqlite-vec.

Wraps the existing :class:`alejandria.search.textual.TextualSearch` and
:class:`alejandria.search.semantic.SemanticSearch` without changing their
behavior. The pipeline calls this adapter through the Protocol; when the
default backend flips to Postgres in §3.4, this module is deleted
together with ``TextualSearch`` and ``SemanticSearch``.

Transaction management — currently one ``sqlite3.Connection`` per public
method — is hidden inside the adapter so callers never see it. That
matches the Protocol contract and keeps the refactor of ``pipeline.py``
a pure rename.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from alejandria.config import settings
from alejandria.search.semantic import SemanticSearch
from alejandria.search.textual import TextualSearch
from alejandria.storage.chunk_writer import ChunkRecord

logger = logging.getLogger(__name__)


class LegacyChunkWriter:
    """Chunk writer backed by SQLite FTS5 + sqlite-vec."""

    def __init__(
        self,
        textual: TextualSearch | None = None,
        semantic: SemanticSearch | None = None,
    ) -> None:
        # Default construction mirrors the wiring used historically by
        # ``api/dependencies.py``: both backends rooted at
        # ``settings.sqlite_db_path``.
        self._textual = textual or TextualSearch(settings.sqlite_db_path)
        # sqlite-vec is optional at import-time; fall back to None if the
        # extension is missing, so the pipeline's existing None-check path
        # keeps working. Callers that require vectors must check the
        # runtime outcome, as they did with the old SemanticSearch wiring.
        if semantic is not None:
            self._semantic = semantic
        else:
            try:
                self._semantic = SemanticSearch(settings.sqlite_db_path)
            except Exception:  # sqlite-vec extension missing, DB locked, etc.
                logger.warning(
                    "sqlite-vec unavailable; LegacyChunkWriter running in "
                    "textual-only mode",
                    exc_info=True,
                )
                self._semantic = None  # type: ignore[assignment]

    # ----- Write API -------------------------------------------------- #

    def delete_by_file(self, file_path: str) -> None:
        conn = self._textual.get_connection()
        try:
            with conn:
                self._textual.delete_by_file(conn, file_path)
        finally:
            conn.close()
        if self._semantic is not None:
            self._semantic.delete_by_file(file_path)

    def insert_chunks(self, chunks: list[ChunkRecord]) -> list[int]:
        if not chunks:
            return []
        ids: list[int] = []
        conn = self._textual.get_connection()
        try:
            with conn:
                for c in chunks:
                    chunk_id = self._textual.index_chunk(
                        conn,
                        file_path=c.file_path,
                        chunk_index=c.chunk_index,
                        text=c.text,
                        start_char=c.start_char or 0,
                        end_char=c.end_char or 0,
                        metadata=json.dumps(c.metadata or {}, ensure_ascii=False),
                        reference=c.reference,
                    )
                    ids.append(int(chunk_id))
        finally:
            conn.close()
        return ids

    def upsert_embeddings(
        self,
        ids: list[int],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
    ) -> None:
        if self._semantic is None:
            return  # textual-only fallback — consistent with the old code
        self._semantic.upsert_chunks(ids=ids, vectors=vectors, payloads=payloads)

    def drop_all(self) -> None:
        # Textual: recreate the table via init; sqlite-vec: drop_collection.
        conn = self._textual.get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM chunks")
        finally:
            conn.close()
        if self._semantic is not None:
            self._semantic.drop_collection()

    # ----- Counts ----------------------------------------------------- #

    def count_chunks(self) -> int:
        return self._textual.count_chunks()

    def count_documents(self) -> int:
        return self._textual.count_documents()
