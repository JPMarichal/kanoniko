# Architecture

## System Layers

Alejandria is organized in four layers, each building on the previous:

```
┌─────────────────────────────────────────────────┐
│  Interfaces: REST API, CLI, MCP Server          │
├─────────────────────────────────────────────────┤
│  Knowledge: RAG Pipeline, Entity Profiles,      │
│             LLM Integration, Synthesis          │
├─────────────────────────────────────────────────┤
│  Index: FTS5, Qdrant Vectors, Neo4j Graph       │
├─────────────────────────────────────────────────┤
│  Corpus: Bilingual documents (bind-mounted)     │
└─────────────────────────────────────────────────┘
```

### Layer 1 — Corpus
Raw documents in multiple formats (md, txt, html, json), organized by language and category. The corpus is **not containerized** — it's bind-mounted from the host filesystem, allowing independent scaling and management.

### Layer 2 — Index
Three complementary search indices:
- **SQLite FTS5**: Full-text search with BM25 ranking. Primary storage for chunks, metadata, and document registry.
- **Qdrant**: Vector database for semantic similarity search using multilingual embeddings.
- **Neo4j**: Knowledge graph storing entities, relations, and document connections.

### Layer 3 — Knowledge
Intelligence built on top of the indices:
- **Entity Profiles**: Persistent metadata and LLM-generated bilingual summaries per entity, stored in SQLite. Survives KG rebuilds.
- **RAG Pipeline**: Retrieves from all three search modes, builds context with entity profiles and graph data, generates grounded answers via LLM.
- **Tiered Model Selection**: Routes questions to appropriate LLM tier (fast/balanced/quality) based on complexity.

### Layer 4 — Interfaces
Multiple access points to the knowledge engine:
- **REST API** (FastAPI, port 4300): Primary interface
- **MCP Server** (stdio): For AI assistants like Claude
- **CLI** (Click): Command-line access

## Data Flow

### Ingestion
```
Corpus files → Parser → Chunker → FTS5 (text + metadata)
                                 → Qdrant (embeddings)
                                 → Neo4j (entities + relations)
                                 → Profile staleness marking
```

### Query (RAG)
```
Question → Complexity classification → Model selection
         → Text search (FTS5)  ─┐
         → Semantic search      ├→ RRF fusion → Top chunks
         → Graph context ───────┘
         → Entity profiles (bilingual summaries)
         → LLM generates grounded answer
```

## Module Structure

```
src/alejandria/
├── main.py              # FastAPI app
├── config.py            # Environment-based settings
├── cli.py               # Click CLI
├── mcp_server.py        # MCP adapter
├── api/                 # REST endpoints
│   ├── routes_search.py
│   ├── routes_chat.py
│   ├── routes_graph.py
│   ├── routes_index.py
│   ├── routes_docs.py
│   ├── schemas.py
│   └── dependencies.py
├── ingestion/           # Corpus processing
│   ├── pipeline.py
│   ├── registry.py
│   ├── parsers.py
│   ├── chunker.py
│   ├── scripture_meta.py
│   └── cross_references.py
├── search/              # Search engines
│   ├── textual.py
│   ├── semantic.py
│   └── hybrid.py
├── embeddings/          # Sentence-transformers
│   └── model.py
├── knowledge/           # KG + profiles
│   ├── extractor.py
│   ├── neo4j_client.py
│   ├── profile_store.py
│   ├── profile_generator.py
│   └── gazetteers/
├── chat/                # RAG + LLM
│   ├── rag.py
│   ├── llm.py
│   └── models.py
```

## Design Principles

- **Independence**: Alejandria is a standalone service, not an extension of existing tools
- **Containerization**: Docker Compose with isolated services (API, Qdrant, Neo4j)
- **Corpus externality**: Corpus is bind-mounted, never containerized
- **Incremental processing**: SHA-256 change detection for efficient re-indexing
- **Bilingual first**: All components handle Spanish and English natively
- **Graceful degradation**: Semantic search and KG are optional — system works with FTS alone
