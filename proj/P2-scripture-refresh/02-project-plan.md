# P2 — Scripture Refresh Pipeline — Project Plan

## Phases

### Phase 1 — API Discovery & Prototyping (2-3 days)
**Deliverables:**
- Documented Church content API endpoints and response formats
- Proof-of-concept downloader for one volume in both languages
- Mapping from API structure to corpus file structure

**Tasks:**
1. Reverse-engineer the Church content API used by scriptures.churchofjesuschrist.org
2. Document endpoints, parameters, response schemas, rate limits
3. Build prototype that downloads Genesis (EN) and Génesis (ES)
4. Validate verse numbering and text fidelity against current corpus

### Phase 2 — Full Downloader (2-3 days)
**Deliverables:**
- Complete downloader covering all volumes in EN/ES
- Change detection (diff against existing files)
- Progress reporting and error handling

**Tasks:**
1. Implement volume/book/chapter traversal for all 5 standard works
2. Handle D&C special structure (sections, not chapters; Official Declarations)
3. Handle PGP special structure (multiple short books, Articles of Faith)
4. Add SHA-256 or content-based diff against existing corpus files
5. Write change report: new/modified/unchanged/deleted counts

### Phase 3 — Pipeline Integration (1-2 days)
**Deliverables:**
- API endpoint `POST /index/refresh-scriptures`
- CLI command `alejandria refresh`
- Auto-trigger incremental indexing after refresh

**Tasks:**
1. Add refresh endpoint to `routes_index.py`
2. Add CLI command to `cli.py`
3. Chain: download → diff → write changes → trigger `pipeline.run()`
4. Return stats: files checked, changed, indexed

### Phase 4 — Scheduling & Monitoring (1 day)
**Deliverables:**
- Configurable scheduled refresh (weekly by default)
- Refresh history log

**Tasks:**
1. Add `ALEJANDRIA_REFRESH_INTERVAL_DAYS` config
2. Background scheduler or cron-compatible entry point
3. Log refresh results to SQLite (timestamp, changes, errors)

## Milestones

| Milestone | Deliverable | Estimate |
|-----------|------------|----------|
| M1 | API documented, prototype works for one volume | Day 3 |
| M2 | Full download EN/ES all volumes with change detection | Day 6 |
| M3 | API/CLI integration, auto-reindex | Day 8 |
| M4 | Scheduling, production-ready | Day 9 |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Church API changes or blocks automated access | High | Cache API documentation; implement user-agent courtesy; consider RSS/feed alternatives |
| Rate limiting causes slow downloads | Medium | Configurable delays; resume capability; parallel per-volume downloads |
| Text differences from current corpus | Medium | Careful diffing; manual review of first full refresh |
| Corporate proxy blocking downloads | Low | Existing `ca-certificates.crt` pattern handles this |

## Dependencies

- None — can proceed independently

## Success Criteria

1. `POST /index/refresh-scriptures` downloads and updates all 5 volumes in EN/ES
2. Second run with no changes writes zero files
3. Changed files automatically trigger re-indexing
4. Spanish coverage is complete (currently missing OT, NT, D&C, PGP)
