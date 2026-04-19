"""Clean up the over-inferred MOTHER_OF edges and edges with conjunction-only
names that were created by the first family-backfill + inference pass before
the polygamy fix.

Specifically removes:
  1. MOTHER_OF relations sourced as 'family_inference' (the rule was dropped).
  2. Any family relation where either endpoint's name is a bare conjunction
     (And, But, Now, Then, Y, Pero, Entonces, etc.) — those are NER fumbles.
  3. Self-loops among family relations (A -X-> A).

Idempotent; safe to re-run.
"""
from __future__ import annotations

import os
import psycopg

CONJUNCTION_NAMES = [
    "And", "But", "Now", "Then", "For", "So", "Yet", "Also",
    "Behold", "Verily",
    "Y", "Pero", "Entonces", "Luego", "Porque", "Mas", "Sino",
    "Shared", "Named",
]

FAMILY_RELS = ("FATHER_OF", "MOTHER_OF", "BROTHER_OF", "SISTER_OF", "SPOUSE_OF")

with psycopg.connect(
    host=os.environ["ALEJANDRIA_POSTGRES_HOST"],
    port=int(os.environ["ALEJANDRIA_POSTGRES_PORT"]),
    user=os.environ["ALEJANDRIA_POSTGRES_USER"],
    password=os.environ["ALEJANDRIA_POSTGRES_PASSWORD"],
    dbname=os.environ["ALEJANDRIA_POSTGRES_DB"],
) as c:
    # Step 1: drop MOTHER_OF edges from family_inference (polygamy-unsafe rule).
    cur = c.execute(
        "DELETE FROM relations "
        "WHERE rel_type = 'MOTHER_OF' AND source = 'family_inference'"
    )
    print(f"Deleted {cur.rowcount} incorrectly-inferred MOTHER_OF edges")

    # Step 2: drop family edges where either side is a bare conjunction.
    cur = c.execute(
        "DELETE FROM relations r "
        "USING entities e "
        "WHERE r.rel_type = ANY(%s) "
        "  AND (r.src_id = e.id OR r.dst_id = e.id) "
        "  AND e.name = ANY(%s)",
        (list(FAMILY_RELS), CONJUNCTION_NAMES),
    )
    print(f"Deleted {cur.rowcount} family edges with conjunction-only names")

    # Step 3: self-loops in family relations.
    cur = c.execute(
        "DELETE FROM relations WHERE rel_type = ANY(%s) AND src_id = dst_id",
        (list(FAMILY_RELS),),
    )
    print(f"Deleted {cur.rowcount} family self-loops")

    c.commit()

    # Report final counts
    print("\nFinal family relation counts:")
    for rel, n in c.execute(
        "SELECT rel_type, count(*) FROM relations WHERE rel_type = ANY(%s) "
        "GROUP BY rel_type ORDER BY rel_type",
        (list(FAMILY_RELS),),
    ).fetchall():
        print(f"  {rel}: {n:,}")
