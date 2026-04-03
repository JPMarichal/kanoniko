#!/usr/bin/env python3
"""Sanitize conference talk .txt files: move notes to .meta.json.

Finds the "Notas" / "Notes" section at the end of each .txt file,
extracts the full note text into .meta.json["notes_text"], and strips
it from the .txt so it doesn't pollute NER/chunking.

The notes data is NOT lost — it lives in .meta.json alongside
scripture_refs. Only the .txt (which feeds the indexing pipeline)
is cleaned.

Usage:
    python scripts/sanitize_conference_notes.py              # run
    python scripts/sanitize_conference_notes.py --dry-run    # preview
    python scripts/sanitize_conference_notes.py --period 202510
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CORPUS_ROOT = Path(__file__).resolve().parent.parent / "corpus"

# Pattern: "Notas" or "Notes" on its own line, typically after 70%+ of content
NOTES_HEADER_RE = re.compile(r"^\s*(?:Notas?|Notes)\s*$", re.MULTILINE)


def find_notes_boundary(text: str) -> int | None:
    """Find the start position of the notes section.

    Only matches if the header appears in the last 40% of the file,
    to avoid false positives from talks that mention "Notes" in content.
    Returns the character offset of the notes header, or None.
    """
    threshold = int(len(text) * 0.6)
    for m in NOTES_HEADER_RE.finditer(text):
        if m.start() >= threshold:
            return m.start()
    return None


def extract_notes(notes_text: str) -> list[str]:
    """Parse individual notes from the notes section text.

    Returns list of note strings like:
    ["1. Russell M. Nelson, ...", "2. See Doctrine and Covenants 12:7–8.", ...]
    """
    lines = notes_text.strip().splitlines()
    # Skip the "Notas" header itself
    content_lines = []
    started = False
    for line in lines:
        if not started:
            if NOTES_HEADER_RE.match(line):
                started = True
            continue
        content_lines.append(line)

    # Join and split by numbered note pattern
    full_text = "\n".join(content_lines).strip()
    if not full_text:
        return []

    # Split on note numbers: "1. ", "2. ", etc. at start of line
    # Some notes use "1.  " (double space after pandoc)
    notes = re.split(r"\n(?=\d{1,3}\.\s)", full_text)
    return [n.strip() for n in notes if n.strip()]


def sanitize_file(txt_path: Path, dry_run: bool = False) -> bool:
    """Sanitize a single .txt file. Returns True if notes were found and moved."""
    meta_path = txt_path.with_suffix(".meta.json")

    text = txt_path.read_text(encoding="utf-8")
    boundary = find_notes_boundary(text)

    if boundary is None:
        return False

    # Split content and notes
    content = text[:boundary].rstrip() + "\n"
    notes_section = text[boundary:]
    notes_list = extract_notes(notes_section)

    if not notes_list:
        return False

    if dry_run:
        logger.info("[DRY RUN] %s — %d notes found, content %d→%d chars",
                     txt_path.name, len(notes_list), len(text), len(content))
        return True

    # Update .meta.json with full notes text
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    else:
        meta = {}

    meta["notes_text"] = notes_list

    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Write cleaned .txt
    txt_path.write_text(content, encoding="utf-8")

    return True


def main():
    parser = argparse.ArgumentParser(description="Move conference notes from .txt to .meta.json")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--period", type=str, help="Only process a specific period (e.g. 202510)")
    parser.add_argument("--lang", type=str, help="Only process a specific language (en or es)")
    args = parser.parse_args()

    # Find all conference .txt files
    txt_files = []
    for lang_dir in ("en", "es"):
        gc_dir = CORPUS_ROOT / lang_dir / "general-conference"
        if gc_dir.exists():
            txt_files.extend(sorted(gc_dir.rglob("*.txt")))

    if args.period:
        txt_files = [f for f in txt_files if f"/{args.period}/" in f.as_posix() or f"\\{args.period}\\" in str(f)]
    if args.lang:
        txt_files = [f for f in txt_files if f.as_posix().split("/corpus/")[-1].startswith(args.lang + "/")]

    logger.info("Scanning %d conference .txt files", len(txt_files))

    sanitized = 0
    no_notes = 0
    errors = 0

    for i, txt_path in enumerate(txt_files, 1):
        try:
            if sanitize_file(txt_path, dry_run=args.dry_run):
                sanitized += 1
            else:
                no_notes += 1
        except Exception:
            logger.exception("Failed: %s", txt_path)
            errors += 1

        if i % 500 == 0:
            logger.info("Progress: %d/%d (%.0f%%)", i, len(txt_files), 100 * i / len(txt_files))

    logger.info("Done: %d sanitized, %d no-notes, %d errors out of %d total",
                sanitized, no_notes, errors, len(txt_files))


if __name__ == "__main__":
    main()
