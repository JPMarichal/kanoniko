---
name: Phase 5 complete — all features delivered
description: Phase 5 (Corpus + RAG) is fully closed; includes entity profiles, disambiguation, volume-diverse passages, staleness, stopword handling, profile-enriched RAG
type: project
---

Phase 5 delivered:
- Scripture download pipeline (bilingual EN/ES)
- Verse-level reference generation
- Chat endpoint with RAG (4 LLM calls per question)
- Entity profiles (two-phase: metadata + LLM generate, with disambiguation)
- Volume-diverse passage selection (round-robin across OT/NT/BoM/D&C/PGP)
- Profile staleness tracking (auto-mark after corpus changes or KG rebuild)
- Orphan cleanup (delete profiles for removed entities)
- Three-tier stopword matching (main regex, contextual phrases, cross-language)
- Language-aware stopword filtering (EN/ES separate sets)
- Profile-enriched RAG (graph context uses profile summaries)
- 18 documentation files in `docs/`

**Why:** Knowing what's complete prevents re-implementing existing features.

**How to apply:** All search modes (textual, semantic, KG) and RAG are operational. Next work comes from the project incubator (`proj/`).
