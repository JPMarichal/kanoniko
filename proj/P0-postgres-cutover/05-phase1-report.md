# P0 — Phase 1 (doc sync) + modular-monolith decision — report

**Date:** 2026-09-10 · **Branch:** `p0/doc-sync-modular-monolith` · **Status:** Phase 1 partial (T1.7 / T1.8 open), Phase 2 done.

## What landed

### Architecture / decision
- **ADR 0002 — modular monolith** (`docs/adr/0002-modular-monolith.md`). Resolves the
  monolith-vs-microservices contradiction: `src/alejandria/` stays one package; boundaries declared
  and enforced; sanctioned extractions = web/mobile front-ends (P5) + a GPU ingestion worker.
  `ARCHITECTURE_PLAN.md` **shelved**.
- `[tool.importlinter]` contract in `pyproject.toml` (3 `forbidden` contracts covering the import
  direction), `just check-boundaries`, non-blocking pre-commit step 7, `import-linter` added to
  `dev` extras. **Advisory until baselined — T1.8.**

### Docs reconciled to `system-spec.md`
| File | Change |
|---|---|
| `architecture.md` | Full rewrite — Postgres store, retrieval modules, module map + enforced import direction, ADR refs |
| `stack.md` | Full rewrite — Postgres/Podman tables, "Retired" note pointing at `vector-db-options.md` |
| `knowledge-graph.md` | Header + Key Classes → `PostgresGraphClient`; taxonomy untouched |
| `search-textual.md` | Full rewrite — `websearch_to_tsquery` + `ts_rank_cd`, `chunks` DDL |
| `search-semantic.md` | Full rewrite — pgvector HNSW `<=>`, `chunk_embeddings` |
| `rag-pipeline.md` | 3 line fixes (FTS5→tsvector, Qdrant→pgvector, Neo4j neighbor→KG neighbor) |
| `configuration.md` | `ALEJANDRIA_POSTGRES_*` + SSH-tunnel vars (from `config.py`); RAG chunk defaults 12→8 |
| `README.md` | Index labels (SQLite/Qdrant/Neo4j/"two Docker engines" → current); ADR section; system-spec/planning-index already linked |
| `system-spec.md` | §1 modular-monolith + import direction; derived-docs note = P0 status |
| `planning-index.md` | Contradiction #2 → Resolved (modular monolith); `ARCHITECTURE_PLAN` row → Shelved |
| `ARCHITECTURE_PLAN.md` | Banner → ARCHIVADO + ADR 0002 pointer |

### Code
- `src/alejandria/api/schemas.py` — 3 Field descriptions reworded off "Neo4j".

### Status docs closed
- `postgres-migration-status.md` — "✅ MIGRACIÓN COMPLETA" header.
- `project-memory/project_postgres_source_of_truth.md` — top note: complete, not Phase 1.

## Deliberately deferred (bannered, not silent)

- **T1.7** — `entity-extraction.md`, `entity-profiles.md`, `ingestion.md`, `operations.md`,
  `backup.md` carry a ⚠️ stale-banner. `operations.md` / `backup.md` describe retired backup
  endpoints and WSL paths; rewriting them accurately needs the current `pg_dump`/IONOS backup story
  written out — a follow-up, not a guess.
- **T1.8** — `import-linter` not run here (`import-linter` not installed in the checkout). First run
  may surface pre-existing violations to fix or `ignore_imports`.
- **Cleanup (T3.1/T3.2)** — untracked `packages/`, `workspace-migration` branch, `stash@{1}` — git
  ops for the user.

## Verification done

- `grep -niE "fts5|sqlite-vec|qdrant" docs/search-*.md docs/rag-pipeline.md` → only "Retired" lines.
- `grep -n "Neo4j" src/alejandria/api/schemas.py` → empty.
- `python scripts/check_spec_sync.py` → ok (docs staged alongside the `schemas.py` touch).
- `just --list` parses the new recipes.

## Next

Merge → then P11 Phase 1 (eval harness) + P12 Phase 1 in parallel. T1.7 / T1.8 can be a small
follow-up PR or folded into the next docs pass.
