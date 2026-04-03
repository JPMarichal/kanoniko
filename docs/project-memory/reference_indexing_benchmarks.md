---
name: Indexing performance benchmarks and ETA calculation
description: Real benchmarks for targeted indexing by phase, ETA must be calculated from chunk count not file count
type: reference
---

## Benchmark: 2026-04-03 supplementary corpus ingest

779 files → 1,632 chunks, GPU stack (RTX PRO 500 Blackwell 6GB), KG pre-seeded.

| Phase | Duration | Rate |
|-------|----------|------|
| Phase 1 (parse + FTS) | ~4 min | ~195 files/min, ~408 chunks/min |
| Phase 2 (embeddings GPU) | ~5 sec | 7 batches, ~327 chunks/sec |
| Phase 3 (NER + KG) | ~4 min | ~408 chunks/min |
| **Total** | **~8 min** | |

## ETA calculation rules

1. **Estimate from chunk count, not file count.** A 1-page calling guide produces ~2 chunks; a 20-page manual produces ~50. Same file count, 25x difference in work.
2. **Estimate chunk count** from file content: short pages (~1-2 chunks), medium manuals (~5-10), long manuals (~20-50).
3. **Phase 2 is negligible on GPU** (~5 sec for 1,632 chunks). Only matters on CPU.
4. **Phase 3 scales with chunk text volume**, not entity count. Pre-seeded KG relations reduce discovery but don't eliminate Phase 3 time — spaCy NER still runs on every chunk.
5. **Never extrapolate from full-reindex times** (7h for 7,000 files) to targeted ingest. Targeted ingest skips file scanning, hash comparison of existing files, and backup overhead.

## Quick reference for future ETAs

| Chunk count | GPU total | CPU total (estimated) |
|-------------|-----------|----------------------|
| ~500 | ~3 min | ~10 min |
| ~1,500 | ~8 min | ~25 min |
| ~5,000 | ~25 min | ~1.5h |
| ~10,000 | ~50 min | ~3h |

These assume targeted ingest with KG pre-seeded. Full reindex adds scanning overhead + backup time.
