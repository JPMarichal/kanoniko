# Alejandría

Bilingual (ES/EN) text library with three search modes: textual (FTS), semantic (embeddings), and knowledge graph.

## Project Context

**Corpus:** LDS Church canonical books (scriptures), general conference talks, biographies, manuals, web page downloads, and broad related literature. Formats: md, txt, html, json.

## Runtime and environment — PODMAN, not Docker

**Alejandría containers run on Podman, NOT on Docker.** Do not mix them with a system-wide Docker engine.

- All repo tooling (`Justfile`, `docker/`, `scripts/`, `docker-compose*.yml`) **invokes the `docker` binary literally**. This works because in this environment `docker` resolves to Podman. **The real engine is Podman.**
- Do not mix networks, volumes, or containers with another Docker stack on the host.
- Maintenance commands assume the containers `alejandria-api`, `alejandria-tunnel`, `alejandria-ollama` and the compose network `alejandria_default`.

### Absolute rule for this project

> **Inside `C:\own\alejandria` (and its subdirectories) NEVER run `docker ...` or `docker compose ...`.**
>
> - Use `podman ...` and `podman compose ...` exclusively.
> - Do not run `docker` commands from terminals located in `C:\own\alejandria` or its subdirectories, because on this host `docker` points to Rancher Desktop/Moby and would touch containers from `C:\git`.
> - If a script, `Justfile`, or tool invokes `docker`, verify it is actually operating against Podman. If in doubt, run `docker ps` from `C:\own\alejandria`: if containers from `C:\git` (`web-shim`, `sso-api`, `mysql`, etc.) appear, you are using the wrong engine.
> - This rule applies to everything: development, maintenance, backups, MCPs, scripts, local CI, and any operation within the project.

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

- Python 3.11, FastAPI, Postgres IONOS + pgvector (sole authoritative store: chunks, FTS via tsvector, embeddings, KG).
- spaCy + domain gazetteers for KG extraction
- Docker Compose (1 container: api — Neo4j retired in §3.3, Postgres lives on IONOS VPS)

### Postgres IONOS = source of truth (Phase 1 PR #3; write cutover PR #4; KG read complete PR #5; Neo4j retired §3.3)

**Postgres 16 + pgvector on IONOS VPS is the sole authoritative store**
for chunks, FTS (tsvector), embeddings (pgvector), entities, relations,
and mentions. Both Neo4j (§3.3) and SQLite (§3.4) have been retired.

- **For any destructive op or correctness audit, operate on Postgres IONOS.**
  SSH tunnel `localhost:15432 → 212.227.243.210:5432` should already be
  active in WSL (`pgrep -f "ssh.*15432"`). Credentials in `.env`
  (`ALEJANDRIA_POSTGRES_*`).
- **Connecting from a container:** `podman run --rm --network host -e
  ALEJANDRIA_POSTGRES_HOST=127.0.0.1 -e ALEJANDRIA_POSTGRES_PORT=15432 ...`
  Load env via heredoc (`bash << 'OUTER' ... source .env; ... OUTER`) —
  single `bash -c "..."` quoting can swallow the password.
- **Read parity:** 31/31 golden queries pass against Postgres (PR #5).
  See `tests/parity/`.
- **MCP tools (`mcp__alejandria__*`)** read via the API which proxies to
  Postgres (PR #6 retired the Neo4j proxy). Same data as direct Postgres.
- **Operational infra:** `docs/ionos-setup.md` (VPS setup),
  `docs/postgres-migration.md` (full plan),
  `docs/postgres-migration-status.md` (current state).
- **Vector DB alternatives (Qdrant, Weaviate, Pinecone, Milvus)** analyzed
  in `docs/vector-db-options.md` — pgvector wins at current scale; triggers
  to reconsider documented there.

## Vision

The final product is a **specialized chat client for scripture/gospel study** (RAG-based). The knowledge engine (search APIs) is the backend; the chat UI is a future service consuming it.

**wp_bc** (`C:/own/wp_bc`) es un producto consumidor de Alejandría — usa sus APIs
de búsqueda semántica, textual y KG para enriquecer biografías y contenido
histórico SUD desde un WordPress local. La integración es vía MCP
(`alejandria-search` skill) y REST API, solo para desarrollo local.

## Corpus Structure

Bilingual corpus, bind-mounted at `corpus/`:
```
corpus/{lang}/scriptures/{volume}/{book}/{chapter}.txt   # verse-numbered files
corpus/{lang}/proclamations/...                          # official FP+Q12 (not canon)
corpus/{lang}/general-conference/...
corpus/{lang}/books/...                                  # individual-author books (GA or other)
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
cd docker && podman compose -f docker-compose.yml up --build

# Run tests
podman run --rm -v ./tests:/app/tests -v ./src:/app/src docker-api bash -c "pip install -q pytest httpx && python -m pytest /app/tests/ -v"
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

**Postgres IONOS is the sole source of truth.** Its canonical backup is
the `pg_dump` daily snapshot on the VPS (cron at 03:15 UTC, 14-day
rotation — see `docs/ionos-setup.md`). Post §3.4 there are no local
backup endpoints: the API container is stateless.

### What's Tracked in Git (disaster recovery baseline)
| Asset | Location | Notes |
|-------|----------|-------|
| Source code | `src/`, `docker/`, `scripts/` | |
| Corpus | `corpus/` | Bind-mounted, full text in git |
| Gazetteers | `data/gazetteers/` | 7 NER assets, hard to rebuild |
| Project memory | `docs/project-memory/` | Primary source — tracked directly in git |
| Skills/hooks | `.claude/` | |
| Secrets | **NOT in git** — encrypted (`env.enc`) in GitHub Release | Download via `scripts/backup-pull.sh secrets`, decrypt with `openssl` passphrase |

### Recovery Procedures
- **KG lost:** restore Postgres from the latest IONOS `pg_dump` snapshot.
- **Full disaster:** clone repo, decrypt `.env`, `podman compose up`.
  The API container has no local persistent state; Postgres is
  recovered server-side.
- **Incremental ingest** (`/index/ingest`) is fast (~2-3 sec/file).
  Full reindex is rarely needed and should be done deliberately.
- **`/index/status` ETA underestimates** — it only tracks Phase 1 (parse/FTS);
  Phases 2+3 (embeddings/KG) add time on CPU.

### Memory Sync
Project memory is tracked in git at `docs/project-memory/` — **this is the authoritative source.** See the "Project Memory" section below for the write protocol.

## GPU Podman Desktop — preferred

Alejandría containers run on **Podman Desktop** (`podman-machine-default`) for GPU workloads. NVIDIA RTX PRO 500 Blackwell is accessible via CDI (`--device nvidia.com/gpu=all`).

**Remember:** this is Podman, not Docker. Even though the commands below use `docker` for compatibility, the engine is Podman and must not touch Rancher Desktop.

### Podman Stack Management
```bash
# From Windows (Git Bash / WSL):
bash scripts/gpu-podman.sh up
bash scripts/gpu-podman.sh down
bash scripts/gpu-podman.sh status
```

Or using Docker CLI with the Podman context:
```bash
docker --context podman-machine-default compose -f docker/docker-compose.yml -f docker/docker-compose.podman.yml up -d --no-build
```

- Compose override: `docker/docker-compose.podman.yml`
- Image: `docker-api:latest` (pre-built, migrated from native Docker)
- GPU via CDI (`nvidia.com/gpu=all`)
- Postgres tunnel: SSH tunnel on port 15432 via Ubuntu-20.04 WSL; reached as `host.containers.internal:15432`

### Legacy (Native Docker Engine in Ubuntu WSL — deprecated)

The old GPU Docker stack still exists for reference:
```bash
wsl -d Ubuntu-20.04 bash -c "bash '/mnt/c/own/alejandria/scripts/gpu-up.sh' up"
```
- Compose override: `docker/docker-compose.gpu.yml` + `docker/Dockerfile.gpu`
- Uses separate Docker Engine on Ubuntu-20.04 WSL with `--gpus all`

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
