#!/usr/bin/env python3
"""Download the General Handbook from churchofjesuschrist.org.

Scrapes the full General Handbook (Serving in The Church of Jesus Christ
of Latter-day Saints) in both English and Spanish. Each chapter becomes
a .txt + .meta.json file pair under corpus/{lang}/manuals/general-handbook/.

The handbook is updated a few times per year — re-run this script to
refresh the corpus with the latest version.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_handbook.py --lang eng
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_handbook.py --lang spa
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_handbook.py --lang all
    python scripts/scrape_handbook.py --lang eng --dry-run
    python scripts/scrape_handbook.py --lang eng --list-only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_ROOT / "corpus"
BASE_URL = "https://www.churchofjesuschrist.org"
HANDBOOK_PATH = "/study/manual/general-handbook"
REQUEST_DELAY = 0.5

# ── Session ────────────────────────────────────────────────────────────────


def get_session(ca_bundle: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; AlejandriaBot/1.0; scripture-study)"
    })
    session.verify = ca_bundle or True
    return session


# ── Index discovery ────────────────────────────────────────────────────────


def discover_chapters(lang: str, session: requests.Session) -> list[dict]:
    """Discover all handbook chapters from the table of contents page.

    Returns list of dicts with keys: slug, title, url.
    """
    url = f"{BASE_URL}{HANDBOOK_PATH}?lang={lang}"
    print(f"  Fetching index: {url}")

    try:
        r = session.get(url, timeout=60)
        r.raise_for_status()
        r.encoding = "utf-8"
    except requests.RequestException as e:
        print(f"  ERROR fetching index: {e}", file=sys.stderr)
        return []

    soup = BeautifulSoup(r.text, "lxml")

    chapters = []
    seen_slugs = set()
    prefix = HANDBOOK_PATH + "/"

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        # Normalize URL to path
        if href.startswith("http"):
            path = urlparse(href).path
        else:
            path = href.split("?")[0]

        if prefix not in path:
            continue

        idx = path.find(prefix)
        slug = path[idx + len(prefix):].strip("/")

        if not slug or slug in seen_slugs:
            continue

        # Skip deep sub-pages (we want chapter-level pages only)
        if "/" in slug:
            continue

        seen_slugs.add(slug)
        title = a_tag.get_text().strip()
        chapters.append({
            "slug": slug,
            "title": title,
            "url": f"{BASE_URL}{HANDBOOK_PATH}/{slug}?lang={lang}",
        })

    return chapters


# ── Chapter scraping ───────────────────────────────────────────────────────


def scrape_chapter(slug: str, lang: str,
                   session: requests.Session) -> Optional[dict]:
    """Scrape a single handbook chapter page.

    Returns dict with keys: text, metadata.
    """
    url = f"{BASE_URL}{HANDBOOK_PATH}/{slug}?lang={lang}"

    try:
        r = session.get(url, timeout=60)
        r.raise_for_status()
        r.encoding = "utf-8"
    except requests.RequestException as e:
        print(f"    ERROR fetching {url}: {e}", file=sys.stderr)
        return None

    soup = BeautifulSoup(r.text, "lxml")

    # Extract title
    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text().strip()

    # Find title-number (e.g., "1.", "2.", "0.")
    chapter_number = ""
    title_num_el = soup.find("p", class_="title-number")
    if title_num_el:
        chapter_number = title_num_el.get_text().strip()

    # Find main content
    body = soup.find("div", class_="body-block") or soup.find("article")
    if not body:
        return None

    # Extract structured text preserving section hierarchy and notation
    lines = []
    sections = {}  # section_number -> title (e.g., "8.1.1" -> "Purpose")
    current_section = ""  # track current section for cross-ref attribution
    # Collect internal cross-references per section: {"8.1.2": ["8.4", "6.2.1.1"]}
    cross_references: dict[str, list[str]] = {}
    # Regex for internal handbook cross-references (e.g., "see 38.4.1.5", "véase 27.3.1")
    xref_re = re.compile(r"(?:see|véase|ver)\s+(\d+\.\d+(?:\.\d+)*)", re.IGNORECASE)

    for el in body.find_all(["h2", "h3", "h4", "p", "li", "dt", "dd"]):
        # Skip nav, footer, header content
        if el.find_parent("footer") or el.find_parent("nav"):
            continue
        if el.find_parent("header") and el.name not in ("h2", "h3", "h4"):
            continue

        # Get section number if present
        section_num = ""
        num_span = el.find("span", class_="title-number")
        if num_span:
            section_num = re.sub(r"\s+", " ", num_span.get_text()).strip()
        else:
            # title-number can also be a <p> sibling in <header>
            parent_header = el.find_parent("header")
            if parent_header:
                num_p = parent_header.find("p", class_="title-number")
                if num_p:
                    section_num = re.sub(r"\s+", " ", num_p.get_text()).strip()

        text = el.get_text()
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            continue

        # Format headings with section number prefix
        if el.name in ("h2", "h3", "h4"):
            prefix = {"h2": "##", "h3": "###", "h4": "####"}[el.name]
            if section_num:
                lines.append(f"\n{prefix} {section_num} {text}\n")
                sections[section_num] = text
                current_section = section_num
            else:
                lines.append(f"\n{prefix} {text}\n")
        elif el.name == "li":
            lines.append(f"- {text}")
        else:
            lines.append(text)

        # Extract internal cross-references from this element's text
        for match in xref_re.finditer(text):
            ref = match.group(1)
            if current_section:
                cross_references.setdefault(current_section, [])
                if ref not in cross_references[current_section]:
                    cross_references[current_section].append(ref)

    full_text = "\n".join(lines).strip()
    # Clean up excessive blank lines
    full_text = re.sub(r"\n{3,}", "\n\n", full_text)

    # Build metadata
    metadata = {
        "title": title,
        "source_url": f"{BASE_URL}{HANDBOOK_PATH}/{slug}?lang={lang}",
        "source_type": "general-handbook",
        "authority": 65,  # Normative — governing policy reference
        "official": True,
        "audience": "leadership",
    }
    if chapter_number:
        metadata["chapter_number"] = chapter_number
    if sections:
        metadata["sections"] = sections
    if cross_references:
        metadata["cross_references"] = cross_references

    # Extract any cross-references to scriptures
    scripture_refs = []
    for a_tag in body.find_all("a", href=True):
        href = a_tag["href"]
        if "/study/scriptures/" in href:
            ref_text = a_tag.get_text().strip()
            if ref_text and ref_text not in scripture_refs:
                scripture_refs.append(ref_text)
    if scripture_refs:
        metadata["scripture_references"] = scripture_refs

    return {"text": full_text, "metadata": metadata}


# ── Checkpoint ─────────────────────────────────────────────────────────────


def load_checkpoint(path: Path) -> set:
    if path.exists():
        return set(path.read_text(encoding="utf-8").strip().split("\n"))
    return set()


def save_checkpoint(path: Path, processed: set):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(sorted(processed)) + "\n", encoding="utf-8")


# ── Main ───────────────────────────────────────────────────────────────────


def run_lang(lang: str, args) -> dict:
    """Download handbook for one language. Returns stats dict."""
    lang_dir = "en" if lang == "eng" else "es"
    out_dir = CORPUS_DIR / lang_dir / "manuals" / "general-handbook"

    ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE", "")
    session = get_session(ca_bundle)

    print(f"\n=== General Handbook ({lang}) ===")
    print(f"  Output dir: {out_dir}")

    # Step 1: Discover chapters
    chapters = discover_chapters(lang, session)
    print(f"  Found {len(chapters)} chapters")

    if not chapters:
        print("  No chapters found. Aborting.")
        return {"downloaded": 0, "skipped": 0, "errors": 0, "empty": 0}

    if args.list_only:
        for ch in chapters:
            print(f"    {ch['slug']}: {ch['title']}")
        return {"downloaded": 0, "skipped": 0, "errors": 0, "empty": 0}

    # Checkpoint
    checkpoint_path = PROJECT_ROOT / "data" / f"scrape_handbook_{lang}_checkpoint.txt"
    processed = load_checkpoint(checkpoint_path) if args.resume else set()
    if args.resume and processed:
        print(f"  Resuming: {len(processed)} already processed")

    if args.limit > 0:
        chapters = chapters[:args.limit]
        print(f"  Limited to {args.limit} chapters")

    print()

    stats = {"downloaded": 0, "skipped": 0, "errors": 0, "empty": 0}
    total = len(chapters)

    for i, ch in enumerate(chapters):
        slug = ch["slug"]

        if slug in processed:
            stats["skipped"] += 1
            continue

        print(f"  [{i+1}/{total}] {slug} ...", end=" ", flush=True)

        if i > 0:
            time.sleep(args.delay)

        result = scrape_chapter(slug, lang, session)

        if result is None:
            print("ERROR")
            stats["errors"] += 1
            continue

        text = result["text"]
        metadata = result["metadata"]

        if not text.strip():
            print("EMPTY")
            stats["empty"] += 1
            continue

        char_count = len(text)
        print(f"OK ({char_count:,} chars) — {metadata.get('title', '?')}")

        if args.dry_run:
            print(f"    [DRY RUN] Would write: {out_dir / slug}.txt")
        else:
            out_dir.mkdir(parents=True, exist_ok=True)
            txt_path = out_dir / f"{slug}.txt"
            meta_path = out_dir / f"{slug}.meta.json"

            txt_path.write_text(text, encoding="utf-8")
            meta_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        processed.add(slug)
        stats["downloaded"] += 1

        # Save checkpoint every 10 chapters
        if not args.dry_run and stats["downloaded"] % 10 == 0:
            save_checkpoint(checkpoint_path, processed)

    # Final checkpoint
    if not args.dry_run:
        save_checkpoint(checkpoint_path, processed)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Scrape the General Handbook from churchofjesuschrist.org"
    )
    parser.add_argument("--lang", required=True, choices=["eng", "spa", "all"],
                        help="Language (or 'all' for both)")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY,
                        help="Delay between requests (seconds)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch but don't write files")
    parser.add_argument("--list-only", action="store_true",
                        help="Only list chapters, don't download content")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from checkpoint")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit number of chapters to download (0=all)")
    args = parser.parse_args()

    langs = ["eng", "spa"] if args.lang == "all" else [args.lang]

    for lang in langs:
        stats = run_lang(lang, args)
        action = "would be written" if args.dry_run else "written"
        print(f"\n=== Summary ({lang}) ===")
        print(f"  Downloaded: {stats['downloaded']} chapters {action}")
        print(f"  Skipped (checkpoint): {stats['skipped']}")
        print(f"  Empty: {stats['empty']}")
        print(f"  Errors: {stats['errors']}")


if __name__ == "__main__":
    main()
