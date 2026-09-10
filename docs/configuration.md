# Configuration

All settings are managed via environment variables with the `ALEJANDRIA_` prefix. Configuration is loaded from `.env` files and environment variables using Pydantic Settings.

## Environment Variables

### Corpus

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_CORPUS_PATH` | `/app/corpus` | Path to the bind-mounted corpus directory |

### Storage — Postgres (single authoritative store: chunks, FTS, embeddings, KG)

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_POSTGRES_HOST` | `postgres` | Host (`127.0.0.1` when using the SSH tunnel) |
| `ALEJANDRIA_POSTGRES_PORT` | `5432` | Port (`15432` via the tunnel) |
| `ALEJANDRIA_POSTGRES_USER` | `alejandria` | Role |
| `ALEJANDRIA_POSTGRES_PASSWORD` | *(empty)* | Password |
| `ALEJANDRIA_POSTGRES_DB` | `alejandria` | Database |
| `ALEJANDRIA_POSTGRES_SSLMODE` | `prefer` | `disable` \| `prefer` \| `require` \| `verify-ca` \| `verify-full` |
| `ALEJANDRIA_POSTGRES_STATEMENT_TIMEOUT_MS` | `30000` | Hard cap on any single query |
| `ALEJANDRIA_POSTGRES_APPLICATION_NAME` | `alejandria` | `application_name` tag |

FTS (`tsvector`), vectors (pgvector HNSW) and the KG all live in this database — no separate config.
Neo4j and SQLite were retired.

### SSH tunnel (dev access to the IONOS VPS)

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_SSH_TUNNEL_ENABLED` | `false` | Open a tunnel on startup |
| `ALEJANDRIA_SSH_TUNNEL_HOST` / `_USER` / `_PORT` | — / — / `22` | VPS SSH target |
| `ALEJANDRIA_SSH_TUNNEL_LOCAL_PORT` | `15432` | Local bind |
| `ALEJANDRIA_SSH_TUNNEL_REMOTE_PORT` | `5432` | Remote Postgres port |
| `ALEJANDRIA_SSH_TUNNEL_PRIVATE_KEY_PATH` | `/root/.ssh/tunnel_key` | Key path |

### Embeddings

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_EMBEDDING_MODEL` | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Embedding model name |
| `ALEJANDRIA_EMBEDDING_DEVICE` | `cuda` | Device for inference (`cuda` or `cpu`) |
| `ALEJANDRIA_EMBEDDING_DIM` | `384` | Vector dimensions |

### Chunking

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_CHUNK_SIZE` | `500` | Target words per chunk |
| `ALEJANDRIA_CHUNK_OVERLAP` | `50` | Overlap words between chunks |

### LLM (Multi-Provider)

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_LLM_PROVIDER` | `anthropic` | Default provider: `anthropic`, `gemini`, `openai`, `deepseek` |
| `ALEJANDRIA_LLM_MODEL` | `claude-haiku-4-5-20251001` | Default model |
| `ALEJANDRIA_LLM_API_KEY` | *(empty)* | Default API key |
| `ALEJANDRIA_LLM_MAX_TOKENS` | `2048` | Max output tokens |
| `ALEJANDRIA_LLM_TEMPERATURE` | `0.3` | Response temperature |

#### Per-Provider API Keys (Preferred)

| Variable | Description |
|----------|-------------|
| `ALEJANDRIA_LLM_ANTHROPIC_API_KEY` | Anthropic (Claude) API key |
| `ALEJANDRIA_LLM_GEMINI_API_KEY` | Google Gemini API key |
| `ALEJANDRIA_LLM_OPENAI_API_KEY` | OpenAI API key |
| `ALEJANDRIA_LLM_DEEPSEEK_API_KEY` | DeepSeek API key |

#### Tiered Selection

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_LLM_ANSWER_TIER` | `auto` | Tier for answers: `auto`, `fast`, `balanced`, `quality`, or model ID |
| `ALEJANDRIA_LLM_INTERNAL_TIER` | `fast` | Tier for internal calls (query expansion, reranking) |

### Entity Profiles

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_PROFILE_MAX_PASSAGES` | `10` | Max key passages per profile |
| `ALEJANDRIA_PROFILE_LLM_TIER` | `fast` | LLM tier for profile generation |

### RAG

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_RAG_CONTEXT_CHUNKS` | `8` | Max chunks in final LLM context |
| `ALEJANDRIA_RAG_CONTEXT_CHUNKS_QUALITY` | `12` | Max chunks for QUALITY-tier questions |
| `ALEJANDRIA_RAG_SEARCH_LIMIT` | `25` | Candidates per search mode before fusion |

### Server

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_HOST` | `0.0.0.0` | Bind address |
| `ALEJANDRIA_PORT` | `4300` | API port |

## Configuration File

Settings are defined in `src/alejandria/config.py` using Pydantic's `BaseSettings` class. A `.env` file in the project root or Docker environment variables override defaults.
