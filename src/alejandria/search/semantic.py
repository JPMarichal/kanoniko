"""Semantic search using sqlite-vec (in-process vector search)."""

from __future__ import annotations

import logging
import sqlite3
import struct
from dataclasses import dataclass
from pathlib import Path

# sqlite_vec is the SQLite-backend dependency. Import it lazily inside the
# class methods so that callers that only use the Postgres backend (or just
# the SemanticSearchResult dataclass) don't need sqlite-vec installed.

from alejandria.config import settings

logger = logging.getLogger(__name__)


def _serialize_f32(vector: list[float]) -> bytes:
    """Serialize a float vector to packed float32 bytes for sqlite-vec."""
    return struct.pack(f"{len(vector)}f", *vector)


@dataclass
class SemanticSearchResult:
    chunk_id: int
    text: str
    score: float
    file_path: str
    chunk_index: int
    metadata: dict
    reference: str | None = None


class SemanticSearch:
    """sqlite-vec backed semantic vector search."""

    TABLE = "chunk_vectors"

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or settings.sqlite_db_path
        self._ensure_table()

    def _conn(self) -> sqlite3.Connection:
        import sqlite_vec  # lazy — only needed when the SQLite backend is used
        conn = sqlite3.connect(str(self._db_path), timeout=30)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    def _ensure_table(self) -> None:
        with self._conn() as conn:
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {self.TABLE} USING vec0(
                    id integer primary key,
                    embedding float[{settings.embedding_dim}] distance_metric=cosine,
                    source text,
                    +file_path text,
                    +text_content text,
                    +chunk_index integer,
                    +reference text
                )
            """)

    def upsert_chunks(
        self,
        ids: list[int],
        vectors: list[list[float]],
        payloads: list[dict],
    ) -> None:
        """Upsert chunk vectors with metadata payloads."""
        with self._conn() as conn:
            for i in range(0, len(ids), 100):
                batch_ids = ids[i : i + 100]
                batch_vecs = vectors[i : i + 100]
                batch_pays = payloads[i : i + 100]

                conn.executemany(
                    f"INSERT OR REPLACE INTO {self.TABLE}"
                    f"(id, embedding, source, file_path, text_content, chunk_index, reference) "
                    f"VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [
                        (
                            id_,
                            _serialize_f32(vec),
                            payload.get("source", ""),
                            payload.get("file_path", ""),
                            payload.get("text", ""),
                            payload.get("chunk_index", 0),
                            payload.get("reference"),
                        )
                        for id_, vec, payload in zip(batch_ids, batch_vecs, batch_pays)
                    ],
                )

    def delete_by_file(self, file_path: str) -> None:
        """Delete all vectors for a given file."""
        with self._conn() as conn:
            # Get rowids via the chunks table (same DB, same ids)
            rows = conn.execute(
                "SELECT id FROM chunks WHERE file_path = ?", (file_path,)
            ).fetchall()
            if rows:
                placeholders = ",".join("?" for _ in rows)
                conn.execute(
                    f"DELETE FROM {self.TABLE} WHERE id IN ({placeholders})",
                    [r[0] for r in rows],
                )

    def search(
        self,
        query_vector: list[float],
        limit: int = 20,
        source_filter: str | None = None,
    ) -> list[SemanticSearchResult]:
        """Search for similar vectors."""
        query_bytes = _serialize_f32(query_vector)

        with self._conn() as conn:
            if source_filter:
                rows = conn.execute(
                    f"SELECT id, distance, file_path, text_content, chunk_index, reference "
                    f"FROM {self.TABLE} "
                    f"WHERE embedding MATCH ? AND k = ? AND source = ?",
                    (query_bytes, limit, source_filter),
                ).fetchall()
            else:
                rows = conn.execute(
                    f"SELECT id, distance, file_path, text_content, chunk_index, reference "
                    f"FROM {self.TABLE} "
                    f"WHERE embedding MATCH ? AND k = ?",
                    (query_bytes, limit),
                ).fetchall()

        results = []
        for row in rows:
            # sqlite-vec returns cosine distance (0 = identical, 2 = opposite)
            # Convert to similarity score (1 = identical, -1 = opposite)
            distance = row[1]
            score = 1.0 - distance
            results.append(SemanticSearchResult(
                chunk_id=row[0],
                text=row[3] or "",
                score=score,
                file_path=row[2] or "",
                chunk_index=row[4] or 0,
                metadata={
                    "source": source_filter or "",
                    "file": row[2] or "",
                },
                reference=row[5],
            ))
        return results

    def count(self) -> int:
        with self._conn() as conn:
            row = conn.execute(f"SELECT count(*) FROM {self.TABLE}").fetchone()
            return row[0] if row else 0

    def drop_collection(self) -> None:
        """Drop and recreate the vector table (for full reindex)."""
        with self._conn() as conn:
            conn.execute(f"DROP TABLE IF EXISTS {self.TABLE}")
        self._ensure_table()


# --------------------------------------------------------------------------- #
# Backend factory (Phase 3 of feature/postgres-migration)
# --------------------------------------------------------------------------- #

def make_semantic_search(db_path: Path | None = None):
    """Return the configured semantic search backend.

    Dispatches on ``settings.storage_backend``:

    * ``"sqlite"`` (default): ``SemanticSearch`` over sqlite-vec (vec0).
    * ``"postgres"``: ``PostgresSemanticSearch`` over pgvector HNSW.

    Named ``make_*`` (not ``get_*``) because the DI layer in
    ``api/dependencies.py`` owns the name ``get_semantic_search`` (retry
    caching wrapper around this factory).
    """
    from alejandria.config import settings

    backend = (settings.storage_backend or "postgres").lower()
    if backend == "postgres":
        from alejandria.search.postgres_semantic import PostgresSemanticSearch
        return PostgresSemanticSearch()
    return SemanticSearch(db_path)
