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

### Pending — prioritized

| Aid | URL | Priority | KG value | Notes |
|-----|-----|----------|----------|-------|
| Harmony of the Gospels | `/study/scriptures/harmony` | **HIGH** | Critical — explicit PARALLEL_ACCOUNT_OF between MT/MC/LC/JN + BoM/D&C parallels | 8 parts + intro; ~150 events; unique intertextuality NER cannot infer |
| Bible Chronology | `/study/scriptures/bible-chron` | **HIGH** | Period nodes + OCCURRED_DURING relations; OT (~3,000 yrs) + NT (AD 1–96) | Syncs with external history (Babylon, Rome) |
| Abbreviations | `/study/scriptures/quad` | **HIGH** | Feeds scripture ref normalizer directly | All 4 volumes; maps "1 Ne." → 1 Nephi, "A of F" → Articles of Faith, etc. |
| Reference Guide to Holy Bible | `/study/scriptures/bible-reference` | MEDIUM | Topical index (Godhead, People, Places, Events) with verse refs | Complements TG with different grouping |
| Reference Guide to Book of Mormon | `/study/scriptures/bofm-reference` | MEDIUM | Same as above for BoM; Christ, Doctrines, People, Events | TG/GEE already cover much overlap |
| Index to Triple Combination | `/study/scriptures/triple-index` | LOW | Extends TG coverage to D&C+PGP | Large volume; assess after TG/GEE use |
| Bible Maps / Photos | visual | SKIP | No text value | — |
| Church History Maps / Photos | visual | SKIP | No text value | — |

**Note:** GEE in Spanish consolidates Topical Guide + Bible Dictionary + Index into one work.
**Harmony** is unique because it includes a LDS revelation column (BoM, D&C) alongside the 4 Gospels — not available in any Protestant harmony.
