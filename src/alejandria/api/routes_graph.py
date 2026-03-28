"""Knowledge graph search API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from alejandria.api.dependencies import get_neo4j_client
from alejandria.api.schemas import (
    GraphDocsResponse,
    GraphEdgeItem,
    GraphNeighborsRequest,
    GraphNeighborsResponse,
    GraphNodeItem,
    GraphSearchRequest,
    GraphSearchResponse,
    GraphSummaryResponse,
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
            )
            for e in result["edges"]
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
