---
name: Incremental reindex workflow and performance
description: Canonical post-commit incremental workflow using git diff → /index/ingest; Phase 1 optimizations; GPU Docker available
type: feedback
---

Full reindex takes 7+ hours on CPU and is destructive — avoid it. Always use incremental.

**Canonical post-commit incremental workflow (use this, not /trigger):**

```bash
git diff --name-only HEAD~1 HEAD -- 'corpus/**/*.txt' \
  | python -c "
import sys, json, urllib.request
paths = [p[len('corpus/'):].strip() for p in sys.stdin if p.strip().startswith('corpus/')]
body = json.dumps({'paths': paths, 'force': False}).encode()
req = urllib.request.Request('http://localhost:4300/index/ingest', data=body,
      headers={'Content-Type': 'application/json'}, method='POST')
print(json.loads(urllib.request.urlopen(req).read()))
"
```

**Why git diff, not /trigger:** `/trigger` scans SHA of every file on disk (24K+ files = 20-30 min overhead before any indexing). `git diff` gives the exact new files in milliseconds.

**Phase 1 optimizations applied (2026-04-03):**
- Skip `delete_by_file` for new files (was called unconditionally before)
- Single shared SQLite connection for all Phase 1 inserts (was 2 opens/closes per file)
- Parallel parsing via `ThreadPoolExecutor(8 workers)` — FTS inserts remain serial

**Observed times (GPU, 2026-04-03):**
- 7,765 new files → ~45-90 min total on GPU
- Phase 1 (parse+FTS): dominant bottleneck, now ~5-10x faster with parallelism
- Phase 2 (embeddings on GPU): fast, batch-encoded all at once
- Phase 3 (KG/Neo4j): ~10-20 min

**How to apply:** After any corpus commit, use the git diff workflow above. Only use `/trigger` if the corpus has diverged from git (manual edits, etc.). Never use `force: true` unless doing a migration.
