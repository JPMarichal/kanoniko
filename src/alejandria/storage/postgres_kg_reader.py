"""Postgres implementation of :class:`KnowledgeGraphReader`.

Narrow read surface used by the ingestion pipeline's Phase 4 (profile
consolidation). Delegates to :class:`PostgresGraphClient`, which owns
the full query implementation over ``entities`` +
``entity_document_mentions``.

The broader graph reads consumed by search/chat (find_node, neighbors,
profile lookups, etc.) remain on ``PostgresGraphClient`` — this Protocol
intentionally only exposes what ingestion needs.
"""
from __future__ import annotations

from alejandria.knowledge.postgres_graph_client import PostgresGraphClient


class PostgresKGReader:
    """KG reader backed by Postgres IONOS."""

    def __init__(self, client: PostgresGraphClient | None = None) -> None:
        self._client = client or PostgresGraphClient()

    def get_all_entity_mentions(self) -> list[dict]:
        return self._client.get_all_entity_mentions()

    def get_disambiguated_counts(self) -> dict[tuple[str, str], dict[str, int]]:
        return self._client.get_disambiguated_counts()
