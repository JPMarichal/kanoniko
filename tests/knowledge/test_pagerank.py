"""Tests for Personalized PageRank (PPR) graph search.

Covers:
- Pure algorithm tests with synthetic NetworkX graphs (no DB).
- Integration tests against live Postgres (skipped if unreachable).
"""
from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Pure algorithm tests (no Postgres required)
# ---------------------------------------------------------------------------

class TestPPRAlgorithm:
    """Test PPR logic using a hand-built NetworkX graph."""

    @staticmethod
    def _build_simple_graph() -> "nx.Graph":
        """Build a 5-node path: 1-2-3-4-5."""
        import networkx as nx

        G = nx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5)])
        return G

    def test_pagerank_converges(self) -> None:
        """PPR should converge on a simple path graph."""
        from alejandria.knowledge.pagerank import _power_iteration_ppr

        G = self._build_simple_graph()
        scores = _power_iteration_ppr(G, seed_ids=[3], alpha=0.5)

        assert abs(sum(scores.values()) - 1.0) < 1e-4
        assert scores[3] > scores[2]
        assert scores[3] > scores[4]

    def test_pagerank_decays_with_distance(self) -> None:
        """Scores should decay as distance from seed increases."""
        from alejandria.knowledge.pagerank import _power_iteration_ppr

        G = self._build_simple_graph()
        scores = _power_iteration_ppr(G, seed_ids=[1], alpha=0.5)

        assert scores[1] > scores[2] > scores[3] > scores[4] > scores[5]

    def test_pagerank_alpha_zero(self) -> None:
        """alpha=0 converges to stationary distribution on a non-bipartite graph."""
        from alejandria.knowledge.pagerank import _power_iteration_ppr

        import networkx as nx

        G = nx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 1)])
        scores = _power_iteration_ppr(G, seed_ids=[1], alpha=0.0)

        # Triangle: all nodes have degree 2, stationary distribution is uniform.
        for s in scores.values():
            assert abs(s - 1/3) < 1e-4

    def test_pagerank_alpha_one(self) -> None:
        """alpha=1 should give all score to seed nodes."""
        from alejandria.knowledge.pagerank import _power_iteration_ppr

        G = self._build_simple_graph()
        scores = _power_iteration_ppr(G, seed_ids=[1], alpha=1.0)

        assert abs(scores[1] - 1.0) < 1e-4
        for nid, s in scores.items():
            if nid != 1:
                assert abs(s) < 1e-4

    def test_pagerank_multiple_seeds(self) -> None:
        """Multiple seeds should split initial probability."""
        from alejandria.knowledge.pagerank import _power_iteration_ppr

        import networkx as nx

        G = nx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5), (4, 6)])
        scores = _power_iteration_ppr(G, seed_ids=[1, 6], alpha=0.5)

        assert scores[1] > scores[3]
        assert scores[6] > scores[3]


# ---------------------------------------------------------------------------
# Integration tests (require live Postgres)
# ---------------------------------------------------------------------------

psycopg = pytest.importorskip("psycopg")


def _pg_reachable() -> bool:
    from alejandria.storage.postgres.connection import get_connection

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM entities")
                n = cur.fetchone()[0]
        return n > 100
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _pg_reachable(),
    reason="Postgres not reachable or entities empty",
)


class TestPPRIntegration:
    """Test PPR against the live Alejandría KG."""

    def test_pagerank_search_returns_results(self) -> None:
        """PPR should return ranked entities for known query entities."""
        from alejandria.knowledge.pagerank import pagerank_search

        results = pagerank_search(
            query_entities=["Nephi"],
            alpha=0.5,
            top_k=10,
        )
        assert isinstance(results, list)
        assert len(results) > 0
        assert all("name" in r for r in results)
        assert all("pagerank_score" in r for r in results)

    def test_pagerank_search_empty_query(self) -> None:
        """Empty query entities should return empty list."""
        from alejandria.knowledge.pagerank import pagerank_search

        results = pagerank_search(query_entities=[], top_k=10)
        assert results == []

    def test_pagerank_search_unknown_entity(self) -> None:
        """Unknown entity should return empty list."""
        from alejandria.knowledge.pagerank import pagerank_search

        results = pagerank_search(
            query_entities=["NonexistentEntityXYZ123"],
            top_k=10,
        )
        assert results == []

    def test_pagerank_scores_decrease(self) -> None:
        """Results should be sorted by descending PPR score."""
        from alejandria.knowledge.pagerank import pagerank_search

        results = pagerank_search(
            query_entities=["Lehi"],
            alpha=0.5,
            top_k=20,
        )
        if len(results) > 1:
            scores = [r["pagerank_score"] for r in results]
            assert scores == sorted(scores, reverse=True)

    def test_pagerank_top_k_limit(self) -> None:
        """Results should respect top_k limit."""
        from alejandria.knowledge.pagerank import pagerank_search

        results = pagerank_search(
            query_entities=["Nephi"],
            alpha=0.5,
            top_k=5,
        )
        assert len(results) <= 5

    def test_pagerank_with_multiple_seeds(self) -> None:
        """Multiple query entities should work."""
        from alejandria.knowledge.pagerank import pagerank_search

        results = pagerank_search(
            query_entities=["Nephi", "Lehi"],
            alpha=0.5,
            top_k=10,
        )
        assert isinstance(results, list)
        if results:
            assert all("name" in r for r in results)

    def test_endpoint_pagerank(self) -> None:
        """POST /search/graph/pagerank should return valid JSON."""
        import requests

        base = "http://localhost:4300"
        try:
            resp = requests.post(
                f"{base}/search/graph/pagerank",
                json={"query_entities": ["Nephi"], "top_k": 5},
                timeout=30,
            )
        except requests.ConnectionError:
            pytest.skip("API not running on localhost:4300")

        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert "count" in data
        assert data["count"] == len(data["results"])
