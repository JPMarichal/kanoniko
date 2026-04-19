"""Postgres-backend KG client — drop-in replacement for ``Neo4jClient``.

Scope (Fase 3 part 2a, 2026-04-18): scaffold + 3 initial methods. Remaining
methods raise ``NotImplementedError`` with a pointer to the audit doc §6.4
classification so it's clear what's still pending vs what's intentionally
dropped.

Contract:
    * Same public method names and signatures as ``Neo4jClient`` — callers
      in ``api/routes_*``, ``cli``, ``mcp_server``, ``chat/rag`` don't need
      to change. DI in ``api/dependencies.py`` and the factory below switch
      by ``settings.storage_backend``.
    * Return shapes mirror the Neo4j-backed client (dicts/lists of dicts)
      so ``tests/parity/golden_queries.yaml`` validates both sides.

Audit reference:
    docs/kg-client-port-audit.md §6.4 — inventory + classification of the
    34 methods of the original Neo4j client, with which this module is
    paired 1:1.

Caveats:
    * Queries that filter by ``entity_type`` carry the R10 caveat
      (docs/kg-ingestion-refactor.md): type misclassification is not yet
      resolved, so filter-by-type may miss or mis-include entries.
    * Writes (merge_*, batch_*, clear_all) still need to land for ingestion
      cutover (Fase 4). Reads are the priority for Fase 3.
"""
from __future__ import annotations

import logging
from typing import Any

import psycopg

from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)


# Methods that the audit explicitly DEPRECATEs. Kept here for awareness —
# callers of these in the old code path should be pruned during cutover.
_DEPRECATED = frozenset({
    "_ensure_indexes",          # Postgres DDL covers this; no runtime equivalent
    "migrate_untyped_relations",  # dead code post-R7
})


class PostgresGraphClient:
    """Postgres-backed drop-in replacement for Neo4jClient."""

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    def __init__(self) -> None:
        # Per-call connections via ``get_connection()`` context manager.
        # No persistent session; matches how psycopg is used elsewhere in
        # the codebase. Pool can be added later if we observe connection
        # pressure under load.
        self._driver = self  # attribute parity with Neo4jClient for callers
                              # that pass ``self._neo4j._driver`` to helpers.

    def close(self) -> None:
        """No-op — per-call connections close themselves via context manager."""
        return None

    # ------------------------------------------------------------------ #
    # Reads — Tier 2a: implemented
    # ------------------------------------------------------------------ #

    def graph_summary(self) -> dict[str, Any]:
        """Aggregate counts for the KG. **Same shape as ``Neo4jClient.graph_summary``**.

        Returns:
            dict with ``total_nodes``, ``total_relationships``,
            ``nodes_by_type`` (list of {type, count}),
            ``relationships_by_type`` (list of {type, count}).

        Parity note: the key names match the Neo4j client so callers
        (``api/routes_graph.py``, ``cli.py``, ``mcp_server.py``, ``main.py``)
        consume both backends identically.
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM entities")
                total_nodes = cur.fetchone()[0]

                cur.execute("SELECT count(*) FROM relations")
                total_relationships = cur.fetchone()[0]

                cur.execute(
                    "SELECT entity_type, count(*) FROM entities "
                    "GROUP BY entity_type ORDER BY count(*) DESC"
                )
                nodes_by_type = [
                    {"type": row[0], "count": row[1]} for row in cur.fetchall()
                ]

                cur.execute(
                    "SELECT rel_type, count(*) FROM relations "
                    "GROUP BY rel_type ORDER BY count(*) DESC LIMIT 20"
                )
                relationships_by_type = [
                    {"type": row[0], "count": row[1]} for row in cur.fetchall()
                ]

        return {
            "total_nodes": total_nodes,
            "total_relationships": total_relationships,
            "nodes_by_type": nodes_by_type,
            "relationships_by_type": relationships_by_type,
        }

    def find_node(
        self,
        search: str,
        entity_type: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Find entities by partial-name match against name and aliases.

        Resolution order:
          1. If ``search`` matches a gazetteer alias (``gazetteer_lookup``),
             resolve to the canonical name and use THAT for the DB query.
             This covers cross-language aliases (Nefi → Nephi) and variants
             that live in the gazetteer JSON but not in ``entity_aliases``
             (where only ~100 rows were migrated from Neo4j's embedded aliases).
          2. Fall back to ILIKE on ``entities.name`` + JOIN to
             ``entity_aliases.alias`` with ``pg_trgm`` similarity.

        ``entity_type`` filter carries the R10 caveat (type misclassification
        unresolved — see docs/kg-ingestion-refactor.md).

        Returns:
            list of {id, name, type, disambiguator, score}.
        """
        if not search or not search.strip():
            return []
        needle_raw = search.strip()

        # Step 1: gazetteer resolution. If the user's input is a known alias
        # of a canonical entity, prefer the canonical form for the DB search.
        # Covers both case variants (nefi → Nephi) and cross-language.
        from alejandria.knowledge.gazetteer_lookup import is_canonical
        canonical_hit = is_canonical(needle_raw)
        needle = canonical_hit[0] if canonical_hit else needle_raw

        sql = (
            "SELECT DISTINCT ON (e.id) e.id, e.name, e.entity_type, e.disambiguator, "
            "       GREATEST("
            "         similarity(e.name, %s), "
            "         COALESCE(MAX(similarity(ea.alias, %s)), 0)"
            "       ) AS score "
            "FROM entities e "
            "LEFT JOIN entity_aliases ea ON ea.entity_id = e.id "
            "WHERE (e.name ILIKE %s OR ea.alias ILIKE %s)"
        )
        params: list[Any] = [
            needle, needle,
            f"%{needle}%", f"%{needle}%",
        ]
        if entity_type:
            sql += " AND e.entity_type = %s"
            params.append(entity_type)
        sql += (
            " GROUP BY e.id, e.name, e.entity_type, e.disambiguator "
            "ORDER BY e.id, score DESC LIMIT %s"
        )
        params.append(limit)

        # NOTE: the DISTINCT ON + ORDER BY dance is required because a single
        # entity can match both its name AND multiple aliases; we dedup to
        # one row per entity with the highest score across all matches.
        # Postgres needs the DISTINCT ON column to be first in ORDER BY, so
        # we re-sort in Python after the query.

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

        # Post-sort by score desc (Postgres DISTINCT ON forces initial e.id sort).
        results = [
            {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "disambiguator": row[3],
                "score": float(row[4]) if row[4] is not None else 0.0,
            }
            for row in rows
        ]
        results.sort(key=lambda r: -r["score"])
        return results[:limit]

    # ------------------------------------------------------------------ #
    # Reads — Tier 2b/c/d: NOT YET IMPLEMENTED
    # ------------------------------------------------------------------ #

    def get_neighbors(
        self,
        name: str,
        depth: int = 1,
        relation_types: list[str] | None = None,
        limit: int = 50,
    ) -> dict:
        """Return bidirectional neighbors of ``name`` up to ``depth`` hops.

        Same return shape as ``Neo4jClient.get_neighbors``:
            {"nodes": [{"name", "type"}, ...],
             "edges": [{"from", "type", "to", "properties"}, ...]}

        Implementation:
          * depth=1: single bidirectional JOIN (fast path).
          * depth>1: recursive CTE with hard cap on intermediate rowset
            (pattern per docs/postgres-migration.md §2.3 — prevents blow-up
            on hub entities).
          * ``name`` is first resolved via gazetteer (alias → canonical).

        ``relation_types`` filter maps to SQL ``WHERE r.rel_type = ANY(%s)``.
        """
        if not name or not name.strip():
            return {"nodes": [], "edges": []}

        # Resolve alias to canonical (cross-language / case variants).
        from alejandria.knowledge.gazetteer_lookup import is_canonical
        canonical_hit = is_canonical(name)
        target_name = canonical_hit[0] if canonical_hit else name.strip()

        # Build optional rel_type filter once.
        rt_clause = ""
        rt_params: list[Any] = []
        if relation_types:
            rt_clause = " AND r.rel_type = ANY(%s)"
            rt_params.append(relation_types)

        nodes: dict[int, dict] = {}  # dedup by entity id
        edges: list[dict] = []

        if depth == 1:
            # Fast path: bidirectional JOIN. We emit two shapes of rows:
            #   - where target is src    → edge goes target → dst_entity
            #   - where target is dst    → edge goes src_entity → target
            # ORDER BY confidence ensures curated/metadata results surface
            # first. Without this, LIMIT would arbitrarily cut signal (curated
            # BROTHER_OF, AUTHORED) under noise (llm_low BELONGS_TO/TEACHES),
            # which validated in bench as the reason the first test failed.
            sql = (
                "WITH target AS ("
                "  SELECT id, name, entity_type FROM entities WHERE name = %s LIMIT 1"
                "), "
                "combined AS ( "
                "  SELECT 'out' AS dir, e2.id AS other_id, e2.name AS other_name, "
                "         e2.entity_type AS other_type, r.rel_type, r.properties, r.confidence "
                "  FROM target t JOIN relations r ON r.src_id = t.id "
                "  JOIN entities e2 ON e2.id = r.dst_id "
                f"  WHERE TRUE{rt_clause} "
                "  UNION ALL "
                "  SELECT 'in', e2.id, e2.name, e2.entity_type, r.rel_type, r.properties, r.confidence "
                "  FROM target t JOIN relations r ON r.dst_id = t.id "
                "  JOIN entities e2 ON e2.id = r.src_id "
                f"  WHERE TRUE{rt_clause} "
                ") "
                "SELECT dir, other_id, other_name, other_type, rel_type, properties "
                "FROM combined ORDER BY "
                "  CASE confidence "
                "    WHEN 'curated' THEN 1 "
                "    WHEN 'metadata' THEN 2 "
                "    WHEN 'llm_high' THEN 3 "
                "    WHEN 'llm_low' THEN 4 "
                "    WHEN 'ner' THEN 5 "
                "    ELSE 6 END, "
                "  rel_type "
                "LIMIT %s"
            )
            params: list[Any] = [target_name]
            params.extend(rt_params)  # outgoing filter
            params.extend(rt_params)  # incoming filter (duplicate)
            params.append(limit)

            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    rows = cur.fetchall()

            for row in rows:
                direction, other_id, other_name, other_type, rel_type, props = row
                nodes.setdefault(other_id, {"name": other_name, "type": other_type})
                if direction == "out":
                    edges.append({
                        "from": target_name, "type": rel_type, "to": other_name,
                        "properties": props or {},
                    })
                else:
                    edges.append({
                        "from": other_name, "type": rel_type, "to": target_name,
                        "properties": props or {},
                    })
            return {"nodes": list(nodes.values()), "edges": edges}

        # depth >= 2: recursive CTE with LIMIT intermedio (hub safety).
        # We walk the undirected graph, keeping visited set on the path.
        # Node cap 5000 intermediate to prevent fan-out on highly connected
        # entities; final LIMIT applies to the distinct neighbor set.
        # NOTE: Postgres doesn't accept LIMIT directly in the anchor query of
        # a recursive CTE before UNION ALL; wrap the entity lookup in a CTE.
        sql = (
            "WITH RECURSIVE target_entity AS ( "
            "  SELECT id, name, entity_type FROM entities WHERE name = %s LIMIT 1 "
            "), "
            "bfs AS ( "
            "  SELECT t.id AS target_id, t.id AS node_id, t.name AS node_name, "
            "         t.entity_type AS node_type, 0 AS depth, ARRAY[t.id] AS visited, "
            "         NULL::bigint AS edge_src, NULL::bigint AS edge_dst, "
            "         NULL::text AS edge_type, NULL::jsonb AS edge_props "
            "  FROM target_entity t "
            "  UNION ALL "
            "  SELECT b.target_id, "
            "         CASE WHEN r.src_id = b.node_id THEN r.dst_id ELSE r.src_id END AS node_id, "
            "         e2.name, e2.entity_type, b.depth + 1, b.visited || "
            "           (CASE WHEN r.src_id = b.node_id THEN r.dst_id ELSE r.src_id END), "
            "         r.src_id, r.dst_id, r.rel_type, r.properties "
            "  FROM bfs b "
            "  JOIN relations r "
            "    ON (r.src_id = b.node_id OR r.dst_id = b.node_id) "
            f"   {rt_clause}"
            "  JOIN entities e2 ON e2.id = "
            "    (CASE WHEN r.src_id = b.node_id THEN r.dst_id ELSE r.src_id END) "
            "  WHERE b.depth < %s "
            "    AND NOT (CASE WHEN r.src_id = b.node_id THEN r.dst_id ELSE r.src_id END) "
            "        = ANY(b.visited) "
            "), capped AS (SELECT * FROM bfs LIMIT 5000) "
            "SELECT DISTINCT ON (node_id) node_id, node_name, node_type, "
            "       edge_src, edge_dst, edge_type, edge_props "
            "FROM capped WHERE depth > 0 ORDER BY node_id, depth LIMIT %s"
        )
        params = [target_name]
        params.extend(rt_params)
        params.extend([depth, limit])

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

        # Need a second pass for edge names: edge_src/edge_dst are ids, resolve.
        edge_ids_needed: set[int] = set()
        for row in rows:
            if row[3] is not None:
                edge_ids_needed.add(row[3])
                edge_ids_needed.add(row[4])
            nodes.setdefault(row[0], {"name": row[1], "type": row[2]})

        id_to_name: dict[int, str] = {}
        if edge_ids_needed:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, name FROM entities WHERE id = ANY(%s)",
                        (list(edge_ids_needed),),
                    )
                    for eid, ename in cur.fetchall():
                        id_to_name[eid] = ename

        for row in rows:
            _, _, _, edge_src, edge_dst, edge_type, edge_props = row
            if edge_src is None:
                continue
            edges.append({
                "from": id_to_name.get(edge_src, str(edge_src)),
                "type": edge_type,
                "to": id_to_name.get(edge_dst, str(edge_dst)),
                "properties": edge_props or {},
            })

        return {"nodes": list(nodes.values()), "edges": edges}

    # ------------------------------------------------------------------ #
    # Tier 2c: mentions-based (unblocked by schema v2)
    # ------------------------------------------------------------------ #

    def get_documents_for_entity(self, name: str) -> list[dict]:
        """Documents that mention the entity. Returns [{file_path, source}, ...].

        Same shape as Neo4jClient. Name resolved via gazetteer first.
        """
        from alejandria.knowledge.gazetteer_lookup import is_canonical
        hit = is_canonical(name)
        target = hit[0] if hit else (name or "").strip()
        if not target:
            return []

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT DISTINCT dr.file_path, COALESCE(dr.status, 'indexed') AS source "
                    "FROM entity_document_mentions m "
                    "JOIN entities e ON e.id = m.entity_id "
                    "JOIN document_registry dr ON dr.file_path = m.file_path "
                    "WHERE e.name = %s",
                    (target,),
                )
                return [{"file_path": r[0], "source": r[1]} for r in cur.fetchall()]

    def get_documents_for_entities_batch(
        self, names: list[str]
    ) -> dict[str, list[str]]:
        """Batch: {entity_name: [file_paths, ...]}. Input strings are keys."""
        if not names:
            return {}
        from alejandria.knowledge.gazetteer_lookup import is_canonical
        name_to_canonical: dict[str, str] = {}
        for n in names:
            if not n or not n.strip():
                continue
            hit = is_canonical(n)
            name_to_canonical[n] = hit[0] if hit else n.strip()
        if not name_to_canonical:
            return {}

        canonicals = list(set(name_to_canonical.values()))
        result: dict[str, list[str]] = {n: [] for n in names}
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT e.name, array_agg(DISTINCT m.file_path) "
                    "FROM entity_document_mentions m "
                    "JOIN entities e ON e.id = m.entity_id "
                    "WHERE e.name = ANY(%s) GROUP BY e.name",
                    (canonicals,),
                )
                rows = {r[0]: r[1] for r in cur.fetchall()}

        for input_name, canonical in name_to_canonical.items():
            result[input_name] = rows.get(canonical, [])
        return result

    def get_all_entity_mentions(self) -> list[dict]:
        """For every entity with mentions, return name/type/aliases/doc_count/file_paths.

        Ordered by doc_count desc. Aliases pulled from entity_aliases table
        (empty list when none).
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT e.name, e.entity_type, "
                    "       COALESCE((SELECT array_agg(ea.alias) FROM entity_aliases ea "
                    "                 WHERE ea.entity_id = e.id), ARRAY[]::text[]) AS aliases, "
                    "       count(DISTINCT m.file_path) AS doc_count, "
                    "       array_agg(DISTINCT m.file_path) AS file_paths "
                    "FROM entities e "
                    "JOIN entity_document_mentions m ON m.entity_id = e.id "
                    "GROUP BY e.id, e.name, e.entity_type "
                    "ORDER BY doc_count DESC"
                )
                return [
                    {
                        "name": r[0],
                        "type": r[1],
                        "aliases": list(r[2]) if r[2] else [],
                        "doc_count": r[3],
                        "file_paths": list(r[4]),
                    }
                    for r in cur.fetchall()
                ]

    def get_disambiguated_counts(self) -> dict[tuple[str, str], dict[str, int]]:
        """Per-entity mention counts grouped by resolved_name.

        Only entries with non-empty resolved_name. Returns
        {(name, type): {resolved_name: count, ...}}.
        """
        counts: dict[tuple[str, str], dict[str, int]] = {}
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT e.name, e.entity_type, m.resolved_name, count(*) "
                    "FROM entity_document_mentions m "
                    "JOIN entities e ON e.id = m.entity_id "
                    "WHERE m.resolved_name <> '' "
                    "GROUP BY e.name, e.entity_type, m.resolved_name "
                    "ORDER BY e.name, count(*) DESC"
                )
                for name, etype, resolved, cnt in cur.fetchall():
                    key = (name, etype)
                    counts.setdefault(key, {})[resolved] = cnt
        return counts

    # ------------------------------------------------------------------ #
    # Tier 2c: relation-based methods
    # ------------------------------------------------------------------ #

    def find_nodes_batch(
        self, searches: list[str], limit_per: int = 15
    ) -> list[dict]:
        """Search multiple names in one query. Returns list of {name, type, aliases}."""
        if not searches:
            return []
        from alejandria.knowledge.gazetteer_lookup import is_canonical
        needles: list[str] = []
        for s in searches:
            if not s or not s.strip():
                continue
            hit = is_canonical(s)
            needles.append(hit[0] if hit else s.strip())
        if not needles:
            return []

        total_limit = limit_per * len(searches)
        like_patterns = [f"%{n}%" for n in needles]

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT DISTINCT ON (e.id) e.id, e.name, e.entity_type, "
                    "       COALESCE((SELECT array_agg(ea.alias) FROM entity_aliases ea "
                    "                 WHERE ea.entity_id = e.id), ARRAY[]::text[]) AS aliases "
                    "FROM entities e "
                    "LEFT JOIN entity_aliases ea ON ea.entity_id = e.id "
                    "WHERE e.name = ANY(%s) "
                    "   OR e.name ILIKE ANY(%s) "
                    "   OR ea.alias ILIKE ANY(%s) "
                    "LIMIT %s",
                    (needles, like_patterns, like_patterns, total_limit),
                )
                rows = cur.fetchall()

        return [
            {
                "name": r[1],
                "type": r[2],
                "aliases": list(r[3]) if r[3] else [],
            }
            for r in rows
        ]

    def get_typed_relations(
        self,
        entity_name: str,
        confidence_min: str | None = None,
        rel_types: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Bidirectional relations for an entity, ordered by confidence.

        Signature matches Neo4jClient.get_typed_relations. Returns list of
        {from_name, from_type, rel_type, to_name, to_type, props}.
        """
        from alejandria.knowledge.gazetteer_lookup import is_canonical
        hit = is_canonical(entity_name)
        target = hit[0] if hit else (entity_name or "").strip()
        if not target:
            return []

        confidence_order = [
            "curated", "metadata", "llm_high", "llm_low", "ner", "co_occurrence",
        ]
        allowed_confidences: list[str] | None = None
        if confidence_min and confidence_min in confidence_order:
            cutoff = confidence_order.index(confidence_min) + 1
            allowed_confidences = confidence_order[:cutoff]

        rt_clause = ""
        rt_params: list[Any] = []
        if rel_types:
            rt_clause = " AND r.rel_type = ANY(%s)"
            rt_params.append(rel_types)
        conf_clause = ""
        conf_params: list[Any] = []
        if allowed_confidences:
            conf_clause = " AND r.confidence = ANY(%s)"
            conf_params.append(allowed_confidences)

        # Wrap UNION ALL in a subquery so ORDER BY can use CASE expression.
        # Postgres refuses CASE directly at the top-level of a UNION query.
        sql = (
            "WITH target AS (SELECT id FROM entities WHERE name = %s LIMIT 1), "
            "combined AS ( "
            "  SELECT a.name AS from_name, a.entity_type AS from_type, r.rel_type, "
            "         b.name AS to_name, b.entity_type AS to_type, "
            "         r.properties || jsonb_build_object('confidence', r.confidence) AS props, "
            "         r.confidence AS _conf "
            "  FROM target t JOIN relations r ON r.src_id = t.id "
            "  JOIN entities a ON a.id = r.src_id JOIN entities b ON b.id = r.dst_id "
            f"  WHERE TRUE{rt_clause}{conf_clause} "
            "  UNION ALL "
            "  SELECT a.name, a.entity_type, r.rel_type, b.name, b.entity_type, "
            "         r.properties || jsonb_build_object('confidence', r.confidence), r.confidence "
            "  FROM target t JOIN relations r ON r.dst_id = t.id "
            "  JOIN entities a ON a.id = r.src_id JOIN entities b ON b.id = r.dst_id "
            f"  WHERE TRUE{rt_clause}{conf_clause} "
            ") "
            "SELECT from_name, from_type, rel_type, to_name, to_type, props "
            "FROM combined "
            "ORDER BY "
            "  CASE _conf WHEN 'curated' THEN 1 WHEN 'metadata' THEN 2 "
            "             WHEN 'llm_high' THEN 3 WHEN 'llm_low' THEN 4 "
            "             WHEN 'ner' THEN 5 ELSE 6 END, rel_type "
            "LIMIT %s"
        )
        params: list[Any] = [target]
        params.extend(rt_params); params.extend(conf_params)
        params.extend(rt_params); params.extend(conf_params)
        params.append(limit)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

        return [
            {
                "from_name": r[0], "from_type": r[1], "rel_type": r[2],
                "to_name": r[3], "to_type": r[4], "props": r[5] or {},
            }
            for r in rows
        ]

    def get_typed_relations_batch(
        self,
        entity_names: list[str],
        confidence_min: str | None = None,
        limit_per: int = 30,
    ) -> list[dict]:
        """Batch variant of get_typed_relations. Excludes MENTIONED_IN."""
        if not entity_names:
            return []
        from alejandria.knowledge.gazetteer_lookup import is_canonical
        resolved: list[str] = []
        for n in entity_names:
            if not n or not n.strip():
                continue
            hit = is_canonical(n)
            resolved.append(hit[0] if hit else n.strip())
        if not resolved:
            return []

        confidence_order = [
            "curated", "metadata", "llm_high", "llm_low", "ner", "co_occurrence",
        ]
        allowed_confidences: list[str] | None = None
        if confidence_min and confidence_min in confidence_order:
            cutoff = confidence_order.index(confidence_min) + 1
            allowed_confidences = confidence_order[:cutoff]

        conf_clause = ""
        conf_params: list[Any] = []
        if allowed_confidences:
            conf_clause = " AND r.confidence = ANY(%s)"
            conf_params.append(allowed_confidences)

        total_limit = limit_per * len(entity_names)

        sql = (
            "WITH targets AS (SELECT id FROM entities WHERE name = ANY(%s)), "
            "combined AS ( "
            "  SELECT a.name AS from_name, a.entity_type AS from_type, r.rel_type, "
            "         b.name AS to_name, b.entity_type AS to_type, "
            "         r.properties || jsonb_build_object('confidence', r.confidence) AS props, "
            "         r.confidence AS _conf "
            "  FROM targets t JOIN relations r ON r.src_id = t.id "
            "  JOIN entities a ON a.id = r.src_id JOIN entities b ON b.id = r.dst_id "
            f"  WHERE r.rel_type <> 'MENTIONED_IN'{conf_clause} "
            "  UNION ALL "
            "  SELECT a.name, a.entity_type, r.rel_type, b.name, b.entity_type, "
            "         r.properties || jsonb_build_object('confidence', r.confidence), r.confidence "
            "  FROM targets t JOIN relations r ON r.dst_id = t.id "
            "  JOIN entities a ON a.id = r.src_id JOIN entities b ON b.id = r.dst_id "
            f"  WHERE r.rel_type <> 'MENTIONED_IN'{conf_clause} "
            ") "
            "SELECT from_name, from_type, rel_type, to_name, to_type, props "
            "FROM combined "
            "ORDER BY "
            "  CASE _conf WHEN 'curated' THEN 1 WHEN 'metadata' THEN 2 "
            "             WHEN 'llm_high' THEN 3 WHEN 'llm_low' THEN 4 "
            "             WHEN 'ner' THEN 5 ELSE 6 END, rel_type "
            "LIMIT %s"
        )
        params: list[Any] = [resolved]
        params.extend(conf_params); params.extend(conf_params)
        params.append(total_limit)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

        return [
            {
                "from_name": r[0], "from_type": r[1], "rel_type": r[2],
                "to_name": r[3], "to_type": r[4], "props": r[5] or {},
            }
            for r in rows
        ]

    def get_parallel_passages(
        self, file_path: str, layer: int | None = None, limit: int = 50,
    ) -> list[dict]:
        """Document↔Document parallel passages — NOT IMPLEMENTED.

        Blocked on schema v3 (Document→Document edges not migrated). Same
        shape of blocker as MENTIONED_IN in §6.1 of the audit; needs a
        dedicated ``document_parallels`` table + migration step before port.
        Tracked as Tier 2c-pending.
        """
        raise NotImplementedError(
            "get_parallel_passages requires schema v3 (Document→Document edges). "
            "Stub kept; implement when parallels table is added."
        )

    def get_genealogy_tree(
        self,
        person: str,
        direction: str = "descendants",
        depth: int = 3,
        lang: str = "en",
    ) -> dict:
        raise NotImplementedError(
            "Tier 2d — recursive CTE with LIMIT intermedio "
            "(pattern in docs/postgres-migration.md §2.3)"
        )

    def get_genealogy_path(self, name1: str, name2: str) -> dict:
        raise NotImplementedError("Tier 2d — bidirectional recursive CTE")

    # ------------------------------------------------------------------ #
    # Writes — Fase 4 (cutover)
    # ------------------------------------------------------------------ #

    def merge_entity(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4 — ingestion cutover")

    def merge_document(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4")

    def merge_relation(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4")

    def link_entity_to_document(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4")

    def batch_merge_entities(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4")

    def batch_merge_documents(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4")

    def batch_merge_relations(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4")

    def batch_link_entities_to_document(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4")

    def batch_delete_documents(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4")

    def batch_write_all(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4")

    def delete_document_relations(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4")

    def update_entity_profile(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4 — profile_store refactor")

    def load_curated_relations(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4")

    def clear_all(self, *args, **kwargs):
        raise NotImplementedError("Write path: Fase 4 — TRUNCATE CASCADE")

    # Explicitly deprecated methods raise a distinct error so they're caught
    # at cutover time if anything still calls them.

    def _ensure_indexes(self) -> None:
        raise NotImplementedError(
            "DEPRECATED per audit §6.4: DDL covers this, no runtime equivalent."
        )

    def migrate_untyped_relations(self, *args, **kwargs):
        raise NotImplementedError(
            "DEPRECATED per audit §6.2: dead code post-R7. Remove API route also."
        )


# --------------------------------------------------------------------------- #
# Factory (dispatch by settings.storage_backend)
# --------------------------------------------------------------------------- #

def make_graph_client():
    """Return the configured KG client.

    Dispatches on ``settings.storage_backend``:

    * ``"sqlite"`` (default): ``Neo4jClient`` — legacy stack.
    * ``"postgres"``: ``PostgresGraphClient`` — this module.

    Same naming convention as ``search/textual.py::make_textual_search``.
    ``api/dependencies.py::get_neo4j_client`` delegates to this factory.
    """
    from alejandria.config import settings

    backend = (settings.storage_backend or "sqlite").lower()
    if backend == "postgres":
        return PostgresGraphClient()
    from alejandria.knowledge.neo4j_client import Neo4jClient
    return Neo4jClient()
