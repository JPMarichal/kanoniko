#!/usr/bin/env bash
# backup-pull.sh — Download DB and secrets from GitHub Releases
#
# Usage:
#   bash scripts/backup-pull.sh db       # Download and decompress SQLite DB
#   bash scripts/backup-pull.sh secrets   # Download encrypted .env (still needs decrypt)
#   bash scripts/backup-pull.sh all       # Download both
#
# The script finds the latest backup-* release automatically.
# All tools used (gh, gunzip, openssl) are available in Git Bash on Windows.
#
# After downloading secrets, decrypt manually:
#   openssl enc -aes-256-cbc -d -pbkdf2 -in data/sqlite/env.enc -out docker/.env -pass pass:PASSPHRASE

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

REPO="JPMarichal/kanoniko"
DB_TARGET="$PROJECT_ROOT/data/sqlite/alejandria.db.gz"
SECRETS_TARGET="$PROJECT_ROOT/data/sqlite/env.enc"

# --- Helpers ---
info()  { echo -e "\033[1;34m[INFO]\033[0m $*"; }
ok()    { echo -e "\033[1;32m[OK]\033[0m $*"; }
err()   { echo -e "\033[1;31m[ERROR]\033[0m $*" >&2; }

find_latest_release() {
    local tag
    tag=$(gh release list -R "$REPO" --limit 20 --json tagName,isPrerelease \
          --jq '[.[] | select(.tagName | startswith("backup-"))] | .[0].tagName // empty')
    if [ -z "$tag" ]; then
        err "No backup-* release found in $REPO"
        exit 1
    fi
    echo "$tag"
}

pull_db() {
    local tag="$1"
    info "Downloading DB from release $tag..."
    mkdir -p "$(dirname "$DB_TARGET")"

    if gh release download "$tag" -R "$REPO" --pattern "alejandria.db.gz" --dir "$(dirname "$DB_TARGET")" --clobber; then
        local size
        size=$(du -h "$DB_TARGET" | cut -f1)
        ok "DB downloaded ($size)"
    else
        err "Failed to download DB from release $tag"
        return 1
    fi

    # Verify it's not a tiny error page
    local size_bytes
    size_bytes=$(wc -c < "$DB_TARGET")
    if [ "$size_bytes" -lt 1000000 ]; then
        err "Downloaded file is suspiciously small (${size_bytes} bytes). Check the release."
        return 1
    fi

    info "Decompressing..."
    gunzip -kf "$DB_TARGET"
    ok "DB ready at ${DB_TARGET%.gz}"
}

pull_secrets() {
    local tag="$1"
    info "Downloading encrypted secrets from release $tag..."
    mkdir -p "$(dirname "$SECRETS_TARGET")"

    if gh release download "$tag" -R "$REPO" --pattern "env.enc" --dir "$(dirname "$SECRETS_TARGET")" --clobber; then
        local size
        size=$(du -h "$SECRETS_TARGET" | cut -f1)
        ok "Encrypted secrets downloaded ($size)"
        info "To decrypt: openssl enc -aes-256-cbc -d -pbkdf2 -in $SECRETS_TARGET -out docker/.env -pass pass:PASSPHRASE"
    else
        err "Failed to download secrets from release $tag"
        return 1
    fi
}

# --- Main ---
TAG=$(find_latest_release)
info "Using release: $TAG"

case "${1:-all}" in
    db)
        pull_db "$TAG"
        ;;
    secrets)
        pull_secrets "$TAG"
        ;;
    all)
        pull_db "$TAG"
        pull_secrets "$TAG"
        ;;
    *)
        echo "Usage: $0 {db|secrets|all}"
        exit 1
        ;;
esac
