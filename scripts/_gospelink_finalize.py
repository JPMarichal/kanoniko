#!/usr/bin/env python
"""End-to-end finalize for a Gospelink slug:
audit → enrich-meta → validate → commit + catalog update.

Accepts either a slug ("mormon-doctrine") or a contents-id ("569").
If the argument is numeric, scans data/raw/gospelink/*/_toc.json to find
the matching slug.
"""
import glob
import json
import os
import subprocess
import sys


RAW_BASE = "data/raw/gospelink"


def resolve_slug(arg: str) -> str:
    """If arg is numeric, look up the slug via _toc.json files. Else return arg."""
    if not arg.isdigit():
        return arg
    target_id = int(arg)
    for toc_path in glob.glob(os.path.join(RAW_BASE, "*", "_toc.json")):
        try:
            with open(toc_path, encoding="utf-8") as f:
                toc = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if toc.get("contents_id") == target_id:
            return os.path.basename(os.path.dirname(toc_path))
    raise SystemExit(
        f"ERROR: no _toc.json found for contents-id {target_id} in {RAW_BASE}/. "
        f"Run discover first."
    )


def run(cmd):
    """Run a command, propagating exit code on failure."""
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    if len(sys.argv) != 2:
        print("Usage: _gospelink_finalize.py <slug-or-contents-id>", file=sys.stderr)
        sys.exit(2)

    slug = resolve_slug(sys.argv[1])
    print(f"Slug resolved: {slug}\n")

    run(["python", "scripts/download_gospelink.py", "audit", "--slug", slug, "--write-redo"])
    run(["python", "scripts/download_gospelink.py", "enrich-meta", "--slug", slug])
    run(["python", "scripts/_gospelink_validate.py", slug])
    run(["python", "scripts/_gospelink_commit.py", slug])


if __name__ == "__main__":
    main()
