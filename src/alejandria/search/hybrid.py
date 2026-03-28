"""Hybrid search combining textual and semantic results using Reciprocal Rank Fusion."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HybridSearchResult:
    chunk_id: int
    text: str
    combined_score: float
    text_score: float | None
    semantic_score: float | None
    file_path: str
    chunk_index: int
    metadata: dict
    reference: str | None = None


def reciprocal_rank_fusion(
    text_results: list[dict],
    semantic_results: list[dict],
    text_weight: float = 0.4,
    semantic_weight: float = 0.6,
    k: int = 60,
    limit: int = 20,
) -> list[HybridSearchResult]:
    """Combine text and semantic results using weighted Reciprocal Rank Fusion.

    RRF score for a document d: weight * 1/(k + rank(d))
    """
    scores: dict[int, dict] = {}

    # Score text results
    for rank, r in enumerate(text_results):
        cid = r["chunk_id"]
        rrf = text_weight * (1.0 / (k + rank + 1))
        if cid not in scores:
            scores[cid] = {
                "text": r["text"],
                "file_path": r["file_path"],
                "chunk_index": r["chunk_index"],
                "metadata": r["metadata"],
                "reference": r.get("reference"),
                "text_score": r["score"],
                "semantic_score": None,
                "combined": 0.0,
            }
        scores[cid]["combined"] += rrf
        scores[cid]["text_score"] = r["score"]

    # Score semantic results
    for rank, r in enumerate(semantic_results):
        cid = r["chunk_id"]
        rrf = semantic_weight * (1.0 / (k + rank + 1))
        if cid not in scores:
            scores[cid] = {
                "text": r["text"],
                "file_path": r["file_path"],
                "chunk_index": r["chunk_index"],
                "metadata": r["metadata"],
                "reference": r.get("reference"),
                "text_score": None,
                "semantic_score": r["score"],
                "combined": 0.0,
            }
        scores[cid]["combined"] += rrf
        if scores[cid]["semantic_score"] is None:
            scores[cid]["semantic_score"] = r["score"]

    # Sort by combined score descending
    sorted_items = sorted(scores.items(), key=lambda x: x[1]["combined"], reverse=True)

    return [
        HybridSearchResult(
            chunk_id=cid,
            text=data["text"],
            combined_score=data["combined"],
            text_score=data["text_score"],
            semantic_score=data["semantic_score"],
            file_path=data["file_path"],
            chunk_index=data["chunk_index"],
            metadata=data["metadata"],
            reference=data.get("reference"),
        )
        for cid, data in sorted_items[:limit]
    ]
