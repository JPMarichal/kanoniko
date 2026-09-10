# P11 — Retrieval Modernization — Tasks

> `[ ]` pending · `[~]` in progress · `[x]` done · `[-]` dropped. Each task names its check.
> Spec: [`01-spec.md`](01-spec.md) · Plan: [`02-plan.md`](02-plan.md).
> Overlaps work already in `main`: `src/alejandria/knowledge/pagerank.py`,
> `docs/architecture-proposals/ppr-implementation-plan.md`, `graph-enhanced-rag-evaluation.md` —
> reconcile before starting (see T0.1).

## Phase 0 — Reconcile with in-flight work

- [ ] **T0.1** Read `docs/architecture-proposals/{ppr-implementation-plan,graph-enhanced-rag-evaluation}.md`
      + `ppr-baseline-metrics.json` + `src/alejandria/knowledge/pagerank.py` + `tests/knowledge/test_pagerank.py`.
      Decide: does PPR/graph-RAG evaluation live here (P11 E4) or stay its own track? Record in `02-plan.md`.
      *Check:* `02-plan.md` has a "Reconciliation" note with the decision.

## Phase 1 — Eval harness first

- [ ] **T1.1** Freeze a golden set + RAGAS pipeline (reuse `tests/parity/golden_queries.yaml` where
      applicable). *Check:* `benchmarks/retrieval-modernization/BASELINE.md` has recall@{5,10,20}, nDCG,
      faithfulness, context-precision for the current MiniLM + LLM-rerank stack.
- [ ] **T1.2** `just bench-retrieval` (or script) reproduces the baseline. *Check:* command exits 0 and prints the table.

## Phase 2 — TEI service + model swap

- [ ] **T2.1** Add `tei` service to `docker/docker-compose.podman.yml` (Podman is the engine — migration
      done 2026-07). Model `BAAI/bge-m3`, cache bind-mounted. *Check:* `curl` the TEI `/embed` endpoint returns a 1024-vec.
- [ ] **T2.2** Point `src/alejandria/embeddings/` at TEI HTTP; remove in-process `sentence-transformers`
      from the request path. *Check:* API `/health` shows embeddings `ok`; no `sentence_transformers` import in the request path (`grep`).
- [ ] **T2.3** pgvector schema migration to 1024 dim (`halfvec` evaluated); HNSW rebuild; re-embed
      ~217K chunks. *Check:* `SELECT vector_dims(embedding) FROM chunk_embeddings LIMIT 1;` → 1024; row count unchanged.
- [ ] **T2.4** Bench vs baseline. *Check:* `benchmarks/retrieval-modernization/PHASE2.md` recorded; recall not worse.

## Phase 3 — Native hybrid

- [ ] **T3.1** Wire BGE-M3 sparse vector into retrieval. *Check:* `03-hybrid-decision.md` records replace-vs-complement.
- [ ] **T3.2** Bench hybrid. *Check:* recall@10 and context-precision ≥ current RRF, per-query-type (factual / enumeration / exact-cite / multi-entity).

## Phase 4 — Cross-encoder reranker

- [ ] **T4.1** Add reranker service (`BAAI/bge-reranker-v2-m3`) to compose. *Check:* `/rerank` endpoint returns scores.
- [ ] **T4.2** Replace `chat/rag.py::_rerank()` LLM call with the cross-encoder; keep `[KG: entity]` boost.
      *Check:* pipeline makes 3 LLM calls/question (was 4) — assert in a test or log check.
- [ ] **T4.3** Bench rerank precision. *Check:* `PHASE4.md` — precision ≥ LLM-rerank baseline.

## Phase 5 — Contextual Retrieval / Late Chunking

- [ ] **T5.1** Pilot both on one subcorpus. *Check:* `04-chunking-decision.md` with the winner + numbers.
- [ ] **T5.2** Apply winner corpus-wide (Batch API + prompt caching if LLM variant). *Check:* top-20 failure rate down vs Phase 4 in RAGAS.

## Phase 6 — Cutover + cleanup

- [ ] **T6.1** Drop the 384-dim column; update `docs/search-semantic.md`, `search-hybrid.md`,
      `rag-pipeline.md`, `stack.md`. *Check:* `grep -n "384" docs/search-*.md` → only historical notes.
- [ ] **T6.2** Note the P9 (fine-tuning) reframe in `docs/roadmap.md`. *Check:* roadmap P9 says "absorbed by P11".
