---
name: Direct scripture lookup
description: When user gives book/chapter/verses, read the file directly instead of using search APIs
type: feedback
---

When the user provides a scripture reference (book, chapter, verses), go directly to the corpus file — do NOT use search APIs (textual, semantic, hybrid).

**Why:** The corpus structure maps 1:1 — `corpus/{lang}/scriptures/{volume}/{book}/{chapter}.txt` where line number = verse number. Using search is a slow, indirect roundabout when the exact location is already known.

**How to apply:** Parse the reference → resolve to file path → `Read` with offset=verse_start, limit=verse_count. Done in one tool call.

**Output format — FCD (Formato de Citas para Dilton):**
Scripture passages displayed inline must follow this format:
1. Text without verse numbers
2. Each verse on its own line (simple line break)
3. Reference in parentheses at the end of the last verse
4. No italics — use blockquote (`>`) but never italic markup

Example:
> Y ahora yo, Moroni, quisiera hablar algo concerniente a estas cosas...
> Porque fue por la fe que Cristo se manifestó a nuestros padres... (Éter 12:6-7)
