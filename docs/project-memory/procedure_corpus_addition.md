---
name: Procedure for adding material to the corpus
description: Step-by-step procedure for adding new documents to the Alejandría corpus, including research, placement, authority, metadata, KG analysis, and indexing
type: feedback
---

When adding new material to the corpus, follow this procedure every time:

## 1. Classify and place correctly

- Determine the document's nature: scripture (canonized by sustaining vote), proclamation (official FP+Q12 but not canonized), conference talk, manual, biography, web content.
- **Never** place non-canonical documents under `scriptures/`. The Family Proclamation and The Living Christ go in `proclamations/`, not `scriptures/dc/official-declarations/`.
- Create bilingual pairs: `corpus/en/{category}/` and `corpus/es/{category}/`.

## 2. Research the material (MANDATORY — blocks steps 3-8)

Before assigning authority or analyzing KG impact, **investigate each resource** (or group of similar resources) to understand what it actually is. **This step is BLOCKING — steps 3 through 8 cannot proceed without it.** Authority levels, KG relationships, tags, and even output directories depend on understanding what the material actually is.

For each resource, determine via web search:

- **What is it?** — Purpose, content type, structure (multi-chapter manual, single-page guide, pamphlet, etc.)
- **Who produced it?** — Specific authors/editors, commissioning body (Correlation, FP, individual GA, S&I, Church Historians Press, etc.)
- **When?** — Original publication date, revision history, current edition
- **For whom?** — Target audience (leaders, youth, children, missionaries, teachers, general membership)
- **How referenced is it?** — Is it widely cited? Foundational for a program? Recommended by GA in Conference?
- **What relationships will it have?** — With existing corpus entities, doctrines, scriptures, other manuals
- **How does it relate to other resources?** — Is it part of a series? Does it complement, replace, or aggregate other materials?

This step prevents superficial authority assignment based on titles alone. A document's real weight comes from understanding its origin and role in the Church's ecosystem.

**How to do it:** Web search for Church Newsroom announcements, reviews, scholarly references, usage in curriculum. Look for who announced it, in what setting, and how it's been received. For well-known manuals, general knowledge may suffice. For unfamiliar materials, the research is essential.

**Anti-pattern (learned the hard way):** Verifying URL slugs and counting TOC entries is NOT research — that's technical preparation for step 5. Research means understanding the *nature, purpose, and weight* of the material. Without it, authority values are guesses, tags are superficial, and KG pre-seeds miss important relationships.

## 3. Authority level

- Informed by the research in step 2, assign authority/rigor/official values.
- Check `src/alejandria/authority.py` `_SOURCE_DEFAULTS` — if the new category doesn't exist, add it with appropriate values.
- Cross-reference with `docs/authority-model.md` for the doctrinal authority scale.
- Proclamations: authority=90, rigor=95, official=True, context="official-declaration".

## 4. KG relationship analysis + pre-seed (BEFORE downloading — BLOCKING)

**This step BLOCKS step 5 (download/format).** The pre-seed must be complete before any content enters the corpus. Rationale: once files are downloaded and committed, the temptation to "just index" is strong. The KG pre-seed is preparation, not a post-download cleanup.

- Search existing KG entities that relate to the new document (`kg_find`).
- Check how many existing corpus documents **cite** the new document (`grep` the corpus for mentions).
- The new document may become a **hub node** — high citation count means many inbound `REFERENCES`/`CITES` edges will be generated automatically.
- Document the expected relationship types: authorship, doctrinal (TEACHES), intertextuality (REFERENCES), temporal (DATED_TO), geographic (LOCATED_IN).
- **Pre-seed known relationships into Neo4j** via Cypher BEFORE downloading. Write a `.cypher` file in `scripts/` with MERGE statements for all identified relationships (confidence: "curated", source: "curated_seed"). Execute against Neo4j HTTP API.
- Phase 3 (NER/KG extraction) then only discovers additional relationships from text — the long tail. Never rely on expensive automated discovery for what preparation already determined.

## 5. File format

- `.txt` for content (plain paragraphs, no verse numbers for non-scripture).
- `.meta.json` with: title, meta_description, study_intro, source_url, date, authors, event/location as applicable.
- Download from official church site (`churchofjesuschrist.org`).

## 6. Commit and sync

- **Commit the new corpus files + code changes to git** before attempting indexing. The Docker containers bind-mount from the Linux FS repo clone, which syncs via `git fetch + git reset --hard`. Without commit, the container won't see the files.
- Sync: `wsl -d Ubuntu-20.04 bash -c "cd /home/jpmarichal/alejandria-repo && git fetch origin && git reset --hard origin/main"`
- This step is mandatory — skipping it means indexing runs against an empty directory.

## 7. Prepare ingest paths

- Build the explicit list of corpus-relative paths (directories or files) for the new material.
- **Never** use `POST /index/trigger` (full corpus scan) for additions. Always use `POST /index/ingest` with the exact `paths` list.
- The pipeline resolves directories recursively — pass top-level directories, not individual files.
- The pipeline extracts source category from path: `{lang}/{category}/...` → category.

## 8. Indexing

- Launch `POST /index/ingest` with the prepared paths list from step 7 and the KG pre-seeded from step 4.
- **Never** run full reindex for additions.
- Alejandría runs on the native Docker Engine in Ubuntu WSL (NOT Rancher Desktop).

**Why:** The user corrected placement of the Family Proclamation (was going into scriptures/dc/official-declarations, should be proclamations/). Every document's canonical status and authority level must be considered before placement. Authority levels were being assigned superficially from titles — e.g., "The Charted Course" got authority=65 without knowing it's a foundational 1938 J. Reuben Clark address that defines S&I philosophy.

**How to apply:** Every time new material is added to the corpus, run through all 8 steps. Pay special attention to step 1 (correct placement), step 2 (research before authority), step 4 (KG pre-seed, not just analysis), step 6 (commit+sync before indexing), and step 7 (explicit paths, never full scan).
