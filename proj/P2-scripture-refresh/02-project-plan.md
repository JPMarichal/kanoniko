# P2 — Scripture Corpus Completion — Project Plan

## Phases

### Phase 1 — Spanish Verses from MySQL Dump
**Deliverables:**
- Script that extracts verses from MySQL dump and writes corpus files
- Complete ES corpus: all 5 standard works in `corpus/es/scriptures/`
- Change report (new vs modified files, especially for existing BoM)

**Tasks:**
1. Parse `versiculos` table from MySQL dump (reuse P1's streaming parser)
2. Join verses to chapters via `PericopaId` → `CapituloId` (use P1's pericopae/chapters JSONs)
3. Assemble chapter files in `N verse text` format, ordered by verse number
4. Handle special cases: D&C sections, Official Declarations (prose, no verse numbers), PGP structure
5. Diff against existing BoM ES files — report modifications
6. Write new files for AT, NT, D&C, PGP in Spanish

### Phase 2 — English Verses from Official Site
**Deliverables:**
- Scraper for `churchofjesuschrist.org` scripture pages
- Updated EN corpus files from official source
- Diff report against current third-party-sourced files

**Tasks:**
1. Analyze scripture page structure on `churchofjesuschrist.org` (HTML inspection)
2. Build scraper: navigate volume → book → chapter, extract verse text
3. Handle D&C and PGP special structures
4. Rate limiting, resumability (checkpoint per book)
5. Diff against existing EN files, report changes
6. Replace corpus files with official-source content

### Phase 3 — Metadata Enrichment
**Deliverables:**
- Extended corpus format supporting headers, section headings, footnotes, cross-references
- Metadata scraped from official site for both EN and ES
- Updated corpus files with metadata

**Tasks:**
1. Design corpus format extension (backward-compatible with `N text` verse format)
2. Scrape chapter headers (summary text before verse 1) — EN and ES
3. Scrape section headings (in-chapter subheadings) — EN and ES
4. Scrape footnotes and cross-references — EN and ES
5. Write enriched corpus files
6. Validate that existing parsers/chunkers handle the new format gracefully

### Phase 4 — Validation & Reindex
**Deliverables:**
- Validated corpus (verse counts, completeness checks)
- Full reindex of changed files

**Tasks:**
1. Cross-validate verse counts: MySQL dump vs scraped EN vs scraped ES
2. Spot-check known passages for text fidelity
3. Trigger full ingestion pipeline for all changed files
4. Verify search results include new content

## Milestones

| Milestone | Deliverable |
|-----------|------------|
| M1 | Complete ES corpus from MySQL dump (all 5 volumes) |
| M2 | Complete EN corpus from official source |
| M3 | Metadata enrichment for both languages |
| M4 | Validated and reindexed |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Church site structure changes or blocks scraping | High | Cache downloaded HTML; implement polite delays and user-agent; do EN scraping in focused sessions |
| MySQL dump verse ordering issues | Medium | Validate against P1's pericopae structure; spot-check known passages |
| Metadata format breaks existing parsers | Medium | Design format extension as backward-compatible; test chunker before full write |
| Corporate proxy blocking scraping | Low | Existing `ca-certificates.crt` pattern handles this |

## Dependencies

- **P1 (complete):** Structure JSONs in `data/scripture_structure/` and the MySQL dump

## Success Criteria

1. `corpus/es/scriptures/` has all 5 volumes with correct verse text from official source
2. `corpus/en/scriptures/` has all 5 volumes with text from official site (not third-party)
3. Both languages include chapter headers, section headings, and footnotes
4. Running the extraction scripts again produces zero file changes (idempotent)
5. Ingestion pipeline indexes all new/changed files successfully
