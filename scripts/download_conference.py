#!/usr/bin/env python3
"""Download General Conference talks from churchofjesuschrist.org.

Downloads all talks for a given conference period, producing .txt + .meta.json
files ready for indexing. No intermediate HTML — text is extracted directly
from the API response via pandoc.

Usage:
    python scripts/download_conference.py --period 202604
    python scripts/download_conference.py --period 202604 --lang eng
    python scripts/download_conference.py --period 202604 --lang spa
    python scripts/download_conference.py --period 202604 --dry-run

Requires:
    - pandoc on PATH
    - requests (pip install requests)
    - beautifulsoup4 (pip install beautifulsoup4)

Environment:
    - REQUESTS_CA_BUNDLE: path to CA cert bundle (for corporate proxies)
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

# Add src to path for conference parser utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from alejandria.ingestion.conference_parser import normalize_calling, strip_author_title

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CORPUS_ROOT = Path(__file__).resolve().parent.parent / "corpus"
BASE_URL = "https://www.churchofjesuschrist.org"
API_URL = f"{BASE_URL}/study/api/v3/language-pages/type/content"
REQUEST_DELAY = 0.5  # seconds between requests — be polite

LANG_MAP = {"eng": "en", "spa": "es"}  # API lang → corpus dir


def fetch_json(uri: str, lang: str) -> dict:
    """Fetch a JSON page from the Church content API."""
    url = f"{API_URL}?lang={lang}&uri={uri}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def list_talks(period: str, lang: str) -> list[dict]:
    """Get the list of talks for a conference period.

    Returns list of dicts with keys: slug, title, speaker.
    """
    # Period format: YYYYMM → API uri: /general-conference/YYYY/MM
    year = period[:4]
    month = period[4:6]
    uri = f"/general-conference/{year}/{month}"

    data = fetch_json(uri, lang)
    body_html = data.get("content", {}).get("body", "")
    soup = BeautifulSoup(body_html, "html.parser")

    talks = []
    for link in soup.select("a[href]"):
        href = link.get("href", "")
        if f"/general-conference/{year}/{month}/" not in href:
            continue

        # Extract slug from href
        slug = href.split("/")[-1].split("?")[0]
        if not slug or slug in ("", year, month):
            continue

        # Extract title and speaker from the link structure
        title_el = link.select_one(".title")
        speaker_el = link.select_one(".primaryMeta")

        title = title_el.get_text(strip=True) if title_el else ""
        speaker = speaker_el.get_text(strip=True) if speaker_el else ""

        if title:  # Skip non-talk links
            talks.append({"slug": slug, "title": title, "speaker": speaker})

    logger.info("Found %d talks for %s/%s (%s)", len(talks), year, month, lang)
    return talks


def download_talk(slug: str, period: str, lang: str) -> dict[str, Any] | None:
    """Download a single talk and return structured data.

    Returns dict with: title, author, author_raw, calling, calling_raw,
    conference_date, lang, source_url, scripture_refs, content_html, note_count.
    """
    year = period[:4]
    month = period[4:6]
    uri = f"/general-conference/{year}/{month}/{slug}"

    try:
        data = fetch_json(uri, lang)
    except requests.HTTPError as e:
        logger.warning("Failed to fetch %s: %s", uri, e)
        return None

    body_html = data.get("content", {}).get("body", "")
    if not body_html:
        logger.warning("No body content for %s", uri)
        return None

    soup = BeautifulSoup(body_html, "html.parser")

    # Extract author and calling from byline
    author_raw = ""
    calling_raw = ""
    author_el = soup.select_one(".author-name")
    if author_el:
        author_raw = author_el.get_text(strip=True)
        # Remove "By " / "Por " prefix
        author_raw = re.sub(r"^(?:By|Por)\s+", "", author_raw, flags=re.IGNORECASE).strip()

    calling_el = soup.select_one(".author-role")
    if calling_el:
        calling_raw = calling_el.get_text(strip=True)

    # Extract title from metadata
    title = data.get("meta", {}).get("title", "")

    # Remove non-content elements before text extraction.
    # Notes/footnotes are excluded — they go to .meta.json as scripture_refs.
    # Including them pollutes NER with name+calling concatenations.
    for sel in (".byline", ".kicker", "footer", "header", "figure", "video",
                ".notes", ".study-note-ref", "sup", "sup.marker"):
        for el in soup.select(sel):
            el.decompose()

    # The remaining body is the talk content
    content_html = str(soup)

    # Extract footnotes and scripture refs
    footnotes = data.get("content", {}).get("footnotes", {})
    note_count = len(footnotes) if isinstance(footnotes, dict) else 0
    scripture_refs = _extract_scripture_refs(footnotes)

    # Build source URL
    source_url = f"{BASE_URL}/study/general-conference/{year}/{month}/{slug}?lang={lang}"

    # Conference date
    conference_date = f"{year}-{month}"

    return {
        "title": title,
        "author": strip_author_title(author_raw),
        "author_raw": author_raw,
        "calling": normalize_calling(calling_raw),
        "calling_raw": calling_raw,
        "conference_date": conference_date,
        "lang": lang,
        "source_url": source_url,
        "note_count": note_count,
        "scripture_refs": scripture_refs,
        "content_html": content_html,
    }


def _extract_scripture_refs(footnotes: dict | list | None) -> list[str]:
    """Extract scripture references from footnote data."""
    if not isinstance(footnotes, dict):
        return []

    # Import the regex from conference_parser
    from alejandria.ingestion.conference_parser import _SCRIPTURE_REF_RE

    refs = []
    for note_data in footnotes.values():
        if isinstance(note_data, dict):
            text = note_data.get("text", "")
            # Also check referenceUris for scripture paths
            for m in _SCRIPTURE_REF_RE.finditer(text):
                ref = m.group(1).strip()
                if ref and ref not in refs:
                    refs.append(ref)
    return refs


def html_to_text_pandoc(html: str) -> str:
    """Convert HTML to plain text via pandoc."""
    result = subprocess.run(
        ["pandoc", "-f", "html", "-t", "plain", "--wrap=none"],
        input=html.encode("utf-8"),
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pandoc failed: {result.stderr.decode('utf-8', errors='replace')}")
    return result.stdout.decode("utf-8").strip()


def slugify_filename(title: str, speaker: str) -> str:
    """Create a filesystem-safe filename from talk title and speaker.

    Matches the existing corpus naming convention:
    'Title of Talk (Elder Speaker Name).txt'
    """
    # Clean title
    clean_title = title.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    clean_title = re.sub(r'[<>:"/\\|?*]', '', clean_title).strip()

    # Clean speaker
    clean_speaker = speaker.replace("\xa0", " ").strip()
    clean_speaker = re.sub(r'[<>:"/\\|?*]', '', clean_speaker).strip()

    if clean_speaker:
        return f"{clean_title} ({clean_speaker})"
    return clean_title


def download_conference(period: str, lang: str, dry_run: bool = False) -> dict:
    """Download all talks for a conference period and language.

    Returns stats dict.
    """
    year = period[:4]
    month = period[4:6]
    corpus_lang = LANG_MAP.get(lang, lang)
    output_dir = CORPUS_ROOT / corpus_lang / "general-conference" / period

    talks = list_talks(period, lang)
    if not talks:
        logger.warning("No talks found for %s (%s)", period, lang)
        return {"talks": 0, "downloaded": 0, "skipped": 0, "errors": 0}

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    skipped = 0
    errors = 0

    for i, talk_info in enumerate(talks, 1):
        slug = talk_info["slug"]
        logger.info("[%d/%d] %s — %s", i, len(talks), talk_info["speaker"], talk_info["title"])

        if dry_run:
            downloaded += 1
            continue

        # Check if already downloaded
        filename = slugify_filename(talk_info["title"], talk_info["speaker"])
        txt_path = output_dir / f"{filename}.txt"
        if txt_path.exists():
            logger.info("  Already exists, skipping")
            skipped += 1
            continue

        time.sleep(REQUEST_DELAY)
        talk_data = download_talk(slug, period, lang)

        if talk_data is None:
            errors += 1
            continue

        try:
            # Convert to plain text
            plain_text = html_to_text_pandoc(talk_data["content_html"])
            if not plain_text.strip():
                logger.warning("  Empty content after conversion")
                errors += 1
                continue

            # Build meta (exclude content_html)
            meta = {k: v for k, v in talk_data.items() if k != "content_html"}
            meta["category"] = "general-conference"
            meta["authority"] = 80

            # Write files
            meta_path = output_dir / f"{filename}.meta.json"
            meta_path.write_text(
                json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            txt_path.write_text(plain_text + "\n", encoding="utf-8")

            downloaded += 1
            logger.info("  Saved: %s", txt_path.name)

        except Exception:
            logger.exception("  Failed to process %s", slug)
            errors += 1

    stats = {
        "period": period,
        "lang": lang,
        "talks": len(talks),
        "downloaded": downloaded,
        "skipped": skipped,
        "errors": errors,
    }
    logger.info("Stats: %s", json.dumps(stats))
    return stats


def main():
    parser = argparse.ArgumentParser(description="Download General Conference talks")
    parser.add_argument("--period", required=True, help="Conference period YYYYMM (e.g., 202604)")
    parser.add_argument("--lang", help="Language: eng or spa (default: both)")
    parser.add_argument("--dry-run", action="store_true", help="List talks without downloading")
    args = parser.parse_args()

    # Validate period format
    if not re.match(r"^\d{6}$", args.period):
        logger.error("Period must be YYYYMM format (e.g., 202604)")
        sys.exit(1)

    month = args.period[4:6]
    if month not in ("04", "10"):
        logger.warning("Unusual month %s — General Conference is typically 04 (April) or 10 (October)", month)

    languages = [args.lang] if args.lang else ["eng", "spa"]

    all_stats = []
    for lang in languages:
        stats = download_conference(args.period, lang, dry_run=args.dry_run)
        all_stats.append(stats)

    logger.info("=" * 60)
    for s in all_stats:
        logger.info(
            "%s (%s): %d talks, %d downloaded, %d skipped, %d errors",
            s["period"], s["lang"], s["talks"], s["downloaded"], s["skipped"], s["errors"],
        )


if __name__ == "__main__":
    main()
