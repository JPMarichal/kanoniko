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
SELECT 'chunks revistas'   AS scope, count(*) FROM chunks WHERE file_path LIKE '%/revistas/%'
UNION ALL SELECT 'chunks Liahona',     count(*) FROM chunks WHERE file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'chunks magazines',   count(*) FROM chunks WHERE file_path LIKE '%/magazines/%'
UNION ALL SELECT 'chunks liahona',     count(*) FROM chunks WHERE file_path LIKE '%/liahona/%'
UNION ALL SELECT 'registry revistas',  count(*) FROM document_registry WHERE file_path LIKE '%/revistas/%'
UNION ALL SELECT 'mentions revistas',  count(*) FROM entity_document_mentions WHERE file_path LIKE '%/revistas/%'
;"
