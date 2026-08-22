#!/bin/sh
set -e

# publish-bio.sh: Publica la biografía de un bc_quote_author de forma confiable.
# Evita el bug de --post_content=/dev/stdin (guarda el string literal).
# Usa wp eval con file_get_contents + wp_update_post.
#
# Uso: scripts/publish-bio.sh <post_id> <archivo.html> [excerpt]

if [ $# -lt 2 ]; then
  echo "Uso: $0 <post_id> <archivo.html> [excerpt]"
  echo "Ej:  $0 3166 /var/www/html/wp-content/uploads/bio.html \"Resumen breve\""
  exit 1
fi

POST_ID="$1"
BIO_FILE="$2"
EXCERPT="${3:-}"

CONTAINER="wp_bc"

# Validar que el archivo existe dentro del contenedor
if ! docker exec "$CONTAINER" test -f "$BIO_FILE"; then
  echo "ERROR: El archivo '$BIO_FILE' no existe dentro del contenedor."
  echo "Primero copia el archivo a wp-content/uploads/ que es volumen montado."
  exit 1
fi

echo "=== Publicando biografía en post $POST_ID ==="

# 1. Publicar post_content desde archivo
docker exec "$CONTAINER" wp eval "
  \$content = file_get_contents('$BIO_FILE');
  wp_update_post(array('ID' => $POST_ID, 'post_content' => \$content));
" --allow-root

echo "  ✓ post_content actualizado"

# 2. Setear excerpt si se proporcionó
if [ -n "$EXCERPT" ]; then
  docker exec "$CONTAINER" wp post update "$POST_ID" --post_excerpt="$EXCERPT" --allow-root
  echo "  ✓ post_excerpt actualizado"
fi

# 3. Abrir comentarios
docker exec "$CONTAINER" wp post update "$POST_ID" --comment_status=open --allow-root
echo "  ✓ comentarios abiertos"

# 4. Verificar que el contenido se guardó correctamente
CONTENT_LEN=$(docker exec "$CONTAINER" wp post get "$POST_ID" --field=post_content --allow-root | wc -c)
if [ "$CONTENT_LEN" -lt 500 ]; then
  echo "ERROR: post_content solo tiene $CONTENT_LEN caracteres (muy corto, posible corrupto)."
  echo "Usa scripts/verify-bio.sh $POST_ID para diagnóstico."
  exit 1
fi

echo "  ✓ verificación: $CONTENT_LEN caracteres en post_content"
echo "=== Publicación completada ==="
