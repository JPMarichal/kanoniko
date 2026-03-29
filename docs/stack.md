# Technology Stack

## Core

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.11 | Application runtime |
| Web framework | FastAPI | REST API |
| CLI | Click | Command-line interface |
| Configuration | Pydantic Settings | Env-based config with validation |

## Storage & Search

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Full-text search | SQLite FTS5 | BM25 ranking, chunk storage, document registry, entity profiles |
| Semantic search | Qdrant | Vector similarity search |
| Knowledge graph | Neo4j | Entity/relation graph, document linkage |
| Embeddings | sentence-transformers | `paraphrase-multilingual-MiniLM-L12-v2` (384 dims, bilingual ES/EN) |

## NLP & AI

| Component | Technology | Purpose |
|-----------|-----------|---------|
| NER | spaCy (`en_core_web_sm`, `es_core_news_sm`) | Auto-discovery of entities not in gazetteers |
| Entity matching | Custom gazetteers + regex | Curated biblical entity detection |
| LLM providers | Anthropic, Google Gemini, OpenAI, DeepSeek | RAG answer generation, entity profiles |

## Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containerization | Docker Compose | 3 services: api, qdrant, neo4j |
| API server | Uvicorn | ASGI server |
| MCP protocol | `mcp` Python SDK | AI assistant integration |

## Python Dependencies

Key packages (see `pyproject.toml` for full list):
- `fastapi`, `uvicorn` — Web server
- `pydantic`, `pydantic-settings` — Data validation
- `sentence-transformers` — Embedding model
- `qdrant-client` — Vector DB client
- `neo4j` — Graph DB driver
- `spacy` — NER
- `click` — CLI
- `mcp` — MCP server SDK
- `anthropic`, `google-generativeai`, `openai` — LLM clients
