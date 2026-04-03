#!/usr/bin/env python3
"""Convert conference talk HTML files to plain text + .meta.json.

Reads every .html file under corpus/*/general-conference/, extracts
structured metadata into .meta.json, converts the talk content to
plain text via pandoc, and removes the original HTML.

Requirements:
- pandoc installed and on PATH
- BeautifulSoup4 (pip install beautifulsoup4)

Usage:
    python scripts/convert_conference_html.py                # convert all
    python scripts/convert_conference_html.py --dry-run      # preview only
    python scripts/convert_conference_html.py --period 202410  # single conference
"""

from __future__ import annotations

import argparse
import glob
import json
import logging
import subprocess
import sys
from pathlib import Path

# Add src to path so we can reuse the conference parser
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from alejandria.ingestion.conference_parser import parse_conference_talk

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CORPUS_ROOT = Path(__file__).resolve().parent.parent / "corpus"


def extract_content_html(html: str) -> str:
    """Extract .content + .notes divs as an HTML fragment for pandoc."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one(".content")
    if not content:
        return ""
    # Notes are excluded — they go to .meta.json as scripture_refs.
    # Including them in text pollutes NER with name+calling concatenations.
    return str(content)


def html_to_text_pandoc(html_fragment: str) -> str:
    """Convert an HTML fragment to plain text via pandoc."""
    result = subprocess.run(
        ["pandoc", "-f", "html", "-t", "plain", "--wrap=none"],
        input=html_fragment.encode("utf-8"),
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pandoc failed: {result.stderr.decode('utf-8', errors='replace')}")
    return result.stdout.decode("utf-8").strip()


def talk_to_meta(talk) -> dict:
    """Build a .meta.json dict from a parsed ConferenceTalk."""
    meta = {
        "title": talk.title,
        "author": talk.author,
        "author_raw": talk.author_raw,
        "calling": talk.calling,
        "calling_raw": talk.calling_raw,
        "conference_date": talk.conference_date,
        "lang": talk.lang,
        "source_url": talk.source_url,
        "category": "general-conference",
        "authority": 80,
    }
    if talk.note_count:
        meta["note_count"] = talk.note_count
    if talk.scripture_refs:
        meta["scripture_refs"] = talk.scripture_refs
    return meta


def convert_file(html_path: Path, dry_run: bool = False) -> bool:
    """Convert a single HTML file. Returns True on success."""
    txt_path = html_path.with_suffix(".txt")
    meta_path = html_path.with_suffix(".meta.json")

    try:
        raw_html = html_path.read_text(encoding="utf-8", errors="replace")

        # Extract metadata using existing parser
        rel_path = html_path.relative_to(CORPUS_ROOT).as_posix()
        talk = parse_conference_talk(raw_html, file_path=rel_path)
        meta = talk_to_meta(talk)

        # Extract content HTML and convert to text
        content_html = extract_content_html(raw_html)
        if not content_html.strip():
            logger.warning("No .content div found: %s", html_path)
            return False

        plain_text = html_to_text_pandoc(content_html)
        if not plain_text.strip():
            logger.warning("Empty text after conversion: %s", html_path)
            return False

        if dry_run:
            logger.info("[DRY RUN] Would convert: %s", rel_path)
            logger.info("  Author: %s | Title: %s | Date: %s", meta["author"], meta["title"], meta["conference_date"])
            logger.info("  Text length: %d chars", len(plain_text))
            return True

        # Write .meta.json
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        # Write .txt
        txt_path.write_text(plain_text + "\n", encoding="utf-8")

        # Remove .html
        html_path.unlink()

        return True

    except Exception:
        logger.exception("Failed to convert: %s", html_path)
        return False


def main():
    parser = argparse.ArgumentParser(description="Convert conference HTML to txt + meta.json")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--period", type=str, help="Convert only a specific period (e.g. 202410)")
    parser.add_argument("--lang", type=str, help="Convert only a specific language (en or es)")
    args = parser.parse_args()

    # Find all HTML files
    pattern = str(CORPUS_ROOT / "**" / "general-conference" / "**" / "*.html")
    html_files = sorted(glob.glob(pattern, recursive=True))

    if args.period:
        html_files = [f for f in html_files if f"/{args.period}/" in f.replace("\\", "/") or f"\\{args.period}\\" in f]
    if args.lang:
        html_files = [f for f in html_files if f.replace("\\", "/").split("/corpus/")[-1].startswith(args.lang + "/")]

    logger.info("Found %d HTML files to convert", len(html_files))

    success = 0
    failed = 0
    for i, html_file in enumerate(html_files, 1):
        path = Path(html_file)
        if convert_file(path, dry_run=args.dry_run):
            success += 1
        else:
            failed += 1

        if i % 500 == 0:
            logger.info("Progress: %d/%d (%.0f%%)", i, len(html_files), 100 * i / len(html_files))

    logger.info("Done: %d converted, %d failed out of %d total", success, failed, len(html_files))


if __name__ == "__main__":
    main()
