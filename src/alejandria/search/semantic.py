"""Semantic search against Postgres (pgvector HNSW index).

Canonical semantic-search backend post §3.4. The sqlite-vec implementation
was retired together with the rest of the SQLite stack.

Design choices:

* Uses pgvector's ``<=>`` operator (cosine distance) against the HNSW index
  built by ``storage.postgres.schema.ensure_hnsw_index``. Score is
  ``1 - distance`` (1.0 = identical, 0.0 = orthogonal).
* The query vector is passed as text in pgvector format (``[v1,v2,…]``);
  psycopg3 handles the cast via the ``::vector`` annotation.
* JOIN to ``chunks`` for text/metadata because ``chunk_embeddings`` is
  a minimal ``(chunk_id, embedding)`` shape.
* Per-call connection (mirrors the textual backend).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)


@dataclass
class SemanticSearchResult:
    """One semantic (vector) search hit."""

    chunk_id: int
    text: str
    score: float
    file_path: str
    chunk_index: int
    metadata: dict
    reference: str | None = None


def _vector_to_pg_text(vec: list[float]) -> str:
    """pgvector accepts text format ``[v1,v2,…,vN]`` with the ::vector cast."""
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"


class SemanticSearch:
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
        -1.0 = opposite.
        """
        if not query_vector:
            return []

        vec_text = _vector_to_pg_text(query_vector)

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


def make_semantic_search(db_path=None) -> SemanticSearch:
    """Return the semantic search backend.

    ``db_path`` accepted for backwards compat but ignored — the backend
    reads connection info from ``settings.postgres_*``.
    """
    return SemanticSearch()
