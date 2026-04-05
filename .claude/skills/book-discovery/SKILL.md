---
name: book-discovery
description: Discover and prioritize books for the Alejandria corpus. Source hierarchy — Church site > RSC BYU > BYU Studies > MTP/Gutenberg > CCEL > Archive.org.
user_invocable: true
---

# Book Discovery Workflow

Use this workflow when adding books to the corpus. Check sources in
priority order — higher-quality sources produce cleaner text with richer
metadata.

## Source Hierarchy (always check in this order)

| Priority | Source | Script | Quality |
|----------|--------|--------|---------|
| 1 | **Church site** (churchofjesuschrist.org) | `download_manual.py` etc. | Best — API, bilingual |
| 2 | **RSC BYU** (rsc.byu.edu) | `download_rsc.py` | Very good — HTML, footnotes, per-chapter author |
| 3 | **BYU Studies** (byustudies.byu.edu) | `download_byustudies.py` | Good — RSC payload, 65 books |
| 4 | **MTP / Gutenberg** | `download_gutenberg.py` | Good — clean text, no metadata |
| 5 | **CCEL** (ccel.org) | ad-hoc | Good — XML structured |
| 6 | **Archive.org** | case-by-case | Variable — OCR, last resort |

## Step 1 — Church Site Check

Is the book on the official Church site? (manuals, conference, scriptures)

```bash
# Check if API serves it
curl -s "https://www.churchofjesuschrist.org/study/api/v3/language-pages/type/content?lang=eng&uri=/manual/{slug}" | head -50
```

If yes → use appropriate `download_*.py` script. Stop here.

## Step 2 — RSC BYU Check

Is it an academic/scholarly LDS book? Check RSC.

```bash
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_rsc.py --list-books | grep -i "{keyword}"
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_rsc.py --list-books --category 7  # Book of Mormon
```

~215 online books. If found → `/rsc-byu` skill.

## Step 3 — BYU Studies Check

Historical texts, NT Commentary, HC volumes?

```bash
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_byustudies.py --list-books | grep -i "{keyword}"
```

65 online books. If found → `/byu-studies` skill.

## Step 4 — MTP / Gutenberg Check

Public-domain (pre-1930) LDS texts?

**MTP is the upstream producer** of most LDS texts on Gutenberg. Checking
MTP first reveals clean human transcriptions (no OCR artifacts).

```
Web search: site:mormontextsproject.org "{book title}"
Web search: site:gutenberg.org "{book title}" "{author}"
```

Or use the Gutendex API:
```bash
curl "https://gutendex.com/books/?search=roberts+new+witness"
```

If found → `/gutenberg` skill.

## Step 5 — CCEL / Archive.org (last resort)

- **CCEL:** Bible dictionaries, patristic texts (ThML/XML format)
- **Archive.org:** OCR scans — variable quality. Verify before ingesting.

## Step 6 — Batch Planning

Group books by source and download method:

| Source | Script | Gotchas |
|--------|--------|---------|
| Church site | `download_manual.py` | API uri != URL path |
| RSC BYU | `download_rsc.py` | Multi-author detection automatic |
| BYU Studies | `download_byustudies.py` | RSC payload may be empty → HTML fallback |
| Gutenberg | `download_gutenberg.py` | Chapter patterns vary wildly |
| Archive.org | ad-hoc | Always verify OCR quality |

## Step 7 — Verify and Commit

1. Spot-check first and last chapters for content quality
2. Check for spurious chapters (embedded text matching chapter patterns)
3. Verify chapter count matches expected TOC
4. Commit per batch (group by author or source)

## Step 8 — Update Status

After successful download + indexing:
1. Move item from `proj/P4-corpus-expansion/04-backlog.md` → `03-corpus-inventory.md`
2. Fase 0 analysis in `fase0/` stays as permanent reference

**P4 file structure:**
- `proj/P4-corpus-expansion/03-corpus-inventory.md` — what's ingested
- `proj/P4-corpus-expansion/04-backlog.md` — what's pending + priorities
- `proj/P4-corpus-expansion/05-source-registry.md` — source catalogs (RSC, Gutenberg, BYU Studies)
- `proj/P4-corpus-expansion/fase0/{slug}.md` — Fase 0 analysis (write here BEFORE downloading)

## Known Gotchas

- **MTP proxy block:** mormontextsproject.org is blocked by Solera proxy. Use WebSearch instead of WebFetch.
- **Essay/article collections:** Need custom splitting logic per book.
- **Sequential numbering:** Books where section numbers restart per Part need `sequential_numbering: True`.
- **RSC BYU purchase-only:** Recent books show "not been released for online reading" — script auto-skips.
- **BYU Studies RSC empty:** Some chapters return empty RSC payload — fallback to HTML scraping.
- **HC volumes on both BYU Studies and Gutenberg:** BYU Studies version is better (cleaner, with metadata). Prefer it.

## Example Session

```
User: "Get the BYU NT Commentary"

1. Church site? No — these are BYU Studies publications
2. RSC BYU? No — different publisher
3. BYU Studies? YES — 4 commentary + 14 rendition volumes
4. Download: download_byustudies.py --book the-testimony-of-luke
5. Repeat for remaining volumes
6. Verify, commit
```
