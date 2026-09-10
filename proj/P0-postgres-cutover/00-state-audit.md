# P0 · A0 — State Audit (2026-09-09)

**First pass audited the wrong branch.** It ran against `workspace-migration` (the checkout at the
time). The user clarified: **`main` is the working system; `workspace-migration` is an abandoned,
non-current attempt.** This is the corrected audit against **`main`** (`eeb851ae5a`).

## Verdict

**The Postgres migration is complete and validated on `main`. `CLAUDE.md` is accurate. The "31/31
golden queries" are real and committed.** The only genuine gap is **documentation debt** in the
architecture/layer docs. P0 collapses to a doc-sync task (~1 day).

## Postgres migration — done & validated on `main`

| Question | Finding | Evidence (on `main`) |
|---|---|---|
| Neo4j dependency / client? | **Gone** | No `neo4j` in `pyproject.toml`; **no `src/alejandria/knowledge/neo4j_client.py`** — only `postgres_graph_client.py` |
| SQLite / `sqlite-vec`? | **Gone** | Not in `pyproject.toml`; deps are `psycopg[binary]`, `pgvector`, `sentence-transformers` |
| `PostgresGraphClient` stubbed? | **No** | Zero `raise NotImplementedError`; genealogy recursive CTEs, typed-relation methods, write path all implemented |
| Ingestion write path ported? | **Yes** | `src/alejandria/ingestion/pipeline.py` imports `alejandria.storage.{chunk_writer,kg_reader,kg_writer}` — all Postgres; no Neo4j/SQLite writes |
| Golden parity suite? | **Committed & passing** | `tests/parity/golden_queries.yaml` (**31 queries**), `oracle_neo4j.json`, `oracle_postgres.json`, `capture_oracle.py`, `compare_oracles.py`, `VALIDATION-TIER2AB.md`. Git: `ecd885fc8d` / `99b1493bfa` **"feat(kg): close §3.2 — 31/31 golden queries passing on Postgres"** |
| Does the app import? | **Code OK; venv incomplete** | `import alejandria.main` fails only with `ModuleNotFoundError: No module named 'mcp'` — the `mcp` SDK isn't installed in this checkout's `.venv`. Environment gap, not a code defect. `uv sync` / `pip install` fixes it |

→ `docs/postgres-migration-status.md` (2026-04-18) and
`docs/project-memory/project_postgres_source_of_truth.md` are **stale snapshots** — their unchecked
"follow-up PR" boxes were completed by `ecd885fc8d` and predecessors.

## Golden queries — diagnosed

Real, committed on `main`, and passing. The first audit missed them because the **abandoned
`workspace-migration` branch deleted them** (`8c0701c1d6 chore(workspace): Limpiar archivos
innecesarios después de migración` removed `oracle_*.json` / `VALIDATION*` and half-ported
`capture_oracle.py` from Neo4j→Postgres). `VALIDATION-TIER2AB.md` documents the earlier 11-query
Tier 2a/2b pass (8 OK / 2 documented non-blocking divergences — q02 is a *Postgres-wins* cleanup
effect, q14 is the known recursive-CTE confidence-ordering caveat / low impact / `depth=1` is the
common path); the full 31/31 landed in the later `§3.2` commit.

**Action:** none needed on the suite itself. Optionally wire `compare_oracles` into `pytest` so
parity is a CI gate rather than a manual script (nice-to-have, → P11 Phase 1).

## Genuine gaps

| Gap | Detail | P0 item |
|---|---|---|
| Architecture/layer docs stale | `docs/architecture.md`, `docs/stack.md`, `docs/knowledge-graph.md`, `docs/search-textual.md`, `docs/search-semantic.md`, `docs/search-hybrid.md`, `docs/README.md` still present Neo4j / Qdrant / SQLite as the current stack | FR-1 |
| Migration status docs open-ended | `docs/postgres-migration-status.md` + `project_postgres_source_of_truth.md` read as "in progress" | FR-2 |
| Stale in-code strings | `postgres_graph_client.py` docstrings say "Same shape as `Neo4jClient`" (harmless parity notes — leave, or reword); `api/schemas.py` Field descriptions may still mention Neo4j | FR-1 |
| Untracked `packages/` on `main` | `git ls-files packages/` → 0. Leftover scaffolding from the abandoned workspace attempt. Dead weight | FR-3 (optional) |
| `.venv` missing `mcp` | Local only; `uv sync` fixes | note, not P0 |
| `workspace-migration` branch + its uncommitted WIP | Abandoned. WIP parked in `git stash` ("workspace-migration WIP … parked by Claude 2026-09-09"). Branch can be deleted when the user is sure | FR-3 (optional) |

## Rescope of P0

| Original assumption | Reality (`main`) | New P0 scope |
|---|---|---|
| Port write path, implement ~30 client methods, cutover, tear down Neo4j | **All done & validated (31/31)** | — |
| "Land the `workspace-migration` branch" (2nd audit) | Branch is abandoned, not the system | — (delete branch when user confirms) |
| Doc sync | Still needed | **Sync 7 architecture docs; close 2 migration-status docs; reword stale code strings** |
| — | Untracked `packages/` cruft + dead branch | **Optional cleanup** |

**P0 effort: ~1 day.** It is no longer a blocker of any size; P11/P12/WI-3 can start as soon as the
docs are trustworthy.

## Decisions taken (per user, 2026-09-09)

- `main` is canonical; `workspace-migration` abandoned.
- **Keep the flat `src/alejandria` package.** The 4-package `uv`/`hatch` split was the abandoned
  attempt — not resurrected. Program **Fase F / F5** ("evaluate 4 packages vs 1") is therefore
  closed: the answer is "1, already".
