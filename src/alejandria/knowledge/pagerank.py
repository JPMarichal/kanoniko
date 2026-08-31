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
import time
from typing import Sequence

import networkx as nx

from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Graph cache (full graph, TTL-based invalidation)
# ---------------------------------------------------------------------------

_graph_cache: tuple[float, nx.Graph] | None = None
_GRAPH_CACHE_TTL = 300  # seconds (5 minutes)


def _get_cached_graph(max_edges: int = 2_000_000) -> nx.Graph:
    """Return the full KG graph, cached for _GRAPH_CACHE_TTL seconds."""
    global _graph_cache
    now = time.time()

    if _graph_cache is not None:
        ts, G = _graph_cache
        if now - ts < _GRAPH_CACHE_TTL:
            logger.debug("PPR cache hit (age=%.1fs)", now - ts)
            return G
        else:
            logger.debug("PPR cache expired (age=%.1fs)", now - ts)
            _graph_cache = None

    logger.info("PPR cache miss — loading full graph from Postgres")
    G = _load_graph_from_postgres(max_edges=max_edges)
    _graph_cache = (now, G)
    return G


def invalidate_pagerank_cache() -> None:
    """Force invalidation of the PPR graph cache."""
    global _graph_cache
    _graph_cache = None
    logger.info("PPR cache invalidated")

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
    if src_ids:
        G_full = _get_cached_graph(max_edges=max_edges)
        # Extract subgraph induced by src_ids and their neighbors
        nodes_to_keep = set(src_ids)
        for nid in src_ids:
            if nid in G_full:
                nodes_to_keep.update(G_full.neighbors(nid))
        G = G_full.subgraph(nodes_to_keep).copy()
        logger.debug("Extracted PPR subgraph: %d nodes, %d edges", G.number_of_nodes(), G.number_of_edges())
        return G

    # Full graph load — bypass cache and query Postgres directly.
    G = nx.Graph()
    with get_connection() as conn:
        with conn.cursor() as cur:
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
    """Resolve entity names to ids via gazetteer + ILIKE fallback.

    Uses the gazetteer's canonical type to disambiguate entities with the
    same name but different types (e.g. "Lehi" the person vs "Lehi" the place).
    """
    from alejandria.knowledge.gazetteer_lookup import is_canonical

    # Build disambiguation map: canonical_name -> preferred_type
    disambig: dict[str, str | None] = {}
    for name in names:
        if not name or not name.strip():
            continue
        hit = is_canonical(name)
        canonical = hit[0] if hit else name.strip()
        preferred_type = hit[1] if hit else None
        disambig[canonical] = preferred_type

    if not disambig:
        return []

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, entity_type FROM entities WHERE name = ANY(%s)",
                (list(disambig.keys()),),
            )
            rows = cur.fetchall()

    # Filter by preferred type when gazetteer provided one.
    # This avoids pulling in same-name entities of the wrong type
    # (e.g. "Lehi" the city when the query meant the prophet Lehi).
    result = []
    for eid, ename, etype in rows:
        preferred = disambig.get(ename)
        if preferred is None or etype == preferred:
            result.append(eid)

    return result


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
                "JOIN chunks c ON c.file_path = m.file_path "
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

def _power_iteration_ppr(
    G: nx.Graph,
    seed_ids: Sequence[int],
    alpha: float = 0.5,
    max_iter: int = 20,
    tol: float = 1e-6,
) -> dict[int, float]:
    """Pure-Python Personalized PageRank via power iteration.

    Args:
        G: Undirected NetworkX graph.
        seed_ids: Entity ids to use as personalization seeds.
        alpha: Damping factor.
        max_iter: Maximum iterations.
        tol: Convergence tolerance on L1 difference.

    Returns:
        Dict mapping node_id -> PPR score.
    """
    nodes = list(G.nodes())
    n = len(nodes)
    if n == 0:
        return {}

    # Map node id -> index for fast array access.
    idx = {node: i for i, node in enumerate(nodes)}

    # Build adjacency list: node -> list of predecessors.
    # For PageRank power iteration: x_new[i] receives from predecessors j.
    predecessors: list[list[int]] = [[] for _ in range(n)]
    for u, v in G.edges():
        iu, iv = idx[u], idx[v]
        predecessors[iv].append(iu)
        predecessors[iu].append(iv)

    # Personalization vector (uniform over seeds).
    p = [0.0] * n
    for sid in seed_ids:
        if sid in idx:
            p[idx[sid]] = 1.0 / len(seed_ids)

    # Initialize scores uniformly.
    scores = [1.0 / n] * n

    for _ in range(max_iter):
        new_scores = [0.0] * n
        for i in range(n):
            if predecessors[i]:
                spread = sum(scores[j] / len(predecessors[j]) for j in predecessors[i])
                new_scores[i] = alpha * p[i] + (1 - alpha) * spread
            else:
                new_scores[i] = alpha * p[i] + (1 - alpha) * (sum(scores) / n)

        # L1 convergence check.
        diff = sum(abs(new_scores[i] - scores[i]) for i in range(n))
        scores = new_scores
        if diff < tol:
            break

    return {nodes[i]: scores[i] for i in range(n)}


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

    # Power iteration PPR (pure Python, no scipy/numpy required).
    scores = _power_iteration_ppr(
        G,
        seed_ids=seed_ids,
        alpha=alpha,
        max_iter=max_iter,
        tol=tol,
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
