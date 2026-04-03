---
name: Pre-seed known data before expensive discovery
description: Never rely on expensive automated phases (KG extraction, full corpus scan) to discover what we already know — pre-insert known relationships and target specific paths
type: feedback
---

When preparing new material for the corpus, the preparation workflow already identifies relationships (authorship, doctrinal references, cross-references, categorization). These known facts must be pre-seeded into the system (KG, indexing paths) BEFORE launching expensive automated phases.

**Why:** Phase 3 KG extraction and full corpus scanning are the most expensive operations. Relying on them to "discover" what we already determined during preparation wastes hours of compute. Similarly, SHA-256 change detection scanning ~8,000 files to find 775 new ones is wasteful when we know exactly which paths are new.

**How to apply:**
1. **Indexing:** Always use `POST /index/ingest` with explicit paths, never `POST /index/trigger` for additions. The paths list should be prepared as part of the corpus addition workflow.
2. **KG:** Pre-insert known relationships (authorship, TEACHES, REFERENCES, DATED_TO, etc.) directly into Neo4j before indexing. Phase 3 then only discovers additional relationships from text analysis — the long tail.
3. **General principle:** If a preparation step already produced knowledge, that knowledge feeds forward into the system directly. Automated discovery is for the unknown, not for re-deriving the known.
