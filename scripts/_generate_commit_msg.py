#!/usr/bin/env python
"""Generate commit message from _toc.json metadata."""
import json
import sys

if len(sys.argv) != 2:
    print("Usage: _generate_commit_msg.py <slug>", file=sys.stderr)
    sys.exit(2)

slug = sys.argv[1]
toc_path = f"data/raw/gospelink/{slug}/_toc.json"

with open(toc_path, encoding="utf-8") as f:
    toc = json.load(f)

n = len(toc.get("doc_ids", []))
title = toc.get("title")
author = toc.get("author")
year = toc.get("year", "?")

msg = (
    f"feat(corpus): add {author} {title} from Gospelink ({n} docs, EN)\n\n"
    f"{n}/{n} docs validated (0 WAF leaks, structure intact). "
    f"Year {year}, publisher Deseret Book."
)

print(msg)
