"""NER candidate tracking for the gazetteer feedback loop.

Tracks entities discovered by spaCy NER that are not in the curated
gazetteer. High-frequency candidates can be promoted to the gazetteer
via API.

Backend: Postgres ``ner_candidates`` table (declared in
``storage/postgres/ddl.sql``). The SQLite implementation was retired
together with the rest of the SQLite stack in §3.4.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from alejandria.storage.postgres.connection import get_connection

logger = logging.getLogger(__name__)


class NERCandidateTracker:
    """Track and manage NER-discovered entity candidates over Postgres."""

    def __init__(self) -> None:
        # Schema is declared in storage/postgres/ddl.sql and applied
        # idempotently by ``apply_schema()``. No per-instance DDL.
        pass

    # ------------------------------------------------------------------ #
    # Write
    # ------------------------------------------------------------------ #

    def record(self, name: str, entity_type: str, source_file: str = "") -> None:
        """Record an NER-discovered entity. Increments frequency if already known.

        R1/R3 gate (kg-ingestion-refactor §3): reject garbage (URLs, punct-only,
        archaic verbs, pronouns, length outliers, xref fragments, NULs) and
        canonical gazetteer matches *before touching the DB*. Prevents the
        table from refilling with noise that R0 just cleaned up.
        """
        from alejandria.knowledge.gazetteer_lookup import should_skip_ner_entity

        if should_skip_ner_entity(name) is not None:
            return

        with get_connection() as conn, conn.cursor() as cur:
            # Try to bump frequency if already present as a candidate.
            cur.execute(
                "UPDATE ner_candidates "
                "SET frequency = frequency + 1, last_seen = now() "
                "WHERE name = %s AND entity_type = %s AND status = 'candidate' "
                "RETURNING sample_files",
                (name, entity_type),
            )
            row = cur.fetchone()
            if row is None:
                # First observation (or the row is already promoted/dismissed).
                # ON CONFLICT DO NOTHING: if a non-candidate row exists, leave it.
                sample = json.dumps([source_file] if source_file else [])
                cur.execute(
                    "INSERT INTO ner_candidates "
                    "    (name, entity_type, frequency, sample_files, status, "
                    "     first_seen, last_seen) "
                    "VALUES (%s, %s, 1, %s::jsonb, 'candidate', now(), now()) "
                    "ON CONFLICT (name, entity_type) DO NOTHING",
                    (name, entity_type, sample),
                )
            elif source_file:
                # Append source file to sample (cap at 10).
                existing = row[0] if isinstance(row[0], list) else (
                    json.loads(row[0]) if row[0] else []
                )
                if source_file not in existing and len(existing) < 10:
                    existing.append(source_file)
                    cur.execute(
                        "UPDATE ner_candidates SET sample_files = %s::jsonb "
                        "WHERE name = %s AND entity_type = %s",
                        (json.dumps(existing), name, entity_type),
                    )
            conn.commit()

    # ------------------------------------------------------------------ #
    # Read
    # ------------------------------------------------------------------ #

    def get_top_candidates(
        self,
        min_frequency: int = 3,
        entity_type: str | None = None,
        limit: int = 50,
        status: str = "candidate",
    ) -> list[dict]:
        """Get top NER candidates by frequency."""
        sql = (
            "SELECT name, entity_type, frequency, sample_files, status, "
            "       first_seen, last_seen "
            "FROM ner_candidates "
            "WHERE frequency >= %s AND status = %s"
        )
        params: list = [min_frequency, status]
        if entity_type:
            sql += " AND entity_type = %s"
            params.append(entity_type)
        sql += " ORDER BY frequency DESC LIMIT %s"
        params.append(limit)

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        return [
            {
                "name": r[0],
                "type": r[1],  # keep legacy key 'type' for API clients
                "frequency": int(r[2]),
                "sample_files": (
                    r[3] if isinstance(r[3], list)
                    else (json.loads(r[3]) if r[3] else [])
                ),
                "status": r[4],
            }
            for r in rows
        ]

    def get_stats(self) -> dict:
        """Get summary statistics."""
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM ner_candidates")
            total = int(cur.fetchone()[0])

            cur.execute(
                "SELECT status, count(*) FROM ner_candidates GROUP BY status"
            )
            by_status = {row[0]: int(row[1]) for row in cur.fetchall()}

            cur.execute(
                "SELECT entity_type, count(*) FROM ner_candidates "
                "WHERE status = 'candidate' GROUP BY entity_type "
                "ORDER BY count(*) DESC"
            )
            by_type = {row[0]: int(row[1]) for row in cur.fetchall()}

            cur.execute(
                "SELECT max(frequency) FROM ner_candidates WHERE status = 'candidate'"
            )
            top_freq_row = cur.fetchone()
            top_freq = int(top_freq_row[0]) if top_freq_row and top_freq_row[0] else 0

        return {
            "total": total,
            "by_status": by_status,
            "by_type": by_type,
            "max_frequency": top_freq,
        }

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    def promote(self, name: str, entity_type: str) -> bool:
        """Promote a candidate: update status AND write to entities.json.

        This closes the feedback loop: NER discoveries become part of the
        curated gazetteer, taking effect on next KGExtractor instantiation.
        """
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE ner_candidates SET status = 'promoted', last_seen = now() "
                "WHERE name = %s AND entity_type = %s",
                (name, entity_type),
            )
            rowcount = cur.rowcount or 0
            conn.commit()
        if rowcount == 0:
            return False
        self._add_to_gazetteer(name, entity_type)
        return True

    def dismiss(self, name: str, entity_type: str) -> bool:
        """Mark a candidate as dismissed (not useful)."""
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE ner_candidates SET status = 'dismissed', last_seen = now() "
                "WHERE name = %s AND entity_type = %s",
                (name, entity_type),
            )
            rowcount = cur.rowcount or 0
            conn.commit()
        return rowcount > 0

    def prune_low_value(
        self,
        min_frequency: int = 3,
        max_age_days: int = 30,
    ) -> int:
        """Retention policy (R2, kg-ingestion-refactor §3): drop candidates that
        never reached the minimum frequency after sitting unreviewed for N days.

        Returns the number of rows deleted.
        """
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM ner_candidates "
                "WHERE status = 'candidate' "
                "  AND frequency < %s "
                "  AND last_seen < now() - (%s || ' days')::interval",
                (min_frequency, max_age_days),
            )
            deleted = cur.rowcount or 0
            conn.commit()
        return deleted

    # ------------------------------------------------------------------ #
    # Gazetteer write (unchanged; filesystem-only)
    # ------------------------------------------------------------------ #

    def _add_to_gazetteer(self, name: str, entity_type: str) -> None:
        """Append a promoted entity to entities.json."""
        gazetteer_path = (
            Path(__file__).parent / "gazetteers" / "entities.json"
        )
        try:
            data = json.loads(gazetteer_path.read_text(encoding="utf-8"))

            if entity_type not in data:
                logger.warning(
                    "Entity type '%s' not in gazetteer — skipping write for '%s'",
                    entity_type, name,
                )
                return

            existing_names = {e["name"].lower() for e in data[entity_type]}
            for entry in data[entity_type]:
                for alias in entry.get("aliases", []):
                    existing_names.add(alias.lower())

            if name.lower() in existing_names:
                logger.info("'%s' already in gazetteer — skipping", name)
                return

            data[entity_type].append({"name": name, "aliases": []})
            gazetteer_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.info(
                "Promoted '%s' (%s) → written to entities.json (%d total in type)",
                name, entity_type, len(data[entity_type]),
            )
        except Exception:
            logger.exception("Failed to write promoted entity to gazetteer")
