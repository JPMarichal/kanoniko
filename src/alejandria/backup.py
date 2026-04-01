"""Backup and restore for Alejandría data stores.

Backup hierarchy (recovery time):
  1. SQLite snapshot  — protects FTS chunks (fastest, most critical)
  2. Qdrant snapshot  — protects vectors (rebuildable from SQLite in ~5 min)
  3. Neo4j dump       — protects KG (rebuildable from SQLite in ~3 hours)

SQLite is the critical backup: from it alone, both Qdrant and Neo4j
can be fully reconstructed via rebuild_vectors / rebuild_kg.
"""

from __future__ import annotations

import json
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


# ── Neo4j Backup (via Cypher export — no APOC file access needed) ──

NEO4J_BACKUP_DIR = BACKUP_DIR.parent / "neo4j_backups"


def backup_neo4j() -> dict | None:
    """Export the full Neo4j graph to a JSON file on the API filesystem.

    Uses Cypher queries to stream all nodes and relationships back to the
    API container, then writes them to a local JSON file.  This avoids
    APOC file-export permissions entirely.

    Returns export info dict, or None on failure.
    """
    from neo4j import GraphDatabase

    NEO4J_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"alejandria_graph_{ts}.json"
    filepath = NEO4J_BACKUP_DIR / filename

    try:
        start = time.time()
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

        nodes = []
        rels = []

        with driver.session() as session:
            # Export all nodes
            result = session.run(
                "MATCH (n) RETURN id(n) AS id, labels(n) AS labels, properties(n) AS props"
            )
            for record in result:
                nodes.append({
                    "id": record["id"],
                    "labels": record["labels"],
                    "properties": record["props"],
                })

            # Export all relationships
            result = session.run(
                "MATCH (a)-[r]->(b) "
                "RETURN id(r) AS id, type(r) AS type, "
                "id(a) AS start_id, id(b) AS end_id, properties(r) AS props"
            )
            for record in result:
                rels.append({
                    "id": record["id"],
                    "type": record["type"],
                    "start_id": record["start_id"],
                    "end_id": record["end_id"],
                    "properties": record["props"],
                })

        driver.close()

        # Write to file
        export_data = {"nodes": nodes, "relationships": rels}
        filepath.write_text(json.dumps(export_data), encoding="utf-8")

        elapsed = time.time() - start
        size_mb = filepath.stat().st_size / (1024 * 1024)

        logger.info(
            "Neo4j backup: %s (%d nodes, %d rels, %.1f MB) in %.1fs",
            filename, len(nodes), len(rels), size_mb, elapsed,
        )
        return {
            "file": filename,
            "nodes": len(nodes),
            "relationships": len(rels),
            "size_mb": round(size_mb, 1),
            "elapsed": round(elapsed, 1),
        }
    except Exception:
        logger.exception("Neo4j backup failed")
        return None


def list_neo4j_backups() -> list[dict]:
    """List available Neo4j backup files, newest first."""
    if not NEO4J_BACKUP_DIR.exists():
        return []

    backups = []
    for f in sorted(NEO4J_BACKUP_DIR.glob("alejandria_graph_*.json"), reverse=True):
        stat = f.stat()
        backups.append({
            "file": f.name,
            "path": str(f),
            "size_mb": round(stat.st_size / (1024 * 1024), 1),
            "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    return backups


def restore_neo4j(filename: str) -> dict | None:
    """Restore Neo4j graph from a JSON backup.

    WARNING: This clears the existing graph and imports from the backup.
    """
    from neo4j import GraphDatabase

    # Find backup file
    filepath = NEO4J_BACKUP_DIR / filename
    if not filepath.exists():
        logger.error("Neo4j backup file not found: %s", filepath)
        return None

    try:
        start = time.time()

        export_data = json.loads(filepath.read_text(encoding="utf-8"))
        nodes_data = export_data.get("nodes", [])
        rels_data = export_data.get("relationships", [])

        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

        with driver.session() as session:
            # Clear existing graph (in batches to avoid memory issues)
            session.run("MATCH (n) DETACH DELETE n")

            # Re-create nodes — use a map of old_id -> new node for relationship wiring
            id_map = {}
            for node in nodes_data:
                labels_str = ":".join(node["labels"]) if node["labels"] else "Node"
                result = session.run(
                    f"CREATE (n:{labels_str} $props) RETURN elementId(n) AS eid",
                    props=node["properties"],
                )
                record = result.single()
                if record:
                    id_map[node["id"]] = record["eid"]

            # Re-create relationships
            rels_created = 0
            for rel in rels_data:
                start_eid = id_map.get(rel["start_id"])
                end_eid = id_map.get(rel["end_id"])
                if start_eid and end_eid:
                    session.run(
                        f"MATCH (a), (b) "
                        f"WHERE elementId(a) = $start_eid AND elementId(b) = $end_eid "
                        f"CREATE (a)-[r:{rel['type']}]->(b) "
                        f"SET r = $props",
                        start_eid=start_eid,
                        end_eid=end_eid,
                        props=rel.get("properties", {}),
                    )
                    rels_created += 1

        driver.close()
        elapsed = time.time() - start

        logger.info(
            "Neo4j restored: %s (%d nodes, %d rels) in %.1fs",
            filename, len(nodes_data), rels_created, elapsed,
        )
        return {
            "file": filename,
            "nodes": len(nodes_data),
            "relationships": rels_created,
            "elapsed": round(elapsed, 1),
        }
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
