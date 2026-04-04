"""Neo4j driver wrapper for the knowledge graph."""

from __future__ import annotations

import json
import logging
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from alejandria.config import settings

logger = logging.getLogger(__name__)

_GAZETTEER_PATH = Path(__file__).parent / "gazetteers" / "entities.json"


@lru_cache(maxsize=1)
def _build_alias_lookup() -> dict[str, str]:
    """Build a lowercase alias → canonical name lookup from the gazetteer.

    Returns a dict where keys are lowercased aliases and values are canonical names.
    """
    lookup: dict[str, str] = {}
    if not _GAZETTEER_PATH.exists():
        return lookup
    try:
        data = json.loads(_GAZETTEER_PATH.read_text(encoding="utf-8"))
        for _type, entries in data.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                canonical = entry.get("name", "")
                if not canonical:
                    continue
                for alias in entry.get("aliases", []):
                    if alias:
                        lookup[alias.lower()] = canonical
    except Exception:
        logger.warning("Failed to load gazetteer for alias lookup", exc_info=True)
    return lookup

# TTL-aware cache: stores (result, timestamp). Cache invalidated after 5 minutes.
_CACHE_TTL_SECONDS = 300


class Neo4jClient:
    """Thin wrapper around the Neo4j Python driver."""

    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self._driver = GraphDatabase.driver(
            uri or settings.neo4j_uri,
            auth=(user or settings.neo4j_user, password or settings.neo4j_password),
        )
        self._ensure_indexes()

    _cache: dict[str, tuple[Any, float]] = {}

    def _cached(self, key: str, fn, ttl: float = _CACHE_TTL_SECONDS):
        """Simple TTL cache for read-only queries."""
        now = time.time()
        if key in self._cache:
            result, ts = self._cache[key]
            if now - ts < ttl:
                return result
        result = fn()
        self._cache[key] = (result, now)
        # Evict old entries periodically (keep cache bounded)
        if len(self._cache) > 500:
            cutoff = now - ttl
            self._cache = {k: v for k, v in self._cache.items() if v[1] > cutoff}
        return result

    def _ensure_indexes(self) -> None:
        """Create indexes and constraints on first connection."""
        with self._driver.session() as session:
            # Unique constraint on Entity name+type
            session.run(
                "CREATE CONSTRAINT entity_unique IF NOT EXISTS "
                "FOR (e:Entity) REQUIRE (e.name, e.type) IS UNIQUE"
            )
            # Index on Entity type for fast filtering
            session.run(
                "CREATE INDEX entity_type_idx IF NOT EXISTS FOR (e:Entity) ON (e.type)"
            )
            # Index on Document file_path
            session.run(
                "CREATE CONSTRAINT doc_unique IF NOT EXISTS "
                "FOR (d:Document) REQUIRE d.file_path IS UNIQUE"
            )
            # P6: Full-text index for entity name search
            session.run(
                "CREATE FULLTEXT INDEX entity_name_ft IF NOT EXISTS "
                "FOR (e:Entity) ON EACH [e.name]"
            )
        logger.info("Neo4j indexes ensured")

    def close(self) -> None:
        self._driver.close()

    def merge_entity(self, name: str, entity_type: str, aliases: list[str] | None = None) -> None:
        """Create or update an entity node."""
        with self._driver.session() as session:
            session.run(
                "MERGE (e:Entity {name: $name, type: $type}) "
                "ON CREATE SET e.aliases = $aliases "
                "ON MATCH SET e.aliases = "
                "  CASE WHEN e.aliases IS NULL THEN $aliases "
                "  ELSE [x IN e.aliases WHERE NOT x IN $aliases] + $aliases END",
                name=name, type=entity_type, aliases=aliases or [],
            )

    def merge_document(self, file_path: str, source: str) -> None:
        """Create or update a document node."""
        with self._driver.session() as session:
            session.run(
                "MERGE (d:Document {file_path: $file_path}) "
                "SET d.source = $source",
                file_path=file_path, source=source,
            )

    def merge_relation(
        self,
        from_name: str,
        from_type: str,
        rel_type: str,
        to_name: str,
        to_type: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Create a relationship between two entities.

        P6 standard properties (optional in ``properties`` dict):
        - source_ref: str — Scripture reference where this relation is stated
        - confidence: str — One of: curated, metadata, llm_high, llm_low, ner
        - source: str — Origin: curated_seed, metadata_extraction, llm, co_occurrence
        - verified: bool — Whether human-verified
        - role: str — For AUTHORED relations: author, compiler, editor, continuator, scribe
        """
        props = properties or {}
        with self._driver.session() as session:
            session.run(
                f"MERGE (a:Entity {{name: $from_name, type: $from_type}}) "
                f"MERGE (b:Entity {{name: $to_name, type: $to_type}}) "
                f"MERGE (a)-[r:{rel_type}]->(b) "
                "SET r += $props",
                from_name=from_name, from_type=from_type,
                to_name=to_name, to_type=to_type,
                props=props,
            )

    def link_entity_to_document(
        self, entity_name: str, entity_type: str, file_path: str, rel_type: str = "MENTIONED_IN"
    ) -> None:
        """Link an entity to a document."""
        with self._driver.session() as session:
            session.run(
                f"MATCH (e:Entity {{name: $name, type: $type}}) "
                f"MATCH (d:Document {{file_path: $file_path}}) "
                f"MERGE (e)-[:{rel_type}]->(d)",
                name=entity_name, type=entity_type, file_path=file_path,
            )

    # ------------------------------------------------------------------
    # Batch operations (for rebuild_kg performance)
    # ------------------------------------------------------------------

    def batch_merge_entities(self, entities: list[dict]) -> None:
        """Batch merge entity nodes.

        Each dict: {name: str, type: str, aliases: list[str]}.
        """
        if not entities:
            return
        with self._driver.session() as session:
            session.run(
                "UNWIND $entities AS e "
                "MERGE (n:Entity {name: e.name, type: e.type}) "
                "ON CREATE SET n.aliases = e.aliases "
                "ON MATCH SET n.aliases = "
                "  CASE WHEN n.aliases IS NULL THEN e.aliases "
                "  ELSE [x IN n.aliases WHERE NOT x IN e.aliases] + e.aliases END",
                entities=entities,
            )

    def batch_merge_documents(self, documents: list[dict]) -> None:
        """Batch merge document nodes.

        Each dict: {file_path: str, source: str}.
        """
        if not documents:
            return
        with self._driver.session() as session:
            session.run(
                "UNWIND $docs AS d "
                "MERGE (n:Document {file_path: d.file_path}) "
                "SET n.source = d.source",
                docs=documents,
            )

    def batch_merge_relations(self, relations: list[dict]) -> None:
        """Batch merge relations between entities.

        Each dict: {from_name, from_type, rel_type, to_name, to_type, props}.
        Groups by rel_type since Cypher needs static relationship types.
        """
        if not relations:
            return
        # Group by rel_type (Cypher requires literal relationship types)
        by_type: dict[str, list[dict]] = {}
        for r in relations:
            by_type.setdefault(r["rel_type"], []).append(r)

        with self._driver.session() as session:
            for rel_type, rels in by_type.items():
                batch = [
                    {
                        "from_name": r["from_name"],
                        "from_type": r["from_type"],
                        "to_name": r["to_name"],
                        "to_type": r["to_type"],
                        "props": r.get("props", {}),
                    }
                    for r in rels
                ]
                session.run(
                    "UNWIND $rels AS r "
                    "MERGE (a:Entity {name: r.from_name, type: r.from_type}) "
                    "MERGE (b:Entity {name: r.to_name, type: r.to_type}) "
                    f"MERGE (a)-[rel:{rel_type}]->(b) "
                    "SET rel += r.props",
                    rels=batch,
                )

    def batch_link_entities_to_document(self, links: list[dict]) -> None:
        """Batch link entities to a document.

        Each dict: {entity_name, entity_type, file_path}.
        """
        if not links:
            return
        with self._driver.session() as session:
            session.run(
                "UNWIND $links AS l "
                "MATCH (e:Entity {name: l.entity_name, type: l.entity_type}) "
                "MATCH (d:Document {file_path: l.file_path}) "
                "MERGE (e)-[:MENTIONED_IN]->(d)",
                links=links,
            )

    def delete_document_relations(self, file_path: str) -> None:
        """Delete all relationships involving a document and orphaned entities."""
        with self._driver.session() as session:
            # Delete relations to this document
            session.run(
                "MATCH (d:Document {file_path: $file_path}) "
                "DETACH DELETE d",
                file_path=file_path,
            )

    def _resolve_name(self, name: str) -> str:
        """Resolve an alias or variant name to the canonical node name in Neo4j.

        Resolution order:
        1. Gazetteer alias lookup (fast, in-memory, authoritative)
        2. Exact Neo4j match
        3. Case-insensitive Neo4j match
        Returns the canonical name if found, otherwise the original input.
        """
        # 1. Gazetteer lookup — maps aliases to canonical names (e.g. Pedro → Peter)
        alias_lookup = _build_alias_lookup()
        canonical = alias_lookup.get(name.lower())
        if canonical:
            return canonical

        cache_key = f"resolve_name:{name}"

        def _query():
            with self._driver.session() as session:
                # 2. Exact match in Neo4j (fast, indexed)
                result = session.run(
                    "MATCH (e:Entity {name: $name}) RETURN e.name AS name LIMIT 1",
                    name=name,
                )
                record = result.single()
                if record:
                    return record["name"]

                # 3. Case-insensitive match
                result = session.run(
                    "MATCH (e:Entity) WHERE toLower(e.name) = toLower($name) "
                    "RETURN e.name AS name LIMIT 1",
                    name=name,
                )
                record = result.single()
                if record:
                    return record["name"]

                return name

        return self._cached(cache_key, _query)

    def _resolve_names(self, names: list[str]) -> list[str]:
        """Resolve a list of names to their canonical forms."""
        return [self._resolve_name(n) for n in names]

    def find_node(self, search: str, entity_type: str | None = None, limit: int = 20) -> list[dict]:
        """Search for entities by partial name match."""
        cache_key = f"find_node:{search}:{entity_type}:{limit}"

        def _query():
            with self._driver.session() as session:
                if entity_type:
                    result = session.run(
                        "MATCH (e:Entity) "
                        "WHERE e.type = $type AND toLower(e.name) CONTAINS toLower($search) "
                        "RETURN e.name AS name, e.type AS type, e.aliases AS aliases "
                        "LIMIT $limit",
                        search=search, type=entity_type, limit=limit,
                    )
                else:
                    result = session.run(
                        "MATCH (e:Entity) "
                        "WHERE toLower(e.name) CONTAINS toLower($search) "
                        "RETURN e.name AS name, e.type AS type, e.aliases AS aliases "
                        "LIMIT $limit",
                        search=search, limit=limit,
                    )
                return [dict(record) for record in result]

        return self._cached(cache_key, _query)

    def get_neighbors(
        self, name: str, depth: int = 1, relation_types: list[str] | None = None, limit: int = 50
    ) -> dict:
        """Get neighboring nodes and edges for an entity."""
        name = self._resolve_name(name)
        rel_filter = ""
        if relation_types:
            types_str = "|".join(relation_types)
            rel_filter = f":{types_str}"

        with self._driver.session() as session:
            query = (
                f"MATCH (e:Entity {{name: $name}}) "
                f"MATCH path = (e)-[r{rel_filter}*1..{depth}]-(other:Entity) "
                f"WITH e, other, path "
                f"LIMIT $limit "
                f"UNWIND relationships(path) AS rel "
                f"WITH collect(DISTINCT other) AS others, "
                f"     collect(DISTINCT {{from: startNode(rel).name, type: type(rel), to: endNode(rel).name, properties: properties(rel)}}) AS rels "
                f"RETURN others, rels"
            )
            result = session.run(query, name=name, limit=limit)
            record = result.single()
            if record is None:
                return {"nodes": [], "edges": []}

            nodes = [
                {"name": n["name"], "type": n.get("type", "unknown")}
                for n in record["others"]
            ]
            edges = record["rels"]
            return {"nodes": nodes, "edges": edges}

    def get_documents_for_entity(self, name: str) -> list[dict]:
        """Find documents that mention an entity."""
        name = self._resolve_name(name)
        with self._driver.session() as session:
            result = session.run(
                "MATCH (e:Entity {name: $name})-[:MENTIONED_IN]->(d:Document) "
                "RETURN d.file_path AS file_path, d.source AS source",
                name=name,
            )
            return [dict(record) for record in result]

    def get_documents_for_entities_batch(self, names: list[str]) -> dict[str, list[str]]:
        """Find documents for multiple entities in a single Cypher query.

        Returns dict mapping entity_name -> list of file_paths.
        """
        if not names:
            return {}
        with self._driver.session() as session:
            result = session.run(
                "MATCH (e:Entity)-[:MENTIONED_IN]->(d:Document) "
                "WHERE e.name IN $names "
                "RETURN e.name AS name, collect(DISTINCT d.file_path) AS file_paths",
                names=names,
            )
            return {record["name"]: record["file_paths"] for record in result}

    def find_nodes_batch(self, searches: list[str], limit_per: int = 15) -> list[dict]:
        """Search for entities matching multiple names in a single query.

        Uses fulltext index for efficient lookup. Returns list of dicts
        with name, type, aliases — deduplicated.
        """
        if not searches:
            return []
        with self._driver.session() as session:
            # Build OR query for fulltext index
            ft_query = " OR ".join(searches)
            try:
                result = session.run(
                    "CALL db.index.fulltext.queryNodes('entity_name_ft', $query) "
                    "YIELD node, score "
                    "RETURN node.name AS name, node.type AS type, node.aliases AS aliases "
                    "LIMIT $limit",
                    query=ft_query, limit=limit_per * len(searches),
                )
                return [dict(record) for record in result]
            except Exception:
                # Fallback: CONTAINS matching (slower but always works)
                conditions = " OR ".join(
                    f"toLower(e.name) CONTAINS toLower('{s.replace(chr(39), '')}')"
                    for s in searches
                )
                result = session.run(
                    f"MATCH (e:Entity) WHERE {conditions} "
                    "RETURN e.name AS name, e.type AS type, e.aliases AS aliases "
                    f"LIMIT $limit",
                    limit=limit_per * len(searches),
                )
                return [dict(record) for record in result]

    def get_typed_relations_batch(
        self,
        entity_names: list[str],
        confidence_min: str | None = None,
        limit_per: int = 30,
    ) -> list[dict]:
        """Get typed relations for multiple entities in a single query.

        Returns list of dicts with: from_name, from_type, rel_type, to_name, to_type, props.
        """
        if not entity_names:
            return []

        entity_names = self._resolve_names(entity_names)

        confidence_order = {
            "curated": 6, "metadata": 5, "llm_high": 4,
            "llm_low": 3, "ner": 2, "co_occurrence": 1,
        }

        with self._driver.session() as session:
            result = session.run(
                "MATCH (a:Entity)-[r]->(b:Entity) "
                "WHERE a.name IN $names AND NOT type(r) IN ['MENTIONED_IN'] "
                "RETURN a.name AS from_name, a.type AS from_type, "
                "       type(r) AS rel_type, "
                "       b.name AS to_name, b.type AS to_type, "
                "       properties(r) AS props "
                f"LIMIT $limit "
                "UNION "
                "MATCH (a:Entity)-[r]->(b:Entity) "
                "WHERE b.name IN $names AND NOT type(r) IN ['MENTIONED_IN'] "
                "RETURN a.name AS from_name, a.type AS from_type, "
                "       type(r) AS rel_type, "
                "       b.name AS to_name, b.type AS to_type, "
                "       properties(r) AS props "
                f"LIMIT $limit",
                names=entity_names, limit=limit_per * len(entity_names),
            )
            relations = [dict(record) for record in result]

        if confidence_min and confidence_min in confidence_order:
            min_level = confidence_order[confidence_min]
            relations = [
                r for r in relations
                if confidence_order.get(
                    (r.get("props") or {}).get("confidence", "co_occurrence"), 0
                ) >= min_level
            ]

        return relations

    def graph_summary(self) -> dict:
        """Get overall graph statistics."""
        with self._driver.session() as session:
            entity_counts = session.run(
                "MATCH (e:Entity) RETURN e.type AS type, count(*) AS count ORDER BY count DESC"
            )
            entity_stats = [dict(r) for r in entity_counts]

            rel_counts = session.run(
                "MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS count ORDER BY count DESC"
            )
            rel_stats = [dict(r) for r in rel_counts]

            total_nodes = session.run("MATCH (n) RETURN count(n) AS count").single()["count"]
            total_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]

            return {
                "total_nodes": total_nodes,
                "total_relationships": total_rels,
                "nodes_by_type": entity_stats,
                "relationships_by_type": rel_stats,
            }

    def get_all_entity_mentions(self) -> list[dict]:
        """Bulk query: for each entity, count documents and list file_paths.

        Returns list of dicts with keys: name, type, aliases, doc_count, file_paths.
        Single Cypher query for efficiency.
        """
        with self._driver.session() as session:
            result = session.run(
                "MATCH (e:Entity)-[:MENTIONED_IN]->(d:Document) "
                "WITH e, collect(DISTINCT d.file_path) AS fps "
                "RETURN e.name AS name, e.type AS type, "
                "       e.aliases AS aliases, "
                "       size(fps) AS doc_count, fps AS file_paths "
                "ORDER BY doc_count DESC"
            )
            return [dict(record) for record in result]

    def update_entity_profile(
        self, name: str, entity_type: str,
        summary: str | None = None,
        disambiguator: str | None = None,
        mention_count: int | None = None,
    ) -> None:
        """Update profile properties on an Entity node in Neo4j."""
        props: dict = {}
        if summary is not None:
            props["summary"] = summary
        if disambiguator is not None:
            props["disambiguator"] = disambiguator
        if mention_count is not None:
            props["mention_count"] = mention_count
        if not props:
            return
        with self._driver.session() as session:
            session.run(
                "MATCH (e:Entity {name: $name, type: $type}) SET e += $props",
                name=name, type=entity_type, props=props,
            )

    def load_curated_relations(self, relations_path: str | Path) -> dict[str, int]:
        """Load curated relations from a JSON seed file into Neo4j.

        Returns dict mapping relation_type -> count of relations loaded.
        """
        import json

        path = Path(relations_path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        counts: dict[str, int] = {}
        for rel_type, relations in data.items():
            count = 0
            for rel in relations:
                from_ent = rel["from"]
                to_ent = rel["to"]

                # Build properties dict from relation fields
                props: dict[str, Any] = {}
                for key in ("source_ref", "confidence", "source", "verified", "role", "verse_range"):
                    if key in rel:
                        props[key] = rel[key]
                # Default confidence for curated data
                if "confidence" not in props:
                    props["confidence"] = "curated"
                props["source"] = "curated_seed"

                self.merge_relation(
                    from_name=from_ent["name"],
                    from_type=from_ent["type"],
                    rel_type=rel_type,
                    to_name=to_ent["name"],
                    to_type=to_ent["type"],
                    properties=props,
                )

                # Handle bidirectional relations
                if rel.get("bidirectional"):
                    self.merge_relation(
                        from_name=to_ent["name"],
                        from_type=to_ent["type"],
                        rel_type=rel_type,
                        to_name=from_ent["name"],
                        to_type=from_ent["type"],
                        properties=props,
                    )

                count += 1
            counts[rel_type] = count
            logger.info("Loaded %d %s relations from curated seed", count, rel_type)

        return counts

    def migrate_untyped_relations(self, batch_size: int = 500) -> dict[str, int]:
        """Reclassify generic CO_OCCURS_WITH and RELATED_TO relations.

        This is a one-time migration to mark existing co-occurrence relations
        with confidence='co_occurrence' so they can be distinguished from
        curated/LLM-extracted typed relations.

        Uses batched updates to avoid Neo4j memory limits.
        Returns count of relations updated per type.
        """
        counts = {}
        with self._driver.session() as session:
            for rel_type in ("CO_OCCURS_WITH", "RELATED_TO", "ASSOCIATED_WITH",
                             "TEACHES", "BELONGS_TO", "REFERENCED_IN",
                             "LIVED_DURING", "EXISTS_DURING"):
                total = 0
                while True:
                    result = session.run(
                        f"MATCH ()-[r:{rel_type}]->() "
                        "WHERE r.confidence IS NULL "
                        "WITH r LIMIT $batch "
                        "SET r.confidence = 'co_occurrence', r.source = 'co_occurrence' "
                        "RETURN count(r) AS count",
                        batch=batch_size,
                    )
                    record = result.single()
                    cnt = record["count"] if record else 0
                    total += cnt
                    if cnt < batch_size:
                        break
                if total > 0:
                    counts[rel_type] = total
                    logger.info("Migrated %d %s relations to co_occurrence confidence", total, rel_type)
        return counts

    def get_parallel_passages(
        self, file_path: str, layer: int | None = None, limit: int = 50,
    ) -> list[dict]:
        """Find parallel passages for a scripture chapter via graph relations.

        Args:
            file_path: Document file_path like 'en/scriptures/ot/genesis/1.txt'
            layer: Optional filter (1=narrative, 2=editorial, 3=thematic)
            limit: Max results

        Returns list of dicts with: file_path, narrative, layer, rel_type
        """
        layer_filter = ""
        if layer is not None:
            layer_filter = " AND r.layer = $layer"

        with self._driver.session() as session:
            result = session.run(
                "MATCH (d:Document {file_path: $fp})-[r]->(d2:Document) "
                "WHERE type(r) IN ['PARALLEL_NARRATIVE', 'EDITORIAL_PARALLEL', 'THEMATIC_LINK']"
                f"{layer_filter} "
                "RETURN d2.file_path AS file_path, r.narrative AS narrative, "
                "       r.layer AS layer, type(r) AS rel_type "
                "LIMIT $limit "
                "UNION "
                "MATCH (d:Document {file_path: $fp})<-[r]-(d2:Document) "
                "WHERE type(r) IN ['PARALLEL_NARRATIVE', 'EDITORIAL_PARALLEL', 'THEMATIC_LINK']"
                f"{layer_filter} "
                "RETURN d2.file_path AS file_path, r.narrative AS narrative, "
                "       r.layer AS layer, type(r) AS rel_type "
                "LIMIT $limit",
                fp=file_path, layer=layer, limit=limit,
            )
            return [dict(record) for record in result]

    def get_typed_relations(
        self,
        entity_name: str,
        confidence_min: str | None = None,
        rel_types: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get relations for an entity, optionally filtered by confidence and type.

        Args:
            entity_name: Entity to query (alias or canonical name — resolved automatically)
            confidence_min: Minimum confidence level
                (curated > metadata > llm_high > llm_low > ner > co_occurrence)
            rel_types: Filter to specific relation types
            limit: Max results

        Returns list of dicts with: from_name, from_type, rel_type, to_name, to_type, properties
        """
        entity_name = self._resolve_name(entity_name)

        confidence_order = {
            "curated": 6, "metadata": 5, "llm_high": 4,
            "llm_low": 3, "ner": 2, "co_occurrence": 1,
        }

        rel_filter = ""
        if rel_types:
            types_str = "|".join(rel_types)
            rel_filter = f":{types_str}"

        # Build confidence filter for Cypher: exclude relations below minimum
        conf_cypher = ""
        if confidence_min and confidence_min in confidence_order:
            min_level = confidence_order[confidence_min]
            allowed = [k for k, v in confidence_order.items() if v >= min_level]
            conf_cypher = f" AND r.confidence IN {allowed}"

        cache_key = f"typed_rels:{entity_name}:{rel_filter}:{conf_cypher}:{limit}"

        def _query():
            with self._driver.session() as session:
                result = session.run(
                    f"MATCH (a:Entity {{name: $name}})-[r{rel_filter}]->(b:Entity) "
                    f"WHERE true{conf_cypher} "
                    "RETURN a.name AS from_name, a.type AS from_type, "
                    "       type(r) AS rel_type, "
                    "       b.name AS to_name, b.type AS to_type, "
                    "       properties(r) AS props "
                    "ORDER BY r.confidence DESC "
                    f"LIMIT $limit "
                    "UNION "
                    f"MATCH (a:Entity)-[r{rel_filter}]->(b:Entity {{name: $name}}) "
                    f"WHERE true{conf_cypher} "
                    "RETURN a.name AS from_name, a.type AS from_type, "
                    "       type(r) AS rel_type, "
                    "       b.name AS to_name, b.type AS to_type, "
                    "       properties(r) AS props "
                    "ORDER BY r.confidence DESC "
                    f"LIMIT $limit",
                    name=entity_name, limit=limit,
                )
                return [dict(record) for record in result]

        relations = self._cached(cache_key, _query)

        # Filter by minimum confidence if specified
        if confidence_min and confidence_min in confidence_order:
            min_level = confidence_order[confidence_min]
            relations = [
                r for r in relations
                if confidence_order.get(
                    (r.get("props") or {}).get("confidence", "co_occurrence"), 0
                ) >= min_level
            ]

        return relations[:limit]

    def clear_all(self, preserve_sources: list[str] | None = None) -> None:
        """Delete graph data, optionally preserving external sources.

        Args:
            preserve_sources: List of source values to keep (e.g. ["topical_guide"]).
                Nodes/relations with these source properties are preserved.
                If None, deletes everything.
        """
        with self._driver.session() as session:
            if preserve_sources:
                # Delete only corpus-derived data, preserve external imports.
                # Use small batches: relations first (they're the bulk), then nodes.
                batch_size = 10000
                preserved_set = preserve_sources

                # 1. Delete all non-preserved relations (batched).
                # Note: r.source IS NULL also counts as non-preserved.
                total = 0
                while True:
                    result = session.run(
                        "MATCH ()-[r]-() "
                        "WHERE r.source IS NULL OR NOT (r.source IN $sources) "
                        "WITH r LIMIT $batch DELETE r RETURN count(*) AS deleted",
                        sources=preserved_set, batch=batch_size,
                    )
                    deleted = result.single()["deleted"]
                    total += deleted
                    if deleted == 0:
                        break
                    if total % 100000 == 0:
                        logger.info("Neo4j clear: deleted %d relations so far...", total)
                logger.info("Neo4j clear: deleted %d non-preserved relations", total)

                # 2. Delete Document nodes (now relation-free, safe to batch)
                total = 0
                while True:
                    result = session.run(
                        "MATCH (d:Document) WITH d LIMIT $batch DETACH DELETE d RETURN count(*) AS deleted",
                        batch=batch_size,
                    )
                    deleted = result.single()["deleted"]
                    total += deleted
                    if deleted == 0:
                        break
                logger.info("Neo4j clear: deleted %d Document nodes", total)

                # 3. Delete Entity nodes that have no preserved relations (batched)
                total = 0
                while True:
                    result = session.run(
                        "MATCH (e:Entity) "
                        "WHERE NOT EXISTS { "
                        "  MATCH (e)-[r]-() WHERE r.source IN $sources "
                        "} "
                        "WITH e LIMIT $batch DETACH DELETE e RETURN count(*) AS deleted",
                        sources=preserved_set, batch=batch_size,
                    )
                    deleted = result.single()["deleted"]
                    total += deleted
                    if deleted == 0:
                        break
                logger.info("Neo4j clear: deleted %d Entity nodes (non-preserved)", total)

                logger.info(
                    "Neo4j graph cleared (preserved sources: %s)",
                    ", ".join(preserve_sources),
                )
            else:
                # Batch delete to avoid Neo4j memory limits on large graphs
                batch_size = 5000
                total_deleted = 0
                while True:
                    result = session.run(
                        "MATCH (n) WITH n LIMIT $batch DETACH DELETE n RETURN count(*) AS deleted",
                        batch=batch_size,
                    )
                    deleted = result.single()["deleted"]
                    total_deleted += deleted
                    if deleted == 0:
                        break
                    logger.info("Neo4j clear: deleted %d nodes (total: %d)", deleted, total_deleted)
                logger.info("Neo4j graph cleared (full, %d nodes deleted)", total_deleted)
        # Invalidate query cache
        self._cache.clear()
