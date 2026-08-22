"""Personalized PageRank (PPR) over the existing Alejandría knowledge graph.

Design goals:
- Zero new infrastructure: reads from Postgres via ``get_connection()``.
- Zero LLM calls at query time: pure graph algorithm.
- Drop-in for multi-hop retrieval in ``chat_ask`` or as an experimental MCP tool.

Implementation choice (Phase 1):
    In-memory NetworkX graph loaded from ``relations`` table.
    Prototype-first: measure graph size and latency before considering
    a stored-procedure / CTE-based implementation.

Future (Phase 2):
    - CTE recursiva en Postgres si el grafo supera ~500K nodos.
    - Peso de aristas por ``confidence`` y ``category``.
    - Integración con ``search_hybrid`` como vector seed → graph expansion.
"""

from __future__ import annotations

import logging
from typing import Sequence

import networkx as nx

from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_graph_from_postgres(
    src_ids: Sequence[int] | None = None,
    max_edges: int = 2_000_000,
) -> nx.Graph:
    """Load an undirected NetworkX graph from Postgres ``relations``.

    Args:
        src_ids: Optional list of entity ids to restrict the subgraph.
            If provided, only edges where src_id OR dst_id is in this list
            are loaded (plus one extra hop is fetched implicitly by loading
            all incident edges).
        max_edges: Safety cap to prevent OOM on unexpectedly large graphs.

    Returns:
        Undirected NetworkX graph where node = entity id, edge = relation.
    """
    G = nx.Graph()

    with get_connection() as conn:
        with conn.cursor() as cur:
            if src_ids:
                cur.execute(
                    "SELECT src_id, dst_id FROM relations "
                    "WHERE src_id = ANY(%s) OR dst_id = ANY(%s) "
                    "LIMIT %s",
                    (list(src_ids), list(src_ids), max_edges),
                )
            else:
                cur.execute(
                    "SELECT src_id, dst_id FROM relations LIMIT %s",
                    (max_edges,),
                )
            rows = cur.fetchall()

    for src_id, dst_id in rows:
        G.add_edge(src_id, dst_id)

    logger.info("Loaded PPR graph: %d nodes, %d edges", G.number_of_nodes(), G.number_of_edges())
    return G


def _resolve_entity_ids(names: Sequence[str]) -> list[int]:
    """Resolve entity names to ids via gazetteer + ILIKE fallback."""
    from alejandria.knowledge.gazetteer_lookup import is_canonical

    resolved: list[str] = []
    for name in names:
        if not name or not name.strip():
            continue
        hit = is_canonical(name)
        resolved.append(hit[0] if hit else name.strip())

    if not resolved:
        return []

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM entities WHERE name = ANY(%s)",
                (resolved,),
            )
            return [row[0] for row in cur.fetchall()]


def _chunks_for_entity_ids(entity_ids: Sequence[int], limit: int = 50) -> dict[int, list[str]]:
    """Map entity_id -> list of chunk texts mentioning that entity.

    Returns dict keyed by entity_id, values are lists of chunk text strings.
    """
    if not entity_ids:
        return {}

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT m.entity_id, c.text "
                "FROM entity_document_mentions m "
                "JOIN chunks c ON c.id = m.chunk_id "
                "WHERE m.entity_id = ANY(%s) "
                "LIMIT %s",
                (list(entity_ids), limit * len(entity_ids)),
            )
            rows = cur.fetchall()

    result: dict[int, list[str]] = {}
    for eid, text in rows:
        result.setdefault(eid, []).append(text)
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def pagerank_search(
    query_entities: Sequence[str],
    alpha: float = 0.5,
    max_iter: int = 20,
    tol: float = 1e-6,
    top_k: int = 20,
    max_edges: int = 2_000_000,
) -> list[dict]:
    """Run Personalized PageRank on the Alejandría knowledge graph.

    Args:
        query_entities: Entity names extracted from the user query.
        alpha: Damping factor (default 0.5).
        max_iter: Maximum power-iterations.
        tol: Convergence tolerance on L1 diff.
        top_k: Number of top-scoring entities to return.
        max_edges: Safety cap on edges loaded from Postgres.

    Returns:
        List of {entity_id, name, entity_type, pagerank_score, chunk_count}.
    """
    if not query_entities:
        return []

    seed_ids = _resolve_entity_ids(query_entities)
    if not seed_ids:
        logger.warning("PPR: no entity ids resolved for query %s", query_entities)
        return []

    # Load graph restricted to seed neighborhood.
    G = _load_graph_from_postgres(src_ids=seed_ids, max_edges=max_edges)
    if G.number_of_nodes() == 0:
        return []

    # Build personalization vector.
    personalization = {nid: 0.0 for nid in G.nodes()}
    for sid in seed_ids:
        if sid in personalization:
            personalization[sid] = 1.0 / len(seed_ids)

    # Power iteration PPR.
    scores = nx.pagerank(
        G,
        alpha=alpha,
        personalization=personalization,
        max_iter=max_iter,
        tol=tol,
        weight="weight",
    )

    # Rank and take top_k (excluding seeds themselves if desired).
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    # Fetch names + types for the ranked ids.
    ranked_ids = [eid for eid, _ in ranked]
    if not ranked_ids:
        return []

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, entity_type FROM entities WHERE id = ANY(%s)",
                (ranked_ids,),
            )
            id_info = {row[0]: {"name": row[1], "entity_type": row[2]} for row in cur.fetchall()}

    # Fetch chunk counts.
    chunks_map = _chunks_for_entity_ids(ranked_ids, limit=50)

    results = []
    for eid, score in ranked:
        info = id_info.get(eid, {"name": str(eid), "entity_type": "unknown"})
        results.append({
            "entity_id": eid,
            "name": info["name"],
            "entity_type": info["entity_type"],
            "pagerank_score": round(score, 6),
            "chunk_count": len(chunks_map.get(eid, [])),
        })

    return results
