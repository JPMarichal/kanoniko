---
name: Development Machine
description: Hardware specs, GPU setup, Docker environments (Rancher Desktop + native GPU Docker), Python versions
type: user
---

## Hardware
- **RAM:** 32 GB DDR5 5600 MT/s (2x SODIMM, both slots used)
- **GPU 0:** NVIDIA RTX PRO 500 Blackwell Generation Laptop GPU, 6 GB VRAM, sm_120
- **GPU 1:** Intel Arc Pro (integrated, used for display)
- **NPU:** Intel AI Boost (not used yet)
- **NVIDIA Driver:** 581.95, CUDA 13.0
- **OS:** Windows 11 Pro (laptop)

## Docker — Two Independent Engines
| | Rancher Desktop | Docker Engine nativo (GPU) |
|---|---|---|
| **WSL distro** | `rancher-desktop` | `Ubuntu-20.04` |
| **Docker version** | 29.1.3 (server) | 28.1.1 |
| **GPU** | No | NVIDIA runtime (default) |
| **Use** | Regular work | Alejandría GPU workloads |
| **daemon.json** | Managed by Rancher | `/etc/docker/daemon.json` with nvidia default-runtime |

- **CRITICAL:** Do NOT modify Rancher Desktop — user depends on it for regular work
- WSL user `jpmarichal` is in `docker` group for native Docker Engine
- Credential helper: use `DOCKER_CONFIG=/tmp/alejandria-docker-config` to avoid Rancher Desktop's secretservice

## WSL
- **Distros:** Ubuntu-20.04 (running, systemd enabled), rancher-desktop (running)
- **Kernel:** 6.6.87.2-microsoft-standard-WSL2

## Python
- **Windows:** 3.7.4 (too old for Alejandria, needs 3.11) — DO NOT MODIFY
- **Ubuntu WSL:** 3.8.10 system + Miniconda with `alejandria` env (Python 3.11.15)
- **PyTorch:** nightly 2.12.0+cu128 in conda env (required for Blackwell sm_120 support)

## GPU Workflows
- **Script:** `scripts/gpu-up.sh` — manages Alejandría GPU stack from WSL (up/down/status/test/logs)
- **Compose override:** `docker/docker-compose.gpu.yml` + `docker/Dockerfile.gpu` (PyTorch CUDA + nvidia device reservation)
- **Standalone reindex:** `scripts/gpu_reindex.py` from Ubuntu WSL conda env connecting to Docker services
- **Embedding model:** paraphrase-multilingual-MiniLM-L12-v2 (~120MB) — fits easily in 6GB VRAM
- **CPU embedding speed:** ~10 docs/min (~23 chunks/min) — full reindex ~5 hours
- **GPU embedding speed:** ~600-800 chunks/min — full reindex ~20 min

## Linux FS Strategy
- Corpus is git-cloned to `/home/jpmarichal/alejandria-repo` on native Linux FS (~250x faster I/O than /mnt/c)
- `gpu-up.sh` auto-syncs via `git fetch` + `git reset --hard` before starting
- SQLite data at `/home/jpmarichal/alejandria-data/sqlite/` (bind-mounted into API container)
- Model cache at `/home/jpmarichal/alejandria-data/models/`

## Backup System (Tested & Working)
- **SQLite:** timestamped copy, rotates last 5 (`POST /backup/sqlite`)
- **Qdrant:** native REST snapshot (`POST /backup/qdrant`)
- **Neo4j:** Cypher streaming to JSON on API filesystem — 75K nodes + 4.5M rels in ~90s (`POST /backup/neo4j`)
- **Pre-index:** automatic backup of all three stores before any indexing run
- Neo4j backup does NOT use APOC file export (avoids permission issues); uses plain Cypher queries streamed to API container
- SQLite DB (85 MB) tracked in git as disaster recovery baseline
