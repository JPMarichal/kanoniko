# Semantic Search (Qdrant)

Vector similarity search using multilingual sentence embeddings.

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
2. Vectors are stored in Qdrant with metadata (file_path, chunk_index, text)
3. At query time, the query is encoded with the same model
4. Qdrant returns the most similar vectors by cosine similarity
5. Results are mapped back to chunk text and metadata

## Qdrant Collection

- **Collection name**: `alejandria`
- **Vector size**: 384
- **Distance metric**: Cosine similarity
- **Payload**: file_path, chunk_index, text, metadata, reference

## Usage

```python
from alejandria.embeddings.model import encode_single
from alejandria.search.semantic import SemanticSearch

sem = SemanticSearch()
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

Semantic search is **optional**. If Qdrant is unavailable or `sentence-transformers` is not installed, the system continues to work with textual search only. The health endpoint reports `semantic_available: false`.

## Key Classes

- `SemanticSearch` (`search/semantic.py`): Qdrant client wrapper
- `get_model()`, `encode()`, `encode_single()` (`embeddings/model.py`): Embedding model singleton
