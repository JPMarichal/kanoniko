# P4 — Corpus Expansion — Requirements

## Problem Statement

The current corpus is limited to scriptures (EN complete, ES partial) and some conference talks, manuals, biographies, and web downloads. The knowledge engine's value grows with corpus breadth — more material enables richer answers, better entity profiles, and deeper knowledge graph connections.

## Functional Requirements

### FR-1: Material Types
Expand the corpus with the following material types (priority order):

1. **General Conference talks** — All available sessions (1971-present digitally available)
2. **Church manuals** — Come Follow Me, Gospel Principles, Teachings of Presidents
3. **Church magazines** — Ensign, Liahona, New Era, Friend
4. **Institute/Seminary materials** — Course manuals and student readings
5. **CES materials** — Church Educational System resources
6. **Historical documents** — Journal of Discourses, History of the Church
7. **Topical guides and Bible Dictionary** — Reference works

### FR-2: Bilingual Coverage
Each material type should be ingested in both English and Spanish where available.

### FR-3: Metadata Richness
Each document must carry:
- Title, author, date of publication
- Language, category, subcategory
- Source URL for provenance
- Material-type-specific fields (conference session, manual lesson number, etc.)

### FR-4: Corpus Directory Structure
Extend the existing corpus layout:
```
corpus/{lang}/general-conference/{year}/{month}/{slug}.md
corpus/{lang}/manuals/{manual-name}/{lesson}.md
corpus/{lang}/magazines/{publication}/{year}/{month}/{slug}.md
corpus/{lang}/institute/{course}/{lesson}.md
corpus/{lang}/historical/{collection}/{document}.md
corpus/{lang}/reference/{type}/{entry}.md
```

### FR-5: Incremental Growth
Support adding material types one at a time without disrupting existing content. Each expansion should be independently testable.

## Non-Functional Requirements

- Respect source site rate limits and terms of service
- Corpus size projections: ~50,000-100,000 documents when fully expanded
- Storage: estimated 500MB-2GB of text content
- Indexing time: must remain manageable (incremental indexing mitigates this)

## Dependencies

- **P3 (ETL Templates)**: Required for standardized ingestion of each material type

## Out of Scope

- Audio/video content
- Non-English/Spanish languages (future extensibility but not in scope)
- Copyrighted third-party commentary
