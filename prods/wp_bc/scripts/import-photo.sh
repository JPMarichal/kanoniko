#!/bin/sh
set -e

# import-photo.sh: Descarga la foto de una persona desde Wikimedia Commons usando
# su QID de Wikidata y la asigna como imagen destacada (featured image) del post.
#
# Uso: scripts/import-photo.sh <post_id> <qid> <nombre_persona>
#
# Ej: scripts/import-photo.sh 3166 Q1177157 "David Whitmer"
#
# También soporta leer wikidata.json local como alternativa (más rápido):
#   Si existe corpus/personajes/<slug>/wikidata.json, lo usa directamente.

if [ $# -lt 3 ]; then
  echo "Uso: $0 <post_id> <qid> <nombre_persona>"
  echo "Ej:  $0 3166 Q1177157 \"David Whitmer\""
  exit 1
fi

POST_ID="$1"
QID="$2"
NAME="$3"
CONTAINER="wp_bc"

# Intentar leer wikidata.json local primero (más rápido)
LOCAL_FILE="corpus/personajes/$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')/wikidata.json"
IMAGE_FILE=""

if [ -f "$LOCAL_FILE" ]; then
  IMAGE_FILE=$(python -c "import json; print(json.load(open('$LOCAL_FILE')).get('image',''))" 2>/dev/null || echo "")
fi

# Si no está en local, consultar API de Wikidata
if [ -z "$IMAGE_FILE" ]; then
  echo "Consultando Wikidata API para $QID..."
  JSON=$(curl -s "https://www.wikidata.org/wiki/Special:EntityData/$QID.json" 2>/dev/null || echo "")
  if [ -n "$JSON" ]; then
    IMAGE_FILE=$(echo "$JSON" | python -c "
import sys, json
try:
  data = json.load(sys.stdin)
  entity = data.get('entities', {}).get('$QID', {})
  claims = entity.get('claims', {})
  prop = claims.get('P18', [{}])
  if prop:
    val = prop[0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
    print(val)
except:
  pass
" 2>/dev/null || echo "")
  fi
fi

if [ -z "$IMAGE_FILE" ]; then
  echo "ERROR: No se pudo obtener el nombre del archivo de imagen para QID=$QID"
  echo "Verifica el QID o agrega wikidata.json manualmente."
  exit 1
fi

echo "Imagen encontrada: $IMAGE_FILE"

# Usar Special:FilePath que redirige al CDN correcto sin calcular hash MD5
URL="https://commons.wikimedia.org/wiki/Special:FilePath/$IMAGE_FILE"

echo "URL: $URL"
echo "Importando e asignando como foto destacada a post $POST_ID..."

docker exec "$CONTAINER" wp media import "$URL" --post_id="$POST_ID" --featured_image --title="$NAME" --allow-root

echo "✓ Foto asignada a $NAME (post $POST_ID)"
