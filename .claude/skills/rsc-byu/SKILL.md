---
name: rsc-byu
description: Download books from RSC BYU (rsc.byu.edu) into the Alejandria corpus. Handles single-author and multi-author (conference/symposium) volumes with per-chapter author, subtitle, section, and footnotes.
user_invocable: true
---

# Download from RSC BYU

Download scholarly books from the Religious Studies Center at BYU into
the corpus. The script handles Drupal server-rendered HTML — no headless
browser needed.

## Key features

- **Multi-author support:** Conference proceedings and symposia have an
  editor at the book level and individual authors per chapter. Both are
  captured in metadata.
- **Structured TOC parsing:** Extracts chapter title, subtitle, author,
  and section from `li.toc-item-basic` elements.
- **Footnotes included:** `p.p-note` elements are extracted and placed
  in a clearly delimited "Notes" section at the end of each chapter.
- **Citation extraction:** Formal citation paragraphs (RSC/Deseret Book)
  are captured in `.meta.json` but excluded from body text.
- **Author bio removal:** Toggle-box elements (bio + citation) are
  stripped from the text output.

## ~215 online books across 15 categories

| Cat ID | Category | Priority |
|--------|----------|----------|
| 7 | Book of Mormon | HIGH |
| 8 | Doctrine and Covenants | HIGH |
| 9 | Pearl of Great Price | HIGH |
| 10 | Bible Studies | HIGH |
| 1 | Scripture Study | HIGH |
| 2 | Church History | HIGH |
| 15 | Sidney B. Sperry Symposium | MEDIUM |
| 13 | Church History Symposium | MEDIUM |
| 309 | Book of Mormon Symposium | MEDIUM |
| 14 | Easter Conference | MEDIUM |
| 12 | Gospel Questions | MEDIUM |
| 11 | Teaching | LOW |
| 3 | Self-Help | LOW |
| 16 | Other Conferences | LOW |
| 17 | World Religions & Traditions | LOW |

## Commands

```bash
# List all online books
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_rsc.py --list-books

# List books in a specific category
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_rsc.py --list-books --category 7

# Dry run — show chapters and per-chapter authors
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_rsc.py --book illuminating-jaredite-records --dry-run

# Download a book
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_rsc.py --book illuminating-jaredite-records

# Override authority and tags
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_rsc.py --book some-slug --authority 35 --tags rsc-byu academic book-of-mormon
```

## Output structure

```
corpus/en/books/{slug}/
  01-{chapter-slug}.txt          # Chapter text with Notes section
  01-{chapter-slug}.meta.json    # Rich metadata
  02-{chapter-slug}.txt
  ...
```

## Metadata fields

Single-author book:
```json
{
  "title": "Chapter Title",
  "author": "Author Name",
  "book": "Book Title",
  "chapter": 1,
  "category": "books",
  "subcategory": "book-slug",
  "tags": ["rsc-byu", "academic"],
  "authority": 30,
  "lang": "eng",
  "source_url": "https://rsc.byu.edu/book-slug/chapter-slug",
  "source": "Religious Studies Center, BYU",
  "citation": "Formal citation from RSC...",
  "note_count": 29
}
```

Multi-author (edited volume) adds:
```json
{
  "editor": "Editor Name(s)",
  "section": "Doctrine",
  "subtitle": "Chapter Subtitle",
  "book_subtitle": "Book Subtitle"
}
```

## Access model

- **Free online:** Older/out-of-print books — full text available.
- **Purchase only:** Recent books show "not been released for online
  reading" — the script detects this and skips them.

## Multi-author detection

The script automatically detects edited volumes:
1. Book page shows "Editor(s)" near author names in `pub-title-block`
2. TOC has `div.toc-author` per chapter with `/node/ID` links
3. Chapter pages have `<h5><a href="/node/ID">Author</a></h5>`
4. Author priority: chapter page h5 > TOC author > book-level editor

## After downloading

Files are in `corpus/` but NOT indexed. To index:

```bash
curl -X POST http://localhost:4300/index/ingest
```

## Authority guidelines

| Category | Suggested authority |
|----------|-------------------|
| Scripture study (cats 1,7,8,9,10) | 30 |
| Church History (cats 2,13) | 30 |
| Symposia/Conference (cats 14,15,16,309) | 25–30 |
| Teaching/Self-Help (cats 3,11) | 25 |
| World Religions (cat 17) | 25 |
