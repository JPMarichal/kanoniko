# Alejandria Project Portfolio

This directory contains the project portfolio for Alejandria's next generation of features. Each subdirectory represents an independent project with its own requirements, plan, and deliverables.

> **2026-09 program overlay:** the structural-debt and 2026-tech initiatives are sequenced in
> [`docs/improvement-program-2026.md`](../docs/improvement-program-2026.md) (rationale in
> [`docs/improvement-analysis-2026.md`](../docs/improvement-analysis-2026.md)). New projects **P0**,
> **P11**, **P12** and work item **WI-3** come from that analysis. Feature projects P5/P8 are gated
> on P11+P12.

## Projects (Priority Order)

| # | Project | Priority | Status | Dependencies |
|---|---------|----------|--------|--------------|
| P0 | [Documentation Sync & Cleanup](P0-postgres-cutover/) | Medium | In Progress (A0 ✅ — Postgres migration confirmed done & 31/31 parity; only doc debt remains) | None |
| P11 | [Retrieval Modernization](P11-retrieval-modernization/) | **High** | Planning | — |
| P12 | [KG Extraction v2](P12-kg-extraction-v2/) | **High** | Planning | — |
| P1 | [Scripture Structure: Long Chain](P1-scripture-structure/) | Highest | Complete | None |
| P2 | [Scripture Refresh Pipeline](P2-scripture-refresh/) | High | Complete | None |
| P3 | [ETL Templates](P3-etl-templates/) | High | **Reactivate** (was Deferred) | None |
| P4 | [Corpus Expansion](P4-corpus-expansion/) | High | Complete / ongoing | P3 |
| P5 | [Chat Client UI](P5-chat-client-ui/) | Medium | Planning | P11, P12 |
| P6 | [Advanced Relations](P6-advanced-relations/) | Medium | Partial — relation extraction moved to P12; P6 keeps Layer 2/3 parallelism + NER→gazetteer loop | P1 ✅, P12 |
| P7 | [Deep Disambiguation](P7-deep-disambiguation/) | Medium | Phase 1 ✅ + gazetteer cleanup (LLM + profile phases deferred) | P12 |
| P8 | [Synthesis Engine](P8-synthesis-engine/) | Lower | Planning | P5, P6 |
| P9 | [Fine-Tuning](P9-fine-tuning/) | Lower | Deferred — absorbed by P11 (better base model + reranker + contextual retrieval, not fine-tuning) | None |
| P10 | [Handbook KG Model](P10-handbook-kg-model/) | Medium | Complete (LLM enrichment deferred) | None (benefits from P6 ✅) |
| P13 | Genealogías Escriturales (renumbered from "P10" in `docs/roadmap.md`) | Medium | Planning | P12 |

## Document Naming Convention

Spec-driven — full rules in [`CONVENTIONS.md`](CONVENTIONS.md); template in [`_TEMPLATE/`](_TEMPLATE/).

```
01-spec.md      — WHAT & WHY: problem, requirements, acceptance criteria (each with a runnable check). No design.
02-plan.md      — HOW: approach, architecture decisions, phases, dependencies.
03-tasks.md     — Ordered, checkboxed, individually testable units; each names its check.
04-risks.md     — Risk / impact / probability / mitigation / acceptance.
00-*.md         — Optional pre-spec context (audits, notes).
NN-phase-report.md — Written when a phase closes.
```

**Legacy projects (P1–P10)** keep `01-requirements.md` / `02-project-plan.md` / `03-risks.md` until
next touched. **P0, P11, P12** use the spec-driven names above.

## How to Use

1. Read `01-spec.md` (or `01-requirements.md` for legacy projects) for scope + acceptance criteria
2. Read `02-plan.md` for the approach; `03-tasks.md` for the work breakdown
3. When starting a project, update its status in this README
4. Write `NN-phase-report.md` when a phase closes; keep `03-tasks.md` checkboxes current
