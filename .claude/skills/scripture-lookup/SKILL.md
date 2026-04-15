---
name: scripture-lookup
description: Look up scripture passages directly from the corpus by reference (e.g., "Marcos 9:21", "3 Nefi 17:7", "DyC 76:22-24"). Returns verse text formatted in FCD.
user_invocable: true
trigger: /scripture
---

# Scripture Lookup

Given one or more scripture references, read the verse text directly from the corpus files and return it formatted in FCD (Formato de Citas para Dilton).

## Input

One or more references in standard format:
- `Marcos 9:21` or `Mark 9:21`
- `3 Nefi 17:7-10` or `3 Nephi 17:7-10`
- `DyC 76:22-24` or `D&C 76:22-24`
- `Génesis 1:1-3` or `Genesis 1:1-3`
- `Moisés 7:18` or `Moses 7:18`

Multiple references separated by `;` — e.g., `Marcos 9:21; Juan 21:5; 3 Nefi 17:7`

## Language Rules

- Detect the language of the reference: Spanish book names → read from `corpus/es/`, English → `corpus/en/`
- If the conversation is in Spanish but the reference uses English names, still read from the English corpus but present the output in Spanish FCD format
- Follow the language consistency rule: if the conversation is in Spanish, output the Spanish version if available; otherwise translate

## Reference Resolution

### Step 1: Parse the reference

Extract: book name, chapter number, verse start, verse end (optional).

### Step 2: Map book name to corpus path

Use the book registry from `src/alejandria/ingestion/scripture_meta.py`. The mapping (display name → slug → path):

**Volumes and paths:**

| Volume | ES path | EN path |
|--------|---------|---------|
| Old Testament | `corpus/es/scriptures/ot/{book-slug}/{chapter}.txt` | `corpus/en/scriptures/ot/{book-slug}/{chapter}.txt` |
| New Testament | `corpus/es/scriptures/nt/{book-slug}/{chapter}.txt` | `corpus/en/scriptures/nt/{book-slug}/{chapter}.txt` |
| Book of Mormon | `corpus/es/scriptures/bom/{book-slug}/{chapter}.txt` | `corpus/en/scriptures/bom/{book-slug}/{chapter}.txt` |
| D&C | `corpus/es/scriptures/dc/secciones/{section}.txt` | `corpus/en/scriptures/dc/sections/{section}.txt` |
| Pearl of Great Price | `corpus/es/scriptures/pgp/{book-slug}/{chapter}.txt` | `corpus/en/scriptures/pgp/{book-slug}/{chapter}.txt` |

**Common book name → slug mappings (ES → slug):**

| Display name (ES) | Slug | Volume |
|---|---|---|
| Génesis | genesis | ot |
| Éxodo | exodus | ot |
| Salmos | psalms | ot |
| Isaías | isaiah | ot |
| Mateo | matthew | nt |
| Marcos | mark | nt |
| Lucas | luke | nt |
| Juan | john | nt |
| Hechos | acts | nt |
| Romanos | romans | nt |
| Hebreos | hebrews | nt |
| Santiago | james | nt |
| Apocalipsis | revelation | nt |
| 1 Nefi | 1-nephi | bom |
| 2 Nefi | 2-nephi | bom |
| Mosíah | mosiah | bom |
| Alma | alma | bom |
| Helamán | helaman | bom |
| 3 Nefi | 3-nephi | bom |
| 4 Nefi | 4-nephi | bom |
| Mormón | mormon | bom |
| Éter | ether | bom |
| Moroni | moroni | bom |
| DyC | dc (special) | dc |
| Moisés | moses | pgp |
| Abraham | abraham | pgp |
| Artículos de Fe | articles-of-faith | pgp |

For the complete registry of all 80+ books, see `src/alejandria/ingestion/scripture_meta.py`.

**EN display names** use the same slugs: Matthew→matthew, Mark→mark, Genesis→genesis, D&C→dc, etc.

### Step 3: Read the file

Use the Read tool to read the chapter file. Verse format in files: each line starts with the verse number followed by a space:

```
1 En el principio creó Dios los cielos y la tierra.
2 Y la tierra estaba desordenada y vacía...
```

### Step 4: Extract the requested verses

- Single verse (e.g., `9:21`): extract line starting with `21 `
- Verse range (e.g., `17:7-10`): extract lines starting with `7 `, `8 `, `9 `, `10 `
- Whole chapter (e.g., `Salmos 23`): extract all numbered lines

## Output Format (FCD)

### Single verse — inline format:

> "Y Jesús preguntó al padre: ¿Cuánto tiempo hace que le sucede esto? Y él dijo: Desde niño." (Marcos 9:21)

### Multiple verses — outline (block) format:

> Y Jesús preguntó al padre: ¿Cuánto tiempo hace que le sucede esto? Y él dijo: Desde niño.
> Y muchas veces le echa en el fuego y en el agua, para matarle; pero si puedes hacer algo, ten misericordia de nosotros y ayúdanos. (Marcos 9:21-22)

### Multiple references — one block per reference, separated by blank line:

> "Y Jesús preguntó al padre: ¿Cuánto tiempo hace que le sucede esto? Y él dijo: Desde niño." (Marcos 9:21)

> "Y les dijo: Hijitos, ¿tenéis algo de comer? Le respondieron: No." (Juan 21:5)

## Rules

1. **Always read from the corpus file** — never quote scripture from memory
2. **Verse text must be exact** — copy verbatim from the file, never paraphrase
3. **Strip the verse number** from the output text (the number is metadata, not text)
4. **Reference in parentheses** at the end of the last line, same line — never on a new line
5. **No commentary** unless the user asks for it — the skill outputs scripture text only
6. **If the file doesn't exist**, say so explicitly — never fabricate verse text
