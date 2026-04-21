"""Entity profile store — persistent knowledge layer for entity metadata.

Profiles accumulate per-entity aggregates (mention counts, key passages,
LLM-generated summaries, disambiguation notes). They survive KG rebuilds.

This module exposes a :class:`ProfileStore` Protocol and a
:func:`make_profile_store` factory dispatching on ``settings.storage_backend``.
Concrete implementations:

* :mod:`alejandria.knowledge.postgres_profile_store` — Postgres IONOS (target).
* :mod:`alejandria.knowledge.sqlite_profile_store` — legacy SQLite (transitional,
  retired in §3.4 of ``docs/ingestion-workflow.md``).

The :class:`EntityProfile` dataclass is backend-neutral. In Postgres the
``entity_name`` / ``entity_type`` / ``disambiguator`` / ``aliases`` fields
are stored in the ``entities`` + ``entity_aliases`` tables and joined on
read; in SQLite they live as columns on ``entity_profiles``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass
class EntityProfile:
    entity_name: str
    entity_type: str
    mention_count: int = 0
    document_count: int = 0
    books: list[str] = field(default_factory=list)
    key_passages: list[dict] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    disambiguator: str | None = None
    summary_en: str | None = None
    summary_es: str | None = None
    disambiguation_notes: str | None = None
    disambiguated_counts: dict[str, int] = field(default_factory=dict)
    profile_version: int = 0
    status: str = "metadata"

    def to_dict(self) -> dict:
        return {
            "entity_name": self.entity_name,
            "entity_type": self.entity_type,
            "mention_count": self.mention_count,
            "document_count": self.document_count,
            "books": self.books,
            "key_passages": self.key_passages,
            "aliases": self.aliases,
            "disambiguator": self.disambiguator,
            "summary_en": self.summary_en,
            "summary_es": self.summary_es,
            "disambiguation_notes": self.disambiguation_notes,
            "disambiguated_counts": self.disambiguated_counts,
            "profile_version": self.profile_version,
            "status": self.status,
        }


@runtime_checkable
class ProfileStore(Protocol):
    """CRUD interface for entity profiles."""

    def upsert_profile(self, profile: EntityProfile) -> None: ...

    def upsert_batch(self, profiles: list[EntityProfile]) -> None: ...

    def get_profile(
        self, entity_name: str, entity_type: str | None = None
    ) -> EntityProfile | None: ...

    def find_profiles(
        self, search: str, entity_type: str | None = None, limit: int = 20
    ) -> list[EntityProfile]: ...

    def get_all(
        self,
        entity_type: str | None = None,
        status: str | None = None,
        min_mentions: int = 0,
        limit: int = 500,
        offset: int = 0,
    ) -> list[EntityProfile]: ...

    def count(
        self, entity_type: str | None = None, status: str | None = None
    ) -> int: ...

    def mark_stale(self, entity_name: str, entity_type: str) -> None: ...

    def mark_all_stale(self) -> int: ...

    def delete_profile(self, entity_name: str, entity_type: str) -> None: ...

    def delete_orphans(self, valid_keys: set[tuple[str, str]]) -> int: ...


def make_profile_store(db_path: Path | None = None) -> ProfileStore:
    """Return the profile store selected by ``settings.storage_backend``.

    * ``"postgres"`` — :class:`PostgresProfileStore` over Postgres IONOS.
      ``db_path`` is ignored.
    * ``"sqlite"`` (legacy) — :class:`SqliteProfileStore` at ``db_path``
      or ``settings.sqlite_db_path`` if not provided.
    """
    from alejandria.config import settings

    backend = (settings.storage_backend or "postgres").lower()
    if backend == "postgres":
        from alejandria.knowledge.postgres_profile_store import PostgresProfileStore

        return PostgresProfileStore()
    from alejandria.knowledge.sqlite_profile_store import SqliteProfileStore

    return SqliteProfileStore(db_path)
