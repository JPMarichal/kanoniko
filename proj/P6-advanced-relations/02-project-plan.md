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

## Milestones

| Milestone | Deliverable | Estimate |
|-----------|------------|----------|
| M1 | Typed relations working, curated data loaded | Day 2 |
| M2 | Parallelism encoded in graph | Day 5 |
| M3 | LLM extraction producing typed relations | Day 10 |
| M4 | NER feedback loop operational | Day 12 |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM relation extraction noisy | High | Start with curated data; LLM supplements, doesn't replace |
| Relation type proliferation | Medium | Keep taxonomy small; prefer fewer accurate types |
| Graph query performance with many relation types | Low | Neo4j handles heterogeneous relations well |

## Dependencies

- P1 (Scripture Structure) improves context for extraction

## Success Criteria

1. "Who is the father of Isaac?" answered from graph relation, not just text search
2. Parallel passages discoverable via graph traversal
3. Top 50 NER candidates reviewable via API
