---
name: byu-studies
description: Download books from BYU Studies (byustudies.byu.edu) into the Alejandria corpus. Auto-discovers catalog, extracts via RSC payload, handles footnotes, supports series metadata.
user_invocable: true
---

# Download from BYU Studies

Download scholarly books from BYU Studies into the corpus. Uses the
Next.js RSC (React Server Components) streaming payload to extract
chapter HTML without a headless browser. Falls back to regular HTML
scraping if RSC payload is empty.

## Catalog: 65 online books

### Series

| Series | Books | Authority | Tags |
|--------|-------|-----------|------|
| History of the Church (vols 1-7) | 7 | 40 | church-history, prophet-history |
| BYU NT Commentary | 4 | 35 | new-testament, commentary, academic |
| BYU NT Commentary: New Renditions | 14 | 30 | new-testament, translation, academic |
| Charting the Scriptures | 2 | 30 | scripture-study, charts, reference |

### Individual Books (9)

- Doctrine and Covenants Contexts
- My Fellow Servants (priesthood history essays)
- Opening the Heavens (divine manifestations 1820-1844)
- Sustaining the Law (Joseph Smith legal encounters)
- The St. Louis Luminary
- The Willie Handcart Company
- Voyages of Faith (Mormon Pacific history)
- Wayward Saints (Godbeite movement)
- The Journals of William E. McLellin

## Commands

```bash
# List all 65 online books
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --list-books

# Download a specific book
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --book history-of-the-church-volume-1

# Dry run — show chapters without downloading
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --book the-testimony-of-luke --dry-run

# Filter chapters (e.g., only actual chapters, not title pages)
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --book history-of-the-church-volume-1 --filter chapter

# Skip specific chapters
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --book history-of-the-church-volume-1 --skip volume-1-title-page

# Override authority and category
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --book opening-the-heavens --authority 35 --corpus-category books
```

## How RSC extraction works

BYU Studies uses Next.js 13+ with React Server Components. Sending the
header `RSC: 1` returns a `text/x-component` streaming payload instead
of full HTML. The HTML content is embedded in a "T-blob" matching:

```
[0-9a-f]+:T[0-9a-f]+,(<.+)
```

This avoids JavaScript rendering while getting the full page content.
If the RSC payload is empty, the script falls back to regular HTML
scraping using BeautifulSoup.

## Output structure

```
corpus/en/books/{slug}/
  01-{chapter-slug}.txt          # Chapter text, [Page N] removed, notes at end
  01-{chapter-slug}.meta.json    # Metadata with series info
  02-{chapter-slug}.txt
  ...
```

## Series auto-detection

The script auto-detects series membership from the book slug and applies
appropriate defaults (author, editor, tags, authority, note). Override
with `--authority` and `--tags` if needed.

| Slug pattern | Series | Auto-applied |
|--------------|--------|--------------|
| `history-of-the-church-*` | HC | author=Joseph Smith, editor=B.H. Roberts, auth=40 |
| `*-new-rendition` | NT Renditions | auth=30 |
| `the-testimony-of-*`, `pauls-*`, etc. | NT Commentary | auth=35 |
| `charting-*` | Charting | auth=30 |

## Footnote handling

- Footnotes in `<p class="note">` or similar elements are extracted
  and placed in a "Notes" section at the end of the text.
- `[Page N]` markers from print edition are stripped.
- Footnote count is recorded in `note_count` in metadata.

## After downloading

Files are in `corpus/` but NOT indexed. To index:

```bash
curl -X POST http://localhost:4300/index/ingest
```

## Priority books for download

| Priority | Book | Notes |
|----------|------|-------|
| P0 | History of the Church vols 1-6 | Vol 7 already ingested |
| P1 | BYU NT Commentary (4 vols) | High-quality NT exegesis |
| P1 | Opening the Heavens | Divine manifestations, primary sources |
| P1 | Doctrine and Covenants Contexts | D&C historical context |
| P2 | NT New Renditions (14 vols) | Modern translations |
| P2 | Sustaining the Law | Legal history |
| P3 | Remaining individual books | Lower priority |
