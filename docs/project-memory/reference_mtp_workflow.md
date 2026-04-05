---
name: MTP-first book discovery workflow
description: When adding public-domain LDS books, check Mormon Texts Project catalog first — they produce the clean Gutenberg transcriptions. Avoids wasting time on OCR.
type: reference
---

Mormon Texts Project (mormontext.org) is the upstream producer of most LDS public-domain texts on Project Gutenberg. Their volunteers transcribe from scans and upload to Gutenberg.

**Workflow:** MTP catalog -> Gutenberg IDs -> download via `download_gutenberg.py` -> archive.org OCR only for what MTP doesn't have.

**Skill:** `/book-discovery` codifies this as a repeatable workflow.

**Why:** Discovered during Roberts books session — initially planned archive.org OCR for several books, then found MTP had clean transcriptions on Gutenberg for most of them. Saved hours of OCR cleanup work.

**How to apply:** Any time we want to add a pre-1930 LDS author's works, start with MTP, not archive.org.
