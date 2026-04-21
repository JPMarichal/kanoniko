"""Postgres implementation of :class:`DocumentRegistry`.

Schema lives in ``storage/postgres/ddl.sql`` — the ``document_registry``
table is the FK target for ``chunks`` and ``chunk_embeddings``, so DDL
management is centralized there, not in this module.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from alejandria.ingestion.registry import FileRecord
from alejandria.storage.postgres.connection import get_connection


_COLS = "file_path, sha256, file_size, chunk_count, last_indexed, status"


def _row_to_record(row: tuple[Any, ...]) -> FileRecord:
    file_path, sha256, file_size, chunk_count, last_indexed, status = row
    return FileRecord(
        file_path=file_path,
        sha256=sha256,
        file_size=int(file_size),
        chunk_count=int(chunk_count),
        last_indexed=(
            last_indexed.astimezone(timezone.utc).isoformat()
            if hasattr(last_indexed, "astimezone")
            else str(last_indexed)
        ),
        status=status,
    )


class PostgresDocumentRegistry:
    """Tracks indexed files in Postgres IONOS."""

    def get_record(self, file_path: str) -> FileRecord | None:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT {_COLS} FROM document_registry WHERE file_path = %s",
                (file_path,),
            )
            row = cur.fetchone()
        return _row_to_record(row) if row else None

    def upsert(
        self,
        file_path: str,
        sha256: str,
        file_size: int,
        chunk_count: int,
        status: str = "indexed",
    ) -> None:
        now = datetime.now(timezone.utc)
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO document_registry
                    (file_path, sha256, file_size, chunk_count, last_indexed, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (file_path) DO UPDATE SET
                    sha256       = EXCLUDED.sha256,
                    file_size    = EXCLUDED.file_size,
                    chunk_count  = EXCLUDED.chunk_count,
                    last_indexed = EXCLUDED.last_indexed,
                    status       = EXCLUDED.status
                """,
                (file_path, sha256, file_size, chunk_count, now, status),
            )
            conn.commit()

    def delete(self, file_path: str) -> None:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM document_registry WHERE file_path = %s",
                (file_path,),
            )
            conn.commit()

    def all_records(self) -> list[FileRecord]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT {_COLS} FROM document_registry ORDER BY file_path"
            )
            rows = cur.fetchall()
        return [_row_to_record(r) for r in rows]

    def count(self) -> int:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM document_registry")
            row = cur.fetchone()
        return int(row[0]) if row else 0

    def errors(self) -> list[FileRecord]:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT {_COLS} FROM document_registry WHERE status = 'error'"
            )
            rows = cur.fetchall()
        return [_row_to_record(r) for r in rows]
