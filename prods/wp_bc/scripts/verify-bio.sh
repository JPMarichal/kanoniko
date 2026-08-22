#!/bin/sh
set -e

# verify-bio.sh: Verifica que un post bc_quote_author esté correctamente poblado.
#
# Uso: scripts/verify-bio.sh <post_id>

if [ $# -lt 1 ]; then
  echo "Uso: $0 <post_id>"
  exit 1
fi

POST_ID="$1"
CONTAINER="wp_bc"
ALL_OK=0

echo "=== Verificación post $POST_ID ==="
echo ""

# Helper: ejecuta wp-cli y retorna el meta value (trimmed)
get_meta() {
  docker exec "$CONTAINER" wp post meta get "$POST_ID" "$1" --allow-root 2>/dev/null | xargs echo -n
}

check() {
  local label="$1"
  local value="$2"
  if [ -z "$value" ] || [ "$value" = " " ]; then
    echo "  ✗ $label: VACÍO"
    ALL_OK=1
  else
    echo "  ✓ $label: $value"
  fi
}

# 1. post_content no corrupto
CONTENT_LEN=$(docker exec "$CONTAINER" wp post get "$POST_ID" --field=post_content --allow-root 2>/dev/null | wc -c)
CONTENT_LEN=$((CONTENT_LEN))
if [ "$CONTENT_LEN" -lt 500 ]; then
  echo "  ✗ post_content: solo $CONTENT_LEN caracteres (corrupto?)"
  ALL_OK=1
else
  echo "  ✓ post_content: $CONTENT_LEN caracteres"
fi

# 2. Metadatos del infobox
check "_author_father"     "$(get_meta _author_father)"
check "_author_mother"     "$(get_meta _author_mother)"
check "_author_birth_date" "$(get_meta _author_birth_date)"
check "_author_birth_place" "$(get_meta _author_birth_place)"
check "_author_death_date" "$(get_meta _author_death_date)"
check "_author_death_place" "$(get_meta _author_death_place)"
check "_author_nationality" "$(get_meta _author_nationality)"
check "_author_witness_type" "$(get_meta _author_witness_type)"
check "_author_callings"   "$(get_meta _author_callings)"

# 3. Foto (thumbnail)
THUMB=$(get_meta _thumbnail_id)
if [ -z "$THUMB" ] || [ "$THUMB" = "0" ]; then
  echo "  ✗ _thumbnail_id: SIN FOTO"
  ALL_OK=1
else
  echo "  ✓ _thumbnail_id: $THUMB"
fi

# 4. comment_status
COMMENT_STATUS=$(docker exec "$CONTAINER" wp post get "$POST_ID" --field=comment_status --allow-root 2>/dev/null | xargs echo -n)
if [ "$COMMENT_STATUS" = "open" ]; then
  echo "  ✓ comment_status: open"
else
  echo "  ✗ comment_status: $COMMENT_STATUS (debe ser open)"
  ALL_OK=1
fi

echo ""
if [ "$ALL_OK" -eq 0 ]; then
  echo "=== Todo OK ==="
else
  echo "=== HAY ERRORES (ver arriba) ==="
fi
exit $ALL_OK
