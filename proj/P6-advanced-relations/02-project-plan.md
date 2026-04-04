# P6 — Advanced Relations — Project Plan

## Phases

### Phase 1 — Relation Type Taxonomy ✅ Complete
**Deliverables:**
- ✅ 52 relation types defined across 12 semantic categories
- ✅ `gazetteers/relations.json` with 634 curated relations (40 types populated)
- ✅ Neo4j schema supports typed relations with confidence tiers
- ✅ Pipeline integration: curated relations auto-loaded during `rebuild_kg` and `run`

**Tasks (all complete):**
1. ✅ Define relation types and their semantics — 52 types in 12 categories (family, governance, prophetic, geographic, temporal, authorship, conflict, spiritual, intertextuality, typology, covenants, dispensational)
2. ✅ Create `gazetteers/relations.json` with curated relations — 634 relations including IS_SAME_AS, FOREORDAINED_AS, MARTYRED_AT, EARLIER_VERSION_OF, PRECEDED_BY
3. ✅ Update `Neo4jClient.merge_relation()` to support typed relations — `load_curated_relations()` method + batch merge
4. ✅ Migration path for existing `RELATED_TO` edges — `migrate_untyped_relations()` reclassified ~993K edges to `co_occurrence` confidence
5. ✅ Pipeline integration — `load_curated_relations` called automatically in both `rebuild_kg()` and `run()` (P6 gap fix)
6. ✅ REST endpoint `POST /index/load-curated-relations?migrate=true` for on-demand loading

**Remaining 12 empty types** (CITES, DESCRIBED_IN, PARALLEL_ACCOUNT_OF, OCCURRED_DURING, AUTHORIZED, REVOKED, DISAVOWED, CANONIZED_AS, COVERS, DESIGNATED_AS, DESCRIBED_BY, ADDRESSED_BY) are intentionally deferred — they require automated extraction in Phases 2-3 or metadata enrichment from `.meta.json` files.

### Phase 2 — Parallelism Encoding ✅ Complete (pipeline integration pending)
**Deliverables:**
- ✅ 36 parallel narratives across 3 layers (direct, editorial, thematic)
- ✅ Neo4j: 36 Narrative nodes, 8,000 PARALLEL_TO relations loaded
- ✅ Neo4j query method `get_parallel_passages()` with layer filtering
- ✅ API endpoint `POST /search/graph/parallels`

**Tasks (all complete):**
1. ✅ Convert `cross_references.py` patterns to Neo4j — 36 narratives
2. ✅ Link document nodes — PARALLEL_NARRATIVE, EDITORIAL_PARALLEL, THEMATIC_LINK
3. ✅ API to query parallel passages
4. ⬜ Refactor `load_parallels_neo4j.py` core to `src/` for auto-loading in `rebuild_kg()`

### Phase 3 — LLM Relation Extraction ✅ Complete
**Deliverables:**
- ✅ LLM-powered relation extraction with structured prompts (78 valid types, confidence tiers)
- ✅ Batch processing with tiered model selection, token tracking, dedup, 4-strategy JSON parsing
- ✅ API endpoint `POST /search/graph/extract-relations` (dry_run, tier, volumes, min_entities)
- ✅ CLI script `scripts/extract_relations_llm.py` with cost estimation and sample preview

**Tasks (all complete):**
1. ✅ LLM prompt design — system prompt with rules + user prompt template with entity list and JSON schema
2. ✅ Batch extraction pipeline — `LLMRelationExtractor.extract_batch()` + `build_batches_from_index()` (entity-rich passage selection from FTS)
3. ✅ Neo4j storage — `merge_relation()` with confidence, source, source_ref properties
4. ✅ Validation and deduplication — key-based dedup, invalid type filtering, truncated response recovery

**Note:** Neo4j writes now use `batch_merge_relations()` (UNWIND) for performance.

### Phase 4 — NER Feedback Loop ✅ Complete
**Deliverables:**
- ✅ SQLite table `ner_candidates` with frequency tracking, status, sample files
- ✅ API endpoints: `GET /search/graph/ner-candidates`, `POST .../promote`, `POST .../dismiss`
- ✅ Promotion writes directly to `entities.json` gazetteer (closed loop)

**Tasks (all complete):**
1. ✅ Track NER-discovered entities with frequency counts — `ner_candidates.py` (208 lines)
2. ✅ Surface candidates above threshold — API with frequency/type/status filters
3. ✅ Promotion workflow — one-click promote to gazetteer + dismiss; dedup check on promotion

### Phase 5 — Entity Attributes and Titles (~35% complete)
**Deliverables:**
- ✅ `HAS_TITLE` with 54 curated relations in `relations.json` (loaded to Neo4j)
- ✅ `HAS_TITLE` in LLM `VALID_RELATION_TYPES` — extractable by F3 pipeline
- ✅ Neighbor queries surface HAS_TITLE alongside other relation types
- ⬜ `HAS_ROLE`, `CALLED_BY_NAME` types (not defined, no data)
- ⬜ Dedicated `entity_attributes.json` seed file
- ⬜ LLM prompt optimized for attribute extraction

**Tasks:**
1. ✅ HAS_TITLE defined with properties and 54 curated relations
2. ⬜ Define `HAS_ROLE` and `CALLED_BY_NAME`; add to `VALID_RELATION_TYPES`
3. ⬜ Create `gazetteers/entity_attributes.json` with roles (Paul→Apostle, Moses→Prophet, David→King)
4. ⬜ Design dedicated LLM prompt for attribute extraction
5. ⬜ Batch-extract attributes for top entities (by mention count)
6. ✅ Neighbor queries already return HAS_TITLE alongside other types

**Extraction sources for AUTHORED relations (from Phase 1):**
- **DyC:** `summary` field in `.meta.json` — reliable, includes receiver and historical context
- **Salmos:** superscriptions + curated seed file for gaps (Asaf 73-83, hijos de Coré 42-49, Hemán 88, Etán 89)
- **Libro de Mormón:** Text transitions ("Yo, Amalekí...", "Yo, Moroni...") — text-level extraction
- **Dependency:** P2 DEF-1 blocks complete Psalm authorship; curated seed covers known attributions

### Phase 6 — Scripture Hierarchy ✅ Complete (pipeline integration pending)
**Deliverables:**
- ✅ Full data model: `Volume`, `Division`, `Book`, `Part`, `Chapter`, `Pericope` dataclasses
- ✅ JSON data files: `volumes.json`, `divisions.json`, `books.json`, `parts.json`, `chapters.json`, `pericopae.json`
- ✅ `scripture_structure.py` (490 lines) with long-chain resolution
- ✅ Neo4j loaded: 5 volumes, 19 divisions, 88 books, 389 parts, 1,584 chapters
- ✅ 2,080 CONTAINS + 1,493 NEXT/PREVIOUS relations
- ✅ 1,900 Chapter nodes with .meta.json properties (study_intro, section_headings, subtitle)

**Tasks (all complete):**
1. ✅ Node types: Volume, Division, Book, Part, Chapter
2. ✅ Curated seed files for all volumes
3. ✅ Hierarchy loaded with CONTAINS relations
4. ✅ `.meta.json` properties on Chapter nodes (bilingual)
5. ✅ NEXT/PREVIOUS sequential navigation
6. ✅ Executed against Neo4j — confirmed 2026-04-04
7. ⬜ Refactor `load_hierarchy_neo4j.py` core to `src/` for auto-loading in `rebuild_kg()`

### Phase 7 — Metadata-Derived Relations ✅ Complete (CHAPTER_TEACHES + pipeline integration pending)
**Deliverables:**
- ✅ 549 metadata relations extracted and loaded to Neo4j:
  - REVEALED_TO: 192 (D&C → person)
  - REVEALED_AT: 118 (D&C → place)
  - REVEALED_ON: 134 (D&C → date)
  - AUTHORED: 97 (Psalms → David, Asaph, Sons of Korah, etc.)
  - WRITTEN_DURING: 8 (PGP → period)
- ✅ Validated: "¿Cuándo fue revelada DyC 76?" → Feb 16, 1832, Hiram Ohio, José Smith + Sidney Rigdon
- ✅ Validated: "¿Qué salmos escribió Asaf?" → Salmos 50, 73-83

**Tasks:**
1. ✅ Parse D&C `study_intro` (140 sections × 2 langs) — 444 relations
2. ✅ Extract `AUTHORED` from Psalm `section_headings` — 97 relations
3. ✅ Extract `WRITTEN_DURING` from PGP `subtitle` — 8 relations
4. ⬜ Design `CHAPTER_TEACHES` extraction from `summary` fields (1,587 summaries)
5. ✅ Executed against Neo4j — confirmed 2026-04-04
6. ✅ Validated with plan success criteria
7. ⬜ Refactor core to `src/` for auto-loading in `rebuild_kg()`

### Phase 8 — Citations and Intertextuality (~45% complete)
**Deliverables:**
- ✅ Curated seed relations: QUOTES (26), ALLUDES_TO (6), JST_OF (6) in `relations.json`
- ✅ `scripts/expand_curated_relations.py` (406 lines): structured seed data for Phases 8-13
- ✅ Cross-references parsed: `data/scripture_structure/cross_references.json` (28MB, 980K lines)
- ✅ Loading script `scripts/load_cross_refs_neo4j.py` for ScriptureVerse + CROSS_REF relations
- ✅ LLM extraction framework includes QUOTES, ALLUDES_TO in `VALID_RELATION_TYPES`
- ⬜ LLM execution for allusion/paraphrase detection
- ⬜ Execution confirmation for cross-ref loading

**Tasks:**
1. ✅ Curated seed file for OT→NT, OT→BofM, intra-BofM quotations
2. ⬜ LLM extraction (Sonnet tier): allusions and paraphrases in prophetic/epistolary passages
3. ✅ JST variants cataloged with `change_type` (expansion, revision, correction, clarification)
4. ⬜ Execute cross-ref loading and curated seed loading against production Neo4j
5. ⬜ Validate: "¿Dónde cita Pablo a Isaías?" returns structured results

### Phase 9 — Typology, Symbolism, and Prophecy (seed data exists)
**Seed data in `relations.json`:** TYPE_OF (14), SYMBOLIZES (17), PROPHECY_OF (16)
**Missing types:** ANTITYPE_OF, DUAL_FULFILLMENT (0 each)

**Tasks:**
1. ✅ (partial) Major typological pairs curated — 14 TYPE_OF relations
2. ✅ (partial) Major symbols curated — 17 SYMBOLIZES relations
3. ✅ (partial) Prophecies cataloged — 16 PROPHECY_OF relations
4. ⬜ LLM extraction (Sonnet): Isaiah, Daniel, Revelation, 1-2 Nephi
5. ⬜ Define ANTITYPE_OF, DUAL_FULFILLMENT; flag dual fulfillments for Opus review

### Phase 10 — Covenants, Priesthood, and Ordinances (seed data exists)
**Seed data in `relations.json`:** COVENANT_WITH (10), HOLDS_PRIESTHOOD (10), CONFERRED_KEYS_TO (8), ORDAINED_BY (5), BAPTIZED_BY (5)
**Missing types:** RENEWED_BY, KEYBEARER_OF (0 each)

**Tasks:**
1. ✅ (partial) Covenant chain curated — 10 COVENANT_WITH relations
2. ✅ (partial) Priesthood events — CONFERRED_KEYS_TO (8), HOLDS_PRIESTHOOD (10)
3. ⬜ Curate key bearers: Peter (kingdom), Elijah (sealing), Moses (gathering), Elias (Abraham)
4. ⬜ Extract `BAPTIZED_BY`, `ORDAINED_BY` from BofM and NT narratives (Haiku tier)
5. ⬜ Validate: "¿Quién restauró el sacerdocio aarónico?" → John the Baptist, D&C 13

### Phase 11 — Extended Relations (seed data exists)
**Seed data in `relations.json`:** SAW_IN_VISION (16), DESCENDANT_OF (11), TRIBE_OF (8), CONVERTED_BY (9), CONQUERED (7)
**Missing types:** LINEAGE_OF, CAPTIVE_OF, REBELLED_AGAINST, ALLIED_WITH, SPOKE_TO, DISCOURSE_ABOUT, ADDRESSED_TO, PERFORMED, WITNESSED, FELL_AWAY, APPEARED_TO (0 each)

**Tasks:**
1. ⬜ Curate patriarchal genealogy: Adam→...→Noah→...→Abraham→...→David→...→Christ
2. ✅ (partial) Tribal assignments — 8 TRIBE_OF relations
3. ⬜ Extract military/political from BofM war chapters + OT conquest (Haiku tier)
4. ⬜ Extract conversion narratives from Acts, BofM (Haiku tier)
5. ✅ (partial) Major visions — 16 SAW_IN_VISION relations
6. ⬜ Define missing types and validate

### Phase 12 — LDS Dispensational Theology (seed data exists)
**Seed data in `relations.json`:** DISPENSATION_HEAD (7), RESTORED (7), RECORD_KEPT_BY (11), ABRIDGED_BY (7)
**Missing types:** APOSTASY_IN, DISPENSATION_OF, STAGE_OF, DEGREE_OF_GLORY, PREFIGURED_BY, TEMPLE_AT, ORDINANCE_FOR_DEAD, WITNESS_OF, COLOPHON_IN, COUNCIL_PARTICIPANT, FACSIMILE_DEPICTS (0 each)

**Tasks:**
1. ✅ (partial) Dispensation heads curated — 7 relations
2. ✅ (partial) Restoration events — 7 RESTORED relations
3. ⬜ Model Plan of Salvation stages with teaching passages
4. ✅ (partial) BofM record-keeping chain — RECORD_KEPT_BY (11), ABRIDGED_BY (7)
5. ⬜ Catalog facsimile interpretations from Abraham
6. ⬜ Validate: "¿Qué restauró José Smith?" returns structured chain

### Phase 13 — Literary and Linguistic Analysis (seed data exists)
**Seed data in `relations.json`:** GENRE_OF (32), CHIASM_IN (6)
**Missing types:** INCLUSIO_IN, PARALLELISM_IN, ACROSTIC_IN, TRANSLATES_AS, WORD_STUDY, EDITORIAL_NOTE, VARIANT_OF, POSSIBLE_SOURCE (0 each)

**Tasks:**
1. ✅ (partial) Known chiasms — 6 CHIASM_IN relations
2. ✅ (partial) Genre assignments — 32 GENRE_OF relations
3. ⬜ Hebrew/Greek terms with TRANSLATES_AS (hesed, berith, logos, agape, etc.)
4. ⬜ Mormon's editorial insertions as EDITORIAL_NOTE
5. ⬜ POSSIBLE_SOURCE for Isaiah/BofM parallels, synoptic dependencies
6. ⬜ LLM extraction (Sonnet): literary patterns in poetic books

### Phase 14 — Quality Framework and Performance (ongoing, ~15% — confidence tracking only)
**Deliverables:**
- ✅ Confidence tiers on all relations (curated, metadata, llm_high, llm_low, ner, co_occurrence)
- ✅ Confidence filtering in `neo4j_client.py` neighbor queries
- ⬜ Two-pass extraction (Haiku → Sonnet/Opus verify)
- ⬜ Human review queue for low-confidence / theologically sensitive
- ⬜ Materialized paths for ancestor chains, covenant chains, dispensation sequences
- ⬜ Bilingual deduplication (merge EN/ES extractions for same entity pairs)

**Tasks:**
1. Add `confidence`, `source`, `source_ref`, `verified` properties to all relation types
2. Implement two-pass extraction: Haiku extracts candidates → Sonnet/Opus verifies ambiguous
3. Build batch prompt templates with compressed JSON output schema
4. Create Neo4j composite indexes: `(node_type, name)`, `(relation_type, confidence)`, `(source_ref)`
5. Implement materialized paths for ancestor chains, covenant chains, dispensation sequences
6. Implement bilingual deduplication: merge EN/ES extractions for same entity pairs
7. Build human review queue surfacing `llm_low` confidence relations on sensitive topics
8. Incremental extraction: integrate with SHA-256 change detection from ingestion pipeline

## Milestones

| Milestone | Deliverable | Estimate |
|-----------|------------|----------|
| M1 | ✅ Typed relations working, curated data loaded | Day 2 |
| M2 | ✅ Parallelism encoded in graph (36 narratives, 8K relations) | Day 5 |
| M3 | ✅ LLM extraction producing typed relations | Day 10 |
| M4 | ✅ NER feedback loop operational | Day 12 |
| M5 | Entity attributes loaded, surfaced in neighbor queries (~35%) | Day 15 |
| M6 | ✅ Canon hierarchy navigable in graph, metadata on Chapter nodes | Day 18 |
| M7 | ✅ Metadata-derived relations (D&C, Psalms, PGP) — 549 relations | Day 21 |
| M8 | Citations and intertextuality (quotes, allusions, JST) | Day 25 |
| M9 | Typology, symbolism, and prophecy catalog | Day 29 |
| M10 | Covenants, priesthood, and ordinances modeled | Day 32 |
| M11 | Extended relations (genealogy, military, discourse, visions) | Day 36 |
| M12 | LDS dispensational theology complete | Day 39 |
| M13 | Literary and linguistic analysis operational | Day 43 |
| M14 | Quality framework, performance optimization, review queue | Day 46 |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM relation extraction noisy | High | Start with curated data; LLM supplements, doesn't replace. Precision-first: false relations worse than missing ones |
| Relation type proliferation | Medium | Keep taxonomy small; prefer fewer accurate types. Each type must justify its existence with a concrete query it enables |
| Graph query performance with many relation types | Low | Neo4j handles heterogeneous relations well; composite indexes on `(node_type, name)`, `(relation_type, confidence)`, `(source_ref)` |
| Theological precision in LDS-specific extractions | High | Curated seed files for sensitive topics (dispensations, priesthood, covenants). Opus-tier review for dual fulfillments and typological claims. Human review queue for `llm_low` confidence on theological content |
| Token cost across 14 phases | Medium | Tiered model strategy (regex→Haiku→Sonnet→Opus). Compressed JSON output schema. Pericope-level batching. Incremental extraction via SHA-256 change detection |
| Curated data quality and completeness | Medium | Cross-reference multiple scholarly sources. Bilingual deduplication. Source_ref required for every non-co-occurrence relation |
| Typological/symbolic classification subjectivity | Medium | Flag ambiguous cases for Opus review. Dual fulfillment requires explicit human confirmation. Confidence tracking on all relations |
| Bilingual consistency (EN/ES entity merging) | Medium | Bilingual deduplication pass after extraction. Gazetteer provides canonical names across languages |
| Stale extractions after corpus updates | Low | SHA-256 change detection triggers re-extraction. Incremental pipeline reprocesses only changed chapters |

## Dependencies

- P1 (Scripture Structure) improves context for extraction
- P2 DEF-1 (metadata completeness) — section headings/superscriptions needed for Psalm authorship and D&C study_intro parsing
- Gazetteer completeness — LLM extraction quality depends on entity resolution against gazetteers

## Success Criteria

**Core (Phases 1–5):**
1. "Who is the father of Isaac?" answered from graph relation, not just text search
2. Parallel passages discoverable via graph traversal
3. Top 50 NER candidates reviewable via API
4. "Is Paul called an apostle in Acts?" answerable from graph — neighbor query for Paul returns `HAS_TITLE → Apostle` with source refs from Acts 14:4 and 14:14

**Hierarchy & Metadata (Phases 6–7):**
5. Canon hierarchy navigable: "¿Cuáles son las epístolas paulinas?" answered by traversing Division→Book
6. "¿Cuándo fue revelada DyC 76?" answered from `REVEALED_ON` relation parsed from study_intro
7. "¿Qué salmos escribió Asaf?" answered from `AUTHORED` relations parsed from superscriptions
8. Sequential navigation: NEXT/PREVIOUS between chapters within each book

**Citations & Intertextuality (Phase 8):**
9. "¿Dónde cita Pablo a Isaías?" returns structured `QUOTES` relations with source and target refs
10. Isaiah chapters in 2 Nephi linked via `QUOTES` to their OT counterparts
11. JST variants cataloged and linked to KJV counterparts via `JST_OF`

**Typology & Symbolism (Phase 9):**
12. "¿Qué prefigura el cordero pascual?" returns `TYPE_OF → Crucifixion` with source refs
13. Major symbols (olive tree, bread, water, vine) queryable with all associated passages
14. Dual fulfillment prophecies flagged and navigable

**Covenants & Priesthood (Phase 10):**
15. "¿Quién restauró el sacerdocio aarónico?" → John the Baptist, source D&C 13
16. Covenant chain navigable: Abrahamic → renewed through Isaac → Jacob → ... → Christ → Joseph Smith
17. Key bearers queryable: "¿Qué llaves restauró Elías?" → sealing power, D&C 110

**Extended Relations (Phase 11):**
18. Patriarchal genealogy traversable from Adam to Christ (Matthew 1, Luke 3, 1 Chronicles)
19. BofM war chapters (Alma 43-63) yield military/political relations
20. Conversion narratives discoverable: "¿Quién convirtió a Alma?" → Abinadi (indirectly), sons of Mosiah

**LDS Dispensational (Phase 12):**
21. "¿Qué restauró José Smith?" returns structured dispensation chain with keys and source refs
22. BofM record-keeping chain navigable: who kept which plates, who abridged what
23. Plan of Salvation stages with associated teaching passages

**Literary & Linguistic (Phase 13):**
24. Chiastic structures identified: Alma 36 confirmed, Mosiah 3:18-19, Leviticus 24
25. Genre assigned to every book; queryable: "¿Qué libros son poéticos?"
26. Key Hebrew/Greek terms with semantic ranges and passage links (hesed, berith, logos, agape)

**Quality & Performance (Phase 14):**
27. Every relation has `confidence`, `source`, `source_ref`, `verified` properties
28. Two-pass extraction operational: Haiku extracts → Sonnet/Opus verifies ambiguous
29. Human review queue surfaces low-confidence relations on theologically sensitive topics
30. Bilingual deduplication merges EN/ES extractions for same entity pairs
