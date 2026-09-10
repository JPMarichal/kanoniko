# P0 — Documentation Sync & Cleanup — Plan

> Rescoped after A0 (2026-09-09, [`00-state-audit.md`](00-state-audit.md)). Postgres migration is
> done & validated on `main` (31/31 golden queries). This project is docs + light cleanup.
> Maps to **Fase A** of [improvement-program-2026.md](../../docs/improvement-program-2026.md).
> **2026-09-10:** widened slightly to record the modular-monolith decision
> ([`docs/adr/0002-modular-monolith.md`](../../docs/adr/0002-modular-monolith.md)) and add the
> `import-linter` boundary contract. Phase 1 (T1.1–T1.6) + Phase 2 landed; T1.7 (deep rewrites of
> `operations.md` / `backup.md` / `ingestion.md` / `entity-*.md`) and T1.8 (baseline import-linter)
> remain. ~1.5 días total.

## Phases

### Phase 0 — State audit ✅ (2026-09-09)
Two passes (first mistakenly on `workspace-migration`, corrected against `main`). Result: migration
complete & validated; only doc debt remains. See `00-state-audit.md`.

### Phase 1 — Doc sync  ✅ (partial — T1.7 open)
**Scope:** FR-1, FR-2.
**Done 2026-09-10:**
- `architecture.md`, `stack.md`, `knowledge-graph.md`, `search-textual.md`, `search-semantic.md`,
  `configuration.md`, `rag-pipeline.md`, `README.md` reconciled to a single Postgres store +
  `PostgresGraphClient` + Podman. Historical "Retired" notes kept.
- **ADR 0002 (modular monolith)** written; `[tool.importlinter]` contract + `just check-boundaries`
  + non-blocking pre-commit step added; `system-spec.md` §1 + `planning-index.md` §2 + `ARCHITECTURE_PLAN.md`
  updated to reflect it.
- `api/schemas.py` Field descriptions reworded (no more "load to Neo4j").
- `postgres-migration-status.md` + `project_postgres_source_of_truth.md` closed with completion headers.
**Open — T1.7:** `entity-extraction.md`, `entity-profiles.md`, `ingestion.md`, `operations.md`,
`backup.md` got a stale-banner only; they need a real rewrite (backup/restore story, per-phase
storage targets, WSL→Podman paths).
**Open — T1.8:** baseline `import-linter` (install, run, fix/ignore violations, make blocking).
**Exit:** every `docs/*.md` (T1.7 set included) grep-clean except historical notes; `just check-boundaries` green.

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

## Acceptance Criteria

1. ☐ `grep -rniE "neo4j|qdrant|sqlite" docs/*.md` → only historical notes.
2. ☐ `docs/architecture.md` + `docs/stack.md` describe Postgres-only + `PostgresGraphClient`.
3. ☐ `postgres-migration-status.md` reads "complete".
4. ☐ (optional) untracked `packages/` + `workspace-migration` branch removed.
5. ☐ (optional) 31/31 parity runs under `pytest`.
