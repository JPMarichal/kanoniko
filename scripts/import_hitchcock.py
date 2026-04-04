#!/usr/bin/env python
"""
Parse Hitchcock's Bible Names Dictionary into Alejandria corpus format.

Input:  data/raw/ccel/hitchcock.txt (simple "Name, meaning" format)
Output: corpus/en/reference/hitchcock-bible-names/{Letter}.txt + .meta.json
"""

import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "ccel", "hitchcock.txt")
CORPUS_DIR = os.path.join(PROJECT_ROOT, "corpus", "en", "reference", "hitchcock-bible-names")


def parse_hitchcock(path):
    """Parse the simple name, meaning format."""
    entries_by_letter = {}

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Skip header (title + description + blank lines)
    in_entries = False
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect start of entries (single letter line = section header)
        if len(line) == 1 and line.isalpha():
            in_entries = True
            continue

        if not in_entries:
            continue

        # Parse "Name, meaning" format
        if ", " in line:
            parts = line.split(", ", 1)
            name = parts[0].strip()
            meaning = parts[1].strip()

            letter = name[0].upper()
            if letter not in entries_by_letter:
                entries_by_letter[letter] = []

            entries_by_letter[letter].append({
                "name": name,
                "meaning": meaning
            })

    return entries_by_letter


def write_corpus(entries_by_letter):
    """Write entries grouped by letter."""
    os.makedirs(CORPUS_DIR, exist_ok=True)

    total = 0
    for letter in sorted(entries_by_letter.keys()):
        entries = entries_by_letter[letter]

        # Write .txt
        lines = []
        for entry in entries:
            lines.append("## {}".format(entry["name"]))
            lines.append("")
            lines.append(entry["meaning"])
            lines.append("")

        txt_path = os.path.join(CORPUS_DIR, "{}.txt".format(letter))
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        # Write .meta.json
        meta = {
            "title": "Hitchcock's Bible Names Dictionary - {}".format(letter),
            "author": "Roswell D. Hitchcock",
            "year": 1869,
            "language": "en",
            "source": "CCEL (Christian Classics Ethereal Library)",
            "license": "Public Domain",
            "category": "reference",
            "subcategory": "bible-names",
            "description": "2,500+ Bible proper names with etymological meanings from Hebrew/Greek. Compact format ideal for KG entity enrichment.",
            "entry_count": len(entries),
            "entries": [e["name"] for e in entries],
            "authority": {
                "doctrinal": 10,
                "rigor": 60,
                "official": False,
                "notes": "19th-century etymological dictionary; meanings are traditional, some debated by modern scholarship"
            }
        }
        meta_path = os.path.join(CORPUS_DIR, "{}.meta.json".format(letter))
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        total += len(entries)
        print("  {}: {} entries".format(letter, len(entries)))

    print("\nTotal: {} entries in {} files".format(total, len(entries_by_letter)))
    return total


def main():
    print("Parsing Hitchcock's Bible Names Dictionary...")
    entries = parse_hitchcock(INPUT_FILE)
    write_corpus(entries)
    print("Done! Files in {}".format(CORPUS_DIR))


if __name__ == "__main__":
    main()
