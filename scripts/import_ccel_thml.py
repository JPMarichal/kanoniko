#!/usr/bin/env python
"""
Parse CCEL ThML XML dictionaries (Easton, Smith) into Alejandría corpus format.

Input:  data/raw/ccel/{easton,smith}.xml
Output: corpus/en/reference/{dict-name}/{Letter}.txt + .meta.json per letter

Each .txt groups entries by letter with "## EntryName" headers.
"""

import xml.etree.ElementTree as ET
import json
import os
import re
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

WORKS = {
    "easton": {
        "xml": os.path.join(PROJECT_ROOT, "data", "raw", "ccel", "easton.xml"),
        "corpus_dir": "easton-bible-dictionary",
        "title": "Easton's Bible Dictionary",
        "author": "M.G. Easton",
        "year": 1897,
        "description": "Classic Protestant Bible dictionary with short and long entries on words, people, places, and topics.",
    },
    "smith": {
        "xml": os.path.join(PROJECT_ROOT, "data", "raw", "ccel", "smith.xml"),
        "corpus_dir": "smith-bible-dictionary",
        "title": "Smith's Bible Dictionary",
        "author": "William Smith",
        "year": 1884,
        "description": "Comprehensive Bible dictionary covering persons, places, antiquities, natural history, and geography.",
    },
}

# ThML namespace handling — CCEL uses no namespace prefix but we need to handle it
NS = {}


def strip_ns(tag):
    """Remove XML namespace from tag."""
    return tag.split("}")[-1] if "}" in tag else tag


def extract_text(elem):
    """Recursively extract text from an element, converting scripRef to inline refs."""
    parts = []
    if elem.text:
        parts.append(elem.text)

    for child in elem:
        tag = strip_ns(child.tag)
        if tag == "scripRef":
            passage = child.get("passage", "")
            text = extract_text(child).strip()
            if passage:
                parts.append(passage)
            elif text:
                parts.append(text)
        elif tag in ("note", "added"):
            # Skip editorial notes
            pass
        elif tag == "a":
            text = extract_text(child).strip()
            if text:
                parts.append(text)
        elif tag == "br":
            parts.append("\n")
        elif tag in ("p", "div", "div1", "div2", "div3"):
            inner = extract_text(child).strip()
            if inner:
                parts.append("\n" + inner + "\n")
        elif tag in ("i", "em"):
            inner = extract_text(child).strip()
            if inner:
                parts.append(inner)
        elif tag in ("b", "strong"):
            inner = extract_text(child).strip()
            if inner:
                parts.append(inner)
        else:
            inner = extract_text(child)
            if inner:
                parts.append(inner)

        if child.tail:
            parts.append(child.tail)

    return "".join(parts)


def clean_text(text):
    """Clean up extracted text."""
    # Normalize whitespace within lines
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_scripture_refs(elem):
    """Extract all scripture references from an element."""
    refs = set()
    for scrip in elem.iter():
        tag = strip_ns(scrip.tag)
        if tag == "scripRef":
            passage = scrip.get("passage", "")
            if passage:
                refs.add(passage.strip())
    return sorted(refs)


def parse_thml(xml_path):
    """Parse a ThML XML file and return dict of {letter: [(term, definition, refs)]}."""
    print(f"  Parsing {xml_path}...")

    # Read and clean the XML (remove DTD reference that causes issues)
    with open(xml_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove DTD declaration to avoid network fetch
    content = re.sub(r"<!DOCTYPE[^>]+>", "", content)

    root = ET.fromstring(content)

    entries_by_letter = defaultdict(list)
    entry_count = 0

    # Find all glossary entries (term + def pairs)
    # ThML structure: ThML.body > div1 > div2 (per letter) > glossary > term + def
    body = None
    for elem in root:
        if strip_ns(elem.tag) == "ThML.body":
            body = elem
            break

    if body is None:
        print("  ERROR: No ThML.body found")
        return entries_by_letter

    # Walk the tree looking for term/def pairs
    current_term = None

    def walk(elem):
        nonlocal current_term, entry_count
        tag = strip_ns(elem.tag)

        if tag == "term":
            current_term = extract_text(elem).strip()

        elif tag == "def" and current_term:
            definition = clean_text(extract_text(elem))
            refs = extract_scripture_refs(elem)

            if definition and len(definition) > 5:
                letter = current_term[0].upper()
                if not letter.isalpha():
                    letter = "_"
                entries_by_letter[letter].append({
                    "term": current_term,
                    "definition": definition,
                    "scripture_refs": refs,
                })
                entry_count += 1

            current_term = None

        else:
            for child in elem:
                walk(child)

    walk(body)
    print(f"  Found {entry_count} entries across {len(entries_by_letter)} letters")
    return entries_by_letter


def write_corpus(entries_by_letter, work_config):
    """Write entries to corpus files grouped by letter."""
    corpus_base = os.path.join(PROJECT_ROOT, "corpus", "en", "reference", work_config["corpus_dir"])
    os.makedirs(corpus_base, exist_ok=True)

    total_entries = 0
    files_written = 0

    for letter in sorted(entries_by_letter.keys()):
        entries = entries_by_letter[letter]
        if not entries:
            continue

        # Write .txt file
        txt_path = os.path.join(corpus_base, f"{letter}.txt")
        lines = []
        all_refs = set()

        for entry in entries:
            lines.append(f"## {entry['term']}")
            lines.append("")
            lines.append(entry["definition"])
            lines.append("")
            all_refs.update(entry["scripture_refs"])

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        # Write .meta.json
        meta_path = os.path.join(corpus_base, f"{letter}.meta.json")
        meta = {
            "title": f"{work_config['title']} — {letter}",
            "author": work_config["author"],
            "year": work_config["year"],
            "language": "en",
            "source": "CCEL (Christian Classics Ethereal Library)",
            "license": "Public Domain",
            "category": "reference",
            "subcategory": "bible-dictionary",
            "description": work_config["description"],
            "entry_count": len(entries),
            "entries": [e["term"] for e in entries],
            "scripture_references": sorted(all_refs),
            "authority": {
                "doctrinal": 15,
                "rigor": 70,
                "official": False,
                "notes": "19th-century Protestant Bible dictionary; useful for historical/geographical context, not LDS doctrine"
            }
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        total_entries += len(entries)
        files_written += 1

    print(f"  Wrote {files_written} files ({total_entries} entries) to {corpus_base}")
    return total_entries


def main():
    works_to_process = sys.argv[1:] if len(sys.argv) > 1 else list(WORKS.keys())

    for work_id in works_to_process:
        if work_id not in WORKS:
            print(f"Unknown work: {work_id}")
            continue

        config = WORKS[work_id]
        print(f"\n{'='*60}")
        print(f"Processing: {config['title']}")
        print(f"{'='*60}")

        if not os.path.exists(config["xml"]):
            print(f"  XML not found: {config['xml']}")
            continue

        entries = parse_thml(config["xml"])
        write_corpus(entries, config)

    print("\nDone! Files written to corpus/en/reference/")
    print("Remember: NO reindex — commit to git only.")


if __name__ == "__main__":
    main()
