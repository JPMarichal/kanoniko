# P0 — Documentation Sync & Cleanup — Requirements

> **Scope settled after two audit passes** (see [`00-state-audit.md`](00-state-audit.md)). The
> Postgres migration is **complete and validated on `main`** (Neo4j + SQLite gone, write path
> ported, `PostgresGraphClient` complete, **31/31 golden queries passing** — committed). The
> abandoned `workspace-migration` branch is not the system. What remains is documentation debt.
> Folder name kept as `P0-postgres-cutover` for stable references.

## Problem Statement

`main` runs a single Postgres + pgvector store, but several docs still describe the retired stack,
so anyone (human or agent) reading them gets a false model of the system:

1. `docs/architecture.md`, `docs/stack.md`, `docs/knowledge-graph.md`,
   `docs/search-textual.md`, `docs/search-semantic.md`, `docs/search-hybrid.md`,
   `docs/README.md` present Neo4j / Qdrant / SQLite-FTS as current.
2. `docs/postgres-migration-status.md` and `docs/project-memory/project_postgres_source_of_truth.md`
   read as "in progress" (unchecked follow-up boxes) when the work is done.
3. Minor stale strings in code: `postgres_graph_client.py` parity docstrings ("Same shape as
   `Neo4jClient`"), possibly `api/schemas.py` Field descriptions mentioning Neo4j.
4. Untracked `packages/` scaffolding on `main` (0 tracked files) + the dead `workspace-migration`
   branch and its parked stash — dead weight.

Downstream initiatives (P11, P12, WI-3) don't depend on any code work here — only on docs being
trustworthy.

## Functional Requirements

### FR-1: Sync architecture/layer docs to a single Postgres store
Update the 7 docs above to describe: Postgres 16 + pgvector on IONOS as the sole store (chunks, FTS
via `tsvector`, embeddings via pgvector, KG entities/relations/mentions); `PostgresGraphClient` as
the KG client; no Neo4j, no Qdrant, no SQLite. Keep explicit *historical* notes where useful
("Phase 2 originally used Qdrant; consolidated to pgvector — see `vector-db-options.md`"). Reword
or drop stale code strings (`postgres_graph_client.py` docstrings, `api/schemas.py` Field
descriptions).

### FR-2: Close out the migration-status docs
Add a closing header to `docs/postgres-migration-status.md` (and the project-memory file) stating
the migration is complete as of `ecd885fc8d` ("close §3.2 — 31/31 golden queries passing"), with a
pointer to `tests/parity/`. Either check the remaining boxes or mark them "done — see commit".

### FR-3: Cleanup (optional, do if quick)
- Remove the untracked `packages/` tree on `main` (confirm `git status` shows it untracked first).
- After the user confirms, delete the `workspace-migration` branch and drop the parked stash
  (`git stash list` → "workspace-migration WIP … parked by Claude 2026-09-09").

### FR-4: Parity as a test (nice-to-have → can defer to P11)
Wire `tests/parity/compare_oracles.py` into `pytest` (or a `just` target) so 31/31 parity is a
gate, not a manual script. If deferred, note it in P11 Phase 1 (eval harness).

## Non-Functional Requirements

- **Docs-only**: no behavior change, no `src/` logic edits (stale-string rewording excepted).
- **Same-commit rule**: this *is* the doc commit; no code counterpart needed.
- **Historical honesty**: don't erase the Neo4j/Qdrant history, just stop presenting it as present tense.

## Out of Scope

- Any Postgres migration work — done (A0).
- Resurrecting the workspace split — abandoned per user; stay on flat `src/alejandria`.
  Program **Fase F / F5** is closed by that decision.
- Embedding/reranker/extractor changes — P11 / P12.

## Current State

- Branch `main` @ `eeb851ae5a`; flat `src/alejandria` package; `tests/` incl. `tests/parity/`.
- `.venv` in this checkout is missing `mcp` (local only; `uv sync` fixes).
- A0 evidence: [`00-state-audit.md`](00-state-audit.md).
