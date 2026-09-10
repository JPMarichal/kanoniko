# P12 — KG Extraction v2 — Project Plan

Maps to **Fase C** of [improvement-program-2026.md](../../docs/improvement-program-2026.md).
No hard dependency (Postgres store already single & stable — A0). P0's doc-sync ideally lands
first. Can overlap **P11**. Feeds **WI-3** (Fase D) and **P13**.

## Phases

### Phase 1 — Global filter fix + measurement baseline
**Scope:** FR-1, FR-6 (baseline).
**Deliverables:**
- Global alias-lookup filter in `extractor.py` + `ner_candidates.record()`; LRU cache.
- Tests: EN/ES variant that currently leaks (`Jesucristo` vs `Cristo` chunk) no longer creates a candidate.
- Baseline noise numbers per type on the n=300 gold, recorded in `benchmarks/kg-extraction-v2/BASELINE.md`.
**Exit:** the current top-15 `ner_candidates` (gazetteer duplicates) stop being generated.
**Est.:** 2–3 días.

### Phase 2 — GLiNER/GLiREL integration (offline eval)
**Scope:** FR-2 (eval only).
**Deliverables:**
- `knowledge/extractor_gliner.py` — schema (7 entity types + 67 relation types) → GLiNER2/GLiREL calls.
- Batch runner over a fixed 5–10k-chunk sample; output compared to gold + to the spaCy path.
- `03-model-choice.md`: GLiNER2 vs GLiREL vs GLiNER-Relex, precision/recall/latency on the sample.
**Exit:** chosen model beats spaCy `sm` on entity precision and produces non-trivial typed relations.
**Est.:** 1–1.5 semanas.

### Phase 3 — Pipeline wiring + type-validation gate
**Scope:** FR-3, FR-5.
**Deliverables:**
- Phase 3 of `ingestion/pipeline.py` runs: gazetteer pass → GLiNER pass (GPU batch) → `is_garbage()`
  + type-validation gate → write. Config flag `KG_EXTRACTOR=gliner|spacy`.
- Chunk-hash cache for extraction results.
- Type-validation rules (scripture-ref regex, numeric-phrase reject, place lookup).
**Exit:** targeted ingest of a subset writes typed relations at `ner` confidence; Phase 3 runs on GPU.
**Est.:** 1–1.5 semanas.

### Phase 4 — LLM batch for the hard subset
**Scope:** FR-4.
**Deliverables:**
- `knowledge/extractor_llm_batch.py` — schema-bound prompt, Anthropic Batch API, prompt caching of
  the schema block. Input: top-K entities by `mention_count` + chapters flagged ambiguous/narrative.
- Emits `llm_high` relations with `source_ref`.
**Exit:** hard-subset relations populated; cost within the batched estimate.
**Est.:** 3–5 días.

### Phase 5 — Validation + cutover
**Scope:** FR-6.
**Deliverables:**
- Partial re-ingest; noise measured per type vs gold (target < 15 %).
- `KG_EXTRACTOR` default flipped to `gliner`; spaCy path kept one release as fallback.
- Docs updated: `entity-extraction.md`, `knowledge-graph.md`; note in `kg-ingestion-refactor.md`.
**Exit:** program **Gate C**.
**Est.:** 3–5 días.

## Milestones

| Milestone | Deliverable | Status |
|-----------|-------------|--------|
| M1 | Global filter fix; baseline noise recorded | ☐ |
| M2 | GLiNER/GLiREL model chosen (beats spaCy on eval) | ☐ |
| M3 | Extractor wired into Phase 3 on GPU; type gate live | ☐ |
| M4 | LLM batch populates the hard subset | ☐ |
| M5 | Noise < 15 %/type; default = `gliner` (**Gate C**) | ☐ |

## Dependencies

- **Inbound:** none blocking. Single Postgres store + ported write path already in place (A0).
- **Outbound:** WI-3 (Fase D) must run *after* M3 so it doesn't re-clean what the old extractor
  re-dirties; P13 genealogies uses this extractor.

## Success Criteria

1. ☐ Typed relations populated for ≥ N of the 67 types (set N at Phase 2).
2. ☐ Noise < 15 % per type on the n=300 gold, `object` included.
3. ☐ Phase 3 ingestion no longer CPU-bound (chunks/min improvement recorded).
4. ☐ `ner_candidates` growth curbed (global filter + retention).
5. ☐ Extractor selectable by config; docs describe the v2 pipeline.
