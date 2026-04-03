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

# Step 2: index everything in a single incremental pass when ready
curl -X POST http://localhost:4300/index/trigger
# or target a specific directory:
curl -X POST http://localhost:4300/index/ingest \
  -H "Content-Type: application/json" \
  -d '{"paths": ["corpus/en/manuals/jesus-the-christ", "corpus/es/manuals/jesus-the-christ"]}'
```

**Incremental indexing** detects changes via SHA-256 hashes — only new or
modified files are processed regardless of how long ago they were added.

### When to use `/ingest` vs `/trigger`

| Endpoint | Use when |
|----------|----------|
| `POST /index/ingest` | You know exactly which directories were added — faster, targeted |
| `POST /index/trigger` | You've added many scattered files and want a full corpus scan |

### Incremental vs. Force: understanding the cost

**Incremental** (default): only processes files whose SHA-256 changed. Adding 20 new
files to a 27K-file corpus takes ~50 seconds — the pipeline skips everything unchanged.

**Force** (`"force": true`): re-processes files even if their hash hasn't changed. This
is needed only for **migrations** — when the parser, chunker, or extractor logic changes
and existing files need to be re-processed with the new code. Force re-indexing 6,910
files takes ~2 hours (phases 2+3 dominate — see below).

The three pipeline phases have very different costs:

| Phase | What | Speed | Bottleneck |
|-------|------|-------|------------|
| 1. Parse/Chunk/FTS | Parse file, chunk text, insert into SQLite FTS | ~200 files/min | CPU (fast) |
| 2. Embeddings | Encode chunks into vectors, upsert to Qdrant | ~4K vectors/10 min (CPU) | GPU or CPU |
| 3. KG extraction | spaCy NER + Neo4j writes per chunk | Variable | Neo4j I/O |

**`/index/status` only tracks Phase 1 progress.** It can show 100% while phases 2 and 3
are still running. The ETA it reports underestimates total time significantly for
force-reindex operations. Check `/health` to monitor vector and graph node counts growing.

### Real-world indexing times (observed)

| Operation | Files | Wall time | Notes |
|-----------|-------|-----------|-------|
| Proclamations (incremental) | 4 | ~10 sec | New files, all 3 phases |
| Missionary manuals (incremental) | 40 | 100 sec | New files, all 3 phases |
| Conference talks (force, format migration) | 6,910 | ~2 hours | Phase 1: 45 min, Phase 2+3: ~75 min |
| Full reindex (all corpus) | ~27K | 7+ hours (CPU) | **Destructive** — avoid |

**Rule of thumb:** incremental indexing of new material is fast (~2-3 sec/file). Force
re-indexing of existing material is 10-50× slower per file due to Qdrant/Neo4j overhead
on data that already exists.

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
# SQLite (critical — source of truth)
curl -X POST "http://localhost:4300/backup/sqlite?label=manual"

# Qdrant snapshot
curl -X POST http://localhost:4300/backup/qdrant

# Neo4j graph export (75K nodes + 4.5M rels in ~90s)
curl -X POST http://localhost:4300/backup/neo4j
```

### List Backups

```bash
curl http://localhost:4300/backup/sqlite
curl http://localhost:4300/backup/neo4j
curl http://localhost:4300/backup/qdrant
```

### Restore

```bash
# Restore SQLite (WARNING: stops must be handled — no indexing during restore)
curl -X POST "http://localhost:4300/backup/sqlite/restore?filename=alejandria_manual_20260401_120000.db"

# Restore Neo4j (WARNING: clears existing graph first)
curl -X POST "http://localhost:4300/backup/neo4j/restore?filename=alejandria_graph_20260401_120000.json"

# Rebuild Qdrant vectors from SQLite (no filesystem I/O)
curl -X POST http://localhost:4300/index/rebuild-vectors
```

### Automatic Pre-Index Backup

The ingestion pipeline automatically backs up all three stores before any indexing run.
No manual action needed. SQLite rotates last 5 snapshots.

### Recovery Hierarchy

SQLite is the **source of truth**. From it alone, everything can be reconstructed:

| Store | Recovery from SQLite | Time |
|-------|---------------------|------|
| Qdrant | `POST /index/rebuild-vectors` | ~5 min (GPU) |
| Neo4j | Full reindex or restore from backup | ~3 hours / ~90s |

### Full Disaster Recovery

1. Clone the git repo (contains code, corpus, SQLite DB, gazetteers)
2. Copy `.env` from `OneDrive/alejandria-secrets/.env`
3. `docker compose up --build`
4. Data is already in git — system is operational immediately
5. Optionally restore Neo4j from backup: `POST /backup/neo4j/restore`

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
| SQLite backup (85 MB) | <1s | <1s | File copy |
| Qdrant snapshot (118 MB) | ~1s | ~1s | Native REST API |
| Metadata profiles (all entities) | ~2s | ~2s | Computational only |
| Generate profiles (200 entities) | ~3 min | ~3 min | LLM calls, ~$0.05 |
| Single chat question | 3-10s | 3-10s | Depends on model tier |

## Memory Sync (Project Memory)

Project memory for Claude sessions lives in `~/.claude/projects/.../memory/` (24 files).
Before major commits, sync to git:

```bash
bash scripts/sync-memory.sh
```
