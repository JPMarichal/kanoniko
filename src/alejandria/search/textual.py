"""Full-text search against Postgres (tsvector + GIN + ts_rank_cd).

Canonical textual-search backend post §3.4. The FTS5 SQLite implementation
was retired together with the rest of the SQLite stack.

Design choices:

* Uses ``websearch_to_tsquery('spanish', …)`` for all queries. Spanish is
  the dominant language in the corpus and its stemming is permissive enough
  that English keywords (mostly proper nouns) pass through as literals.
  A future refinement could detect query language and dispatch to
  ``'english'`` or run both and merge — measured latency first.
* Ranking via ``ts_rank_cd`` (cover-density rank). Matches the benchmark
  query from the migration so the latency profile (p95 ~44 ms) applies.
* Per-call connection (no pool) because queries are short reads.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)


@dataclass
class TextSearchResult:
    """One full-text search hit."""

    chunk_id: int
    text: str
    score: float
    file_path: str
    chunk_index: int
    metadata: dict
    reference: str | None = None


class TextualSearch:
    """Full-text search against the Postgres ``chunks.tsv`` GIN index."""

    #: Language passed to ``websearch_to_tsquery``. Kept as a class attribute
    #: so future work can override per-request without changing the signature.
    QUERY_LANGUAGE = "spanish"

    def __init__(self) -> None:
        # No-op init; settings are read lazily by get_connection().
        pass

    # ------------------------------------------------------------------ #
    # Read API
    # ------------------------------------------------------------------ #

    def search(
        self,
        query: str,
        limit: int = 20,
        file_path_filter: str | None = None,
    ) -> list[TextSearchResult]:
        """Full-text search with ``ts_rank_cd`` ranking."""
        if not query.strip():
            return []

        sql = (
            "SELECT c.id, c.text, c.file_path, c.chunk_index, c.metadata, "
            "       c.reference, ts_rank_cd(c.tsv, q) AS score "
            "FROM chunks c, websearch_to_tsquery(%s, %s) q "
            "WHERE c.tsv @@ q"
        )
        params: list[Any] = [self.QUERY_LANGUAGE, query]

        if file_path_filter:
            sql += " AND c.file_path LIKE %s"
            params.append(f"%{file_path_filter}%")

        sql += " ORDER BY score DESC LIMIT %s"
        params.append(limit)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

        results: list[TextSearchResult] = []
        for row in rows:
            metadata_raw = row[4]
            # psycopg3 returns JSONB as dict already; handle TEXT-typed safety net.
            if isinstance(metadata_raw, str):
                try:
                    metadata = json.loads(metadata_raw)
                except Exception:
                    metadata = {}
            else:
                metadata = metadata_raw or {}
            results.append(TextSearchResult(
                chunk_id=row[0],
                text=row[1],
                score=float(row[6]),
                file_path=row[2],
                chunk_index=row[3],
                metadata=metadata,
                reference=row[5],
            ))
        return results

    # ------------------------------------------------------------------ #
    # Stats
    # ------------------------------------------------------------------ #

    def count_chunks(self) -> int:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM chunks")
                return cur.fetchone()[0]

    def count_documents(self) -> int:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(DISTINCT file_path) FROM chunks")
                return cur.fetchone()[0]


def make_textual_search(db_path=None) -> TextualSearch:
    """Return the textual search backend.

    Kept as a factory (rather than inlining ``TextualSearch()``) so the
    DI layer in :mod:`alejandria.api.dependencies` can wrap it with
    ``lru_cache`` without knowing the concrete class.

    ``db_path`` is accepted for backwards compat but ignored — the
    Postgres backend reads connection info from ``settings.postgres_*``.
    """
    return TextualSearch()
