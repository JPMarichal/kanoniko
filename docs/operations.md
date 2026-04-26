# Operations Guide

Common operational workflows for maintaining the Alejandria knowledge engine.

## Initial Setup

After first deployment:

```bash
# 1. Start services
cd docker && docker compose up --build -d

# 2. Run initial indexing (parses corpus, builds FTS + embeddings + KG)
curl -X POST http://localhost:4300/index/trigger -H "Content-Type: application/json" -d '{"full_reindex": true}'

# 3. Build entity profiles — metadata phase
curl -X POST http://localhost:4300/index/build-profiles -H "Content-Type: application/json" -d '{"phase": "metadata"}'

# 4. Build entity profiles — generate phase (requires LLM API key)
curl -X POST http://localhost:4300/index/build-profiles -H "Content-Type: application/json" -d '{"phase": "generate", "max_entities": 500}'
```

## Adding New Corpus Content

### Design contract: indexing is always explicit

There is **no automatic trigger**. Corpus files can be added, downloaded, or
modified at any time without triggering indexing. This allows bulk corpus
accumulation (multiple download scripts, multiple materials) before paying
the indexing cost once.

### Workflow: accumulate then index

```bash
# Step 1: download as many materials as needed — no indexing happens
python scripts/download_jesus_the_christ.py
python scripts/download_easter_study_plan.py
python scripts/download_christmas_study_plan.py
# ... more downloads ...

# Step 2: commit the new corpus files
git add corpus/ && git commit -m "Add new corpus materials"

# Step 3: index using git diff — fastest path, skips SHA scan of existing files
git diff --name-only HEAD~1 HEAD -- 'corpus/**/*.txt' \
  | python -c "
import sys, json, urllib.request
paths = [p[len('corpus/'):].strip() for p in sys.stdin if p.strip().startswith('corpus/')]
body = json.dumps({'paths': paths, 'force': False}).encode()
req = urllib.request.Request('http://localhost:4300/index/ingest', data=body,
      headers={'Content-Type': 'application/json'}, method='POST')
print(json.loads(urllib.request.urlopen(req).read()))
"
```

This is the **canonical post-commit incremental workflow**. It uses git to identify
exactly which files are new (O(1)) rather than hashing all 24K+ corpus files on disk
(O(n)). On a corpus of 24K files, this saves 20-30 minutes before Phase 1 even starts.

> **Why commit first?** `git diff HEAD~1 HEAD` is stable and precise. Running ingest
> before committing risks including partial downloads or files not yet committed to the
> record.

### When to use `/ingest` vs `/trigger`

| Endpoint | Use when |
|----------|----------|
| `POST /index/ingest` (via git diff) | **Default.** After committing new corpus files — fastest, no SHA scan |
| `POST /index/ingest` (manual paths) | You know exactly which directories were added and haven't committed yet |
| `POST /index/trigger` | Corpus diverged from git (manual edits, partial downloads) — needed only for debugging |

**Never use `/trigger` after a normal corpus commit.** It scans SHA of every file in
the corpus before it can identify what's new. At 24K+ files this wastes 20-30 minutes
before any actual indexing begins.

### Incremental vs. Force: understanding the cost

**Incremental** (default): only processes files whose SHA-256 changed. Adding 7,765 new
files to a 24K-file corpus takes ~45-90 min on GPU — the pipeline skips everything unchanged.

**Force** (`"force": true`): re-processes files even if their hash hasn't changed. This
is needed only for **migrations** — when the parser, chunker, or extractor logic changes
and existing files need to be re-processed with the new code.

### Pipeline phases

Phase 1 runs parse and FTS insert in two sub-steps:

| Sub-phase | What | Implementation |
|-----------|------|----------------|
| 1a. Delete (updates only) | Remove old chunks from FTS + sqlite-vec | Serial, single connection, skipped for new files |
| 1b. Parse + chunk | Parse text, chunk, build metadata | **Parallel** — `ThreadPoolExecutor(8 workers)`, no SQLite |
| 1c. FTS insert | Insert chunks into SQLite FTS5 | Serial, **single shared connection** for all files |

| Phase | What | Bottleneck |
|-------|------|------------|
| 1. Parse/Chunk/FTS | See sub-phases above | I/O + SQLite writes |
| 2. Embeddings | Batch-encode ALL chunks at once, upsert to sqlite-vec | GPU (fast) or CPU (slow) |
| 3. KG extraction | spaCy NER + Neo4j batch writes per file | Neo4j I/O |

**`/index/status` only tracks Phase 1 progress.** It can show 100% while phases 2 and 3
are still running. Check `/health` to monitor vector and graph node counts growing.

### Real-world indexing times (observed)

| Operation | Files | Wall time | Notes |
|-----------|-------|-----------|-------|
| Proclamations (incremental) | 4 | ~10 sec | New files, all 3 phases |
| Missionary manuals (incremental) | 40 | ~60 sec | New files, all 3 phases |
| Corpus expansion (incremental, GPU) | 7,765 | ~45-90 min | git diff → /ingest, parallel Phase 1 |
| Conference talks (force, format migration) | 6,910 | ~2 hours | Phase 1: 45 min, Phase 2+3: ~75 min |
| Full reindex (all corpus) | ~24K | 7+ hours (CPU) | **Destructive** — avoid |

**Rule of thumb:** For new files, Phase 1 is now fast (parallel parsing + single SQLite
connection). The bottleneck shifts to Phase 2 (embeddings) on CPU — use GPU when possible.

## Knowledge Graph Rebuild

Required after changes to the extractor (gazetteers, NER rules, stopword lists):

```bash
# Full rebuild (~15 min)
curl -X POST http://localhost:4300/index/rebuild-kg

# Then rebuild metadata profiles (cleans orphans, updates counts)
curl -X POST http://localhost:4300/index/build-profiles -H "Content-Type: application/json" -d '{"phase": "metadata"}'
```

## Profile Regeneration

### All entities
```bash
curl -X POST http://localhost:4300/index/build-profiles -H "Content-Type: application/json" \
  -d '{"phase": "generate", "max_entities": 500}'
```

### Specific entities
```bash
curl -X POST http://localhost:4300/index/build-profiles -H "Content-Type: application/json" \
  -d '{"phase": "generate", "entity_names": ["Zion", "Mount Zion", "Judas"]}'
```

## Monitoring

```bash
# System health
curl http://localhost:4300/health

# Index status and errors
curl http://localhost:4300/index/status

# Graph statistics
curl http://localhost:4300/search/graph/summary

# Profile counts
curl "http://localhost:4300/search/graph/profiles?status=profiled&limit=1"
```

## Backup & Recovery

### Create Backups

```bash
# SQLite (critical — source of truth, includes vectors via sqlite-vec)
curl -X POST "http://localhost:4300/backup/sqlite?label=manual"

# Neo4j graph export (75K nodes + 4.5M rels in ~90s)
curl -X POST http://localhost:4300/backup/neo4j
```

### List Backups

```bash
curl http://localhost:4300/backup/sqlite
curl http://localhost:4300/backup/neo4j
```

### Restore

```bash
# Restore SQLite (WARNING: stops must be handled — no indexing during restore)
curl -X POST "http://localhost:4300/backup/sqlite/restore?filename=alejandria_manual_20260401_120000.db"

# Restore Neo4j (WARNING: clears existing graph first)
curl -X POST "http://localhost:4300/backup/neo4j/restore?filename=alejandria_graph_20260401_120000.json"

# Rebuild sqlite-vec vectors from chunk text (no filesystem I/O)
curl -X POST http://localhost:4300/index/rebuild-vectors
```

### Automatic Pre-Index Backup

The ingestion pipeline automatically backs up SQLite and Neo4j before any indexing run.
No manual action needed. SQLite rotates last 5 snapshots.

### Recovery Hierarchy

SQLite is the **source of truth** (includes vectors via sqlite-vec). From it alone, everything can be reconstructed:

| Store | Recovery from SQLite | Time |
|-------|---------------------|------|
| Vectors (sqlite-vec) | `POST /index/rebuild-vectors` | ~5 min (GPU) |
| Neo4j | Full reindex or restore from backup | ~3 hours / ~90s |

### Full Disaster Recovery

1. Clone the git repo.
2. Download backup assets from the latest `backup-*` GitHub Release.
3. Run `bash scripts/backup-pull.sh all` to restore `alejandria.db.gz` and `env.enc`.
4. Decrypt `env.enc` into `docker/.env`.
5. Download `ca-certificates.crt` from the same release into `docker/` if the target machine requires the corporate CA bundle.
6. `docker compose up --build`
7. Optionally restore Neo4j from backup: `POST /backup/neo4j/restore`

See [docs/backup.md](backup.md) for the exact release-based workflow and commands.

### What NOT to Do

- **NEVER run full reindex casually** — takes 7+ hours on CPU, deletes existing data first
- **NEVER delete `data/sqlite/alejandria.db`** without a backup — it's the source of truth
- Always prefer incremental indexing (`full_reindex: false` or omit)

## Typical Timings

| Operation | CPU | GPU | Notes |
|-----------|-----|-----|-------|
| Incremental indexing (no changes) | ~2s | ~2s | Hash comparison only |
| Incremental indexing (4 new files) | ~10s | ~10s | All 3 phases, minimal |
| Incremental indexing (40 new files) | ~100s | ~30s | All 3 phases |
| Force reindex (6,910 files) | ~2 hours | ~20 min | Format migration scenario |
| Full reindex (~27K docs) | ~7+ hours | ~45 min | **Destructive** — deletes existing data first |
| Rebuild vectors from SQLite | ~3 hours | ~5 min | Non-destructive |
| KG rebuild | ~15 min | ~15 min | CPU-bound (spaCy NER) |
| Neo4j backup (75K nodes) | ~90s | ~90s | Cypher streaming |
| Neo4j restore (75K nodes) | TBD | TBD | Node-by-node Cypher import |
| SQLite backup (~130 MB, includes vectors) | <1s | <1s | File copy |
| Metadata profiles (all entities) | ~2s | ~2s | Computational only |
| Generate profiles (200 entities) | ~3 min | ~3 min | LLM calls, ~$0.05 |
| Single chat question | 3-10s | 3-10s | Depends on model tier |

## Memory Sync (Project Memory)

Project memory for Claude sessions lives in `~/.claude/projects/.../memory/` (24 files).
Before major commits, sync to git:

```bash
bash scripts/sync-memory.sh
```
