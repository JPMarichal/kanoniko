"""Full-text search against Postgres (tsvector + GIN + ts_rank_cd).

Postgres-backend counterpart of ``TextualSearch`` (SQLite FTS5). Same public
API so ``search/hybrid.py`` doesn't need to know which backend is active —
the factory in ``textual.py::get_textual_search`` decides at runtime based
on ``settings.storage_backend``.

Design choices:

* Uses ``websearch_to_tsquery('spanish', …)`` for all queries. Spanish is
  the dominant language in the corpus and its stemming is permissive enough
  that English keywords (mostly proper nouns) pass through as literals.
  A future refinement could detect query language and dispatch to
  ``'english'`` or run both and merge — measured latency first.
* Ranking via ``ts_rank_cd`` (cover-density rank). Matches the benchmark
  query from phase 1 so the latency profile we measured (p95 ~44 ms)
  applies.
* Per-call connection (no pool) because queries are short reads and the
  connection pool adds state we don't need during migration.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from alejandria.search.textual import TextSearchResult
from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)


class PostgresTextualSearch:
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
        """Full-text search with ``ts_rank_cd`` ranking.

        Matches the SQLite ``TextualSearch.search`` signature so that callers
        (notably ``search/hybrid.py``) don't need to care which backend is in
        use.
        """
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
    # Stats (mirrors SQLite backend)
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
