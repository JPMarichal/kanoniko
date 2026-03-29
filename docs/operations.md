# Operations Guide

Common operational workflows for maintaining the Alejandria knowledge engine.

## Initial Setup

After first deployment:

```bash
# 1. Start services
cd docker && docker compose up --build -d

# 2. Run initial indexing (parses corpus, builds FTS + embeddings)
curl -X POST http://localhost:4300/index/trigger -H "Content-Type: application/json" -d '{"full_reindex": true}'

# 3. Build knowledge graph (~15 min for full corpus)
curl -X POST http://localhost:4300/index/rebuild-kg

# 4. Build entity profiles — metadata phase
curl -X POST http://localhost:4300/index/build-profiles -H "Content-Type: application/json" -d '{"phase": "metadata"}'

# 5. Build entity profiles — generate phase (requires LLM API key)
curl -X POST http://localhost:4300/index/build-profiles -H "Content-Type: application/json" -d '{"phase": "generate", "max_entities": 500}'
```

## Adding New Corpus Content

1. Place files in the appropriate `corpus/{lang}/...` directory
2. Trigger incremental indexing:
   ```bash
   curl -X POST http://localhost:4300/index/trigger
   ```
3. Entity profiles will be marked as `stale` automatically
4. Optionally rebuild KG and regenerate profiles for updated entities

## Knowledge Graph Rebuild

Required after changes to the extractor (gazetteers, NER rules, stopword lists):

```bash
# Full rebuild (~15 min)
curl -X POST http://localhost:4300/index/rebuild-kg

# Then rebuild metadata profiles (cleans orphans, updates counts)
curl -X POST http://localhost:4300/index/build-profiles -H "Content-Type: application/json" -d '{"phase": "metadata"}'
```

## Profile Regeneration

### All entities
```bash
curl -X POST http://localhost:4300/index/build-profiles -H "Content-Type: application/json" \
  -d '{"phase": "generate", "max_entities": 500}'
```

### Specific entities
```bash
curl -X POST http://localhost:4300/index/build-profiles -H "Content-Type: application/json" \
  -d '{"phase": "generate", "entity_names": ["Zion", "Mount Zion", "Judas"]}'
```

### By entity type
```bash
curl -X POST http://localhost:4300/index/build-profiles -H "Content-Type: application/json" \
  -d '{"phase": "generate", "entity_types": ["concept", "place"], "max_entities": 200}'
```

## Monitoring

```bash
# System health
curl http://localhost:4300/health

# Index status and errors
curl http://localhost:4300/index/status

# Graph statistics
curl http://localhost:4300/search/graph/summary

# Profile counts
curl "http://localhost:4300/search/graph/profiles?status=profiled&limit=1"
curl "http://localhost:4300/search/graph/profiles?status=stale&limit=1"
```

## Typical Timings

| Operation | Duration | Notes |
|-----------|----------|-------|
| Incremental indexing (no changes) | ~2s | Hash comparison only |
| Full reindex | ~5 min | Depends on corpus size |
| KG rebuild | ~15 min | Processes all chunks |
| Metadata profiles (all entities) | ~2s | Computational only |
| Generate profiles (200 entities) | ~3 min | LLM calls, ~$0.05 |
| Single chat question | 3-10s | Depends on model tier |
