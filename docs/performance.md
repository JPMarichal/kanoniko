# Performance & Memory Tuning

## System Resources

The development machine has 32 GB RAM shared between Windows, two WSL distros, and Docker.
Memory pressure is the primary constraint.

### Memory Budget (32 GB total)

| Consumer | Typical | Max | Notes |
|----------|---------|-----|-------|
| Windows + apps | 8–12 GB | — | Browsers, VS Code, etc. |
| WSL2 (shared by all distros) | 10–12 GB | 12 GB (.wslconfig) | Ubuntu-20.04 + rancher-desktop |
| → Docker containers (inside WSL) | ~1.2 GB | ~2 GB | API 220 MB + Qdrant 90 MB + Neo4j 934 MB |
| → WSL buffer/cache | 8–10 GB | — | Reclaimable; `autoMemoryReclaim=gradual` |
| **Headroom** | **~4 GB** | — | Target: never below 3 GB free |

### .wslconfig (C:\Users\<user>\.wslconfig)

```ini
[wsl2]
memory=12GB
swap=4GB
autoMemoryReclaim=gradual
```

Without this file, **each WSL distro defaults to 50% of physical RAM** (16 GB), and two
distros can claim 32 GB total — starving Windows.

**After changing `.wslconfig`, restart WSL:**
```bash
wsl --shutdown
# Then restart your distro/containers
```

### Neo4j Memory Tuning

Neo4j is the largest container. Its JVM heap is capped in `docker-compose.yml`:

```yaml
environment:
  - NEO4J_server_memory_heap_initial__size=256m
  - NEO4J_server_memory_heap_max__size=512m
  - NEO4J_server_memory_pagecache_size=128m
```

For the current graph (75K nodes, 4.5M rels), this is sufficient.
If the graph grows significantly (500K+ nodes), consider increasing to 1 GB heap.

### Qdrant Memory

Qdrant with 34,000 vectors (384 dimensions) uses ~90 MB.
At 100K vectors it would use ~250 MB. No tuning needed until then.

## I/O Performance

### Filesystem Speed

| Path | Speed | Use |
|------|-------|-----|
| `/mnt/c/...` (Windows FS via WSL) | ~1x (baseline, slow) | Code editing, git |
| `/home/...` (native Linux FS) | ~250x faster | Corpus reads, SQLite, model cache |

The GPU Docker compose overrides mount corpus and data from Linux FS for this reason.

### Docker Build

Builds are fast (~5s) when only `src/` changes (layer 16/20 in Dockerfile).
Full rebuilds (dependency changes) take 5-10 minutes due to PyTorch nightly download.

## Ingestion Pipeline

### 3-Phase Batch Architecture

The pipeline is optimized for GPU utilization:

```
Phase 1 (CPU): Parse + chunk + FTS insert     — per file, sequential
Phase 2 (GPU): Batch encode ALL chunks        — single call, batch_size=256
Phase 3 (CPU): Qdrant upsert + KG extraction  — per file, sequential
```

Phase 2 is the key optimization: instead of encoding file-by-file (which leaves the GPU
idle between files), all chunks from all files are collected and encoded in one batch.

### Neo4j Batch Writes

KG extraction uses UNWIND-based batch operations (500 chunks per batch) instead of
individual merge calls. This reduced `rebuild-kg` from ~19h to ~27 min (43x speedup).
Batch methods: `batch_merge_entities()`, `batch_merge_relations()`,
`batch_link_entities_to_document()`, `batch_merge_documents()`.

### Embedding Performance

| Device | Speed | Full Reindex (19,770 docs) |
|--------|-------|---------------------------|
| CPU (i7) | ~23 chunks/min | ~7+ hours |
| GPU (RTX PRO 500, 6 GB) | ~600-800 chunks/min | ~45 min |

### Memory During Indexing

Peak memory during Phase 2 (batch encoding of 34K chunks):
- GPU VRAM: ~1.5 GB (model + batch tensors)
- System RAM: ~500 MB (chunk text buffer)

## Monitoring Commands

```bash
# Docker container stats (CPU, RAM, network)
wsl -d Ubuntu-20.04 bash -c "export DOCKER_HOST=unix:///var/run/docker.sock && /usr/bin/docker stats --no-stream"

# WSL memory
wsl -d Ubuntu-20.04 bash -c "free -h"

# GPU status
wsl -d Ubuntu-20.04 bash -c "nvidia-smi"

# Windows Task Manager
# Memory → check "Available" stays above 3 GB
```

## Troubleshooting

### "Out of memory" or system freeze
1. Check if `.wslconfig` exists and limits memory to 12 GB
2. After editing, run `wsl --shutdown` and restart services
3. Close unnecessary browser tabs (biggest Windows memory consumer)

### GPU at 0% during indexing
The pipeline uses 3-phase batch encoding. If GPU shows 0%, Phase 1 or 3 is running (CPU-bound).
GPU utilization spikes during Phase 2 only.

### Slow corpus reads in Docker
Ensure the GPU compose override mounts from Linux FS (`/home/...`), not Windows FS (`/mnt/c/...`).
