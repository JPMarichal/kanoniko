# EPUB → Corpus incorporation process

End-to-end workflow for turning an EPUB in `epub/!Ready/` into a properly
classified, chapter-split, evaluated corpus entry under `corpus/{lang}/{category}/`.

**Definition of Done for a single work:** chapters extracted, meta.json
populated with the 9-axis evaluation (authority, rigor, importance, official,
current, context, audience, tags, note), committed under the correct
`corpus/{lang}/{category}/{subcategory?}/{slug}/` path.

**NOT** part of this process: running `/index/ingest` (that's corpus ingestion,
separate phase) and reclassifying pre-existing corpus items.

## Prerequisites

- `epub/!Ready/<file>.epub` exists.
- Inventory is current: `python scripts/epub_inventory.py` produced
  `epub/_inventory.csv` recently (re-run if the lot changed).
- The target category directory exists under `corpus/{lang}/`.

## The 6-step workflow

### 1. Pick a batch

Open `epub/_inventory.csv` (or the grouped `epub/_triage.md`). Filter by
`bucket = nuevo` and group by `creator` or `category`. Work in small lots —
typically 1 author at a time, or a coherent sub-series (e.g. all "at a Glance"
entries).

Do **not** batch across widely different typologies in one Fase 0 session —
each needs its own research.

### 2. Fase 0 research (BLOCKING)

For each work, understand **what it is, who produced it, when, for whom, how
referenced**. See `docs/project-memory/procedure_corpus_addition.md` for the
full checklist. Output:

1. Prose note at `proj/P4-corpus-expansion/fase0/{slug}.md` — human-readable
   research notes, bibliography, narrative.
2. Structured sidecar at `proj/P4-corpus-expansion/fase0/{slug}.fase0.json`
   — machine-readable decisions. See `proj/P4-corpus-expansion/fase0/_SIDECAR_SCHEMA.md`.

A minimal sidecar:

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

**Without a sidecar**, extraction still produces valid output but every
chapter carries `authority_pending: true` and null evaluation fields. This is
intentional — never guess the axes, always research them.

### 3. Extract to preview

```bash
python scripts/epub_extract.py "epub/!Ready/<file>.epub" \
    --lang en --category books
```

Output lands in `epub/_preview/{lang}/{category}/{slug}/`. The extractor:

- Normalizes the author (IJCSUD for Church variants, "Various" for multi-author, adds dots to bare initials).
- Segments on `h1`/`h2` where present; falls back to one-chapter-per-spine-file using first `<b>` as title when no headings exist.
- Strips Calibre topic-index prefixes (`<span>TOPIC/</span>`).
- Captures footnotes: inline refs `<a href="...#fn-N">N</a>` → `[^N]`, and
  definition paragraphs `<p>N. body</p>` → per-chapter `Notas:` section.
- Single-file mode when total text ≤ `--max-single-file-kb` (default 10 KB)
  or only 1 chapter detected.
- Auto-loads the Fase 0 sidecar if `{slug}.fase0.json` exists.

Flags worth knowing:
- `--slug <slug>` — override when OPF title produces a weird auto-slug.
- `--subcategory <name>` — place under `manuals/<sub>/` or `magazines/<sub>/`.
- `--fase0 PATH` — explicit sidecar path (overrides slug-based lookup).
- `--apply` — skip preview, write directly to `corpus/`.

### 4. Review the preview

Spot-check:
- Chapter titles sensible (no "Part 1" placeholders that should have been real titles).
- Chapter count matches expectations (too few = segmentation missed; too many = false h2s).
- Body text is clean (no `calibre1`, `calibre2` class leaks, no stray HTML).
- Footnotes captured when the source has them — check `Notas:` section at end.
- meta.json has all 9 evaluation fields populated (or `authority_pending: true`
  if you deferred Fase 0).

If something's wrong, fix the Fase 0 sidecar or the extractor, then re-run
(the extractor overwrites preview, doesn't merge).

### 5. Promote to corpus

```bash
python scripts/epub_extract.py --promote epub/_preview/en/books/<slug>
```

This `mv`s the preview dir into `corpus/`. Refuses if target already exists
(no silent overwrite of ingested content).

### 6. Commit

```bash
git add corpus/en/books/<slug> proj/P4-corpus-expansion/fase0/<slug>*
git commit -m "corpus(books): add <Title> — <Author>"
```

If you're in a batch, commit per work (easier rollback) or per author
(tighter history) — pick the cadence that matches the lot.

## Batch mode sketch (not yet implemented)

For lots of 10+ works by the same author with uniform evaluation values,
it's reasonable to:

1. Write one Fase 0 sidecar template per author (say, all Roberts books get
   `authority=35, context="book-private", audience="adult"`).
2. Loop: extract → visually diff chapter titles against the book's TOC → promote.

A future `--from-inventory --author "B. H. Roberts"` flag will help here.
For now, a bash for-loop over `epub/!Ready/B. H. Roberts*.epub` works.

## Troubleshooting

| symptom | likely cause | fix |
|---|---|---|
| 1 chapter for an 80KB book | no `<h1>/<h2>` found, fallback fired with only 1 spine file | inspect raw HTML; may need a new heading-detection heuristic |
| Calibre topic prefix leaking (`TOPIC/Text...`) | span wasn't pattern-matched | widen `CALIBRE_TOPIC_SPAN_RE` in `epub_extract.py` |
| Footnotes missing | source uses different anchor scheme | add pattern to `FN_REF_RE` / `FN_DEF_RE` |
| Chapter title is "Part N" | no `<b>/<strong>` near file top | check HTML for alternative marker; may need manual `--slug` + custom post-edit |
| `opf_date: "0101-01-01..."` in meta | already filtered to null; report if you see it |
| Wrong category inferred | OPF creator/publisher unreliable | force via `--category` CLI or `category` field in sidecar |

## Related documents

- `docs/authority-model.md` — 3-axis authority scale (doctrinal/rigor/4I's).
- `docs/project-memory/procedure_corpus_addition.md` — the parent 9-step corpus-addition checklist. EPUB incorporation is one path into it.
- `proj/P4-corpus-expansion/fase0/_SIDECAR_SCHEMA.md` — sidecar JSON schema.
- `epub/_inventory.csv` / `_triage.md` — current epub lot status.
- `epub/_authors.csv` / `_authors.md` — author normalization reference.
