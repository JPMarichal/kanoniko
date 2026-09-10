# P11 — Retrieval Modernization — Plan

Maps to **Fase B** of [improvement-program-2026.md](../../docs/improvement-program-2026.md).
No hard dependency (the Postgres store is already single & stable — A0). Nice to have P0's doc-sync
done first so `docs/` is trustworthy. Can overlap **P12** and **Fase F**.

## Phases

### Phase 1 — Eval harness first
**Scope:** FR-6.
**Deliverables:** frozen golden set + RAGAS pipeline; baseline numbers for the current
MiniLM + LLM-rerank stack recorded in `benchmarks/retrieval-modernization/BASELINE.md`.
**Exit:** reproducible `just bench-retrieval` (or script) that prints recall@{5,10,20}, nDCG,
faithfulness, context precision.
**Est.:** 2–3 días.

### Phase 2 — TEI service + model swap
**Scope:** FR-1, FR-2.
**Deliverables:**
- `docker/` compose service `tei` (embeddings), model `BAAI/bge-m3`, cache bind-mounted.
- `core/embeddings/` client points at TEI HTTP; in-process path removed from API.
- pgvector schema migration to 1024 dim (`halfvec` evaluated); HNSW rebuild; re-embed 217K chunks.
- `EMBEDDING_MODEL` + dim config централizados; 384-dim column retained until Phase 5.
**Exit:** semantic search runs on BGE-M3 via TEI; bench recorded (expect recall gain, latency check).
**Est.:** 1 semana.

### Phase 3 — Native hybrid
**Scope:** FR-3.
**Deliverables:** BGE-M3 sparse vector wired into retrieval; decision doc `03-hybrid-decision.md`
(replace vs complement `search/hybrid.py`); RRF kept where it wins.
**Exit:** hybrid bench ≥ current RRF on recall@10 and context precision.
**Est.:** 3–5 días.

### Phase 4 — Cross-encoder reranker
**Scope:** FR-4.
**Deliverables:**
- `tei` reranker service (or second TEI instance), model `BAAI/bge-reranker-v2-m3`.
- `chat/rag.py::_rerank()` replaced by cross-encoder call; `[KG: entity]` boost preserved.
- LLM rerank call removed from the pipeline (4 → 3 LLM calls/question).
**Exit:** rerank precision ≥ LLM-rerank baseline on the eval; one fewer LLM call.
**Est.:** 3–5 días.

### Phase 5 — Contextual Retrieval / Late Chunking
**Scope:** FR-5.
**Deliverables:** pilot on one subcorpus (both approaches); winner applied corpus-wide via Batch
API; `04-chunking-decision.md`.
**Exit:** top-20 retrieval-failure rate down vs Phase 4; cost acceptable (offline, batched).
**Est.:** 1 semana + batch run time.

### Phase 6 — Cutover + cleanup
**Deliverables:** drop the 384-dim column; update `search-semantic.md`, `search-hybrid.md`,
`rag-pipeline.md`, `stack.md`; note the P9 reframe in `roadmap.md`.
**Exit:** program **Gate B**.
**Est.:** 1–2 días.

## Milestones

| Milestone | Deliverable | Status |
|-----------|-------------|--------|
| M1 | Eval harness + baseline recorded | ☐ |
| M2 | BGE-M3 via TEI serving semantic search | ☐ |
| M3 | Native hybrid decision + parity | ☐ |
| M4 | Cross-encoder reranker live; LLM rerank removed | ☐ |
| M5 | Contextual/late chunking applied corpus-wide | ☐ |
| M6 | 384-dim dropped; docs synced (**Gate B**) | ☐ |

## Dependencies

- **Inbound:** none blocking. Single Postgres schema already in place (A0). TEI needs the GPU Docker
  engine (Fase F1 can run in parallel). P0 doc-sync ideally lands first.
- **Outbound:** Fase E (token savings) builds on the reduced call count; P5 (UI) gated on Gate B.

## Acceptance Criteria

1. ☐ recall@10 and faithfulness ≥ baseline + agreed margin; no regression on simple QA.
2. ☐ LLM calls per question: 4 → 3.
3. ☐ p95 `search_semantic` < 500 ms sustained.
4. ☐ Embeddings served by TEI, not in-process.
5. ☐ Docs describe BGE-M3 + cross-encoder + (contextual|late) chunking.
