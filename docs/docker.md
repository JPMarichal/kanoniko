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

| Service | Image | Purpose | Ports |
|---------|-------|---------|-------|
| `api` | Custom (Dockerfile) | FastAPI + Python app | 4300 |
| `qdrant` | `qdrant/qdrant` | Vector database | 6333, 6334 |
| `neo4j` | `neo4j:5` | Graph database | 7687, 7474 |

## Volumes & Bind Mounts

| Mount | Container Path | Purpose |
|-------|---------------|---------|
| `./corpus` | `/app/corpus` | Bilingual text corpus (read-only) |
| `./data` | `/app/data` | SQLite databases (persistent) |
| `qdrant_data` | `/qdrant/storage` | Qdrant vectors (Docker volume) |
| `neo4j_data` | `/data` | Neo4j graph (Docker volume) |

## Building & Running

```bash
cd docker

# First time (downloads ~500MB embedding model)
docker compose up --build

# Background
docker compose up --build -d

# Rebuild after code changes
docker compose up --build -d

# View logs
docker compose logs -f api
```

## SSL / Corporate Proxy

The Dockerfile expects `docker/ca-certificates.crt` for corporate CA certificates (needed for model downloads behind proxies).

Generate it:
```bash
python docker/export_certs.py
```

This file is gitignored — each dev machine generates its own.

## Environment Variables

Pass via `docker-compose.yml` environment section or `.env` file. See [configuration.md](configuration.md) for full list.

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
