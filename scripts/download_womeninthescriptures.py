"""Download Women in the Scriptures profiles (Tier 1) from womeninthescriptures.com.

Reads URLs from data/wits_urls_profiles.txt, fetches HTML, extracts blog post
content, and writes .txt + .meta.json pairs to corpus/en/web/women-in-the-scriptures/.

Author: Heather Farrell (independent LDS scholarship).
Authority: 20/50/interesante, official=false.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# Allow importing from scripts/lib/
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.church_scraper import (
    html_to_structured_text,
    write_corpus_file,
    Checkpoint,
    PROJECT_ROOT,
    CORPUS_ROOT,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────

URL_FILE = PROJECT_ROOT / "data" / "wits_urls_profiles.txt"
OUTPUT_DIR = CORPUS_ROOT / "en" / "web" / "women-in-the-scriptures"
SITE_NAME = "Women in the Scriptures"
AUTHOR = "Heather Farrell"
DEFAULT_DELAY = 1.0  # respectful rate limit for personal blog
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
CA_BUNDLE = PROJECT_ROOT / "docker" / "ca-certificates.crt"


def load_urls(path: Path) -> list[str]:
    """Load URLs from file, skipping comments and blanks."""
    urls = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls


def url_to_slug(url: str) -> str:
    """Extract slug from WordPress URL like /2009/03/nephis-wife.html -> nephis-wife."""
    path = urlparse(url).path.rstrip("/")
    filename = path.split("/")[-1]
    return filename.replace(".html", "")


def fetch_post(session: requests.Session, url: str, delay: float) -> dict | None:
    """Fetch a blog post and extract title + body HTML."""
    time.sleep(delay)
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.warning("Failed to fetch %s: %s", url, e)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # WordPress title
    title_el = soup.select_one("h1.entry-title") or soup.select_one("h3.post-title")
    title = title_el.get_text(strip=True) if title_el else ""

    # WordPress post body
    body_el = soup.select_one("div.entry-content") or soup.select_one("div.post-body")
    if not body_el:
        logger.warning("No body found for %s", url)
        return None

    # Extract date from URL path: /YYYY/MM/slug.html
    date = ""
    m = re.search(r"/(\d{4})/(\d{2})/", url)
    if m:
        date = f"{m.group(1)}-{m.group(2)}"

    return {
        "title": title,
        "body_html": str(body_el),
        "date": date,
        "url": url,
    }


def process_post(post: dict) -> tuple[str, dict]:
    """Convert fetched post to plain text + metadata dict."""
    text = html_to_structured_text(post["body_html"])

    if not text or len(text.strip()) < 100:
        return "", {}

    meta = {
        "title": post["title"],
        "author": AUTHOR,
        "site_name": SITE_NAME,
        "source_url": post["url"],
        "date": post["date"],
        "category": "web",
        "subcategory": "women-in-the-scriptures",
        "tags": ["women", "scripture-profiles", "biblical-women"],
        "authority": 20,
        "rigor": 50,
        "importance": "interesante",
        "official": False,
        "lang": "eng",
    }

    return text, meta


def main():
    parser = argparse.ArgumentParser(description="Download Women in the Scriptures profiles")
    parser.add_argument("--dry-run", action="store_true", help="List URLs without downloading")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="Delay between requests (seconds)")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--limit", type=int, default=0, help="Limit downloads (0=all)")
    args = parser.parse_args()

    urls = load_urls(URL_FILE)
    logger.info("Loaded %d URLs from %s", len(urls), URL_FILE)

    if args.dry_run:
        for url in urls:
            slug = url_to_slug(url)
            print(f"{slug} -> {url}")
        print(f"\nTotal: {len(urls)} URLs")
        return

    checkpoint = Checkpoint("wits", "eng")
    if args.resume:
        checkpoint.load()
        logger.info("Resumed: %d already processed", len(checkpoint.processed))

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    if CA_BUNDLE.exists():
        session.verify = str(CA_BUNDLE)

    downloaded = 0
    skipped = 0
    errors = 0

    for i, url in enumerate(urls, 1):
        slug = url_to_slug(url)

        if checkpoint.is_done(slug):
            skipped += 1
            continue

        if args.limit and downloaded >= args.limit:
            logger.info("Limit reached (%d)", args.limit)
            break

        logger.info("[%d/%d] %s", i, len(urls), slug)

        try:
            post = fetch_post(session, url, args.delay)
            if not post:
                errors += 1
                continue

            text, meta = process_post(post)
            if not text:
                logger.warning("  Empty content after conversion")
                errors += 1
                continue

            write_corpus_file(OUTPUT_DIR, slug, text, meta)
            logger.info("  -> %s.txt (%d chars)", slug, len(text))

            checkpoint.mark(slug)
            checkpoint.save_if_needed(every=10)
            downloaded += 1

        except Exception:
            logger.exception("  Failed: %s", url)
            errors += 1

    checkpoint.save()

    stats = {
        "total_urls": len(urls),
        "downloaded": downloaded,
        "skipped": skipped,
        "errors": errors,
    }
    logger.info("Done. Stats: %s", json.dumps(stats))


if __name__ == "__main__":
    main()
