---
name: Citation Norms Document
description: Formal citation standards for all corpus materials — scriptures, study aids (TG/BD/GEE/JST), introductions, conference talks
type: reference
---

Full citation norms are formalized in `docs/citation-norms.md`. Key points:

- **Scriptures:** `Book Chapter:Verse` — bilingual (EN/ES book names, D&C/DyC)
- **FCD format** for displayed blocks: no verse numbers, one verse per line, reference at end, blockquote
- **Study aids:** `TG Entry` (EN), `GEE Entrada` (ES), `BD Entry` (EN only). No quotes/commas/pages.
- **JST/TJS:** Cited as scripture refs with comma: `JST, Genesis 14:25`
- **Introductory materials:** Full name, no abbreviation
- **Conference talks:** `Author, "Title," Session Year`
- **Inline style preferred:** quote then `(reference)` in parentheses

**Why:** Consistent citation across RAG answers, search results, and all output. The Church's own footnote conventions are the authority.
**How to apply:** Any code or prompt that formats citations should follow `docs/citation-norms.md`. The RAG system prompt in `chat/rag.py` should reference these norms.
