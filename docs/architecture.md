# Architecture

> Current state. Derives from [`system-spec.md`](system-spec.md). Structure decisions:
> [`adr/0001-storage-driver-pattern.md`](adr/0001-storage-driver-pattern.md),
> [`adr/0002-modular-monolith.md`](adr/0002-modular-monolith.md).

## System layers

```
┌─────────────────────────────────────────────────────────┐
│  Interfaces:  REST API (:4300), CLI, MCP server          │
├─────────────────────────────────────────────────────────┤
│  Knowledge:   RAG pipeline, entity profiles, LLM tiering │
├─────────────────────────────────────────────────────────┤
│  Retrieval:   textual (FTS) + semantic (pgvector) + KG   │
├─────────────────────────────────────────────────────────┤
│  Storage:     Postgres 16 + pgvector (IONOS VPS)         │
├─────────────────────────────────────────────────────────┤
│  Corpus:      bilingual documents (bind-mounted)         │
└─────────────────────────────────────────────────────────┘
```

### Corpus
Documents in `md`, `txt`, `html`, `json`, organized by language and category, **bind-mounted** from
the host — never containerized. Scripture files carry verse numbers + `.meta.json` sidecars.

### Storage — one Postgres store
**Postgres 16 + pgvector on an IONOS VPS is the sole authoritative store**: chunks, full-text index
(`tsvector` + GIN), embeddings (`chunk_embeddings`, pgvector HNSW), and the knowledge graph
(`entities`, `relations`, `entity_document_mentions`, entity profiles). Infra helpers
(connection, DDL, migrators, HNSW builder) live in `src/alejandria/storage/postgres/`.

Ingestion writes go through three cohesive Protocols (`src/alejandria/storage/__init__.py`,
per ADR 0001): `ChunkWriter`, `KnowledgeGraphWriter`, `KnowledgeGraphReader`, each with a `make_*`
factory that returns the Postgres implementation. Neo4j and SQLite/`sqlite-vec` were retired
(§3.3 / §3.4 of `postgres-migration.md`).

### Retrieval
- **Textual** (`search/textual.py`): Postgres `websearch_to_tsquery` + `ts_rank_cd` (cover-density).
- **Semantic** (`search/semantic.py`): pgvector `<=>` (cosine) against the HNSW index; score `1 - distance`.
- **Hybrid** (`search/hybrid.py`): Reciprocal Rank Fusion over the two ranked lists
  (`k = 60`, default weights 0.4 text / 0.6 semantic). Backend-agnostic — takes result dicts.
  Modes: `hybrid`, `cross-ref`, `kg-boost`, `footnote-xref`.
- **KG** (`knowledge/postgres_graph_client.py`): entity lookup, typed relations, neighbors,
  genealogy (recursive CTE), graph summary.

### Knowledge
- **Entity profiles**: per-entity metadata + LLM-generated bilingual summaries, in Postgres.
  Survive KG rebuilds; staleness-tracked.
- **RAG pipeline** (`chat/rag.py`): fuses the retrieval modes, adds profile + graph context,
  generates a grounded answer. Four LLM calls/question (expansion, entity extraction, rerank,
  answer); calls 1–3 use the cheapest tier.
- **Tiered model selection** (`chat/models.py`): a heuristic complexity classifier routes the
  answer call to fast / balanced / quality; multi-provider with a fallback chain.

### Interfaces
- **REST API** — FastAPI on port **4300** (`main.py`, `api/`). Primary.
- **MCP server** — `mcp_server.py`, `.mcp.json`; `mcp__alejandria__*` tools.
- **CLI** — Click (`cli.py`).

## Data flow

### Ingestion (3-phase, incremental via SHA-256)
```
Corpus files → parse → chunk ──┬─ Phase 1: tsvector (text + metadata)
                               ├─ Phase 2: batch-embed → pgvector upsert
                               └─ Phase 3: NER + relation extraction → KG tables
                                           + profile staleness marking
```

### Query (RAG)
```
Question → complexity classification → model selection
         → textual (tsvector) ─┐
         → semantic (pgvector) ─┼→ RRF → top chunks
         → KG context ─────────┘
         → entity-profile summaries (ES/EN)
         → LLM → grounded answer with citations
```

## Module structure (`src/alejandria/`)

Flat single package — see [`adr/0002-modular-monolith.md`](adr/0002-modular-monolith.md).

```
src/alejandria/
├── main.py · config.py · cli.py · mcp_server.py · authority.py
├── api/            REST endpoints (routes_*, schemas.py, dependencies.py)
├── ingestion/      pipeline.py, registry.py, parsers.py, chunker.py,
│                   scripture_meta.py, cross_references.py, conference_parser.py
├── search/         textual.py, semantic.py, hybrid.py
├── embeddings/     model.py (sentence-transformers singleton)
├── knowledge/      extractor.py, postgres_graph_client.py, pagerank.py,
│                   profile_store.py, profile_generator.py, disambiguator.py,
│                   family_patterns.py, ner_candidates.py, gazetteer_lookup.py, gazetteers/
├── chat/           rag.py, llm.py, models.py
└── storage/        chunk_writer.py, kg_reader.py, kg_writer.py (Protocols + factories)
    └── postgres/   connection.py, schema.py, ddl.sql, kg_cleanup.py, migrators
```

### Internal dependency direction (enforced by `import-linter`, ADR 0002)
```
api / cli / mcp_server   →   chat / knowledge   →   search / embeddings   →   storage / ingestion / config
```
Nothing imports `api`; `storage` imports nothing above it. `just check-boundaries` runs the check.

## Design principles

- **Modular monolith** — one package; boundaries declared and enforced, not networked (ADR 0002).
- **One authoritative store** — Postgres; from it the HNSW index and derived data rebuild.
- **Corpus externality** — bind-mounted, never containerized.
- **Incremental processing** — SHA-256 change detection.
- **Bilingual first** — every component handles ES + EN.
- **Graceful degradation** — semantic search and KG are optional; textual search alone still works.
- **Containers: Podman** — see `docker.md`; `docker` on this host points at Rancher Desktop and must not be used from this repo.
