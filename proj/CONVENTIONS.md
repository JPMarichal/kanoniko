# Incubator Conventions — Spec-Driven

Every project under `proj/` follows a **spec → plan → tasks → risks** structure. The spec is the
source of truth; the plan and tasks derive from it; the code is verified against the spec's
acceptance criteria.

This is not a new framework — it formalizes what `01-requirements.md` / `02-project-plan.md` already
did, and adds two rules: **the spec carries no solution**, and **every acceptance criterion is a
command, test, or metric someone can run.**

## File layout

```
proj/PXX-slug/
├── 00-*.md            optional — audits, notes, context gathered before the spec (kept)
├── 01-spec.md         WHAT & WHY. Problem, requirements, acceptance criteria. No design.
├── 02-plan.md         HOW. Technical approach, architecture decisions, phases, dependencies.
├── 03-tasks.md        Ordered, checkboxed, individually testable units of work.
├── 04-risks.md        Risks with impact / probability / mitigation / acceptance.
└── NN-phase-report.md written when a phase closes (evidence, deltas, decisions)
```

Legacy projects (`P1`–`P10`) keep `01-requirements.md` / `02-project-plan.md` / `03-risks.md` until
they are next touched; new and reframed projects use the names above.

## `01-spec.md` — the contract

- **Problem statement** — the gap, in terms of observed behavior or missed capability.
- **Requirements** — `FR-n` (functional) / `NFR-n` (non-functional). Each is a *what*, not a *how*.
  "The KG must expose typed relations for an entity" — yes. "Use a recursive CTE" — no, that's `02-plan.md`.
- **Acceptance criteria** — the discriminating rule. **Each one names how it is checked:**
  a shell command, a test path, a benchmark + threshold, or a manual check with a defined pass bar.
  Example: `AC-1: `grep -rniE "neo4j|qdrant" docs/*.md` returns only lines under a "Historical" heading.`
- **Out of scope** — what this project explicitly does not touch, with a pointer to where it lives.
- **Current state** — the files, tables, endpoints the project starts from.

Rule: if you can't write the acceptance criterion as something runnable, the requirement is too
vague — sharpen it.

## `02-plan.md` — the approach

- Technical approach and the **architecture decisions** it commits to (with the alternative rejected
  and why — one line each).
- **Phases** with an *exit* per phase (usually one or more acceptance criteria from the spec).
- **Dependencies** — inbound (what must exist first) and outbound (what waits on this).
- Effort estimate per phase.

## `03-tasks.md` — the breakdown

- Ordered list, `[ ]` / `[~]` / `[x]` / `[-]`.
- Each task is small enough to land in one commit/PR and **names its own check**
  (test to add, command to run, doc to update).
- Group by phase. A task that can't state how it's verified is not ready — split or specify it.

## `04-risks.md`

Table: `ID | Risk | Impact | Probability | Mitigation | Acceptance` (unchanged from prior practice).

## Sync rule (enforced)

A commit that changes behavior in `src/` must touch the relevant spec **or** the relevant
`docs/*.md` in the same commit. `scripts/check_spec_sync.py` (run via `just check-specs`, and warned
by the pre-commit hook) flags commits that touch `src/alejandria/<area>/` without touching that
area's doc/spec. It warns; it does not block. Override by staging the doc, or by adding
`[skip-spec-sync]` to the commit subject for genuinely doc-irrelevant changes.

## Status vocabulary

`Planning` · `In Progress` · `Blocked` · `Review` · `Done` · `Deferred` · `Superseded`.
Project status lives in `proj/README.md`; phase/task status lives in the project's own files.

## Relationship to `docs/`

- `docs/system-spec.md` — the **current-state** spec of the whole system (what IS). Projects change
  it only when their work lands; it is never a plan.
- `docs/planning-index.md` — the map of every planning artifact and its authority/status. Read it
  first when planning docs seem to disagree.
- `docs/roadmap.md` — the priority-ordered incubator list. Points into `proj/`.
- Per-feature `docs/*.md` (architecture, search, kg, …) derive from `system-spec.md`; keep them in sync.
