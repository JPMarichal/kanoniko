"""Postgres implementation of :class:`KnowledgeGraphWriter`.

Thin adapter over :class:`PostgresGraphClient`, which owns the full KG
write implementation (entities, relations, documents, mentions,
clear_all). Keeping the Protocol layer separate from the concrete
client lets tests and the chat/search layer use the client directly
while the ingestion pipeline depends only on the Protocol.
"""
from __future__ import annotations

import logging
from typing import Any

from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

logger = logging.getLogger(__name__)


class PostgresKGWriter:
    """KG writer backed by Postgres IONOS."""

    def __init__(self, client: PostgresGraphClient | None = None) -> None:
        self._client = client or PostgresGraphClient()

    # ----- Lifecycle ------------------------------------------------- #

    def clear_all(self, preserve_sources: list[str] | None = None) -> None:
        self._client.clear_all(preserve_sources=preserve_sources)

    def ensure_indexes(self) -> None:
        # Postgres DDL already declares all the indexes via
        # ``storage/postgres/ddl.sql`` (entities_name_trgm, entities_type_idx,
        # relations_src_type_idx, etc.). The HNSW index on chunk_embeddings
        # is created lazily by storage.postgres.schema.ensure_hnsw_index
        # after bulk load; we invoke it here so the contract matches the
        # Legacy adapter (idempotent, safe to call every rebuild).
        from alejandria.storage.postgres import schema

        try:
            schema.ensure_hnsw_index()
        except AttributeError:
            # ensure_hnsw_index may not exist in every deployment of the
            # schema module; the base DDL already ensures the BTree/GIN
            # indexes, so this is a best-effort upgrade.
            pass

    # ----- Batch writes --------------------------------------------- #

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

    # ----- Singular writes ------------------------------------------ #

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
