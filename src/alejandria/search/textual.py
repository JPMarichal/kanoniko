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
    reference: str | None = None


class TextualSearch:
    """SQLite FTS5 full-text search engine."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
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
                    metadata TEXT DEFAULT '{}',
                    reference TEXT
                )
            """)
            # Migration: add reference column if missing (existing DBs)
            try:
                conn.execute("ALTER TABLE chunks ADD COLUMN reference TEXT")
            except Exception:
                pass  # column already exists
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
        reference: str | None = None,
    ) -> int:
        """Insert a chunk into the search index. Returns the chunk id."""
        cursor = conn.execute(
            "INSERT INTO chunks (file_path, chunk_index, text, start_char, end_char, metadata, reference) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (file_path, chunk_index, text, start_char, end_char, metadata, reference),
        )
        return cursor.lastrowid  # type: ignore[return-value]

    def delete_by_file(self, conn: sqlite3.Connection, file_path: str) -> int:
        """Delete all chunks for a file. Returns count deleted."""
        cursor = conn.execute("DELETE FROM chunks WHERE file_path = ?", (file_path,))
        return cursor.rowcount

    _STOP_WORDS = frozenset({
        # English
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "shall",
        "should", "may", "might", "can", "could", "must", "what", "which",
        "who", "whom", "when", "where", "why", "how", "that", "this", "these",
        "those", "it", "its", "i", "me", "my", "we", "our", "you", "your",
        "he", "him", "his", "she", "her", "they", "them", "their", "of", "in",
        "to", "for", "with", "on", "at", "by", "from", "as", "if", "or",
        "and", "but", "not", "no", "so", "up", "out", "about", "into", "than",
        "too", "very", "just", "also", "any", "each", "every", "all", "both",
        "some", "such", "other", "than", "then", "there", "here", "ever",
        # Spanish
        "el", "la", "los", "las", "un", "una", "unos", "unas", "es", "son",
        "fue", "era", "del", "al", "en", "de", "con", "por", "para", "se",
        "su", "sus", "que", "qué", "como", "cómo", "cual", "cuál", "donde",
        "dónde", "quien", "quién", "cuando", "cuándo", "yo", "tu", "él",
        "ella", "nos", "les", "lo", "le", "me", "te", "más", "pero", "si",
        "ya", "hay", "no", "ni", "muy",
    })

    @staticmethod
    def _sanitize_fts_query(query: str) -> str:
        """Convert natural-language query to effective FTS5 query.

        - Strips FTS5 operators
        - Removes stop words (EN/ES)
        - Joins remaining keywords with OR for broader matching
        """
        import re
        sanitized = re.sub(r'[*?:^~()"{}]', " ", query)
        words = sanitized.lower().split()
        keywords = [w for w in words if w not in TextualSearch._STOP_WORDS and len(w) > 1]
        if not keywords:
            # Fall back to original if all words were stop words
            return " ".join(sanitized.split())
        # Expand with basic stem variants (plural/singular) using prefix matching
        expanded = []
        for kw in keywords:
            # Use FTS5 prefix token for words > 3 chars to catch plural/singular
            if len(kw) > 3:
                # Strip common suffixes and use prefix match
                stem = kw
                for suffix in ("ies", "es", "ing", "ed", "s"):
                    if kw.endswith(suffix) and len(kw) - len(suffix) >= 3:
                        stem = kw[: -len(suffix)]
                        break
                expanded.append(f"{stem}*")
            else:
                expanded.append(kw)
        return " OR ".join(expanded)

    def search(
        self,
        query: str,
        limit: int = 20,
        file_path_filter: str | None = None,
    ) -> list[TextSearchResult]:
        """Search using BM25 ranking."""
        if not query.strip():
            return []
        query = self._sanitize_fts_query(query)

        with self._conn() as conn:
            if file_path_filter:
                rows = conn.execute(
                    """
                    SELECT c.id, c.text, c.file_path, c.chunk_index, c.metadata,
                           c.reference, bm25(chunks_fts) AS score
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
                           c.reference, bm25(chunks_fts) AS score
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
                reference=row["reference"],
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


# --------------------------------------------------------------------------- #
# Backend factory (Phase 3 of feature/postgres-migration)
# --------------------------------------------------------------------------- #

def make_textual_search(db_path: Path | None = None):
    """Return the configured textual search backend.

    Dispatches on ``settings.storage_backend``:

    * ``"sqlite"`` (default): the battle-tested ``TextualSearch`` over FTS5.
    * ``"postgres"``: ``PostgresTextualSearch`` over tsvector + GIN.

    Named ``make_*`` because the DI layer in ``api/dependencies.py`` already
    owns the name ``get_textual_search`` (lru_cache wrapper around this
    factory). Callers in CLI / MCP / ingestion pipeline should use this
    factory; FastAPI routes pull via the DI accessor.
    """
    from alejandria.config import settings

    backend = (settings.storage_backend or "sqlite").lower()
    if backend == "postgres":
        from alejandria.search.postgres_textual import PostgresTextualSearch
        return PostgresTextualSearch()
    # default: SQLite (legacy stack)
    return TextualSearch(db_path or settings.sqlite_db_path)
