---
name: Church Site JSON API
description: churchofjesuschrist.org API v3 endpoint — URI format rules, response structure, when it works vs when to use HTML fallback
type: reference
---

**Endpoint:** `https://www.churchofjesuschrist.org/study/api/v3/language-pages/type/content?lang={lang}&uri={path}`

**URI format rule:** Strip `/study` from the page URL path. E.g., page at `/study/manual/jesus-the-christ/chapter-1` → `uri=/manual/jesus-the-christ/chapter-1`

**Response structure:**
- `meta`: title, canonicalUrl, audio (narration URLs), pageAttributes
- `content.body`: HTML content string
- `content.footnotes`: structured dict — keys are IDs, values have `marker`, `text`, `referenceUris`
- `pids`: paragraph ID mappings
- `uri` / `tableOfContentsUri`: navigation paths

**Works well for:** manuals, books, conference talks — any `/study/manual/` or `/study/general-conference/` content
**Less reliable for:** study aids (GEE, TG, BD) — some entries return 404 via API but work via HTML

**Why:** API returns clean structured JSON with separated footnotes. HTML scraping is fallback for verse-level content and study aids.
**How to apply:** See comprehensive patterns in `reference_church_site_download_patterns.md`
