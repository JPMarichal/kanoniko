# P1 — Scripture Structure: Long Chain — Requirements

## Problem Statement

The current system implements only the "short chain" for scripture hierarchy: **volume → book → chapter → verse**. This is sufficient for basic citation (e.g., "Genesis 1:1") but misses the editorial structure that gives scriptures their organizational meaning.

The "long chain" adds intermediate levels: **volume → division → book → part → chapter → pericope → verse**. Both chains must coexist — the short chain for everyday practical use, the long chain for structural navigation, thematic analysis, and knowledge graph enrichment.

### Available Asset

A pre-existing MySQL database (Laravel conventions) contains the complete long-chain hierarchy in Spanish:
- 5 volumes, 20 divisions, 88 books, 412 thematic parts, 1,584 chapters, 4,904 pericopae, 42,699 verses
- Dump location: `proj/P1-scripture-structure/recursos/dump-scriptures_db-202603281925.sql`

This asset accelerates the project but requires transformation (MySQL → JSON), bilingual completion (EN), and adaptation to Alejandría's architecture.

### Known Structural Exceptions

These cases break the "chapter:verse" assumption and require explicit modeling:

1. **Doctrine & Covenants (D&C / DyC)**: Structurally flat — no natural sub-books or literary divisions. Contains 138 *sections* (not chapters) + 2 Official Declarations. The adopted model uses a single Division ("Revelaciones de los últimos días" / "Latter-day Revelations") with two Books: "Secciones" (138 sections) and "Declaraciones Oficiales" (2 ODs). Parts are historical-geographic periods (Periodo de Nueva York, Periodo de Ohio, Periodo de Misuri, Periodo de Illinois, El Oeste). The MySQL dump has the geographic groupings as parts; they must be renamed to "Periodo de..." for clarity.

2. **Official Declarations**: OD-1 (1890) and OD-2 (1978) are prose documents without verse numbering. They form their own Book under the single D&C Division, with a single Part ("La Iglesia moderna" / "The Modern Church").

3. **Pearl of Great Price — Facsimiles**: The Book of Abraham includes 3 Facsimiles with numbered figure explanations that are NOT verse format. The MySQL dump does NOT include facsimiles — they must be added.
   - Facsimile 1: before Abraham 1
   - Facsimile 2: between chapters 3 and 4
   - Facsimile 3: after chapter 5

4. **Articles of Faith**: 13 numbered items functioning as verses in a single "chapter". Citation: "A of F 1:1-13" / "A de F 1:1-13".

## Functional Requirements

### FR-1: Data Extraction and Transformation
The system must extract structural data from the MySQL dump and produce JSON data files consumable by Alejandría.

- Input: MySQL dump (Laravel conventions, Spanish-only)
- Output: JSON files under `data/scripture_structure/`
- Mapping: MySQL IDs → Alejandría file path conventions (`corpus/{lang}/scriptures/{volume}/{book}/{chapter}.txt`)

### FR-2: Division Registry
The system must maintain a bilingual (EN/ES) registry of scripture divisions.

Source data (19 divisions — consolidated from 20 in MySQL dump, D&C collapsed to 1):

| Volume | Division (ES, from dump) | Division (EN, to add) |
|--------|--------------------------|----------------------|
| AT | La Ley | The Law (Pentateuch) |
| AT | Libros históricos (AT) | Historical Books |
| AT | Libros poéticos | Poetic Books (Wisdom Literature) |
| AT | Profetas mayores | Major Prophets |
| AT | Profetas menores | Minor Prophets |
| NT | Los evangelios | The Gospels |
| NT | Libros históricos (NT) | Historical Books (NT) |
| NT | Epístolas paulinas | Pauline Epistles |
| NT | Epístolas universales | General Epistles |
| NT | Libros proféticos | Prophetic Books |
| LM | Planchas menores | Small Plates |
| LM | Puente editorial | Editorial Bridge |
| LM | Planchas mayores | Large Plates |
| LM | Escritos de Mormón | Writings of Mormon |
| LM | Adiciones de Moroni | Additions of Moroni |
| DC | Revelaciones de los últimos días | Latter-day Revelations |
| PGP | Relacionados con el AT | Old Testament Related |
| PGP | Relacionados con el NT | New Testament Related |
| PGP | Relacionados con la Restauración | Restoration Related |

### FR-3: Part Registry
The system must maintain bilingual thematic parts — subdivisions within books that describe narrative or thematic units.

The MySQL dump provides 412 parts. These are NOT the "1 Samuel / 2 Samuel" numbered-book splits (those are already modeled as separate books). These are richer thematic divisions:

Examples from the dump:
- Génesis: La Creación, La Caída, El Diluvio, La dispersión de las naciones, Abraham, Isaac, Jacob, José
- D&C Secciones: Periodo de Nueva York, Periodo de Ohio, Periodo de Misuri, Periodo de Illinois, El Oeste (historical-geographic periods)
- D&C Declaraciones Oficiales: La Iglesia moderna
- Abraham (PGP): Preparación de Abraham, La visión de Abraham, La Creación

All 412 parts require EN translations.

### FR-4: Pericope Registry
The system must maintain titled passage units (pericopae) linked to chapter and verse ranges.

The MySQL dump provides 4,904 pericopae with: name (ES), chapter FK, verse_start, verse_end.

Examples from the dump:
- "Los seis días de la Creación, día 1" (Génesis 1:1-5)
- "Institución del matrimonio eterno" (Génesis 2:21-25)
- "La transgresión de Adán y Eva" (Génesis 3:1-7)

**Coverage constraint:** Every verse in every chapter must belong to exactly one pericope — no gaps, no overlaps. Within a chapter, pericopae must be contiguous: `verse_start[n+1] = verse_end[n] + 1`. The MySQL dump has gaps that must be identified and filled during extraction.

All pericopae (4,904 + gap-fills) require EN translations.

### FR-5: Facsimile Modeling (deferred — design only)
The 3 Abraham Facsimiles are absent from the MySQL dump and from the current corpus. Implementation is deferred, but the structural model must accommodate them without special-casing.

**Design decision:** Facsimiles are modeled as special chapters within the Book of Abraham. Numbered figure explanations function as verses. A `chapter_type` field (`"standard"` | `"facsimile"`) distinguishes them.

```
Libro: Abraham
  Parte: Preparación de Abraham
    Capítulo: Abraham 1
    Capítulo: Abraham 2
  Parte: La visión de Abraham
    Capítulo: Abraham 3
  Parte: La Creación
    Capítulo: Abraham 4
    Capítulo: Abraham 5
  Parte: Facsímiles del Libro de Abraham / Facsimiles of the Book of Abraham
    Capítulo: Facsímile 1  (chapter_type: facsimile, 12 figures)
    Capítulo: Facsímile 2  (chapter_type: facsimile, 22 figures)
    Capítulo: Facsímile 3  (chapter_type: facsimile, 6 figures)
```

Citation format: `Abraham, Facsimile 2:1` / `Abraham, Facsímile 2:1`

**What P1 delivers now:** The `chapter_type` field in the chapters JSON schema, with facsimile entries as placeholders (no corpus files yet). Future work will add corpus files and populate figure/verse content.

### FR-6: Chunk Metadata Enrichment
Each scripture chunk must carry metadata linking to both chains:
- Short: volume, book, chapter, verse range
- Long: division, part, pericope (when applicable)

### FR-7: Knowledge Graph Integration
Long-chain structural data must enrich the existing knowledge graph:
- **Division nodes** (type: `division`) linked to volume and containing books
- **Part nodes** (type: `part`) linked to book, providing thematic context
- **Pericope nodes** (type: `pericope`) linked to chapter/verse ranges, enabling thematic navigation
- Relations: `BELONGS_TO`, `CONTAINS`, `PART_OF`
- Entity profiles can reference structural context (e.g., "this passage is in the Sermon on the Mount pericope")

### FR-8: API Exposure
New or extended endpoints:
- `GET /scriptures/structure` — browse the full hierarchy tree
- `GET /scriptures/divisions?volume=ot` — list divisions per volume
- `GET /scriptures/pericopae?book=genesis&chapter=1` — list pericopae for a book/chapter
- Add `division`, `part`, `pericope` to search result metadata
- Add `division_filter` and `pericope_filter` to search endpoints

### FR-9: Bilingual Completeness
All structural names (divisions, parts, pericopae, facsimile titles) must exist in both English and Spanish. The MySQL dump provides ES; EN must be added.

## Non-Functional Requirements

- **Backward compatibility**: Existing short-chain references must continue to work unchanged
- **Extensibility**: The structure must support adding new languages beyond EN/ES
- **Data-driven**: All structural data in JSON files, not hardcoded
- **Incremental**: Adding pericopae should not require re-indexing the entire corpus
- **Traceability**: JSON files must retain MySQL source IDs for auditing the transformation

## Out of Scope

- Footnotes and study aids
- Manuscript variants
- Verse-level cross-references (covered by P6 — Advanced Relations)
- Non-canonical texts
- Pasajes and citas tables from the MySQL dump (future projects)
- Temas classification from the MySQL dump (future projects)
