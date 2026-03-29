# P1 Phase 1 Report — ETL: MySQL → JSON

**Status:** Complete
**Date:** 2026-03-28
**Commit:** `ac6750e` — "P1 Phase 1: ETL script - extract scripture structure from MySQL dump"

## Deliverables

### Extraction Script

`scripts/extract_scripture_structure.py` (809 lines)

A streaming SQL parser that processes the 620MB MySQL dump line-by-line. Key components:

- **`extract_tables_streaming()`** — Line-by-line SQL parser (avoids MemoryError on 32-bit Python 3.7). Detects `INSERT INTO` statements for each table and yields parsed rows.
- **`parse_values_string()`** — State machine parser for SQL VALUES with proper string/escape handling.
- **`BOOK_SLUG_MAP`** — 88-entry dictionary mapping MySQL Spanish book names to `(volume_slug, book_slug)` tuples for corpus file path generation.
- **`build_divisions()`** — Collapses D&C's 2 MySQL divisions (IDs 16, 17) into 1: "Revelaciones de los últimos días".
- **`build_parts()`** — Renames D&C parts via `DC_PART_RENAME` dict ("Nueva York" → "Periodo de Nueva York", etc.).
- **`add_facsimile_placeholders()`** — Adds new Part "Facsímiles del Libro de Abraham" + 3 facsimile chapters (`chapter_type: "facsimile"`).
- **`validate_pericope_coverage()`** — Checks gaps/overlaps against actual corpus verse counts.
- **`validate_corpus()`** — Verifies every chapter path exists in corpus.

### JSON Output Files

All written to `data/scripture_structure/`:

| File | Records | Description |
|------|---------|-------------|
| `volumes.json` | 5 | AT, NT, LM, DC, PGP with slug and ES names |
| `divisions.json` | 19 | 19 divisions (collapsed from 20 in MySQL) with ES+EN names |
| `books.json` | 88 | All canonical books with ES names and abbreviations |
| `parts.json` | 389 | Thematic/geographic sections with ES names |
| `chapters.json` | 1,587 | 1,584 standard + 3 facsimile placeholders |
| `pericopae.json` | 4,904 | All pericope entries with verse ranges |

### Structural Decisions Implemented

1. **D&C Restructuring:** MySQL had 2 divisions → collapsed to 1 Division ("Revelaciones de los últimos días"), promoted to 2 Books ("Secciones" + "Declaraciones Oficiales"), renamed geographic parts ("Nueva York" → "Periodo de Nueva York").

2. **Facsimiles:** Added new Part "Facsímiles del Libro de Abraham" under Book Abraham with 3 chapters of `chapter_type: "facsimile"`. Content deferred to future phase.

3. **Official Declarations:** Modeled as prose chapters (`chapter_type: "prose"`) with `verse_start: null, verse_end: null`.

4. **Pericope Coverage:** Validated 100% — 0 gaps, 0 overlaps across all 1,582 corpus chapters (every verse belongs to exactly one pericope).

### Technical Challenges Resolved

| Challenge | Solution |
|-----------|----------|
| MemoryError loading 620MB SQL dump on 32-bit Python 3.7 | Streaming line-by-line parser instead of `f.read()` |
| `TypeError: 'type' object is not subscriptable` (Python 3.7) | Added `from __future__ import annotations` |
| UnicodeEncodeError on Windows cp1252 console | Replaced box-drawing/emoji chars with ASCII |
| GitHub push rejected (620MB file exceeded 100MB limit) | Added `proj/**/recursos/` to `.gitignore`, recommitted |

### Validation Results

- 88/88 books mapped to corpus slugs
- 1,582/1,582 standard chapters verified against corpus files
- 4,904 pericopae validated: 0 gaps, 0 overlaps
- D&C chain verified: DyC 20:15 → Volume: Doctrina y Convenios → División: Revelaciones de los últimos días → Libro: Secciones → Parte: Periodo de Nueva York → Capítulo: Sección 20 → Perícopa → Versículo 15

### MySQL Dump Additional Discovery

The `versiculos` table contains 42,699 verse records extracted from the official Church website in Spanish. This can fill the missing ES corpus for AT, NT, D&C, and PGP in a future phase (currently only Book of Mormon exists in Spanish corpus).
