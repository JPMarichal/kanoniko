# Configuration

All settings are managed via environment variables with the `ALEJANDRIA_` prefix. Configuration is loaded from `.env` files and environment variables using Pydantic Settings.

## Environment Variables

### Corpus & Storage

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_CORPUS_PATH` | `/app/corpus` | Path to the bind-mounted corpus directory |
| `ALEJANDRIA_SQLITE_DB_PATH` | `/app/data/sqlite/alejandria.db` | SQLite database for FTS, registry, and profiles |

### Qdrant (Semantic Search)

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_QDRANT_HOST` | `qdrant` | Qdrant server hostname |
| `ALEJANDRIA_QDRANT_PORT` | `6333` | Qdrant server port |
| `ALEJANDRIA_QDRANT_COLLECTION` | `alejandria` | Qdrant collection name |

### Neo4j (Knowledge Graph)

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_NEO4J_URI` | `bolt://neo4j:7687` | Neo4j connection URI |
| `ALEJANDRIA_NEO4J_USER` | `neo4j` | Neo4j username |
| `ALEJANDRIA_NEO4J_PASSWORD` | `alejandria` | Neo4j password |

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
| `ALEJANDRIA_RAG_CONTEXT_CHUNKS` | `12` | Max chunks in final LLM context |
| `ALEJANDRIA_RAG_SEARCH_LIMIT` | `25` | Candidates per search mode before fusion |

### Server

| Variable | Default | Description |
|----------|---------|-------------|
| `ALEJANDRIA_HOST` | `0.0.0.0` | Bind address |
| `ALEJANDRIA_PORT` | `4300` | API port |

## Configuration File

Settings are defined in `src/alejandria/config.py` using Pydantic's `BaseSettings` class. A `.env` file in the project root or Docker environment variables override defaults.
