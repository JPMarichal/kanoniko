# Ingestion Pipeline

The ingestion pipeline scans the corpus, detects changes, parses files, creates chunks, and indexes them across all three search backends.

## Pipeline Flow

```
Corpus scan → Change detection (SHA-256) → Parse → Chunk → Index
                                                         ├── SQLite FTS5
                                                         ├── Qdrant (embeddings)
                                                         └── Neo4j (KG extraction)
```

## Incremental Indexing

The `DocumentRegistry` (SQLite) tracks every file with its SHA-256 hash. On each indexing run:

1. **Scan** corpus directory for all supported files
2. **Compare** current hash vs. registry hash
3. **Skip** unchanged files
4. **Re-index** modified files (delete old data, re-ingest)
5. **Remove** deleted files from all indices
6. **Mark profiles stale** if any changes occurred

This enables efficient incremental updates — only changed files are reprocessed.

## Parsing

`parsers.py` handles format-specific text extraction:
- **TXT**: Read as-is
- **MD**: Strip markdown formatting
- **HTML**: Strip tags, extract text content
- **JSON**: Extract text fields

## Chunking

Two chunking strategies:

### Standard Chunking (`chunk_text`)
- Target: 500 words per chunk, 50-word overlap
- Splits on sentence boundaries when possible
- Used for non-scripture content

### Scripture-Aware Chunking (`chunk_scripture`)
- Respects verse boundaries — never splits mid-verse
- Target: 150 words, max 300 words
- Each chunk tracks start/end verse numbers
- Generates scripture references (e.g., "Genesis 1:1-5")

## KG Extraction During Ingestion

For each chunk, the `KGExtractor` runs:
1. Gazetteer regex matching (2,400+ terms in single compiled regex)
2. Contextual phrase matching for stopword-colliding entities
3. Cross-language matching for bilingual stopword handling
4. spaCy NER for auto-discovery of unknown entities
5. Co-occurrence relation inference
6. Results stored as Neo4j nodes and edges

## Profile Staleness

After any indexing run that modifies files, all entity profiles with status `profiled` are marked as `stale`. This signals that their metadata (mention counts, passages) may be outdated and should be regenerated.

## Key Classes

- `IngestionPipeline` (`pipeline.py`): Main orchestrator
  - `run(full_reindex=False)` — Incremental or full indexing
  - `rebuild_kg()` — Clear and rebuild entire knowledge graph
  - `build_metadata_profiles()` — Phase 1 profile generation
- `DocumentRegistry` (`registry.py`): File tracking with SHA-256
- `chunk_text()`, `chunk_scripture()` (`chunker.py`): Chunking strategies

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST /index/trigger` | Run incremental indexing |
| `GET /index/status` | Current index state and errors |
| `POST /index/rebuild-kg` | Rebuild knowledge graph from chunks |
| `POST /index/build-profiles` | Build entity profiles |
