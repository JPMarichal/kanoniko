"""Full-text search using SQLite FTS5 with BM25 ranking."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TextSearchResult:
    chunk_id: int
    text: str
    score: float
    file_path: str
    chunk_index: int
    metadata: dict


class TextualSearch:
    """SQLite FTS5 full-text search engine."""

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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    start_char INTEGER,
                    end_char INTEGER,
                    metadata TEXT DEFAULT '{}'
                )
            """)
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    text,
                    content='chunks',
                    content_rowid='id',
                    tokenize='unicode61'
                )
            """)
            # Triggers to keep FTS in sync
            conn.executescript("""
                CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
                    INSERT INTO chunks_fts(rowid, text) VALUES (new.id, new.text);
                END;
                CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
                    INSERT INTO chunks_fts(chunks_fts, rowid, text) VALUES('delete', old.id, old.text);
                END;
                CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
                    INSERT INTO chunks_fts(chunks_fts, rowid, text) VALUES('delete', old.id, old.text);
                    INSERT INTO chunks_fts(rowid, text) VALUES (new.id, new.text);
                END;
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_file ON chunks(file_path)
            """)

    def index_chunk(
        self,
        conn: sqlite3.Connection,
        file_path: str,
        chunk_index: int,
        text: str,
        start_char: int,
        end_char: int,
        metadata: str = "{}",
    ) -> int:
        """Insert a chunk into the search index. Returns the chunk id."""
        cursor = conn.execute(
            "INSERT INTO chunks (file_path, chunk_index, text, start_char, end_char, metadata) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (file_path, chunk_index, text, start_char, end_char, metadata),
        )
        return cursor.lastrowid  # type: ignore[return-value]

    def delete_by_file(self, conn: sqlite3.Connection, file_path: str) -> int:
        """Delete all chunks for a file. Returns count deleted."""
        cursor = conn.execute("DELETE FROM chunks WHERE file_path = ?", (file_path,))
        return cursor.rowcount

    def search(
        self,
        query: str,
        limit: int = 20,
        file_path_filter: str | None = None,
    ) -> list[TextSearchResult]:
        """Search using BM25 ranking."""
        if not query.strip():
            return []

        with self._conn() as conn:
            if file_path_filter:
                rows = conn.execute(
                    """
                    SELECT c.id, c.text, c.file_path, c.chunk_index, c.metadata,
                           bm25(chunks_fts) AS score
                    FROM chunks_fts fts
                    JOIN chunks c ON c.id = fts.rowid
                    WHERE chunks_fts MATCH ?
                      AND c.file_path LIKE ?
                    ORDER BY score
                    LIMIT ?
                    """,
                    (query, f"%{file_path_filter}%", limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT c.id, c.text, c.file_path, c.chunk_index, c.metadata,
                           bm25(chunks_fts) AS score
                    FROM chunks_fts fts
                    JOIN chunks c ON c.id = fts.rowid
                    WHERE chunks_fts MATCH ?
                    ORDER BY score
                    LIMIT ?
                    """,
                    (query, limit),
                ).fetchall()

        results = []
        for row in rows:
            import json
            results.append(TextSearchResult(
                chunk_id=row["id"],
                text=row["text"],
                score=abs(row["score"]),  # BM25 returns negative scores in FTS5
                file_path=row["file_path"],
                chunk_index=row["chunk_index"],
                metadata=json.loads(row["metadata"]),
            ))
        return results

    def get_connection(self) -> sqlite3.Connection:
        """Get a connection for batch operations."""
        return self._conn()

    def count_chunks(self) -> int:
        with self._conn() as conn:
            row = conn.execute("SELECT COUNT(*) AS cnt FROM chunks").fetchone()
            return row["cnt"]

    def count_documents(self) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(DISTINCT file_path) AS cnt FROM chunks"
            ).fetchone()
            return row["cnt"]
