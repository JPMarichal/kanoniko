# P6 — Advanced Relations — Project Plan

## Phases

### Phase 1 — Relation Type Taxonomy (1-2 days)
**Deliverables:**
- Defined relation type hierarchy
- Gazetteer-style data file with known relations (e.g., family trees)
- Neo4j schema update for typed relations

**Tasks:**
1. Define relation types and their semantics
2. Create `gazetteers/relations.json` with curated relations (patriarchal lineages, apostolic callings, etc.)
3. Update `Neo4jClient.merge_relation()` to support typed relations
4. Migration path for existing `RELATED_TO` edges

### Phase 2 — Parallelism Encoding (2-3 days)
**Deliverables:**
- Cross-reference parallels encoded as graph relations
- New relation types: `PARALLEL_NARRATIVE`, `EDITORIAL_PARALLEL`, `THEMATIC_LINK`
- Data from existing `cross_references.py` migrated to graph

**Tasks:**
1. Convert `cross_references.py` patterns to Neo4j relations
2. Link document nodes with parallelism type
3. API to query parallel passages for a given reference

### Phase 3 — LLM Relation Extraction (3-5 days)
**Deliverables:**
- LLM-powered relation extraction from key passages
- Batch processing similar to profile generation
- New API endpoint for relation extraction

**Tasks:**
1. Design LLM prompt for relation extraction (input: passage + entities, output: typed relations)
2. Implement batch extraction pipeline
3. Store extracted relations in Neo4j
4. Validation and deduplication

### Phase 4 — NER Feedback Loop (2 days)
**Deliverables:**
- NER candidate tracking table in SQLite
- API to list top NER candidates
- CLI/API to promote candidates to gazetteer

**Tasks:**
1. Track NER-discovered entities with frequency counts
2. Surface candidates above threshold
3. Promotion workflow: add to gazetteer, trigger re-extraction

### Phase 5 — Entity Attributes and Titles (2-3 days)
**Deliverables:**
- `HAS_TITLE`, `HAS_ROLE`, `CALLED_BY_NAME` relations in Neo4j
- Curated seed data for key entities (apostles, prophets, kings)
- LLM extraction prompt for titles/roles from passages
- Neighbor queries automatically surface titles alongside other relations

**Tasks:**
1. Define relation types `HAS_TITLE`, `HAS_ROLE`, `CALLED_BY_NAME` with properties (`source_ref`, `attributed_by`, `context`)
2. Create curated seed file `gazetteers/entity_attributes.json` with high-confidence titles (Paul→Apostle, Moses→Prophet, David→King, etc.) and their source references
3. Load seed data into Neo4j
4. Design LLM prompt for attribute extraction (input: passage + entity, output: titles/roles with attribution)
5. Batch-extract attributes for top entities (by mention count)
6. Verify that `GET /search/graph/neighbors` returns title/role relations alongside existing relation types

**Extraction sources for AUTHORED relations (Phase 1):**
- **DyC:** `summary` field in `.meta.json` — reliable, includes receiver and historical context (e.g., "Revelación dada a José Smith...")
- **Salmos:** `summary` field + superscriptions (once P2 DEF-1 is fixed) + curated seed file for gaps (Asaf 73-83, hijos de Coré 42-49, Hemán 88, Etán 89)
- **Libro de Mormón:** Explicit text transitions within chapters (e.g., "Yo, Amalekí..." in Omni, "Yo, Moroni..." in Mormón 8) — requires text-level extraction, not just metadata
- **Dependency:** P2 DEF-1 (missing section headings/superscriptions) blocks complete Psalm authorship; curated seed file covers known attributions until then

### Phase 6 — Scripture Hierarchy (2-3 days)
**Deliverables:**
- Canon structure modeled as graph: Volume, Division, Book, Part, Chapter, Pericope, Verse
- Both short chain (Volume→Book→Chapter→Verse) and long chain (Volume→Division→Book→Part→Chapter→Pericope→Verse)
- `CONTAINS`/`PART_OF` relations, `NEXT`/`PREVIOUS` for sequential navigation
- `.meta.json` properties loaded onto Chapter nodes: `source_url`, `summary`, `study_intro`, `subtitle`, `section_headings`

**Tasks:**
1. Define node types and hierarchy schema in Neo4j (Volume, Division, Book, Part, Chapter, Pericope)
2. Create curated seed file for Divisions (Pentateuch, Poetry & Wisdom, Gospels, Pauline Epistles, Small Plates, Large Plates, etc.) and Parts (Psalms Books I–V, Record of Zeniff, Words of Alma, etc.)
3. Load hierarchy from `chapters.json` + seed file — create nodes, `CONTAINS`/`PART_OF` relations
4. Load `.meta.json` properties onto Chapter nodes (`source_url`, `summary`, `study_intro`, `subtitle`, `section_headings`) for both EN and ES
5. Create `NEXT`/`PREVIOUS` relations between chapters within each book
6. Link existing `ScriptureVerse` nodes to their Chapter nodes via `PART_OF`

### Phase 7 — Metadata-Derived Relations (2-3 days)
**Deliverables:**
- D&C `study_intro` parsed into `REVEALED_TO`, `REVEALED_AT`, `REVEALED_ON`, `OCCASIONED_BY` relations
- Chapter summaries feeding `CHAPTER_TEACHES` concept relations
- Psalm superscriptions feeding `AUTHORED` relations
- PGP/BofM subtitles feeding `WRITTEN_DURING` temporal relations

**Tasks:**
1. Parse D&C `study_intro` (140 sections × 2 langs) with regex patterns for person, place, date, occasion — fallback to LLM for ambiguous cases
2. Extract `AUTHORED` from Psalm `section_headings` (116 EN, 118 ES) — map author names to gazetteer entities
3. Extract `WRITTEN_DURING` from PGP `subtitle` dates (13 chapters)
4. Design `CHAPTER_TEACHES` extraction from `summary` fields — NER + concept matching over 1,587 summaries
5. Load all extracted relations into Neo4j
6. Validate: "¿Cuándo fue revelada DyC 76?" answerable from graph; "¿Qué salmos escribió Asaf?" from `AUTHORED`

### Phase 8 — Citations and Intertextuality (3-4 days)
**Deliverables:**
- `QUOTES`, `ALLUDES_TO`, `JST_OF` relations in Neo4j
- Curated seed file for high-confidence quotations (Jesus quoting OT, Nephi quoting Isaiah, Paul quoting OT)
- LLM extraction for allusions and paraphrases
- JST variant catalog linked to KJV counterparts

**Tasks:**
1. Create curated seed file for known OT→NT quotes (from cross-references), OT→BofM quotes (Isaiah in 2 Nephi), and intra-BofM quotes
2. LLM extraction (Sonnet tier): identify allusions and paraphrases in key prophetic and epistolary passages
3. Catalog JST changes from LDS scripture appendix — store as `JST_OF` relations with `change_type`
4. Load into Neo4j with `verbatim` flag and source/target refs
5. Validate: "¿Dónde cita Pablo a Isaías?" returns structured results

### Phase 9 — Typology, Symbolism, and Prophecy (3-4 days)
**Deliverables:**
- `TYPE_OF`, `ANTITYPE_OF`, `SYMBOLIZES`, `PROPHECY_OF`, `DUAL_FULFILLMENT` relations
- Curated seed file for major types and symbols
- LLM extraction (Sonnet tier) for typological reasoning

**Tasks:**
1. Curate major typological pairs: Melchizedek→Christ, Isaac→Atonement, Passover→Crucifixion, serpent→Crucifixion, etc.
2. Curate major symbols: olive tree, bread, water, vine, veil, cornerstone, shepherd, etc. with source refs
3. Catalog prophecies with fulfillment status (fulfilled, pending, dual) — seed from Topical Guide + known chains
4. LLM extraction (Sonnet): process Isaiah, Daniel, Revelation, 1-2 Nephi for typological and prophetic relations
5. Flag dual fulfillments for Opus-tier review

### Phase 10 — Covenants, Priesthood, and Ordinances (2-3 days)
**Deliverables:**
- `COVENANT_WITH`, `RENEWED_BY`, `ORDAINED_BY`, `BAPTIZED_BY`, `HOLDS_PRIESTHOOD`, `KEYBEARER_OF`, `CONFERRED_KEYS_TO` relations
- Curated seed files for covenants (Abrahamic, Mosaic, new/everlasting) and priesthood events (D&C 13, 20, 27, 84, 107, 110, 128)
- LDS-specific ordinance chain modeled

**Tasks:**
1. Curate covenant chain: Abrahamic → renewed through Isaac → Jacob → Joseph → Moses → Christ → Joseph Smith
2. Curate priesthood restoration events from D&C with exact dates and source refs
3. Curate key bearers: Peter (kingdom), Elijah (sealing), Moses (gathering), Elias (dispensation of Abraham)
4. Extract `BAPTIZED_BY`, `ORDAINED_BY` from BofM and NT narratives (Haiku tier)
5. Load and validate: "¿Quién restauró el sacerdocio aarónico?" → John the Baptist, source D&C 13

### Phase 11 — Extended Relations (Genealogy, Military, Conversion, Discourse) (3-4 days)
**Deliverables:**
- `DESCENDANT_OF`, `TRIBE_OF`, `LINEAGE_OF` genealogical relations
- `CONQUERED`, `CAPTIVE_OF`, `REBELLED_AGAINST`, `ALLIED_WITH` military/political relations
- `CONVERTED_BY`, `REPENTED_OF`, `FELL_AWAY` spiritual transformation relations
- `SPOKE_TO`, `DISCOURSE_ABOUT`, `ADDRESSED_TO` discourse relations
- `PERFORMED`, `WITNESSED`, `SAW_IN_VISION`, `APPEARED_TO` miracle/vision relations

**Tasks:**
1. Curate patriarchal genealogy seed file: Adam→Seth→...→Noah→...→Abraham→...→David→...→Christ (from Matthew 1, Luke 3, 1 Chronicles)
2. Curate tribal assignments for key persons from gazetteer
3. Extract military/political relations from BofM war chapters (Alma 43-63) and OT conquest/exile narratives (Haiku tier)
4. Extract conversion narratives from Acts, BofM (Alma, sons of Mosiah, Lamanite kings) (Haiku tier)
5. Curate major visions: Lehi's tree, Nephi's expansion, John's Revelation, Joseph Smith's First Vision, D&C 76, D&C 138
6. Load and validate all relation types

### Phase 12 — LDS Dispensational Theology (2-3 days)
**Deliverables:**
- `DISPENSATION_HEAD`, `RESTORED`, `APOSTASY_IN`, `DISPENSATION_OF` relations
- `STAGE_OF`, `DEGREE_OF_GLORY` Plan of Salvation relations
- `PREFIGURED_BY`, `TEMPLE_AT`, `ORDINANCE_FOR_DEAD` temple relations
- BofM-specific: `RECORD_KEPT_BY`, `ABRIDGED_BY`, `WITNESS_OF`, `COLOPHON_IN`
- PGP-specific: `COUNCIL_PARTICIPANT`, `FACSIMILE_DEPICTS`

**Tasks:**
1. Curate dispensation heads with source refs (7 dispensations + associated keys/truths)
2. Curate restoration events timeline from D&C and Church history
3. Model Plan of Salvation stages with teaching passages
4. Curate BofM record-keeping chain: who kept which plates, who abridged what
5. Catalog facsimile interpretations from Abraham
6. Load and validate: "¿Qué restauró José Smith?" returns structured chain

### Phase 13 — Literary and Linguistic Analysis (3-4 days)
**Deliverables:**
- `CHIASM_IN`, `INCLUSIO_IN`, `PARALLELISM_IN`, `ACROSTIC_IN` literary structure relations
- `GENRE_OF` for every book/chapter
- `TRANSLATES_AS`, `WORD_STUDY` linguistic relations
- `EDITORIAL_NOTE` for Mormon's editorial voice in BofM
- `VARIANT_OF`, `POSSIBLE_SOURCE` text-critical relations

**Tasks:**
1. Curate known chiasms: Alma 36 (confirmed), Mosiah 3:18-19, Leviticus 24, key Isaiah passages
2. Assign `GENRE_OF` to every book — curated from standard biblical scholarship
3. Curate key Hebrew/Greek terms with `TRANSLATES_AS`: hesed, berith, logos, agape, emeth, ruach, etc. with semantic ranges and key passages
4. Identify and tag Mormon's editorial insertions in BofM ("And thus we see...", "And now I, Mormon...") as `EDITORIAL_NOTE`
5. Catalog `POSSIBLE_SOURCE` for Isaiah/BofM parallels, synoptic Gospel dependencies
6. LLM extraction (Sonnet): scan for additional literary patterns in poetic books (Psalms, Proverbs, Isaiah, Jacob, Alma)

### Phase 14 — Quality Framework and Performance (ongoing)
**Deliverables:**
- Confidence and provenance tracking on all relations
- Model tier assignment operational
- Token optimization pipeline
- Graph performance indexes and materialized paths
- Human review queue for low-confidence and theologically sensitive extractions

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
| M1 | Typed relations working, curated data loaded | Day 2 |
| M2 | Parallelism encoded in graph | Day 5 |
| M3 | LLM extraction producing typed relations | Day 10 |
| M4 | NER feedback loop operational | Day 12 |
| M5 | Entity attributes loaded, surfaced in neighbor queries | Day 15 |
| M6 | Canon hierarchy navigable in graph, metadata on Chapter nodes | Day 18 |
| M7 | Metadata-derived relations (D&C study_intro, Psalm authorship, summaries) loaded | Day 21 |
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
