---
name: feedback_gitignore_data
description: Never exclude data/ directory from git — everything must survive a machine change
type: feedback
---

Never use a catch-all exclusion for `data/` in `.gitignore`. All assets in `data/` must be tracked for disaster recovery when switching machines.

Also: project memory must be written to `docs/project-memory/` (in repo) as the primary location — not only to `~/.claude/...`. See CLAUDE.md "Project Memory" section for the dual-write protocol.

**Why:** User explicitly requires that nothing be lost on a machine change. A `data/*` wildcard silently excluded kg-seeds, scrape checkpoints, and other hard-to-rebuild assets.

**How to apply:** Only exclude specific large generated artifacts:
- `data/sqlite/backups/` — timestamped backup files (can regenerate via API)
- `data/sqlite/neo4j_backups/` — Neo4j streaming exports (can regenerate via API)

Everything else in `data/` (gazetteers, kg-seeds, scripture_structure, SQLite DB, scrape checkpoints) must be tracked in git. When adding new subdirectories under `data/`, do NOT add them to `.gitignore` unless they are large generated files that can be fully reconstructed.
