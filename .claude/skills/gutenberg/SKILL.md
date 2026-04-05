---
name: gutenberg
description: Download books from Project Gutenberg into the Alejandría corpus. Split into chapters, reflow text, parse footnotes, generate .meta.json.
---

# Download from Project Gutenberg

Download public-domain books from Project Gutenberg, process them into
corpus-ready chapters (.txt + .meta.json), and place them in `corpus/en/manuals/`.

## Discovery workflow

Before adding books, use the `/book-discovery` skill to check MTP catalog first,
then Gutenberg, then archive.org. This avoids wasted effort on OCR when clean
transcriptions exist.

## Pre-configured books

Run `python scripts/download_gutenberg.py --list-books` for the full list. Key entries:

| ID | Slug | Author | Notes |
|----|------|--------|-------|
| 42238 | articles-of-faith | Talmage | 24 lectures |
| 35514 | great-apostasy | Talmage | 10 chapters |
| 45149 | house-of-the-lord | Talmage | ~10 chapters |
| 47182 | vitality-of-mormonism | Talmage | 104 essays |
| 74447 | discourses-brigham-young | BY/Widtsoe | 42 chapters |
| 46202 | new-witness-for-god-vol1 | Roberts | 18 chapters |
| 47316 | new-witnesses-for-god-vol2 | Roberts | 37 chapters |
| 59951 | new-witnesses-for-god-vol3 | Roberts | 38 chapters |
| 52391 | outlines-ecclesiastical-history | Roberts | sequential |
| 49526 | missouri-persecutions | Roberts | 22 chapters |
| 35974 | corianton | Roberts | word-numbered chapters |
| 60235 | seventys-course-theology-1st | Roberts | sequential |
| 60490 | seventys-course-theology-2nd | Roberts | sequential |
| 60575 | seventys-course-theology-3rd | Roberts | sequential |
| 60491 | seventys-course-theology-4th | Roberts | sequential |
| 60492 | seventys-course-theology-5th | Roberts | 5 chapters |
| 50302 | rise-and-fall-of-nauvoo | Roberts | 45 chapters |
| 45464 | mormon-doctrine-of-deity | Roberts | 7 chapters |
| 45303 | life-of-john-taylor | Roberts | 46 chapters |
| 47091 | history-of-the-church-vol1 | Smith/Roberts | 48 chapters |
| 47192 | history-of-the-church-vol2 | Smith/Roberts | sequential |
| 47316 | history-of-the-church-vol3 | Smith/Roberts | 15 chapters |
| 60757 | history-of-the-church-vol4 | Smith/Roberts | 30 chapters |
| 60706 | history-of-the-church-vol5 | Smith/Roberts | 32 chapters |
| 60758 | history-of-the-church-vol6 | Smith/Roberts | 12 chapters |

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
