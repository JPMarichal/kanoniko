"""Knowledge graph search API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from alejandria.api.dependencies import get_neo4j_client, get_profile_store
from alejandria.api.schemas import (
    EntityProfileListResponse,
    EntityProfileResponse,
    GraphDocsResponse,
    GraphEdgeItem,
    GraphNeighborsRequest,
    GraphNeighborsResponse,
    GraphNodeItem,
    GraphSearchRequest,
    GraphSearchResponse,
    GraphSummaryResponse,
    ParallelPassageItem,
    ParallelPassagesRequest,
    ParallelPassagesResponse,
    TypedRelationItem,
    TypedRelationsRequest,
    TypedRelationsResponse,
)

router = APIRouter(prefix="/search/graph", tags=["graph"])


def _require_neo4j(neo4j=Depends(get_neo4j_client)):
    if neo4j is None:
        raise HTTPException(503, "Knowledge graph is not available (Neo4j not connected)")
    return neo4j


@router.post("/find", response_model=GraphSearchResponse)
def graph_find(
    req: GraphSearchRequest,
    neo4j=Depends(_require_neo4j),
) -> GraphSearchResponse:
    """Search for entities by name (partial match)."""
    results = neo4j.find_node(
        search=req.query,
        entity_type=req.entity_type,
        limit=req.limit,
    )
    return GraphSearchResponse(
        query=req.query,
        count=len(results),
        results=[
            GraphNodeItem(
                name=r["name"],
                type=r["type"],
                aliases=r.get("aliases"),
            )
            for r in results
        ],
    )


@router.post("/neighbors", response_model=GraphNeighborsResponse)
def graph_neighbors(
    req: GraphNeighborsRequest,
    neo4j=Depends(_require_neo4j),
) -> GraphNeighborsResponse:
    """Get neighboring nodes and edges for an entity."""
    result = neo4j.get_neighbors(
        name=req.name,
        depth=req.depth,
        relation_types=req.relation_types,
        limit=req.limit,
    )
    return GraphNeighborsResponse(
        name=req.name,
        nodes=[
            GraphNodeItem(name=n["name"], type=n.get("type", "unknown"))
            for n in result["nodes"]
        ],
        edges=[
            GraphEdgeItem(
                source=e.get("from", ""),
                relation=e.get("type", ""),
                target=e.get("to", ""),
                properties=e.get("properties"),
            )
            for e in result["edges"]
        ],
    )


@router.post("/relations", response_model=TypedRelationsResponse)
def graph_typed_relations(
    req: TypedRelationsRequest,
    neo4j=Depends(_require_neo4j),
) -> TypedRelationsResponse:
    """Get typed relations for an entity, filtered by confidence and type."""
    results = neo4j.get_typed_relations(
        entity_name=req.name,
        confidence_min=req.confidence_min,
        rel_types=req.rel_types,
        limit=req.limit,
    )
    return TypedRelationsResponse(
        name=req.name,
        count=len(results),
        relations=[
            TypedRelationItem(
                from_name=r["from_name"],
                from_type=r["from_type"],
                rel_type=r["rel_type"],
                to_name=r["to_name"],
                to_type=r["to_type"],
                properties=r.get("props"),
            )
            for r in results
        ],
    )


@router.post("/parallels", response_model=ParallelPassagesResponse)
def graph_parallels(
    req: ParallelPassagesRequest,
    neo4j=Depends(_require_neo4j),
) -> ParallelPassagesResponse:
    """Find parallel passages for a scripture chapter."""
    results = neo4j.get_parallel_passages(
        file_path=req.file_path,
        layer=req.layer,
        limit=req.limit,
    )
    return ParallelPassagesResponse(
        file_path=req.file_path,
        count=len(results),
        parallels=[
            ParallelPassageItem(
                file_path=r["file_path"],
                narrative=r.get("narrative"),
                layer=r.get("layer"),
                rel_type=r.get("rel_type"),
            )
            for r in results
        ],
    )


@router.get("/summary", response_model=GraphSummaryResponse)
def graph_summary(
    neo4j=Depends(_require_neo4j),
) -> GraphSummaryResponse:
    """Get overall knowledge graph statistics."""
    summary = neo4j.graph_summary()
    return GraphSummaryResponse(**summary)


@router.get("/docs/{entity_name}", response_model=GraphDocsResponse)
def graph_docs(
    entity_name: str,
    neo4j=Depends(_require_neo4j),
) -> GraphDocsResponse:
    """Find documents that mention a specific entity."""
    docs = neo4j.get_documents_for_entity(entity_name)
    return GraphDocsResponse(entity=entity_name, documents=docs)


@router.get("/profile/{entity_name}", response_model=EntityProfileResponse)
def entity_profile(
    entity_name: str,
    entity_type: str | None = None,
    profile_store=Depends(get_profile_store),
):
    """Get the entity profile for a named entity."""
    if profile_store is None:
        raise HTTPException(503, "Profile store is not available")
    profile = profile_store.get_profile(entity_name, entity_type)
    if profile is None:
        raise HTTPException(404, f"No profile found for '{entity_name}'")
    return EntityProfileResponse(**profile.to_dict())


@router.get("/profiles", response_model=EntityProfileListResponse)
def list_profiles(
    entity_type: str | None = None,
    status: str | None = None,
    min_mentions: int = 0,
    limit: int = 50,
    offset: int = 0,
    search: str | None = None,
    profile_store=Depends(get_profile_store),
):
    """List entity profiles with optional filters."""
    if profile_store is None:
        raise HTTPException(503, "Profile store is not available")
    if search:
        profiles = profile_store.find_profiles(search, entity_type, limit)
    else:
        profiles = profile_store.get_all(entity_type, status, min_mentions, limit, offset)
    return EntityProfileListResponse(
        count=len(profiles),
        profiles=[EntityProfileResponse(**p.to_dict()) for p in profiles],
    )


@router.get("/ner-candidates")
def list_ner_candidates(
    min_frequency: int = 3,
    entity_type: str | None = None,
    limit: int = 50,
):
    """List top NER-discovered entity candidates for gazetteer promotion."""
    from alejandria.knowledge.ner_candidates import NERCandidateTracker
    try:
        tracker = NERCandidateTracker()
        candidates = tracker.get_top_candidates(
            min_frequency=min_frequency,
            entity_type=entity_type,
            limit=limit,
        )
        stats = tracker.get_stats()
        return {"candidates": candidates, "stats": stats}
    except Exception as e:
        raise HTTPException(500, f"NER candidate tracking not available: {e}")


@router.post("/ner-candidates/{name}/promote")
def promote_ner_candidate(name: str, entity_type: str):
    """Promote an NER candidate to gazetteer status."""
    from alejandria.knowledge.ner_candidates import NERCandidateTracker
    try:
        tracker = NERCandidateTracker()
        success = tracker.promote(name, entity_type)
        if not success:
            raise HTTPException(404, f"Candidate '{name}' ({entity_type}) not found")
        return {"status": "promoted", "name": name, "type": entity_type}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/ner-candidates/{name}/dismiss")
def dismiss_ner_candidate(name: str, entity_type: str):
    """Dismiss an NER candidate (mark as not useful)."""
    from alejandria.knowledge.ner_candidates import NERCandidateTracker
    try:
        tracker = NERCandidateTracker()
        success = tracker.dismiss(name, entity_type)
        if not success:
            raise HTTPException(404, f"Candidate '{name}' ({entity_type}) not found")
        return {"status": "dismissed", "name": name, "type": entity_type}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
