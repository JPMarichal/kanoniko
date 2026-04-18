"""Semantic search against Postgres (pgvector HNSW index).

Postgres-backend counterpart of ``SemanticSearch`` (SQLite + sqlite-vec).
Same public API so ``search/hybrid.py`` can switch backends via
``settings.storage_backend`` without knowing the implementation.

Design choices:

* Uses pgvector's ``<=>`` operator (cosine distance) against the HNSW index
  built by ``storage.postgres.schema.ensure_hnsw_index``. Same distance
  metric as sqlite-vec so the score semantics match (``1 - distance``).
* The query vector is passed as text in pgvector format (``[v1,v2,…]``).
  psycopg3 handles the cast via the ``::vector`` annotation.
* JOIN to ``chunks`` for text/metadata because the embeddings table is a
  minimal ``(chunk_id, embedding)`` shape — unlike sqlite-vec's vec0 which
  carried payload columns.
* Per-call connection (mirrors the textual backend).
"""
from __future__ import annotations

import logging
from typing import Any

from alejandria.search.semantic import SemanticSearchResult
from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)


def _vector_to_pg_text(vec: list[float]) -> str:
    """pgvector accepts text format ``[v1,v2,…,vN]`` with the ::vector cast."""
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"


class PostgresSemanticSearch:
    """HNSW-backed nearest neighbor search over ``chunk_embeddings``."""

    def __init__(self) -> None:
        # No-op init; settings read lazily.
        pass

    # ------------------------------------------------------------------ #
    # Read API
    # ------------------------------------------------------------------ #

    def search(
        self,
        query_vector: list[float],
        limit: int = 20,
        source_filter: str | None = None,
    ) -> list[SemanticSearchResult]:
        """k-NN search with cosine distance.

        Score = ``1 - cosine_distance`` so 1.0 = identical, 0.0 = orthogonal,
        -1.0 = opposite (matches the SQLite backend's score space).
        """
        if not query_vector:
            return []

        vec_text = _vector_to_pg_text(query_vector)

        # We hit chunks.metadata JSONB to filter by source. In sqlite-vec,
        # `source` was a first-class column in vec0; here it's part of the
        # payload we migrated into chunks.metadata.
        sql = (
            "SELECT c.id, c.text, c.file_path, c.chunk_index, c.metadata, "
            "       c.reference, (1 - (e.embedding <=> %s::vector))::float AS score "
            "FROM chunk_embeddings e "
            "JOIN chunks c ON c.id = e.chunk_id "
        )
        params: list[Any] = [vec_text]

        if source_filter:
            sql += "WHERE c.metadata->>'source' = %s "
            params.append(source_filter)

        # ORDER BY the distance operator (not the score) so the planner can
        # use the HNSW index. Score is just the inverted display value.
        sql += "ORDER BY e.embedding <=> %s::vector LIMIT %s"
        params.extend([vec_text, limit])

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

        results: list[SemanticSearchResult] = []
        for row in rows:
            metadata = row[4] if isinstance(row[4], dict) else {}
            results.append(SemanticSearchResult(
                chunk_id=row[0],
                text=row[1] or "",
                score=float(row[6]),
                file_path=row[2] or "",
                chunk_index=row[3] or 0,
                metadata=metadata,
                reference=row[5],
            ))
        return results

    def count(self) -> int:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM chunk_embeddings")
                row = cur.fetchone()
                return row[0] if row else 0
