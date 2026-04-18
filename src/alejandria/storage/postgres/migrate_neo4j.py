"""Migrate the live Neo4j KG to the Postgres backend.

Tables migrated:
    * entities          (from (:Entity) nodes)
    * entity_aliases    (from Entity.aliases property array)
    * relations         (Entity→Entity typed relations with properties)

Out of scope for this MVP:
    * Entity→Document relations (MENTIONED_IN, REFERENCED_IN, etc.) — they are
      skipped and counted. Design doc did not include a polymorphic edge table;
      reconstructing them from Postgres chunks' file_path is cheaper than
      porting 10M+ edges that point to document nodes which no longer exist as
      Entity rows.
    * Document→* edges.

Design:
    * All writes use COPY FROM STDIN.
    * Neo4j read is streamed via the driver's cursor; rows are processed one
      at a time. 820k entities + 62M relations fit in memory only via the
      (name,type)->pg_id dict (~80 MB); relations never hold all rows at once.
    * Categories are left NULL at migration time; they can be backfilled from
      knowledge/gazetteers/relations.json as part of R0 cleanup.

Run as a module::

    python -m alejandria.storage.postgres.migrate_neo4j \
        --neo4j-uri bolt://neo4j:7687 --neo4j-password alejandria --reset
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

import psycopg
from neo4j import GraphDatabase, Session

from alejandria.config import settings
from alejandria.storage.postgres.connection import get_connection
from alejandria.storage.postgres.schema import apply_schema

logger = logging.getLogger(__name__)


TARGET_TABLES_IN_FK_ORDER = (
    "entities",
    "entity_aliases",
    "relations",
    "entity_document_mentions",
)


@dataclass
class KGReport:
    entities: int = 0
    aliases: int = 0
    relations: int = 0
    mentions: int = 0
    skipped_doc_edges: int = 0
    skipped_unknown_endpoint: int = 0
    skipped_mentions_unknown_entity: int = 0
    skipped_mentions_unknown_file: int = 0
    seconds: dict[str, float] = field(default_factory=dict)
    profiles_resolved: int = 0

    def summary(self) -> str:
        lines = [
            "Neo4j → Postgres migration summary:",
            f"  entities        {self.entities:>12,} rows  {self.seconds.get('entities', 0):7.1f}s",
            f"  entity_aliases  {self.aliases:>12,} rows  {self.seconds.get('entity_aliases', 0):7.1f}s",
            f"  relations       {self.relations:>12,} rows  {self.seconds.get('relations', 0):7.1f}s",
            f"  mentions (E→D)  {self.mentions:>12,} rows  {self.seconds.get('mentions', 0):7.1f}s",
        ]
        if self.skipped_doc_edges:
            lines.append(f"  (skipped {self.skipped_doc_edges:,} Entity→Document edges NOT MENTIONED_IN)")
        if self.skipped_unknown_endpoint:
            lines.append(f"  (skipped {self.skipped_unknown_endpoint:,} edges with unknown endpoints)")
        if self.skipped_mentions_unknown_entity:
            lines.append(f"  (skipped {self.skipped_mentions_unknown_entity:,} mentions: entity not in id_map)")
        if self.skipped_mentions_unknown_file:
            lines.append(f"  (skipped {self.skipped_mentions_unknown_file:,} mentions: file_path not in document_registry)")
        if self.profiles_resolved:
            lines.append(f"  staged profiles resolved: {self.profiles_resolved}")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

@contextmanager
def open_neo4j(uri: str, user: str, password: str) -> Iterator[Session]:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session(default_access_mode="READ") as session:
            yield session
    finally:
        driver.close()


def _normalize_aliases(raw) -> list[str]:
    """Neo4j returns list[str] or None. Dedup + non-empty."""
    if not raw:
        return []
    seen = set()
    out = []
    for a in raw:
        if isinstance(a, str) and a.strip() and a not in seen:
            seen.add(a)
            out.append(a)
    return out


def _reset_or_verify(pg: psycopg.Connection, reset: bool) -> None:
    with pg.cursor() as cur:
        if reset:
            cur.execute(
                "TRUNCATE " + ", ".join(TARGET_TABLES_IN_FK_ORDER) + " RESTART IDENTITY CASCADE"
            )
            logger.info("Target tables truncated (reset=True)")
            pg.commit()
            return
        for t in TARGET_TABLES_IN_FK_ORDER:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            n = cur.fetchone()[0]
            if n > 0:
                raise RuntimeError(
                    f"Target table {t!r} has {n} rows; re-run with --reset to truncate."
                )


# --------------------------------------------------------------------------- #
# Migrators
# --------------------------------------------------------------------------- #

def migrate_entities(
    neo4j: Session, pg: psycopg.Connection
) -> tuple[dict[tuple[str, str], int], int, int, float]:
    """Bulk-migrate Entity nodes to the entities table.

    Returns (id_map, entity_count, alias_count, elapsed). id_map[(name,type)] = pg_id.
    """
    t0 = time.perf_counter()
    id_map: dict[tuple[str, str], int] = {}

    # --- entities ---
    n_entities = 0
    with pg.cursor().copy(
        "COPY entities (name, entity_type, disambiguator) FROM STDIN"
    ) as cp:
        result = neo4j.run(
            "MATCH (e:Entity) "
            "RETURN e.name AS name, e.type AS type, e.disambiguator AS disambiguator"
        )
        # We want to preserve Neo4j's ordering so that the sequence assigns
        # stable ids. psycopg returns no IDs from COPY; we fetch them right after.
        for rec in result:
            cp.write_row((rec["name"], rec["type"], rec.get("disambiguator")))
            n_entities += 1
            if n_entities % 100_000 == 0:
                logger.info("  … %d entities copied", n_entities)
    pg.commit()
    logger.info("entities: %d rows copied, now building id_map…", n_entities)

    # --- build id_map from the loaded table ---
    with pg.cursor() as cur:
        cur.execute("SELECT id, name, entity_type FROM entities")
        for eid, name, etype in cur:
            id_map[(name, etype)] = eid
    logger.info("id_map built with %d entries", len(id_map))

    # --- aliases (re-query Neo4j for nodes that have them) ---
    n_aliases = 0
    with pg.cursor().copy(
        "COPY entity_aliases (entity_id, alias) FROM STDIN"
    ) as cp:
        result = neo4j.run(
            "MATCH (e:Entity) WHERE e.aliases IS NOT NULL AND size(e.aliases) > 0 "
            "RETURN e.name AS name, e.type AS type, e.aliases AS aliases"
        )
        for rec in result:
            key = (rec["name"], rec["type"])
            eid = id_map.get(key)
            if eid is None:
                continue
            for alias in _normalize_aliases(rec["aliases"]):
                cp.write_row((eid, alias))
                n_aliases += 1
    pg.commit()

    return id_map, n_entities, n_aliases, time.perf_counter() - t0


def migrate_relations(
    neo4j: Session,
    pg: psycopg.Connection,
    id_map: dict[tuple[str, str], int],
) -> tuple[int, int, int, float]:
    """Bulk-migrate Entity→Entity typed relations to the relations table.

    Returns (relations_copied, skipped_doc_edges, skipped_unknown, elapsed).
    """
    t0 = time.perf_counter()
    copied = 0
    skipped_doc = 0
    skipped_unknown = 0

    # This COPY streams 50M+ rows and routinely exceeds any reasonable
    # statement_timeout. Disable it for this session/transaction only; the
    # setting is session-scoped and the connection is closed at the end.
    with pg.cursor() as cur:
        cur.execute("SET statement_timeout = 0")

    # Streaming query covers *only* Entity→Entity edges; Document-targeted
    # edges are filtered by the WHERE clause so Neo4j does not stream them.
    cypher = (
        "MATCH (a:Entity)-[r]->(b:Entity) "
        "RETURN a.name AS src_name, a.type AS src_type, "
        "       b.name AS dst_name, b.type AS dst_type, "
        "       type(r) AS rel_type, "
        "       r.source_ref AS source_ref, r.confidence AS confidence, "
        "       r.source AS source, r.verified AS verified, r.role AS role, "
        "       properties(r) AS all_props"
    )
    # Count Entity→Document edges separately (single query, not streamed).
    with pg.cursor().copy(
        "COPY relations (src_id, dst_id, rel_type, confidence, source_ref, source, "
        "verified, role, properties) FROM STDIN"
    ) as cp:
        result = neo4j.run(cypher)
        for rec in result:
            src_id = id_map.get((rec["src_name"], rec["src_type"]))
            dst_id = id_map.get((rec["dst_name"], rec["dst_type"]))
            if src_id is None or dst_id is None:
                skipped_unknown += 1
                continue
            props = rec["all_props"] or {}
            # Remove surfaced props so `properties` JSONB only has leftovers
            surfaced = {"source_ref", "confidence", "source", "verified", "role"}
            leftovers = {k: v for k, v in props.items() if k not in surfaced}
            verified = rec["verified"]
            if verified is None:
                verified = False
            cp.write_row((
                src_id,
                dst_id,
                rec["rel_type"],
                rec["confidence"] or "llm_low",
                rec["source_ref"],
                rec["source"],
                verified,
                rec["role"],
                json.dumps(leftovers, ensure_ascii=False),
            ))
            copied += 1
            if copied % 1_000_000 == 0:
                logger.info("  … %d relations copied", copied)
    pg.commit()

    # Count skipped Entity→Document edges (for reporting — fast aggregate).
    skipped_doc_res = neo4j.run(
        "MATCH (:Entity)-[r]->(:Document) RETURN count(r) AS n"
    ).single()
    skipped_doc = int(skipped_doc_res["n"]) if skipped_doc_res else 0

    return copied, skipped_doc, skipped_unknown, time.perf_counter() - t0


def migrate_entity_document_mentions(
    neo4j: Session,
    pg: psycopg.Connection,
    id_map: dict[tuple[str, str], int] | None = None,
) -> tuple[int, int, int, float]:
    """Migrate `Entity-[:MENTIONED_IN]->Document` edges to `entity_document_mentions`.

    Added in SCHEMA_VERSION=2 to unlock 4 methods blocked by the initial design
    decision to skip Entity→Document edges
    (see docs/kg-client-port-audit.md §6.1 Option A).

    Args:
        neo4j: open Neo4j session.
        pg: open Postgres connection (writes).
        id_map: optional pre-built (name, type) → pg_id dict. If None, loaded
            from Postgres — useful when this function runs standalone, i.e.
            after a previous full migration without this step.

    Returns:
        (copied, skipped_unknown_entity, skipped_unknown_file, elapsed_seconds).
    """
    t0 = time.perf_counter()

    # Load id_map from Postgres if not provided (standalone re-run).
    if id_map is None:
        id_map = {}
        with pg.cursor() as cur:
            cur.execute("SELECT id, name, entity_type FROM entities")
            for eid, name, etype in cur:
                id_map[(name, etype)] = eid
        logger.info("id_map built from Postgres with %d entries", len(id_map))

    # Load valid file_paths to skip mentions that don't match any document_registry.
    # Neo4j Documents may have been created for paths that never reached SQLite.
    valid_paths: set[str] = set()
    with pg.cursor() as cur:
        cur.execute("SELECT file_path FROM document_registry")
        for row in cur:
            valid_paths.add(row[0])
    logger.info("valid file_paths loaded: %d", len(valid_paths))

    # Disable statement timeout for the COPY (same rationale as relations).
    with pg.cursor() as cur:
        cur.execute("SET statement_timeout = 0")

    copied = 0
    skipped_entity = 0
    skipped_file = 0
    seen: set[tuple[int, str, str]] = set()  # dedup for composite PK

    cypher = (
        "MATCH (e:Entity)-[r:MENTIONED_IN]->(d:Document) "
        "RETURN e.name AS name, e.type AS type, d.file_path AS file_path, "
        "       r.resolved_name AS resolved_name, r.confidence AS confidence"
    )

    with pg.cursor().copy(
        "COPY entity_document_mentions (entity_id, file_path, resolved_name, confidence) FROM STDIN"
    ) as cp:
        result = neo4j.run(cypher)
        for rec in result:
            entity_key = (rec["name"], rec["type"])
            eid = id_map.get(entity_key)
            if eid is None:
                skipped_entity += 1
                continue
            file_path = rec["file_path"]
            if file_path not in valid_paths:
                skipped_file += 1
                continue
            resolved_name = rec["resolved_name"] or ""
            pk = (eid, file_path, resolved_name)
            if pk in seen:
                # Neo4j normally collapses to 1 edge via MERGE, but defensive
                # against any residual duplicates.
                continue
            seen.add(pk)
            cp.write_row((eid, file_path, resolved_name, rec["confidence"]))
            copied += 1
            if copied % 500_000 == 0:
                logger.info("  … %d mentions copied", copied)
    pg.commit()

    return copied, skipped_entity, skipped_file, time.perf_counter() - t0


def resolve_staged_profiles(
    pg: psycopg.Connection,
    id_map: dict[tuple[str, str], int],
) -> int:
    """If the SQLite migrator staged entity_profiles, resolve entity_id now.

    The staging temp table is session-scoped; this function only does work if
    the caller passed the same connection used for the SQLite migration. For
    normal migration flow (separate connection), this is a no-op returning 0.
    """
    with pg.cursor() as cur:
        cur.execute(
            "SELECT to_regclass('pg_temp._staging_profiles') IS NOT NULL AS present"
        )
        present = cur.fetchone()[0]
        if not present:
            return 0
        cur.execute(
            "INSERT INTO entity_profiles "
            "  (entity_id, mention_count, document_count, books, key_passages, "
            "   summary_en, summary_es, disambiguation_notes, disambiguated_counts, "
            "   profile_version, status) "
            "SELECT e.id, s.mention_count, s.document_count, s.books, s.key_passages, "
            "       s.summary_en, s.summary_es, s.disambiguation_notes, s.disambiguated_counts, "
            "       s.profile_version, s.status "
            "FROM _staging_profiles s "
            "JOIN entities e ON e.name = s.entity_name AND e.entity_type = s.entity_type"
        )
        resolved = cur.rowcount or 0
    pg.commit()
    return resolved


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #

def migrate_all(
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    pg_conn: psycopg.Connection | None = None,
    reset: bool = False,
    apply_ddl: bool = True,
) -> KGReport:
    report = KGReport()
    close_after = pg_conn is None
    if pg_conn is None:
        cm = get_connection()
        pg_conn = cm.__enter__()
    try:
        if apply_ddl:
            apply_schema(pg_conn, notes="neo4j migration")
        _reset_or_verify(pg_conn, reset)

        with open_neo4j(neo4j_uri, neo4j_user, neo4j_password) as neo4j:
            id_map, n_ent, n_al, t = migrate_entities(neo4j, pg_conn)
            report.entities = n_ent
            report.aliases = n_al
            report.seconds["entities"] = t
            logger.info("entities: %d + %d aliases in %.1fs", n_ent, n_al, t)

            n_rel, n_skip_doc, n_skip_unknown, t = migrate_relations(neo4j, pg_conn, id_map)
            report.relations = n_rel
            report.skipped_doc_edges = n_skip_doc
            report.skipped_unknown_endpoint = n_skip_unknown
            report.seconds["relations"] = t
            logger.info(
                "relations: %d in %.1fs (skipped %d Entity→Document, %d unknown)",
                n_rel, t, n_skip_doc, n_skip_unknown,
            )

            report.profiles_resolved = resolve_staged_profiles(pg_conn, id_map)
            if report.profiles_resolved:
                logger.info("staged profiles resolved: %d", report.profiles_resolved)

            # SCHEMA_VERSION=2 — Entity→Document mentions
            n_m, n_skip_e, n_skip_f, t_m = migrate_entity_document_mentions(
                neo4j, pg_conn, id_map=id_map,
            )
            report.mentions = n_m
            report.skipped_mentions_unknown_entity = n_skip_e
            report.skipped_mentions_unknown_file = n_skip_f
            report.seconds["mentions"] = t_m
            logger.info(
                "mentions: %d in %.1fs (skipped %d unknown entity, %d unknown file)",
                n_m, t_m, n_skip_e, n_skip_f,
            )
    finally:
        if close_after:
            pg_conn.close()
    return report


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Migrate live Neo4j KG to Postgres.")
    parser.add_argument(
        "--neo4j-uri", default=settings.neo4j_uri,
        help=f"Neo4j bolt URI (default from settings: {settings.neo4j_uri})",
    )
    parser.add_argument(
        "--neo4j-user", default=settings.neo4j_user,
        help=f"Neo4j username (default: {settings.neo4j_user})",
    )
    parser.add_argument(
        "--neo4j-password", default=settings.neo4j_password,
        help="Neo4j password (defaults from settings)",
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="TRUNCATE target tables before load.",
    )
    parser.add_argument(
        "--no-schema", action="store_true",
        help="Skip apply_schema().",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    report = migrate_all(
        neo4j_uri=args.neo4j_uri,
        neo4j_user=args.neo4j_user,
        neo4j_password=args.neo4j_password,
        reset=args.reset,
        apply_ddl=not args.no_schema,
    )
    print(report.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
