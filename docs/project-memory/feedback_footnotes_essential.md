---
name: Footnotes are essential content
description: Footnotes/endnotes must ALWAYS be downloaded and preserved — they carry scripture cross-refs, commentary, and variant readings indispensable for KG and RAG
type: feedback
---

Footnotes, endnotes, and related-content links are NOT optional metadata — they are essential content that must always be captured when downloading from any source.

**Why:** Footnotes carry: (1) scripture cross-references — primary source of intertextuality relations in the KG, (2) historical/linguistic commentary enriching RAG responses, (3) see-also links to related topics, (4) variant readings and translation notes for bilingual alignment. Missing footnotes means missing KG relations and impoverished RAG context.

**How to apply:**
- Every download script must extract footnotes (API: `content.footnotes`, HTML: `<li id="note{N}">`)
- Footnotes go in BOTH places: appended as endnotes in `.txt` AND structured in `.meta.json`
- The shared module `scripts/lib/church_scraper.py` has `extract_footnotes_api()`, `extract_footnotes_html()`, `format_footnotes_text()`, and `footnotes_to_meta()` — always use them
- Scripture refs extracted from footnotes feed KG intertextuality relations
- When reviewing/auditing existing scripts, check footnote completeness
