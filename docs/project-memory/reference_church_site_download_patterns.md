---
name: Church site download patterns
description: Comprehensive patterns for downloading content from churchofjesuschrist.org — URL structures, API vs HTML strategy, TOC discovery, output conventions, CLI args, shared code gaps
type: reference
---

## Two access strategies

| Strategy | When to use | Scripts using it |
|---|---|---|
| **API v3** (`/study/api/v3/language-pages/type/content?lang={lang}&uri={uri}`) | Prose content: manuals, books, talks | download_pme, download_conference, download_jesus_the_christ, scrape_study_aids (fallback) |
| **Direct HTML scrape** | Structured content: verses, numbered sections, study aids with nav.index blocks | scrape_scriptures, scrape_introductions, scrape_handbook, scrape_jst, scrape_study_aids |

**Rule:** API for prose → pandoc conversion. HTML for verse-level or section-numbered content → BeautifulSoup manual extraction.

## URL patterns on the Church site

| Content type | URL pattern | API uri (remove /study) |
|---|---|---|
| Scriptures | `/study/scriptures/{volume}/{book}/{chapter}` | N/A (use HTML) |
| Manuals/books | `/study/manual/{manual-slug}/{chapter-slug}` | `/manual/{manual-slug}/{chapter-slug}` |
| Conference | `/study/general-conference/{year}/{month}/{talk-slug}` | `/general-conference/{year}/{month}/{talk-slug}` |
| Study aids | `/study/scriptures/{gs\|tg\|bd\|jst}/{entry-slug}` | `/scriptures/{gs\|tg\|bd}/{entry-slug}` |

**Key:** The API `uri` parameter strips the `/study` prefix from the page URL path.

## Volume slugs (site vs corpus)

Site uses different volume abbreviations than the corpus:
- `bofm` (site) → `bom` (corpus)
- `dc-testament` (site) → `dc` (corpus)
- `ot`, `nt`, `pgp` are the same

## TOC/index discovery (universal pattern)

All scripts follow the same approach:
1. Fetch parent page (TOC) via API or HTML
2. Parse all `<a>` links whose href contains the content prefix
3. Extract slug as last path segment after prefix, stripping `?lang=` params
4. Deduplicate with `seen_slugs: set`
5. Return list of `{uri, slug, title}` dicts

For API-based scripts: fetch TOC JSON → parse `content.body` HTML → extract links.
For HTML-based scripts: fetch page directly → parse full page → extract links.

## Bilingual handling

- **Manuals, conference, books:** Same slugs for both `?lang=eng` and `?lang=spa`. Only the lang parameter changes.
- **Scriptures:** ES uses Spanish book directory slugs (exodus→exodo, psalms→salmos, etc.). Book slug mapping required.
- **Corpus directories:** `en`/`es` (not `eng`/`spa`). Mapping: `LANG_MAP = {"eng": "en", "spa": "es"}`

## HTML → text conversion

### API route (prose)
```python
# Pre-process headings to markdown markers
heading_map = {"h1": "#", "h2": "##", "h3": "###", "h4": "####"}
# Remove: img, nav, figure, .manifest, p.reference, sup.marker, .study-note-ref
# Then pandoc: pandoc -f html -t plain --wrap=none
# Post: collapse 4+ newlines to 2
```

### HTML route (verses)
```python
# Find: soup.find_all("p", class_=lambda c: c and "verse" in str(c))
# Verse number: span.verse-number or data-eng-ref or id="pN"
# Clean: decompose sup.marker, span.verse-number, button, svg
# Output: "{verse_num} {verse_text}\n"
```

### Common cleanup targets
- `sup.marker` (footnote letter markers) — always remove
- `footer`, `nav` (navigation) — always skip
- `p.reference`, `p.short-reference` (series reference line) — remove for API route
- `.study-note-ref` — remove

## Output conventions

Always produce `.txt` + `.meta.json` pairs.

### Minimum meta.json fields
```json
{
  "title": "...",
  "source_url": "https://www.churchofjesuschrist.org/study/...",
  "authority": 45,
  "lang": "eng"
}
```

### Common optional fields
- `category`, `subcategory` — for corpus classification
- `tags` — topical keywords
- `note_count` — number of footnotes
- `scripture_refs` / `scripture_references` — extracted cross-refs
- `author`, `book`, `manual`, `edition` — for authored works
- `sections`, `cross_references` — for structured manuals (handbook)
- `official: true/false` — for authority model

### Authority levels by content type
- Scriptures: 100
- Proclamations: 90
- Conference talks: 80
- General Handbook: 65
- Manuals: 60
- Study aids: 57
- GA-authored books (adopted): 45
- Web content: 25
- Biographies: 20

## CLI conventions

All scripts support:
- `--lang` (eng/spa or both as default)
- `--dry-run` (list without downloading)

Large scrapers add:
- `--resume` (checkpoint-based)
- `--list-only` (just list entries)
- `--limit N` (cap entries)
- `--delay N` (override rate limit)

## Rate limiting

`REQUEST_DELAY = 0.3–0.5` seconds between requests. User-Agent: `Mozilla/5.0 (compatible; AlejandriaBot/1.0; scripture-study)`.

## Checkpoint pattern (large scrapers only)

```python
checkpoint_path = PROJECT_ROOT / "data" / f"scrape_{name}_{lang}_checkpoint.txt"
# Set of processed slug/path strings, one per line, sorted
# Save every N entries + final save
```

## Footnotes handling

- **API route:** structured in `content.footnotes` dict — keys are IDs, values have `marker`, `text`, `referenceUris`
- **HTML route:** `<li id="note{N}_{letter}">` or `note{N}{letter}` (ES omits underscore)

## What's NOT shared (refactoring opportunity)

Each script independently implements:
- Session setup with CA bundle and User-Agent
- Checkpoint load/save
- HTML cleanup (sup.marker removal, nav/footer exclusion)
- Rate limiting loop
- Stats collection and reporting
- LANG_MAP, BASE_URL, CORPUS_ROOT constants

A future `scripts/lib/church_scraper.py` base module could extract ~100 lines of shared code.

## Preparing a new download script (recipe)

1. **Visit the TOC page** in browser: `churchofjesuschrist.org/study/manual/{slug}` or `/study/scriptures/{slug}`
2. **Decide API vs HTML:** prose → API, verses → HTML
3. **Test the API:** `curl "https://www.churchofjesuschrist.org/study/api/v3/language-pages/type/content?lang=eng&uri=/manual/{slug}/{chapter-slug}"` — check `content.body` exists and has substantial HTML
4. **Check both languages:** same curl with `?lang=spa` — verify slugs are identical
5. **Count pages:** parse TOC to get full slug list
6. **Copy closest existing script** and adapt: slug map, output dir, meta fields, authority level
7. **Test with `--dry-run`** and `--lang eng` first, then `--lang spa`, then both
