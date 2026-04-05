#!/bin/bash
# pre-commit-sync.sh — Run before commits to keep recovery assets in sync
# Install: ln -sf ../../scripts/pre-commit-sync.sh .git/hooks/pre-commit
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

# 1. Sync project memory to docs/
MEMORY_SRC="$HOME/.claude/projects/C--own-alejandria/memory"
MEMORY_DST="$REPO_ROOT/docs/project-memory"
if [ -d "$MEMORY_SRC" ]; then
    mkdir -p "$MEMORY_DST"
    cp -u "$MEMORY_SRC"/*.md "$MEMORY_DST/" 2>/dev/null || true
    # Stage any new/changed memory files
    git add "$MEMORY_DST"/*.md 2>/dev/null || true
fi

# 2. Sync SQLite DB from GPU container to Windows (authoritative → git via LFS)
GPU_DISTRO="Ubuntu-20.04"
GPU_DB_PATH="/home/jpmarichal/alejandria-data/sqlite/alejandria.db"
LOCAL_DB_GZ="$REPO_ROOT/data/sqlite/alejandria.db.gz"
if wsl -d "$GPU_DISTRO" bash -c "test -f $GPU_DB_PATH" 2>/dev/null; then
    echo "[pre-commit] Syncing SQLite from GPU container (compress + LFS)..."
    wsl -d "$GPU_DISTRO" bash -c "gzip -c -1 $GPU_DB_PATH > /tmp/alejandria-sync.db.gz"
    WIN_PATH=$(wsl -d "$GPU_DISTRO" bash -c "wslpath -w /tmp/alejandria-sync.db.gz")
    cp "$WIN_PATH" "$LOCAL_DB_GZ"
    git add "$LOCAL_DB_GZ"
    echo "[pre-commit] SQLite synced ($(du -h "$LOCAL_DB_GZ" | cut -f1) compressed via LFS)"
else
    echo "[pre-commit] WARNING: GPU DB not found at $GPU_DISTRO:$GPU_DB_PATH — skipping sync"
fi

# 3. Sync promoted NER candidates to gazetteer (entities.json is already
#    written by the promote() function — just ensure it's staged if changed)
ENTITIES="$REPO_ROOT/src/alejandria/knowledge/gazetteers/entities.json"
if git diff --name-only "$ENTITIES" 2>/dev/null | grep -q .; then
    git add "$ENTITIES"
    echo "[pre-commit] Staged updated entities.json (gazetteer promotion)"
fi

# 4. Stage gazetteers if changed
GAZETTEERS="$REPO_ROOT/data/gazetteers"
if [ -d "$GAZETTEERS" ]; then
    git add "$GAZETTEERS"/*.csv "$GAZETTEERS"/*.json 2>/dev/null || true
fi
