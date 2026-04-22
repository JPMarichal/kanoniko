---
name: epub-incorporate
description: Incorporate an EPUB from epub/!Ready/ into the Alejandría corpus. Runs the full workflow — Fase 0 research note → structured sidecar → extraction → preview review → promote to corpus/. Uses scripts/epub_extract.py. Triggers on "incorpora este epub", "add this book to the corpus", "procesa el epub X", or when the user points to an epub under epub/!Ready/.
---

# EPUB → Corpus incorporation

Turn an EPUB from `epub/!Ready/` into a properly classified, chapter-split,
evaluated corpus entry under `corpus/{lang}/{category}/`.

**Not in scope:** running `/index/ingest`, reclassifying pre-existing corpus
items, downloading new EPUBs.

**Full process doc:** `docs/epub-incorporation.md`. This skill is the
operational shortcut for a single work or a small homogeneous batch.

## Before you start

1. Confirm `epub/_inventory.csv` exists and is current. If not:
   ```bash
   python scripts/epub_inventory.py
   ```
2. Confirm the `.fase0.json` schema is clear: read `proj/P4-corpus-expansion/fase0/_SIDECAR_SCHEMA.md`.
3. Confirm the target category directory exists under `corpus/{lang}/`.
   The 13 supported categories are:
   `scriptures`, `proclamations`, `general-conference`, `manuals`, `books`,
   `biographies`, `history`, `discourses`, `study-aids`, `reference`,
   `magazines`, `music`, `web`.

## Workflow (per work)

### Step 1 — Locate and read the EPUB metadata

```bash
grep -F "<filename stem>" epub/_inventory.csv
```

Note the row's `title`, `creator` (normalized), `lang`, proposed `title_slug`,
and `bucket`. If `bucket = duplicado-corpus`, stop — the work is already in
the corpus at the listed path.

### Step 2 — Fase 0 research

**Do not skip.** The authority axes are not guessable.

Write two files under `proj/P4-corpus-expansion/fase0/`:

1. **Prose research** — `{slug}.md`. Cover: what it is, who produced it, when,
   for whom, how referenced, relationships to existing corpus. Follow
   `docs/project-memory/procedure_corpus_addition.md` step 2.

2. **Structured sidecar** — `{slug}.fase0.json` with the 9 evaluation fields
   plus optional placement overrides:
   ```json
   {
     "authority": 45,
     "rigor": 65,
     "importance": "importante",
     "official": false,
     "current": false,
     "context": "book-official",
     "audience": "adult",
     "tags": ["doctrine", "apostle-authored"],
     "author": "James E. Talmage",
     "source_url": "https://...",
     "note": "Originally delivered as lectures at LDS University, 1893."
   }
   ```

   Consult `docs/authority-model.md` for authority-scale reference points.
   Pick values from research, not from title heuristics.

### Step 3 — Extract to preview

```bash
python scripts/epub_extract.py "epub/!Ready/<filename>.epub" \
    --lang <en|es> \
    --category <books|manuals|biographies|history|discourses|...>
```

Optional flags:
- `--subcategory <name>` (e.g. `teachings-of-presidents` under `manuals/`)
- `--slug <slug>` when auto-slug diverges from your Fase 0 filename
- `--fase0 PATH` for an explicit sidecar path

Output lands in `epub/_preview/{lang}/{category}/[{sub}/]{slug}/`. The
extractor auto-loads the sidecar if `{slug}.fase0.json` matches.

### Step 4 — Review the preview

Spot-check these four things:

- **Chapter count and titles**: open a few `.txt` files; titles should be the
  real chapter headings, not generic "Part N" placeholders (that fallback
  fires only when the EPUB has no `<h1>/<h2>` and no `<b>` near top).
- **Body cleanliness**: `grep -lE "calibre[0-9]|</?(p|span|a)\b" epub/_preview/**/*.txt`
  should return nothing.
- **Footnotes**: if the source has footnotes, every chapter should have a
  `---\nNotas:\n[^N] ...` tail section. If missing on a work you know has
  footnotes, the anchor scheme is new — extend `FN_REF_RE` / `FN_DEF_RE`.
- **meta.json**: `authority_pending: false` when the sidecar loaded;
  `true` means the sidecar was missing or slug mismatched.

If something's wrong, fix the sidecar or the extractor and re-run — the
preview dir is overwritten on each extraction, no merge.

### Step 5 — Promote to corpus

```bash
python scripts/epub_extract.py --promote epub/_preview/<lang>/<category>/<slug>
```

This `mv`s the preview dir into `corpus/`. It refuses if the target exists
— that guards against overwriting already-ingested content.

### Step 6 — Commit

```bash
git add corpus/<lang>/<category>/<slug> \
        proj/P4-corpus-expansion/fase0/<slug>.md \
        proj/P4-corpus-expansion/fase0/<slug>.fase0.json
git commit -m "corpus(<category>): add <Title> — <Author>"
```

Per-work commits keep rollback surgical. For a homogeneous batch of the
same author with shared evaluation, one commit per author is fine.

## Smoke-test the extractor on diverse typologies

If you suspect a new Calibre style or extractor regression, run:

```bash
python scripts/epub_extract_smoke.py
```

This extracts 4 representative EPUBs (IJCSUD ES manual, EN anthology, Rose
short-single, ES individual author) to `epub/_smoke/` and reports red flags
(Calibre class leaks, empty chapters, raw HTML tags, footnote pair rate).

## Inventory helpers

- `python scripts/epub_inventory.py` — classify all 1468 EPUBs in `epub/!Ready/`
  (fuzzy match against corpus, bucket into nuevo/duplicado/basura/propio).
- `python scripts/epub_authors_inventory.py` — normalized author list with
  IJCSUD / Various / initials merges. Useful for planning author-batched
  incorporation.

## When to stop and escalate

- The EPUB produces 1 chapter for >50 KB content and the structural probe
  shows no `<h1>/<h2>` and no meaningful `<b>` — stop, report the HTML
  structure, decide a new heuristic.
- Footnotes are in the source but extraction shows 0 in every chapter —
  same as above for `FN_REF_RE`.
- Fase 0 research surfaces a doctrinal controversy or authority ambiguity —
  stop, consult, don't guess.
- The EPUB is `creator = (unknown)` and research can't attribute it —
  leave `author: "(unknown)"` in the sidecar, mark `importance: "marginal"`,
  and document the provenance gap in `{slug}.md`.
