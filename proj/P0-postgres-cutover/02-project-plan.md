# P0 — Documentation Sync & Cleanup — Project Plan

> Rescoped after A0 (2026-09-09, [`00-state-audit.md`](00-state-audit.md)). Postgres migration is
> done & validated on `main` (31/31 golden queries). This project is docs + light cleanup, ~1 day.
> Maps to **Fase A** of [improvement-program-2026.md](../../docs/improvement-program-2026.md).

## Phases

### Phase 0 — State audit ✅ (2026-09-09)
Two passes (first mistakenly on `workspace-migration`, corrected against `main`). Result: migration
complete & validated; only doc debt remains. See `00-state-audit.md`.

### Phase 1 — Doc sync
**Scope:** FR-1, FR-2.
**Deliverables:**
- `docs/architecture.md`, `docs/stack.md`, `docs/knowledge-graph.md`,
  `docs/search-{textual,semantic,hybrid}.md`, `docs/README.md` updated to a single Postgres store +
  `PostgresGraphClient`. Historical notes kept where useful.
- Stale code strings reworded: `src/alejandria/knowledge/postgres_graph_client.py` docstrings,
  `src/alejandria/api/schemas.py` Field descriptions (grep `Neo4j`).
- `docs/postgres-migration-status.md` + `docs/project-memory/project_postgres_source_of_truth.md`
  closed out with a "complete as of `ecd885fc8d`" header + pointer to `tests/parity/`.
**Exit:** `grep -rniE "neo4j|qdrant|sqlite" docs/*.md` returns only explicit historical notes.
**Est.:** ~1 día.

### Phase 2 — Cleanup (optional, only if quick)
**Scope:** FR-3.
**Deliverables:**
- Untracked `packages/` tree removed from `main` working copy (after confirming untracked).
- With user confirmation: `git branch -D workspace-migration`; `git stash drop` the parked WIP.
**Exit:** `git status` clean of the abandoned scaffolding.
**Est.:** 15 min.

### Phase 3 — Parity as a gate (nice-to-have; may move to P11)
**Scope:** FR-4.
**Deliverable:** `tests/parity/test_parity.py` (or `just parity`) that runs `compare_oracles` and
asserts 31/31. If deferred, add a checkbox to P11 Phase 1.
**Est.:** ½ día (or 0 if deferred).

## Milestones

| Milestone | Deliverable | Status |
|-----------|-------------|--------|
| M0 | State audit (both passes) | ✅ 2026-09-09 |
| M1 | 7 docs + code strings + 2 status docs synced (**Gate A**) | ☐ |
| M2 | `packages/` cruft + dead branch removed | ☐ (optional) |
| M3 | Parity wired into pytest | ☐ (optional / P11) |

## Dependencies

- **Inbound:** none.
- **Outbound:** P11, P12, WI-3 want trustworthy docs before they start; none depend on P0 *code*.

## Success Criteria

1. ☐ `grep -rniE "neo4j|qdrant|sqlite" docs/*.md` → only historical notes.
2. ☐ `docs/architecture.md` + `docs/stack.md` describe Postgres-only + `PostgresGraphClient`.
3. ☐ `postgres-migration-status.md` reads "complete".
4. ☐ (optional) untracked `packages/` + `workspace-migration` branch removed.
5. ☐ (optional) 31/31 parity runs under `pytest`.
