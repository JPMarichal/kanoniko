#!/usr/bin/env bash
# Dry-run: count affected rows for revistas->magazines + Liahona->liahona.
# Then run UPDATE inside a transaction with ROLLBACK to prove the SQL works.
set -euo pipefail
cd /mnt/c/own/alejandria
set -a; . ./.env; set +a

PSQL_RUN() {
  docker run --rm --network host \
    -e PGPASSWORD="$ALEJANDRIA_POSTGRES_PASSWORD" \
    -e PGHOST=127.0.0.1 -e PGPORT=15432 \
    -e PGUSER="$ALEJANDRIA_POSTGRES_USER" \
    -e PGDATABASE="$ALEJANDRIA_POSTGRES_DB" \
    postgres:16-alpine psql "$@"
}

echo "=== Conteos antes del rename ==="
PSQL_RUN -c "
SELECT 'chunks revistas'         AS scope, count(*) FROM chunks                   WHERE file_path LIKE '%/revistas/%'
UNION ALL SELECT 'chunks Liahona',        count(*) FROM chunks                   WHERE file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'registry revistas',     count(*) FROM document_registry        WHERE file_path LIKE '%/revistas/%'
UNION ALL SELECT 'registry Liahona',      count(*) FROM document_registry        WHERE file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'mentions revistas',     count(*) FROM entity_document_mentions WHERE file_path LIKE '%/revistas/%'
UNION ALL SELECT 'mentions Liahona',      count(*) FROM entity_document_mentions WHERE file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'parallels src revistas',count(*) FROM document_parallels       WHERE src_file_path LIKE '%/revistas/%' OR dst_file_path LIKE '%/revistas/%'
;"

echo
echo "=== Sample paths (antes) ==="
PSQL_RUN -c "SELECT file_path FROM chunks WHERE file_path LIKE '%/revistas/%' LIMIT 5;"

echo
echo "=== DRY-RUN: BEGIN + UPDATE + ROLLBACK ==="
PSQL_RUN <<'SQL'
BEGIN;

UPDATE chunks
   SET file_path = replace(replace(file_path, '/revistas/', '/magazines/'), '/Liahona/', '/liahona/')
 WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%';

UPDATE document_registry
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

-- Verify: zero rows should remain with old paths
SELECT 'chunks leftover'   AS check, count(*) FROM chunks                   WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'registry leftover', count(*) FROM document_registry        WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'mentions leftover', count(*) FROM entity_document_mentions WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'parallels leftover',count(*) FROM document_parallels       WHERE src_file_path LIKE '%/revistas/%' OR dst_file_path LIKE '%/revistas/%' OR src_file_path LIKE '%/Liahona/%' OR dst_file_path LIKE '%/Liahona/%'
;

-- Sample migrated
SELECT 'migrated sample', file_path FROM chunks WHERE file_path LIKE '%/magazines/%' LIMIT 5;

ROLLBACK;
SQL

echo
echo "=== Post-rollback confirmación: sigue revistas ==="
PSQL_RUN -c "SELECT count(*) AS still_revistas FROM chunks WHERE file_path LIKE '%/revistas/%';"
