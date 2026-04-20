#!/usr/bin/env python
"""Extract metadata from _toc.json for catalog entry."""
import json
import subprocess
import sys

if len(sys.argv) != 2:
    print("Usage: _get_toc_metadata.py <slug>", file=sys.stderr)
    sys.exit(2)

slug = sys.argv[1]
toc_path = f"data/raw/gospelink/{slug}/_toc.json"

with open(toc_path, encoding="utf-8") as f:
    toc = json.load(f)

# Get latest commit SHA for this slug
result = subprocess.run(
    ["git", "log", "-1", "--format=%h", f"corpus/en/books/gospelink/{slug}"],
    capture_output=True,
    text=True,
    check=True,
)
commit_sha = result.stdout.strip()

# Extract from TOC
metadata = {
    "contents_id": toc.get("contents_id"),
    "slug": slug,
    "author": toc.get("author"),
    "title": toc.get("title"),
    "docs": len(toc.get("doc_ids", [])),
    "committed": commit_sha,
}

# Output as JSON (will be captured by Justfile)
print(json.dumps(metadata, ensure_ascii=False))
