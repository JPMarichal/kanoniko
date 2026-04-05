"""Backup and restore API endpoints."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from alejandria.backup import (
    backup_neo4j,
    backup_sqlite,
    list_neo4j_backups,
    list_sqlite_backups,
    restore_neo4j,
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


@router.post("/neo4j")
def create_neo4j_backup() -> dict:
    """Export Neo4j graph via Cypher to JSON. No server restart needed."""
    result = backup_neo4j()
    if result is None:
        raise HTTPException(500, "Neo4j backup failed")
    return {"status": "ok", **result}


@router.get("/neo4j")
def get_neo4j_backups() -> dict:
    """List available Neo4j backup files."""
    backups = list_neo4j_backups()
    return {"backups": backups, "count": len(backups)}


@router.post("/neo4j/restore")
def restore_neo4j_backup(filename: str) -> dict:
    """Restore Neo4j graph from JSON backup.

    WARNING: This clears the existing graph and imports from the backup.
    """
    backups = list_neo4j_backups()
    match = next((b for b in backups if b["file"] == filename), None)
    if match is None:
        raise HTTPException(404, f"Backup '{filename}' not found. Use GET /backup/neo4j to list.")

    result = restore_neo4j(filename)
    if result is None:
        raise HTTPException(500, "Neo4j restore failed")
    return {"status": "restored", **result}
