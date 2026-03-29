# P1 — Scripture Structure: Long Chain — Project Plan

## Key Change from Original Plan

The discovery of the pre-existing MySQL database (Laravel) transforms Phase 1 from "research and create from scratch" to "extract, transform, and complete". The 4,904 pericopae, 412 parts, and 20 divisions already exist in Spanish — the work shifts to ETL, bilingual completion, and integration.

## Adopted D&C Model

D&C uses a single Division with two Books, resolving the structural flatness:

```
Volumen: Doctrina y Convenios / Doctrine and Covenants
  División: Revelaciones de los últimos días / Latter-day Revelations
    Libro: Secciones / Sections
      Parte: Periodo de Nueva York / New York Period
      Parte: Periodo de Ohio / Ohio Period
      Parte: Periodo de Misuri / Missouri Period
      Parte: Periodo de Illinois / Illinois Period
      Parte: El Oeste / The West
        Capítulo: Sección N
    Libro: Declaraciones Oficiales / Official Declarations
      Parte: La Iglesia moderna / The Modern Church
        Capítulo: Declaración Oficial 1, Declaración Oficial 2
```

The MySQL dump has two divisions (Secciones + Declaraciones Oficiales) and two books mirroring them. During extraction:
- Collapse into 1 Division: "Revelaciones de los últimos días"
- Promote the dump's 2 divisions to 2 Books: "Secciones" and "Declaraciones Oficiales"
- Rename geographic parts: "Nueva York" → "Periodo de Nueva York", etc.
- Rename OD part: "La Iglesia en la actualidad" → "La Iglesia moderna"

## Phases

### Phase 1 — ETL: MySQL → JSON (1-2 days)
**Goal:** Transform the MySQL dump into Alejandría's JSON data files.

**Deliverables:**
- Python extraction script: `scripts/extract_scripture_structure.py`
- `data/scripture_structure/volumes.json`
- `data/scripture_structure/divisions.json`
- `data/scripture_structure/books.json`
- `data/scripture_structure/parts.json`
- `data/scripture_structure/chapters.json` (with file path mapping)
- `data/scripture_structure/pericopae.json`
- Facsimile placeholders in chapters.json (`chapter_type: "facsimile"`)

**Tasks:**
1. Write extraction script that parses INSERT statements from the SQL dump
2. Map MySQL references to Alejandría file paths: `Génesis 1` → `es/scriptures/ot/genesis/1.txt`
3. Generate cross-reference table: MySQL `capitulos.Id` ↔ file path (needed for pericope mapping)
4. Produce JSON files with `mysql_id` field for traceability
5. Add a new Part "Facsímiles del Libro de Abraham" under Book Abraham, with 3 facsimile placeholder chapters (`chapter_type: "facsimile"`, no corpus file yet)
6. Handle D&C restructuring: collapse 2 dump divisions → 1 Division, promote to 2 Books, rename parts to "Periodo de..."
7. Handle ODs: prose documents under Book "Declaraciones Oficiales", Part "La Iglesia moderna"
8. **Pericope coverage validation**: for every chapter, verify that pericopae cover all verses contiguously (no gaps, no overlaps). Generate gap report.
9. **Pericope gap-fill**: create new pericopae for uncovered verse ranges with descriptive names
10. Validate: every chapter in JSON must correspond to an existing corpus file

### Phase 2 — Bilingual Completion (2-3 days)
**Goal:** Add English names to all structural data.

**Deliverables:**
- All JSON files enriched with `name_en` / `name_es` fields
- Validation report: coverage completeness per volume

**Tasks:**
1. Divisions (19 entries): manual EN translation — straightforward, well-known names
2. Parts (412 entries): semi-automated EN translation
   - Use LLM batch translation with domain context (scripture terminology)
   - Manual review of Book of Mormon and D&C parts (less standardized names)
3. Pericopae (4,904 + gap-fills): LLM batch translation with review
   - Group by volume for consistency
   - Spot-check well-known pericopae: "Sermon on the Mount", "Lehi's Dream", "The First Vision"
   - Gap-filled pericopae need both ES and EN names
4. Facsimile placeholders (3 entries): manual bilingual titles using official Church names

### Phase 3 — Metadata Integration (2-3 days)
**Goal:** Enrich chunks with long-chain metadata and integrate with KG.

**Deliverables:**
- `scripture_structure.py` — new module to load and resolve long-chain data
- Extended chunk metadata with `division`, `part`, `pericope` fields
- KG nodes and relations for structural entities

**Tasks:**
1. Create `src/alejandria/knowledge/scripture_structure.py`:
   - `load_structure()` — load all JSON files into memory
   - `resolve_long_chain(file_path, verse_start, verse_end)` → `{division, part, pericopae[]}`
   - Handle D&C sections (file path `dc/{section}.txt` → Division "Revelaciones de los últimos días" → Book "Secciones" → Part by period)
   - Handle ODs (Book "Declaraciones Oficiales" → Part "La Iglesia moderna")
   - Handle facsimiles (not verse-based, positional)
2. Extend chunk metadata in pipeline.py to call `resolve_long_chain()`
3. Add migration for existing chunks: populate long-chain fields from file paths
4. KG integration:
   - Add `division`, `part`, `pericope` as entity types in gazetteers
   - Create `PART_OF` relations: pericope → chapter, part → book, division → volume
   - Create `CONTAINS` relations: division → books, part → chapters
   - Entity profiles can reference pericope context in summaries

### Phase 4 — API & Search (1-2 days)
**Goal:** Expose structure via API and enable structural filtering.

**Deliverables:**
- New API endpoints for structure browsing
- Search faceting by division/pericope
- Updated search result schemas

**Tasks:**
1. `GET /scriptures/structure` — full hierarchy tree (cached)
2. `GET /scriptures/divisions?volume=ot` — divisions for a volume
3. `GET /scriptures/pericopae?book=genesis&chapter=1` — pericopae for a book/chapter
4. Add `division`, `part`, `pericope` to `SearchResultItem` schema
5. Add `division_filter` and `pericope_filter` parameters to search endpoints
6. Include pericope names in RAG context when available
7. Update system prompt to leverage structural information

## Milestones

| Milestone | Deliverable | Estimate |
|-----------|------------|----------|
| M1 | JSON files extracted from MySQL dump (ES only) | Day 2 |
| M2 | Bilingual JSON files complete (EN+ES) | Day 5 |
| M3 | Metadata integration + KG nodes working | Day 8 |
| M4 | API endpoints live, search faceting works | Day 10 |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| MySQL file path mapping errors | High — chunks won't find their structure | Validate every chapter against actual corpus files |
| EN translation quality for 4,904 pericopae | Medium — wrong names degrade search | LLM translation + spot-check of well-known passages |
| D&C restructuring (collapse divisions, rename parts) | Medium | Explicit mapping table in extraction script, validate chain completeness |
| Pericope gap-fill naming quality | Medium | LLM generates names from verse content; manual review for D&C and PGP |
| Facsimile corpus files don't exist yet | Low | P1 creates placeholders with `chapter_type: "facsimile"`; content deferred |
| ODs without verses break pericope model | Low | Model as prose units with `verse_start: null, verse_end: null` |

## Dependencies

- MySQL dump file (available: `proj/P1-scripture-structure/recursos/`)
- Corpus files must be downloaded (`scripts/download_scriptures.py`)
- No external service dependencies for Phases 1-2

## Success Criteria

1. Every scripture chunk carries both short-chain and long-chain metadata
2. `GET /scriptures/structure` returns complete bilingual hierarchy for all 5 standard works
3. D&C sections, Official Declarations, and Facsimiles are correctly modeled
4. Search results can be filtered by division or pericope
5. "The Sermon on the Mount" as a pericope search returns Matthew 5-7 chunks
6. KG contains division, part, and pericope nodes with structural relations
7. All pericopae (4,904 + gap-fills) have bilingual names
8. Pericope coverage is 100%: every verse belongs to exactly one pericope, no gaps, no overlaps
9. D&C chain resolves correctly: Volume → "Revelaciones de los últimos días" → "Secciones"/"Declaraciones Oficiales" → Period → Section
