#!/bin/sh
set -e

echo "=== Seed bc_quote_author ==="

docker exec wp_bc sh -c "cd /var/www/html && wp eval-file wp-content/plugins/bc-quote-block/data/seed-authors.php --allow-root"

echo "=== Seed complete ==="
