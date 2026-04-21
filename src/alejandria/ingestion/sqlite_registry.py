"""SQLite implementation of :class:`DocumentRegistry`.

Transitional — retired in §3.4 of ``docs/ingestion-workflow.md`` together
with the rest of the SQLite stack. New code should depend on
:func:`make_document_registry`, not on this class directly.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from alejandria.ingestion.registry import FileRecord


class SqliteDocumentRegistry:
    """Tracks indexed files in a local SQLite database."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS document_registry (
                    file_path    TEXT PRIMARY KEY,
                    sha256       TEXT NOT NULL,
                    file_size    INTEGER NOT NULL,
                    chunk_count  INTEGER DEFAULT 0,
                    last_indexed TEXT NOT NULL,
                    status       TEXT DEFAULT 'pending'
                )
                """
            )

    def get_record(self, file_path: str) -> FileRecord | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM document_registry WHERE file_path = ?", (file_path,)
            ).fetchone()
        if row is None:
            return None
        return FileRecord(**dict(row))

    def upsert(
        self,
        file_path: str,
        sha256: str,
        file_size: int,
        chunk_count: int,
        status: str = "indexed",
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO document_registry
                    (file_path, sha256, file_size, chunk_count, last_indexed, status)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    sha256 = excluded.sha256,
                    file_size = excluded.file_size,
                    chunk_count = excluded.chunk_count,
                    last_indexed = excluded.last_indexed,
                    status = excluded.status
                """,
                (file_path, sha256, file_size, chunk_count, now, status),
            )

    def delete(self, file_path: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "DELETE FROM document_registry WHERE file_path = ?", (file_path,)
            )

    def all_records(self) -> list[FileRecord]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM document_registry ORDER BY file_path"
            ).fetchall()
        return [FileRecord(**dict(r)) for r in rows]

    def count(self) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM document_registry"
            ).fetchone()
            return row["cnt"]

    def errors(self) -> list[FileRecord]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM document_registry WHERE status = 'error'"
            ).fetchall()
        return [FileRecord(**dict(r)) for r in rows]
