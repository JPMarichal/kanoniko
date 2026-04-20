#!/usr/bin/env python
"""Update data/gospelink-catalog.json with newly committed work."""
import json
import sys

if len(sys.argv) != 3:
    print("Usage: _update_catalog.py <slug> <metadata.json>", file=sys.stderr)
    sys.exit(2)

slug, meta_file = sys.argv[1], sys.argv[2]

with open(meta_file, encoding="utf-8") as f:
    meta = json.load(f)

catalog_path = "data/gospelink-catalog.json"
with open(catalog_path, encoding="utf-8") as f:
    catalog = json.load(f)

# Update or insert
found = False
for work in catalog["works"]:
    if work["slug"] == slug:
        work.update(meta)
        found = True
        break

if not found:
    catalog["works"].append(meta)

# Sort by contents_id
catalog["works"].sort(key=lambda x: x["contents_id"])

with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)
    f.write("\n")
