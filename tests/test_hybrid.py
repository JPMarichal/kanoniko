"""Tests for hybrid search (RRF fusion)."""

from alejandria.search.hybrid import reciprocal_rank_fusion


def _make_result(chunk_id: int, score: float, text: str = "text") -> dict:
    return {
        "chunk_id": chunk_id,
        "text": text,
        "score": score,
        "file_path": "test.txt",
        "chunk_index": 0,
        "metadata": {},
    }


def test_rrf_empty() -> None:
    results = reciprocal_rank_fusion([], [])
    assert results == []


def test_rrf_text_only() -> None:
    text_results = [_make_result(1, 5.0), _make_result(2, 3.0)]
    results = reciprocal_rank_fusion(text_results, [])
    assert len(results) == 2
    assert results[0].chunk_id == 1  # Higher ranked


def test_rrf_semantic_only() -> None:
    sem_results = [_make_result(10, 0.95), _make_result(20, 0.80)]
    results = reciprocal_rank_fusion([], sem_results)
    assert len(results) == 2
    assert results[0].chunk_id == 10


def test_rrf_fusion_boosts_overlap() -> None:
    """A chunk appearing in both result sets should rank higher."""
    text_results = [_make_result(1, 5.0), _make_result(2, 3.0)]
    sem_results = [_make_result(2, 0.95), _make_result(3, 0.80)]

    results = reciprocal_rank_fusion(
        text_results, sem_results, text_weight=0.5, semantic_weight=0.5
    )
    # chunk_id=2 appears in both, so should be boosted
    assert results[0].chunk_id == 2
    assert results[0].text_score is not None
    assert results[0].semantic_score is not None


def test_rrf_respects_limit() -> None:
    text_results = [_make_result(i, float(10 - i)) for i in range(10)]
    sem_results = [_make_result(i + 10, 0.9 - i * 0.05) for i in range(10)]

    results = reciprocal_rank_fusion(text_results, sem_results, limit=5)
    assert len(results) == 5


def test_rrf_weights_affect_ranking() -> None:
    """With extreme weights, one source should dominate."""
    text_results = [_make_result(1, 10.0)]
    sem_results = [_make_result(2, 0.99)]

    # Heavy text weight
    results_text_heavy = reciprocal_rank_fusion(
        text_results, sem_results, text_weight=0.99, semantic_weight=0.01
    )
    assert results_text_heavy[0].chunk_id == 1

    # Heavy semantic weight
    results_sem_heavy = reciprocal_rank_fusion(
        text_results, sem_results, text_weight=0.01, semantic_weight=0.99
    )
    assert results_sem_heavy[0].chunk_id == 2
