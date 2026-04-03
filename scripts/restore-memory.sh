#!/usr/bin/env bash
# Restore project memory from git to Claude Code's local memory directory.
# Run once on a new machine after cloning the repo.
#
# Usage:
#   bash scripts/restore-memory.sh
#
# Claude Code derives the project memory path from the absolute project path.
# On Windows it transforms C:\own\alejandria → C--own-alejandria.
# On Linux/Mac it transforms /home/user/alejandria → -home-user-alejandria.
#
# If auto-detection fails, set CLAUDE_MEMORY_DIR manually:
#   CLAUDE_MEMORY_DIR="$HOME/.claude/projects/my-project/memory" bash scripts/restore-memory.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="$REPO_ROOT/docs/project-memory"

if [[ -z "${CLAUDE_MEMORY_DIR:-}" ]]; then
  # Derive the Claude Code project key from the repo path.
  # Claude Code replaces path separators with dashes and strips leading slash.
  # Examples:
  #   /home/user/alejandria   → -home-user-alejandria
  #   C:\own\alejandria       → C--own-alejandria  (via MINGW/bash on Windows)
  RAW_PATH="$REPO_ROOT"
  # Normalize Windows paths if running under MINGW/Git Bash
  if [[ "$RAW_PATH" == /[a-zA-Z]/* ]]; then
    # /c/own/alejandria → C--own-alejandria
    DRIVE=$(echo "$RAW_PATH" | sed 's|^/\([a-zA-Z]\)/.*|\1|' | tr '[:lower:]' '[:upper:]')
    REST=$(echo "$RAW_PATH" | sed 's|^/[a-zA-Z]/||')
    PROJECT_KEY="${DRIVE}--${REST//\//-}"
  else
    # /home/user/alejandria → -home-user-alejandria
    PROJECT_KEY="${RAW_PATH//\//-}"
  fi

  CLAUDE_MEMORY_DIR="$HOME/.claude/projects/$PROJECT_KEY/memory"
fi

echo "Source : $SOURCE"
echo "Target : $CLAUDE_MEMORY_DIR"
echo ""

if [[ ! -d "$SOURCE" ]]; then
  echo "ERROR: Source directory not found: $SOURCE"
  exit 1
fi

mkdir -p "$CLAUDE_MEMORY_DIR"

COUNT=0
for f in "$SOURCE"/*.md; do
  [[ -f "$f" ]] || continue
  cp "$f" "$CLAUDE_MEMORY_DIR/"
  ((COUNT++))
done

echo "Restored $COUNT memory files to $CLAUDE_MEMORY_DIR"
echo "Restart Claude Code to pick up the restored memory."
