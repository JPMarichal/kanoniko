"""One-shot migration v2 → v3: switch entities unique constraint to
NULLS NOT DISTINCT so ``ON CONFLICT`` upserts work with NULL disambiguator.

Safe preconditions (verified 2026-04-19 on IONOS):
  * Postgres 15+ (we run 16.13)
  * No duplicate ``(name, entity_type)`` rows with disambiguator IS NULL
    (query: SELECT count(*) FROM (SELECT ... HAVING count(*) > 1) → 0)

Idempotent: if the constraint is already NULLS NOT DISTINCT, the script
detects it and exits without touching anything.

Run via Docker or any env with psycopg + ALEJANDRIA_POSTGRES_* exported.
"""
from __future__ import annotations

import logging
import sys

from alejandria.storage.postgres.connection import get_connection
from alejandria.storage.postgres.schema import apply_schema

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("migrate_pg_schema_v3")

CONSTRAINT_NAME = "entities_name_entity_type_disambiguator_key"


def _is_nulls_not_distinct(cur) -> bool:
    """Inspect pg_constraint to check the current flag."""
    cur.execute(
        """
        SELECT conindid::regclass::text, pg_get_constraintdef(oid)
          FROM pg_constraint
         WHERE conname = %s
        """,
        (CONSTRAINT_NAME,),
    )
    row = cur.fetchone()
    if row is None:
        raise RuntimeError(f"constraint {CONSTRAINT_NAME} not found on entities")
    definition = row[1] or ""
    return "NULLS NOT DISTINCT" in definition.upper()


def _count_null_disambig_duplicates(cur) -> int:
    cur.execute(
        """
        SELECT count(*)
          FROM (
              SELECT name, entity_type
                FROM entities
               WHERE disambiguator IS NULL
               GROUP BY name, entity_type
              HAVING count(*) > 1
          ) x
        """,
    )
    return cur.fetchone()[0]


def main() -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            if _is_nulls_not_distinct(cur):
                logger.info("entities constraint already NULLS NOT DISTINCT — nothing to do.")
            else:
                dup = _count_null_disambig_duplicates(cur)
                if dup > 0:
                    logger.error(
                        "ABORT: %d duplicate (name, entity_type) groups with NULL "
                        "disambiguator. Dedupe them before re-running.", dup,
                    )
                    return 2

                logger.info("Dropping old constraint %s…", CONSTRAINT_NAME)
                cur.execute(f"ALTER TABLE entities DROP CONSTRAINT {CONSTRAINT_NAME}")
                logger.info("Adding NULLS NOT DISTINCT constraint…")
                cur.execute(
                    f"ALTER TABLE entities ADD CONSTRAINT {CONSTRAINT_NAME} "
                    f"UNIQUE NULLS NOT DISTINCT (name, entity_type, disambiguator)"
                )
                conn.commit()
                logger.info("Constraint swapped.")

    # Stamp schema version.
    v = apply_schema(notes="v3 — NULLS NOT DISTINCT on entities unique")
    logger.info("Schema stamped: v%d", v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
