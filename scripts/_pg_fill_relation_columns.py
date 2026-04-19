"""Backfill NULL columns on family relations.

Two independent fixes:
  1. Set category='family' where NULL for family relation types
     (covers legacy 'genealogy_extraction' + 'curated_seed' rows).
  2. Drop NULL-source_ref rows from family_pattern_backfill and
     family_inference so the caller can re-run `--stage family` and
     `--stage infer` with the updated code that fills source_ref.
     This is simpler than joining back to chunks after the fact.

Idempotent; safe to re-run.
"""
import os
import psycopg

FAMILY_RELS = ("FATHER_OF", "MOTHER_OF", "BROTHER_OF", "SISTER_OF",
               "SPOUSE_OF", "SON_OF", "DAUGHTER_OF", "ANCESTOR_OF",
               "DESCENDANT_OF")

OUR_SOURCES = ("family_pattern_backfill", "family_inference")

with psycopg.connect(
    host=os.environ["ALEJANDRIA_POSTGRES_HOST"],
    port=int(os.environ["ALEJANDRIA_POSTGRES_PORT"]),
    user=os.environ["ALEJANDRIA_POSTGRES_USER"],
    password=os.environ["ALEJANDRIA_POSTGRES_PASSWORD"],
    dbname=os.environ["ALEJANDRIA_POSTGRES_DB"],
) as c:
    # Fix 1: category='family' for legacy rows
    cur = c.execute(
        "UPDATE relations SET category = 'family' "
        "WHERE category IS NULL AND rel_type = ANY(%s)",
        (list(FAMILY_RELS),),
    )
    print(f"Set category='family' on {cur.rowcount:,} legacy rows")

    # Fix 2: delete our rows that lack source_ref (re-run will refill)
    cur = c.execute(
        "DELETE FROM relations "
        "WHERE rel_type = ANY(%s) "
        "  AND source = ANY(%s) "
        "  AND source_ref IS NULL",
        (list(FAMILY_RELS), list(OUR_SOURCES)),
    )
    print(f"Deleted {cur.rowcount:,} rows missing source_ref "
          f"(re-run family + infer to repopulate)")

    c.commit()

    # Report
    print("\nFamily relation column fill-rate after fix:")
    rows = c.execute("""
        SELECT rel_type, COALESCE(source, '(null)') AS src,
               count(*) AS n,
               count(category) AS nc,
               count(source_ref) AS ns
        FROM relations WHERE rel_type = ANY(%s)
        GROUP BY rel_type, source
        ORDER BY rel_type, count(*) DESC
    """, (list(FAMILY_RELS),)).fetchall()
    print(f"{'rel_type':18s} {'source':30s} {'n':>7s}  cat%  sref%")
    for rel, src, n, nc, ns in rows:
        print(f"{rel:18s} {src:30s} {n:7,}  "
              f"{100*nc/n:4.0f}  {100*ns/n:4.0f}")
