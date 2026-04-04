# Alejandria — Project Backlog

## Purpose

This document formalizes the **incubator** as the project's backlog. After closing Phase 5 (Corpus + RAG), the monolithic "Phase 6" was decomposed into 9 independent projects, each self-contained with its own requirements and implementation plan.

The incubator replaces the traditional phase-based roadmap with a **priority-ordered backlog** that can be worked incrementally without sequential dependencies blocking progress.

## Backlog Management

### Priority Tiers

| Tier | Projects | Rationale |
|------|----------|-----------|
| **Highest** | P1 Scripture Structure | Foundation: enriches every subsequent feature with structural metadata |
| **High** | P2 Scripture Refresh, P3 ETL Templates, P4 Corpus Expansion | Corpus quality and completeness — the system is only as good as its data |
| **Medium** | P5 Chat Client UI, P6 Advanced Relations, P7 Deep Disambiguation, P10 Handbook KG Model | User experience and knowledge depth — value multipliers |
| **Lower** | P8 Synthesis Engine, P9 Fine-Tuning | Advanced capabilities — build on top of a mature corpus and knowledge layer |

### Selection Criteria

When choosing the next project to start:

1. **Priority tier** — higher tiers first, but not strictly sequential
2. **Dependencies resolved** — check the dependency column in `README.md`
3. **Value/effort ratio** — within a tier, prefer projects that unlock the most downstream value
4. **Current pain points** — if a specific gap is blocking real usage, prioritize it regardless of tier

### Parallel Work

Projects within the same tier (and without mutual dependencies) can be worked in parallel. For example:
- P2 + P3 can run simultaneously (both High, independent)
- P5 + P7 can run simultaneously (both Medium, independent)
- P1 should complete before P6 (P6 depends on P1)

### Status Tracking

Each project's status is tracked in `README.md`:

| Status | Meaning |
|--------|---------|
| **Planning** | Requirements and plan exist, work has not started |
| **In Progress** | Active development |
| **Review** | Implementation complete, under testing/review |
| **Complete** | Delivered and verified |
| **Deferred** | Deprioritized, may be revisited |

Update the status in `README.md` as projects progress. Each project directory may also contain progress notes as additional numbered documents.

## Backlog Grooming

The backlog is a living document. Priorities may shift based on:

- **User feedback** — real usage reveals which gaps matter most
- **Technical discoveries** — implementation of one project may reveal new needs or change priorities
- **Corpus growth** — as the corpus expands, some projects become more urgent (e.g., P7 disambiguation becomes critical with more ambiguous entities)
- **External changes** — API changes, model improvements, or new tools may accelerate or defer projects

When reprioritizing, update both this document and the priority table in `README.md`.

## Active Work Items

Items that don't warrant a full project but represent significant curation/enrichment work.

### WI-1: Biographical KG Curation (All Scripture Characters)

**Priority:** High — directly enables Forma T generation from KG data
**Status:** In Progress
**Parent:** P6 Advanced Relations (phases 8-14 enrichment)

**Goal:** Curate biographical relations in `relations.json` for all major scripture characters across every volume (OT, NT, BofM, D&C, PGP) so the KG can serve as the primary structured input for Formas T and entity profiles.

**Current gap:** 776 curated relations exist but biographical coverage is thin. BORN_IN and DIED_IN types have zero entries. Most characters have ≤5 biographical relations. Only Jesus Christ (7), Paul (7), and Joseph Smith (5) have meaningful biographical data.

**Scope (Tier 1 — ~58 characters):**
- **OT:** Adam, Eve, Noah, Enoch, Abraham, Sarah, Isaac, Rebecca, Jacob, Rachel, Joseph (son of Jacob), Moses, Aaron, Joshua, Samuel, David, Solomon, Elijah, Elisha, Isaiah, Jeremiah, Daniel, Melchizedek, Job, Ruth, Esther
- **NT:** Jesus Christ, Peter, John, Paul, James (son of Zebedee), James (brother of Jesus), Matthew, John the Baptist, Mary (mother of Jesus), Stephen, Barnabas, Thomas, Mary Magdalene, Luke
- **BofM:** Lehi, Sariah, Nephi, Jacob (son of Lehi), Alma the Elder, Alma the Younger, King Benjamin, Mosiah, Captain Moroni, Helaman, Samuel the Lamanite, Mormon, Moroni, Abinadi, Ammon (son of Mosiah), Brother of Jared, Ether
- **D&C/Restoration:** Joseph Smith, Oliver Cowdery, Hyrum Smith, Brigham Young, Sidney Rigdon, Emma Smith, Martin Harris

**Relation types (biographical focus):**
Existing: FATHER_OF, MOTHER_OF, BROTHER_OF, SPOUSE_OF, SON_OF, CALLED_AS, TRAVELED_TO, BORN_IN, DIED_IN, MARTYRED_AT, BAPTIZED_BY, CONVERTED_BY, SAW_IN_VISION, APPEARED_TO, CONFERRED_KEYS_TO, HOLDS_PRIESTHOOD, AUTHORED, PROPHESIED_ABOUT, TAUGHT, LIVED_IN, FOUNDED, FOREORDAINED_AS, ORDAINED_BY, BLESSED_BY, HEALED_BY

**Success criteria:**
- Every Tier 1 character has ≥8 curated biographical relations
- BORN_IN and DIED_IN populated for characters where scripture records it
- KG query for any Tier 1 character returns enough structure to generate a Forma T without corpus search

**Future tiers:** Tier 2 (~100 secondary characters), Tier 3 (remaining gazetteer entries via LLM extraction — deferred to P6 LLM phases)

## Relationship to Completed Work

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1 — Foundation | Complete | Parsers, chunker, FTS5, incremental indexing, REST API |
| Phase 2 — Semantic Search | Complete | Qdrant, multilingual embeddings, hybrid search |
| Phase 3 — Knowledge Graph | Complete | Neo4j, gazetteers, relation extraction |
| Phase 4 — MCP, CLI, Polish | Complete | MCP adapter, CLI, API refinements |
| Phase 5 — Corpus + RAG | Complete | Scripture download, verse references, chat endpoint, entity profiles, disambiguation |
| **Incubator (this backlog)** | Active | 9 projects replacing Phase 6 |

The incubator is not "Phase 6" — it is a fundamentally different model. Each project is independently scoped, planned, and deliverable. There is no single "Phase 6 complete" milestone; instead, each project has its own success criteria documented in its `01-requirements.md`.
