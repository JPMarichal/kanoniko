"""Integration tests for PostgresSemanticSearch (Phase 3).

Requires a Postgres with chunk_embeddings populated + HNSW built. Uses a
random 384-dim query vector to exercise the k-NN path; doesn't need the
real embedding model loaded.
"""
from __future__ import annotations

import pytest

psycopg = pytest.importorskip("psycopg")
np = pytest.importorskip("numpy")


def _pg_reachable_with_embeddings() -> bool:
    from alejandria.storage.postgres.connection import get_connection
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM chunk_embeddings")
                n = cur.fetchone()[0]
        return n > 100
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _pg_reachable_with_embeddings(),
    reason="Postgres not reachable or chunk_embeddings empty",
)


def _random_vec(dim: int = 384) -> list[float]:
    """Random unit-norm vector for k-NN exercises."""
    rng = np.random.default_rng(42)
    v = rng.standard_normal(dim).astype(float)
    v = v / (np.linalg.norm(v) + 1e-9)
    return v.tolist()


def test_search_returns_results() -> None:
    from alejandria.search.postgres_semantic import PostgresSemanticSearch

    pg = PostgresSemanticSearch()
    results = pg.search(_random_vec(), limit=10)

    assert 0 < len(results) <= 10
    for r in results:
        assert r.chunk_id > 0
        # Cosine similarity score range [-1, 1]
        assert -1.0 <= r.score <= 1.0


def test_search_respects_limit() -> None:
    from alejandria.search.postgres_semantic import PostgresSemanticSearch

    pg = PostgresSemanticSearch()
    assert len(pg.search(_random_vec(), limit=5)) <= 5
    assert len(pg.search(_random_vec(), limit=50)) <= 50


def test_search_ordered_by_similarity_desc() -> None:
    from alejandria.search.postgres_semantic import PostgresSemanticSearch

    pg = PostgresSemanticSearch()
    results = pg.search(_random_vec(), limit=10)
    if len(results) < 2:
        pytest.skip("not enough matches to check ordering")
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True), \
        "score must be descending (higher = more similar)"


def test_search_empty_vector_returns_empty() -> None:
    from alejandria.search.postgres_semantic import PostgresSemanticSearch
    pg = PostgresSemanticSearch()
    assert pg.search([], limit=10) == []


def test_count() -> None:
    from alejandria.search.postgres_semantic import PostgresSemanticSearch
    pg = PostgresSemanticSearch()
    assert pg.count() > 100


def test_factory_returns_postgres_when_flag_set(monkeypatch) -> None:
    from alejandria.config import settings
    from alejandria.search.semantic import make_semantic_search
    from alejandria.search.postgres_semantic import PostgresSemanticSearch

    monkeypatch.setattr(settings, "storage_backend", "postgres")
    backend = make_semantic_search()
    assert isinstance(backend, PostgresSemanticSearch)


def test_factory_returns_sqlite_by_default(monkeypatch, tmp_path) -> None:
    import importlib.util
    if importlib.util.find_spec("sqlite_vec") is None:
        pytest.skip("sqlite_vec not installed in this test env (legacy stack opt-in)")

    from alejandria.config import settings
    from alejandria.search.semantic import make_semantic_search, SemanticSearch

    monkeypatch.setattr(settings, "storage_backend", "sqlite")
    monkeypatch.setattr(settings, "sqlite_db_path", tmp_path / "test.db")
    backend = make_semantic_search(db_path=tmp_path / "test.db")
    assert isinstance(backend, SemanticSearch)
