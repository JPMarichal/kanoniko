"""Index management API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from alejandria.api.schemas import (
    BuildProfilesRequest,
    BuildProfilesResponse,
    IndexStatusResponse,
    IndexTriggerRequest,
    IndexingStatsResponse,
)
from alejandria.api.dependencies import get_pipeline, get_profile_store, get_registry, get_textual_search
from alejandria.config import settings
from alejandria.ingestion.pipeline import IngestionPipeline
from alejandria.ingestion.registry import DocumentRegistry
from alejandria.search.textual import TextualSearch

router = APIRouter(prefix="/index", tags=["index"])

# Store last run stats
_last_stats: IndexingStatsResponse | None = None


@router.get("/status", response_model=IndexStatusResponse)
def index_status(
    registry: DocumentRegistry = Depends(get_registry),
    textual: TextualSearch = Depends(get_textual_search),
) -> IndexStatusResponse:
    errors = registry.errors()
    return IndexStatusResponse(
        total_documents=registry.count(),
        total_chunks=textual.count_chunks(),
        error_count=len(errors),
        errors=[{"file_path": e.file_path, "last_indexed": e.last_indexed} for e in errors],
    )


@router.post("/trigger", response_model=IndexingStatsResponse)
def trigger_indexing(
    req: IndexTriggerRequest,
    pipeline: IngestionPipeline = Depends(get_pipeline),
) -> IndexingStatsResponse:
    stats = pipeline.run(full_reindex=req.full_reindex)
    return IndexingStatsResponse(
        new_files=stats.new_files,
        updated_files=stats.updated_files,
        deleted_files=stats.deleted_files,
        errors=stats.errors,
        total_chunks=stats.total_chunks,
    )


@router.post("/rebuild-kg")
def rebuild_kg(
    pipeline: IngestionPipeline = Depends(get_pipeline),
) -> dict:
    """Rebuild the knowledge graph from already-indexed chunks.

    Much faster than full reindex — skips parsing, chunking, embeddings.
    Only re-runs the KG extractor with current gazetteers against existing
    chunk text in SQLite. Use after expanding gazetteers.
    """
    return pipeline.rebuild_kg()


@router.post("/build-profiles", response_model=BuildProfilesResponse)
def build_profiles(
    req: BuildProfilesRequest,
    pipeline: IngestionPipeline = Depends(get_pipeline),
) -> BuildProfilesResponse:
    """Build entity profiles from the knowledge graph.

    Phase 'metadata': aggregate mention counts, books, key passages ($0 cost).
    Phase 'generate': LLM-generated summaries and disambiguation (future).
    """
    if req.phase == "metadata":
        result = pipeline.build_metadata_profiles(
            entity_types=req.entity_types,
            max_entities=req.max_entities,
            max_passages=settings.profile_max_passages,
        )
        if "error" in result:
            raise HTTPException(503, result["error"])
        return BuildProfilesResponse(**result)
    elif req.phase == "generate":
        profile_store = get_profile_store()
        if profile_store is None:
            raise HTTPException(503, "ProfileStore not available")
        from alejandria.knowledge.profile_generator import ProfileGenerator
        generator = ProfileGenerator(profile_store, tier=settings.profile_llm_tier)
        result = generator.generate_batch(
            entity_types=req.entity_types,
            max_entities=req.max_entities or 50,
            force=req.force,
        )
        return BuildProfilesResponse(**result)
    else:
        raise HTTPException(400, f"Unknown phase '{req.phase}'. Use 'metadata' or 'generate'.")
