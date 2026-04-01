"""NER candidate tracking for gazetteer feedback loop.

Tracks entities discovered by spaCy NER that are not in the curated gazetteer.
High-frequency candidates can be promoted to the gazetteer via API.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

_DB_PATH_DEFAULT = Path(__file__).resolve().parent.parent.parent.parent / "data" / "sqlite" / "alejandria.db"


class NERCandidateTracker:
    """Track and manage NER-discovered entity candidates."""

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or _DB_PATH_DEFAULT
        self._ensure_table()

    def _ensure_table(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ner_candidates (
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    sample_files TEXT DEFAULT '[]',
                    status TEXT DEFAULT 'candidate',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (name, type)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ner_freq
                ON ner_candidates(frequency DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ner_status
                ON ner_candidates(status)
            """)

    def record(self, name: str, entity_type: str, source_file: str = "") -> None:
        """Record an NER-discovered entity. Increments frequency if already known."""
        with sqlite3.connect(self._db_path) as conn:
            # Try to update existing
            cursor = conn.execute(
                "UPDATE ner_candidates SET frequency = frequency + 1, "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE name = ? AND type = ? AND status = 'candidate'",
                (name, entity_type),
            )
            if cursor.rowcount == 0:
                # Insert new
                sample = json.dumps([source_file] if source_file else [])
                conn.execute(
                    "INSERT OR IGNORE INTO ner_candidates (name, type, sample_files) "
                    "VALUES (?, ?, ?)",
                    (name, entity_type, sample),
                )
            elif source_file:
                # Append source file to sample (up to 10)
                row = conn.execute(
                    "SELECT sample_files FROM ner_candidates WHERE name = ? AND type = ?",
                    (name, entity_type),
                ).fetchone()
                if row:
                    files = json.loads(row[0])
                    if source_file not in files and len(files) < 10:
                        files.append(source_file)
                        conn.execute(
                            "UPDATE ner_candidates SET sample_files = ? "
                            "WHERE name = ? AND type = ?",
                            (json.dumps(files), name, entity_type),
                        )

    def get_top_candidates(
        self, min_frequency: int = 3, entity_type: str | None = None,
        limit: int = 50, status: str = "candidate",
    ) -> list[dict]:
        """Get top NER candidates by frequency."""
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = (
                "SELECT name, type, frequency, sample_files, status, "
                "created_at, updated_at "
                "FROM ner_candidates "
                "WHERE frequency >= ? AND status = ?"
            )
            params: list = [min_frequency, status]
            if entity_type:
                query += " AND type = ?"
                params.append(entity_type)
            query += " ORDER BY frequency DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [
                {
                    "name": r["name"],
                    "type": r["type"],
                    "frequency": r["frequency"],
                    "sample_files": json.loads(r["sample_files"]),
                    "status": r["status"],
                }
                for r in rows
            ]

    def promote(self, name: str, entity_type: str) -> bool:
        """Promote a candidate: update SQLite status AND write to entities.json.

        This closes the feedback loop: NER discoveries become part of the
        curated gazetteer, taking effect on next KGExtractor instantiation.
        """
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                "UPDATE ner_candidates SET status = 'promoted', "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE name = ? AND type = ?",
                (name, entity_type),
            )
            if cursor.rowcount == 0:
                return False

        # Write to gazetteer file
        self._add_to_gazetteer(name, entity_type)
        return True

    def _add_to_gazetteer(self, name: str, entity_type: str) -> None:
        """Append a promoted entity to entities.json."""
        gazetteer_path = (
            Path(__file__).parent / "gazetteers" / "entities.json"
        )
        try:
            data = json.loads(gazetteer_path.read_text(encoding="utf-8"))

            # Skip if entity type doesn't exist in gazetteer
            if entity_type not in data:
                logger.warning(
                    "Entity type '%s' not in gazetteer — skipping write for '%s'",
                    entity_type, name,
                )
                return

            # Skip if already present (by name, case-insensitive)
            existing_names = {
                e["name"].lower() for e in data[entity_type]
            }
            for entry in data[entity_type]:
                for alias in entry.get("aliases", []):
                    existing_names.add(alias.lower())

            if name.lower() in existing_names:
                logger.info("'%s' already in gazetteer — skipping", name)
                return

            # Add new entry
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

    def dismiss(self, name: str, entity_type: str) -> bool:
        """Mark a candidate as dismissed (not useful)."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                "UPDATE ner_candidates SET status = 'dismissed', "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE name = ? AND type = ?",
                (name, entity_type),
            )
            return cursor.rowcount > 0

    def get_stats(self) -> dict:
        """Get summary statistics."""
        with sqlite3.connect(self._db_path) as conn:
            total = conn.execute("SELECT count(*) FROM ner_candidates").fetchone()[0]
            by_status = conn.execute(
                "SELECT status, count(*) as cnt FROM ner_candidates GROUP BY status"
            ).fetchall()
            by_type = conn.execute(
                "SELECT type, count(*) as cnt FROM ner_candidates "
                "WHERE status = 'candidate' GROUP BY type ORDER BY cnt DESC"
            ).fetchall()
            top_freq = conn.execute(
                "SELECT max(frequency) FROM ner_candidates WHERE status = 'candidate'"
            ).fetchone()[0]

            return {
                "total": total,
                "by_status": {r[0]: r[1] for r in by_status},
                "by_type": {r[0]: r[1] for r in by_type},
                "max_frequency": top_freq or 0,
            }
