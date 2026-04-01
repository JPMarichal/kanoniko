# KG Learnings & Tiered Model Selection

## Tiered Model Selection (implemented)
- Three tiers: fast (Flash Lite ~$0.002/q), balanced (2.5 Flash ~$0.004/q), quality (Gemini 3 Flash ~$0.005/q, Haiku fallback ~$0.013/q)
- Heuristic classifier routes questions by complexity — no extra LLM cost
- Internal pipeline calls (query expansion, reranking, entity extraction) always use fast tier
- DeepSeek V3 integrated as quality tier but blocked by corporate firewall at api.deepseek.com — will activate automatically when accessible from another machine
- Fallback chain: if a model fails (connection error, 404), automatically tries next in tier
- Per-provider API keys: anthropic, gemini, deepseek, openai — each independent
- `POST /index/rebuild-kg` endpoint for fast KG-only rebuilds (~13 min for 9,339 chunks with 2,222 persons)

## KG Architecture Learnings

### Gazetteer Bias Problem (critical finding)
- Gazetteer-based extraction has inherent **prejudice**: "Mary" defaults to "Mary (mother of Jesus)" because it's the first match
- Solution: LLM extracts entity names from the question (no gazetteer bias), then KG searches ALL matching entities via `find_node`
- This costs ~$0.0002 per question (fast tier) but eliminates the bias completely

### Disambiguation Challenge (unsolved)
- Same name, different entities: "Judah" = patriarch + tribe + kingdom; "James" = 3+ different people; "Judas" = 6 NT people
- Same entity, different names by language: ES "Judá" ≠ "Judas", but EN "Judah" covers both patriarch and tribe
- Current extractor does pure string matching — cannot distinguish WHICH "Judas" appears in a chunk
- Context needed: book/chapter location, surrounding entities, narrative role
- Long-term solution: spaCy NER + gazetteer + chunk context (book, chapter) for disambiguation

### Entity Coreference / Multiple Names Problem (unsolved — critical for future)
- Many biblical figures have multiple names: Matthew/Levi, Peter/Simon/Cephas, Paul/Saul, Jacob/Israel, Judas/Thaddaeus/Lebbaeus
- Genealogies (Matthew 1, Luke 3) are especially complicated because different name variants are used
- Current gazetteer has `aliases` field — handles simple lookup (alias → canonical name)
- But this is ONE-WAY: if "Leví" appears in text, it maps to "Matthew" — good for search
- Missing: **SAME_AS / ALSO_KNOWN_AS relations** in the KG itself
  - Would allow: search for "Matthew" → also find chunks mentioning "Levi" via graph traversal
  - Would allow: merge relation neighborhoods — Levi's connections + Matthew's connections = one complete picture
  - Enables transitional reasoning: Saul→Paul, Simon→Peter→Cephas
- The KG can potentially **guide** this: if Matthew and Levi are mentioned in the same passage (or same book context), suggest a SAME_AS link
- This intersects with disambiguation: "Levi" is ALSO a tribe name AND other individuals — the SAME_AS must be contextual
- Implementation ideas:
  1. Add ALSO_KNOWN_AS relation type to KG schema
  2. Populate from gazetteer aliases during KG build
  3. During retrieval, when KG finds "Matthew", also follow ALSO_KNOWN_AS edges to find "Levi" documents
  4. Future: LLM-assisted coreference resolution for ambiguous cases

### Scale Problem (discovered)
- Bible alone: ~2,175 named persons, ~700+ places, ~200+ concepts
- Book of Mormon/D&C/PGP add hundreds more
- Conference talks, manuals, commentaries: thousands of modern leaders/authors
- Gazetteer went from 170 → 2,424 entries; KG from 12K → 100K+ relations
- Rebuild time scaled from 4 min → 13 min with larger gazetteer
- Static gazetteers always have gaps — auto-discovery (NER) needed for completeness

### KG-Boosted Retrieval (implemented)
- Pipeline: question → LLM extracts entities → KG finds ALL matching entities → get their documents → FTS within those docs → tag chunks with `[KG: entity_name]` → reranker sees the tag and knows WHY the chunk is relevant
- This solved: Mary of Cleophas (John 19:25), Mary mother of Mark (Acts 12:12) — both single-verse mentions that FTS alone couldn't rank high enough
- Limitation: still depends on KG having the entity. Judas of Galilee, Judas Barsabas not in gazetteer = not found

### Enumeration Query Detection
- "How many X" / "cuántas X" questions need broader recall than normal queries
- System doubles search limit (25→50) and context chunks (12→24) for enumeration queries
- Pattern detected via regex heuristics — no extra LLM cost

### Four LLM Calls Per Question (current pipeline)
1. Query expansion (fast tier) — generates FTS keywords
2. Entity extraction (fast tier) — extracts names for KG search
3. Reranking (fast tier) — selects best chunks from candidate pool
4. Answer generation (auto tier) — generates the final response

Calls 1+2 could potentially be merged into a single LLM call to save one round-trip.

## Data Sources
- `data/gazetteers/bible_persons_bilingual.json` — 2,175 biblical persons with EN/ES names from Theographic + BibleData + Hitchcock's
- `data/gazetteers/theographic_people.csv` — raw source (CC-BY-SA-4.0)
- `data/gazetteers/bibledata_person.csv` — raw source with descriptions
- Places, objects, concepts gazetteers remain manually curated (63/22/74 entries) — future expansion needed
