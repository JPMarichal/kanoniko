# Alejandria Documentation

Technical documentation for the Alejandria knowledge engine.

## System Overview

Alejandria is a bilingual (Spanish/English) knowledge engine for scripture and gospel study.
It provides three search modes, a knowledge graph, entity profiles, and RAG-powered Q&A.

## Documentation Index

### Architecture
- [architecture.md](architecture.md) — System architecture, layers, data flow
- [stack.md](stack.md) — Technology stack and dependencies
- [configuration.md](configuration.md) — Environment variables and settings

### Data Layer
- [corpus.md](corpus.md) — Corpus structure, formats, bilingual organization
- [ingestion.md](ingestion.md) — Ingestion pipeline, parsing, chunking, change detection
- [scripture-references.md](scripture-references.md) — Verse-level references, citation formats

### Search
- [search-textual.md](search-textual.md) — Full-text search (SQLite FTS5, BM25)
- [search-semantic.md](search-semantic.md) — Semantic search (Qdrant, multilingual embeddings)
- [search-hybrid.md](search-hybrid.md) — Hybrid search (Reciprocal Rank Fusion)

### Knowledge Graph
- [knowledge-graph.md](knowledge-graph.md) — Neo4j graph model, nodes, relations
- [entity-extraction.md](entity-extraction.md) — Gazetteer + spaCy NER pipeline, stopword handling
- [entity-profiles.md](entity-profiles.md) — Entity profiles: metadata, LLM generation, disambiguation

### RAG & Chat
- [rag-pipeline.md](rag-pipeline.md) — RAG pipeline: retrieval, context building, answer generation
- [llm-models.md](llm-models.md) — Multi-provider LLM support, tiered model selection

### Interfaces
- [api-reference.md](api-reference.md) — REST API endpoints
- [cli.md](cli.md) — Command-line interface
- [mcp-server.md](mcp-server.md) — MCP adapter for AI assistants

### Operations
- [docker.md](docker.md) — Docker Compose setup, CPU/GPU stacks, two Docker engines
- [operations.md](operations.md) — Indexing, backup/recovery, KG rebuild, profile generation
- [performance.md](performance.md) — Memory tuning, .wslconfig, I/O optimization, pipeline profiling

### Project
- [roadmap.md](roadmap.md) — Completed phases and project incubator
- [project-memory/](project-memory/) — Claude session memory (synced from ~/.claude/)
