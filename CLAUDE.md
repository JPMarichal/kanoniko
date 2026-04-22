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

- Python 3.11, FastAPI, Postgres IONOS + pgvector (authoritative: chunks, FTS via tsvector, embeddings, KG). Transitional SQLite + sqlite-vec mirror retired in §3.4.
- spaCy + domain gazetteers for KG extraction
- Docker Compose (1 container: api — Neo4j retired in §3.3, Postgres lives on IONOS VPS)

### Postgres IONOS = source of truth (Phase 1 PR #3; write cutover PR #4; KG read complete PR #5; Neo4j retired §3.3)

**Postgres 16 + pgvector on IONOS VPS is the authoritative store** for
chunks, FTS (tsvector), embeddings (pgvector), entities, relations, and
mentions. The Neo4j container and SQLite write path have been retired;
the local SQLite file is kept read-only for the transitional period
until §3.4 closes.

- **For any destructive op or correctness audit, verify Postgres IONOS** —
  not Neo4j local, not SQLite local. SSH tunnel `localhost:15432 →
  212.227.243.210:5432` should already be active in WSL
  (`pgrep -f "ssh.*15432"`). Credentials in `.env` (`ALEJANDRIA_POSTGRES_*`).
- **Connecting from a container:** `docker run --rm --network host -e
  ALEJANDRIA_POSTGRES_HOST=127.0.0.1 -e ALEJANDRIA_POSTGRES_PORT=15432 ...`
  Load env via heredoc (`bash << 'OUTER' ... source .env; ... OUTER`) — single
  `bash -c "..."` quoting can swallow the password.
- **Feature flag (transitional):** `ALEJANDRIA_STORAGE_BACKEND` (default
  `"sqlite"`). Setting `"postgres"` routes reads through the Postgres backend
  via DI factories (`search.textual.make_textual_search`,
  `search.semantic.make_semantic_search`,
  `knowledge.postgres_graph_client.make_graph_client`).
- **Read parity partial:** 3 KG client methods ported and validated against
  Neo4j oracle (`find_node`, `get_neighbors`, `graph_summary`). Remaining
  methods raise `NotImplementedError` — tracked in
  `docs/kg-client-port-audit.md`.
- **Write path cutover pending.** Ingestion still writes SQLite + Neo4j;
  Postgres cutover is a follow-up PR. Until that lands, the Postgres copy
  is the source of truth for **reads, audits, and corrective mutations** —
  the local mirrors can drift.
- **MCP tools (`mcp__alejandria__*`) read via the local API which currently
  proxies to Neo4j.** They are a *view*, not the oracle. To verify or mutate
  ground truth, connect directly to Postgres IONOS.
- **Operational infra:** see `docs/ionos-setup.md` for VPS setup,
  `docs/postgres-migration.md` for the full plan,
  `docs/postgres-migration-status.md` for current state + follow-up PRs.
- **Vector DB alternatives (Qdrant, Weaviate, Pinecone, Milvus)** analyzed
  in `docs/vector-db-options.md` — pgvector wins at current scale; triggers
  to reconsider documented there.

## Vision

The final product is a **specialized chat client for scripture/gospel study** (RAG-based). The knowledge engine (search APIs) is the backend; the chat UI is a future service consuming it.

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

**Postgres IONOS is the source of truth** (post Phase 1 merge — see § Stack above). Its canonical backup is the `pg_dump` daily snapshot on IONOS (see `docs/ionos-setup.md`).

The local endpoints below act on the **transitional SQLite mirror only** — Neo4j backup endpoints were retired in §3.3 together with the Neo4j container.

### Backup Endpoints (API running at :4300)
| Endpoint | What it does |
|----------|-------------|
| `POST /backup/sqlite?label=manual` | Timestamped copy (includes vectors), rotates last 5 |
| `GET /backup/sqlite` | List available SQLite backups |
| `POST /backup/sqlite/restore?filename=...` | Restore SQLite from backup |
| `POST /index/rebuild-vectors` | Rebuild vectors in sqlite-vec from chunk text (no filesystem I/O) |

### Automatic Pre-Index Backup
The pipeline automatically backs up SQLite before any indexing run. KG snapshots are handled server-side by the IONOS `pg_dump` cron.

### What's Tracked in Git (disaster recovery baseline)
| Asset | Location | Notes |
|-------|----------|-------|
| Source code | `src/`, `docker/`, `scripts/` | |
| Corpus | `corpus/` | Bind-mounted, full text in git |
| SQLite DB | GitHub Release (`backup-*`, ~1.4 GB compressed) | Derived artifact, NOT in git; download via `scripts/backup-pull.sh db` |
| Gazetteers | `data/gazetteers/` | 7 NER assets, hard to rebuild |
| Project memory | `docs/project-memory/` | Primary source — tracked directly in git |
| Skills/hooks | `.claude/` | |
| Secrets | **NOT in git** — encrypted (`env.enc`) in GitHub Release | Download via `scripts/backup-pull.sh secrets`, decrypt with `openssl` passphrase |

**IMPORTANT:** The raw `data/sqlite/alejandria.db` on Windows is **NOT the source of truth** — it's gitignored and may be stale. The authoritative DB is in the GPU container at `/home/jpmarichal/alejandria-data/sqlite/alejandria.db`. The DB is stored as GitHub Release assets (not Git LFS) to avoid bandwidth limits.

### Recovery Procedures
- **SQLite lost:** `gunzip -k data/sqlite/alejandria.db.gz` or restore from backup endpoint
- **Vectors lost:** `POST /index/rebuild-vectors` (~5 min on GPU) — rebuilds sqlite-vec table from chunk text
- **KG lost:** restore Postgres from the latest IONOS `pg_dump` (see `docs/ionos-setup.md`); no per-instance recovery needed.
- **Full disaster:** Clone repo, `bash scripts/backup-pull.sh all`, decrypt `.env`, `docker compose up`, data is in git
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
