"""Verify Amaleki genealogy + final family relation counts in Postgres IONOS."""
import os, psycopg

with psycopg.connect(
    host=os.environ["ALEJANDRIA_POSTGRES_HOST"],
    port=int(os.environ["ALEJANDRIA_POSTGRES_PORT"]),
    user=os.environ["ALEJANDRIA_POSTGRES_USER"],
    password=os.environ["ALEJANDRIA_POSTGRES_PASSWORD"],
    dbname=os.environ["ALEJANDRIA_POSTGRES_DB"],
) as c:
    print("=== Final entity counts ===")
    for t, n in c.execute(
        "SELECT entity_type, count(*) FROM entities GROUP BY entity_type "
        "ORDER BY count(*) DESC LIMIT 12"
    ).fetchall():
        print(f"  {t}: {n:,}")
    total = c.execute("SELECT count(*) FROM entities").fetchone()[0]
    print(f"  TOTAL: {total:,}")

    print("\n=== Family relations ===")
    for rel, n in c.execute(
        "SELECT rel_type, count(*) FROM relations WHERE rel_type IN "
        "('FATHER_OF','MOTHER_OF','SPOUSE_OF','SON_OF','DAUGHTER_OF','BROTHER_OF','SISTER_OF') "
        "GROUP BY rel_type ORDER BY rel_type"
    ).fetchall():
        print(f"  {rel}: {n:,}")
    total_rel = c.execute("SELECT count(*) FROM relations").fetchone()[0]
    print(f"  TOTAL all relations: {total_rel:,}")

    print("\n=== Amaleki ancestors (testigo) ===")
    rows = c.execute("""
        WITH RECURSIVE up AS (
            SELECT e.id, e.name, e.entity_type, 0 AS depth, ARRAY[e.id] AS path
            FROM entities e
            WHERE lower(e.name) = 'amaleki' AND e.entity_type = 'person'
          UNION ALL
            SELECT parent.id, parent.name, parent.entity_type, up.depth + 1, up.path || parent.id
            FROM up
            JOIN relations r ON r.dst_id = up.id AND r.rel_type = 'FATHER_OF'
            JOIN entities parent ON parent.id = r.src_id
            WHERE NOT parent.id = ANY(up.path) AND up.depth < 8
        )
        SELECT depth, name, entity_type FROM up ORDER BY depth
    """).fetchall()
    for row in rows:
        print(f"  depth={row[0]}: {row[1]} [{row[2]}]")
