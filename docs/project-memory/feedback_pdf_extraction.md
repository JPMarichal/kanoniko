---
name: feedback_pdf_extraction
description: PDF extraction tool policy — PyMuPDF by default, Marker only with explicit authorization
type: feedback
---

PyMuPDF (fitz) is the default tool for PDF-to-Markdown extraction. Marker requires explicit user authorization.

**Why:** PyMuPDF processes 691 pages in 2 seconds with no GPU/RAM pressure. Marker consumed 30+ GB RAM, required GPU at 100%, and OOM-killed with 8 GB mem_limit — overkill for text-selectable PDFs. The quality difference is marginal for text+headings+paragraphs (the common case).

**How to apply:**
- Default: PyMuPDF with font-size-based heading detection (script: `scripts/pdf2md-fitz.py`)
- Marker: only when user explicitly authorizes (scanned PDFs, complex layouts with tables/columns)
- Never assume Marker is needed — ask first
- PDF is an input format only, never a corpus format — always convert to .md
