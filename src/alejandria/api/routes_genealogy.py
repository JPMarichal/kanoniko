"""Genealogy tree and path API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from alejandria.api.dependencies import get_neo4j_client
from alejandria.api.schemas import GenealogyPathResponse, GenealogyTreeResponse

router = APIRouter(prefix="/kg/genealogy", tags=["genealogy"])


def _require_neo4j(neo4j=Depends(get_neo4j_client)):
    if neo4j is None:
        raise HTTPException(503, "Knowledge graph is not available (Neo4j not connected)")
    return neo4j


@router.get("/{person}", response_model=GenealogyTreeResponse)
def genealogy_tree(
    person: str,
    direction: str = Query("both", pattern="^(up|down|both)$"),
    depth: int = Query(3, ge=1, le=10),
    lang: str = Query("en", pattern="^(en|es)$"),
    neo4j=Depends(_require_neo4j),
) -> GenealogyTreeResponse:
    """Get hierarchical family tree for a person.

    - **direction**: ``up`` (ancestors), ``down`` (descendants), or ``both``
    - **depth**: max generations to traverse (1-10)
    - **lang**: ``en`` or ``es`` for bilingual alternate names
    """
    tree = neo4j.get_genealogy_tree(person, direction=direction, depth=depth, lang=lang)
    return GenealogyTreeResponse(person=tree["name"], direction=direction, depth=depth, tree=tree)


@router.get("/{person}/path/{person2}", response_model=GenealogyPathResponse)
def genealogy_path(
    person: str,
    person2: str,
    neo4j=Depends(_require_neo4j),
) -> GenealogyPathResponse:
    """Find shortest family path between two people."""
    result = neo4j.get_genealogy_path(person, person2)
    if result["path_length"] < 0:
        raise HTTPException(404, f"No family path found between '{person}' and '{person2}'")
    return GenealogyPathResponse(**result)
