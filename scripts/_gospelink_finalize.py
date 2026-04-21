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
CATALOG = "data/gospelink-catalog.json"


def find_pending_slugs():
    """Return slugs present in data/raw/gospelink/ but missing from the
    catalog as committed. A slug is 'pending' if its raw dir exists and
    either it has no catalog entry, or its entry lacks a 'committed' hash."""
    try:
        with open(CATALOG, encoding="utf-8") as f:
            catalog = json.load(f)
    except (OSError, json.JSONDecodeError):
        catalog = {"works": []}
    committed = {
        w["slug"] for w in catalog.get("works", []) if w.get("committed")
    }
    pending = []
    for entry in sorted(os.listdir(RAW_BASE)):
        raw_dir = os.path.join(RAW_BASE, entry)
        if not os.path.isdir(raw_dir):
            continue
        if entry in committed:
            continue
        # Skip leftover discover temp dirs (e.g. "_auto-2569") that never
        # got renamed. They have no _toc.json so audit would fail.
        if entry.startswith("_auto-"):
            continue
        if not os.path.exists(os.path.join(raw_dir, "_toc.json")):
            continue
        pending.append(entry)
    return pending


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


def run(cmd, check=True):
    """Run a command. If check=True, exit on failure; else return rc."""
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result.returncode


def finalize_one(slug, check=True):
    """Run the full pipeline for one slug. With check=False, returns True on
    success, False on any step failure (used for batch mode to keep going)."""
    print(f"\n=== Finalizing: {slug} ===\n")
    steps = [
        ["python", "scripts/download_gospelink.py", "audit", "--slug", slug, "--write-redo"],
        ["python", "scripts/download_gospelink.py", "enrich-meta", "--slug", slug],
        ["python", "scripts/_gospelink_validate.py", slug],
        ["python", "scripts/_gospelink_commit.py", slug],
    ]
    for cmd in steps:
        rc = run(cmd, check=check)
        if rc != 0:
            return False
    return True


def main():
    if len(sys.argv) > 2:
        print("Usage: _gospelink_finalize.py [<slug-or-contents-id>]", file=sys.stderr)
        sys.exit(2)

    if len(sys.argv) == 2 and sys.argv[1]:
        slug = resolve_slug(sys.argv[1])
        print(f"Slug resolved: {slug}\n")
        finalize_one(slug)
        return

    pending = find_pending_slugs()
    if not pending:
        print("No pending slugs — catalog matches data/raw/gospelink/.")
        return

    print(f"Found {len(pending)} pending slug(s):")
    for s in pending:
        print(f"  - {s}")
    reply = input("\nFinalize all? [y/N]: ").strip().lower()
    if reply != "y":
        print("Aborted.")
        sys.exit(1)

    succeeded, failed = [], []
    for slug in pending:
        if finalize_one(slug, check=False):
            succeeded.append(slug)
        else:
            failed.append(slug)
            print(f"\n!!! {slug} failed — continuing with next.\n", file=sys.stderr)

    print(f"\n=== Batch summary: {len(succeeded)} ok, {len(failed)} failed ===")
    if succeeded:
        print("OK:")
        for s in succeeded:
            print(f"  ✓ {s}")
    if failed:
        print("FAILED:")
        for s in failed:
            print(f"  ✗ {s}")
        sys.exit(1)


if __name__ == "__main__":
    main()
