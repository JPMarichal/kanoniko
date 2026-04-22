#!/usr/bin/env bash
# APPLY (no rollback): revistas->magazines + Liahona->liahona across all path columns.
set -euo pipefail
cd /mnt/c/own/alejandria
set -a; . ./.env; set +a

LOG=/tmp/pg_apply_revistas.$$.log
echo "Logging to $LOG"

cat > /tmp/pg_apply_revistas.sql <<'SQL'
BEGIN;
SET CONSTRAINTS ALL DEFERRED;

UPDATE document_registry
   SET file_path = replace(replace(file_path, '/revistas/', '/magazines/'), '/Liahona/', '/liahona/')
 WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%';

UPDATE chunks
   SET file_path = replace(replace(file_path, '/revistas/', '/magazines/'), '/Liahona/', '/liahona/')
 WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%';

UPDATE entity_document_mentions
   SET file_path = replace(replace(file_path, '/revistas/', '/magazines/'), '/Liahona/', '/liahona/')
 WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%';

UPDATE document_parallels
   SET src_file_path = replace(replace(src_file_path, '/revistas/', '/magazines/'), '/Liahona/', '/liahona/'),
       dst_file_path = replace(replace(dst_file_path, '/revistas/', '/magazines/'), '/Liahona/', '/liahona/')
 WHERE src_file_path LIKE '%/revistas/%' OR dst_file_path LIKE '%/revistas/%'
    OR src_file_path LIKE '%/Liahona/%'  OR dst_file_path LIKE '%/Liahona/%';

-- Verify: zero leftovers
SELECT 'chunks leftover'   AS check, count(*) FROM chunks                   WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'registry leftover', count(*) FROM document_registry        WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'mentions leftover', count(*) FROM entity_document_mentions WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'parallels leftover',count(*) FROM document_parallels       WHERE src_file_path LIKE '%/revistas/%' OR dst_file_path LIKE '%/revistas/%' OR src_file_path LIKE '%/Liahona/%' OR dst_file_path LIKE '%/Liahona/%'
;

COMMIT;

SELECT 'final magazines sample', file_path FROM chunks WHERE file_path LIKE '%/magazines/%' LIMIT 3;
SQL

docker run --rm --network host -i \
  -v /tmp/pg_apply_revistas.sql:/sql.sql:ro \
  -e PGPASSWORD="$ALEJANDRIA_POSTGRES_PASSWORD" \
  -e PGHOST=127.0.0.1 -e PGPORT=15432 \
  -e PGUSER="$ALEJANDRIA_POSTGRES_USER" \
  -e PGDATABASE="$ALEJANDRIA_POSTGRES_DB" \
  postgres:16-alpine psql -v ON_ERROR_STOP=1 -f /sql.sql 2>&1 | tee "$LOG"

echo "=== Exit: ${PIPESTATUS[0]} ==="
echo "Log: $LOG"
