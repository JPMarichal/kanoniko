# Fase 0 sidecar (`.fase0.json`) — schema for `scripts/epub_extract.py`

The prose `{slug}.md` file is for humans — research notes, narrative, bibliography.

The `{slug}.fase0.json` sibling is the **structured output** the extractor reads
to populate `.meta.json`. Without it, every chapter lands with
`authority_pending: true` and `authority`, `rigor`, `official`, `context`,
`audience`, `importance`, `current`, `tags` all set to `null`.

## Where it lives

```
proj/P4-corpus-expansion/fase0/{slug}.md          # human research
proj/P4-corpus-expansion/fase0/{slug}.fase0.json  # machine-readable decisions
```

Slug matches what `epub_extract.py` computes from the EPUB title
(`slugify(dc:title)`). Use `--slug` on the extractor to override if the
auto-slug diverges from your Fase 0 filename.

## Full field reference

All fields are optional. Unknown keys are silently ignored. Types must match.

```json
{
  "authority":    45,
  "rigor":        65,
  "importance":   "importante",
  "official":     false,
  "current":      false,
  "context":      "book-official",
  "audience":     "adult",
  "tags":         ["doctrine", "apostle-authored", "lectures"],

  "category":     "books",
  "subcategory":  null,

  "author":       "James E. Talmage",
  "source_url":   "https://www.gutenberg.org/ebooks/42238",
  "note":         "Originally delivered as lectures at LDS University, 1893. Published 1899."
}
```

### Evaluation axes (fill from research, see `docs/authority-model.md`)

| field | type | values |
|---|---|---|
| `authority` | int 1–100 | doctrinal weight. 100=canon, 80=prophetic FP/Q12, 60=correlated manuals, 45=GA private authored official, 40=GA private not official |
| `rigor` | int 1–100 | scholarly / textual rigor of the source itself (not the topic) |
| `importance` | string | `"esencial"` / `"importante"` / `"complementario"` / `"marginal"` |
| `official` | bool | whether it carries official Church endorsement |
| `current` | bool | whether the teaching is still in force |
| `context` | string | `"book-official"`, `"book-private"`, `"manual"`, `"conference"`, `"scholarly"`, `"devotional"`, `"apologetic"` |
| `audience` | string | `"adult"`, `"youth"`, `"child"`, `"leadership"`, `"missionary"`, `"general"` |
| `tags` | list[string] | free keywords for search/classification |

### Placement overrides

| field | purpose |
|---|---|
| `category` | force target corpus category (overrides `--category` CLI) |
| `subcategory` | force sub-bucket (e.g. `"teachings-of-presidents"` under `manuals/`) |

### Identity / provenance

| field | purpose |
|---|---|
| `author` | canonical author string written to meta.json (overrides OPF creator + `--author` CLI) |
| `source_url` | URL of authoritative source (Gutenberg, Church site, etc.) |
| `note` | free-text annotation carried to every chapter's meta.json |

## Workflow

1. Pick an EPUB lot from `epub/_inventory.csv`.
2. For each work, research it (what it is, who wrote it, origin, weight) — see
   `docs/project-memory/procedure_corpus_addition.md`.
3. Write the prose `{slug}.md` as usual. Decide the evaluation values.
4. Write `{slug}.fase0.json` with at least the 7 axes + `tags`.
5. Run `python scripts/epub_extract.py <epub> --lang X --category Y` — the
   sidecar is auto-picked by slug match. Or pass `--fase0 <path>` explicitly.
6. The `_preview/` output carries the authority values in every chapter's
   meta.json. Review, then `--promote` to `corpus/`.
