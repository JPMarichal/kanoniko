# P1 — Scripture Structure: Long Chain — Project Plan

## Phases

### Phase 1 — Data Modeling (1-2 days)
**Deliverables:**
- JSON data files for divisions, parts, and pericopae (bilingual EN/ES)
- `scripture_hierarchy.json` with the complete long-chain structure per volume
- Coverage: all 5 standard works

**Tasks:**
1. Research and document the traditional division structure for each volume
2. Create `gazetteers/scripture_divisions.json` with division → books mapping
3. Create `gazetteers/scripture_parts.json` with part groupings
4. Create `gazetteers/scripture_pericopae.json` with pericope → chapter:verse mappings
5. Bilingual names for all entries

### Phase 2 — Metadata Integration (2-3 days)
**Deliverables:**
- Extended `scripture_meta.py` with long-chain resolution
- Chunk metadata enriched with division, part, pericope fields
- Updated SQLite schema for extended metadata

**Tasks:**
1. Add `resolve_long_chain(file_path, verse_start, verse_end)` to scripture_meta.py
2. Extend chunk metadata JSON to include `division`, `part`, `pericope` fields
3. Add migration for existing chunks (populate long-chain metadata from file paths)
4. Update `build_chunk_reference()` to optionally include pericope name

### Phase 3 — API & Search (1-2 days)
**Deliverables:**
- New API endpoints for structure browsing
- Search faceting by division/pericope
- Updated search result schemas

**Tasks:**
1. `GET /scriptures/structure` — browse the hierarchy tree
2. `GET /scriptures/pericopae?book=matthew` — list pericopae for a book
3. Add `division` and `pericope` to search result metadata
4. Add `division_filter` and `pericope_filter` to search endpoints

### Phase 4 — RAG Integration (1 day)
**Deliverables:**
- RAG context includes pericope/division awareness
- Answers reference structural context when relevant

**Tasks:**
1. Include pericope names in graph context when available
2. Update system prompt to leverage structural information

## Milestones

| Milestone | Deliverable | Estimate |
|-----------|------------|----------|
| M1 | Data files complete (all divisions + pericopae, bilingual) | Day 2 |
| M2 | Metadata integration working, chunks enriched | Day 5 |
| M3 | API endpoints live, search faceting works | Day 7 |
| M4 | RAG uses structural context | Day 8 |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pericope boundaries are subjective | Medium — different traditions disagree | Use the Church's official study aids as authoritative source |
| D&C doesn't have traditional divisions | Low | Make divisions optional per volume; evaluate thematic groupings |
| Large data entry effort for pericopae | Medium | Start with major pericopae (~100), expand incrementally |

## Dependencies

- None — this project has no external dependencies

## Success Criteria

1. Every scripture chunk carries both short-chain and long-chain metadata
2. `GET /scriptures/structure` returns complete bilingual hierarchy
3. Search results can be filtered by division or pericope
4. "The Sermon on the Mount" as a pericope search returns Matthew 5-7 chunks
