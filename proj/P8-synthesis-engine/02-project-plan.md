# P8 — Synthesis Engine — Project Plan

## Phases

### Phase 1 — Comparison/T-Chart (3-4 days)
**Deliverables:**
- `POST /synthesis/compare` endpoint
- Retrieves profiles + passages for both entities, produces structured comparison
- JSON and markdown output

**Tasks:**
1. Design comparison prompt template
2. Implement retrieval strategy (profiles + key passages for each entity)
3. LLM generates structured comparison
4. Parse and validate output structure
5. Markdown rendering

### Phase 2 — Timeline (3-4 days)
**Deliverables:**
- `POST /synthesis/timeline` endpoint
- Chronological event sequence with references
- JSON and markdown output

**Tasks:**
1. Design timeline prompt template
2. Retrieve temporal data from profiles and passages
3. LLM generates ordered events with dates/references
4. Validate chronological ordering

### Phase 3 — Discourse & Article (4-5 days)
**Deliverables:**
- `POST /synthesis/discourse` and `POST /synthesis/article` endpoints
- Structured long-form output with sections and citations
- Configurable parameters (length, audience, tone)

**Tasks:**
1. Design multi-section prompt strategy (outline → sections → assembly)
2. Retrieval strategy for broad topics (multiple search queries)
3. LLM generates outline, then populates each section
4. Citation grounding verification
5. Markdown output with embedded references

### Phase 4 — Concept Map (2-3 days)
**Deliverables:**
- `POST /synthesis/concept-map` endpoint
- Structured concept graph (JSON) suitable for visualization
- Central concept with radiating connections

**Tasks:**
1. Leverage knowledge graph for initial structure
2. LLM enriches with descriptions and relation labels
3. Output as JSON graph structure (nodes + edges)

## Milestones

| Milestone | Deliverable | Estimate |
|-----------|------------|----------|
| M1 | Comparison/T-chart working | Day 4 |
| M2 | Timeline working | Day 8 |
| M3 | Discourse and article generation | Day 13 |
| M4 | Concept map, full synthesis suite | Day 16 |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM hallucination in long-form output | High | Citation grounding check; reject ungrounded claims |
| High LLM costs for long outputs | Medium | Quality tier only; caching for repeated requests |
| Output quality inconsistent | Medium | Structured prompts; iterative refinement |

## Success Criteria

1. "Compare Peter and Paul" produces a structured T-chart with 5+ dimensions
2. "Timeline of Moses" produces 10+ chronological events with references
3. All synthesis outputs have traceable citations to corpus sources
