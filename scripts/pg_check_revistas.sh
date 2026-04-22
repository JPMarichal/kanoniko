#!/usr/bin/env bash
# One-shot: verify scope of revistas->magazines rename in Postgres.
set -euo pipefail
cd /mnt/c/own/alejandria
set -a
. ./.env
set +a

echo "USER=$ALEJANDRIA_POSTGRES_USER DB=$ALEJANDRIA_POSTGRES_DB"

docker run --rm --network host \
  -e PGPASSWORD="$ALEJANDRIA_POSTGRES_PASSWORD" \
  -e PGHOST=127.0.0.1 -e PGPORT=15432 \
  -e PGUSER="$ALEJANDRIA_POSTGRES_USER" \
  -e PGDATABASE="$ALEJANDRIA_POSTGRES_DB" \
  postgres:16-alpine psql -c "\dt"

echo "---"
echo "chunks columns with path-like names:"
docker run --rm --network host \
  -e PGPASSWORD="$ALEJANDRIA_POSTGRES_PASSWORD" \
  -e PGHOST=127.0.0.1 -e PGPORT=15432 \
  -e PGUSER="$ALEJANDRIA_POSTGRES_USER" \
  -e PGDATABASE="$ALEJANDRIA_POSTGRES_DB" \
  postgres:16-alpine psql -c "SELECT table_name, column_name FROM information_schema.columns WHERE column_name ~ 'path|file|source' ORDER BY table_name, column_name;"
