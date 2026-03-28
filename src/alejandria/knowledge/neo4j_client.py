"""Neo4j driver wrapper for the knowledge graph."""

from __future__ import annotations

import logging
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
        """Create a relationship between two entities."""
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
                f"     collect(DISTINCT {{from: startNode(rel).name, type: type(rel), to: endNode(rel).name}}) AS rels "
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

    def clear_all(self) -> None:
        """Delete everything in the graph (for full reindex)."""
        with self._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("Neo4j graph cleared")
