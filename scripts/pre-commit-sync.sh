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

# 2. Sync promoted NER candidates to gazetteer (entities.json is already
#    written by the promote() function — just ensure it's staged if changed)
ENTITIES="$REPO_ROOT/src/alejandria/knowledge/gazetteers/entities.json"
if git diff --name-only "$ENTITIES" 2>/dev/null | grep -q .; then
    git add "$ENTITIES"
    echo "[pre-commit] Staged updated entities.json (gazetteer promotion)"
fi

# 3. Stage gazetteers if changed
GAZETTEERS="$REPO_ROOT/data/gazetteers"
if [ -d "$GAZETTEERS" ]; then
    git add "$GAZETTEERS"/*.csv "$GAZETTEERS"/*.json 2>/dev/null || true
fi
