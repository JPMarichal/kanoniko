# P10 — Handbook KG Model — Project Plan

## Overview

Extend the KG to represent the organizational/normative domain of the General Handbook. Three phases: model, extract, validate.

## Phase 1: Model Extension

**Goal:** Define and register new entity types, relation types, and bilingual gazetteers.

### Deliverables

1. **Entity type registry** — Add 9 new types (`role`, `unit`, `ordinance`, `meeting`, `record`, `fund`, `program`, `standard`, `sin_category`) to the extractor's type system
2. **Relation type registry** — Add ~30 new relation types across 5 categories (authority/governance, ordinance/procedure, financial, membership/discipline, meetings)
3. **Handbook gazetteer** — Bilingual gazetteer file with all handbook-specific entities:
   - Roles: ~40 entries (Bishop/Obispo, Stake President/Presidente de Estaca, etc.)
   - Units: ~25 entries (Ward/Barrio, Stake/Estaca, Branch/Rama, etc.)
   - Ordinances: ~20 entries (Baptism/Bautismo, Endowment/Investidura, etc.)
   - Meetings: ~15 entries (Sacrament Meeting/Reunión Sacramental, etc.)
   - Records: ~10 entries (Temple Recommend/Recomendación para el Templo, etc.)
   - Funds: ~8 entries (Tithing/Diezmo, Fast Offering/Ofrenda de Ayuno, etc.)
   - Programs: ~10 entries (Seminary/Seminario, Institute/Instituto, etc.)
   - Standards: ~8 entries
   - Total: ~136 bilingual entries

4. **Neo4j schema update** — Ensure new types work with existing indexes and constraints

### Risks
- Gazetteer collision: terms like "church", "temple", "priesthood" may conflict with existing concept entries. Needs disambiguation rules.
- Role vs. Person ambiguity: "the bishop" in scriptural text = a person; in handbook = a role. Source-aware extraction needed.

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
