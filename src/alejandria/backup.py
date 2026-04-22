"""Backup and restore for Alejandría local data stores.

Post §3.3 the authoritative KG lives in Postgres IONOS and is backed up
by ``pg_dump`` server-side (see ``docs/ionos-setup.md``). This module
covers only the transitional SQLite snapshot; the ``alejandria-neo4j``
container and its Cypher-export backup workflow were retired alongside
Neo4j itself.
"""

from __future__ import annotations

import json
import logging
import shutil
import time
from datetime import datetime
from pathlib import Path

from alejandria.config import settings

logger = logging.getLogger(__name__)

# ── Configuration ──

BACKUP_DIR = settings.sqlite_db_path.parent / "backups"
MAX_SQLITE_BACKUPS = 5  # Keep last N snapshots, rotate older ones


# ── SQLite Backup ──

def backup_sqlite(label: str = "auto") -> Path | None:
    """Create a timestamped copy of the SQLite database.

    Args:
        label: Tag for the backup (e.g., "pre-index", "manual", "auto").

    Returns:
        Path to the backup file, or None if source doesn't exist.
    """
    src = settings.sqlite_db_path
    if not src.exists():
        logger.warning("SQLite DB not found at %s — skipping backup", src)
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = BACKUP_DIR / f"alejandria_{label}_{ts}.db"

    start = time.time()
    shutil.copy2(src, dst)
    elapsed = time.time() - start

    size_mb = dst.stat().st_size / (1024 * 1024)
    logger.info("SQLite backup: %s (%.1f MB) in %.1fs", dst.name, size_mb, elapsed)

    # Rotate old backups
    _rotate_sqlite_backups()

    return dst


def restore_sqlite(backup_path: Path) -> bool:
    """Restore SQLite from a backup file.

    WARNING: This overwrites the current database. The API should be stopped
    or at minimum not indexing when this runs.

    Returns True on success.
    """
    dst = settings.sqlite_db_path
    if not backup_path.exists():
        logger.error("Backup file not found: %s", backup_path)
        return False

    start = time.time()
    shutil.copy2(backup_path, dst)
    elapsed = time.time() - start

    size_mb = dst.stat().st_size / (1024 * 1024)
    logger.info("SQLite restored from %s (%.1f MB) in %.1fs", backup_path.name, size_mb, elapsed)
    return True


def list_sqlite_backups() -> list[dict]:
    """List available SQLite backups, newest first."""
    if not BACKUP_DIR.exists():
        return []

    backups = []
    for f in sorted(BACKUP_DIR.glob("alejandria_*.db"), reverse=True):
        stat = f.stat()
        backups.append({
            "file": f.name,
            "path": str(f),
            "size_mb": round(stat.st_size / (1024 * 1024), 1),
            "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    return backups


def _rotate_sqlite_backups() -> None:
    """Keep only the last MAX_SQLITE_BACKUPS snapshots."""
    if not BACKUP_DIR.exists():
        return

    backups = sorted(BACKUP_DIR.glob("alejandria_*.db"), key=lambda p: p.stat().st_mtime)
    while len(backups) > MAX_SQLITE_BACKUPS:
        old = backups.pop(0)
        old.unlink()
        logger.info("Rotated old backup: %s", old.name)


# ── Pre-Index Backup (called automatically by pipeline) ──

def pre_index_backup() -> dict:
    """Create backups before an indexing run.

    Called automatically by the pipeline before any data modification.
    Returns a summary of what was backed up.

    Post §3.3: only the SQLite snapshot is produced. The KG authoritative
    copy lives in Postgres IONOS and is backed up server-side via
    ``pg_dump`` (see ``docs/ionos-setup.md``); there is no longer a
    per-index KG dump from this process.
    """
    result = {}

    # SQLite — always (critical; includes vectors via sqlite-vec)
    sqlite_path = backup_sqlite(label="pre-index")
    result["sqlite"] = str(sqlite_path) if sqlite_path else None

    logger.info("Pre-index backup complete: %s", result)
    return result
