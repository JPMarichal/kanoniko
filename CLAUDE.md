# Alejandría

Bilingual (ES/EN) text library with three search modes: textual (FTS), semantic (embeddings), and knowledge graph.

## Project Context

**Corpus:** LDS Church canonical books (scriptures), general conference talks, biographies, manuals, web page downloads, and broad related literature. Formats: md, txt, html, json.

## Key Decisions

- Independent service with its own git repo — NOT an extension of existing MCPs
- Containerized (Docker) for: auto server startup, isolation from host, CI/CD
- Corpus is NOT containerized — bind-mounted externally, it's the first thing that scales
- Local embedding model: `paraphrase-multilingual-MiniLM-L12-v2` (bilingual ES/EN)
- API port: **4300**
- Interface priority: REST API → MCP adapter → CLI → UI
- Not exclusive to Claude Code — independent REST services, optionally consumed via MCP
- Incremental ingestion via SHA-256 change detection
- A secondary ETL system may handle format conversion/ingestion
- Template systems planned for format standardization

## KG Model

- **Nodes:** concepts, people, characters, places, peoples, objects, periods
- **Relations:** 67 typed relation types across 12 categories (family, governance, prophetic, geographic, temporal, authorship, conflict, spiritual, intertextuality, typology, covenants, dispensational)
- **Confidence tiers:** curated > metadata > llm_high > llm_low > ner > co_occurrence

## Stack

- Python 3.11, FastAPI, SQLite FTS5 (textual), Qdrant (semantic), Neo4j (graph)
- spaCy + domain gazetteers for KG extraction
- Docker Compose (3 containers: api, qdrant, neo4j)

## Vision

The final product is a **specialized chat client for scripture/gospel study** (RAG-based). The knowledge engine (search APIs) is the backend; the chat UI is a future service consuming it.

## Corpus Structure

Bilingual corpus, bind-mounted at `corpus/`:
```
corpus/{lang}/scriptures/{volume}/{book}/{chapter}.txt   # verse-numbered files
corpus/{lang}/general-conference/...
corpus/{lang}/biographies/...
corpus/{lang}/manuals/...
corpus/{lang}/web/...
```

Scripture files have numbered verses: `1 Text of verse one.\n2 Text of verse two.`
The system generates scripture references (e.g., "Matthew 1:25", "1 Nefi 3:7") per chunk.

Download scriptures: `REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_scriptures.py`

## Phases (Completed)

1. ~~Foundation: parsers, chunker, FTS5, incremental indexing, REST API~~
2. ~~Semantic search: Qdrant + multilingual embeddings + hybrid search~~
3. ~~Knowledge graph: Neo4j + gazetteers + relation extraction~~
4. ~~MCP adapter, CLI, polish~~
5. ~~Corpus + RAG: scripture download, verse-level references, chat endpoint, entity profiles, disambiguation, profile-enriched RAG, volume-diverse passage selection, staleness tracking, language-aware stopword filtering~~

Future work is organized as an **incubator of independent projects** — see `docs/roadmap.md`.

## Running

```bash
# Build and run (first time downloads ~500MB embedding model)
cd docker && docker compose up --build

# Run tests
docker run --rm -v ./tests:/app/tests -v ./src:/app/src docker-api bash -c "pip install -q pytest httpx && python -m pytest /app/tests/ -v"
```

## MCP Tools (Preferred)

The Alejandría MCP server (`.mcp.json`) provides native tools — **always prefer these over curl/REST calls:**

| Tool | Use for |
|------|---------|
| `mcp__alejandria__kg_relations` | Typed relations for an entity (family, prophecy, authorship, etc.) |
| `mcp__alejandria__kg_profile` | Rich entity profile (summary, aliases, key passages, themes) |
| `mcp__alejandria__kg_find` | Search entities by partial name |
| `mcp__alejandria__search_hybrid` | Full corpus search (textual + semantic fusion) |
| `mcp__alejandria__search_text` | Exact keyword/phrase search (FTS5) |
| `mcp__alejandria__kg_neighbors` | Graph neighbors and edges |
| `mcp__alejandria__kg_docs` | Documents mentioning an entity |
| `mcp__alejandria__kg_summary` | KG statistics |
| `mcp__alejandria__chat_ask` | Full RAG pipeline (search + KG + rerank + LLM answer) |
| `mcp__alejandria__chat_classify` | Preview question complexity tier |
| `mcp__alejandria__corpus_status` | System health (documents, vectors, graph) |

If MCP tools are unavailable (server not running), fall back to REST API at `http://localhost:4300`.

## Answering Corpus Questions

When the user asks a theological, doctrinal, or scripture-content question:

1. **KG entity lookup** (1-2 calls) — use `mcp__alejandria__kg_relations` or `mcp__alejandria__kg_profile` to get typed relations, key passages, and connected entities. Let the graph reveal structure.
2. **Hybrid search** (2-3 calls) — use `mcp__alejandria__search_hybrid` to discover passages across the full corpus, especially non-canonical sources (conference talks, manuals, biographies) that LLM training may not cover well.
3. **Synthesize** — use your own knowledge to connect, explain, and structure what the corpus surfaced. Your role is to synthesize, not to be the primary source.
4. **Direct file reads** — for exact verse text when precision matters (e.g., FCD format).

**Principle:** The corpus discovers, you synthesize. If the user wanted only LLM knowledge, they wouldn't be using Alejandría. The value of this system is surfacing connections and content beyond what general knowledge provides.

**Never:** launch a generic subagent to exhaustively search the corpus. The MCP tools are surgical — use them directly. Total tool calls for a corpus question should typically be 3-7, not 40+.

## SSL/Corporate Proxy Note

The Dockerfile expects `docker/ca-certificates.crt` with your corporate CA certs for model downloads.
Generate it: `python docker/export_certs.py` (or export from Windows cert store).
This file is gitignored — each dev machine generates its own.
