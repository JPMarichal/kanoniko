# External Source Scrapers — Reference

## Source Hierarchy (quality order)

1. **Church site** (churchofjesuschrist.org) — API, bilingual, canonical
2. **RSC BYU** (rsc.byu.edu) — ~215 books, Drupal HTML, per-chapter author, footnotes
3. **BYU Studies** (byustudies.byu.edu) — 65 books, Next.js RSC payload
4. **MTP / Gutenberg** — ~129 LDS titles, proofread 2x plain text
5. **CCEL** (ccel.org) — Bible dictionaries, ThML/XML
6. **Archive.org** — OCR, last resort

## Scripts and Skills

| Script | Skill | Source | Key Feature |
|--------|-------|--------|-------------|
| `download_rsc.py` | `/rsc-byu` | rsc.byu.edu | Multi-author support (conferences/symposia), structured TOC, footnotes |
| `download_byustudies.py` | `/byu-studies` | byustudies.byu.edu | RSC payload extraction, series auto-detection, 65-book catalog |
| `download_gutenberg.py` | `/gutenberg` | gutenberg.org | 62 pre-configured books, chapter splitting, footnote parsing |
| `download_manual.py` | — | churchofjesuschrist.org | Church API v3, bilingual |

## RSC BYU Key Details

- **Site stack:** Drupal, server-rendered HTML, no headless browser needed
- **Book page:** `div.pub-title-block` has `<h2>` title + `<h4>` subtitle + author links
- **TOC:** `li.toc-item-basic` with `div.toc-title`, `div.toc-subtitle`, `div.toc-author`
- **Chapter page:** `div.content-title-pane` (h3 title, h5 author) + `div.content-body-pane.rsc-markup`
- **Footnotes:** `p.p-note` in body pane, `a.a-ref` inline, `toggle-box` = citation+bio (removed)
- **Multi-author:** `is_edited=True` when "Editor(s)" in pub-title-block text
- **Access:** Free online (older) vs purchase-only ("not been released for online reading")

## BYU Studies Key Details

- **Site stack:** Next.js 13+ with React Server Components
- **RSC trick:** Send `RSC: 1` + `Accept: text/x-component` headers → get streaming payload
- **T-blob regex:** `[0-9a-f]+:T[0-9a-f]+,(<.+)` extracts HTML content
- **Catalog page:** `/online-books` lists all 65 books with series groupings
- **Book page:** `/online-book/{slug}` lists chapters as links matching `/{slug}/{ch-slug}`
- **Series:** HC (7 vols), NT Commentary (4), NT Renditions (14), Charting (2), Individual (9)
- **Fallback:** Regular HTML scraping if RSC payload is empty

## MTP Key Details

- **All MTP texts are on Gutenberg** — no exclusive content
- **~94 ebooks produced**, all proofread 2x
- **No Journal of Discourses** — explicitly declined by project
- **Proxy blocked:** mormontextsproject.org blocked by Solera; use WebSearch not WebFetch
- **Workflow:** `/book-discovery` skill checks MTP before Gutenberg

## Backlog Counts (verified 2026-04-05)

- RSC BYU: 214 unique online books across 15 categories (full inventory in backlog)
- BYU Studies: 38 books (37 not yet in corpus) — was estimated 65, actual catalog has 38
- MTP/Gutenberg: ~89 LDS titles not yet in corpus
- Church site: ~51 items in priority tables (P0-P6)
- Total backlog: ~300+ distinct items (many RSC books overlap across categories)
