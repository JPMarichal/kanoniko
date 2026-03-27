"""Search API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from alejandria.api.schemas import SearchResponse, SearchResultItem, TextSearchRequest
from alejandria.api.dependencies import get_textual_search
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
            )
            for r in results
        ],
    )
