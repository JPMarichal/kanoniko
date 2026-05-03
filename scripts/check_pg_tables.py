#!/usr/bin/env python3
from alejandria.storage.postgres.connection import get_connection

try:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public' 
                ORDER BY table_name
            """)
            tables = [row[0] for row in cur.fetchall()]
            print("Tablas en PostgreSQL (IONOS):")
            for t in tables:
                print(f"  - {t}")
            print(f"\nTotal: {len(tables)} tablas")
except Exception as e:
    print(f"Error: {e}")
