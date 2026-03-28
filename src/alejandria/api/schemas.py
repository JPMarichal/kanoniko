"""Pydantic request/response models for the API."""

from __future__ import annotations

from pydantic import BaseModel, Field


# --- Search ---

class TextSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query text")
    limit: int = Field(20, ge=1, le=100)
    source_filter: str | None = Field(None, description="Filter by corpus subdirectory")


class SearchResultItem(BaseModel):
    chunk_id: int
    text: str
    score: float
    file_path: str
    chunk_index: int
    metadata: dict


class SearchResponse(BaseModel):
    query: str
    mode: str
    count: int
    results: list[SearchResultItem]


class HybridSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(20, ge=1, le=100)
    source_filter: str | None = None
    text_weight: float = Field(0.4, ge=0.0, le=1.0)
    semantic_weight: float = Field(0.6, ge=0.0, le=1.0)


class HybridResultItem(BaseModel):
    chunk_id: int
    text: str
    combined_score: float
    text_score: float | None
    semantic_score: float | None
    file_path: str
    chunk_index: int
    metadata: dict


class HybridSearchResponse(BaseModel):
    query: str
    mode: str
    count: int
    results: list[HybridResultItem]


# --- Indexing ---

class IndexTriggerRequest(BaseModel):
    full_reindex: bool = False


class IndexingStatsResponse(BaseModel):
    new_files: int
    updated_files: int
    deleted_files: int
    errors: int
    total_chunks: int


class IndexStatusResponse(BaseModel):
    total_documents: int
    total_chunks: int
    error_count: int
    errors: list[dict]


# --- Documents ---

class DocumentListItem(BaseModel):
    file_path: str
    sha256: str
    file_size: int
    chunk_count: int
    last_indexed: str
    status: str


class DocumentListResponse(BaseModel):
    count: int
    documents: list[DocumentListItem]


# --- Health ---

class HealthResponse(BaseModel):
    status: str
    version: str
    fts_documents: int
    fts_chunks: int
    semantic_available: bool
    semantic_vectors: int | None = None
