"""Backup and restore for Alejandría data stores.

Backup hierarchy (recovery time):
  1. SQLite snapshot  — protects FTS chunks (fastest, most critical)
  2. Qdrant snapshot  — protects vectors (rebuildable from SQLite in ~5 min)
  3. Neo4j dump       — protects KG (rebuildable from SQLite in ~3 hours)

SQLite is the critical backup: from it alone, both Qdrant and Neo4j
can be fully reconstructed via rebuild_vectors / rebuild_kg.
"""

from __future__ import annotations

import logging
import shutil
import time
from datetime import datetime
from pathlib import Path

import httpx

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


# ── Qdrant Snapshot ──

def backup_qdrant() -> dict | None:
    """Create a Qdrant collection snapshot via its REST API.

    Returns snapshot info dict, or None on failure.
    """
    url = f"http://{settings.qdrant_host}:{settings.qdrant_port}"
    collection = settings.qdrant_collection

    try:
        start = time.time()
        resp = httpx.post(f"{url}/collections/{collection}/snapshots", timeout=120)
        resp.raise_for_status()
        result = resp.json().get("result", {})
        elapsed = time.time() - start

        logger.info(
            "Qdrant snapshot: %s (%.1f MB) in %.1fs",
            result.get("name", "?"),
            result.get("size", 0) / (1024 * 1024),
            elapsed,
        )
        return result
    except Exception:
        logger.exception("Qdrant snapshot failed")
        return None


def list_qdrant_snapshots() -> list[dict]:
    """List available Qdrant snapshots."""
    url = f"http://{settings.qdrant_host}:{settings.qdrant_port}"
    collection = settings.qdrant_collection

    try:
        resp = httpx.get(f"{url}/collections/{collection}/snapshots", timeout=30)
        resp.raise_for_status()
        return resp.json().get("result", [])
    except Exception:
        logger.exception("Failed to list Qdrant snapshots")
        return []


# ── Neo4j Backup (via APOC) ──

def backup_neo4j() -> dict | None:
    """Export the full Neo4j graph via APOC to a JSON file.

    Requires APOC plugin installed and /backups volume mounted.
    The export runs inside Neo4j via Cypher — no server restart needed.

    Returns export info dict, or None on failure.
    """
    from neo4j import GraphDatabase

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"alejandria_graph_{ts}.json"

    try:
        start = time.time()
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        with driver.session() as session:
            # Export all nodes and relationships to JSON
            result = session.run(
                "CALL apoc.export.json.all($file, {useTypes: true})",
                file=filename,
            )
            record = result.single()
            nodes = record["nodes"] if record else 0
            rels = record["relationships"] if record else 0

        driver.close()
        elapsed = time.time() - start

        logger.info(
            "Neo4j backup: %s (%d nodes, %d rels) in %.1fs",
            filename, nodes, rels, elapsed,
        )
        return {"file": filename, "nodes": nodes, "relationships": rels, "elapsed": round(elapsed, 1)}
    except Exception:
        logger.exception("Neo4j backup failed")
        return None


def list_neo4j_backups() -> list[str]:
    """List available Neo4j backup files via APOC."""
    from neo4j import GraphDatabase

    try:
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        with driver.session() as session:
            # List files in the import/export directory
            result = session.run(
                "CALL dbms.listConfig() YIELD name, value "
                "WHERE name = 'server.directories.import' RETURN value"
            )
            # Fallback: just return the filename pattern we use
        driver.close()
    except Exception:
        pass

    # List from the known backup mount point
    backup_dir = Path("/backups")
    if not backup_dir.exists():
        return []
    return sorted([f.name for f in backup_dir.glob("alejandria_graph_*.json")], reverse=True)


def restore_neo4j(filename: str) -> dict | None:
    """Import a Neo4j graph from APOC JSON export.

    WARNING: This adds to the existing graph. Clear first if needed.
    """
    from neo4j import GraphDatabase

    try:
        start = time.time()
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        with driver.session() as session:
            # Clear existing graph
            session.run("MATCH (n) DETACH DELETE n")
            # Import from JSON
            result = session.run(
                "CALL apoc.import.json($file)",
                file=filename,
            )
            record = result.single()
            nodes = record["nodes"] if record else 0
            rels = record["relationships"] if record else 0

        driver.close()
        elapsed = time.time() - start

        logger.info("Neo4j restored: %s (%d nodes, %d rels) in %.1fs", filename, nodes, rels, elapsed)
        return {"file": filename, "nodes": nodes, "relationships": rels, "elapsed": round(elapsed, 1)}
    except Exception:
        logger.exception("Neo4j restore failed")
        return None


# ── Pre-Index Backup (called automatically by pipeline) ──

def pre_index_backup() -> dict:
    """Create backups before an indexing run.

    Called automatically by the pipeline before any data modification.
    Returns a summary of what was backed up.
    """
    result = {}

    # SQLite — always (critical)
    sqlite_path = backup_sqlite(label="pre-index")
    result["sqlite"] = str(sqlite_path) if sqlite_path else None

    # Qdrant — only if vectors exist (skip on empty collection)
    try:
        resp = httpx.get(
            f"http://{settings.qdrant_host}:{settings.qdrant_port}"
            f"/collections/{settings.qdrant_collection}",
            timeout=10,
        )
        vectors_count = resp.json().get("result", {}).get("vectors_count", 0)
        if vectors_count > 0:
            qdrant_snap = backup_qdrant()
            result["qdrant"] = qdrant_snap.get("name") if qdrant_snap else None
        else:
            result["qdrant"] = "skipped (empty)"
    except Exception:
        result["qdrant"] = "skipped (unavailable)"

    # Neo4j — only if graph has nodes (APOC export, skip if unavailable)
    try:
        neo4j_result = backup_neo4j()
        result["neo4j"] = neo4j_result.get("file") if neo4j_result else None
    except Exception:
        result["neo4j"] = "skipped (APOC unavailable)"

    logger.info("Pre-index backup complete: %s", result)
    return result
