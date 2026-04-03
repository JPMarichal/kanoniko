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
corpus/{lang}/proclamations/...                          # official FP+Q12 (not canon)
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

## Backup & Disaster Recovery

**SQLite is the source of truth.** From it alone, Qdrant (~5 min) and Neo4j (~3h) can be fully reconstructed.

### Backup Endpoints (API running at :4300)
| Endpoint | What it does |
|----------|-------------|
| `POST /backup/sqlite?label=manual` | Timestamped copy, rotates last 5 |
| `POST /backup/qdrant` | Qdrant native snapshot |
| `POST /backup/neo4j` | Cypher streaming export to JSON (~90s for 75K nodes + 4.5M rels) |
| `GET /backup/sqlite` | List available SQLite backups |
| `GET /backup/neo4j` | List available Neo4j backups |
| `POST /backup/sqlite/restore?filename=...` | Restore SQLite from backup |
| `POST /backup/neo4j/restore?filename=...` | Restore Neo4j from backup (clears graph first) |
| `POST /index/rebuild-vectors` | Rebuild Qdrant from SQLite (no filesystem I/O) |

### Automatic Pre-Index Backup
The pipeline automatically backs up all three stores before any indexing run. No manual action needed.

### What's Tracked in Git (disaster recovery baseline)
| Asset | Location | Notes |
|-------|----------|-------|
| Source code | `src/`, `docker/`, `scripts/` | |
| Corpus | `corpus/` | Bind-mounted, full text in git |
| SQLite DB | `data/sqlite/alejandria.db` (85 MB) | FTS chunks + registry |
| Gazetteers | `data/gazetteers/` | 7 NER assets, hard to rebuild |
| Project memory | `docs/project-memory/` | Primary source — tracked directly in git |
| Skills/hooks | `.claude/` | |
| Secrets | **NOT in git** — backed up to `OneDrive/alejandria-secrets/.env` | |

### Recovery Procedures
- **SQLite lost:** `git checkout data/sqlite/alejandria.db` or restore from backup endpoint
- **Qdrant lost:** `POST /index/rebuild-vectors` (~5 min on GPU)
- **Neo4j lost:** `POST /backup/neo4j/restore?filename=...` or rebuild from SQLite via reindex (~3h)
- **Full disaster:** Clone repo, copy `.env` from OneDrive, `docker compose up`, data is in git
- **NEVER run full reindex casually** — it takes 7+ hours and deletes existing data first. Always use incremental.
- **Incremental is fast** (~2-3 sec/file for new material). Only `force: true` is slow (~2h for 7K files on CPU).
- **`/index/status` ETA underestimates** — it only tracks Phase 1 (parse/FTS). Phases 2+3 (vectors/KG) can add significant time on CPU.

### Memory Sync
Project memory is tracked in git at `docs/project-memory/` — **this is the authoritative source.** See the "Project Memory" section below for the write protocol.

## GPU Docker (Native Docker Engine in Ubuntu WSL)

Two independent Docker engines coexist:
| | Rancher Desktop | Docker Engine nativo (GPU) |
|---|---|---|
| **WSL distro** | `rancher-desktop` | `Ubuntu-20.04` |
| **GPU** | No | NVIDIA runtime (default) |
| **Use** | Regular work (do NOT modify) | Alejandria GPU workloads |

### GPU Stack Management
```bash
# From Windows (all commands go through gpu-up.sh):
wsl -d Ubuntu-20.04 bash -c "bash '/mnt/c/own/alejandria/scripts/gpu-up.sh' up"
wsl -d Ubuntu-20.04 bash -c "bash '/mnt/c/own/alejandria/scripts/gpu-up.sh' down"
wsl -d Ubuntu-20.04 bash -c "bash '/mnt/c/own/alejandria/scripts/gpu-up.sh' status"
```

- Corpus is git-cloned to `/home/jpmarichal/alejandria-repo` on native Linux FS (~250x faster I/O)
- `gpu-up.sh` auto-syncs via `git fetch` + `git reset --hard` before starting
- Compose override: `docker/docker-compose.gpu.yml` + `docker/Dockerfile.gpu`

## Project Memory

**`docs/project-memory/` is the authoritative memory location** — it lives in git and survives machine changes.

### Write protocol (every memory save)

When saving any memory file, **always write to both locations**:

1. `docs/project-memory/{type}_{name}.md` — primary, tracked in git
2. The system memory path shown in the auto-memory prompt at session start (e.g., `~/.claude/projects/.../memory/`) — secondary, for auto-loading this session

Also update both `docs/project-memory/MEMORY.md` and the system `MEMORY.md` index.

> If for any reason only one write is possible, prefer `docs/project-memory/`.

### Read protocol

- Normal session: the system auto-loads `~/.claude/.../memory/MEMORY.md` — no action needed.
- New machine / empty system memory: explicitly read `docs/project-memory/MEMORY.md` to load the full index.

### New machine bootstrap

Run once after cloning to populate the local Claude Code memory dir:

```bash
bash scripts/restore-memory.sh
```

---

## Documentation & Sync Rules

**When modifying any feature, the relevant `docs/*.md` MUST be updated in the same commit.**

Checklist before every commit that changes behavior:
1. Update the relevant `docs/*.md` file (architecture, operations, docker, etc.)
2. If `docs/README.md` index needs a new entry, add it
3. Promoted NER candidates auto-write to `entities.json` (closed feedback loop)

A pre-commit hook (`scripts/pre-commit-sync.sh`) auto-stages gazetteer changes.
Install: `ln -sf ../../scripts/pre-commit-sync.sh .git/hooks/pre-commit`

## SSL/Corporate Proxy Note

The Dockerfile expects `docker/ca-certificates.crt` with your corporate CA certs for model downloads.
Generate it: `python docker/export_certs.py` (or export from Windows cert store).
This file is gitignored — each dev machine generates its own.
