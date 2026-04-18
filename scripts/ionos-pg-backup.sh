#!/bin/bash
# Daily backup of the Alejandria Postgres DB on the IONOS VPS.
# Instalado como /usr/local/bin/alejandria-backup.sh vía cron postgres.
# Formato: pg_dump custom (Fc) + gzip level 6 — permite pg_restore paralelo
# y filtros por tabla.
set -euo pipefail

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
BACKUP_DIR="/var/backups/alejandria"
OUT="${BACKUP_DIR}/alejandria-${STAMP}.sql.gz"

pg_dump -Fc -Z 6 alejandria > "$OUT"

SIZE=$(du -h "$OUT" | cut -f1)
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  backup  ${OUT}  ${SIZE}" \
  >> "${BACKUP_DIR}/backup.log"

# Rotar: conservar últimos 14 días
find "${BACKUP_DIR}" -name "alejandria-*.sql.gz" -mtime +14 -delete
