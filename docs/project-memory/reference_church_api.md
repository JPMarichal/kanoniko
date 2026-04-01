---
name: Church Site JSON API
description: churchofjesuschrist.org has a JSON API at /study/api/v3/language-pages/type/content that returns HTML content in JSON wrapper; useful for dynamic pages
type: reference
---

The official Church site (churchofjesuschrist.org) loads scripture content dynamically via a JSON API:

**Endpoint:** `https://www.churchofjesuschrist.org/study/api/v3/language-pages/type/content?lang={lang}&uri={path}`

- `lang`: "eng", "spa", etc.
- `uri`: the content path, e.g., `/scriptures/gs/abraham`

**Response structure:**
- `meta`: page metadata (title, URL, content type, language)
- `content.body`: HTML content of the page
- `pids`: paragraph identifiers mapping
- `uri` / `tableOfContentsUri`: navigation paths

**Status (2026-03-31):**
- Works for some pages (confirmed for `/scriptures/gs/abraham`)
- Returns 404 for others (e.g., most GEE entries in direct URL form)
- The URI path format may differ from the page URL — needs investigation
- Fallback to direct HTML scraping works reliably

**Why:** This API could enable faster, cleaner scraping without parsing full HTML pages. Worth revisiting when the exact URI format is understood better.
**How to apply:** When building scrapers for church content, try API first with HTML fallback. The API may use different path conventions than the public URLs.
