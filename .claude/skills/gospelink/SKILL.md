---
name: gospelink
description: Download a complete work from Gospelink.com (Deseret Bookshelf) into the Alejandria corpus given only its contents-id. Handles AWS WAF, captchas, metadata enrichment, validation, and commit.
user_invocable: true
---

# Download from Gospelink

End-to-end workflow to add a Gospelink work to the corpus given **only the
contents-id** (the `N` in `https://www.gospelink.com/library/contents/N`).
Everything else (title, author, year, volume, publisher, topics, slug,
authority, rigor) is auto-derived from the TOC page and the curated author
table below; the user only confirms before fetch starts.

## Stack & dependencies

- `scripts/download_gospelink.py` (Playwright, headed Chrome)
- System Chrome at `C:\Program Files\Google\Chrome\Application\chrome.exe`
- Auth: `GOSPELINK_USER` + `GOSPELINK_PWD` in `.env`
- Session cookies cached in `data/.gospelink-session.json` (gitignored)
- Raw HTML in `data/raw/gospelink/{slug}/` (gitignored)
- Corpus output in `corpus/en/books/gospelink/{slug}/` (committed)

## When to invoke

Triggers: "descarga gospelink", "agrega DNTC vol N", "baja la obra X de
Gospelink", "contents-id N", "/library/contents/NNN".

## Workflow

### Step 1 — Pre-flight

Check session is fresh (< 24 h since last modify):

```bash
ls -l data/.gospelink-session.json
```

If missing or stale, **the user runs in their PowerShell** (interactive
captcha required, never invoke from agent context):

```powershell
python scripts/download_gospelink.py bootstrap
```

### Step 2 — Discover (agent runs)

```bash
python scripts/download_gospelink.py discover --contents-id NNN --slug TBD
```

`--slug` can be a placeholder; we'll regenerate the TOC after picking the
real slug. The output gives:

- `Title:` → e.g. "Doctrinal New Testament Commentary, vol. 2"
- `Author:` → e.g. "Bruce R. McConkie"
- `Year:` → e.g. 1971
- `Volume:` → e.g. 2
- `Publisher:` → e.g. "Deseret Book Company"
- `Topics:` → e.g. ['Doctrinal', 'New Testament', 'Scripture Commentaries']
- `doc_ids:` count

### Step 3 — Derive slug + metadata

**Slug rule** (apply in order):
1. If author + work has a known acronym (DNTC, MD, AGQ, JST), use
   `{acronym-lower}-vol-{N}` (e.g., `dntc-vol-2`, `md-2nd-ed`).
2. Else slugify the title: lowercase, ASCII, drop punctuation, spaces→`-`,
   "vol. N" → `-vol-N`. Cap at 60 chars. Example: "The Mortal Messiah,
   vol. 1" → `the-mortal-messiah-vol-1`.

**Metadata by author** (curated; lookup the `Author:` value verbatim):

| Author | authority | rigor | importance | context | extra tags |
|---|---|---|---|---|---|
| Bruce R. McConkie | 60 | 75 | importante | book-author | apostle-authored |
| James E. Talmage | 55 | 80 | importante | book-author | apostle-authored, scholar |
| Joseph Fielding Smith | 65 | 70 | importante | book-author | apostle-authored, prophet |
| John A. Widtsoe | 55 | 75 | importante | book-author | apostle-authored, scholar |
| Bruce R. McConkie; Joseph Fielding Smith | 65 | 70 | importante | book-author | apostle-authored, prophet |
| B. H. Roberts | 50 | 75 | importante | book-author | seventy-authored, scholar |
| Hugh Nibley | 40 | 80 | importante | book-author | scholar, apologetic |
| Hyrum L. Andrus | 35 | 70 | consulta | book-author | scholar, theologian |
| Robert L. Millet | 35 | 70 | consulta | book-author | scholar |
| Stephen E. Robinson | 35 | 70 | consulta | book-author | scholar |
| (any current Q15 apostle) | 75 | 70 | importante | book-apostle | apostle-authored, current |
| (any First Presidency historical) | 70 | 70 | importante | book-apostle | apostle-authored, prophet |
| (any Seventy / Bishopric) | 50 | 70 | consulta | book-author | seventy-authored |
| (LDS scholar, BYU faculty) | 35 | 75 | consulta | book-author | scholar |
| (multi-author / edited volume) | 40 | 70 | consulta | book-edited | scholar, anthology |
| (unknown / first time) | **ASK USER** | | | | |

If author isn't in the table, propose `authority: 40, rigor: 70` and ask
the user to confirm or override before proceeding.

**Tag composition** (always apply):
- `gospelink`, `{slug}`, lowercased topics from TOC (spaces→dashes).
- Topical inferrals from title:
  - "New Testament" or NT book name → `new-testament`
  - "Old Testament" or OT book name → `old-testament`
  - "Book of Mormon" → `book-of-mormon`
  - "Doctrine and Covenants", "D&C" → `doctrine-covenants`
  - "Doctrine", "Doctrinal", "Doctrines" → `doctrine`
  - "Commentary" → `commentary`
  - "History" → `church-history`
  - "Atonement", "Christ", "Messiah", "Jesus" → `christology`
- Plus any from the author table's "extra tags" column.

### Step 4 — Confirm with user

Present a single-message summary:

```
Vol N • Author • Year • {N} docs
slug: {derived-slug}
authority: {N} | rigor: {N} | importance: {X} | context: {X}
tags: {comma-list}
ETA: ~{minutes} min @ 4.5 s/req
Proceed?
```

If user says yes → step 5. If user overrides any field → adjust + recompute.

### Step 5 — Re-discover under correct slug, then fetch

```bash
python scripts/download_gospelink.py discover --contents-id NNN --slug {slug}
```

The user runs fetch in their PowerShell (captcha may pop up):

```powershell
python scripts/download_gospelink.py fetch `
    --slug {slug} `
    --series "{Series}" `
    --authority {N} --rigor {N} --importance {X} --context {X} `
    --tag {tag1} --tag {tag2} ...
```

> **Never run fetch from agent context.** Captcha pause is interactive,
> Chrome window must be visible to the user, and AWS WAF flags background
> processes more aggressively. Always hand the command to the user.

### Step 6 — Audit (agent)

```bash
python scripts/download_gospelink.py audit --slug {slug} --write-redo
```

If gaps reported, hand back to user to re-run fetch (it auto-resumes).
Re-audit until zero missing and zero tiny.

### Step 7 — Validate content (agent — MANDATORY)

Run this Python check before committing:

```python
import os, re
OUT = "corpus/en/books/gospelink/{slug}"
files = sorted(f for f in os.listdir(OUT) if f.endswith(".txt"))
LEAK = re.compile(
    r"verify you are human|human verification|awsWafCookie|let'?s confirm|"
    r"confirme que es humano|elija todo|challenge\.js|captcha",
    re.I,
)
HEADER = re.compile(r'{Author},\s*{Book Title}\s*\(\s*{year}\s*\)')
FOOTER = re.compile(r'Printed from Gospelink\.com\s*$')
leaks = no_h = no_f = 0
sizes = []
for fn in files:
    with open(os.path.join(OUT, fn), encoding='utf-8') as f:
        t = f.read()
    sizes.append(len(t))
    if LEAK.search(t): leaks += 1
    if not HEADER.search(t): no_h += 1
    if not FOOTER.search(t): no_f += 1
sizes.sort()
print(f"Files: {len(files)}  WAF leaks: {leaks}  no-header: {no_h}  no-footer: {no_f}")
print(f"Sizes: min={sizes[0]} median={sizes[len(sizes)//2]} max={sizes[-1]}")
assert leaks == 0 and no_h == 0 and no_f == 0, "Validation failed — investigate before commit."
```

Fail → investigate (`audit --write-redo`, redo offending IDs). Pass → step 8.

### Step 8 — Enrich metadata (agent)

```bash
python scripts/download_gospelink.py enrich-meta --slug {slug}
```

Backfills `year`, `volume`, `publisher`, `chapter_title`, topic tags into
each `.meta.json` from the TOC + body header line.

### Step 9 — Commit (agent)

```bash
git add corpus/en/books/gospelink/{slug} scripts/download_gospelink.py .gitignore
git commit -m "feat(corpus): add {Author} {Title} from Gospelink ({N} docs, EN)

{1-line description: e.g. covers Synoptic Gospels and Acts.} {N}/{N} docs
validated (0 WAF leaks, structure intact). Metadata: year {Y}, volume {V},
publisher Deseret Book, topic tags from TOC."
```

Update the catalog at the bottom of this file with the new entry.

## Operational notes

- **Delay 3.5–5.5 s/req** (set in script). DO NOT lower — observed ~3
  captcha hits per 340 docs at this rate.
- **Headed Chrome only.** Headless gets WAF-blocked instantly.
- **Anti-detection flags** already in `_launch_headed`: `--disable-blink-features=AutomationControlled` + `navigator.webdriver = undefined`.
- **Captcha resolution**: visible Chrome window → user solves drag-puzzle
  or image-grid → script auto-detects clearance via title/markup polling.
- **Sessions auto-refresh** every 50 docs during fetch (saves new
  `aws-waf-token` to `data/.gospelink-session.json`).
- **State**: `data/raw/gospelink/{slug}/_state.json` tracks `done` and
  `failed` IDs. Resume by re-running same fetch command.
- **Tiny files** are legitimate; McConkie has many <1 KB single-paragraph
  entries. The 400 B threshold in `audit` is the floor.
- **The `©` may render as `�` in non-UTF-8 terminals**, but files are
  always UTF-8. Ignore the cosmetic.

## Catalog of downloaded works

| contents-id | slug | author | title | docs | committed |
|---|---|---|---|---|---|
| 500 | dntc-vol-1 | Bruce R. McConkie | Doctrinal NT Commentary, vol. 1 (1965) | 340 | b46a5e0c3 |
| 501 | dntc-vol-2 | Bruce R. McConkie | Doctrinal NT Commentary, vol. 2 (1971) | 221 | 15d3e1dd9 |
| 502 | dntc-vol-3 | Bruce R. McConkie | Doctrinal NT Commentary, vol. 3 (1973) | 219 | 57074f572 |

When adding a new entry: include the commit SHA short hash (or `pending`
during the run) so future invocations can detect duplicates.

## Anti-patterns

- ❌ Running `fetch` from agent background context (captcha = `EOFError`).
- ❌ Running `fetch` without prior `bootstrap` if session > 24 h old.
- ❌ Skipping the WAF-leak validation step before commit.
- ❌ Lowering the inter-request delay.
- ❌ Asking user for `authority`/`rigor`/`tags` when the author is in the
  curated table — derive and confirm in one shot.
- ❌ Indexing into FTS/KG as part of this skill — that's a separate step
  the user requests explicitly.
