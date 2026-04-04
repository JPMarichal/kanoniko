---
name: gutenberg
description: Download books from Project Gutenberg into the Alejandría corpus. Split into chapters, reflow text, parse footnotes, generate .meta.json.
---

# Download from Project Gutenberg

Download public-domain books from Project Gutenberg, process them into
corpus-ready chapters (.txt + .meta.json), and place them in `corpus/en/manuals/`.

## Pre-configured books

| ID | Slug | Author | Notes |
|----|------|--------|-------|
| 42238 | articles-of-faith | Talmage | 24 lectures, ~70K words |
| 35514 | great-apostasy | Talmage | 10 chapters, ~30K words |
| 45149 | house-of-the-lord | Talmage | ~10 chapters, ~30K words |
| 47182 | vitality-of-mormonism | Talmage | 104 essays, ~80K words |
| 74447 | discourses-brigham-young | BY/Widtsoe | 42 chapters, ~250K words |

## Commands

```bash
# List available pre-configured books
python scripts/download_gutenberg.py --list-books

# Download a single book
python scripts/download_gutenberg.py --book-id 42238

# Download all pre-configured books
python scripts/download_gutenberg.py --book-id 42238 35514 45149 47182 74447

# Dry run (show what would be downloaded)
python scripts/download_gutenberg.py --book-id 42238 --dry-run

# Any Gutenberg book (fetches metadata from Gutendex API)
python scripts/download_gutenberg.py --book-id 12345
```

## What the script does

1. Downloads plain text from `gutenberg.org/files/{id}/{id}-0.txt`
2. Strips Gutenberg header/footer boilerplate
3. Strips transcriber notes
4. Splits into chapters using the book's configured pattern
5. Reflows hard-wrapped lines (~75 char) into full paragraphs
6. Cleans formatting markers (`_italic_`, `=bold=`, `{page}`)
7. Parses inline footnotes (`[Footnote N: ...]`)
8. Extracts Journal of Discourses references for BY book
9. Writes `{NN}-chapter-{NN}.txt` + `.meta.json` per chapter
10. Skips already-downloaded chapters (idempotent)

## Output location

```
corpus/en/manuals/{slug}/
  01-chapter-1.txt
  01-chapter-1.meta.json
  02-chapter-2.txt
  ...
```

## After downloading

The files are in `corpus/` but NOT indexed. To index them, run incremental
ingestion when the Alejandría container is running:

```bash
curl -X POST http://localhost:4300/index/ingest
```

## Adding a new book

Edit `BOOK_CONFIGS` in `scripts/download_gutenberg.py` and add:

```python
99999: {
    "slug": "book-slug",
    "author": "Author Name",
    "category": "manuals",
    "tags": ["relevant", "tags"],
    "authority": 40,
    "chapter_pattern": r"^CHAPTER\s+([IVXLC\d]+)\.?\s*$",
    "title_offset": 2,
    "has_toc": True,
    "note": "Publication context note.",
},
```

Key fields:
- `chapter_pattern`: regex matching chapter boundary lines (capture group = chapter number)
- `title_offset`: how many lines after the chapter marker to find the title
- `has_toc`: if True, chapters appear twice (TOC + body) — script deduplicates
- `authority`: doctrinal authority score (see docs/authority-model.md)
