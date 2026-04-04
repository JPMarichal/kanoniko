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

## Phase 2: Extraction Patterns

**Goal:** Enable the extractor to recognize handbook entities and infer normative relations.

### Deliverables

1. **Source-aware extraction** — The extractor should know when it's processing handbook content (via `source_file` path) and apply handbook-specific logic
2. **Normative relation patterns** — Pattern-based extraction for common handbook structures:
   - "The [role] presides over the [unit]" → `PRESIDES_OVER`
   - "The [role] is responsible for [X]" → `RESPONSIBLE_FOR`
   - "The [role] may delegate to [role]" → `DELEGATES_TO`
   - "[Role] reports to [role]" → `REPORTS_TO`
   - "Authorization from [role] is required" → `AUTHORIZES`
   - "[Ordinance] is prerequisite for [ordinance]" → `PREREQUISITE_FOR`
3. **Handbook-specific chunking** — Handbook sections are structured by numbered subsections (7.1.2, 38.6.13). The chunker should respect these boundaries for better relation extraction.

### Risks
- Pattern-based extraction is fragile. The handbook's language is varied — "presides", "has responsibility for", "oversees", "leads" all express the same relation. May need LLM assist (Phase 3).

## Phase 3: Validation & Enrichment

**Goal:** Verify extracted graph, fill gaps, and establish update workflow.

### Deliverables

1. **Curated core relations** — Manually verify the ~50 most important organizational relations (role→unit hierarchy, ordinance prerequisites, authority chains). Add to `relations.json` as `confidence: "curated"`.
2. **LLM enrichment pass** — Use the existing `relation_extractor_llm.py` to extract relations from handbook chunks that pattern matching missed. Handbook text is explicit enough for high-confidence LLM extraction.
3. **Update workflow** — Document the re-download + reindex process for handbook updates:
   - `scrape_handbook.py --lang all` → downloads latest
   - Incremental reindex detects SHA-256 changes → re-indexes changed chapters
   - KG extractor processes new/changed chunks → updates graph
4. **Validation queries** — Neo4j Cypher queries that verify graph integrity:
   - Every unit has a presiding role
   - Ordinance prerequisite chain is acyclic
   - All roles have at least one `PRESIDES_OVER` or `REPORTS_TO`

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
