# RAG Pipeline

Retrieval-Augmented Generation pipeline that retrieves context from all search modes and generates grounded answers via LLM.

## Pipeline Flow

```
Question
  │
  ├─→ Complexity classification → Tier selection → Model selection
  │
  ├─→ Query expansion (internal LLM call)
  │     └─→ Generates search variants for better retrieval
  │
  ├─→ Retrieval (parallel)
  │     ├─→ Textual search (FTS5/BM25)
  │     ├─→ Semantic search (Qdrant)
  │     └─→ KG entity extraction
  │
  ├─→ Reciprocal Rank Fusion
  │     └─→ Top 12 chunks from merged results
  │
  ├─→ Graph context building
  │     ├─→ Entity profiles (bilingual summaries)
  │     └─→ Graph neighbors (for entities without profiles)
  │
  ├─→ LLM reranking (internal call)
  │     └─→ Reorders chunks by relevance to question
  │
  └─→ Answer generation (tier-appropriate model)
        └─→ Grounded answer with source citations
```

## Four LLM Calls Per Question

1. **Query expansion** (fast tier): Generates search variants
2. **Entity extraction** (fast tier): Identifies entities in the question
3. **Reranking** (fast tier): Reorders retrieved chunks by relevance
4. **Answer generation** (auto/configured tier): Produces the final answer

Calls 1-3 use the cheapest available model; call 4 routes to an appropriate tier based on question complexity.

## Graph Context Enrichment

The graph context sent to the LLM is built in two layers:

### Layer 1 — Entity Profiles
For each entity detected in the question, the system looks up its profile. If an LLM-generated summary exists:
- Selects the summary in the question's language (ES/EN detection via keyword heuristic)
- Includes aliases for cross-reference
- Profiles provide rich, pre-computed context

### Layer 2 — Graph Neighbors (Fallback)
For entities without profile summaries, the system falls back to Neo4j neighbor data:
- Connected entities and their types
- Relationship labels

### Language Detection
```python
lang = "es" if any(
    w in question.lower()
    for w in ("quién", "qué", "cuál", "cómo", "dónde", "cuándo", "cuántos", "por qué")
) else "en"
```

## System Prompt

The LLM receives a system prompt that instructs it to:
- Answer based ONLY on provided context passages
- Respond in the same language as the question
- Acknowledge when context is insufficient
- Weave knowledge graph data naturally into answers
- Organize biographical/chronological information clearly

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `rag_context_chunks` | 12 | Max chunks in final context |
| `rag_search_limit` | 25 | Candidates per search mode |
| `llm_answer_tier` | `auto` | Tier for answer generation |
| `llm_internal_tier` | `fast` | Tier for expansion/reranking |
| `llm_max_tokens` | 2048 | Max output tokens |
| `llm_temperature` | 0.3 | Response temperature |

## Key Class

`RAGPipeline` (`chat/rag.py`):
- `ask(question, source_filter, provider_override, model_override, tier_override)` → `ChatResult`
- `_expand_query()` — Query expansion via LLM
- `_get_graph_context()` — Profile + graph neighbor context
- `_rerank()` — LLM-based reranking
- `_build_context()` — Assembles final prompt context
- `_generate_answer()` — LLM answer generation

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST /chat` | Ask a question, get a grounded answer |
| `POST /chat/classify` | Preview complexity tier without running pipeline |
| `POST /chat/compare` | A/B test two LLM providers |
| `GET /chat/models` | List available models and tiers |
