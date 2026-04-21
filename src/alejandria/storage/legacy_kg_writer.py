"""Transitional adapter: :class:`KnowledgeGraphWriter` over Neo4j.

Thin wrapper around :class:`alejandria.knowledge.neo4j_client.Neo4jClient`
with identical method signatures. Deleted together with ``Neo4jClient``
when the default backend flips to Postgres in §3.3.

``load_curated_relations`` is intentionally **not** forwarded — that
logic moved to :class:`CuratedSeedLoader` during the same PR (ADR 0001
v2: persistence vs. orchestration).
"""
from __future__ import annotations

import logging
from typing import Any

from alejandria.knowledge.neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)


class LegacyKGWriter:
    """KG writer backed by Neo4j."""

    def __init__(self, client: Neo4jClient | None = None) -> None:
        self._client = client or Neo4jClient()

    # ----- Lifecycle -------------------------------------------------- #

    def clear_all(self, preserve_sources: list[str] | None = None) -> None:
        self._client.clear_all(preserve_sources=preserve_sources)

    def ensure_indexes(self) -> None:
        # The existing ``ensure_indexes`` lives in knowledge/indexes.py and
        # consumes the Neo4j driver directly. We forward by calling it with
        # the internal driver — the helper is refactored in the same PR to
        # accept the Protocol instead, at which point this pass-through
        # disappears.
        from alejandria.knowledge.indexes import ensure_indexes

        ensure_indexes(self._client._driver)  # noqa: SLF001 — transitional

    # ----- Batch writes ---------------------------------------------- #

    def batch_merge_documents(self, documents: list[dict[str, Any]]) -> None:
        self._client.batch_merge_documents(documents)

    def batch_merge_entities(self, entities: list[dict[str, Any]]) -> None:
        self._client.batch_merge_entities(entities)

    def batch_merge_relations(self, relations: list[dict[str, Any]]) -> None:
        self._client.batch_merge_relations(relations)

    def batch_link_entities_to_document(
        self, links: list[dict[str, Any]]
    ) -> None:
        self._client.batch_link_entities_to_document(links)

    def delete_document_relations(self, file_path: str) -> None:
        self._client.delete_document_relations(file_path)

    def batch_write_all(
        self,
        delete_paths: list[str],
        documents: list[dict[str, Any]],
        entities: list[dict[str, Any]],
        links: list[dict[str, Any]],
        relations: list[dict[str, Any]],
    ) -> None:
        self._client.batch_write_all(
            delete_paths=delete_paths,
            documents=documents,
            entities=entities,
            links=links,
            relations=relations,
        )

    # ----- Singular writes ------------------------------------------- #

    def merge_entity(
        self,
        name: str,
        entity_type: str,
        aliases: list[str] | None = None,
    ) -> None:
        self._client.merge_entity(name, entity_type, aliases=aliases)

    def merge_relation(
        self,
        from_name: str,
        from_type: str,
        rel_type: str,
        to_name: str,
        to_type: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        self._client.merge_relation(
            from_name=from_name,
            from_type=from_type,
            rel_type=rel_type,
            to_name=to_name,
            to_type=to_type,
            properties=properties,
        )

    # ----- Specialized bulk loaders ---------------------------------- #
    #
    # Transitional: delegates to the existing Neo4j-only helpers in the
    # knowledge/ package. At §3.3 retirement, these helpers and this
    # adapter disappear together; the Postgres impl carries the loader
    # logic rewritten directly against pgvector/SQL.

    def load_scripture_structure(self) -> dict[str, int]:
        from alejandria.knowledge.hierarchy_loader import load_hierarchy

        return load_hierarchy(self._client._driver)  # noqa: SLF001

    def load_scripture_parallels(self) -> dict[str, int]:
        from alejandria.knowledge.parallels import load_parallels

        return load_parallels(self._client._driver)  # noqa: SLF001

    def extract_metadata_relations(self) -> dict[str, int]:
        from alejandria.knowledge.metadata_relations import (
            extract_metadata_relations,
        )

        return extract_metadata_relations(self._client._driver)  # noqa: SLF001

    def load_cross_references(self) -> dict[str, int]:
        from alejandria.knowledge.cross_ref_loader import load_cross_refs

        return load_cross_refs(self._client._driver)  # noqa: SLF001
