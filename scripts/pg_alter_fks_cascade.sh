#!/usr/bin/env bash
# Add ON UPDATE CASCADE to the 4 file_path FKs, then apply revistas->magazines rename.
# Run with MODE=dryrun (default) or MODE=apply.
set -euo pipefail
cd /mnt/c/own/alejandria
set -a; . ./.env; set +a
MODE="${MODE:-dryrun}"
TAIL="ROLLBACK;"
[[ "$MODE" == "apply" ]] && TAIL="COMMIT;"

cat > /tmp/pg_fk_cascade.sql <<SQL
BEGIN;

-- 1. Rebuild the 4 FKs with ON UPDATE CASCADE (keep ON DELETE CASCADE)
ALTER TABLE chunks
  DROP CONSTRAINT chunks_file_path_fkey,
  ADD CONSTRAINT chunks_file_path_fkey
    FOREIGN KEY (file_path) REFERENCES document_registry(file_path)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE entity_document_mentions
  DROP CONSTRAINT entity_document_mentions_file_path_fkey,
  ADD CONSTRAINT entity_document_mentions_file_path_fkey
    FOREIGN KEY (file_path) REFERENCES document_registry(file_path)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE document_parallels
  DROP CONSTRAINT document_parallels_src_file_path_fkey,
  ADD CONSTRAINT document_parallels_src_file_path_fkey
    FOREIGN KEY (src_file_path) REFERENCES document_registry(file_path)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE document_parallels
  DROP CONSTRAINT document_parallels_dst_file_path_fkey,
  ADD CONSTRAINT document_parallels_dst_file_path_fkey
    FOREIGN KEY (dst_file_path) REFERENCES document_registry(file_path)
    ON UPDATE CASCADE ON DELETE CASCADE;

-- 2. UPDATE only document_registry; chunks/mentions/parallels cascade automatically
UPDATE document_registry
   SET file_path = replace(replace(file_path, '/revistas/', '/magazines/'), '/Liahona/', '/liahona/')
 WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%';

-- 3. Verify no leftovers anywhere
SELECT 'registry leftover' AS check, count(*) FROM document_registry WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'chunks leftover',   count(*) FROM chunks WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'mentions leftover', count(*) FROM entity_document_mentions WHERE file_path LIKE '%/revistas/%' OR file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'parallels leftover',count(*) FROM document_parallels WHERE src_file_path LIKE '%/revistas/%' OR dst_file_path LIKE '%/revistas/%' OR src_file_path LIKE '%/Liahona/%' OR dst_file_path LIKE '%/Liahona/%'
UNION ALL SELECT 'chunks magazines OK',   count(*) FROM chunks WHERE file_path LIKE '%/magazines/liahona/%'
UNION ALL SELECT 'registry magazines OK', count(*) FROM document_registry WHERE file_path LIKE '%/magazines/liahona/%'
UNION ALL SELECT 'mentions magazines OK', count(*) FROM entity_document_mentions WHERE file_path LIKE '%/magazines/liahona/%'
;

$TAIL
SQL

echo "=== MODE=$MODE ==="
docker run --rm --network host \
  -v /tmp/pg_fk_cascade.sql:/sql.sql:ro \
  -e PGPASSWORD="$ALEJANDRIA_POSTGRES_PASSWORD" \
  -e PGHOST=127.0.0.1 -e PGPORT=15432 \
  -e PGUSER="$ALEJANDRIA_POSTGRES_USER" \
  -e PGDATABASE="$ALEJANDRIA_POSTGRES_DB" \
  postgres:16-alpine psql -v ON_ERROR_STOP=1 -f /sql.sql
