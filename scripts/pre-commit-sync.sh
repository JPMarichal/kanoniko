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

# 5. Validate ingestion backlogs (§Level B, docs/ingestion-workflow.md).
#    Blocks the commit if any backlog JSON violates its schema or has
#    duplicate slugs.
if [ -d "$REPO_ROOT/backlogs" ]; then
    if command -v python >/dev/null 2>&1; then
        if ! python "$REPO_ROOT/scripts/validate_backlogs.py" >/dev/null 2>&1; then
            echo "[pre-commit] ERROR: backlog validation failed. Running with full output:"
            python "$REPO_ROOT/scripts/validate_backlogs.py" || exit 1
        fi
    fi
fi

# 6. Spec-sync warning (proj/CONVENTIONS.md): src/ changes without a matching
#    doc/spec. Warn only — never blocks. Bypass with [skip-spec-sync] in the
#    commit subject or by staging the doc.
if command -v python >/dev/null 2>&1 && [ -f "$REPO_ROOT/scripts/check_spec_sync.py" ]; then
    python "$REPO_ROOT/scripts/check_spec_sync.py" || true
fi

# 7. Module-boundary check (docs/adr/0002-modular-monolith.md). Warn only until
#    the contract is baselined (P0 T1.8). No-op if import-linter isn't installed.
if command -v lint-imports >/dev/null 2>&1; then
    (cd "$REPO_ROOT" && lint-imports --config pyproject.toml) || \
        echo "[pre-commit] boundary check reported issues (non-blocking — see docs/adr/0002)"
fi
