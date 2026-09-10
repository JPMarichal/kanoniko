# Alejandria Documentation

> ⚠️ **Environment rule:** this project lives in `C:\own\alejandria` and operates exclusively on **Podman**. Do not use `docker` or `docker compose` from this folder, because on this host `docker` points to Rancher Desktop/Moby and would touch containers from `C:\git`.

Technical documentation for the Alejandria knowledge engine.

> **Start here:** [system-spec.md](system-spec.md) is the single source of truth for what the system
> *is* today. [planning-index.md](planning-index.md) maps every plan/proposal and their authority —
> read it when planning docs seem to disagree. Incubator format: [`../proj/CONVENTIONS.md`](../proj/CONVENTIONS.md).

## System Overview

Alejandria is a bilingual (Spanish/English) knowledge engine for scripture and gospel study.
It provides three search modes, a knowledge graph, entity profiles, and RAG-powered Q&A.

## Documentation Index

### Architecture
- [architecture.md](architecture.md) — System architecture, layers, data flow
- [stack.md](stack.md) — Technology stack and dependencies
- [adr/](adr/) — Architecture Decision Records ([0001](adr/0001-storage-driver-pattern.md) storage driver pattern · [0002](adr/0002-modular-monolith.md) modular monolith)
- [configuration.md](configuration.md) — Environment variables and settings
- [architecture-proposals/](architecture-proposals/) — Architecture improvement proposals and repository split analysis

### Data Layer
- [corpus.md](corpus.md) — Corpus structure, formats, bilingual organization
- [download-scripts.md](download-scripts.md) — Download scripts: Church site patterns, shared module, footnote handling
- [ingestion.md](ingestion.md) — Ingestion pipeline, parsing, chunking, change detection
- [scripture-references.md](scripture-references.md) — Verse-level references, citation formats

### Search
- [search-textual.md](search-textual.md) — Full-text search (Postgres tsvector, ts_rank_cd)
- [search-semantic.md](search-semantic.md) — Semantic search (pgvector HNSW, multilingual embeddings)
- [search-hybrid.md](search-hybrid.md) — Hybrid search (Reciprocal Rank Fusion)

### Knowledge Graph
- [knowledge-graph.md](knowledge-graph.md) — Postgres KG model (PostgresGraphClient), nodes, relations
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
- [docker.md](docker.md) — Podman compose, GPU stack
- [operations.md](operations.md) — Indexing, backup/recovery, KG rebuild, profile generation
- [performance.md](performance.md) — Memory tuning, .wslconfig, I/O optimization, pipeline profiling
- [backup.md](backup.md) — DB & secrets distribution via GitHub Releases, backup frequency, new machine setup

### Project
- [system-spec.md](system-spec.md) — **Current state of the whole system** (source of truth for what IS)
- [planning-index.md](planning-index.md) — Map of every planning artifact, its authority and status; open contradictions
- [roadmap.md](roadmap.md) — Priority-ordered project incubator (P1–P13, WI-1–3)
- [improvement-analysis-2026.md](improvement-analysis-2026.md) — SWOT, pain→technology mapping, 2026 tech landscape, roadmap evaluation, Graphify assessment
- [improvement-program-2026.md](improvement-program-2026.md) — Phased modernization program + live tracking (Fases A–G; projects P0, P11, P12, WI-3)
- [../proj/CONVENTIONS.md](../proj/CONVENTIONS.md) — Spec-driven incubator format (spec → plan → tasks → risks)
- [architecture-proposals/](architecture-proposals/) — Graph-enhanced RAG / PPR proposals (inputs, not plans)
- [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) — Microservices split proposal (**not adopted** — see planning-index)
- [project-memory/](project-memory/) — Claude session memory (synced from ~/.claude/)
