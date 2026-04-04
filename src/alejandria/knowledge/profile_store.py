"""SQLite storage for entity profiles — the persistent knowledge layer.

Entity profiles accumulate metadata and LLM-generated summaries per entity.
They survive KG rebuilds (which clear Neo4j) because they live in SQLite.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from alejandria.config import settings

logger = logging.getLogger(__name__)

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS entity_profiles (
    entity_name   TEXT    NOT NULL,
    entity_type   TEXT    NOT NULL,
    mention_count INTEGER NOT NULL DEFAULT 0,
    document_count INTEGER NOT NULL DEFAULT 0,
    books         TEXT    NOT NULL DEFAULT '[]',
    key_passages  TEXT    NOT NULL DEFAULT '[]',
    aliases       TEXT    NOT NULL DEFAULT '[]',
    disambiguator TEXT,
    summary_en    TEXT,
    summary_es    TEXT,
    disambiguation_notes TEXT,
    disambiguated_counts TEXT NOT NULL DEFAULT '{}',
    profile_version INTEGER NOT NULL DEFAULT 0,
    status        TEXT    NOT NULL DEFAULT 'metadata',
    PRIMARY KEY (entity_name, entity_type)
)
"""


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


class ProfileStore:
    """SQLite CRUD for entity profiles."""

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = str(db_path or settings.sqlite_db_path)
        self._ensure_table()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self) -> None:
        conn = self._get_conn()
        try:
            conn.execute(_CREATE_TABLE)
            # Migration: add disambiguated_counts column if missing (P7)
            try:
                conn.execute(
                    "ALTER TABLE entity_profiles ADD COLUMN disambiguated_counts TEXT NOT NULL DEFAULT '{}'"
                )
            except sqlite3.OperationalError:
                pass  # column already exists
            conn.commit()
        finally:
            conn.close()
        logger.debug("entity_profiles table ensured")

    def upsert_profile(self, profile: EntityProfile) -> None:
        """Insert or update an entity profile."""
        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT INTO entity_profiles
                   (entity_name, entity_type, mention_count, document_count,
                    books, key_passages, aliases, disambiguator,
                    summary_en, summary_es, disambiguation_notes,
                    disambiguated_counts, profile_version, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(entity_name, entity_type) DO UPDATE SET
                    mention_count = excluded.mention_count,
                    document_count = excluded.document_count,
                    books = excluded.books,
                    key_passages = excluded.key_passages,
                    aliases = excluded.aliases,
                    disambiguator = excluded.disambiguator,
                    summary_en = excluded.summary_en,
                    summary_es = excluded.summary_es,
                    disambiguation_notes = excluded.disambiguation_notes,
                    disambiguated_counts = excluded.disambiguated_counts,
                    profile_version = excluded.profile_version,
                    status = excluded.status
                """,
                (
                    profile.entity_name,
                    profile.entity_type,
                    profile.mention_count,
                    profile.document_count,
                    json.dumps(profile.books, ensure_ascii=False),
                    json.dumps(profile.key_passages, ensure_ascii=False),
                    json.dumps(profile.aliases, ensure_ascii=False),
                    profile.disambiguator,
                    profile.summary_en,
                    profile.summary_es,
                    profile.disambiguation_notes,
                    json.dumps(profile.disambiguated_counts, ensure_ascii=False),
                    profile.profile_version,
                    profile.status,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def upsert_batch(self, profiles: list[EntityProfile]) -> None:
        """Insert or update multiple profiles in a single transaction."""
        conn = self._get_conn()
        try:
            conn.executemany(
                """INSERT INTO entity_profiles
                   (entity_name, entity_type, mention_count, document_count,
                    books, key_passages, aliases, disambiguator,
                    summary_en, summary_es, disambiguation_notes,
                    disambiguated_counts, profile_version, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(entity_name, entity_type) DO UPDATE SET
                    mention_count = excluded.mention_count,
                    document_count = excluded.document_count,
                    books = excluded.books,
                    key_passages = excluded.key_passages,
                    aliases = excluded.aliases,
                    disambiguator = excluded.disambiguator,
                    summary_en = COALESCE(entity_profiles.summary_en, excluded.summary_en),
                    summary_es = COALESCE(entity_profiles.summary_es, excluded.summary_es),
                    disambiguation_notes = COALESCE(entity_profiles.disambiguation_notes, excluded.disambiguation_notes),
                    disambiguated_counts = excluded.disambiguated_counts,
                    profile_version = excluded.profile_version,
                    status = CASE
                        WHEN entity_profiles.status = 'profiled' AND excluded.status = 'metadata'
                        THEN 'stale'
                        ELSE excluded.status
                    END
                """,
                [
                    (
                        p.entity_name, p.entity_type, p.mention_count, p.document_count,
                        json.dumps(p.books, ensure_ascii=False),
                        json.dumps(p.key_passages, ensure_ascii=False),
                        json.dumps(p.aliases, ensure_ascii=False),
                        p.disambiguator, p.summary_en, p.summary_es,
                        p.disambiguation_notes,
                        json.dumps(p.disambiguated_counts, ensure_ascii=False),
                        p.profile_version, p.status,
                    )
                    for p in profiles
                ],
            )
            conn.commit()
        finally:
            conn.close()

    def get_profile(self, entity_name: str, entity_type: str | None = None) -> EntityProfile | None:
        """Get a single entity profile. If entity_type is None, returns first match."""
        conn = self._get_conn()
        try:
            if entity_type:
                row = conn.execute(
                    "SELECT * FROM entity_profiles WHERE entity_name = ? AND entity_type = ?",
                    (entity_name, entity_type),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM entity_profiles WHERE entity_name = ? ORDER BY mention_count DESC",
                    (entity_name,),
                ).fetchone()
            return self._row_to_profile(row) if row else None
        finally:
            conn.close()

    def find_profiles(self, search: str, entity_type: str | None = None, limit: int = 20) -> list[EntityProfile]:
        """Search profiles by partial name match."""
        conn = self._get_conn()
        try:
            if entity_type:
                rows = conn.execute(
                    "SELECT * FROM entity_profiles WHERE entity_name LIKE ? AND entity_type = ? "
                    "ORDER BY mention_count DESC LIMIT ?",
                    (f"%{search}%", entity_type, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM entity_profiles WHERE entity_name LIKE ? "
                    "ORDER BY mention_count DESC LIMIT ?",
                    (f"%{search}%", limit),
                ).fetchall()
            return [self._row_to_profile(r) for r in rows]
        finally:
            conn.close()

    def get_all(
        self,
        entity_type: str | None = None,
        status: str | None = None,
        min_mentions: int = 0,
        limit: int = 500,
        offset: int = 0,
    ) -> list[EntityProfile]:
        """List profiles with optional filters, ordered by mention_count DESC."""
        conn = self._get_conn()
        try:
            where_clauses = ["mention_count >= ?"]
            params: list = [min_mentions]

            if entity_type:
                where_clauses.append("entity_type = ?")
                params.append(entity_type)
            if status:
                where_clauses.append("status = ?")
                params.append(status)

            where = " AND ".join(where_clauses)
            params.extend([limit, offset])

            rows = conn.execute(
                f"SELECT * FROM entity_profiles WHERE {where} "
                "ORDER BY mention_count DESC LIMIT ? OFFSET ?",
                params,
            ).fetchall()
            return [self._row_to_profile(r) for r in rows]
        finally:
            conn.close()

    def count(self, entity_type: str | None = None, status: str | None = None) -> int:
        """Count profiles with optional filters."""
        conn = self._get_conn()
        try:
            where_clauses = ["1=1"]
            params: list = []
            if entity_type:
                where_clauses.append("entity_type = ?")
                params.append(entity_type)
            if status:
                where_clauses.append("status = ?")
                params.append(status)
            where = " AND ".join(where_clauses)
            row = conn.execute(f"SELECT COUNT(*) FROM entity_profiles WHERE {where}", params).fetchone()
            return row[0]
        finally:
            conn.close()

    def mark_stale(self, entity_name: str, entity_type: str) -> None:
        """Mark a single profile as stale (needs regeneration)."""
        conn = self._get_conn()
        try:
            conn.execute(
                "UPDATE entity_profiles SET status = 'stale' "
                "WHERE entity_name = ? AND entity_type = ?",
                (entity_name, entity_type),
            )
            conn.commit()
        finally:
            conn.close()

    def mark_all_stale(self) -> int:
        """Mark all profiled entries as stale. Returns count of affected rows."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "UPDATE entity_profiles SET status = 'stale' WHERE status = 'profiled'"
            )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def delete_profile(self, entity_name: str, entity_type: str) -> None:
        conn = self._get_conn()
        try:
            conn.execute(
                "DELETE FROM entity_profiles WHERE entity_name = ? AND entity_type = ?",
                (entity_name, entity_type),
            )
            conn.commit()
        finally:
            conn.close()

    def delete_orphans(self, valid_keys: set[tuple[str, str]]) -> int:
        """Delete profiles whose (entity_name, entity_type) is not in valid_keys.

        Returns count of deleted profiles.
        """
        conn = self._get_conn()
        try:
            all_rows = conn.execute(
                "SELECT entity_name, entity_type FROM entity_profiles"
            ).fetchall()
            orphans = [
                (row["entity_name"], row["entity_type"])
                for row in all_rows
                if (row["entity_name"], row["entity_type"]) not in valid_keys
            ]
            if orphans:
                conn.executemany(
                    "DELETE FROM entity_profiles WHERE entity_name = ? AND entity_type = ?",
                    orphans,
                )
                conn.commit()
            return len(orphans)
        finally:
            conn.close()

    @staticmethod
    def _row_to_profile(row: sqlite3.Row) -> EntityProfile:
        return EntityProfile(
            entity_name=row["entity_name"],
            entity_type=row["entity_type"],
            mention_count=row["mention_count"],
            document_count=row["document_count"],
            books=json.loads(row["books"]),
            key_passages=json.loads(row["key_passages"]),
            aliases=json.loads(row["aliases"]),
            disambiguator=row["disambiguator"],
            summary_en=row["summary_en"],
            summary_es=row["summary_es"],
            disambiguation_notes=row["disambiguation_notes"],
            disambiguated_counts=json.loads(row["disambiguated_counts"]) if row["disambiguated_counts"] else {},
            profile_version=row["profile_version"],
            status=row["status"],
        )
