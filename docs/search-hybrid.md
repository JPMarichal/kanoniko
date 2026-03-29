# Hybrid Search (Reciprocal Rank Fusion)

Combines textual and semantic search results using Reciprocal Rank Fusion (RRF).

## Overview

Hybrid search leverages the strengths of both search modes:
- **Textual (BM25)**: Precise keyword matching, good for specific terms and names
- **Semantic**: Meaning-based retrieval, good for paraphrased or conceptual queries

RRF merges both ranked lists into a single result set.

## Algorithm

Reciprocal Rank Fusion assigns scores based on rank position rather than raw scores:

```
RRF_score(d) = text_weight / (k + rank_text(d)) + semantic_weight / (k + rank_semantic(d))
```

Where `k = 60` (standard RRF constant), and weights default to 0.4 (text) / 0.6 (semantic).

Documents appearing in both lists get boosted; those in only one list still appear.

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text_weight` | 0.4 | Weight for BM25 results |
| `semantic_weight` | 0.6 | Weight for semantic results |
| `limit` | 20 | Max results after fusion |

## Usage

```python
from alejandria.search.hybrid import reciprocal_rank_fusion

merged = reciprocal_rank_fusion(
    text_results=text_dicts,
    semantic_results=semantic_dicts,
    limit=20,
    text_weight=0.4,
    semantic_weight=0.6,
)
```

## API

```
POST /search/hybrid
{
  "query": "plan of salvation",
  "limit": 20,
  "text_weight": 0.4,
  "semantic_weight": 0.6
}
```

## In the RAG Pipeline

The RAG pipeline uses hybrid search as its primary retrieval strategy, fetching `rag_search_limit` (default 25) candidates from each mode, then fusing them down to `rag_context_chunks` (default 12) for the LLM context.
