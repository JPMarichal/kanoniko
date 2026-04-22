"""Migrate Document→Document parallel edges from Neo4j to Postgres.

Populates the ``document_parallels`` table added in SCHEMA_VERSION=4. Reads
three rel_types from Neo4j (PARALLEL_NARRATIVE / EDITORIAL_PARALLEL /
THEMATIC_LINK), COPYs them into Postgres in a single transaction.

Preconditions:
    * Schema v4 applied (``python -c "from alejandria.storage.postgres.schema
      import apply_schema; apply_schema()"``).
    * Neo4j reachable (container up OR uri+creds available).
    * Postgres reachable (SSH tunnel up).

Idempotent: TRUNCATE + refill. Safe to run multiple times.

Usage::

    docker run --rm --network host \\
      -v /mnt/c/own/alejandria/src:/app/src \\
      -e ALEJANDRIA_POSTGRES_HOST=127.0.0.1 \\
      -e ALEJANDRIA_POSTGRES_PORT=15432 \\
      ... \\
      -e ALEJANDRIA_NEO4J_URI=bolt://host.docker.internal:7687 \\
      docker-api python scripts/migrate_postgres_document_parallels.py
"""
from __future__ import annotations

import logging
import sys

from alejandria.knowledge.neo4j_client import Neo4jClient
from alejandria.storage.postgres.connection import get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


_REL_TYPES = ("PARALLEL_NARRATIVE", "EDITORIAL_PARALLEL", "THEMATIC_LINK")


def _fetch_edges(client: Neo4jClient) -> list[tuple[str, str, str, str | None, int | None]]:
    """Return a list of (src_file_path, dst_file_path, rel_type, narrative, layer)."""
    edges: list[tuple[str, str, str, str | None, int | None]] = []
    rel_filter = "|".join(_REL_TYPES)
    cypher = (
        f"MATCH (d:Document)-[r:{rel_filter}]->(d2:Document) "
        "RETURN d.file_path AS src, d2.file_path AS dst, type(r) AS rel_type, "
        "       r.narrative AS narrative, r.layer AS layer"
    )
    with client._driver.session() as session:  # noqa: SLF001
        result = session.run(cypher)
        for record in result:
            src = record["src"]
            dst = record["dst"]
            if not src or not dst:
                continue
            edges.append((
                src,
                dst,
                record["rel_type"],
                record.get("narrative"),
                record.get("layer"),
            ))
    return edges


def _insert_parallel_skipping_missing_docs(edges) -> tuple[int, int]:
    """Copy edges into document_parallels.

    Skips rows whose src/dst file_path isn't in document_registry (the FK
    target). Returns (inserted, skipped).
    """
    if not edges:
        return 0, 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Staging temp table (no FK) — then filter into the real table via
            # a join to document_registry so we can count skipped rows cleanly.
            cur.execute(
                "CREATE TEMP TABLE _dp_staging ("
                "  src_file_path TEXT, dst_file_path TEXT, "
                "  rel_type TEXT, narrative TEXT, layer INTEGER"
                ") ON COMMIT DROP"
            )
            with cur.copy("COPY _dp_staging FROM STDIN") as cp:
                for row in edges:
                    cp.write_row(row)

            # Idempotent: TRUNCATE + INSERT. Faster than ON CONFLICT for bulk.
            cur.execute("TRUNCATE document_parallels")
            cur.execute(
                """
                INSERT INTO document_parallels
                    (src_file_path, dst_file_path, rel_type, narrative, layer)
                SELECT s.src_file_path, s.dst_file_path, s.rel_type, s.narrative, s.layer
                FROM _dp_staging s
                WHERE EXISTS (SELECT 1 FROM document_registry r WHERE r.file_path = s.src_file_path)
                  AND EXISTS (SELECT 1 FROM document_registry r WHERE r.file_path = s.dst_file_path)
                ON CONFLICT (src_file_path, dst_file_path, rel_type) DO NOTHING
                """
            )
            inserted = cur.rowcount or 0

            cur.execute("SELECT count(*) FROM _dp_staging")
            total = cur.fetchone()[0] or 0
            skipped = total - inserted
        conn.commit()
    return inserted, skipped


def main() -> int:
    logger.info("Connecting to Neo4j…")
    client = Neo4jClient()
    try:
        logger.info("Fetching parallel edges from Neo4j…")
        edges = _fetch_edges(client)
        by_type: dict[str, int] = {}
        for _, _, rt, _, _ in edges:
            by_type[rt] = by_type.get(rt, 0) + 1
        logger.info(
            "Fetched %d edges (%s)",
            len(edges),
            ", ".join(f"{k}={v}" for k, v in sorted(by_type.items())),
        )

        if not edges:
            logger.warning("No parallel edges found in Neo4j — target remains empty.")
            return 0

        logger.info("Writing to Postgres document_parallels…")
        inserted, skipped = _insert_parallel_skipping_missing_docs(edges)
        logger.info(
            "Done: inserted=%d skipped=%d (skipped rows had src/dst not in document_registry)",
            inserted, skipped,
        )
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
