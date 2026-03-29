# Entity Profiles

Persistent knowledge layer that accumulates metadata and LLM-generated bilingual summaries per entity.

## Overview

Entity profiles survive KG rebuilds (which clear Neo4j) because they live in SQLite. They serve two purposes:
1. **Metadata aggregation**: Mention counts, document counts, books, key passages, aliases
2. **LLM-generated knowledge**: Bilingual summaries (EN/ES) and disambiguation of ambiguous entities

## Two-Phase Generation

### Phase 1 — Metadata (computational, $0)

`POST /index/build-profiles {"phase": "metadata"}`

Aggregates data from Neo4j entity mentions and SQLite chunk text:
- Counts mentions and documents per entity
- Extracts key passages with **volume-diverse selection** (round-robin across OT, NT, BoM, D&C, PGP, conference, etc.)
- Collects aliases from gazetteers and Neo4j
- Lists books where entity appears

### Phase 2 — Generate (LLM, ~$0.05/200 entities)

`POST /index/build-profiles {"phase": "generate"}`

Sends key passages to LLM (fast tier) for each entity and receives:
- `summary_en`: 2-3 sentence English description
- `summary_es`: 2-3 sentence Spanish translation
- `disambiguation`: If the name refers to multiple individuals, a list of distinct variants

## Disambiguation

When the LLM detects that a name (e.g., "Judas", "Mary", "James") refers to multiple distinct individuals, it returns a disambiguation list. Each variant gets:
- `preferred_name`: Most recognizable name (e.g., "Judas Iscariot", not "Lebbaeus")
- `id`: Disambiguator slug
- `summary_en`, `summary_es`: Per-variant bilingual summaries

The system then splits the original profile into multiple profiles, one per variant.

### Disambiguation Results (examples)
- **Judas** → 7 variants: Judas Iscariot, Judas of Galilee, Judas Barsabas, Judas (not Iscariot), Judas the brother of James, Judas (son of Jacob), Judas Maccabeus
- **James** → 8+ variants: James the son of Zebedee, James the son of Alphaeus, James the brother of Jesus, etc.
- **Mary** → Multiple: Mary mother of Jesus, Mary Magdalene, Mary sister of Martha, etc.

## Volume-Diverse Passage Selection

Key passages are selected using round-robin across corpus volumes to ensure broad coverage:

```
Candidates grouped by volume:
  OT: [Isaiah 2:3, Psalms 76:2, ...]
  NT: [Hebrews 12:22, 1 Peter 2:6, ...]
  BoM: [1 Nephi 13:37, ...]
  D&C: [D&C 97:21, D&C 101:5, ...]
  PGP: [Moses 7:18, ...]

Round-robin: 1 from each, then 1 more from each, until max_passages reached
```

This ensures concepts like "Zion" include perspectives from all five standard works, not just the Old Testament.

## Profile Lifecycle

```
           metadata          generate           corpus change
    ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
    │  (new entity) │──→│   metadata   │──→│     profiled     │
    └──────────────┘   └──────────────┘   └────────┬─────────┘
                                                    │
                                              corpus changes
                                                    │
                                          ┌─────────▼─────────┐
                                          │      stale        │
                                          └───────────────────┘
```

- **metadata**: Has counts and passages, no LLM summaries
- **profiled**: Has LLM-generated summaries
- **stale**: Was profiled, but corpus changed — needs re-generation

## Orphan Cleanup

When `build_metadata_profiles` runs, it deletes profiles for entities that no longer exist in Neo4j. This handles cases where a KG rebuild removes entities that were previously profiled.

## Storage

SQLite table `entity_profiles`:
```sql
entity_name, entity_type (PRIMARY KEY)
mention_count, document_count
books (JSON), key_passages (JSON), aliases (JSON)
disambiguator, summary_en, summary_es, disambiguation_notes
profile_version, status
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET /search/graph/profile/{name}` | Single entity profile |
| `GET /search/graph/profiles` | List with filters (type, status, search, min_mentions) |
| `POST /index/build-profiles` | Build profiles (metadata or generate phase) |

### Targeted Generation

Process specific entities by name:
```
POST /index/build-profiles
{"phase": "generate", "entity_names": ["Judas", "Zion"]}
```

## Key Classes

- `ProfileStore` (`profile_store.py`): SQLite CRUD
- `ProfileGenerator` (`profile_generator.py`): LLM-powered generation
- `EntityProfile` (dataclass): Profile data model
