# P7 — Deep Disambiguation — Project Plan

## Phases

### Phase 1 — Rule-Based Disambiguation (2-3 days)
**Deliverables:**
- Disambiguation rules engine
- Rules for top 20 most ambiguous entities (Judas, Mary, James, John, etc.)
- Integration with extraction pipeline

**Tasks:**
1. Define rule format: entity + contextual patterns → resolved entity
2. Curate rules for top ambiguous entities using modifier and companion patterns
3. Apply rules during `KGExtractor.extract()` before graph storage
4. Track resolution confidence per mention

### Phase 2 — LLM-Assisted Resolution (3-4 days)
**Deliverables:**
- LLM disambiguation for hard cases (no rule match, multiple candidates)
- Batch processing for cost efficiency
- Confidence scoring

**Tasks:**
1. Design LLM prompt: passage + candidates → resolved entity + confidence
2. Identify mentions that rules couldn't resolve
3. Batch LLM calls for unresolved mentions
4. Store results and update graph links

### Phase 3 — Profile & Graph Update (2 days)
**Deliverables:**
- Disambiguated mention counts in profiles
- Specific entity-document links in Neo4j
- Updated profile generation to use resolved mentions

**Tasks:**
1. Update `build_metadata_profiles()` to use resolved entity names
2. Update Neo4j links to use specific entities
3. Regenerate affected profiles

## Milestones

| Milestone | Deliverable | Estimate |
|-----------|------------|----------|
| M1 | Rule-based disambiguation for top 20 entities | Day 3 |
| M2 | LLM handles remaining ambiguous cases | Day 7 |
| M3 | Profiles and graph reflect specific mentions | Day 9 |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Rules become complex and hard to maintain | Medium | Keep rules simple; LLM handles edge cases |
| LLM costs for corpus-wide disambiguation | High | Rule-based first; LLM only for unresolved |
| Incorrect disambiguation degrades quality | Medium | Confidence scoring; only apply high-confidence resolutions |

## Success Criteria

1. "Judas Iscariot" has accurate mention count (not inflated by other Judases)
2. In Matthew 26, the system knows it's Judas Iscariot specifically
3. Mary of Bethany has distinct mentions from Mary mother of Jesus
