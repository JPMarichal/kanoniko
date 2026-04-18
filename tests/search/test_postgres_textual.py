"""Integration tests for PostgresTextualSearch (Phase 3).

Requires a Postgres reachable through the ALEJANDRIA_POSTGRES_* env vars.
Use the SSH tunnel when on corporate network (port 15432 → VPS 5432), or
point at the bench container. Tests skip automatically when Postgres is
not reachable so CI without infra stays green.

    ALEJANDRIA_STORAGE_BACKEND=postgres \
    ALEJANDRIA_POSTGRES_HOST=localhost \
    ALEJANDRIA_POSTGRES_PORT=15432 \
    ... \
    pytest tests/search/test_postgres_textual.py -v
"""
from __future__ import annotations

import pytest

psycopg = pytest.importorskip("psycopg")


def _pg_reachable_with_data() -> bool:
    from alejandria.storage.postgres.connection import get_connection
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM chunks")
                n = cur.fetchone()[0]
        return n > 100  # need real data to test search quality
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _pg_reachable_with_data(),
    reason="Postgres not reachable or empty — set ALEJANDRIA_POSTGRES_* envs",
)


def test_search_returns_results_for_known_query() -> None:
    from alejandria.search.postgres_textual import PostgresTextualSearch

    pg = PostgresTextualSearch()
    results = pg.search("Expiación Jesucristo", limit=5)

    assert len(results) > 0, "should find chunks mentioning Expiación Jesucristo"
    assert all(r.chunk_id > 0 for r in results)
    assert all(r.score > 0 for r in results)
    # Results are ordered by score desc; the first should be the strongest.
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True), "scores must be descending"


def test_search_respects_limit() -> None:
    from alejandria.search.postgres_textual import PostgresTextualSearch

    pg = PostgresTextualSearch()
    r5 = pg.search("profeta", limit=5)
    r20 = pg.search("profeta", limit=20)

    assert len(r5) <= 5
    assert len(r20) <= 20
    assert len(r20) >= len(r5)


def test_search_file_path_filter() -> None:
    from alejandria.search.postgres_textual import PostgresTextualSearch

    pg = PostgresTextualSearch()
    unfiltered = pg.search("evangelio", limit=20)
    filtered = pg.search("evangelio", limit=20, file_path_filter="es/")

    assert len(filtered) <= len(unfiltered)
    assert all("es/" in r.file_path for r in filtered), \
        "filter must restrict to matching file_path substring"


def test_search_empty_query_returns_empty() -> None:
    from alejandria.search.postgres_textual import PostgresTextualSearch

    pg = PostgresTextualSearch()
    assert pg.search("") == []
    assert pg.search("   ") == []


def test_count_methods() -> None:
    from alejandria.search.postgres_textual import PostgresTextualSearch

    pg = PostgresTextualSearch()
    n_chunks = pg.count_chunks()
    n_docs = pg.count_documents()

    assert n_chunks > 100
    assert n_docs > 0
    assert n_docs <= n_chunks  # each doc has >= 1 chunk


def test_result_dataclass_shape() -> None:
    """Guard against the Postgres backend silently diverging from the SQLite
    TextSearchResult shape. search/hybrid.py reads `.score`, `.text`, etc."""
    from alejandria.search.postgres_textual import PostgresTextualSearch
    from alejandria.search.textual import TextSearchResult

    pg = PostgresTextualSearch()
    results = pg.search("Jerusalén", limit=1)
    if not results:
        pytest.skip("no matches for seed query; test is environment-dependent")
    r = results[0]
    assert isinstance(r, TextSearchResult)
    for attr in ("chunk_id", "text", "score", "file_path", "chunk_index",
                 "metadata", "reference"):
        assert hasattr(r, attr), f"missing attr {attr}"
    assert isinstance(r.metadata, dict)


# --------------------------------------------------------------------------- #
# Factory
# --------------------------------------------------------------------------- #

def test_factory_returns_postgres_when_flag_set(monkeypatch) -> None:
    """make_textual_search must dispatch on settings.storage_backend."""
    from alejandria.config import settings
    from alejandria.search.textual import make_textual_search
    from alejandria.search.postgres_textual import PostgresTextualSearch

    monkeypatch.setattr(settings, "storage_backend", "postgres")
    backend = make_textual_search()
    assert isinstance(backend, PostgresTextualSearch)


def test_factory_returns_sqlite_by_default(monkeypatch, tmp_path) -> None:
    from alejandria.config import settings
    from alejandria.search.textual import make_textual_search, TextualSearch

    monkeypatch.setattr(settings, "storage_backend", "sqlite")
    # override sqlite_db_path to a fresh temp file so we don't touch real data
    monkeypatch.setattr(settings, "sqlite_db_path", tmp_path / "test.db")
    backend = make_textual_search(db_path=tmp_path / "test.db")
    assert isinstance(backend, TextualSearch)
