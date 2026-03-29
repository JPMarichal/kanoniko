# Scripture References

The system generates verse-level references for every scripture chunk, enabling precise citations in search results and RAG answers.

## How References Are Built

1. Scripture files are detected by path pattern (`*/scriptures/*/*/*.txt`)
2. `build_scripture_metadata()` extracts volume, book, and language from the path
3. `build_chunk_reference()` parses verse numbers from chunk text boundaries
4. References are stored per chunk in SQLite

## Reference Format

### English
```
Genesis 1:1-5
1 Nephi 3:7
D&C 76:22-24
Moses 7:18-19
Articles of Faith 1:10
```

### Spanish
```
Génesis 1:1-5
1 Nefi 3:7
DyC 76:22-24
Moisés 7:18-19
Artículos de Fe 1:10
```

## Book Name Mapping

The system maintains bilingual book name mappings for all standard works:

| English | Spanish | Volume |
|---------|---------|--------|
| Genesis | Génesis | OT |
| Matthew | Mateo | NT |
| 1 Nephi | 1 Nefi | BoM |
| Doctrine and Covenants | Doctrina y Convenios | D&C |
| Moses | Moisés | PGP |

Short forms are also supported:
- `D&C` / `DyC`
- `JS-H` / `JS-H`

## Implementation

- `scripture_meta.py`: `is_scripture()`, `build_scripture_metadata()`, `build_chunk_reference()`
- `cross_references.py`: Scripture citation regex patterns for cross-reference detection in text
