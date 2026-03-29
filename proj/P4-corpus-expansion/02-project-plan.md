# P4 — Corpus Expansion — Project Plan

## Phases

### Phase 1 — General Conference Archive (3-5 days)
**Deliverables:**
- Complete conference talk corpus (1971-present, EN/ES)
- ETL template for conference talks (built in P3)
- Download scripts with rate limiting

**Tasks:**
1. Map conference talk URL patterns and API endpoints
2. Build or adapt downloader for bulk conference talk retrieval
3. Apply ETL template to produce corpus files
4. Run indexing and validate search results
5. Verify entity extraction quality on conference content

### Phase 2 — Church Manuals (2-3 days)
**Deliverables:**
- Key manuals in corpus (Come Follow Me, Gospel Principles)
- ETL template for manuals

**Tasks:**
1. Identify priority manuals and their digital availability
2. Download and apply ETL template
3. Index and validate

### Phase 3 — Magazines & Institute (3-4 days)
**Deliverables:**
- Ensign/Liahona archive (recent years)
- Institute course materials
- ETL templates for each

**Tasks:**
1. Map magazine archive structure
2. Map institute material structure
3. Download, ETL, index for each type

### Phase 4 — Historical & Reference (2-3 days)
**Deliverables:**
- Journal of Discourses (public domain)
- Bible Dictionary and Topical Guide
- ETL templates for reference works

**Tasks:**
1. Source public domain historical texts
2. Build reference work ETL (entry-based, not chapter-based)
3. Index and validate cross-references with existing corpus

## Milestones

| Milestone | Deliverable | Estimate |
|-----------|------------|----------|
| M1 | Conference talks complete (EN/ES) | Week 1 |
| M2 | Manuals added | Week 2 |
| M3 | Magazines and institute | Week 3 |
| M4 | Historical and reference works | Week 4 |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Large corpus strains indexing performance | Medium | Incremental indexing; monitor timing per phase |
| Qdrant memory usage grows significantly | Medium | Monitor vector count; consider collection partitioning |
| Neo4j KG rebuild time becomes prohibitive | High | Consider incremental KG updates instead of full rebuilds |
| Quality variation across material types | Medium | Per-type validation rules in ETL templates |

## Dependencies

- **P3 (ETL Templates)** must be complete before starting

## Success Criteria

1. Conference talks searchable and appearing in RAG answers
2. Corpus grows from ~1,800 to 10,000+ documents
3. Entity profiles enriched with conference/manual references
4. Search quality improves for doctrinal and modern-context questions
