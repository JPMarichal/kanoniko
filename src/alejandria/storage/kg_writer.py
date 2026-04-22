"""Knowledge-graph write Protocol.

Covers all write operations the ingestion pipeline performs against the
graph: entities, relations, document nodes, entity→document mention
edges, and lifecycle (clear, ensure indexes).

``load_curated_relations`` **does not** live here — it is orchestration
(read-curated-file → batch_merge_*), not persistence. See
:class:`alejandria.knowledge.curated_seed_loader.CuratedSeedLoader`.

Concrete implementation: :mod:`alejandria.storage.postgres_kg_writer`
over Postgres IONOS. The §3.1-era ``LegacyKGWriter`` (Neo4j adapter)
was retired together with Neo4j itself in §3.3.
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class KnowledgeGraphWriter(Protocol):
    """Write operations over the knowledge graph."""

    # ----- Lifecycle -------------------------------------------------- #

    def clear_all(self, preserve_sources: list[str] | None = None) -> None:
        """Wipe the graph. Used at the start of a full rebuild.

        ``preserve_sources`` names curated sources whose nodes and
        relations must survive the wipe (e.g. ``["topical_guide"]``).
        """
        ...

    def ensure_indexes(self) -> None:
        """Create any indexes / constraints the backend needs.

        Idempotent. Called once per pipeline run before writes.
        """
        ...

    # ----- Batch writes (hot path) ------------------------------------ #

    def batch_merge_documents(self, documents: list[dict[str, Any]]) -> None:
        ...

    def batch_merge_entities(self, entities: list[dict[str, Any]]) -> None:
        ...

    def batch_merge_relations(self, relations: list[dict[str, Any]]) -> None:
        ...

    def batch_link_entities_to_document(
        self, links: list[dict[str, Any]]
    ) -> None:
        """Create entity → document MENTIONED_IN edges (or equivalent)."""
        ...

    def delete_document_relations(self, file_path: str) -> None:
        """Remove all relations anchored to ``file_path`` before reindex."""
        ...

    def batch_write_all(
        self,
        delete_paths: list[str],
        documents: list[dict[str, Any]],
        entities: list[dict[str, Any]],
        links: list[dict[str, Any]],
        relations: list[dict[str, Any]],
    ) -> None:
        """Combined-batch write for the hot flush path.

        Groups deletions, document merges, entity merges, mention links and
        relation merges into a single transaction / session. Pipelines
        call this from a background thread during large ingestions.
        """
        ...

    # ----- Singular writes (curated seeds and unit tests) ------------- #

    def merge_entity(
        self,
        name: str,
        entity_type: str,
        aliases: list[str] | None = None,
    ) -> None:
        ...

    def merge_relation(
        self,
        from_name: str,
        from_type: str,
        rel_type: str,
        to_name: str,
        to_type: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        ...


def make_kg_writer() -> KnowledgeGraphWriter:
    """Return the KG writer backed by Postgres IONOS.

    Kept as a factory rather than inlining ``PostgresKGWriter()`` so
    future backend swaps (e.g. a managed Postgres, a sharded cluster)
    stay transparent to consumers.
    """
    from alejandria.storage.postgres_kg_writer import PostgresKGWriter

    return PostgresKGWriter()
