# P0 — Documentation Sync & Cleanup — Tasks

> `[ ]` pending · `[~]` in progress · `[x]` done · `[-]` dropped. Each task names its check.
> Spec: [`01-spec.md`](01-spec.md) · Plan: [`02-plan.md`](02-plan.md).

## Phase 0 — State audit

- [x] **T0.1** Audit migration state against `main`. → [`00-state-audit.md`](00-state-audit.md). *(2026-09-09)*

## Phase 1 — Doc sync

- [x] **T1.1** `docs/architecture.md` → Postgres-only + modular-monolith framing + ADR refs. *Check:* `grep -niE "neo4j|qdrant|sqlite" docs/architecture.md` → only the historical "Retired" line.
- [x] **T1.2** `docs/stack.md` → Postgres/Podman tables + "Retired" note. *Check:* grep → only historical.
- [x] **T1.3** `docs/knowledge-graph.md` → `PostgresGraphClient`; kept the node/relation taxonomy. *Check:* grep → only historical parity notes.
- [x] **T1.4** `docs/search-textual.md` (tsvector/`ts_rank_cd`), `docs/search-semantic.md` (pgvector HNSW), `docs/rag-pipeline.md` (3 refs). *Check:* `grep -niE "fts5|sqlite-vec|qdrant" docs/search-*.md docs/rag-pipeline.md` → only "Retired" lines.
- [x] **T1.5** `docs/README.md` index labels + ADR entry. *Check:* `grep -niE "neo4j|qdrant|sqlite fts5|two docker" docs/README.md` → empty.
- [x] **T1.6** `docs/configuration.md` env vars → `ALEJANDRIA_POSTGRES_*` + SSH tunnel; `src/alejandria/api/schemas.py` Field descriptions reworded. *Check:* `grep -n "Neo4j" src/alejandria/api/schemas.py` → empty.
- [ ] **T1.7** Full rewrite of the docs that only got a **stale-banner** this pass:
      `entity-extraction.md`, `entity-profiles.md`, `ingestion.md`, `operations.md`, `backup.md`
      (backup/restore, per-phase storage targets, WSL/Podman paths). *Check:* each file's banner
      removed; `grep -niE "sqlite|qdrant|neo4j|Ubuntu-20.04" docs/{operations,backup,ingestion,entity-*}.md`
      → only historical.
- [ ] **T1.8** Baseline `import-linter`: `pip install import-linter`, run `just check-boundaries`,
      fix real violations or add `ignore_imports`, then make the pre-commit step blocking.
      *Check:* `just check-boundaries` exits 0.

## Phase 2 — Close status docs

- [x] **T2.1** `docs/postgres-migration-status.md` completion header. *Check:* first blockquote says "MIGRACIÓN COMPLETA".
- [x] **T2.2** `docs/project-memory/project_postgres_source_of_truth.md` update note. *Check:* top note says migration complete, not Phase 1.

## Phase 3 — Cleanup (optional)

- [ ] **T3.1** Remove the untracked `packages/` tree on `main`. *Check:* `git status --porcelain | grep packages/` → empty. *(git op — user runs it.)*
- [ ] **T3.2** With user OK: `git branch -D workspace-migration` + `git stash drop "stash@{1}"`. *(git op — user runs it.)*

## Phase 4 — Parity as a gate (nice-to-have; may move to P11)

- [ ] **T4.1** `tests/parity/test_parity.py` (or `just parity`) asserts 31/31. *Check:* `just parity` exits 0.

## Done / notes

- 2026-09-10 — Phase 1 (T1.1–T1.6) + Phase 2 landed on branch `p0/doc-sync-modular-monolith`.
  ADR 0002 (modular monolith) written; `import-linter` contract added (advisory, T1.8 to baseline).
  T1.7 (deep rewrites of operations/backup/ingestion/entity docs) deferred — bannered, not silent.
