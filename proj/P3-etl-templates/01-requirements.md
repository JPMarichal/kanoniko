# P3 — ETL Templates — Requirements

## Problem Statement

Adding new material types to the corpus requires custom parsing and metadata extraction logic each time. There is no standardized pipeline for ingesting conference talks, manuals, institute materials, or web content with consistent quality and metadata.

## Functional Requirements

### FR-1: Template Definition Format
A declarative template format (YAML or JSON) that specifies:
- Source format (HTML, PDF, JSON, DOCX, etc.)
- Metadata extraction rules (title, author, date, language, category)
- Text extraction and cleaning rules
- Output structure (directory path, file naming convention)
- Chunking strategy override (if different from default)

### FR-2: Built-in Templates
Templates for the major corpus categories:
- General Conference talks
- Church manuals (Gospel Principles, Come Follow Me, etc.)
- Institute/seminary materials
- Church magazine articles (Ensign, Liahona)
- Web page downloads

### FR-3: Metadata Extraction
Each template must produce consistent metadata:
- `title`, `author`, `date`, `language`, `category`, `source_url`
- Category-specific fields (e.g., `session` for conference, `lesson_number` for manuals)

### FR-4: Quality Validation
Post-extraction validation:
- Minimum text length (reject empty or stub pages)
- Language detection confirmation
- Duplicate detection (same content already in corpus)
- Encoding verification (UTF-8 clean)

### FR-5: CLI & API Interface
- CLI: `alejandria etl --template conference --input ./raw/ --output ./corpus/`
- API: `POST /index/etl` with template name and source path

## Non-Functional Requirements

- Templates must be user-editable without code changes
- Processing must be idempotent (re-running produces same output)
- Error reporting per file with skip-and-continue behavior

## Out of Scope

- Actual content downloading (P2 handles scriptures; P4 handles other sources)
- PDF parsing (may be added later as a parser plugin)
- OCR for scanned documents
