# P10 — Handbook KG Model — Project Plan

## Overview

Extend the KG to represent the organizational/normative domain of the General Handbook. Three phases: model, extract, validate.

## Phase 1: Model Extension ✅ Complete

**Goal:** Define and register new entity types, relation types, and bilingual gazetteers.

### Deliverables

1. ✅ **Entity types** — 6 types in `entities.json`: role (24), unit (15), ordinance (18), meeting (8), fund (5), program (10) — all bilingual EN/ES
2. ✅ **Relation types** — Already in `VALID_RELATION_TYPES` from P6: PRESIDES_OVER, REPORTS_TO, MEMBER_OF, AUTHORIZED_TO_PERFORM, MANAGES_FUND, CONDUCTS_INTERVIEW, etc.
3. ✅ **Curated relations** — 47 handbook relations in `relations.json`: PRESIDES_OVER (10), REPORTS_TO (8), AUTHORIZED_TO_PERFORM (10), PREREQUISITE_FOR (5 new), MANAGES_FUND (4), CONDUCTS_INTERVIEW (5), MEMBER_OF (5)
4. ✅ **Merged calling→role** — Consolidated duplicate "calling" type into "role" (24 unique entries)

### Risks (addressed)
- Gazetteer collision: handbook entities use distinct types (role, unit, meeting) separate from scriptural "person" and "concept"
- Role vs. Person ambiguity: source-aware extraction in Phase 2 will differentiate

## Phase 2: Extraction Patterns ✅ Complete

**Goal:** Enable the extractor to recognize handbook entities and infer normative relations.

### Deliverables

1. ✅ **Source-aware extraction** — `extractor.py` detects `manuals/general-handbook` in `source_file`, activates handbook-specific entity matching and relation patterns
2. ✅ **Normative relation patterns** — 4 regex patterns:
   - "The [role] presides over the [unit]" → `PRESIDES_OVER`
   - "[Role] reports to [role]" → `REPORTS_TO`
   - "authorized by the [role]" → `REQUIRES_APPROVAL_OF`
   - "with approval of [role]" → `REQUIRES_APPROVAL_OF`
3. ✅ **Handbook-specific chunking** — `chunk_handbook()` in `chunker.py` respects `##`/`###`/`####` section boundaries, preserves headings, sets section reference (e.g., "8.1.2")
4. ✅ **Pipeline routing** — `_parse_file_cpu()` routes handbook files to `chunk_handbook()` automatically
5. ✅ **Fixed calling→role** — All co-occurrence rules updated from "calling" to "role" type
6. ✅ **Enhanced co-occurrence inference** — New type combinations: role+meeting, role+fund, role+program, directional role+role

### Risks (mitigated)
- Pattern fragility: regex handles common forms; LLM extractor supplements with broader VALID_RELATION_TYPES coverage

## Phase 3: Validation & Enrichment ✅ Complete

**Goal:** Verify extracted graph, fill gaps, and establish update workflow.

### Deliverables

1. ✅ **Curated core relations** — 47 curated relations in `relations.json` (Phase 1) covering authority chains, ordinance sequences, financial administration
2. ✅ **Validation script** — `scripts/validate_handbook_kg.py` with 5 integrity checks:
   - Every unit has a presiding role
   - Ordinance prerequisite chain is acyclic
   - All roles have at least one PRESIDES_OVER or REPORTS_TO
   - Authority chain completeness (who can authorize what)
   - Reporting chain depth analysis
3. ✅ **Update workflow** — Handbook content follows standard incremental reindex:
   - Re-download → SHA-256 change detection → incremental reindex
   - `chunk_handbook()` auto-routes handbook files
   - Source-aware extractor applies handbook-specific patterns
4. ⬜ **LLM enrichment pass** — Deferred (same as P6 LLM extraction; will run when Sonnet tier is available)

## Effort Estimate

| Phase | Effort | Notes |
|-------|--------|-------|
| Phase 1 | Medium | Gazetteer creation is mechanical but needs care for bilingual aliases |
| Phase 2 | Medium-High | Pattern extraction needs testing across all 41 chapters |
| Phase 3 | Low-Medium | Mostly validation and curation |

## Milestone Sequence

```
Phase 1 ──→ Phase 2 ──→ Phase 3
(model)     (extract)    (validate)
```

Phases are sequential — each builds on the previous.
