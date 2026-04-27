#!/usr/bin/env python3
"""Download scripture study aids from churchofjesuschrist.org.

Downloads the Guide to the Scriptures (GEE), Topical Guide, Bible Dictionary,
and JST Appendix. Each entry becomes a .txt + .meta.json file pair.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_study_aids.py --aid gs --lang eng
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_study_aids.py --aid gs --lang spa
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_study_aids.py --aid tg --lang eng
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_study_aids.py --aid bd --lang eng
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_study_aids.py --aid jst --lang eng
    python scripts/scrape_study_aids.py --aid gs --lang eng --dry-run
    python scripts/scrape_study_aids.py --aid gs --lang eng --list-only   # just list entries
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

import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_ROOT / "corpus"
BASE_URL = "https://www.churchofjesuschrist.org"
REQUEST_DELAY = 0.3

# ── Study aid definitions ───────────────────────────────────────────────────
# Each aid: (site_path_prefix, corpus_subdir, description)
AIDS = {
    "gs": ("/study/scriptures/gs", "study-aids/guide-to-scriptures", "Guide to the Scriptures"),
    "tg": ("/study/scriptures/tg", "study-aids/topical-guide", "Topical Guide"),
    "bd": ("/study/scriptures/bd", "study-aids/bible-dictionary", "Bible Dictionary"),
    "jst": ("/study/scriptures/jst", "study-aids/jst-appendix", "JST Appendix"),
    "bible-ref": ("/study/scriptures/bible-reference", "study-aids/reference-guide-holy-bible", "Reference Guide to the Holy Bible"),
    "bofm-ref": ("/study/scriptures/bofm-reference", "study-aids/reference-guide-book-of-mormon", "Reference Guide to the Book of Mormon"),
    "triple-index": ("/study/scriptures/triple-index", "study-aids/index-triple-combination", "Index to the Triple Combination"),
}

SECTION_SPLIT_AIDS = {"bible-ref", "bofm-ref"}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "section"


def get_session(ca_bundle: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; AlejandriaBot/1.0; scripture-study)"
    })
    session.verify = ca_bundle or True
    return session


# ── Index scraping ──────────────────────────────────────────────────────────

def scrape_index(site_prefix: str, lang: str, session: requests.Session) -> list[tuple[str, str]]:
    """Scrape the index page to get all entry slugs and titles.

    Returns list of (slug, title) tuples.
    """
    url = f"{BASE_URL}{site_prefix}?lang={lang}"
    print(f"  Fetching index: {url}")

    try:
        r = session.get(url, timeout=60)
        r.raise_for_status()
        r.encoding = "utf-8"
    except requests.RequestException as e:
        print(f"  ERROR fetching index: {e}", file=sys.stderr)
        return []

    soup = BeautifulSoup(r.text, "lxml")

    entries = []
    seen_slugs = set()

    # Find all links that point to entries under this study aid
    # Pattern: /study/scriptures/gs/slug or /study/scriptures/tg/slug etc.
    prefix_pattern = site_prefix + "/"

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        # Normalize: remove lang param, domain, etc.
        # Handle both absolute and relative URLs
        if href.startswith("http"):
            # Remove domain
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(href)
            path = parsed.path
        else:
            path = href.split("?")[0]

        if prefix_pattern not in path:
            continue

        # Extract slug: everything after the prefix
        idx = path.find(prefix_pattern)
        slug = path[idx + len(prefix_pattern):].strip("/")

        if not slug or slug in seen_slugs:
            continue

        # Skip if slug contains another slash (sub-pages we don't want)
        if "/" in slug:
            continue

        seen_slugs.add(slug)
        title = a_tag.get_text().strip()
        entries.append((slug, title))

    return entries


# ── Entry scraping ──────────────────────────────────────────────────────────

def scrape_entry_api(site_prefix: str, slug: str, lang: str,
                     session: requests.Session) -> Optional[dict]:
    """Scrape a single entry using the JSON API.

    The Church site loads content dynamically; the API returns HTML in a JSON wrapper.
    """
    uri = f"{site_prefix}/{slug}"
    api_url = f"{BASE_URL}/study/api/v3/language-pages/type/content?lang={lang}&uri={uri}"

    try:
        r = session.get(api_url, timeout=30)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        print(f"    ERROR fetching API: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"    ERROR: non-JSON response for {slug}", file=sys.stderr)
        return None

    # The content is HTML inside the JSON
    html_content = data.get("content", {}).get("body", "")
    if not html_content:
        # Try alternate structure
        html_content = data.get("content", "")
        if isinstance(html_content, dict):
            html_content = html_content.get("body", "") or json.dumps(html_content)

    if not html_content or not isinstance(html_content, str):
        return None

    soup = BeautifulSoup(html_content, "lxml")

    # Extract title
    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text().strip()

    # Extract body text
    body_block = soup.find("div", class_="body-block")
    if not body_block:
        body_block = soup.find("article") or soup

    paragraphs = []
    for el in body_block.find_all(["p", "li", "h2", "h3", "h4", "dt", "dd"]):
        # Skip nav and footer elements
        if el.find_parent("footer") or el.find_parent("nav"):
            continue
        if el.find_parent("header"):
            continue

        text = el.get_text()
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            paragraphs.append(text)

    full_text = "\n\n".join(paragraphs)

    # Extract scripture references (links to scriptures)
    references = []
    for a_tag in body_block.find_all("a", href=True):
        href = a_tag["href"]
        if "/study/scriptures/" in href and "/gs/" not in href and "/tg/" not in href and "/bd/" not in href:
            ref_text = a_tag.get_text().strip()
            if ref_text:
                references.append(ref_text)

    metadata = {
        "title": title,
        "source_url": f"{BASE_URL}{site_prefix}/{slug}?lang={lang}",
    }
    if references:
        metadata["scripture_references"] = references

    # Also try meta description from the API data
    meta = data.get("meta", {})
    if meta.get("title"):
        metadata["title"] = meta["title"]
    if meta.get("description"):
        metadata["meta_description"] = meta["description"]

    return {"text": full_text, "metadata": metadata}


def scrape_entry_html(site_prefix: str, slug: str, lang: str,
                      session: requests.Session,
                      include_nav: bool = False,
                      split_sections: bool = False) -> Optional[dict | list[dict]]:
    """Scrape entry directly from HTML page.

    Args:
        include_nav: If True, include content inside <nav> elements.
            Needed for TG/BD where scripture references live in nav.index blocks.
    """
    url = f"{BASE_URL}{site_prefix}/{slug}?lang={lang}"

    try:
        r = session.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = "utf-8"
    except requests.RequestException as e:
        print(f"    ERROR fetching {url}: {e}", file=sys.stderr)
        return None

    soup = BeautifulSoup(r.text, "lxml")

    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text().strip()

    body = soup.find("div", class_="body-block") or soup.find("article")
    if not body:
        return None

    # For TG/BD: extract see-also and reference list from nav.index blocks
    see_also = []
    references = []
    if include_nav:
        navs = body.find_all("nav", class_="index")
        for nav in navs:
            text = re.sub(r"\s+", " ", nav.get_text()).strip()
            if text.lower().startswith("see also") or text.lower().startswith("véase también"):
                see_also.append(text)
            elif text.lower().startswith("see ") or text.lower().startswith("véase "):
                # Pure redirect — "See X" with no other content
                see_also.append(text)
            else:
                # Scripture reference list — extract individual items
                for li in nav.find_all("li"):
                    ref = re.sub(r"\s+", " ", li.get_text()).strip()
                    if ref:
                        references.append(ref)

    if split_sections:
        intro_blocks = []
        results = []

        for child in body.children:
            if getattr(child, "name", None) is None:
                continue

            if child.name == "section":
                heading_el = child.find(["h2", "h3"])
                heading = heading_el.get_text(" ", strip=True) if heading_el else "Section"

                section_parts = []
                for el in child.find_all(["p", "li", "h2", "h3", "dt", "dd"]):
                    if el.find_parent("footer"):
                        continue
                    if el.find_parent("nav"):
                        continue
                    text = re.sub(r"\s+", " ", el.get_text()).strip()
                    if text:
                        section_parts.append(text)

                section_refs = []
                for nav in child.find_all("nav", class_="index"):
                    text = re.sub(r"\s+", " ", nav.get_text()).strip()
                    if text.lower().startswith("see also") or text.lower().startswith("véase también"):
                        section_parts.insert(0, text)
                    elif text.lower().startswith("see ") or text.lower().startswith("véase "):
                        section_parts.insert(0, text)
                    else:
                        for li in nav.find_all("li"):
                            ref = re.sub(r"\s+", " ", li.get_text()).strip()
                            if ref:
                                section_refs.append(ref)

                parts = []
                if section_parts:
                    parts.append("\n\n".join(section_parts))
                if section_refs:
                    parts.append("\n".join(section_refs))
                section_text = "\n\n".join(parts)

                if section_text.strip():
                    results.append({
                        "slug": slugify(heading),
                        "text": section_text,
                        "metadata": {
                            "title": f"{title} — {heading}",
                            "section_title": heading,
                            "source_url": url,
                            "source_slug": slug,
                        },
                    })
                continue

            if child.name in {"p", "ul", "ol", "h2", "h3", "dt", "dd"}:
                text = re.sub(r"\s+", " ", child.get_text()).strip()
                if text:
                    intro_blocks.append(text)

        if intro_blocks:
            results.insert(0, {
                "slug": "introduction",
                "text": "\n\n".join(intro_blocks),
                "metadata": {
                    "title": f"{title} — Introduction",
                    "section_title": "Introduction",
                    "source_url": url,
                    "source_slug": slug,
                },
            })

        return results or None

    paragraphs = []
    for el in body.find_all(["p", "li", "h2", "h3", "dt", "dd"]):
        if el.find_parent("footer"):
            continue
        if el.find_parent("nav"):
            continue  # nav content handled separately when include_nav=True
        text = el.get_text()
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            paragraphs.append(text)

    # Build full text
    parts = []
    if see_also:
        parts.append("\n".join(see_also))
    if paragraphs:
        parts.append("\n\n".join(paragraphs))
    if references:
        parts.append("\n".join(references))
    full_text = "\n\n".join(parts)

    metadata = {
        "title": title,
        "source_url": url,
    }
    if see_also:
        metadata["see_also"] = see_also

    return {"text": full_text, "metadata": metadata}


def scrape_entry(site_prefix: str, slug: str, lang: str,
                 session: requests.Session, use_api: bool = False,
                 include_nav: bool = False,
                 split_sections: bool = False) -> Optional[dict | list[dict]]:
    """Scrape a single entry. Uses HTML by default; API optional."""
    if use_api:
        result = scrape_entry_api(site_prefix, slug, lang, session)
        if result and result["text"].strip():
            return result
    return scrape_entry_html(site_prefix, slug, lang, session,
                             include_nav=include_nav,
                             split_sections=split_sections)


# ── Checkpoint ──────────────────────────────────────────────────────────────

def load_checkpoint(path: Path) -> set:
    if path.exists():
        return set(path.read_text(encoding="utf-8").strip().split("\n"))
    return set()


def save_checkpoint(path: Path, processed: set):
    path.write_text("\n".join(sorted(processed)) + "\n", encoding="utf-8")


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Scrape scripture study aids from churchofjesuschrist.org"
    )
    parser.add_argument("--aid", required=True, choices=list(AIDS.keys()),
                        help="Study aid to download")
    parser.add_argument("--lang", required=True, choices=["eng", "spa"],
                        help="Language")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY,
                        help="Delay between requests (seconds)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch but don't write files")
    parser.add_argument("--list-only", action="store_true",
                        help="Only list entries, don't download content")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from checkpoint")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit number of entries to download (0=all)")
    args = parser.parse_args()

    site_prefix, corpus_subdir, description = AIDS[args.aid]
    lang_dir = "en" if args.lang == "eng" else "es"
    corpus_aid_dir = CORPUS_DIR / lang_dir / corpus_subdir
    # Some study aids store reference content inside nav.index blocks
    include_nav = args.aid in ("tg", "bd", "bible-ref", "bofm-ref", "triple-index")
    split_sections = args.aid in SECTION_SPLIT_AIDS

    ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE", "")
    session = get_session(ca_bundle)

    print(f"=== {description} ({args.lang}) ===")
    print(f"  Output dir: {corpus_aid_dir}")

    # Step 1: Get all entry slugs
    entries = scrape_index(site_prefix, args.lang, session)
    print(f"  Found {len(entries)} entries")

    if not entries:
        print("  No entries found. Aborting.")
        return

    if args.list_only:
        for slug, title in entries:
            print(f"    {slug}: {title}")
        return

    # Checkpoint
    checkpoint_path = PROJECT_ROOT / "data" / f"scrape_{args.aid}_{args.lang}_checkpoint.txt"
    processed = load_checkpoint(checkpoint_path) if args.resume else set()
    if args.resume:
        print(f"  Resuming: {len(processed)} already processed")

    if args.limit > 0:
        entries = entries[:args.limit]
        print(f"  Limited to {args.limit} entries")

    print()

    stats = {"downloaded": 0, "written_files": 0, "skipped": 0, "errors": 0, "empty": 0}
    total = len(entries)

    for i, (slug, title) in enumerate(entries):
        if slug in processed:
            stats["skipped"] += 1
            continue

        print(f"  [{i+1}/{total}] {slug} ...", end=" ", flush=True)

        if i > 0:
            time.sleep(args.delay)

        result = scrape_entry(site_prefix, slug, args.lang, session,
                      include_nav=include_nav,
                      split_sections=split_sections)

        if result is None:
            print("ERROR")
            stats["errors"] += 1
            continue

        results = result if isinstance(result, list) else [result]
        results = [item for item in results if item and item["text"].strip()]

        if not results:
            print("EMPTY")
            stats["empty"] += 1
            continue

        char_count = sum(len(item["text"]) for item in results)
        print(f"OK ({char_count} chars, {len(results)} file(s)) — {results[0]['metadata'].get('title', '?')}")

        if args.dry_run:
            for item in results:
                item_slug = item.get("slug") or slug
                print(f"    [DRY RUN] Would write: {corpus_aid_dir / item_slug}.txt")
        else:
            corpus_aid_dir.mkdir(parents=True, exist_ok=True)
            for item in results:
                item_slug = item.get("slug") or slug
                txt_path = corpus_aid_dir / f"{item_slug}.txt"
                meta_path = corpus_aid_dir / f"{item_slug}.meta.json"

                txt_path.write_text(item["text"], encoding="utf-8")
                meta_path.write_text(
                    json.dumps(item["metadata"], ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                stats["written_files"] += 1

        processed.add(slug)
        stats["downloaded"] += 1

        # Save checkpoint every 50 entries
        if not args.dry_run and stats["downloaded"] % 50 == 0:
            save_checkpoint(checkpoint_path, processed)

    # Final checkpoint
    if not args.dry_run:
        save_checkpoint(checkpoint_path, processed)

    print(f"\n=== Summary ===")
    action = "would be written" if args.dry_run else "written"
    print(f"  Downloaded: {stats['downloaded']} entries {action}")
    if args.dry_run:
        print("  Files planned: see dry-run lines above")
    else:
        print(f"  Files written: {stats['written_files']}")
    print(f"  Skipped (checkpoint): {stats['skipped']}")
    print(f"  Empty: {stats['empty']}")
    print(f"  Errors: {stats['errors']}")


if __name__ == "__main__":
    main()
