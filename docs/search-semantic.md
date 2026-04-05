# Semantic Search (sqlite-vec)

Vector similarity search using multilingual sentence embeddings, stored in SQLite via the sqlite-vec extension.

## Overview

Semantic search finds passages by meaning rather than keywords. A multilingual embedding model encodes both queries and corpus chunks into 384-dimensional vectors, enabling cross-language similarity matching.

## Embedding Model

- **Model**: `paraphrase-multilingual-MiniLM-L12-v2`
- **Dimensions**: 384
- **Languages**: Bilingual Spanish/English (trained on 50+ languages)
- **Device**: CUDA (GPU) when available, falls back to CPU
- **Singleton**: Model is loaded once and shared across all requests

The model is downloaded on first container build (~500MB).

## How It Works

1. During ingestion, each chunk is encoded into a 384-dim vector
2. Vectors are stored in SQLite via sqlite-vec virtual table (`chunk_vectors`)
3. At query time, the query is encoded with the same model
4. sqlite-vec returns the most similar vectors by cosine distance (brute-force KNN)
5. Results are mapped back to chunk text and metadata

## sqlite-vec Table

- **Table name**: `chunk_vectors`
- **Vector size**: 384 (float32)
- **Distance metric**: Cosine
- **Metadata column**: `source` (filterable in KNN query)
- **Auxiliary columns**: `file_path`, `text_content`, `chunk_index`, `reference` (stored, returned in results)

## Usage

```python
from alejandria.embeddings.model import encode_single
from alejandria.search.semantic import SemanticSearch

sem = SemanticSearch(db_path)
query_vector = encode_single("Who baptized Jesus?").tolist()
results = sem.search(query_vector=query_vector, limit=10, source_filter="scriptures")
```

## API

```
POST /search/semantic
{
  "query": "Who baptized Jesus?",
  "limit": 10,
  "source_filter": "scriptures"
}
```

## Graceful Degradation

Semantic search is **optional**. If sqlite-vec is unavailable or `sentence-transformers` is not installed, the system continues to work with textual search only. The health endpoint reports `semantic_available: false`.

## Key Classes

- `SemanticSearch` (`search/semantic.py`): sqlite-vec wrapper with same interface as former Qdrant client
- `get_model()`, `encode()`, `encode_single()` (`embeddings/model.py`): Embedding model singleton
