# P2 — Scripture Refresh Pipeline — Requirements

## Problem Statement

The current scripture download (`scripts/download_scriptures.py`) is a one-shot manual script that pulls from third-party GitHub repositories (beandog/lds-scriptures for English, janKaje for Spanish BoM only). It has no incremental update capability, no official source integration, and incomplete Spanish coverage (missing OT, NT, D&C, PGP in Spanish).

The system needs an automated, repeatable pipeline that downloads from the official Church content API, detects changes, and triggers re-indexing.

## Functional Requirements

### FR-1: Official Source Integration
Download scriptures from `churchofjesuschrist.org` content API or equivalent official endpoints. The source must be authoritative and maintained.

### FR-2: Bilingual Complete Coverage
Download all 5 standard works in both English and Spanish:
- Old Testament / Antiguo Testamento
- New Testament / Nuevo Testamento
- Book of Mormon / Libro de Mormón
- Doctrine and Covenants / Doctrina y Convenios
- Pearl of Great Price / Perla de Gran Precio

### FR-3: Incremental Updates
Compare downloaded content against existing corpus files. Only write files that have changed. Generate a change report (new, modified, unchanged, deleted).

### FR-4: Integration with Ingestion Pipeline
After a refresh, automatically trigger incremental indexing for changed files. The existing SHA-256 change detection handles the rest.

### FR-5: Scheduling
Support both on-demand execution (CLI/API) and scheduled runs (e.g., weekly check for updates).

### FR-6: Rate Limiting & Politeness
Respect the official site's rate limits and terms of service. Include configurable delays between requests.

### FR-7: Language Extensibility
Design for easy addition of new languages (Portuguese, French, etc.) without code changes — language codes as configuration.

## Non-Functional Requirements

- **Idempotent**: Running the refresh twice with no changes should produce no writes
- **Resumable**: If interrupted, can resume from where it stopped
- **Auditable**: Log what was downloaded, changed, and when
- **SSL-aware**: Handle corporate proxy certificates (existing `ca-certificates.crt` pattern)

## Out of Scope

- Footnotes, cross-references, and study aids from the official site
- Non-scripture content (conference talks, manuals — covered by P3/P4)
- Translation of UI or metadata (only scripture text)

## Current State

- `scripts/download_scriptures.py` exists but uses third-party sources
- English coverage: complete (all 5 volumes)
- Spanish coverage: Book of Mormon only
- No change detection, no scheduling, no official API integration
