# P11 — Retrieval Modernization — Spec

> Format: [`proj/CONVENTIONS.md`](../CONVENTIONS.md). Plan: [`02-plan.md`](02-plan.md) ·
> Tasks: [`03-tasks.md`](03-tasks.md) · Risks: [`04-risks.md`](04-risks.md).
> Reframed from `01-requirements.md` — acceptance criteria live in `02-plan.md` § Acceptance
> Criteria plus the per-task checks in `03-tasks.md`.

## Problem Statement

The retrieval core is dated relative to 2026 practice and is a ceiling on answer quality:

1. **Embedding model:** `paraphrase-multilingual-MiniLM-L12-v2` (384 dim, 2019). ~3 generations
   behind BGE-M3 / Granite-R2 / E5-large. 384 dims under-discriminate on a corpus with heavy
   lexical similarity (scripture verses).
2. **Serving:** embeddings run in-process via `sentence-transformers`, competing with the API for
   Python/GPU and giving poor batch utilization.
3. **Reranking:** done with an LLM call (`chat/rag.py::_rerank()`) — slower, costlier, and lower
   precision than a dedicated cross-encoder.
4. **Hybrid:** a hand-rolled RRF over BM25 + dense (`search/hybrid.py`). Works, but a modern
   dense+sparse model provides this natively.
5. **Chunking:** verse-aware / recursive, with no document-level context enrichment — cross-verse
   and cross-document references get lost.

The roadmap treats retrieval as "done" (struck-through Phases 1–2). It is not; it is unmodernized.
This project owns that gap. It also absorbs the reframed **P9 (Fine-Tuning)**: in 2026 the lever is
a better base model + reranker + contextual retrieval, not fine-tuning a MiniLM.

## Functional Requirements

### FR-1: Embedding service (TEI)
Introduce **HF Text-Embeddings-Inference v1.9** as a container service. Remove in-process
`sentence-transformers` from the API path. Model cache under `D:\myapps\ai-models`. Blackwell
(sm_120) supported natively by TEI ≥ 1.9.

### FR-2: Model upgrade to BGE-M3
Swap the embedding model to **BAAI/bge-m3** (1024 dim, 8192 ctx, MIT). Migrate the pgvector schema
(`vector(1024)` or `halfvec(1024)`), rebuild the HNSW index, re-embed the ~217K existing chunks
(bench estimate ~10 min on the RTX PRO 500). Update `EMBEDDING_MODEL` config and any hardcoded
384-dim assumptions.

### FR-3: Native hybrid
Use BGE-M3's sparse vector alongside its dense vector. Decide whether this **replaces**
`search/hybrid.py` (custom RRF + FTS) or complements it (e.g., keep FTS for exact-phrase, add
sparse for weighted-term). Document the decision and keep RRF fusion where it still wins.

### FR-4: Cross-encoder reranker
Add a multilingual cross-encoder (`BAAI/bge-reranker-v2-m3`, alt: `jina-reranker-v2-base-multilingual`,
`Qwen3-Reranker`) served by TEI. Replace the LLM rerank call in `chat/rag.py`. Keep the
`[KG: entity]` tag signal as a rerank feature/boost.

### FR-5: Contextual Retrieval / Late Chunking
Enrich chunks at index time: either an LLM-generated one-line context prepended before embedding
(Anthropic Batch API + prompt caching), or late chunking (embed the full doc at token level, then
pool per chunk — no LLM). Pilot on one subcorpus; keep whichever wins on the eval.

### FR-6: Evaluation harness
A/B bench on the golden set + RAGAS: recall@k, nDCG, faithfulness, context precision — before and
after each change. Results in `benchmarks/retrieval-modernization/`.

## Non-Functional Requirements

- **No corpus loss**: re-embed is additive; keep the 384-dim column until the 1024-dim path passes eval.
- **VRAM budget**: TEI (embeddings + reranker) must fit alongside the API in ≤ 2 GB VRAM resident.
- **RAM budget**: 1024-dim vectors + HNSW must fit IONOS VPS M, or trigger the VPS-L upgrade path.
- **Latency**: p95 `search_semantic` < 500 ms sustained.

## Out of Scope

- Storage engine work — none needed; Postgres is already the single store (A0). `docs/` should be
  synced by **P0** first.
- KG extraction / relations — that is **P12**.
- Merging the query-path LLM calls — program **Fase E** (E1).
- HippoRAG-2 PPR retrieval — program **Fase E** (E4 spike).

## Current State

- `core/embeddings/` — sentence-transformers wrapper, 384 dim.
- `search/semantic.py` / `search/postgres_semantic.py` — pgvector query with JOIN to chunks.
- `search/hybrid.py` — RRF over BM25 + dense (~90 lines).
- `chat/rag.py::_rerank()` — LLM-based reranking (internal fast tier).
- `docs/search-semantic.md`, `docs/search-hybrid.md`, `docs/rag-pipeline.md`.
- `vector-db-options.md` — pgvector decision + triggers (T2 HNSW build, T3 table size).
