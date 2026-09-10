# Semantic Search (pgvector)

Vector similarity search using multilingual sentence embeddings, stored in Postgres via pgvector
with an HNSW index.

> The `sqlite-vec` implementation was retired with the rest of the SQLite stack (§3.4 of
> `postgres-migration.md`). Qdrant (the Phase-2 store) was consolidated into pgvector — see
> [`vector-db-options.md`](vector-db-options.md). Ground truth: [`system-spec.md`](system-spec.md).

## Embedding model

- **Model:** `paraphrase-multilingual-MiniLM-L12-v2`
- **Dimensions:** 384
- **Languages:** bilingual ES/EN (trained on 50+ languages)
- **Device:** CUDA when available, CPU fallback
- **Singleton:** loaded once, shared across requests (`embeddings/model.py`)
- Downloaded on first container build (~500 MB)
- *(Modernization to BGE-M3 + a TEI serving container is project P11.)*

## How it works

1. During ingestion, each chunk is encoded to a 384-dim vector and upserted into
   `chunk_embeddings` `(chunk_id, embedding vector(384))`.
2. An HNSW index is built by `storage.postgres.schema.ensure_hnsw_index`.
3. At query time the query is encoded with the same model and passed as pgvector text
   (`[v1,v2,…]`, cast `::vector` by psycopg3).
4. pgvector's `<=>` operator (cosine distance) ranks against the HNSW index; score = `1 - distance`.
5. Results JOIN back to `chunks` for text and metadata; optional `source_filter`.

## Usage

```python
from alejandria.embeddings.model import encode_single
from alejandria.search.semantic import SemanticSearch

vec = encode_single("Who baptized Jesus?").tolist()
results = SemanticSearch().search(query_vector=vec, limit=10, source_filter="scriptures")
```

## API

```
POST /search/semantic
{ "query": "Who baptized Jesus?", "limit": 10, "source_filter": "scriptures" }
```

## Graceful degradation

Semantic search is **optional**. If `sentence-transformers` is not installed or the embedding model
can't load, the system runs on textual search alone; `/health` reports `semantic` as unavailable.

## Key modules

- `search/semantic.py` — `SemanticSearchResult`; pgvector `<=>` query; connection via
  `alejandria.storage.postgres.connection.get_connection`.
- `embeddings/model.py` — `get_model()`, `encode()`, `encode_single()` singleton.
