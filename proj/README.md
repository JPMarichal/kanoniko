# Alejandria Project Portfolio

This directory contains the project portfolio for Alejandria's next generation of features. Each subdirectory represents an independent project with its own requirements, plan, and deliverables.

## Projects (Priority Order)

| # | Project | Priority | Status | Dependencies |
|---|---------|----------|--------|--------------|
| P1 | [Scripture Structure: Long Chain](P1-scripture-structure/) | Highest | Planning | None |
| P2 | [Scripture Refresh Pipeline](P2-scripture-refresh/) | High | Planning | None |
| P3 | [ETL Templates](P3-etl-templates/) | High | Planning | None |
| P4 | [Corpus Expansion](P4-corpus-expansion/) | High | Planning | P3 |
| P5 | [Chat Client UI](P5-chat-client-ui/) | Medium | Planning | None |
| P6 | [Advanced Relations](P6-advanced-relations/) | Medium | Planning | P1 |
| P7 | [Deep Disambiguation](P7-deep-disambiguation/) | Medium | Planning | None |
| P8 | [Synthesis Engine](P8-synthesis-engine/) | Lower | Planning | P5, P6 |
| P9 | [Fine-Tuning](P9-fine-tuning/) | Lower | Planning | None |

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
