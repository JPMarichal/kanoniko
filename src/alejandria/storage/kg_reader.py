"""Knowledge-graph read Protocol for the ingestion pipeline.

Scope is intentionally minimal: only the reads the pipeline performs
during Phase 4 (profile consolidation). Production KG reads for the
search / chat layer live in
:mod:`alejandria.knowledge.postgres_graph_client` — that module is the
broader client; this Protocol narrows it to ingestion-time needs.

Split from :class:`KnowledgeGraphWriter` because the two have different
evolution pressures: reads may eventually be routed to replicas, writes
never will.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class KnowledgeGraphReader(Protocol):
    """Read operations the ingestion pipeline needs during Phase 4."""

    def get_all_entity_mentions(self) -> list[dict]:
        """Return one row per (entity, mentioning-document) pair.

        Each row carries ``entity_name``, ``entity_type``, ``file_path``
        (and optionally source, language) — enough for ProfileGenerator
        to count and aggregate per entity.
        """
        ...

    def get_disambiguated_counts(self) -> dict[tuple[str, str], dict[str, int]]:
        """Return per-entity disambiguation counts.

        Key: ``(entity_name, entity_type)`` in the non-disambiguated form.
        Value: ``{disambiguator: mention_count}`` across the corpus.
        """
        ...


def make_kg_reader() -> KnowledgeGraphReader:
    """Return the KG reader backed by Postgres IONOS.

    Kept as a factory (not a bare ``PostgresKGReader()`` import) so
    future backend swaps stay transparent to consumers.
    """
    from alejandria.storage.postgres_kg_reader import PostgresKGReader

    return PostgresKGReader()
