"""Quick Postgres health/count check."""
import os
import psycopg

host = os.environ.get("ALEJANDRIA_POSTGRES_HOST", "localhost")
port = (os.environ.get("ALEJANDRIA_POSTGRES_PORT") or "15432").strip()
user = os.environ.get("ALEJANDRIA_POSTGRES_USER", "alejandria_rw")
pw = os.environ.get("ALEJANDRIA_POSTGRES_PASSWORD", "")
db = os.environ.get("ALEJANDRIA_POSTGRES_DB", "alejandria")
with psycopg.connect(host=host, port=int(port), user=user, password=pw, dbname=db) as c:
    print("entities:", c.execute("SELECT count(*) FROM entities").fetchone()[0])
    print("relations:", c.execute("SELECT count(*) FROM relations").fetchone()[0])
    for rel, n in c.execute(
        "SELECT rel_type, count(*) FROM relations WHERE rel_type IN "
        "('FATHER_OF','MOTHER_OF','SPOUSE_OF','SON_OF','DAUGHTER_OF') "
        "GROUP BY rel_type ORDER BY rel_type"
    ).fetchall():
        print(f"  {rel}: {n}")
    print("\nentities by type:")
    for t, n in c.execute(
        "SELECT entity_type, count(*) FROM entities GROUP BY entity_type "
        "ORDER BY count(*) DESC LIMIT 15"
    ).fetchall():
        print(f"  {t}: {n}")
