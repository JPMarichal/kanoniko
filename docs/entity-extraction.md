# Entity Extraction

Hybrid NER pipeline combining curated gazetteers, spaCy models, and contextual phrase matching for bilingual entity detection.

## Extraction Pipeline

For each text chunk, the extractor runs four passes in sequence:

### Pass 1 — Gazetteer Regex (Primary)
A single pre-compiled regex matches all ~2,400 gazetteer terms in one O(n) scan. Terms are sorted by length descending so "Mary Magdalene" matches before "Mary". Results map to canonical entity names and types.

### Pass 1b — Contextual Phrases (Stopword Entities)
Short terms that collide with common words (On, Put, So, No) are excluded from the main regex. Instead, they are matched via contextual phrase patterns specific to each entity:
- `"priest of On"` → On (place, Heliopolis)
- `"Put, and Canaan"` → Phut (person, son of Ham)
- `"So king of Egypt"` → So (person)
- `"populous No"` → No (place, Thebes/No-Amon)

### Pass 1c — Cross-Language Matching
Stopword collision is language-specific. Terms that are stopwords in English but not in Spanish (e.g., "on", "put", "so") are matched directly via `\b` regex when processing Spanish text — because they don't cause false positives in Spanish. The reverse applies for Spanish stopwords in English text.

### Pass 2 — spaCy NER (Auto-Discovery)
spaCy models (`en_core_web_sm`, `es_core_news_sm`) detect entities not in the gazetteer. Results are filtered:
- Must not overlap with gazetteer matches
- Must pass the KJV archaic verb filter
- Must have a mappable entity type (PERSON, GPE, LOC, ORG, etc.)

#### KJV Archaic Verb Filter
spaCy sometimes creates false entities from KJV English constructions like "Mary hath" or "Jacob begat Judas". A regex filter excludes any NER result containing archaic verbs:
```
hath|begat|saith|spake|smote|doth|shalt|wilt|cometh|goeth|maketh|taketh|dwelt
```

### Pass 3 — Scripture Citation Regex
Detects inline scripture references (e.g., "see Matthew 5:3") and creates `scripture` type entities.

### Pass 4 — Co-occurrence Relations
Entities found in the same chunk are linked with `RELATED_TO` relations. The relation type is inferred from co-occurrence proximity.

## Stopword Handling Architecture

```
                    ┌── Main regex (2,400+ terms)
                    │
Text ──→ Language ──┼── Contextual phrases (On, Put, So, No)
         detection  │
                    ├── Cross-language matching
                    │   (EN stopwords OK in ES text, and vice versa)
                    │
                    └── spaCy NER (auto-discovery)
```

### Stopword Sets

**English-only stopwords** (excluded from EN text, OK in ES):
`on, so, put, set, ye, he, be, by, do, go, if, is, it, me, my, of, or, to, up, us, we, am, an, as, at, in, no`

**Spanish-only stopwords** (excluded from ES text, OK in EN):
`ha, yo, es, en, al, el, la, lo, un, si, ni, ya`

**Shared** (excluded in both): `no, an, as`

## Key Class

`KGExtractor` (`knowledge/extractor.py`):
- `extract(text, source_file)` → `ExtractionResult` (entities, relations, scripture_refs)
- `_build_lookup()` — Gazetteer alias → canonical name mapping
- `_compile_gazetteer_regex()` — Single compiled regex for all terms
- `_build_lang_specific_lookup()` — Cross-language stopword lookups
- `_extract_ner()` — spaCy NER with filtering
