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
    reference: str | None = None


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
    reference: str | None = None


class HybridSearchResponse(BaseModel):
    query: str
    mode: str
    count: int
    results: list[HybridResultItem]


# --- Graph Search ---

class GraphSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Entity name to search")
    entity_type: str | None = Field(None, description="Filter by entity type")
    limit: int = Field(20, ge=1, le=100)


class GraphNodeItem(BaseModel):
    name: str
    type: str
    aliases: list[str] | None = None


class GraphEdgeItem(BaseModel):
    source: str  # renamed from 'from' which is a Python keyword
    relation: str
    target: str
    properties: dict | None = None


class TypedRelationItem(BaseModel):
    from_name: str
    from_type: str
    rel_type: str
    to_name: str
    to_type: str
    properties: dict | None = None


class TypedRelationsRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Entity name to query")
    confidence_min: str | None = Field(None, description="Minimum confidence: curated, metadata, llm_high, llm_low, ner, co_occurrence")
    rel_types: list[str] | None = Field(None, description="Filter to specific relation types")
    limit: int = Field(100, ge=1, le=500)


class TypedRelationsResponse(BaseModel):
    name: str
    count: int
    relations: list[TypedRelationItem]


class ParallelPassageItem(BaseModel):
    file_path: str
    narrative: str | None = None
    layer: int | None = None
    rel_type: str | None = None


class ParallelPassagesRequest(BaseModel):
    file_path: str = Field(..., min_length=1, description="Scripture chapter file path")
    layer: int | None = Field(None, ge=1, le=3, description="Filter by layer: 1=narrative, 2=editorial, 3=thematic")
    limit: int = Field(50, ge=1, le=200)


class ParallelPassagesResponse(BaseModel):
    file_path: str
    count: int
    parallels: list[ParallelPassageItem]


class GraphNeighborsRequest(BaseModel):
    name: str = Field(..., min_length=1)
    depth: int = Field(1, ge=1, le=5)
    relation_types: list[str] | None = None
    limit: int = Field(50, ge=1, le=200)


class GraphNeighborsResponse(BaseModel):
    name: str
    nodes: list[GraphNodeItem]
    edges: list[GraphEdgeItem]


class GraphSearchResponse(BaseModel):
    query: str
    count: int
    results: list[GraphNodeItem]


class GraphSummaryResponse(BaseModel):
    total_nodes: int
    total_relationships: int
    nodes_by_type: list[dict]
    relationships_by_type: list[dict]


class GraphDocsResponse(BaseModel):
    entity: str
    documents: list[dict]


# --- Entity Profiles ---

class EntityProfileResponse(BaseModel):
    entity_name: str
    entity_type: str
    mention_count: int
    document_count: int
    books: list[str]
    key_passages: list[dict]
    aliases: list[str]
    disambiguator: str | None = None
    summary_en: str | None = None
    summary_es: str | None = None
    disambiguation_notes: str | None = None
    profile_version: int
    status: str


class EntityProfileListResponse(BaseModel):
    count: int
    profiles: list[EntityProfileResponse]


class BuildProfilesRequest(BaseModel):
    phase: str = Field("metadata", description="Phase to run: 'metadata' or 'generate'")
    entity_types: list[str] | None = Field(None, description="Filter to specific types, e.g. ['person']")
    max_entities: int = Field(0, ge=0, description="Max entities to process. 0 = all")
    force: bool = Field(False, description="Force regeneration even if already profiled (generate phase)")
    entity_names: list[str] | None = Field(None, description="Process specific entities by name (generate phase)")


class BuildProfilesResponse(BaseModel):
    entities_processed: int
    elapsed_seconds: float
    profiles_generated: int | None = None
    disambiguations: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


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


# --- Chat (RAG) ---

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")
    source_filter: str | None = Field(None, description="Filter by corpus subdirectory")
    provider: str | None = Field(None, description="LLM provider override: 'anthropic', 'gemini', 'openai'")
    model: str | None = Field(None, description="LLM model override, e.g. 'gemini-2.5-flash'")
    tier: str | None = Field(None, description="Tier override: 'fast', 'balanced', 'quality', or a model ID")


class ChatSourceItem(BaseModel):
    text: str
    file_path: str
    chunk_index: int
    score: float
    mode: str
    reference: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSourceItem]
    graph_context: str | None = None
    model: str
    tier: str = ""
    input_tokens: int
    output_tokens: int


# --- Health ---

class HealthResponse(BaseModel):
    status: str
    version: str
    fts_documents: int
    fts_chunks: int
    semantic_available: bool
    semantic_vectors: int | None = None
    graph_available: bool
    graph_nodes: int | None = None
