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

## Phases

1. ~~Foundation: parsers, chunker, FTS5, incremental indexing, REST API~~ (done)
2. Semantic search: Qdrant + multilingual embeddings + hybrid search
3. Knowledge graph: Neo4j + spaCy NER + gazetteers + relation extraction
4. MCP adapter, CLI, polish
5. UI, ETL templates, fine-tuning, advanced relations

## Running

```bash
# Build and run
cd docker && docker compose up --build

# Run tests
docker run --rm -v ./tests:/app/tests alejandria-api:dev bash -c "pip install -q pytest httpx && python -m pytest tests/ -v"
```
