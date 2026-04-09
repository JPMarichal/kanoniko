#!/usr/bin/env bash
# pcloud-pull.sh — Download assets from pCloud public links
#
# Usage:
#   bash scripts/pcloud-pull.sh db       # Download SQLite DB
#   bash scripts/pcloud-pull.sh secrets   # Download .env secrets
#   bash scripts/pcloud-pull.sh all       # Download both
#
# Setup:
#   1. Upload alejandria.db.gz to pCloud (e.g. Backups/alejandria/)
#   2. Upload .env to pCloud (e.g. Backups/alejandria-secrets/)
#   3. Generate public download links for each
#   4. Set the links below (or use env vars)
#
# The pCloud direct download URL format is:
#   https://e1.pcloud.link/publink/show?code=XXXX
# To get a direct download link, use the "Download link" option in pCloud.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Configuration ---
# Set these to your pCloud public download links, or override via env vars.
# To get a direct-download URL from a pCloud public link:
#   https://api.pcloud.com/getpublinkdownload?code=XXXX
# The response JSON contains hosts[] and path — combine as https://{host}{path}
PCLOUD_DB_LINK="${PCLOUD_DB_LINK:-}"
PCLOUD_SECRETS_LINK="${PCLOUD_SECRETS_LINK:-}"

# --- Targets ---
DB_TARGET="$PROJECT_ROOT/data/sqlite/alejandria.db.gz"
SECRETS_TARGET="$PROJECT_ROOT/.env"

# --- Helpers ---
info()  { echo -e "\033[1;34m[INFO]\033[0m $*"; }
ok()    { echo -e "\033[1;32m[OK]\033[0m $*"; }
err()   { echo -e "\033[1;31m[ERROR]\033[0m $*" >&2; }

download() {
    local url="$1" target="$2" label="$3"

    if [ -z "$url" ]; then
        err "$label link not configured. Set $4 env var or edit this script."
        return 1
    fi

    info "Downloading $label → $target"
    mkdir -p "$(dirname "$target")"

    if curl -fSL --progress-bar -o "$target" "$url"; then
        local size
        size=$(du -h "$target" | cut -f1)
        ok "$label downloaded ($size)"
    else
        err "Failed to download $label"
        return 1
    fi
}

pull_db() {
    download "$PCLOUD_DB_LINK" "$DB_TARGET" "SQLite DB" "PCLOUD_DB_LINK"

    # Verify it's not a tiny error page
    local size_bytes
    size_bytes=$(wc -c < "$DB_TARGET")
    if [ "$size_bytes" -lt 1000000 ]; then
        err "Downloaded file is suspiciously small (${size_bytes} bytes). Check the link."
        return 1
    fi

    info "Decompressing..."
    gunzip -kf "$DB_TARGET"
    ok "DB ready at ${DB_TARGET%.gz}"
}

pull_secrets() {
    download "$PCLOUD_SECRETS_LINK" "$SECRETS_TARGET" "Secrets (.env)" "PCLOUD_SECRETS_LINK"
}

# --- Main ---
case "${1:-all}" in
    db)
        pull_db
        ;;
    secrets)
        pull_secrets
        ;;
    all)
        pull_db
        pull_secrets
        ;;
    *)
        echo "Usage: $0 {db|secrets|all}"
        exit 1
        ;;
esac
