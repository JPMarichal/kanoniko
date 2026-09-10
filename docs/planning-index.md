# Planning Index — Alejandría

> **Read this first when planning docs seem to disagree.** It maps every planning/proposal artifact
> to its authority and status. The system's **current state** (not plans) lives in
> [`system-spec.md`](system-spec.md).
> **Last reviewed:** 2026-09-09.

## Authority order

1. **`system-spec.md`** — what the system IS. Wins over any doc that describes the system in the
   present tense.
2. **`roadmap.md` + `proj/`** — the priority-ordered incubator and its per-project spec/plan/tasks
   (format: [`proj/CONVENTIONS.md`](../proj/CONVENTIONS.md)). This is the working backlog.
3. **`improvement-program-2026.md`** — the phased modernization program (Fases A–G) that sits on top
   of the incubator, with live tracking. Rationale in `improvement-analysis-2026.md`.
4. Everything else is an input to the above, not an authority.

## Active

| Doc | Scope | Status / notes |
|---|---|---|
| [`system-spec.md`](system-spec.md) | Current state of the whole system | Authoritative. Update on landing. |
| [`roadmap.md`](roadmap.md) | Incubator P1–P13 + WI list | Active. 2026-09 revision merged (PR #14). |
| [`proj/`](../proj/) | Per-project spec/plan/tasks/risks | Active. P0/P11/P12 are SDD-formatted; P1–P10 legacy names until next touched. |
| [`improvement-analysis-2026.md`](improvement-analysis-2026.md) | SWOT, pain→tech, roadmap eval | Active. Some passages predate the A0 audit findings and the discovery of the docs below — treat `system-spec.md` + this index as the tiebreak. |
| [`improvement-program-2026.md`](improvement-program-2026.md) | Fases A–G + tracking | Active, with two known overlaps — see **Contradictions** below. |
| [`architecture-proposals/graph-enhanced-rag-evaluation.md`](architecture-proposals/graph-enhanced-rag-evaluation.md) | Graph-enhanced RAG options (Graphify, GraphRAG, PPR) | **Propuesta**, 2026-08-22. The authoritative version of this analysis — supersedes the "HippoRAG-2 / PPR" passages in `improvement-analysis-2026.md`. |
| [`architecture-proposals/ppr-implementation-plan.md`](architecture-proposals/ppr-implementation-plan.md) | Personalized PageRank retrieval | Active implementation plan (2026-08-22, ETA 2026-09-05). PPR module already exists: `src/alejandria/knowledge/pagerank.py`. **This is the plan of record for PPR** — `improvement-program-2026.md` Fase E / P11·E4 defers to it. |
| [`postgres-migration.md`](postgres-migration.md) | Postgres migration master plan | Reference. Migration is **complete** (`ecd885fc8d`) — `line 283` "write path Pendiente" is stale; P0·T2 closes it. |

## Historical / done (keep for the record, not a plan)

| Doc | What it was | Why it's closed |
|---|---|---|
| [`postgres-blockers-workplan.md`](postgres-blockers-workplan.md) | Blockers before the workspace migration | PR #1/#2 COMPLETADO; only R5 honorifics (0.5 d) outstanding, tracked in WI-3. |
| [`project-memory/project_podman_migration.md`](project-memory/project_podman_migration.md) | Docker→Podman container migration | COMPLETE 2026-07-04. This is why `improvement-program-2026.md` Fase F (F1/F4) is largely done. |
| [`postgres-migration-status.md`](postgres-migration-status.md) | April merge-status snapshot | Stale snapshot; P0·T2 adds a completion header. |

## Superseded

| Doc | Superseded by |
|---|---|
| [`workspace-migration-specs.md`](workspace-migration-specs.md) (1744 lines) | The 4-package split it specs was **abandoned** (`workspace-migration` branch). Kept only as a record. `system-spec.md` §1: flat `src/alejandria` is the layout. |

## Aspirational — NOT adopted (needs an explicit decision to revive)

| Doc | Claim | Conflict |
|---|---|---|
| [`ARCHITECTURE_PLAN.md`](ARCHITECTURE_PLAN.md) | Split the monolith into ~10–14 microservice repos; 12-month, 5-phase; ROI 150–200 %. May 2026, "revisión semanal" but unmaintained. | Directly contradicts `system-spec.md` §1 and the 2026-09 decision to keep the flat package. **Not on the roadmap.** Either resurrect as a real incubator project with a spec, or add a "shelved" banner. |
| [`architecture-proposals/README.md`](architecture-proposals/README.md) | Indexes `ARCHITECTURE_IMPROVEMENT_CHECKLIST.md`, `REPOSITORY_SPLIT_PROPOSAL.md`, `REPOSITORY_SPLIT_ANALYSIS.md`, `APPLICATION_PRODUCTS_INTEGRATION.md` | Those files **do not exist** in the directory. Index is stale — fixed in this change to list only what's present. |

## Contradictions to resolve (owner: user)

1. **PPR / graph-enhanced RAG — two plans.**
   `improvement-program-2026.md` (Fase E · E4 "HippoRAG-2 spike", and P11 mentions) vs
   `architecture-proposals/ppr-implementation-plan.md` (concrete, dated, module already built).
   **Resolution applied here:** the PPR plan is the plan of record; `improvement-program-2026.md`
   E4 and P11·T0.1 now say "adopt PPR per `ppr-implementation-plan.md`; do not re-plan". The
   `improvement-analysis-2026.md` HippoRAG-2 passages should be read as background, not a competing
   proposal.

2. **Monolith vs microservices.**
   `system-spec.md` + roadmap (flat `src/alejandria`, keep it) vs `ARCHITECTURE_PLAN.md` +
   `architecture-proposals/` (10-repo split). **Unresolved — needs your call.** Until then:
   `system-spec.md` reflects reality (flat package); `ARCHITECTURE_PLAN.md` carries a "not adopted"
   note. If you want the split, it becomes a first-class incubator project (`proj/Pxx-repo-split/`)
   with a real spec, not a floating document.

3. **`improvement-program-2026.md` Fase F is partly done.**
   Podman migration completed 2026-07-04. F1 (unify engines) and F4 (retire Neo4j container) are
   done; marked as such in this change.
