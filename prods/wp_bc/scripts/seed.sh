#!/bin/sh
set -e

echo "=== WP Seed ==="

MAX_RETRIES=15
i=1
while [ $i -le $MAX_RETRIES ]; do
  if mysqladmin ping -h db -u wpuser -pwppass --silent 2>/dev/null; then
    echo "Database ready."
    break
  fi
  echo "Waiting for database... ($i/$MAX_RETRIES)"
  sleep 4
  i=$((i + 1))
done

if [ $i -gt $MAX_RETRIES ]; then
  echo "Database not reachable. Aborting."
  exit 1
fi

if wp core is-installed --path=/var/www/html 2>/dev/null; then
  echo "WordPress already installed."
  wp user create JPMarichal jpmarichal@example.com --role=administrator --user_pass=my-Adm1n! --path=/var/www/html 2>/dev/null \
    && echo "User JPMarichal created." \
    || echo "User JPMarichal already exists."
else
  echo "Installing WordPress..."
  wp core install \
    --url="${WP_HOME:-http://localhost:8080}" \
    --title="BC WordPress" \
    --admin_user=JPMarichal \
    --admin_password=my-Adm1n! \
    --admin_email=jpmarichal@example.com \
    --path=/var/www/html
  echo "WordPress installed."
fi

echo "Installing GeneratePress theme..."
wp theme install generatepress --activate --path=/var/www/html 2>/dev/null \
  && echo "GeneratePress activated." \
  || echo "GeneratePress already present."

echo "=== Seed complete ==="
