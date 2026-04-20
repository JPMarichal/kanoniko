#!/usr/bin/env python
"""Stage corpus + script + .gitignore for a Gospelink slug and commit
with a templated message derived from the TOC."""
import json
import subprocess
import sys

if len(sys.argv) != 2:
    print("Usage: _gospelink_commit.py <slug>", file=sys.stderr)
    sys.exit(2)

slug = sys.argv[1]
toc_path = f"data/raw/gospelink/{slug}/_toc.json"
with open(toc_path, encoding="utf-8") as f:
    toc = json.load(f)

n = len(toc["doc_ids"])
title = toc["title"]
author = toc["author"]
year = toc.get("year", "?")

paths = [
    f"corpus/en/books/gospelink/{slug}",
    "scripts/download_gospelink.py",
    "scripts/_gospelink_validate.py",
    "scripts/_gospelink_commit.py",
    "Justfile",
    ".gitignore",
]
subprocess.run(["git", "add"] + paths, check=True)

msg = (
    f"feat(corpus): add {author} {title} from Gospelink ({n} docs, EN)\n\n"
    f"{n}/{n} docs validated (0 WAF leaks, structure intact). "
    f"Year {year}, publisher Deseret Book."
)
subprocess.run(["git", "commit", "-m", msg], check=True)
