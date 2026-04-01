---
name: Scripture Study Aids Inventory
description: Complete inventory of official LDS scripture study aids — internal (title pages, intros, headings) and external (GEE, TG, BD, JST) — with download status
type: project
---

## Tier 1 — Internal Canonical Aids — ALL COMPLETE

### A. Chapter headings / summaries — ALREADY INDEXED
- Present in .meta.json `summary` field for every chapter
- Indexed via JSON parser into FTS5 and Qdrant

### B. Book superscriptions (Book of Mormon) — ALREADY INDEXED
- Present in .meta.json `section_headings` field on chapter 1 of each BOM book

### C. D&C Section headings — ALREADY INDEXED
- Present in .meta.json `study_intro` field for each section

### D. Volume-level introductory material — DOWNLOADED 2026-03-31
- 29 files (15 EN + 14 ES) via `scripts/scrape_introductions.py`
- BOM: title-page, bofm-title, introduction, testimony-three-witnesses, testimony-eight-witnesses, testimony-joseph-smith, explanation
- D&C: title-page, introduction, chronological-order
- PGP: title-page, introduction; Facsimiles already existed
- OT: title-page (EN+ES), epistle-dedicatory (EN only, KJV exclusive)
- NT: title-page (EN+ES)

---

## Tier 2 — External Study Aids — HIGH PRIORITY COMPLETE

### Downloaded 2026-03-31

| Aid | EN | ES | Script |
|-----|----|----|--------|
| Guide to the Scriptures (GEE) | 813 entries | 810 entries | `scrape_study_aids.py --aid gs` |
| Topical Guide | 3,513 entries | N/A (in GEE ES) | `scrape_study_aids.py --aid tg` |
| Bible Dictionary | 1,275 entries | N/A (in GEE ES) | `scrape_study_aids.py --aid bd` |
| JST Appendix | 94 chapters | 94 chapters | `scrape_jst.py` |
| GEE synonym mappings | 145 redirects | — | `_see-also-mappings.json` |

Corpus locations:
- `corpus/{en,es}/study-aids/guide-to-scriptures/`
- `corpus/en/study-aids/topical-guide/`
- `corpus/en/study-aids/bible-dictionary/`
- `corpus/{en,es}/study-aids/jst-appendix/`

### Not yet downloaded (lower priority)

| Aid | Notes |
|-----|-------|
| Reference Guide to Holy Bible | Both EN+ES |
| Bible Chronology | Both EN+ES |
| Harmony of the Gospels | Both EN+ES |
| Bible Maps / Photos | Visual content — low priority |
| Church History Maps / Photos | Visual content — low priority |
| Abbreviations | Both EN+ES |
| Index to Triple Combination | EN only |
| Reference Guide to BOM | EN only |

**Note:** GEE in Spanish consolidates Topical Guide + Bible Dictionary + Index into one work.

**Why:** Study aids provide doctrinal context, cross-references, and definitions that enrich RAG answers beyond raw scripture text.
**How to apply:** High-priority aids (GEE, TG, BD, JST) are done. Remaining aids are textual reference material (chronologies, harmonies) or visual (maps, photos) — defer until needed.
