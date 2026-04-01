#!/bin/bash
# sync-memory.sh — Copy Claude project memory to repo for git backup
# Run before commits or periodically to keep memory backed up in git
set -euo pipefail

MEMORY_SRC="$HOME/.claude/projects/C--own-alejandria/memory"
MEMORY_DST="$(dirname "$0")/../docs/project-memory"

if [ ! -d "$MEMORY_SRC" ]; then
    echo "Memory source not found: $MEMORY_SRC"
    exit 1
fi

mkdir -p "$MEMORY_DST"

# Copy all memory files, preserving timestamps
cp -u "$MEMORY_SRC"/*.md "$MEMORY_DST/" 2>/dev/null || true

# Report
count=$(ls -1 "$MEMORY_DST"/*.md 2>/dev/null | wc -l)
echo "Synced $count memory files to docs/project-memory/"
