# P1 — Scripture Structure: Long Chain — Requirements

## Problem Statement

The current system implements only the "short chain" for scripture hierarchy: **volume → book → chapter → verse**. This is sufficient for basic citation (e.g., "Genesis 1:1") but misses the editorial structure that gives scriptures their organizational meaning.

The "long chain" adds three intermediate levels: **volume → division → part → book → pericope → chapter → verse**. Both chains must coexist — the short chain for everyday practical use, the long chain for structural navigation and thematic analysis.

## Functional Requirements

### FR-1: Division Registry
The system must maintain a bilingual (EN/ES) registry of scripture divisions.

Examples:
| Volume | Division (EN) | Division (ES) |
|--------|--------------|--------------|
| OT | Pentateuch | Pentateuco |
| OT | Historical Books | Libros Históricos |
| OT | Wisdom Literature | Literatura Sapiencial |
| OT | Major Prophets | Profetas Mayores |
| OT | Minor Prophets | Profetas Menores |
| NT | Gospels | Evangelios |
| NT | Pauline Epistles | Epístolas Paulinas |
| NT | General Epistles | Epístolas Generales |
| BoM | Small Plates | Planchas Menores |
| BoM | Large Plates | Planchas Mayores |
| D&C | (sections are not traditionally grouped into divisions — evaluate if thematic groupings are useful) |
| PGP | (each book is its own division) |

### FR-2: Part Registry
The system must support "parts" as subdivisions of books where applicable.

Examples:
- Samuel → 1 Samuel, 2 Samuel
- Kings → 1 Kings, 2 Kings
- Chronicles → 1 Chronicles, 2 Chronicles
- Nephi → 1 Nephi, 2 Nephi
- Corinthians → 1 Corinthians, 2 Corinthians

### FR-3: Pericope Registry
The system must maintain titled passage units (pericopae) that span one or more chapters or portions of chapters.

Examples:
- "The Sermon on the Mount" (Matthew 5-7)
- "The Parable of the Sower" (Matthew 13:1-23)
- "Lehi's Dream" (1 Nephi 8)
- "Alma's Discourse on Faith" (Alma 32)
- "The Articles of Faith" (AoF 1:1-13)

Pericopae must be bilingual (EN/ES).

### FR-4: Chunk Metadata Enrichment
Each chunk must carry metadata linking to both the short chain and the long chain:
- Short: volume, book, chapter, verse range
- Long: division, part, pericope (when applicable)

### FR-5: API Exposure
New or extended endpoints to:
- List divisions per volume
- List pericopae per book/chapter
- Search/filter by division or pericope
- Include long-chain metadata in search results

### FR-6: Bilingual Completeness
All structural names (divisions, parts, pericopae) must exist in both English and Spanish.

## Non-Functional Requirements

- **Backward compatibility**: Existing short-chain references must continue to work unchanged
- **Extensibility**: The structure must support adding new languages beyond EN/ES
- **Data-driven**: Divisions and pericopae should be defined in data files (JSON/YAML), not hardcoded
- **Incremental**: Adding pericopae should not require re-indexing the entire corpus

## Out of Scope

- Footnotes and study aids
- Manuscript variants
- Verse-level cross-references (covered by P6 — Advanced Relations)
- Non-canonical texts
