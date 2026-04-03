---
name: Procedure for adding material to the corpus
description: Step-by-step procedure for adding new documents to the Alejandría corpus, including placement, authority, metadata, KG analysis, and indexing
type: feedback
---

When adding new material to the corpus, follow this procedure every time:

## 1. Classify and place correctly

- Determine the document's nature: scripture (canonized by sustaining vote), proclamation (official FP+Q12 but not canonized), conference talk, manual, biography, web content.
- **Never** place non-canonical documents under `scriptures/`. The Family Proclamation and The Living Christ go in `proclamations/`, not `scriptures/dc/official-declarations/`.
- Create bilingual pairs: `corpus/en/{category}/` and `corpus/es/{category}/`.

## 2. Authority level

- Check `src/alejandria/authority.py` `_SOURCE_DEFAULTS` — if the new category doesn't exist, add it with appropriate authority/rigor/official values.
- Cross-reference with `docs/authority-model.md` for the doctrinal authority scale.
- Proclamations: authority=90, rigor=95, official=True, context="official-declaration".

## 3. KG relationship analysis (BEFORE indexing)

- Search existing KG entities that relate to the new document (`kg_find`).
- Check how many existing corpus documents **cite** the new document (`grep` the corpus for mentions).
- The new document may become a **hub node** — high citation count means many inbound `REFERENCES`/`CITES` edges will be generated automatically.
- Document the expected relationship types: authorship, doctrinal (TEACHES), intertextuality (REFERENCES), temporal (DATED_TO), geographic (LOCATED_IN).
- The pipeline's NER/extraction handles relation creation automatically — no manual KG insertion needed.

## 4. File format

- `.txt` for content (plain paragraphs, no verse numbers for non-scripture).
- `.meta.json` with: title, meta_description, study_intro, source_url, date, authors, event/location as applicable.
- Download from official church site (`churchofjesuschrist.org`).

## 5. Indexing

- Incremental indexing detects new files automatically via SHA-256 change detection.
- **Never** run full reindex for additions — always incremental.
- The pipeline extracts source category from path: `{lang}/{category}/...` → category.

**Why:** The user corrected placement of the Family Proclamation (was going into scriptures/dc/official-declarations, should be proclamations/). Every document's canonical status and authority level must be considered before placement.

**How to apply:** Every time new material is added to the corpus, run through all 5 steps. Pay special attention to step 1 (correct placement) and step 3 (KG impact analysis with existing material).
