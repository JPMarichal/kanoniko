# Technology Stack

> Current state. Derives from [`system-spec.md`](system-spec.md). Full dependency list: `pyproject.toml`.

## Core

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python ≥ 3.11 | Application runtime |
| Web framework | FastAPI + Uvicorn | REST API (:4300) |
| CLI | Click | Command-line interface |
| Configuration | Pydantic Settings | Env-based config with validation |
| Package layout | Flat `src/alejandria/` (hatchling build) | Modular monolith — [`adr/0002`](adr/0002-modular-monolith.md) |

## Storage & search

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Authoritative store | **Postgres 16 + pgvector** (IONOS VPS) | Chunks, FTS, embeddings, KG — everything |
| Full-text search | Postgres `tsvector` + GIN, `ts_rank_cd` | `websearch_to_tsquery('spanish', …)`; p95 ~44 ms |
| Semantic search | pgvector HNSW, `<=>` cosine | 384-dim vectors in `chunk_embeddings` |
| Knowledge graph | Postgres tables + `PostgresGraphClient` | `entities`, `relations`, `entity_document_mentions`, profiles; recursive CTEs for genealogy |
| Embeddings | `sentence-transformers` | `paraphrase-multilingual-MiniLM-L12-v2` (384 dim, ES/EN) — in-process singleton |

> **Retired:** Neo4j (KG → Postgres, §3.3), SQLite FTS5 + `sqlite-vec` (§3.4), Qdrant (→ pgvector).
> History and reconsideration triggers: [`vector-db-options.md`](vector-db-options.md).

## NLP & AI

| Component | Technology | Purpose |
|-----------|-----------|---------|
| NER | spaCy (`en_core_web_sm`, `es_core_news_sm`) | Entity auto-discovery beyond the gazetteers |
| Entity matching | Curated bilingual gazetteers + regex | Canonical biblical entities |
| Relation extraction | Deterministic patterns + curated seeds | Family patterns, curated `relations.json` |
| Graph retrieval | Personalized PageRank (`knowledge/pagerank.py`) | Experimental multi-hop — `architecture-proposals/ppr-implementation-plan.md` |
| LLM providers | Anthropic, Gemini, OpenAI, DeepSeek, Ollama | RAG answers, entity profiles; tiered + fallback chain |

## Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containers | **Podman** (`podman-machine-default`) | `alejandria-api`, `alejandria-ollama`. Migrated from native Docker 2026-07-04 (`project-memory/project_podman_migration.md`). |
| Compose | `docker/docker-compose.podman.yml` | Podman override; management via `scripts/gpu-podman.sh` |
| GPU | NVIDIA RTX PRO 500 Blackwell (sm_120), CUDA 12 nightly | `Dockerfile.gpu` |
| DB access | SSH tunnel `localhost:15432 → VPS:5432` (inside the Podman machine) | `sshtunnel` |
| Backup | `pg_dump` cron on the VPS (03:15 UTC, 14-day rotation) | Sole canonical backup; API container is stateless |
| MCP protocol | `mcp` Python SDK | AI-assistant integration |

## Python dependencies

Base: `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `click`, `beautifulsoup4`,
`markdown-it-py`, `aiofiles`.
Optional extras (`pyproject.toml`): `postgres` (`psycopg[binary]`, `pgvector`, `sshtunnel`),
`semantic` (`sentence-transformers`), `graph` (`spacy`), `mcp`, `chat` (`anthropic`, `openai`),
`dev` (`pytest`, `pytest-asyncio`, `httpx`, `ruff`, `import-linter`).
