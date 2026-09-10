# P0 — Documentation Sync & Cleanup — Tasks

> `[ ]` pending · `[~]` in progress · `[x]` done · `[-]` dropped. Each task names its check.
> Spec: [`01-spec.md`](01-spec.md) · Plan: [`02-plan.md`](02-plan.md).

## Phase 0 — State audit

- [x] **T0.1** Audit migration state against `main` (Postgres, Neo4j/SQLite, write path, graph
      client, golden queries). *Check:* [`00-state-audit.md`](00-state-audit.md) exists with evidence.
      *(Done 2026-09-09; second pass corrected the branch.)*

## Phase 1 — Doc sync

- [ ] **T1.1** Rewrite `docs/architecture.md` layer/store sections to Postgres-only + `PostgresGraphClient`.
      *Check:* `grep -niE "neo4j|qdrant|sqlite" docs/architecture.md` → only lines under a "Historical" heading.
- [ ] **T1.2** Rewrite `docs/stack.md` storage/KG rows. *Check:* same grep on `docs/stack.md`.
- [ ] **T1.3** Rewrite `docs/knowledge-graph.md` to `PostgresGraphClient` model (keep the node/relation
      taxonomy; drop "Neo4j-based"). *Check:* grep on the file.
- [ ] **T1.4** Update `docs/search-textual.md` (FTS via `tsvector`, not SQLite FTS5),
      `docs/search-semantic.md` (pgvector, not Qdrant), `docs/search-hybrid.md` (RRF over pg). *Check:* grep on the three.
- [ ] **T1.5** Fix the `docs/README.md` index labels ("Neo4j graph model" → "Postgres KG model",
      "Qdrant" → "pgvector", "SQLite FTS5" → "Postgres FTS", "two Docker engines" → "Podman").
      *Check:* `grep -niE "neo4j|qdrant|sqlite|two docker" docs/README.md` → empty.
- [ ] **T1.6** Reword stale code strings: `src/alejandria/knowledge/postgres_graph_client.py`
      docstrings ("Same shape as `Neo4jClient`" → "record shape N"), `src/alejandria/api/schemas.py`
      Field descriptions mentioning Neo4j. *Check:* `grep -rn "Neo4j" src/alejandria/` → only intentional historical comments.

## Phase 2 — Close status docs

- [ ] **T2.1** Add a "COMPLETE as of `ecd885fc8d` — see `tests/parity/`" header to
      `docs/postgres-migration-status.md`; check or annotate its open boxes.
      *Check:* file's first non-title line states completion.
- [ ] **T2.2** Update `docs/project-memory/project_postgres_source_of_truth.md` "Pendiente operativo"
      section to reflect completion. *Check:* no open "pending" items about write-path / graph client.

## Phase 3 — Cleanup (optional)

- [ ] **T3.1** Remove the untracked `packages/` tree on `main` (confirm untracked first).
      *Check:* `git status --porcelain | grep packages/` → empty.
- [ ] **T3.2** With user OK: `git branch -D workspace-migration` + `git stash drop` the parked WIP
      (`stash@{1}`). *Check:* `git branch` and `git stash list` no longer show them.

## Phase 4 — Parity as a gate (nice-to-have; may move to P11)

- [ ] **T4.1** `tests/parity/test_parity.py` (or `just parity`) runs `compare_oracles` and asserts
      31/31. *Check:* `just parity` exits 0 in CI/local.

## Notes

- Do **not** erase Neo4j/Qdrant history — change tense, keep the fact, link `docs/vector-db-options.md`.
- `docs/architecture-proposals/` and `docs/ARCHITECTURE_PLAN.md` are a separate (microservices)
  planning track — out of scope here; see `docs/planning-index.md`.
