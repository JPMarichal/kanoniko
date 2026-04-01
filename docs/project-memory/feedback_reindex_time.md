---
name: Full reindex takes 7+ hours
description: Full reindex is extremely expensive (~7h not 45min); always prefer incremental; never trigger full reindex casually
type: feedback
---

Full reindex takes 7+ hours, not 45 minutes as initially estimated. It was described as "una pesadilla".

**Why:** The embedding step is CPU-bound (no GPU in Docker yet — GPU Docker engine installation in progress as of 2026-04-01). 33,990 chunks at current speed is very slow.

**How to apply:** Never trigger a full reindex unless absolutely necessary. Always confirm incremental-only. When making corpus changes, ensure SHA-256 change detection works so only modified files are re-processed. A second Docker engine with GPU is being installed to mitigate this.
