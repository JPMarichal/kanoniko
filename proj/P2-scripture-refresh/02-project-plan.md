# P2 — Scripture Corpus Completion — Project Plan

## Phases

### Phase 1 — Spanish Verses from MySQL Dump ✅
**Status:** COMPLETE (2026-03-28)
**Deliverables:**
- `scripts/extract_es_verses.py` — extracts verses from MySQL dump, writes corpus files
- Complete ES corpus: 1,587 chapters across all 5 standard works
- Superseded by Phase 2 ES scrape (official source preferred over dump)

### Phase 2 — Scrape from Official Site (EN + ES) ✅
**Status:** COMPLETE (2026-03-29)
**Deliverables:**
- `scripts/scrape_scriptures.py` — scraper for `churchofjesuschrist.org`
- EN corpus: 1,587 files, 42,032 verses, 47,192 footnotes
- ES corpus: 1,587 files, 42,033 verses, 29,923 footnotes
- `.meta.json` sidecar files with title, summary, footnotes per chapter
- `docs/P2-verse-discrepancy-report.md` — analysis of 10 EN/ES differences

### Phase 3 — Cross-Reference Parsing & KG Integration ✅
**Status:** COMPLETE (2026-03-29)
**Deliverables:**
- `scripts/parse_cross_references.py` — parses footnote references, builds bidirectional index
- `data/scripture_structure/cross_references.json` — 97,961 bidirectional cross-references
- `scripts/load_cross_refs_neo4j.py` — loads cross-refs into Neo4j (29,299 verse nodes, 97,961 relationships)
- Extended `src/alejandria/ingestion/cross_references.py` with footnote-based RAG expansion

**Key metrics:**
| Metric | Value |
|--------|-------|
| EN directional references | 43,588 |
| ES directional references | 22,637 |
| Already bidirectional (in footnotes) | 15,016 pairs |
| New reciprocals created | 31,736 |
| Total bidirectional entries | 97,961 |
| Unique verse pairs | 86,007 |
| Abbreviations mapped (EN) | ~95 |
| Abbreviations mapped (ES) | ~90 |
| Unresolved footnotes | 286 (0.37%) — legitimate linguistic/explanatory notes |

### Phase 4 — KG Loading & RAG Integration ✅
**Status:** COMPLETE (2026-03-29)
**Deliverables:**
- Neo4j loaded: 29,299 ScriptureVerse nodes, 86,007 CROSS_REF relationships, 59,413 IN_CHAPTER links
- RAG pipeline extended with `_expand_footnote_xrefs()` method in `chat/rag.py`
- New search mode `"footnote-xref"` alongside existing `"hybrid"`, `"cross-ref"`, `"kg-boost"`
- Container rebuild needed to activate in production (`docker compose up --build`)

## Milestones

| Milestone | Deliverable | Status |
|-----------|------------|--------|
| M1 | Complete ES corpus from MySQL dump (all 5 volumes) | ✅ |
| M2 | Complete EN+ES corpus from official source | ✅ |
| M3 | Cross-reference parsing + bidirectional index + RAG integration | ✅ |
| M4 | Neo4j loaded + RAG integrated | ✅ |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Church site structure changes or blocks scraping | High | All data already scraped and cached in corpus+meta files |
| MySQL dump verse ordering issues | Medium | RESOLVED: dump data superseded by official site scrape |
| Cross-reference JSON too large for memory | Low | 27 MB loads in ~2s; batch loading for Neo4j |
| Corporate proxy blocking scraping | Low | RESOLVED: existing `ca-certificates.crt` pattern |

## Dependencies

- **P1 (complete):** Structure JSONs in `data/scripture_structure/` and the MySQL dump

## Success Criteria

1. ✅ `corpus/es/scriptures/` has all 5 volumes with correct verse text from official source
2. ✅ `corpus/en/scriptures/` has all 5 volumes with text from official site (not third-party)
3. ✅ Both languages have `.meta.json` sidecar files with footnotes and cross-references
4. ✅ Cross-references are parsed, bidirectional, and available for RAG expansion
5. ✅ Neo4j graph loaded with cross-reference relationships (29,299 nodes, 86,007 rels)
6. ✅ RAG pipeline integrated with `_expand_footnote_xrefs()` — activates on container rebuild
