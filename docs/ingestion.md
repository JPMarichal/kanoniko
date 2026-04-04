# Ingestion Pipeline

End-to-end flow from source site to indexed corpus — three independent layers.

---

## Layer 1: Acquisition (scripts/)

Each source has a dedicated download script. All share `scripts/lib/church_scraper.py`
as a common base (HTTP session, API v3 access, HTML parsing, `write_corpus_file`).

### Scripts by source type

| Script | Source | Method | Output |
|--------|--------|--------|--------|
| `download_scriptures.py` | Canonical scriptures | API v3 | `corpus/{lang}/scriptures/` |
| `download_conference.py` | General conference talks | API v3 | `corpus/{lang}/general-conference/` |
| `download_manual.py` | All manuals (CFM, Seminary, ToP, Gospel Topics, Saints…) | API v3 | `corpus/{lang}/manuals/` |
| `download_music.py` | Hymns, children's songbook, youth music, hymn-helps | API v3 + lyrics extractor | `corpus/{lang}/music/` |
| `download_jesus_the_christ.py` | *Jesus the Christ* (Talmage) | API v3 | `corpus/{lang}/books/jesus-the-christ/` |
| `download_gutenberg.py` | Classic LDS books (Talmage, Discourses of BY) | Project Gutenberg | `corpus/en/books/` |
| `download_easter_study_plan.py` | Easter study plan | API v3 | `corpus/{lang}/manuals/easter-plan/` |
| `download_christmas_study_plan.py` | Christmas study plan | API v3 | `corpus/{lang}/manuals/christmas-study-plan-{year}/` |
| `download_pme.py` | Missionary Prep Manual | API v3 | `corpus/{lang}/manuals/missionary-preparation/` |
| `scrape_harmony.py` | Harmony of the Gospels | HTML (table parser) | `corpus/{lang}/study-aids/harmony-of-the-gospels/` |
| `scrape_abbreviations.py` | Scripture abbreviations | HTML | `corpus/{lang}/study-aids/abbreviations/` |
| `scrape_bible_chronology.py` | Bible chronology | HTML | `corpus/en/study-aids/bible-chronology/` |
| `scrape_study_aids.py` | TG, BD, GS, JST | HTML | `corpus/{lang}/study-aids/` |

Each script produces two files per document: `{slug}.txt` (content) + `{slug}.meta.json`
(structured metadata: title, authority, scripture refs, author, etc.).

### Two access strategies in church_scraper.py

**API v3** (`fetch_api_page`): `GET /study/api/v3/language-pages/type/content?lang={lang}&uri={uri}`
Returns structured JSON with `body_html`, `title`, `footnotes`. Works for most prose content.

**HTML direct** (`fetch_html` / `session.fetch_html`): Used when the API returns a nav manifest
instead of content (e.g., ES Harmony of Gospels uses a single combined table at `/harmony/table`
rather than per-section pages).

### Running all downloads (orchestrator)

```bash
# Full corpus refresh (72 jobs, 6 parallel workers)
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_all.py

# Specific groups only
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_all.py --group manuals music

# Available groups: scriptures, manuals, music, study-aids, special
# Note: 'conference' is excluded from defaults — it requires --period YYYYMM

# New conference session (run separately after each April/October conference)
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt \
  python scripts/download_conference.py --period 202604

# List all jobs without running
python scripts/download_all.py --list
```

Downloads are **idempotent** — re-running skips files that already exist on disk.
Results and errors are logged to `logs/download_all_{timestamp}.log`.

---

## Layer 2: Indexing (API)

The corpus is **never indexed automatically**. Run indexing explicitly when ready.

### Canonical post-commit workflow

After downloading and committing new files:

```bash
# 1. Commit the new corpus files
git add corpus/ && git commit -m "Add new corpus materials"

# 2. Index only the new files — identified from git, no SHA scan of existing files
git diff --name-only HEAD~1 HEAD -- 'corpus/**/*.txt' \
  | python -c "
import sys, json, urllib.request
paths = [p[len('corpus/'):].strip() for p in sys.stdin if p.strip().startswith('corpus/')]
body = json.dumps({'paths': paths, 'force': False}).encode()
req = urllib.request.Request('http://localhost:4300/index/ingest', data=body,
      headers={'Content-Type': 'application/json'}, method='POST')
print(json.loads(urllib.request.urlopen(req).read()))
"

# 3. Monitor progress
curl http://localhost:4300/index/status
```

> Use `/index/ingest` (git-targeted), not `/index/trigger` (full SHA scan).
> At 24K+ files, `/trigger` wastes 20-30 min scanning existing files before finding new ones.

### Three-phase pipeline

| Phase | What | Implementation |
|-------|------|----------------|
| **1a. Delete** (updates only) | Remove old FTS chunks and Qdrant vectors | Serial, single connection; skipped for new files |
| **1b. Parse + chunk** | Read file, chunk text, build metadata | **Parallel** — `ThreadPoolExecutor(8 workers)`, no SQLite |
| **1c. FTS insert** | Insert chunks into SQLite FTS5 | Serial, **single shared connection** for all files |
| **2. Embeddings** | Batch-encode all new chunks at once | GPU (fast) or CPU (slow); one `encode()` call for all files |
| **3. KG + Qdrant** | spaCy NER → Neo4j; vector upsert → Qdrant | Per-file; Neo4j writes batched with UNWIND |

`/index/status` tracks Phase 1 progress only. Check `/health` (vector/node counts) to confirm
Phases 2 and 3 are progressing.

### KG enrichment from meta.json

During Phase 3, `_enrich_kg_from_meta()` reads the companion `.meta.json` to create
structured KG edges without NER — faster and more precise than text extraction:

| meta.json field | KG relation created |
|----------------|---------------------|
| `scripture_refs` | `work -[CITES]-> scripture_reference` |
| `parallel_events` | `passage -[PARALLEL_ACCOUNT_OF]-> passage` |
| `author` / `composer` | `work -[AUTHORED_BY]-> person` |

---

## Layer 3: Post-indexing

After new material is indexed:

```bash
# Rebuild entity profiles (mention counts, key passages)
curl -X POST http://localhost:4300/index/build-profiles \
  -H "Content-Type: application/json" -d '{"phase": "metadata"}'

# If gazetteers changed, rebuild the KG from existing chunks (~15 min)
curl -X POST http://localhost:4300/index/rebuild-kg
```

---

## Corpus structure

```
corpus/{lang}/scriptures/{volume}/{book}/{chapter}.txt   # verse-numbered
corpus/{lang}/general-conference/{year}/{period}/{slug}.txt
corpus/{lang}/manuals/{manual-key}/{slug}.txt
corpus/{lang}/music/{collection}/{slug}.txt
corpus/{lang}/study-aids/{aid}/{slug}.txt
```

Each `.txt` has a companion `.meta.json` with:
- `title`, `lang`, `category`, `subcategory`
- `authority` (0-100 doctrinal weight)
- `source_url`
- `scripture_refs`, `tags`, and collection-specific fields

---

## Key classes

| Class | File | Role |
|-------|------|------|
| `IngestionPipeline` | `ingestion/pipeline.py` | Orchestrates all 3 phases |
| `DocumentRegistry` | `ingestion/registry.py` | SHA-256 change tracking per file |
| `chunk_text` / `chunk_scripture` | `ingestion/chunker.py` | Chunking strategies |
| `KGExtractor` | `knowledge/extractor.py` | NER + relation extraction per chunk |
| `ChurchSession` | `scripts/lib/church_scraper.py` | Shared HTTP session for all scripts |
