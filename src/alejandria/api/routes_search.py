"""Search API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from alejandria.api.dependencies import get_semantic_search, get_textual_search
from alejandria.api.schemas import (
    HybridResultItem,
    HybridSearchRequest,
    HybridSearchResponse,
    SearchResponse,
    SearchResultItem,
    TextSearchRequest,
)
from alejandria.search.textual import TextualSearch

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/text", response_model=SearchResponse)
def search_text(
    req: TextSearchRequest,
    textual: TextualSearch = Depends(get_textual_search),
) -> SearchResponse:
    results = textual.search(
        query=req.query,
        limit=req.limit,
        file_path_filter=req.source_filter,
    )
    return SearchResponse(
        query=req.query,
        mode="text",
        count=len(results),
        results=[
            SearchResultItem(
                chunk_id=r.chunk_id,
                text=r.text,
                score=r.score,
                file_path=r.file_path,
                chunk_index=r.chunk_index,
                metadata=r.metadata,
                reference=r.reference,
            )
            for r in results
        ],
    )


@router.post("/semantic", response_model=SearchResponse)
def search_semantic(
    req: TextSearchRequest,
    semantic=Depends(get_semantic_search),
) -> SearchResponse:
    if semantic is None:
        raise HTTPException(503, "Semantic search is not available (sqlite-vec not loaded)")

    from alejandria.embeddings.model import encode_single

    query_vector = encode_single(req.query).tolist()
    results = semantic.search(
        query_vector=query_vector,
        limit=req.limit,
        source_filter=req.source_filter,
    )
    return SearchResponse(
        query=req.query,
        mode="semantic",
        count=len(results),
        results=[
            SearchResultItem(
                chunk_id=r.chunk_id,
                text=r.text,
                score=r.score,
                file_path=r.file_path,
                chunk_index=r.chunk_index,
                metadata=r.metadata,
                reference=r.reference,
            )
            for r in results
        ],
    )


@router.post("/hybrid", response_model=HybridSearchResponse)
def search_hybrid(
    req: HybridSearchRequest,
    textual: TextualSearch = Depends(get_textual_search),
    semantic=Depends(get_semantic_search),
) -> HybridSearchResponse:
    if semantic is None:
        raise HTTPException(503, "Hybrid search requires semantic search (sqlite-vec not loaded)")

    from alejandria.embeddings.model import encode_single
    from alejandria.search.hybrid import reciprocal_rank_fusion

    # Fetch more than limit from each source for better fusion
    fetch_limit = min(req.limit * 3, 100)

    # Text results
    text_results = textual.search(query=req.query, limit=fetch_limit, file_path_filter=req.source_filter)
    text_dicts = [
        {"chunk_id": r.chunk_id, "text": r.text, "score": r.score,
         "file_path": r.file_path, "chunk_index": r.chunk_index, "metadata": r.metadata,
         "reference": r.reference}
        for r in text_results
    ]

    # Semantic results
    query_vector = encode_single(req.query).tolist()
    sem_results = semantic.search(query_vector=query_vector, limit=fetch_limit, source_filter=req.source_filter)
    sem_dicts = [
        {"chunk_id": r.chunk_id, "text": r.text, "score": r.score,
         "file_path": r.file_path, "chunk_index": r.chunk_index, "metadata": r.metadata,
         "reference": r.reference}
        for r in sem_results
    ]

    # Fuse
    fused = reciprocal_rank_fusion(
        text_results=text_dicts,
        semantic_results=sem_dicts,
        text_weight=req.text_weight,
        semantic_weight=req.semantic_weight,
        limit=req.limit,
    )

    return HybridSearchResponse(
        query=req.query,
        mode="hybrid",
        count=len(fused),
        results=[
            HybridResultItem(
                chunk_id=r.chunk_id,
                text=r.text,
                combined_score=r.combined_score,
                text_score=r.text_score,
                semantic_score=r.semantic_score,
                file_path=r.file_path,
                chunk_index=r.chunk_index,
                metadata=r.metadata,
                reference=r.reference,
            )
            for r in fused
        ],
    )
