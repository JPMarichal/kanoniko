"""Transitional adapter: :class:`KnowledgeGraphReader` over Neo4j.

Narrow read-side facade that forwards the two ingestion-phase queries to
:class:`alejandria.knowledge.neo4j_client.Neo4jClient`. Deleted together
with the Neo4j client in §3.3.
"""
from __future__ import annotations

from alejandria.knowledge.neo4j_client import Neo4jClient


class LegacyKGReader:
    """KG reader backed by Neo4j."""

    def __init__(self, client: Neo4jClient | None = None) -> None:
        self._client = client or Neo4jClient()

    def get_all_entity_mentions(self) -> list[dict]:
        return self._client.get_all_entity_mentions()

    def get_disambiguated_counts(self) -> dict[tuple[str, str], dict[str, int]]:
        return self._client.get_disambiguated_counts()
