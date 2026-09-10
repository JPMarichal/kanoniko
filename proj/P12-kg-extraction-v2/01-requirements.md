# P12 — KG Extraction v2 — Requirements

## Problem Statement

The knowledge graph is **rich in schema, poor in real edges**, and noisy:

1. **No real relation extraction.** Co-occurrence relations were killed in R7 (−33M edges). What
   remains auto-generated is minimal; the 1,966 family relations are all deterministic/curated.
   The ontology defines **67 typed relation types across 12 categories** — almost none are populated
   by the pipeline.
2. **Entity noise ~55–80 % by type** (calibrated): `object` ~81 %, `person` ~59 %, `period` ~60 %.
   Root causes: spaCy `sm` propagates wrong labels (`_SPACY_LABEL_MAP` blindly maps `DATE→period`,
   `ORG→people`); a **per-chunk (not global) gazetteer overlap filter** lets EN/ES variants through
   as `ner_candidates` and into the graph; no type validation.
3. **Phase 3 of ingestion is CPU-bound** — spaCy NER runs on every chunk; the GPU sits idle.

The roadmap buries this inside P6 ("move beyond co-occurrence") at Medium priority. Co-occurrence is
already gone; the real task is a new extractor that produces trustworthy typed edges without a
per-chunk LLM cost. This project owns entity + relation extraction. P6 is reframed to Layer 2/3
parallelism and the NER→gazetteer feedback loop.

## Functional Requirements

### FR-1: Global gazetteer filter (bug fix)
In `knowledge/extractor.py`, build `known_names_lower` from the **global alias lookup**
(`_build_alias_lookup`), not from per-chunk matches. Same fix in `ner_candidates.record()`. Add an
LRU-cached module-level lookup. Ref: `kg-ingestion-refactor.md §2 Capa 2`, R1.

### FR-2: Schema-driven extractor (GLiNER2 / GLiREL)
Replace spaCy `sm` NER + co-occurrence with **GLiNER2 / GLiREL** (or GLiNER-Relex for joint NER+RE).
Inference schema = the 7 entity types + the 67 relation types from `knowledge-graph.md`. Runs in
**GPU batch** in Phase 3 of ingestion. Results cached by chunk SHA-256 (incremental re-ingest skips
unchanged chunks).

### FR-3: Gazetteer as precision pass
Keep the curated gazetteer regex as the **first pass** — high precision on canonical biblical
entities. GLiNER runs for entities/relations not covered; its output is filtered against
`gazetteer_lookup.is_garbage()` and type rules.

### FR-4: LLM batch for the hard subset
For top-K entities by `mention_count` and chapters flagged ambiguous/narrative, run a
**schema-bound LLM extraction** via Anthropic Batch API (−50 %) + prompt caching of the
schema/instructions block (−90 %). Emits `llm_high` confidence relations. Not per-chunk — a curated
subset only.

### FR-5: Type-validation gate
Before writing an entity, validate `entity_type` against deterministic rules (scripture-ref regex →
`scripture_reference`, not `person`/`period`; numeric-phrase → reject; European place lookup →
`place`). Wrong-type entities are corrected or rejected, not propagated.

### FR-6: Noise measurement
Re-ingest a validation subset; measure noise against the n=300 gold standard
(`data/kg-diagnostic/manual_labels_300.csv`) per type. Target < 15 % per type, `object` included.

## Non-Functional Requirements

- **Incremental**: chunk-hash cache; unchanged chunks are not re-extracted.
- **GPU-batched**: Phase 3 throughput measured in chunks/min must improve materially vs spaCy CPU.
- **Confidence-tiered**: every emitted relation carries `source_ref` + confidence
  (`ner` for GLiNER, `llm_high` for FR-4, `curated`/`metadata` unchanged).
- **Reversible**: extractor selectable by config during A/B; old spaCy path kept until Gate C.

## Out of Scope

- Cleaning the **existing** noisy KG content (R10 type-correctness sweep, dedup) — that is **WI-3**
  / program Fase D. This project stops new noise; WI-3 removes accumulated noise.
- Genealogy-specific extraction — **P13** (uses this project's extractor + regex for "begat" lists).
- Layer 2/3 parallelism, cross-references — **P6** (reframed).

## Current State

- `knowledge/extractor.py` — `KGExtractor`: gazetteer regex + contextual phrases + cross-language
  + spaCy NER + KJV archaic-verb filter + Pass 4 co-occurrence (now mostly inert post-R7).
- `knowledge/ner_candidates.py` — `NERCandidateTracker` (623K candidates, 0 promotions, 207 MB).
- `knowledge/gazetteers/` — `entities.json` (~2,400 terms) + `bible_persons_bilingual.json` (2,175).
- `knowledge/family_patterns.py` — deterministic `son of`/`hijo de`/`begat`/`wife of` extractor.
- `gazetteer_lookup.is_garbage()` — 8+ garbage reasons (scripture_ref, mojibake, html_fragment, …).
- `ingestion/pipeline.py:1694-1707` — Phase 3 entity/relation write loop.
- Docs: `entity-extraction.md`, `knowledge-graph.md`, `kg-noise-diagnostic.md`,
  `kg-ingestion-refactor.md`.
