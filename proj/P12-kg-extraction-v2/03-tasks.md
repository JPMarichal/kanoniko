# P12 — KG Extraction v2 — Tasks

> `[ ]` pending · `[~]` in progress · `[x]` done · `[-]` dropped. Each task names its check.
> Spec: [`01-spec.md`](01-spec.md) · Plan: [`02-plan.md`](02-plan.md).

## Phase 1 — Global filter fix + baseline

- [ ] **T1.1** In `src/alejandria/knowledge/extractor.py`, build `known_names_lower` from the global
      alias lookup, not per-chunk matches. Same in `ner_candidates.record()`. Add an LRU-cached lookup.
      *Check:* new test `tests/knowledge/test_extractor_global_filter.py` — "Jesucristo" vs "Cristo"
      chunk no longer creates an `ner_candidate`.
- [ ] **T1.2** Record baseline noise per entity type against `data/kg-diagnostic/manual_labels_300.csv`.
      *Check:* `benchmarks/kg-extraction-v2/BASELINE.md` has per-type noise %.
- [ ] **T1.3** Verify the current top-15 `ner_candidates` (gazetteer dupes) stop being generated.
      *Check:* re-run ingest on a fixture; assert none of the 15 appear as new candidates.

## Phase 2 — GLiNER/GLiREL integration (offline eval)

- [ ] **T2.1** `src/alejandria/knowledge/extractor_gliner.py` — schema (7 entity types + N of the 67
      relation types; start with the ~15 highest-value, grouped by category). *Check:* module imports; runs on a 10-chunk fixture.
- [ ] **T2.2** Batch-run over a fixed 5–10k-chunk sample; compare to gold + to the spaCy path.
      *Check:* `03-model-choice.md` — precision/recall/latency for GLiNER2 vs GLiREL vs GLiNER-Relex.
- [ ] **T2.3** Decide `N` (how many of the 67 relation types the extractor targets at launch).
      *Check:* `01-spec.md` AC updated with the chosen `N`.

## Phase 3 — Pipeline wiring + type gate

- [ ] **T3.1** Phase 3 of `src/alejandria/ingestion/pipeline.py`: gazetteer pass → GLiNER pass (GPU
      batch) → `is_garbage()` + type-validation gate → write. Config flag `KG_EXTRACTOR=gliner|spacy`.
      *Check:* targeted ingest of a fixture writes typed relations at `ner` confidence with `KG_EXTRACTOR=gliner`.
- [ ] **T3.2** Chunk-hash cache keyed on `hash(chunk_text) + hash(schema_version)`.
      *Check:* re-ingest unchanged fixture → 0 re-extractions; bump `schema_version` → re-extracts.
- [ ] **T3.3** Type-validation rules (scripture-ref regex → `scripture_reference`; numeric-phrase →
      reject; European-place lookup → `place`). *Check:* unit tests per rule in `tests/knowledge/test_type_gate.py`.
- [ ] **T3.4** Measure Phase 3 throughput. *Check:* chunks/min with GLiNER on GPU recorded in `benchmarks/kg-extraction-v2/PHASE3.md`; materially > spaCy CPU baseline.

## Phase 4 — LLM batch for the hard subset

- [ ] **T4.1** `src/alejandria/knowledge/extractor_llm_batch.py` — schema-bound prompt, Anthropic Batch
      API, prompt caching of the schema block. Input: top-K by `mention_count` + chapters flagged
      ambiguous/narrative. *Check:* emits `llm_high` relations with `source_ref` on a fixture; cost within the batched estimate.

## Phase 5 — Validation + cutover

- [ ] **T5.1** Partial re-ingest; measure noise per type vs the n=300 gold.
      *Check:* `benchmarks/kg-extraction-v2/PHASE5.md` — noise < 15 % per type (`object` included).
- [ ] **T5.2** Flip `KG_EXTRACTOR` default to `gliner`; keep spaCy one release as fallback.
      *Check:* `config.py` default is `gliner`; `grep` shows spaCy path still selectable.
- [ ] **T5.3** Update `docs/entity-extraction.md`, `docs/knowledge-graph.md`; note in `docs/kg-ingestion-refactor.md`.
      *Check:* `docs/entity-extraction.md` describes the gazetteer → GLiNER → gate → LLM-batch pipeline.

## Dependency note

WI-3 (KG hygiene mass pass) must run **after** T5.2 — see `04-risks.md` R3.
