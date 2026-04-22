#!/usr/bin/env bash
set -euo pipefail
cd /mnt/c/own/alejandria
set -a; . ./.env; set +a
docker run --rm --network host \
  -e PGPASSWORD="$ALEJANDRIA_POSTGRES_PASSWORD" \
  -e PGHOST=127.0.0.1 -e PGPORT=15432 \
  -e PGUSER="$ALEJANDRIA_POSTGRES_USER" \
  -e PGDATABASE="$ALEJANDRIA_POSTGRES_DB" \
  postgres:16-alpine psql -c "
SELECT conrelid::regclass AS table, conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE contype='f'
  AND pg_get_constraintdef(oid) LIKE '%file_path%';
"
