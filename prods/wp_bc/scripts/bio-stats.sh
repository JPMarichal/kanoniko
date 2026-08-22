#!/bin/sh
set -e

# bio-stats.sh: Reporta el estado de todas las biografías bc_quote_author.
# Ejecuta todo en una sola llamada a wp eval para ser rápido.
#
# Uso: scripts/bio-stats.sh

CONTAINER="wp_bc"

echo "Estado de biografías — bc_quote_author"
echo "======================================="
echo ""

docker exec "$CONTAINER" wp eval '
$posts = get_posts(array(
  "post_type"      => "bc_quote_author",
  "posts_per_page" => -1,
  "post_status"    => "publish",
));

$total = 0;
$completas = 0;
$sin_contenido = 0;
$sin_foto = 0;
$sin_padre_madre = 0;
$sin_comentarios = 0;

foreach ($posts as $p) {
  $total++;
  $content_len = strlen($p->post_content);
  $thumb = get_post_meta($p->ID, "_thumbnail_id", true);
  $father = get_post_meta($p->ID, "_author_father", true);
  $mother = get_post_meta($p->ID, "_author_mother", true);
  $comment = $p->comment_status;

  $problemas = 0;

  if ($content_len < 500) { $sin_contenido++; $problemas++; }
  if (empty($thumb)) { $sin_foto++; $problemas++; }
  if (empty($father) || empty($mother)) { $sin_padre_madre++; $problemas++; }
  if ($comment !== "open") { $sin_comentarios++; $problemas++; }

  if ($problemas === 0) { $completas++; }
}

echo "  Completas:           $completas\n";
echo "  Sin contenido:       $sin_contenido\n";
echo "  Sin foto:            $sin_foto\n";
echo "  Sin padre/madre:     $sin_padre_madre\n";
echo "  Comentarios cerrados: $sin_comentarios\n";
echo "  Total personas:      $total\n";
' --allow-root 2>&1
