# Roadmap

## Completed Phases

### Phase 1 — Foundation
Parsers (md, txt, html, json), text chunker, SQLite FTS5 with BM25, incremental indexing via SHA-256 change detection, REST API with FastAPI.

### Phase 2 — Semantic Search
Qdrant vector database, multilingual embeddings (`paraphrase-multilingual-MiniLM-L12-v2`), hybrid search with Reciprocal Rank Fusion.

### Phase 3 — Knowledge Graph
Neo4j graph database, curated gazetteers (2,400+ terms), spaCy NER auto-discovery, co-occurrence relation extraction, document-entity linkage.

### Phase 4 — Interfaces
MCP server adapter for AI assistants, Click CLI with search/graph/system commands, API polish and documentation.

### Phase 5 — Corpus + RAG
Scripture download pipeline (bilingual EN/ES), verse-aware chunking with scripture references, RAG chat endpoint with multi-provider LLM support (Anthropic, Gemini, OpenAI, DeepSeek), tiered model selection (fast/balanced/quality), entity profiles with two-phase generation (metadata + LLM), LLM-powered disambiguation (Judas→7 variants, James→8+, Mary→multiple), volume-diverse passage selection (round-robin across OT/NT/BoM/D&C/PGP), profile-enriched RAG context with bilingual summaries, automatic staleness tracking and orphan cleanup, language-aware stopword filtering with contextual phrase matching.

---

## Project Incubator

Phase 6 has been decomposed into an incubator of independent projects. Each represents a distinct initiative with its own scope, goals, and deliverables.

### Project: Chat Client UI
**Vision**: Specialized web-based chat interface for scripture/gospel study, consuming the Alejandria REST API. The final user-facing product.
**Scope**: Frontend application (separate service/repo), conversation history, source display, entity exploration, bilingual UI.

### Project: ETL Templates
**Vision**: Standardized format conversion and ingestion templates for new corpus material types.
**Scope**: Template system for conference talks, manuals, institute materials, CES content. Format normalization, metadata extraction, quality validation.

### Project: Corpus Expansion
**Vision**: Grow the corpus beyond current scriptures and conference talks.
**Scope**: Church magazines (Ensign, Liahona), institute manuals, CES materials, historical documents, additional web sources. Per-material-type architecture decisions.

### Project: Advanced Relations
**Vision**: Move beyond co-occurrence to meaningful, typed relationships.
**Scope**: Three layers of scripture parallelism (direct references, editorial cross-references, thematic connections). Causal, chronological, and doctrinal relations. NER→gazetteer feedback loop where the KG discovers new entities and retrofeeds the gazetteer.

### Project: Deep Disambiguation
**Vision**: Context-aware entity disambiguation at the passage level.
**Scope**: Determine which "Mary" or "Judas" is meant in each specific verse, not just at the profile level. Contextual clues (location, companions, time period) for per-mention resolution.

### Project: Synthesis Engine
**Vision**: Knowledge generation beyond Q&A — producing structured artifacts from the corpus.
**Scope**: Endpoints for generating discourses, T-charts, timelines, concept maps, articles, comparative analyses. The 4th layer of the architecture (corpus→index→knowledge→synthesis).

### Project: Fine-Tuning
**Vision**: Domain-specific model optimization for scripture/gospel content.
**Scope**: Prompt optimization, evaluation benchmarks, potential fine-tuning of embedding or language models on LDS corpus.

---

## Known Issues (Backlog)

- **On disambiguation**: On (city/Heliopolis) vs On (son of Pelet) — gazetteer needs both entries
- **"Daughter" gazetteer noise**: Multiple "Daughter of X" entries cause false matches on the word "daughter"
- **KG relation quality**: EXISTS_DURING relations contain garbage periods ("God. 17", "Jun. 38")
- **Duplicate people profiles**: "House of Judah" and "the house of Judah" exist as separate entities
