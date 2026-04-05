---
name: book-discovery
description: Discover and prioritize public-domain books for the Alejandria corpus. MTP-first workflow — check Mormon Texts Project catalog, then Gutenberg, then archive.org OCR.
user_invocable: true
---

# Book Discovery Workflow (MTP-First)

Use this workflow when adding public-domain books (pre-1930, LDS authors) to the corpus.
The key insight: **Mormon Texts Project (MTP) is the upstream producer** of most LDS texts
on Gutenberg. Checking MTP first reveals what's available as clean transcriptions, avoiding
noisy archive.org OCR.

## Step 1 — MTP Catalog Check

Search the Mormon Texts Project catalog to see what's available as volunteer-transcribed text.

```
Web search: site:mormontext.org "{author name}"
Web search: site:mormontext.org "{book title}"
```

MTP texts are clean human transcriptions — no OCR artifacts. Most are also uploaded to
Project Gutenberg with the same structure.

**Output:** List of titles available on MTP, with Gutenberg IDs if linked.

## Step 2 — Gutenberg Cross-Reference

For each MTP title, find the Gutenberg ID:

```
Web search: site:gutenberg.org "{book title}" "{author}"
```

Or use the Gutendex API:
```bash
curl "https://gutendex.com/books/?search=roberts+new+witness"
```

**Output:** Map of title -> Gutenberg ID. Books found here go to the Gutenberg download
pipeline (`/gutenberg` skill).

## Step 3 — Remaining Books Assessment

Books NOT on MTP/Gutenberg need alternative sources. Check in order:

1. **Archive.org** — DjVuTXT format (OCR, needs cleanup)
   ```bash
   python scripts/download_archive_org.py --list-books
   # Or search: https://archive.org/search?query=creator%3A%22{author}%22
   ```
2. **BYU WordCruncher** — CC BY 4.0 but locked in ETBU binary format (last resort)
3. **Church Historians Press** — some titles freely available online

**Output:** Source assignment for each remaining title + quality notes.

## Step 4 — Batch Planning

Group books by source and download method:

| Source | Script | Quality | Priority |
|--------|--------|---------|----------|
| Gutenberg (via MTP) | `download_gutenberg.py` | Clean | First |
| Archive.org | `download_archive_org.py` | OCR, needs cleanup | Second |
| Manual transcription | — | Best but slow | Last resort |

For each book, note:
- Chapter structure (regular chapters vs essay collections vs sections-per-part)
- Special flags needed: `sequential_numbering`, `_WORD_TO_NUM`, `has_toc`
- Whether the book needs a custom `chapter_pattern`

## Step 5 — Configure and Download

### Gutenberg books
Add `BOOK_CONFIGS` entry to `scripts/download_gutenberg.py`, then:
```bash
python scripts/download_gutenberg.py --book-id {id} --dry-run
python scripts/download_gutenberg.py --book-id {id}
```

### Archive.org books
Add item config to `scripts/download_archive_org.py`, then:
```bash
python scripts/download_archive_org.py --item-id {id} --dry-run
python scripts/download_archive_org.py --item-id {id}
```

## Step 6 — Verify and Commit

1. Spot-check first and last chapters for content quality
2. Check for spurious chapters (embedded text matching chapter patterns)
3. Verify chapter count matches expected TOC
4. Commit per batch (group by author or source)

## Known Gotchas

- **Essay/article collections** (Defense of the Faith, Scrap Book of Mormon Literature)
  don't have regular chapter structure — need custom splitting logic per book
- **Sequential numbering**: Books where section numbers restart per Part need
  `sequential_numbering: True` to avoid filename collisions
- **Word-spelled chapters**: Some books use "CHAPTER ONE" instead of "CHAPTER I" —
  use `_WORD_TO_NUM` support in `chapter_sort_key()`
- **TOC duplication**: Books with `has_toc: True` may have mixed casing between TOC
  and body chapter markers — test with `--dry-run` first
- **NW v3 false chapter**: Embedded Book of Mormon text within a chapter can match
  `CHAPTER I` pattern, creating spurious files — verify after download
- **HC v2 mixed casing**: History of the Church volumes can have `Chapter` (TOC)
  vs `CHAPTER` (body) — `sequential_numbering` handles this

## Example Session

```
User: "Get B.H. Roberts' books"

1. Search MTP for Roberts → find 15+ titles with Gutenberg IDs
2. Cross-reference Gutenberg → confirm IDs, note which need special config
3. Remaining (CHC 6 vols) → only on archive.org/WordCruncher
4. Batch 1: 8 easy Gutenberg books → download, verify, commit
5. Batch 2: 12 more Gutenberg (HC, remaining Seventy's) → download, commit
6. Batch 3: archive.org OCR for CHC (future, needs cleanup pipeline)
```
