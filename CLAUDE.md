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
- **Relations:** mentions, defines, contradicts, themes (more to be discovered as corpus is explored)

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

## SSL/Corporate Proxy Note

The Dockerfile expects `docker/ca-certificates.crt` with your corporate CA certs for model downloads.
Generate it: `python docker/export_certs.py` (or export from Windows cert store).
This file is gitignored — each dev machine generates its own.
