# API Reference

REST API served on port 4300 (configurable via `ALEJANDRIA_PORT`).

## Health

### `GET /health`
System health check with component status.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "fts_documents": 1821,
  "fts_chunks": 9348,
  "semantic_available": true,
  "semantic_vectors": 9348,
  "graph_available": true,
  "graph_nodes": 9348
}
```

---

## Search

### `POST /search/text`
Full-text search (BM25).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | string | *required* | Search query |
| `limit` | int | 20 | Max results (1-100) |
| `source_filter` | string | null | Corpus subdirectory filter |

### `POST /search/semantic`
Semantic (embedding) search.

Same parameters as `/search/text`.

### `POST /search/hybrid`
Combined text + semantic search with RRF.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | string | *required* | Search query |
| `limit` | int | 20 | Max results |
| `source_filter` | string | null | Corpus filter |
| `text_weight` | float | 0.4 | BM25 weight (0-1) |
| `semantic_weight` | float | 0.6 | Semantic weight (0-1) |

---

## Knowledge Graph

### `POST /search/graph/find`
Search entities by name.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | string | *required* | Entity name (partial match) |
| `entity_type` | string | null | Filter: person, place, concept, etc. |
| `limit` | int | 20 | Max results |

### `POST /search/graph/neighbors`
Get connected entities and relationships.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | *required* | Exact entity name |
| `depth` | int | 1 | Traversal depth (max 5) |
| `limit` | int | 50 | Max results |

### `POST /search/graph/pagerank`
Personalized PageRank (PPR) over the knowledge graph.

Experimental endpoint for multi-hop entity retrieval. Returns entities ranked by graph proximity to the query seeds.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query_entities` | list[string] | *required* | Entity names to use as PPR seeds |
| `alpha` | float | 0.5 | Damping factor (0-1) |
| `top_k` | int | 20 | Max results |

**Response:**
```json
{
  "results": [
    {
      "entity_id": 123,
      "name": "Nephi",
      "entity_type": "person",
      "pagerank_score": 0.42,
      "chunk_count": 15
    }
  ],
  "count": 10
}
```

### `GET /search/graph/summary`
Graph statistics (node/relationship counts by type).

### `GET /search/graph/docs/{entity_name}`
Documents that mention an entity.

### `GET /search/graph/profile/{entity_name}`
Single entity profile.

**Query params:** `entity_type` (optional)

### `GET /search/graph/profiles`
List entity profiles with filters.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `entity_type` | string | null | Filter by type |
| `status` | string | null | Filter: metadata, profiled, stale |
| `min_mentions` | int | 0 | Minimum mention count |
| `limit` | int | 50 | Max results |
| `offset` | int | 0 | Pagination offset |
| `search` | string | null | Name search (partial match) |

---

## Chat (RAG)

### `POST /chat`
Ask a question and get a RAG-powered answer.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `question` | string | *required* | User question |
| `source_filter` | string | null | Corpus filter |
| `provider` | string | null | LLM provider override |
| `model` | string | null | Model override |
| `tier` | string | null | Tier override: fast, balanced, quality |
| `graph_mode` | string | `auto` | Graph mode: `auto`, `vector_only`, `ppr`, `hybrid` |

**`graph_mode` behavior:**
- `auto`: uses PPR expansion when 2+ entities are detected in the question; otherwise vector-only.
- `vector_only`: skips graph expansion entirely.
- `ppr`: forces PPR expansion on extracted entities.
- `hybrid`: combines vector search with PPR-expanded chunks.

**Response:**
```json
{
  "answer": "...",
  "sources": [
    {"text": "...", "file_path": "...", "chunk_index": 0, "score": 0.95, "mode": "hybrid", "reference": "Genesis 1:1-5"}
  ],
  "graph_context": "Knowledge Graph:\n- ...",
  "model": "gemini-2.5-flash",
  "tier": "balanced",
  "input_tokens": 3500,
  "output_tokens": 800
}
```

### `GET /chat/models`
List available models, tiers, and costs.

### `POST /chat/classify`
Preview question complexity classification without running the full pipeline.

### `POST /chat/compare`
A/B comparison of two LLM providers on the same question.

---

## Indexing

### `POST /index/trigger`
Run incremental indexing.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `full_reindex` | bool | false | Drop all indices and rebuild |

### `POST /index/ingest`
Index specific files or directories without scanning the full corpus. Much faster than `/trigger` for small additions.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `paths` | list[str] | (required) | Corpus-relative paths (files or dirs), e.g. `["en/proclamations/"]` |
| `skip_backup` | bool | false | Skip pre-index backup for small additions |

### `GET /index/status`
Current index state, document counts, and errors.

### `POST /index/rebuild-kg`
Rebuild the entire knowledge graph from existing chunks. Takes ~15 minutes for the full corpus.

### `POST /index/build-profiles`
Build entity profiles.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `phase` | string | "metadata" | `metadata` (computational) or `generate` (LLM) |
| `entity_types` | list | null | Filter: `["person"]`, `["place","concept"]`, etc. |
| `max_entities` | int | 0 | Max entities (0 = all) |
| `force` | bool | false | Force regeneration of already-profiled entities |
| `entity_names` | list | null | Process specific entities by name |

---

## Documents

### `GET /documents`
List all indexed files with metadata.
