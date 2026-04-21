"""Postgres implementation of :class:`ProfileStore`.

The Postgres schema (see ``storage/postgres/ddl.sql``) normalizes the
SQLite profile model:

* ``entity_profiles`` is keyed by ``entity_id BIGINT REFERENCES entities(id)``.
  Name, type, disambiguator, aliases live in ``entities`` and
  ``entity_aliases``.
* Reads reconstruct the full :class:`EntityProfile` via JOIN.
* Writes resolve ``entity_id`` by upserting into ``entities`` first, then
  upserting the profile row, then synchronizing aliases.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from alejandria.knowledge.profile_store import EntityProfile
from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)


# Column list returned by profile SELECTs. Aliases come from a correlated
# subquery so the row shape stays flat.
_SELECT_COLS = """
    e.name                           AS entity_name,
    e.entity_type                    AS entity_type,
    e.disambiguator                  AS disambiguator,
    COALESCE(p.mention_count, 0)     AS mention_count,
    COALESCE(p.document_count, 0)    AS document_count,
    COALESCE(p.books, '[]'::jsonb)   AS books,
    COALESCE(p.key_passages, '[]'::jsonb) AS key_passages,
    p.summary_en                     AS summary_en,
    p.summary_es                     AS summary_es,
    p.disambiguation_notes           AS disambiguation_notes,
    COALESCE(p.disambiguated_counts, '{}'::jsonb) AS disambiguated_counts,
    COALESCE(p.profile_version, 0)   AS profile_version,
    COALESCE(p.status, 'metadata')   AS status,
    COALESCE(
        (SELECT jsonb_agg(alias ORDER BY alias)
         FROM entity_aliases WHERE entity_id = e.id),
        '[]'::jsonb
    )                                AS aliases
"""


def _json_loads(value: Any) -> Any:
    """psycopg3 returns JSONB as native Python objects; accept both."""
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return value
    return json.loads(value)


def _row_to_profile(row: tuple[Any, ...]) -> EntityProfile:
    (
        entity_name,
        entity_type,
        disambiguator,
        mention_count,
        document_count,
        books,
        key_passages,
        summary_en,
        summary_es,
        disambiguation_notes,
        disambiguated_counts,
        profile_version,
        status,
        aliases,
    ) = row
    return EntityProfile(
        entity_name=entity_name,
        entity_type=entity_type,
        mention_count=int(mention_count),
        document_count=int(document_count),
        books=_json_loads(books) or [],
        key_passages=_json_loads(key_passages) or [],
        aliases=_json_loads(aliases) or [],
        disambiguator=disambiguator,
        summary_en=summary_en,
        summary_es=summary_es,
        disambiguation_notes=disambiguation_notes,
        disambiguated_counts=_json_loads(disambiguated_counts) or {},
        profile_version=int(profile_version),
        status=status,
    )


class PostgresProfileStore:
    """Entity profile store backed by Postgres IONOS."""

    # ------------------------------------------------------------------ #
    # Entity resolution helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _upsert_entity(cur, name: str, entity_type: str, disambiguator: str | None) -> int:
        """Ensure an entity row exists, return its id.

        Uses the ``UNIQUE NULLS NOT DISTINCT`` constraint on
        ``(name, entity_type, disambiguator)``. The ``DO UPDATE`` is a no-op
        set so ``RETURNING id`` fires for both insert and conflict paths.
        """
        cur.execute(
            """
            INSERT INTO entities (name, entity_type, disambiguator)
            VALUES (%s, %s, %s)
            ON CONFLICT (name, entity_type, disambiguator)
                DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            (name, entity_type, disambiguator),
        )
        row = cur.fetchone()
        return int(row[0])

    @staticmethod
    def _sync_aliases(cur, entity_id: int, aliases: list[str]) -> None:
        """Replace the alias set for ``entity_id``.

        Simpler than diffing — alias lists are small (typically <10) and
        this runs under the same transaction as the profile upsert.
        """
        cur.execute("DELETE FROM entity_aliases WHERE entity_id = %s", (entity_id,))
        if not aliases:
            return
        cur.executemany(
            "INSERT INTO entity_aliases (entity_id, alias) VALUES (%s, %s) "
            "ON CONFLICT (entity_id, alias) DO NOTHING",
            [(entity_id, a) for a in aliases],
        )

    # ------------------------------------------------------------------ #
    # Write API
    # ------------------------------------------------------------------ #

    def upsert_profile(self, profile: EntityProfile) -> None:
        with get_connection() as conn, conn.cursor() as cur:
            entity_id = self._upsert_entity(
                cur, profile.entity_name, profile.entity_type, profile.disambiguator
            )
            cur.execute(
                """
                INSERT INTO entity_profiles
                    (entity_id, mention_count, document_count, books, key_passages,
                     summary_en, summary_es, disambiguation_notes,
                     disambiguated_counts, profile_version, status, updated_at)
                VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s::jsonb, %s, %s, now())
                ON CONFLICT (entity_id) DO UPDATE SET
                    mention_count         = EXCLUDED.mention_count,
                    document_count        = EXCLUDED.document_count,
                    books                 = EXCLUDED.books,
                    key_passages          = EXCLUDED.key_passages,
                    summary_en            = EXCLUDED.summary_en,
                    summary_es            = EXCLUDED.summary_es,
                    disambiguation_notes  = EXCLUDED.disambiguation_notes,
                    disambiguated_counts  = EXCLUDED.disambiguated_counts,
                    profile_version       = EXCLUDED.profile_version,
                    status                = EXCLUDED.status,
                    updated_at            = now()
                """,
                (
                    entity_id,
                    profile.mention_count,
                    profile.document_count,
                    json.dumps(profile.books, ensure_ascii=False),
                    json.dumps(profile.key_passages, ensure_ascii=False),
                    profile.summary_en,
                    profile.summary_es,
                    profile.disambiguation_notes,
                    json.dumps(profile.disambiguated_counts, ensure_ascii=False),
                    profile.profile_version,
                    profile.status,
                ),
            )
            self._sync_aliases(cur, entity_id, profile.aliases)
            conn.commit()

    def upsert_batch(self, profiles: list[EntityProfile]) -> None:
        """Batch upsert.

        Reuses :meth:`upsert_profile` under one connection/transaction.
        Postgres is fast enough here at batch sizes we see in ingestion
        (hundreds to low thousands); if profiling highlights this as a
        bottleneck, move to a CTE-based bulk upsert.

        The SQLite batch variant implements a ``profiled→stale`` downgrade
        rule — we replicate it by comparing current status before upsert.
        """
        if not profiles:
            return
        with get_connection() as conn, conn.cursor() as cur:
            # Pre-fetch existing statuses for the profiled→stale downgrade rule.
            keys = [
                (p.entity_name, p.entity_type, p.disambiguator) for p in profiles
            ]
            existing_status: dict[tuple[str, str, str | None], str] = {}
            if keys:
                cur.execute(
                    """
                    SELECT e.name, e.entity_type, e.disambiguator, p.status
                    FROM entities e
                    JOIN entity_profiles p ON p.entity_id = e.id
                    WHERE (e.name, e.entity_type, e.disambiguator) IN (
                        SELECT * FROM unnest(
                            %s::text[], %s::text[], %s::text[]
                        )
                    )
                    """,
                    (
                        [k[0] for k in keys],
                        [k[1] for k in keys],
                        [k[2] for k in keys],
                    ),
                )
                for name, etype, disamb, st in cur.fetchall():
                    existing_status[(name, etype, disamb)] = st

            for p in profiles:
                key = (p.entity_name, p.entity_type, p.disambiguator)
                effective_status = p.status
                if (
                    existing_status.get(key) == "profiled"
                    and p.status == "metadata"
                ):
                    effective_status = "stale"

                entity_id = self._upsert_entity(
                    cur, p.entity_name, p.entity_type, p.disambiguator
                )
                cur.execute(
                    """
                    INSERT INTO entity_profiles
                        (entity_id, mention_count, document_count, books, key_passages,
                         summary_en, summary_es, disambiguation_notes,
                         disambiguated_counts, profile_version, status, updated_at)
                    VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s::jsonb, %s, %s, now())
                    ON CONFLICT (entity_id) DO UPDATE SET
                        mention_count         = EXCLUDED.mention_count,
                        document_count        = EXCLUDED.document_count,
                        books                 = EXCLUDED.books,
                        key_passages          = EXCLUDED.key_passages,
                        summary_en            = COALESCE(entity_profiles.summary_en, EXCLUDED.summary_en),
                        summary_es            = COALESCE(entity_profiles.summary_es, EXCLUDED.summary_es),
                        disambiguation_notes  = COALESCE(entity_profiles.disambiguation_notes, EXCLUDED.disambiguation_notes),
                        disambiguated_counts  = EXCLUDED.disambiguated_counts,
                        profile_version       = EXCLUDED.profile_version,
                        status                = EXCLUDED.status,
                        updated_at            = now()
                    """,
                    (
                        entity_id,
                        p.mention_count,
                        p.document_count,
                        json.dumps(p.books, ensure_ascii=False),
                        json.dumps(p.key_passages, ensure_ascii=False),
                        p.summary_en,
                        p.summary_es,
                        p.disambiguation_notes,
                        json.dumps(p.disambiguated_counts, ensure_ascii=False),
                        p.profile_version,
                        effective_status,
                    ),
                )
                self._sync_aliases(cur, entity_id, p.aliases)
            conn.commit()

    # ------------------------------------------------------------------ #
    # Read API
    # ------------------------------------------------------------------ #

    def get_profile(
        self, entity_name: str, entity_type: str | None = None
    ) -> EntityProfile | None:
        with get_connection() as conn, conn.cursor() as cur:
            if entity_type:
                cur.execute(
                    f"""
                    SELECT {_SELECT_COLS}
                    FROM entities e
                    LEFT JOIN entity_profiles p ON p.entity_id = e.id
                    WHERE e.name = %s AND e.entity_type = %s
                    ORDER BY p.mention_count DESC NULLS LAST
                    LIMIT 1
                    """,
                    (entity_name, entity_type),
                )
            else:
                cur.execute(
                    f"""
                    SELECT {_SELECT_COLS}
                    FROM entities e
                    LEFT JOIN entity_profiles p ON p.entity_id = e.id
                    WHERE e.name = %s
                    ORDER BY p.mention_count DESC NULLS LAST
                    LIMIT 1
                    """,
                    (entity_name,),
                )
            row = cur.fetchone()
        return _row_to_profile(row) if row else None

    def find_profiles(
        self, search: str, entity_type: str | None = None, limit: int = 20
    ) -> list[EntityProfile]:
        with get_connection() as conn, conn.cursor() as cur:
            if entity_type:
                cur.execute(
                    f"""
                    SELECT {_SELECT_COLS}
                    FROM entities e
                    LEFT JOIN entity_profiles p ON p.entity_id = e.id
                    WHERE e.name ILIKE %s AND e.entity_type = %s
                    ORDER BY p.mention_count DESC NULLS LAST
                    LIMIT %s
                    """,
                    (f"%{search}%", entity_type, limit),
                )
            else:
                cur.execute(
                    f"""
                    SELECT {_SELECT_COLS}
                    FROM entities e
                    LEFT JOIN entity_profiles p ON p.entity_id = e.id
                    WHERE e.name ILIKE %s
                    ORDER BY p.mention_count DESC NULLS LAST
                    LIMIT %s
                    """,
                    (f"%{search}%", limit),
                )
            rows = cur.fetchall()
        return [_row_to_profile(r) for r in rows]

    def get_all(
        self,
        entity_type: str | None = None,
        status: str | None = None,
        min_mentions: int = 0,
        limit: int = 500,
        offset: int = 0,
    ) -> list[EntityProfile]:
        clauses = ["COALESCE(p.mention_count, 0) >= %s"]
        params: list[Any] = [min_mentions]
        if entity_type:
            clauses.append("e.entity_type = %s")
            params.append(entity_type)
        if status:
            clauses.append("COALESCE(p.status, 'metadata') = %s")
            params.append(status)
        where = " AND ".join(clauses)
        params.extend([limit, offset])

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT {_SELECT_COLS}
                FROM entities e
                LEFT JOIN entity_profiles p ON p.entity_id = e.id
                WHERE {where}
                ORDER BY p.mention_count DESC NULLS LAST
                LIMIT %s OFFSET %s
                """,
                params,
            )
            rows = cur.fetchall()
        return [_row_to_profile(r) for r in rows]

    def count(
        self, entity_type: str | None = None, status: str | None = None
    ) -> int:
        clauses = ["1=1"]
        params: list[Any] = []
        if entity_type:
            clauses.append("e.entity_type = %s")
            params.append(entity_type)
        if status:
            clauses.append("COALESCE(p.status, 'metadata') = %s")
            params.append(status)
        where = " AND ".join(clauses)
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT COUNT(*)
                FROM entities e
                LEFT JOIN entity_profiles p ON p.entity_id = e.id
                WHERE {where}
                """,
                params,
            )
            row = cur.fetchone()
        return int(row[0]) if row else 0

    # ------------------------------------------------------------------ #
    # Lifecycle API
    # ------------------------------------------------------------------ #

    def mark_stale(self, entity_name: str, entity_type: str) -> None:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE entity_profiles SET status = 'stale', updated_at = now()
                WHERE entity_id IN (
                    SELECT id FROM entities
                    WHERE name = %s AND entity_type = %s
                )
                """,
                (entity_name, entity_type),
            )
            conn.commit()

    def mark_all_stale(self) -> int:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE entity_profiles SET status = 'stale', updated_at = now() "
                "WHERE status = 'profiled'"
            )
            count = cur.rowcount or 0
            conn.commit()
        return count

    def delete_profile(self, entity_name: str, entity_type: str) -> None:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM entity_profiles
                WHERE entity_id IN (
                    SELECT id FROM entities
                    WHERE name = %s AND entity_type = %s
                )
                """,
                (entity_name, entity_type),
            )
            conn.commit()

    def delete_orphans(self, valid_keys: set[tuple[str, str]]) -> int:
        """Delete profiles whose (entity_name, entity_type) is not in valid_keys.

        Note: operates on ``entity_profiles`` only — the underlying ``entities``
        row is preserved (it may be referenced by relations/mentions).
        """
        if not valid_keys:
            # Nothing is valid — delete all profiles.
            with get_connection() as conn, conn.cursor() as cur:
                cur.execute("DELETE FROM entity_profiles")
                count = cur.rowcount or 0
                conn.commit()
            return count
        names = [k[0] for k in valid_keys]
        types = [k[1] for k in valid_keys]
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM entity_profiles
                WHERE entity_id NOT IN (
                    SELECT e.id FROM entities e
                    JOIN unnest(%s::text[], %s::text[]) AS v(name, entity_type)
                      ON e.name = v.name AND e.entity_type = v.entity_type
                )
                """,
                (names, types),
            )
            count = cur.rowcount or 0
            conn.commit()
        return count
