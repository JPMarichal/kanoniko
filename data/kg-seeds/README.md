# KG Seeds

Pre-defined entities and relations that the KG should know **before** indexing begins.

Seeds encode the research intelligence gathered during corpus preparation. Each JSON file covers
one corpus section and defines:
- **entities**: named nodes to ensure exist (with canonical name, type, aliases)
- **relations**: explicitly typed edges between named entities

Seeds are loaded at the start of every `rebuild_kg` run and every full `run()` pass,
before any NER/gazetteer extraction. This ensures:
1. Entities are discoverable even before any document is indexed
2. Typed relations are asserted from structured knowledge, not co-occurrence inference
3. Research investment is preserved as machine-readable artifacts alongside the corpus

## Schema

```json
{
  "name": "Human-readable name",
  "corpus_pattern": "optional glob matching corpus paths this seed covers",
  "confidence": "curated",
  "entities": [
    { "name": "Canonical Name", "type": "person|place|concept|object|period|work", "aliases": ["..."] }
  ],
  "relations": [
    {
      "subject": "entity name",
      "subject_type": "person|concept|work|...",
      "predicate": "AUTHORED_BY|TAUGHT|PREREQUISITE_FOR|...",
      "object": "entity name",
      "object_type": "person|concept|work|...",
      "source_ref": "Scripture/source note (optional)"
    }
  ]
}
```

## Adding a new seed file

When preparing a new corpus material:
1. Research the content and identify key entities and relations
2. Document them in a Fase 0 file: `proj/P4-corpus-expansion/fase0/{slug}.md`
3. Create a seed file here encoding the machine-readable form of that analysis
4. Run `POST /index/rebuild-kg` to apply seeds + re-extract NER

Seeds are idempotent (Neo4j MERGE) — safe to re-apply on every run.
