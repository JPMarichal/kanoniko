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

Phase 6 has been decomposed into an incubator of independent projects. Each represents a distinct initiative with its own scope, goals, and deliverables. Projects are listed in priority order.

---

### P1 — Scripture Structure: Long Chain
**Priority**: Highest — foundational for everything else
**Vision**: Complete the scripture metadata model with the "long chain" hierarchy: volume → division → part → book → pericope → chapter → verse. Currently only the short chain (volume → book → chapter → verse) is implemented. Both chains must coexist — the short chain is practical for everyday use, the long chain captures the full editorial structure.
**Scope**:
- Divisions (e.g., Pentateuch, Historical Books, Prophets, Gospels, Pauline Epistles)
- Parts (e.g., 1 Samuel / 2 Samuel as parts of "Samuel")
- Pericopae (titled passage units within chapters, e.g., "The Sermon on the Mount", "The Parable of the Sower")
- Metadata per chunk linking to both chains
- Bilingual pericope/division names (EN/ES)
- Enables structured navigation, thematic grouping, and richer search facets

### P2 — Scripture Refresh Pipeline
**Priority**: High — keeps the corpus authoritative and current
**Vision**: Automated pipeline to download and refresh scriptures from the official Church site, detecting changes and updating the corpus incrementally.
**Scope**:
- Scheduled or on-demand refresh from churchofjesuschrist.org content API
- Diff detection against current corpus files
- Language-aware download (EN/ES, extensible to other languages)
- Respect rate limits and site policies
- Integration with the existing ingestion pipeline (auto-reindex changed files)
- Currently `scripts/download_scriptures.py` exists but is manual and one-shot

### P3 — ETL Templates
**Priority**: High — unlocks corpus expansion
**Vision**: Standardized format conversion and ingestion templates for new corpus material types.
**Scope**: Template system for conference talks, manuals, institute materials, CES content. Format normalization, metadata extraction, quality validation.

### P4 — Corpus Expansion
**Priority**: High — depends on P3 (ETL Templates)
**Vision**: Grow the corpus beyond current scriptures and conference talks.
**Scope**: Church magazines (Ensign, Liahona), institute manuals, CES materials, historical documents, additional web sources. Per-material-type architecture decisions.

### P5 — Chat Client UI
**Priority**: Medium — the user-facing product, but the backend must be solid first
**Vision**: Specialized web-based chat interface for scripture/gospel study, consuming the Alejandria REST API. The final user-facing product.
**Scope**: Frontend application (separate service/repo), conversation history, source display, entity exploration, bilingual UI.

### P6 — Advanced Relations
**Priority**: Medium — enriches the knowledge graph significantly
**Vision**: Move beyond co-occurrence to meaningful, typed relationships.
**Scope**: Three layers of scripture parallelism (direct references, editorial cross-references, thematic connections). Causal, chronological, and doctrinal relations. NER→gazetteer feedback loop where the KG discovers new entities and retrofeeds the gazetteer.

### P7 — Deep Disambiguation
**Priority**: Medium — improves accuracy of existing features
**Vision**: Context-aware entity disambiguation at the passage level.
**Scope**: Determine which "Mary" or "Judas" is meant in each specific verse, not just at the profile level. Contextual clues (location, companions, time period) for per-mention resolution.

### P8 — Synthesis Engine
**Priority**: Lower — builds on everything above
**Vision**: Knowledge generation beyond Q&A — producing structured artifacts from the corpus.
**Scope**: Endpoints for generating discourses, T-charts, timelines, concept maps, articles, comparative analyses. The 4th layer of the architecture (corpus→index→knowledge→synthesis).

### P9 — Fine-Tuning
**Priority**: Lower — optimization after core features stabilize
**Vision**: Domain-specific model optimization for scripture/gospel content.
**Scope**: Prompt optimization, evaluation benchmarks, potential fine-tuning of embedding or language models on LDS corpus.

---

## Known Issues (Backlog)

- **On disambiguation**: On (city/Heliopolis) vs On (son of Pelet) — gazetteer needs both entries
- **"Daughter" gazetteer noise**: Multiple "Daughter of X" entries cause false matches on the word "daughter"
- **KG relation quality**: EXISTS_DURING relations contain garbage periods ("God. 17", "Jun. 38")
- **Duplicate people profiles**: "House of Judah" and "the house of Judah" exist as separate entities
- **Co-occurrence noise in conference talks**: spaCy NER creates BELONGS_TO relations with garbage targets (URLs, scripture refs as person, "Brethren", "Gospel Library"). Needs a cleanup pass or NER filter for conference source files
- **Conference speaker dedup**: 1,156 speaker names may duplicate existing gazetteer persons (e.g., "Russell M Nelson" vs "Russell M. Nelson")
- **Project-scoped MCP server**: `.mcp.json` at project root is not being loaded by Claude Code — currently workaround is adding to `~/.claude.json` (user-level). Investigate why project-scoped MCP is ignored (approval flow? format issue?) and fix so the MCP config stays self-contained in the repo
