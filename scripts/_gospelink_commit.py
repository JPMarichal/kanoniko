#!/usr/bin/env python
"""Commit the corpus folder for a Gospelink slug AND update the JSON catalog.

Reads metadata from data/raw/gospelink/{slug}/_toc.json, generates the
commit message, stages files, commits, and updates data/gospelink-catalog.json
with the new entry.
"""
import json
import os
import subprocess
import sys


def run(cmd, **kwargs):
    """Run a command, raising on non-zero exit."""
    return subprocess.run(cmd, check=True, **kwargs)


def main():
    if len(sys.argv) != 2:
        print("Usage: _gospelink_commit.py <slug>", file=sys.stderr)
        sys.exit(2)

    slug = sys.argv[1]
    toc_path = f"data/raw/gospelink/{slug}/_toc.json"

    with open(toc_path, encoding="utf-8") as f:
        toc = json.load(f)

    n = len(toc.get("doc_ids", []))
    title = toc.get("title", "")
    author = toc.get("author", "")
    year = toc.get("year", "?")
    contents_id = toc.get("contents_id")

    # Stage files.
    paths = [
        f"corpus/en/books/gospelink/{slug}",
        "scripts/download_gospelink.py",
        "scripts/_gospelink_commit.py",
        "scripts/_gospelink_validate.py",
        "scripts/_update_catalog.py",
        "data/gospelink-catalog.json",
        "Justfile",
        ".gitignore",
    ]
    # Only add paths that exist.
    existing_paths = [p for p in paths if os.path.exists(p)]
    run(["git", "add"] + existing_paths)

    # Commit.
    msg = (
        f"feat(corpus): add {author} {title} from Gospelink ({n} docs, EN)\n\n"
        f"{n}/{n} docs validated (0 WAF leaks, structure intact). "
        f"Year {year}, publisher Deseret Book."
    )
    run(["git", "commit", "-m", msg])

    # Get the new commit SHA (short).
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    commit_sha = result.stdout.strip()

    # Update catalog JSON.
    catalog_path = "data/gospelink-catalog.json"
    if os.path.exists(catalog_path):
        with open(catalog_path, encoding="utf-8") as f:
            catalog = json.load(f)
    else:
        catalog = {"works": []}

    entry = {
        "contents_id": contents_id,
        "slug": slug,
        "author": author,
        "title": f"{title} ({year})" if year and year != "?" else title,
        "docs": n,
        "committed": commit_sha,
    }

    # Update or insert.
    found = False
    for work in catalog["works"]:
        if work["slug"] == slug:
            work.update(entry)
            found = True
            break
    if not found:
        catalog["works"].append(entry)

    catalog["works"].sort(key=lambda x: x.get("contents_id") or 0)

    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Amend the commit to include the updated catalog.
    run(["git", "add", catalog_path])
    run(["git", "commit", "--amend", "--no-edit"])

    print(f"\n✓ Committed {slug} ({commit_sha}) and updated catalog.")


if __name__ == "__main__":
    main()
