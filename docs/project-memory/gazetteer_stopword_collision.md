---
name: Gazetteer stopword collision
description: Short biblical names (On, So, Put, Ye) collide with common English/Spanish words, inflating mention counts — needs context-aware filtering or minimum name length for gazetteer matching
type: project
---

## Problem

Biblical persons with very short names that are also common words:
- **EN**: On (Numbers 16:1), So (2 Kings 17:4), Put (Genesis 10:6), Ye (unknown)
- **ES**: Likely similar collisions (e.g., "Ur" = place + common in Spanish text)

These match via `\b` word-boundary regex on virtually every chunk, producing thousands of false positive mentions (On=5,339 mentions across 967 docs).

**Why:** The compiled gazetteer regex uses `\b(on|so|put|...)\b` which matches common English words. This is a form of disambiguation — distinguishing between "On the person" and "on the preposition."

**How to apply:** Future fix options:
1. Minimum name length filter (e.g., skip gazetteer terms < 3 chars) — simple but loses real short names
2. Context-aware matching — only match short names when capitalized or in gazetteer-heavy context
3. NER validation — only count a short-name match if spaCy also flags it as PERSON
4. Stopword exclusion list for gazetteer — manually curate which short names to skip in regex matching
5. Post-hoc filtering in profile build — exclude entities where mention_count >> document_count (signal of false positives)

This affects both EN and ES corpora.
