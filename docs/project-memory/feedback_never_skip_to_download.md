---
name: Never skip preparation before corpus download
description: After inventory, always follow full preparation workflow (classify, authority, KG analysis, script design) before any download — never suggest jumping to download
type: feedback
---

After completing a corpus material inventory, NEVER suggest proceeding directly to download. The full preparation workflow must be followed:

1. Classify materials and define corpus directory structure
2. Define authority levels for each category
3. KG impact analysis (what entities/relations will be created)
4. Design/adapt download script (API vs HTML, TOC discovery, dry-run)
5. Only then: execute download

**Why:** The user corrected this — the preparation workflow is institutionalized and documented in `procedure_corpus_addition.md` and `reference_church_site_download_patterns.md`. Skipping to download risks misclassification, wrong authority, and wasted reprocessing.

**How to apply:** After any inventory, the next step is always "let's prepare" — classification, authority, script design. Present a preparation plan, not a download prompt.
