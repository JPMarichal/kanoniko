# P3 — ETL Templates — Project Plan

## Phases

### Phase 1 — Template Engine (2-3 days)
**Deliverables:**
- Template schema definition (YAML format)
- Template loader and validator
- Base ETL processor that applies templates to source files

**Tasks:**
1. Design template YAML schema with extraction rules
2. Build template loader with validation
3. Implement extraction pipeline: load template → read source → extract text → extract metadata → clean → validate → write output
4. Error handling and per-file reporting

### Phase 2 — Core Templates (3-4 days)
**Deliverables:**
- Conference talk template (HTML source from churchofjesuschrist.org)
- Church manual template (HTML/JSON source)
- Web page generic template

**Tasks:**
1. Analyze conference talk HTML structure, build extraction rules
2. Analyze manual page structure, build extraction rules
3. Build generic web template with configurable CSS selectors
4. Test each template against 10+ real source files
5. Validate metadata completeness

### Phase 3 — Integration (1-2 days)
**Deliverables:**
- CLI command `alejandria etl`
- API endpoint `POST /index/etl`
- Template directory in repository (`etl/templates/`)

**Tasks:**
1. CLI with --template, --input, --output flags
2. API endpoint with template name and source path
3. Auto-trigger indexing after ETL completes
4. Documentation for creating custom templates

## Milestones

| Milestone | Deliverable | Estimate |
|-----------|------------|----------|
| M1 | Template engine working with test template | Day 3 |
| M2 | Conference and manual templates validated | Day 7 |
| M3 | CLI/API integration, production-ready | Day 9 |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Source HTML structures vary across years | Medium | Templates support CSS selector fallbacks; version-specific rules |
| Metadata extraction unreliable | Medium | Validation step catches incomplete metadata; manual review queue |
| Template format too rigid | Low | Start simple, extend schema as needed |

## Dependencies

- None — can proceed independently (P4 depends on this)

## Success Criteria

1. Conference talk ETL produces clean, metadata-rich corpus files from raw HTML
2. Templates are YAML files editable without code changes
3. `alejandria etl --template conference` processes 100+ talks without errors
