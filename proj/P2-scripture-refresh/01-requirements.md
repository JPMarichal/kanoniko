# P2 — Scripture Corpus Completion — Requirements

## Problem Statement

The current scripture corpus has two gaps:

1. **Incomplete Spanish text:** Only Book of Mormon exists in `corpus/es/`. The remaining 4 standard works (OT, NT, D&C, PGP) are missing. A MySQL dump with 42,699 official Spanish verses is available from P1.
2. **Missing metadata in both languages:** Scripture files contain only verse text. Headers (chapter summaries, section headings), footnotes, and cross-references from the official Church site are absent.
3. **English text from third-party source:** Current EN files come from GitHub repos (beandog/lds-scriptures), not from the official Church site.

This is a **one-time corpus completion** operation per language, not a recurring refresh pipeline.

## Functional Requirements

### FR-1: Spanish Verses from MySQL Dump
Extract verses from the MySQL dump (`proj/P1-scripture-structure/recursos/dump-scriptures_db-202603281925.sql`) and assemble them into chapter files following the corpus format:
- Path: `corpus/es/scriptures/{volume}/{book}/{chapter}.txt`
- Format: `1 Verse text.\n2 Verse text.\n...`
- Use P1's structure JSONs (`data/scripture_structure/`) for slug mapping and chapter organization
- Handle special structures: D&C sections, Official Declarations (prose), PGP short books

### FR-2: English Verses from Official Site
Scrape verse text from `churchofjesuschrist.org` for all 5 standard works in English. Replace current third-party-sourced files with official content.

### FR-3: Metadata Enrichment (Both Languages)
Scrape and add to corpus files for both EN and ES:
- **Chapter headers:** Summary/intro text that precedes verse 1
- **Section headings:** In-chapter subheadings between verses
- **Footnotes and cross-references:** Verse-level annotations

Define a corpus format extension that preserves the current `N text` verse format while accommodating metadata (e.g., header lines before verse 1, inline markers for footnotes).

### FR-4: Bilingual Complete Coverage
All 5 standard works in both languages:
- Old Testament / Antiguo Testamento
- New Testament / Nuevo Testamento
- Book of Mormon / Libro de Mormón
- Doctrine and Covenants / Doctrina y Convenios
- Pearl of Great Price / Perla de Gran Precio

### FR-5: Change Detection
Compare generated content against existing corpus files. Only write files that have changed. Report: new, modified, unchanged counts.

### FR-6: Integration with Ingestion Pipeline
After corpus writes, trigger incremental indexing. The existing SHA-256 change detection in the ingestion pipeline handles the rest.

## Non-Functional Requirements

- **Idempotent**: Running the same extraction twice produces zero writes
- **Resumable**: Scraping (EN) can resume from where it stopped if interrupted
- **Auditable**: Log what was extracted/scraped, changed, and when
- **Rate-limited**: Scraping respects the official site (configurable delays between requests)
- **SSL-aware**: Handle corporate proxy certificates (existing `ca-certificates.crt` pattern)

## Out of Scope

- Recurring/scheduled refresh (this is a one-time operation per language)
- Non-scripture content (conference talks, manuals — covered by P3/P4)
- Facsimile images (Abraham facsimiles — placeholder chapters only)
- Additional languages beyond EN/ES (architecture supports it, but not in this project's scope)

## Current State

- `scripts/download_scriptures.py` — current downloader, uses third-party GitHub repos
- `scripts/extract_scripture_structure.py` — P1 ETL, extracts structure from MySQL dump
- `data/scripture_structure/` — 6 structure JSONs (volumes, divisions, books, parts, chapters, pericopae)
- `corpus/en/scriptures/` — complete (5 volumes, third-party source)
- `corpus/es/scriptures/` — Book of Mormon only (239 files)
- MySQL dump — 42,699 ES verses linked to chapters via pericopae
