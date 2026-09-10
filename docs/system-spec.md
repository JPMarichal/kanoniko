# System Spec — Alejandría (current state)

> **This is the single source of truth for what the system IS today.** Not a plan. Per-feature docs
> (`architecture.md`, `stack.md`, `search-*.md`, `knowledge-graph.md`, …) derive from this file and
> must stay consistent with it. Plans and proposals live elsewhere — see
> [`planning-index.md`](planning-index.md).
>
> **Last verified:** 2026-09-09 (against `main` @ merge of PR #14; storage facts from the A0 audit,
> `proj/P0-postgres-cutover/00-state-audit.md`).
> **Update rule:** a project changes this file only when its work lands. Every edit updates
> "Last verified".

---

## 1. What Alejandría is

A bilingual (ES/EN) knowledge engine for scripture and gospel study. It ingests a corpus of LDS
canonical texts and related literature, and exposes three search modes (textual, semantic,
knowledge-graph), entity profiles, and a RAG chat endpoint. Backend only; the user-facing chat
client is a future product.

- **Language:** Python 3.11 (repo runs under 3.14 locally with workarounds noted per machine).
- **Package layout:** single flat package `src/alejandria/` (`api`, `chat`, `embeddings`,
  `ingestion`, `knowledge`, `search`, `storage`). A 4-package `uv`/`hatch` split was attempted on
  branch `workspace-migration` and **abandoned**.
- **API:** FastAPI on port **4300**. Interfaces, in priority order: REST → MCP adapter → CLI.

## 2. Corpus

- Bind-mounted at `corpus/`, **not** containerized. Layout:
  `corpus/{lang}/{scriptures|general-conference|books|biographies|manuals|proclamations|web|...}/…`.
- Scriptures: verse-numbered `.txt` + `.meta.json` sidecars (title, summary, footnotes,
  cross-references). EN + ES complete for all 5 standard works (from churchofjesuschrist.org, P2).
- ~56K documents / ~309K chunks / ~217K embedding vectors (order of magnitude; grows ~1–10K
  chunks/month).
- Incremental ingestion via SHA-256 change detection. 3-phase pipeline: (1) parse + chunk + FTS,
  (2) batch embed, (3) NER + KG extraction.

## 3. Storage — single Postgres store

**Postgres 16 + pgvector on an IONOS VPS is the sole authoritative store** for: chunks, full-text
search (`tsvector`), embeddings (pgvector / HNSW), and the knowledge graph (entities, relations,
mentions, entity profiles).

- **Neo4j: retired.** No dependency, no container, no `neo4j_client.py`. `PostgresGraphClient`
  (`src/alejandria/knowledge/postgres_graph_client.py`) is the KG client — fully implemented, no
  `NotImplementedError`. Read parity validated: **31/31 golden queries pass** against Postgres
  (`tests/parity/`, commit `ecd885fc8d`).
- **SQLite / `sqlite-vec`: retired.** No dependency, no code path, no storage-backend feature flag.
- **Qdrant: retired.** It was the Phase-2 vector store; consolidated into pgvector. Rationale and
  reconsideration triggers: `docs/vector-db-options.md`.
- Access from dev is via an SSH tunnel `localhost:15432 → VPS:5432` (started inside the Podman
  machine). Canonical backup: `pg_dump` cron on the VPS (03:15 UTC, 14-day rotation).

## 4. Search

- **Textual:** Postgres FTS (`tsvector` / BM25-style ranking).
- **Semantic:** pgvector HNSW. Embedding model `paraphrase-multilingual-MiniLM-L12-v2`
  (384 dim, in-process `sentence-transformers`).
- **Hybrid:** Reciprocal Rank Fusion over textual + semantic (`src/alejandria/search/hybrid.py`),
  with modes `hybrid`, `cross-ref`, `kg-boost`, `footnote-xref`.
- A Personalized-PageRank module exists (`src/alejandria/knowledge/pagerank.py`,
  `tests/knowledge/test_pagerank.py`) — see `docs/architecture-proposals/ppr-implementation-plan.md`
  for its intended role; not yet the default retrieval path.

## 5. Knowledge graph

- **Model:** 7 corpus entity types (person, place, concept, people, object, period, +
  institutional / conference / structured-metadata types) and **67 typed relation types** across 12
  categories. Confidence tiers: `curated` > `metadata` > `llm_high` > `llm_low` > `ner` > `co_occurrence`.
- **Extraction:** curated bilingual gazetteers (~2,400 terms; 2,175 biblical persons EN/ES) +
  spaCy `sm` NER + deterministic family patterns. Co-occurrence relations were purged (cleanup R7).
- **Known quality issue:** calibrated ~55–80 % noise per entity type (`object` worst). Addressed by
  project **P12** (extractor v2) and work item **WI-3** (hygiene). See `docs/kg-noise-diagnostic.md`,
  `docs/kg-ingestion-refactor.md`.
- Cross-references: ~97,961 bidirectional pairs parsed from scripture footnotes, integrated into RAG.

## 6. RAG pipeline

Four LLM calls per question: (1) query expansion, (2) entity extraction, (3) rerank, (4) answer.
Calls 1–3 use the cheapest tier; call 4 is routed by a heuristic complexity classifier
(fast / balanced / quality). Multi-provider (Anthropic, Gemini, OpenAI, DeepSeek, Ollama) with a
fallback chain. Context is built from fused chunks + entity-profile summaries + graph neighbors.
Reranking is currently an LLM call (P11 replaces it with a cross-encoder).

## 7. Infrastructure

- **Containers: Podman** (`podman-machine-default`). Migration from native Docker Engine completed
  2026-07-04 (`docs/project-memory/project_podman_migration.md`). Compose override:
  `docker/docker-compose.podman.yml`. Management: `scripts/gpu-podman.sh`.
  `docker/docker-compose.gpu.yml` and the native-Docker context are kept for reference only.
- **GPU:** NVIDIA RTX PRO 500 Blackwell (sm_120), 6 GB VRAM, CUDA 12 nightly image
  (`Dockerfile.gpu`, built 2026-05-23).
- Two containers: `alejandria-api`, `alejandria-ollama`.
- Dev machine: 32 GB RAM; memory pressure is the primary local constraint (`docs/performance.md`).

## 8. Interfaces

- **REST API** (FastAPI, :4300) — primary.
- **MCP server** (`src/alejandria/mcp_server.py`, `.mcp.json`) — `mcp__alejandria__*` tools:
  `kg_relations`, `kg_profile`, `kg_find`, `kg_neighbors`, `kg_docs`, `kg_summary`, `search_hybrid`,
  `search_text`, `chat_ask`, `chat_classify`, `corpus_status`.
- **CLI** (Click) — `alejandria` / `alejandria-mcp` entry points.

## 9. What is NOT part of the system (common misconceptions)

| Not present | Note |
|---|---|
| Neo4j | Retired. Docstrings that say "same shape as `Neo4jClient`" are historical parity notes. |
| Qdrant | Retired; pgvector. |
| SQLite / `sqlite-vec` FTS | Retired; Postgres `tsvector`. |
| Native Docker Engine as the runtime | Podman. `docker` on this host points at Rancher Desktop and must not be used from this repo. |
| 4-package workspace split | Abandoned experiment (`workspace-migration` branch). |
| Microservices / 10-repo split | A **proposal**, not built. See `docs/planning-index.md`. |

## 10. Derived docs (keep in sync with this file)

`architecture.md`, `stack.md`, `configuration.md`, `search-textual.md`, `search-semantic.md`,
`search-hybrid.md`, `knowledge-graph.md`, `entity-extraction.md`, `entity-profiles.md`,
`rag-pipeline.md`, `llm-models.md`, `api-reference.md`, `cli.md`, `mcp-server.md`, `docker.md`,
`operations.md`, `performance.md`, `backup.md`, `corpus.md`, `ingestion.md`, `scripture-references.md`.

> As of 2026-09-09 several of these still describe Neo4j / Qdrant / SQLite / two Docker engines.
> Reconciling them to this spec is project **P0** (`proj/P0-postgres-cutover/`).
