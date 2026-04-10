"""Index management API endpoints.

DESIGN CONTRACT: indexing is always on-demand. No endpoint, hook, or daemon
triggers indexing automatically. Corpus files can be added freely; call
POST /index/ingest (targeted) or POST /index/trigger (full scan) only when
explicitly ready to index. This separation allows bulk corpus accumulation
before paying the indexing cost.
"""

from __future__ import annotations

import logging
import threading

from fastapi import APIRouter, Depends, HTTPException

from alejandria.api.schemas import (
    BuildProfilesRequest,
    BuildProfilesResponse,
    IndexIngestRequest,
    IndexStatusResponse,
    IndexTriggerRequest,
    IndexingStatsResponse,
)
from alejandria.api.dependencies import get_pipeline, get_profile_store, get_registry, get_textual_search
from alejandria.config import settings
from alejandria.ingestion.pipeline import IngestionPipeline
from alejandria.ingestion.registry import DocumentRegistry
from alejandria.search.textual import TextualSearch

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/index", tags=["index"])


@router.get("/status", response_model=IndexStatusResponse)
def index_status(
    registry: DocumentRegistry = Depends(get_registry),
    textual: TextualSearch = Depends(get_textual_search),
    pipeline: IngestionPipeline = Depends(get_pipeline),
) -> IndexStatusResponse:
    errors = registry.errors()
    progress = pipeline.progress
    return IndexStatusResponse(
        total_documents=registry.count(),
        total_chunks=textual.count_chunks(),
        error_count=len(errors),
        errors=[{"file_path": e.file_path, "last_indexed": e.last_indexed} for e in errors],
        indexing=progress.running,
        current_file=progress.current_file if progress.running else None,
        files_processed=progress.files_processed,
        files_total=progress.files_total,
        percent=progress.percent,
        elapsed_seconds=progress.elapsed,
        eta_seconds=progress.eta_seconds,
        phase=progress.phase,
        phase_name=progress.phase_name,
        phase_percent=progress.phase_percent,
        phase_elapsed_seconds=progress.phase_elapsed,
        phase_2_chunks=progress.phase_2_chunks,
        phase_3_done=progress.phase_3_done,
        phase_3_total=progress.phase_3_total,
        phase_3_chunks_done=progress.phase_3_chunks_done,
        phase_3_chunks_total=progress.phase_3_chunks_total,
    )


@router.post("/trigger")
def trigger_indexing(
    req: IndexTriggerRequest,
    pipeline: IngestionPipeline = Depends(get_pipeline),
) -> dict:
    """Launch indexing in background. Returns immediately.

    Returns 409 if indexing is already running.
    Poll GET /index/status for progress.
    """
    if pipeline.progress.running:
        raise HTTPException(
            status_code=409,
            detail="Indexing already in progress. Poll GET /index/status for progress.",
        )

    def _run_in_background():
        try:
            pipeline.run(full_reindex=req.full_reindex)
        except RuntimeError as e:
            logger.warning("Indexing rejected: %s", e)
        except Exception:
            logger.exception("Background indexing failed")
            pipeline.progress.error_message = "Indexing failed — check server logs"
            pipeline.progress.running = False

    thread = threading.Thread(target=_run_in_background, daemon=True, name="indexing")
    thread.start()

    return {
        "status": "started",
        "full_reindex": req.full_reindex,
        "message": "Indexing launched in background. Poll GET /index/status for progress.",
    }


@router.post("/ingest")
def ingest_paths(
    req: IndexIngestRequest,
    pipeline: IngestionPipeline = Depends(get_pipeline),
) -> dict:
    """Index specific files or directories without scanning the full corpus.

    Much faster than /trigger for small additions — resolves only the given
    paths instead of hashing every file in the corpus.

    Returns 409 if indexing is already running.
    Poll GET /index/status for progress.
    """
    if pipeline.progress.running:
        raise HTTPException(
            status_code=409,
            detail="Indexing already in progress. Poll GET /index/status for progress.",
        )

    def _run_in_background():
        try:
            pipeline.ingest_paths(req.paths, force=req.force, skip_kg=req.skip_kg, kg_flush_interval=req.kg_flush_interval)
        except RuntimeError as e:
            logger.warning("Ingest rejected: %s", e)
        except Exception:
            logger.exception("Targeted ingest failed")
            pipeline.progress.error_message = "Ingest failed — check server logs"
            pipeline.progress.running = False

    thread = threading.Thread(target=_run_in_background, daemon=True, name="ingest-paths")
    thread.start()

    return {
        "status": "started",
        "paths": req.paths,
        "message": "Targeted ingest launched. Poll GET /index/status for progress.",
    }


@router.post("/rebuild-vectors")
def rebuild_vectors(
    pipeline: IngestionPipeline = Depends(get_pipeline),
) -> dict:
    """Rebuild semantic vectors from already-indexed chunks in SQLite.

    Reads chunk text from SQLite, batch-encodes on GPU, upserts to sqlite-vec.
    No filesystem I/O — ideal for GPU migration or after model change.
    """
    if pipeline.progress.running:
        raise HTTPException(409, "Indexing already in progress.")

    def _run_in_background():
        try:
            pipeline.progress.running = True
            pipeline.progress.start_time = __import__("time").time()
            pipeline.rebuild_vectors()
        except Exception:
            logger.exception("Vector rebuild failed")
        finally:
            pipeline.progress.running = False

    thread = threading.Thread(target=_run_in_background, daemon=True, name="rebuild-vectors")
    thread.start()
    return {"status": "started", "message": "Vector rebuild launched. Poll GET /index/status."}


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


@router.post("/load-curated-relations")
def load_curated_relations(
    migrate: bool = False,
) -> dict:
    """Load curated relations from gazetteers/relations.json into Neo4j.

    Also migrates existing untyped relations (RELATED_TO, CO_OCCURS_WITH)
    to co_occurrence confidence when migrate=True.
    """
    from alejandria.api.dependencies import get_neo4j_client
    from alejandria.knowledge.extractor import _RELATIONS_PATH

    neo4j = get_neo4j_client()
    if neo4j is None:
        raise HTTPException(503, "Neo4j not available")

    try:
        migration_counts = {}
        if migrate:
            migration_counts = neo4j.migrate_untyped_relations() or {}

        if not _RELATIONS_PATH.exists():
            raise HTTPException(404, f"Relations file not found: {_RELATIONS_PATH}")

        counts = neo4j.load_curated_relations(_RELATIONS_PATH)
        total = sum(counts.values())
        populated = {k: v for k, v in counts.items() if v > 0}

        return {
            "status": "ok",
            "total_relations_loaded": total,
            "types_populated": len(populated),
            "counts": populated,
            **({"migrated": migration_counts} if migration_counts else {}),
        }
    finally:
        neo4j.close()


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
            entity_names=req.entity_names,
        )
        return BuildProfilesResponse(**result)
    else:
        raise HTTPException(400, f"Unknown phase '{req.phase}'. Use 'metadata' or 'generate'.")
