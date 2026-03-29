# P2 Phase 2 — Verse Count Discrepancy Report EN vs ES

**Total chapters with line count differences:** 10
**Total extra lines in ES (vs EN):** +42
**Root cause:** Bug in MySQL dump data — `NumVersiculo` field contains duplicate values within the same chapter, causing the ETL to produce multiple lines with the same verse number.

## Diagnosis

The MySQL dump's `versiculos` table has rows where `NumVersiculo=1` is reused for content that belongs to other verses. These appear to be:

1. **Hymn/song lines** stored as separate rows (D&C 84:99-102 hymn text split into 15 rows all with NumVersiculo=1)
2. **Colophon/signature** lines (D&C 102 has "OLIVER COWDERY" and "Secretarios" as separate verse-1 rows)
3. **Cross-book contamination** (Amos 9 has Obadiah verses mixed in — verses 3-15 each appear twice with different text)
4. **Quotation fragments** (Hebrews 1, 2, 8 and Romans 16 have biblical quotations or colophons stored as extra verse-1 rows)

## Summary Table

| Chapter | EN lines | ES lines | Diff | Cause |
|---------|----------|----------|------|-------|
| dc/sections/84.txt | 120 | 134 | +14 | Hymn text (84:99-102) split into 15 separate rows, all NumVersiculo=1 |
| dc/sections/102.txt | 34 | 37 | +3 | Colophon: "OLIVER COWDERY", "ORSON HYDE", "Secretarios" as verse-1 rows |
| ot/amos/9.txt | 15 | 34 | +19 | Obadiah verses mixed in: v3-v15 each duplicated with Obadiah text. ES also has v16-21 (Obadiah 16-21) |
| ot/joel/1.txt | 20 | 19 | -1 | ES dump missing verse 1 entirely |
| nt/2-corinthians/6.txt | 18 | 19 | +1 | Verse 2b quotation stored as separate verse-1 row |
| nt/3-john/1.txt | 14 | 15 | +1 | ES has verse 15 (some traditions include it; EN KJV does not) |
| nt/hebrews/1.txt | 14 | 15 | +1 | Verse 5b quotation stored as separate verse-1 row |
| nt/hebrews/2.txt | 18 | 20 | +2 | Two quotation fragments (8b, 13b) stored as verse-1 rows |
| nt/hebrews/8.txt | 13 | 14 | +1 | Verse 10b quotation stored as separate verse-1 row |
| nt/romans/16.txt | 27 | 28 | +1 | Colophon ("Fue escrita en Corinto...") stored as verse-1 row |

## Detail per Chapter

### dc/sections/84.txt
- EN: 120 lines (120 verses), ES: 134 lines (120 unique verse nums + 14 duplicate v1 rows)
- **Problem:** D&C 84:99-102 contains the "new song" hymn. In EN (scraped from official site), the hymn lines are concatenated within each verse. In the MySQL dump, the hymn lines are stored as 15 separate rows all with `NumVersiculo=1`, placed in pericopa 4562 (which covers verses 1-5).
- **EN verse 99:** `The Lord hath brought again Zion;The Lord hath redeemed his people, Israel,According to the election of grace,...`
- **ES duplicate v1 rows:** `el Señor ha redimido a su pueblo, Israel,` / `conforme a la elección de gracia,` / `la cual se llevó a cabo por la fe` / etc. (15 lines)

### dc/sections/102.txt
- EN: 34 lines, ES: 37 lines (34 unique + 3 duplicate v1 rows)
- **Problem:** Section 102 has a colophon with signatories. The dump stores these as 3 extra verse-1 rows: "Este día se reunió un concilio general...", "OLIVER COWDERY,", "ORSON HYDE,", "Secretarios."

### ot/amos/9.txt
- EN: 15 lines (v1-15), ES: 34 lines (v1-21, with v3-15 duplicated)
- **Problem:** The MySQL dump has **Obadiah** verses mixed into Amos 9. Verses 3-15 each appear twice — once with the correct Amos text and once with Obadiah text. Additionally, ES has verses 16-21 which are Obadiah 16-21 (Obadiah has 21 verses, Amos 9 has only 15).
- **Duplicate example v3:**
  - Amos: `Y aunque se escondan en la cumbre del Carmelo, allí los buscaré...`
  - Obadiah: `La soberbia de tu corazón te ha engañado, tú que moras en las hendiduras...`

### ot/joel/1.txt
- EN: 20 lines (v1-20), ES: 19 lines (v2-20)
- **Problem:** ES dump is missing verse 1 entirely. The verse range starts at 2.

### nt/2-corinthians/6.txt
- EN: 18 lines, ES: 19 lines
- **Problem:** Verse 2 contains an OT quotation ("he aquí ahora es el tiempo aceptable..."). The dump stores the quotation as a separate row with NumVersiculo=1.

### nt/3-john/1.txt
- EN: 14 lines (v1-14), ES: 15 lines (v1-15)
- **Note:** This is a legitimate textual difference. Some Bible traditions (including Reina-Valera used for LDS Spanish) include verse 15 in 3 John, while the KJV (used for LDS English) ends at verse 14. This is NOT a bug.

### nt/hebrews/1.txt
- EN: 14 lines, ES: 15 lines
- **Problem:** Verse 5 contains a quotation ("Yo seré para él Padre, y él será para mí hijo"). The dump stores the second part of the quotation as a separate verse-1 row.

### nt/hebrews/2.txt
- EN: 18 lines, ES: 20 lines
- **Problem:** Two biblical quotations (in verses 8 and 13) are stored as separate verse-1 rows: "Porque en cuanto le sujetó todas las cosas..." and "He aquí, yo y los hijos que me dio Dios."

### nt/hebrews/8.txt
- EN: 13 lines, ES: 14 lines
- **Problem:** Verse 10 contains a quotation from Jeremiah. The second part is stored as a separate verse-1 row: "después de aquellos días, dice el Señor..."

### nt/romans/16.txt
- EN: 27 lines, ES: 28 lines
- **Problem:** The chapter ends with a colophon ("Fue escrita en Corinto para los romanos, enviada por medio de Febe, servidora de la iglesia de Cencrea") stored as a separate verse-1 row.

## Classification

| Type | Count | Chapters |
|------|-------|----------|
| Hymn/song lines split into separate rows | 1 | D&C 84 |
| Colophon/signature lines as verse-1 | 2 | D&C 102, Romans 16 |
| Cross-book contamination (Obadiah in Amos) | 1 | Amos 9 |
| Biblical quotation fragments as verse-1 | 4 | 2 Cor 6, Heb 1, Heb 2, Heb 8 |
| Missing verse in dump | 1 | Joel 1 |
| Legitimate textual difference | 1 | 3 John 1 |

## Recommended Fix

Run the ES scrape from the official site (`--lang spa`) to replace the MySQL dump data with clean, authoritative text. This will resolve all 9 buggy cases and confirm the 1 legitimate difference (3 John).
