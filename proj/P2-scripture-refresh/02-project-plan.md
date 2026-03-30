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

## Known Defects

### DEF-1: Section headings not captured (FR-3 partial)
**Status:** PARTIALLY RESOLVED (steps 1–2 done; steps 3–4 pending re-scrape)
**Severity:** Medium — blocks accurate authorship extraction in P6

FR-3 requires capturing "Section headings: In-chapter subheadings between verses." This was never implemented in `scrape_scriptures.py`. The function `extract_metadata()` only extracts `study-summary`, `<h1>`, `<meta>`, and footnotes — it never looks for section heading elements.

**Impact:**
- **Psalms:** Superscriptions with author attributions are missing (e.g., "Salmo de Asaf" for Psalms 73-83, "De los hijos de Coré" for Psalms 42-49, "Masquil de Hemán ezraíta" for Psalm 88). Only 82 of 150 psalms have author info derivable from the `summary` field; the rest require superscriptions that were not scraped.
- **Other books:** Pericope headings in the NT and other section markers may also be absent.
- **P6 dependency:** The `AUTHORED` relation extraction planned in P6-FR-1/FR-8 cannot be fully automated without this data.

**HTML selectors identified:**
- `<p id="intro{N}">` (e.g. `id="intro1"`): chapter-level introductory text / Psalm superscriptions. Appears between the chapter number and verse 1. Confirmed in reference scraper output for Psalm 73.
- `<h2>` within `<article>`: in-chapter section headings (pericope headings) that appear between verses. Confirmed by reference scraper type mapping (`h2` → `section-title`).

Both element types are scoped to `soup.find("article")` to exclude navigation elements outside the article body.

**Fix status:**
1. ✅ HTML selectors identified (see above)
2. ✅ Added extraction to `extract_metadata()` — stored as `"section_headings"` (list of strings, document order) in `.meta.json`
3. ⏳ Re-scrape all books in both languages (EN + ES) to populate `section_headings` in corpus `.meta.json` files
4. ⏳ Update success criteria #3 to include section headings

**Fix required:**
1. ~~Identify the HTML selector for section headings / superscriptions on `churchofjesuschrist.org`~~
2. ~~Add extraction to `extract_metadata()` — store as `"section_headings"` or `"superscription"` in `.meta.json`~~
3. Re-scrape affected chapters (all books in both languages)
4. Update success criteria #3 to include section headings

## Success Criteria

1. ✅ `corpus/es/scriptures/` has all 5 volumes with correct verse text from official source
2. ✅ `corpus/en/scriptures/` has all 5 volumes with text from official site (not third-party)
3. ✅ Both languages have `.meta.json` sidecar files with footnotes and cross-references
4. ✅ Cross-references are parsed, bidirectional, and available for RAG expansion
5. ✅ Neo4j graph loaded with cross-reference relationships (29,299 nodes, 86,007 rels)
6. ✅ RAG pipeline integrated with `_expand_footnote_xrefs()` — activates on container rebuild
