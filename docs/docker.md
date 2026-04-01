# Docker Setup

Alejandria runs as three containerized services via Docker Compose.

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌──────────────┐
│   alejandria-api │    │  qdrant      │    │  neo4j       │
│   (Python/FastAPI)│───→│  (vectors)   │    │  (graph)     │
│   Port: 4300     │    │  Port: 6333  │    │  Port: 7687  │
│                  │───→│              │    │  UI: 7474    │
│                  │───→│              │    │              │
└────────┬─────────┘    └──────────────┘    └──────────────┘
         │
    ┌────▼────┐
    │ corpus/ │  (bind mount)
    │ data/   │  (bind mount)
    └─────────┘
```

## Services

| Service | Image | Purpose | Ports | Typical RAM |
|---------|-------|---------|-------|-------------|
| `api` | Custom (Dockerfile/Dockerfile.gpu) | FastAPI + Python app | 4300 | ~220 MB |
| `qdrant` | `qdrant/qdrant:v1.13.2` | Vector database | 6333, 6334 | ~90 MB |
| `neo4j` | `neo4j:5-community` | Graph database | 7687, 7474 | ~900 MB |

Neo4j is the heaviest container. Its JVM heap is capped at 512 MB with 128 MB page cache
(see `docker-compose.yml` environment variables).

## Two Docker Environments

This project uses **two independent Docker engines** on the same machine:

| | Rancher Desktop | Docker Engine nativo (GPU) |
|---|---|---|
| **WSL distro** | `rancher-desktop` | `Ubuntu-20.04` |
| **Docker version** | 29.1.3 | 28.1.1 |
| **GPU** | No | NVIDIA runtime (default) |
| **Use** | Regular work (**do NOT modify**) | Alejandria GPU workloads |
| **daemon.json** | Managed by Rancher | `/etc/docker/daemon.json` with nvidia default-runtime |

**CRITICAL:** Never modify the Rancher Desktop installation. The user depends on it for work.

### CPU Stack (Rancher Desktop)

```bash
cd docker && docker compose up --build -d
```

Uses `docker-compose.yml` + `Dockerfile`. Embedding on CPU (~10 docs/min).

### GPU Stack (Native Docker Engine)

```bash
# From Windows:
wsl -d Ubuntu-20.04 bash -c "bash '/mnt/c/own/alejandria/scripts/gpu-up.sh' up"
wsl -d Ubuntu-20.04 bash -c "bash '/mnt/c/own/alejandria/scripts/gpu-up.sh' down"
wsl -d Ubuntu-20.04 bash -c "bash '/mnt/c/own/alejandria/scripts/gpu-up.sh' status"
wsl -d Ubuntu-20.04 bash -c "bash '/mnt/c/own/alejandria/scripts/gpu-up.sh' logs"
```

Uses `docker-compose.yml` + `docker-compose.gpu.yml` (override) + `Dockerfile.gpu`.
- PyTorch nightly cu128 for Blackwell sm_120 GPU
- Corpus on native Linux FS at `/home/jpmarichal/alejandria-repo` (250x faster I/O)
- Auto-syncs repo via `git fetch` + `git reset --hard` before starting
- NVIDIA RTX PRO 500 Blackwell, 6 GB VRAM
- Embedding speed: ~600-800 chunks/min (vs ~23/min on CPU)

### GPU Stack — Credential Helper Workaround

`gpu-up.sh` strips Rancher Desktop from PATH and uses a clean DOCKER_CONFIG
to prevent `docker-credential-secretservice` errors during build/pull.

## Volumes & Bind Mounts

### CPU Stack
| Mount | Container Path | Purpose |
|-------|---------------|---------|
| `../corpus` | `/app/corpus:ro` | Bilingual text corpus |
| `../data/sqlite` | `/app/data/sqlite` | SQLite databases |
| `alejandria-models` (volume) | `/root/.cache` | Embedding model cache |
| `alejandria-qdrant` (volume) | `/qdrant/storage` | Qdrant vectors |
| `alejandria-neo4j` (volume) | `/data` | Neo4j graph |

### GPU Stack (overrides)
| Mount | Container Path | Purpose |
|-------|---------------|---------|
| `/home/jpmarichal/alejandria-repo/corpus` | `/app/corpus:ro` | Corpus on Linux FS |
| `/home/jpmarichal/alejandria-data/sqlite` | `/app/data/sqlite` | SQLite on Linux FS |
| `/home/jpmarichal/alejandria-data/models` | `/root/.cache` | Model cache on Linux FS |

## SSL / Corporate Proxy

The Dockerfile expects `docker/ca-certificates.crt` for corporate CA certificates.

```bash
python docker/export_certs.py
```

This file is gitignored — each dev machine generates its own.

## Environment Variables

Pass via `docker-compose.yml` environment section or `.env` file. See [configuration.md](configuration.md).

## Running Tests

```bash
docker run --rm \
  -v ./tests:/app/tests \
  -v ./src:/app/src \
  docker-api \
  bash -c "pip install -q pytest httpx && python -m pytest /app/tests/ -v"
```

## Health Check

```bash
curl http://localhost:4300/health
```
