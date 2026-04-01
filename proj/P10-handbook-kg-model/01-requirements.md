# P10 — Handbook KG Model — Requirements

## Problem Statement

The General Handbook (Manual General) was added to the corpus (2026-03-31) and is being indexed for FTS5 + Qdrant search. However, the current KG model was designed for **scriptural/narrative** content: persons, places, peoples, concepts, and relations like family, prophecy, authorship, and geography.

The handbook is a **normative/organizational** document. Its content operates in domains the KG cannot currently represent:

- **Organizational hierarchy**: stakes, wards, branches, quorums, auxiliaries, and who presides/reports/delegates
- **Roles and callings**: bishop, stake president, Relief Society president — not persons but *positions*
- **Ordinances as structured procedures**: who can perform them, who authorizes them, prerequisites, sequences
- **Policies and rules**: requirements, prohibitions, exceptions, conditions
- **Financial instruments**: tithing, fast offerings, missionary fund, budgets, audits
- **Records and documents**: membership records, recommend types, reports, certificates
- **Membership states and transitions**: active, restricted, withdrawn, restored
- **Disciplinary processes**: confession, councils, restrictions, restoration
- **Meetings**: types, frequency, who presides, who attends, purpose
- **Missionary service**: types, eligibility, recommendation flow, assignment
- **Medical/legal entities**: disability accommodations, abuse reporting, legal compliance

Without KG modeling, the handbook's rich relational structure is invisible to the graph — questions like "Who can authorize a baptism?", "What are the prerequisites for a temple recommend?", or "What is the bishop's relationship to the Aaronic Priesthood?" cannot be answered from the graph.

## Scope

Extend the Alejandría KG model to represent the normative/organizational domain introduced by the General Handbook, while preserving full backward compatibility with the existing scriptural model.

### In Scope

1. New entity types for organizational/normative content
2. New relation types for authority, hierarchy, procedure, and policy
3. Gazetteer entries for handbook-specific entities (bilingual EN/ES)
4. Extraction patterns for the handbook's structured content
5. Integration with existing KG infrastructure (Neo4j, extractor, pipeline)

### Out of Scope

- Modifying the chat/RAG pipeline (it already benefits from FTS5/Qdrant)
- UI for browsing organizational structure (future, P5)
- LLM-based extraction of normative rules as first-class graph objects (future, P8)

## Entity Type Analysis

### New Entity Types Needed

| Type | Description | Examples |
|------|-------------|---------|
| `role` | Ecclesiastical positions/callings — not individual persons but the office itself | Bishop, Stake President, Relief Society President, Patriarch, Mission President, Sealer |
| `unit` | Organizational units at all levels | Ward, Stake, Branch, District, Mission, Quorum, Relief Society, Primary, Sunday School, Young Women |
| `ordinance` | Sacred acts performed by priesthood authority | Baptism, Confirmation, Sacrament, Endowment, Sealing, Ordination, Setting Apart, Patriarchal Blessing |
| `meeting` | Formal gatherings with defined structure | Sacrament Meeting, Ward Council, Bishopric Meeting, Stake Conference, Ward Youth Council |
| `record` | Administrative documents and artifacts | Membership Record, Temple Recommend, Tithing Declaration, Ordinance Certificate |
| `fund` | Financial instruments and contribution categories | Tithing, Fast Offering, Missionary Fund, Ward Budget, General Missionary Fund |
| `program` | Organizational programs and curricula | Come Follow Me, Seminary, Institute, Children and Youth, Self-Reliance |
| `standard` | Worthiness standards, behavioral norms, policy rules | Temple Worthiness, Chastity Standard, Word of Wisdom, Tithing |
| `sin_category` | Categories of serious sin requiring specific procedures | (As defined in chapter 32: abuse types, sexual immorality categories, fraud, apostasy, etc.) |

### Existing Types That Absorb Handbook Content

| Existing Type | Handbook Content It Absorbs |
|---------------|---------------------------|
| `concept` | Doctrinal principles referenced in policies (Atonement, Priesthood Keys, Repentance) |
| `person` | Historical figures cited in handbook (Jesus Christ, Joseph Smith, Paul) |
| `scripture` | Scripture references throughout the handbook |
| `period` | Not heavily used in handbook |

## Relation Type Analysis

### New Relations Needed

#### Authority & Governance (10)

| Relation | From → To | Example |
|----------|-----------|---------|
| `PRESIDES_OVER` | role → unit | Bishop → Ward |
| `REPORTS_TO` | role → role | Bishop → Stake President |
| `DELEGATES_TO` | role → role | Bishop → Counselors |
| `AUTHORIZES` | role → ordinance | Stake President → Ordination to Elder |
| `HOLDS_KEYS_FOR` | role → ordinance/unit | Bishop → Ward ordinances |
| `CALLED_BY` | role → role | Bishop → Stake President |
| `SET_APART_BY` | role → role | Ward clerk → Bishopric member |
| `SUPERVISES` | role → unit/role | Bishop → Relief Society President |
| `MEMBER_OF` | role → unit | Bishop → Bishopric; Elder → Elders Quorum |
| `PART_OF` | unit → unit | Ward → Stake; Quorum → Ward |

#### Ordinance & Procedure (8)

| Relation | From → To | Example |
|----------|-----------|---------|
| `PERFORMS` | role → ordinance | Priest → Sacrament blessing |
| `PREREQUISITE_FOR` | ordinance → ordinance | Baptism → Confirmation → Priesthood → Endowment → Sealing |
| `REQUIRES` | ordinance → standard | Temple Recommend → Temple Worthiness |
| `RENEWS` | ordinance → ordinance | Sacrament → Baptismal Covenant |
| `RECEIVES` | (generic, for member → ordinance patterns) | |
| `WITNESSES` | role → ordinance | (Two witnesses required for baptism) |
| `RECORDS_EVENT` | role → ordinance | Clerk → Baptism record |
| `APPROVES` | role → ordinance/record | Bishop → Temple Recommend |

#### Financial (4)

| Relation | From → To | Example |
|----------|-----------|---------|
| `MANAGES` | role → fund | Bishop → Fast Offerings |
| `CONTRIBUTES_TO` | (generic direction) | Member → Tithing |
| `AUDITS` | role → fund | Audit Committee → Ward Finances |
| `FUNDED_BY` | program → fund | Missionary service → Missionary Fund |

#### Membership & Discipline (5)

| Relation | From → To | Example |
|----------|-----------|---------|
| `RESTRICTS` | (council action) → ordinance | Membership Council → Sacrament participation |
| `RESTORES` | role → (membership state) | Stake President → Full membership |
| `CONVENES` | role → meeting | Bishop → Ward Membership Council |
| `REFERS_TO` | role → role | Bishop → Stake President (for stake-level councils) |
| `TRIGGERS` | sin_category → meeting | (Certain sins mandate a membership council) |

#### Meetings (3)

| Relation | From → To | Example |
|----------|-----------|---------|
| `CONDUCTS` | role → meeting | Bishop → Sacrament Meeting |
| `ATTENDS` | role → meeting | Elders Quorum President → Ward Council |
| `SCHEDULED_IN` | meeting → unit | Ward Council → Ward |

### Existing Relations That Apply to Handbook

| Existing Relation | Handbook Usage |
|-------------------|---------------|
| `TAUGHT` | Roles teaching principles |
| `HOLDS_PRIESTHOOD` | Roles requiring priesthood |
| `CONFERRED_KEYS_TO` | Key transfer patterns |
| `COVENANT_WITH` | Ordinance/covenant relationships |

## Non-Functional Requirements

### NFR-1: Backward Compatibility
Adding new entity types and relations must not break existing scriptural graph data or queries. The extractor should handle both domains transparently.

### NFR-2: Bilingual Gazetteers
All handbook entities need EN/ES aliases:
- Bishop / Obispo
- Stake President / Presidente de Estaca
- Relief Society / Sociedad de Socorro
- Sacrament Meeting / Reunión Sacramental
- etc.

### NFR-3: Authority Metadata
Handbook-derived KG relations should carry `confidence: "metadata"` (they come from an authoritative normative source, not inference) and `source: "general-handbook"`.

### NFR-4: Repeatability
When the handbook is re-downloaded (it updates a few times per year), re-running KG extraction should update relations cleanly without duplication.

## Dependencies

- **None blocking** — can start independently
- **Benefits from P6** (Advanced Relations) infrastructure if P6 runs first, but P6 is not required
- **Benefits from P3** (ETL Templates) for handbook update automation

## Success Criteria

1. New entity types and relations are queryable in Neo4j
2. Questions like "Who presides over a ward?" return structured graph answers
3. Handbook re-download + reindex cleanly updates the graph
4. Existing scriptural KG is unaffected
5. Bilingual entity recognition works for handbook terms
