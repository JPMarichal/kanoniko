"""Index management API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends

from alejandria.api.schemas import (
    IndexStatusResponse,
    IndexTriggerRequest,
    IndexingStatsResponse,
)
from alejandria.api.dependencies import get_pipeline, get_registry, get_textual_search
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
