"""Neo4j driver wrapper for the knowledge graph."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from alejandria.config import settings

logger = logging.getLogger(__name__)


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

    def delete_document_relations(self, file_path: str) -> None:
        """Delete all relationships involving a document and orphaned entities."""
        with self._driver.session() as session:
            # Delete relations to this document
            session.run(
                "MATCH (d:Document {file_path: $file_path}) "
                "DETACH DELETE d",
                file_path=file_path,
            )

    def find_node(self, search: str, entity_type: str | None = None, limit: int = 20) -> list[dict]:
        """Search for entities by partial name match."""
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

    def get_neighbors(
        self, name: str, depth: int = 1, relation_types: list[str] | None = None, limit: int = 50
    ) -> dict:
        """Get neighboring nodes and edges for an entity."""
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
        with self._driver.session() as session:
            result = session.run(
                "MATCH (e:Entity {name: $name})-[:MENTIONED_IN]->(d:Document) "
                "RETURN d.file_path AS file_path, d.source AS source",
                name=name,
            )
            return [dict(record) for record in result]

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

    def migrate_untyped_relations(self) -> dict[str, int]:
        """Reclassify generic CO_OCCURS_WITH and RELATED_TO relations.

        This is a one-time migration to mark existing co-occurrence relations
        with confidence='co_occurrence' so they can be distinguished from
        curated/LLM-extracted typed relations.

        Returns count of relations updated per type.
        """
        counts = {}
        with self._driver.session() as session:
            for rel_type in ("CO_OCCURS_WITH", "RELATED_TO", "ASSOCIATED_WITH",
                             "TEACHES", "BELONGS_TO", "REFERENCED_IN",
                             "LIVED_DURING", "EXISTS_DURING"):
                result = session.run(
                    f"MATCH ()-[r:{rel_type}]->() "
                    "WHERE r.confidence IS NULL "
                    "SET r.confidence = 'co_occurrence', r.source = 'co_occurrence' "
                    "RETURN count(r) AS count"
                )
                record = result.single()
                cnt = record["count"] if record else 0
                if cnt > 0:
                    counts[rel_type] = cnt
                    logger.info("Migrated %d %s relations to co_occurrence confidence", cnt, rel_type)
        return counts

    def get_typed_relations(
        self,
        entity_name: str,
        confidence_min: str | None = None,
        rel_types: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get relations for an entity, optionally filtered by confidence and type.

        Args:
            entity_name: Entity to query
            confidence_min: Minimum confidence level
                (curated > metadata > llm_high > llm_low > ner > co_occurrence)
            rel_types: Filter to specific relation types
            limit: Max results

        Returns list of dicts with: from_name, from_type, rel_type, to_name, to_type, properties
        """
        confidence_order = {
            "curated": 6, "metadata": 5, "llm_high": 4,
            "llm_low": 3, "ner": 2, "co_occurrence": 1,
        }

        rel_filter = ""
        if rel_types:
            types_str = "|".join(rel_types)
            rel_filter = f":{types_str}"

        with self._driver.session() as session:
            result = session.run(
                f"MATCH (a:Entity {{name: $name}})-[r{rel_filter}]->(b:Entity) "
                "RETURN a.name AS from_name, a.type AS from_type, "
                "       type(r) AS rel_type, "
                "       b.name AS to_name, b.type AS to_type, "
                "       properties(r) AS props "
                "ORDER BY r.confidence DESC "
                f"LIMIT $limit "
                "UNION "
                f"MATCH (a:Entity)-[r{rel_filter}]->(b:Entity {{name: $name}}) "
                "RETURN a.name AS from_name, a.type AS from_type, "
                "       type(r) AS rel_type, "
                "       b.name AS to_name, b.type AS to_type, "
                "       properties(r) AS props "
                "ORDER BY r.confidence DESC "
                f"LIMIT $limit",
                name=entity_name, limit=limit,
            )
            relations = [dict(record) for record in result]

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

    def clear_all(self) -> None:
        """Delete everything in the graph (for full reindex)."""
        with self._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("Neo4j graph cleared")
