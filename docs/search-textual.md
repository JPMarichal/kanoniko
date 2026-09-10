# Textual Search (Postgres FTS)

Full-text search using Postgres `tsvector` + GIN, ranked with `ts_rank_cd` (cover-density).

> The SQLite FTS5 implementation was retired with the rest of the SQLite stack (§3.4 of
> `postgres-migration.md`). See [`system-spec.md`](system-spec.md).

## How it works

1. During ingestion, chunk text is written to `chunks` and a `tsvector` column is maintained
   (GIN index).
2. Queries use `websearch_to_tsquery('spanish', …)` — Spanish is the dominant corpus language and
   its stemming is permissive enough that English proper nouns pass through as literals.
   *(Future refinement: detect query language and dispatch to `'english'`, or run both and merge —
   measure latency first.)*
3. Ranking via `ts_rank_cd` (cover density). Observed p95 ~44 ms (migration benchmark).
4. Optional filter by corpus subdirectory (`scriptures`, `general-conference`, …).
5. Per-call connection (no pool) — queries are short reads.

## Schema (`chunks`)

```
chunk_id     bigint PRIMARY KEY
file_path    text NOT NULL
chunk_index  int  NOT NULL
text         text NOT NULL
start_char   int
end_char     int
metadata     jsonb
reference    text            -- scripture reference, nullable
-- tsvector column + GIN index for FTS
```

Canonical DDL: `src/alejandria/storage/postgres/ddl.sql`.

## Usage

```python
from alejandria.search.textual import TextualSearch  # or the module's search entry point

results = TextualSearch().search(query="faith repentance", limit=20, source_filter="scriptures")
```

## API

```
POST /search/text
{ "query": "faith and repentance", "limit": 20, "source_filter": "scriptures" }
```

## Key module

`search/textual.py` — `websearch_to_tsquery` + `ts_rank_cd`; returns `TextSearchResult`
(file path, chunk index, text, score, reference). Connection via
`alejandria.storage.postgres.connection.get_connection`.
