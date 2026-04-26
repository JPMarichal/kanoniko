"""Postgres implementation of :class:`ChunkWriter`.

Writes chunks to Postgres IONOS: ``chunks`` carries the text + an automatic
``tsvector`` column (FTS via ``chunks_tsv_gin``), ``chunk_embeddings`` holds
pgvector embeddings. DDL lives in ``storage/postgres/ddl.sql``.

Transaction policy: each public method opens one connection and one
transaction. Callers never see psycopg objects.

FK subtlety: ``chunks.file_path`` references ``document_registry(file_path)``.
Because the pipeline orders its writes so the registry row is upserted
*after* chunks succeed, :meth:`insert_chunks` touches the registry row with
placeholder values on conflict-do-nothing so the FK is satisfied.
:meth:`alejandria.ingestion.registry.PostgresDocumentRegistry.upsert` later
replaces those placeholders with real metadata.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Iterable

from alejandria.storage.chunk_writer import ChunkRecord
from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)


def _detect_language(metadata: dict[str, Any] | None, fallback: str = "es") -> str:
    if not metadata:
        return fallback
    lang = metadata.get("lang") or metadata.get("language")
    if isinstance(lang, str) and len(lang) >= 2:
        return lang[:2].lower()
    return fallback


class PostgresChunkWriter:
    """ChunkWriter backed by Postgres + pgvector."""

    # ------------------------------------------------------------------ #
    # Write API
    # ------------------------------------------------------------------ #

    def delete_by_file(self, file_path: str) -> None:
        # chunk_embeddings cascades via FK chunks.id -> chunk_embeddings.chunk_id.
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM chunks WHERE file_path = %s", (file_path,))
            conn.commit()

    def insert_chunks(self, chunks: list[ChunkRecord]) -> list[int]:
        if not chunks:
            return []

        # Ensure registry rows exist (FK). The real upsert happens later in
        # the pipeline; these placeholders will be overwritten.
        distinct_paths = sorted({c.file_path for c in chunks})

        rows = [
            (
                c.file_path,
                c.chunk_index,
                c.text,
                c.reference,
                c.start_char,
                c.end_char,
                json.dumps(c.metadata or {}, ensure_ascii=False),
                _detect_language(c.metadata, fallback=c.language or "es"),
            )
            for c in chunks
        ]

        with get_connection() as conn, conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO document_registry
                    (file_path, sha256, file_size, chunk_count, status)
                VALUES (%s, '', 0, 0, 'indexing')
                ON CONFLICT (file_path) DO NOTHING
                """,
                [(p,) for p in distinct_paths],
            )
            # Insert chunks. RETURNING id preserves the input order because
            # executemany with RETURNING is only supported row-by-row in
            # psycopg3; use execute in a loop.
            ids: list[int] = []
            for row in rows:
                cur.execute(
                    """
                    INSERT INTO chunks
                        (file_path, chunk_index, text, reference,
                         start_char, end_char, metadata, language)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                    RETURNING id
                    """,
                    row,
                )
                ids.append(int(cur.fetchone()[0]))
            conn.commit()
        return ids

    def upsert_embeddings(
        self,
        ids: list[int],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
    ) -> None:
        if not ids:
            return
        if not (len(ids) == len(vectors) == len(payloads)):
            raise ValueError(
                "ids / vectors / payloads must be parallel lists of equal length"
            )
        # pgvector accepts the literal "[...]" string form.
        rows = [
            (chunk_id, "[" + ",".join(f"{v:.8f}" for v in vec) + "]")
            for chunk_id, vec in zip(ids, vectors)
        ]
        with get_connection() as conn, conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO chunk_embeddings (chunk_id, embedding)
                VALUES (%s, %s::vector)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    embedding = EXCLUDED.embedding
                """,
                rows,
            )
            conn.commit()

    def drop_all(self) -> None:
        # TRUNCATE cascades through chunk_embeddings (FK). document_registry
        # is preserved — the pipeline's caller decides when to clear it.
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("TRUNCATE chunks RESTART IDENTITY CASCADE")
            conn.commit()

    # ------------------------------------------------------------------ #
    # Counts
    # ------------------------------------------------------------------ #

    def count_chunks(self) -> int:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM chunks")
            row = cur.fetchone()
        return int(row[0]) if row else 0

    def count_documents(self) -> int:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(DISTINCT file_path) FROM chunks")
            row = cur.fetchone()
        return int(row[0]) if row else 0

    # ------------------------------------------------------------------ #
    # Reads
    # ------------------------------------------------------------------ #

    def iter_all_chunks(self) -> Iterable[dict[str, Any]]:
        # Full-corpus rebuilds can exceed the default statement timeout on
        # remote Postgres even though the scan itself is expected. Keep the
        # override scoped to this read connection and stream rows in batches
        # instead of materializing the whole corpus up front.
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SET statement_timeout = 0")
            cur.execute(
                "SELECT id, file_path, chunk_index, text, metadata, reference "
                "FROM chunks ORDER BY file_path, chunk_index"
            )
            while True:
                rows = cur.fetchmany(1_000)
                if not rows:
                    break
                for row in rows:
                    cid, fp, idx, text, metadata, reference = row
                    yield {
                        "id": int(cid),
                        "file_path": fp,
                        "chunk_index": int(idx),
                        "text": text,
                        "metadata": metadata if isinstance(metadata, dict) else (
                            json.loads(metadata) if metadata else {}
                        ),
                        "reference": reference,
                    }

    def find_chunks_with_patterns(
        self,
        file_paths: list[str],
        text_patterns: list[str],
    ) -> list[dict[str, Any]]:
        if not file_paths or not text_patterns:
            return []
        # ILIKE ANY for case-insensitive substring match across multiple
        # patterns. Much cleaner than the sqlite OR-chain.
        patterns_sql = [f"%{p.lower()}%" for p in text_patterns]
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT file_path, chunk_index, text, reference
                FROM chunks
                WHERE file_path = ANY(%s)
                  AND LOWER(text) ILIKE ANY(%s)
                ORDER BY file_path, chunk_index
                """,
                (file_paths, patterns_sql),
            )
            rows = cur.fetchall()
        return [
            {
                "file_path": r[0],
                "chunk_index": int(r[1]),
                "text": r[2],
                "reference": r[3],
            }
            for r in rows
        ]
