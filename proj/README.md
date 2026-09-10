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

Each project contains numbered documents for consistent ordering:

```
01-requirements.md    — What needs to be built and why
02-project-plan.md    — Phases, milestones, deliverables, risks
03-design.md          — Technical design and architecture decisions (when applicable)
```

Additional documents may be added as projects progress (e.g., `04-test-plan.md`, `05-deployment.md`).

## How to Use

1. Read `01-requirements.md` to understand the project scope
2. Read `02-project-plan.md` to see the implementation strategy
3. When starting a project, update its status in this README
4. Create additional documents as needed during implementation
