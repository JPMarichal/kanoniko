# Textual Search (FTS5)

Full-text search using SQLite FTS5 with BM25 ranking.

## Overview

SQLite FTS5 provides the primary text search capability. It stores all chunks and serves as the backbone for document registry, entity profiles, and metadata.

## How It Works

1. Text is indexed into the `chunks_fts` virtual table
2. Queries use FTS5's built-in BM25 ranking algorithm
3. Results include file path, chunk index, text, score, and scripture reference
4. Optional filtering by corpus subdirectory (e.g., `scriptures`, `conference`)

## Schema

### `chunks` table
```sql
chunk_id     INTEGER PRIMARY KEY
file_path    TEXT NOT NULL
chunk_index  INTEGER NOT NULL
text         TEXT NOT NULL
start_char   INTEGER
end_char     INTEGER
metadata     TEXT (JSON)
reference    TEXT (scripture reference, nullable)
```

### `chunks_fts` virtual table
FTS5 index on the `text` column of `chunks`, enabling fast full-text queries.

## Usage

```python
from alejandria.search.textual import TextualSearch

ts = TextualSearch(db_path)
results = ts.search(query="faith repentance", limit=20, file_path_filter="scriptures")
```

## API

```
POST /search/text
{
  "query": "faith and repentance",
  "limit": 20,
  "source_filter": "scriptures"
}
```

## Key Class

`TextualSearch` (`search/textual.py`):
- `search(query, limit, file_path_filter)` — BM25-ranked search
- `index_chunk(...)` — Index a single chunk
- `delete_by_file(conn, file_path)` — Remove all chunks for a file
- `count_documents()`, `count_chunks()` — Statistics
- `get_connection()` — Raw SQLite connection for batch operations
