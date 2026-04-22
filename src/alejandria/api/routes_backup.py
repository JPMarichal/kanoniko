"""Backup and restore API endpoints (SQLite snapshot only).

The KG authoritative copy is Postgres IONOS; server-side ``pg_dump``
handles its backup (see ``docs/ionos-setup.md``). The Neo4j Cypher-export
endpoints were retired in §3.3.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from alejandria.backup import (
    backup_sqlite,
    list_sqlite_backups,
    restore_sqlite,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backup", tags=["backup"])


@router.post("/sqlite")
def create_sqlite_backup(label: str = "manual") -> dict:
    """Create a SQLite backup snapshot (includes vectors via sqlite-vec)."""
    path = backup_sqlite(label=label)
    if path is None:
        raise HTTPException(404, "SQLite database not found")
    return {"status": "ok", "file": path.name, "size_mb": round(path.stat().st_size / (1024 * 1024), 1)}


@router.get("/sqlite")
def get_sqlite_backups() -> dict:
    """List available SQLite backups."""
    backups = list_sqlite_backups()
    return {"backups": backups, "count": len(backups)}


@router.post("/sqlite/restore")
def restore_sqlite_backup(filename: str) -> dict:
    """Restore SQLite from a backup file.

    WARNING: Overwrites the current database. Stop indexing first.
    """
    backups = list_sqlite_backups()
    match = next((b for b in backups if b["file"] == filename), None)
    if match is None:
        raise HTTPException(404, f"Backup '{filename}' not found. Use GET /backup/sqlite to list.")

    ok = restore_sqlite(Path(match["path"]))
    if not ok:
        raise HTTPException(500, "Restore failed")
    return {"status": "restored", "from": filename}
