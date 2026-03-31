---
name: corpus
description: Search the Alejandría corpus for scripture passages, doctrinal concepts, and entity relationships. Use when the user asks theological, doctrinal, or scripture-content questions.
---

# Corpus Query Strategy

When answering questions about scriptures, doctrine, or gospel topics, follow this workflow:

## Step 1: KG Entity Lookup (1-2 calls)
Use `mcp__alejandria__kg_relations` or `mcp__alejandria__kg_profile` to get:
- Typed relations (family, prophecy, authorship, geography, etc.)
- Entity summary and key passages
- Connected entities and their roles

## Step 2: Hybrid Search (2-3 calls)
Use `mcp__alejandria__search_hybrid` to discover:
- Relevant passages across the full corpus
- Non-canonical sources (conference talks, manuals, biographies)
- Cross-language results (ES/EN)

## Step 3: Synthesize
- Use your own knowledge to connect and explain what the corpus surfaced
- The corpus discovers, you synthesize
- Always cite the sources with their references

## Corpus Structure
```
corpus/{lang}/scriptures/{volume}/{book}/{chapter}.txt
corpus/{lang}/general-conference/...
corpus/{lang}/biographies/...
corpus/{lang}/manuals/...
corpus/{lang}/web/...
```

Volumes: ot (Old Testament), nt (New Testament), bom (Book of Mormon), dc (D&C), pgp (Pearl of Great Price)

## Available MCP Tools
- `mcp__alejandria__search_hybrid` — Full corpus search (textual + semantic)
- `mcp__alejandria__search_text` — Exact keyword/phrase search
- `mcp__alejandria__kg_find` — Search entities by name
- `mcp__alejandria__kg_relations` — Get typed relations for an entity
- `mcp__alejandria__kg_profile` — Get rich entity profile
- `mcp__alejandria__kg_neighbors` — Graph neighbors
- `mcp__alejandria__kg_docs` — Documents mentioning an entity
- `mcp__alejandria__chat_ask` — Full RAG pipeline (search + KG + LLM answer)

## Principle
Total tool calls for a corpus question should be 3-7, not 40+. The KG and search APIs are surgical tools — use them directly.
