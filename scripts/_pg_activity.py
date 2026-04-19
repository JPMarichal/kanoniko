"""Show active Postgres queries."""
import os, psycopg

with psycopg.connect(
    host=os.environ["ALEJANDRIA_POSTGRES_HOST"],
    port=int(os.environ["ALEJANDRIA_POSTGRES_PORT"]),
    user=os.environ["ALEJANDRIA_POSTGRES_USER"],
    password=os.environ["ALEJANDRIA_POSTGRES_PASSWORD"],
    dbname=os.environ["ALEJANDRIA_POSTGRES_DB"],
) as c:
    print("entities:", c.execute("SELECT count(*) FROM entities").fetchone()[0])
    n = c.execute("SELECT count(*) FROM pg_stat_activity WHERE state='active'").fetchone()[0]
    print("active queries:", n)
    rs = c.execute(
        "SELECT pid, application_name, state, "
        "EXTRACT(epoch FROM (now()-query_start))::int AS sec, "
        "substring(query, 1, 100) "
        "FROM pg_stat_activity "
        "WHERE state='active' AND query NOT ILIKE '%pg_stat_activity%' "
        "ORDER BY query_start"
    ).fetchall()
    for r in rs:
        print(r)
