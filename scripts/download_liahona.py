#!/usr/bin/env python3
"""Download Liahona magazine articles from churchofjesuschrist.org.

Downloads all non-conference articles for a given issue or year range,
producing .txt + .meta.json files ready for indexing.

Conference talks are automatically detected and skipped (they already
exist in corpus/{lang}/general-conference/).

Usage:
    # Single issue
    python scripts/download_liahona.py --year 2024 --month 10
    python scripts/download_liahona.py --year 2024 --month 10 --lang eng

    # Full year (skips conference months automatically)
    python scripts/download_liahona.py --year 2024

    # Year range (D1 phase: 2021-2026)
    python scripts/download_liahona.py --year-from 2021 --year-to 2026

    # Dry run — list articles without downloading
    python scripts/download_liahona.py --year 2024 --month 10 --dry-run

    # Include conference issues (download non-talk articles only)
    python scripts/download_liahona.py --year 2024 --include-conference

    # Resume interrupted download
    python scripts/download_liahona.py --year 2024 --resume

Requires:
    - pandoc on PATH
    - requests, beautifulsoup4

Environment:
    - REQUESTS_CA_BUNDLE: path to CA cert bundle (for corporate proxies)
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.church_scraper import (
    ChurchSession,
    Checkpoint,
    DownloadStats,
    add_common_args,
    build_source_url,
    extract_footnotes_api,
    fetch_api_page,
    footnotes_to_meta,
    get_languages,
    html_to_structured_text,
    write_corpus_file,
    CORPUS_ROOT,
    LANG_MAP,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ── Conference talk detection ─────��───────────────────────────────────────

# Conference months by era (validated case-by-case, see fase0/liahona.md)
# Key = (year_from, year_to), Value = set of months that contain conference
CONFERENCE_MONTHS = [
    # 2000-2002: July (April conf) + January next year (October conf)
    (2000, 2002, {1, 7}),
    # 2003+: May (April conf) + November (October conf)
    (2003, 9999, {5, 11}),
]

# Slug patterns for conference talks: 2-digit prefix + speaker name
_CONF_SLUG_RE = re.compile(r"^\d{2}[a-z]")

# Session header keywords in TOC
_SESSION_KEYWORDS = {
    "saturday morning", "saturday afternoon", "saturday evening",
    "sunday morning", "sunday afternoon",
    "priesthood session", "women's session", "relief society",
    "general priesthood", "general young women",
    "sesión del sábado", "sesión del domingo",
    "sesión del sacerdocio", "sesión de mujeres",
}


def is_conference_month(year: int, month: int) -> bool:
    """Check if a given year/month is a known conference issue."""
    for y_from, y_to, months in CONFERENCE_MONTHS:
        if y_from <= year <= y_to:
            return month in months
    return False


def is_conference_talk_slug(slug: str) -> bool:
    """Detect if a slug looks like a conference talk (e.g., '11oaks', '35uchtdorf')."""
    return bool(_CONF_SLUG_RE.match(slug))


def is_conference_section(title: str) -> bool:
    """Check if a TOC section title indicates a conference session."""
    lower = title.lower()
    return any(kw in lower for kw in _SESSION_KEYWORDS)


# ── Article classification ────────────────────────────────────────────────

# Section name → content_type mapping
_SECTION_MAP = {
    "featured articles": "leader_message",
    "artículos destacados": "leader_message",
    "gospel solutions": "doctrinal_article",
    "soluciones del evangelio": "doctrinal_article",
    "latter-day saint voices": "member_story",
    "voces de los santos de los últimos días": "member_story",
    "come, follow me": "study_guide",
    "ven, sígueme": "study_guide",
    "young adults": "young_adult",
    "adultos jóvenes": "young_adult",
    "the church is here": "feature",
    "la iglesia está aquí": "feature",
    "news of the church": "news",
    "noticias de la iglesia": "news",
    "new callings": "news",
    "nuevos llamamientos": "news",
    "local pages": "local_pages",
    "páginas locales": "local_pages",
}

# Authority by content_type
_AUTHORITY_MAP = {
    "leader_message": 65,
    "doctrinal_article": 55,
    "study_guide": 60,
    "member_story": 40,
    "young_adult": 50,
    "historical": 50,
    "feature": 45,
    "news": 45,
    "local_pages": 30,
}

DEFAULT_AUTHORITY = 60  # Official Church publication


def classify_section(section_title: str) -> str:
    """Map a TOC section title to a content_type."""
    lower = section_title.lower().strip()
    for key, ct in _SECTION_MAP.items():
        if key in lower:
            return ct
    return "doctrinal_article"  # safe default


def authority_for_type(content_type: str) -> int:
    """Return authority level for a content type."""
    return _AUTHORITY_MAP.get(content_type, DEFAULT_AUTHORITY)


# ── TOC parsing ────────���──────────────────────────────────────────────────

def discover_liahona_toc(session: ChurchSession, year: int, month: int,
                         lang: str) -> list[dict]:
    """Discover articles in a Liahona issue via API v3.

    Parses the nav.manifest structure: h2.label sections followed by
    ul.doc-map lists containing article links.

    Returns list of dicts: {slug, title, author, section, uri}.
    """
    uri = f"/liahona/{year}/{month:02d}"
    page = fetch_api_page(session, uri, lang)
    if not page:
        logger.warning("No TOC found for Liahona %d/%02d (%s)", year, month, lang)
        return []

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page.body_html, "html.parser")

    nav = soup.select_one("nav.manifest")
    if not nav:
        nav = soup

    articles = []
    seen_slugs = set()

    def _extract_link(a, section_name=""):
        """Extract article info from a TOC link element."""
        href = a["href"].split("?")[0]
        if "/liahona/" not in href:
            return None

        slug = href.rstrip("/").split("/")[-1]
        if not slug or slug in seen_slugs:
            return None
        if slug in (str(year), f"{month:02d}", "contents"):
            return None

        title_el = a.select_one(".title")
        author_el = a.select_one(".primaryMeta")

        title = title_el.get_text(strip=True) if title_el else a.get_text(strip=True)
        author = author_el.get_text(strip=True) if author_el else ""

        if not title or len(title) < 3:
            return None

        if "/study/" in href:
            article_uri = href.split("/study")[1]
        else:
            article_uri = href

        seen_slugs.add(slug)
        return {
            "slug": slug,
            "title": title,
            "author": author,
            "section": section_name,
            "uri": article_uri,
        }

    # Strategy 1: Walk h2.label sections + ul.doc-map (new format 2021+)
    for h2 in nav.find_all("h2", class_="label"):
        section_name = h2.get_text(strip=True)
        ul = h2.find_next_sibling("ul", class_="doc-map")
        if not ul:
            continue
        for a in ul.select("a[href]"):
            entry = _extract_link(a, section_name)
            if entry:
                articles.append(entry)

    # Strategy 2: If few articles found, scan all nav links (old format)
    all_nav_links = nav.select("a[href]")
    nav_liahona_links = [a for a in all_nav_links
                         if "/liahona/" in a.get("href", "")]

    if len(articles) < len(nav_liahona_links) // 2:
        # Most links were missed — rescan all nav links
        seen_slugs.clear()
        articles.clear()
        for a in nav_liahona_links:
            entry = _extract_link(a, "")
            if entry:
                articles.append(entry)

    logger.info("Found %d articles in Liahona %d/%02d (%s)",
                len(articles), year, month, lang)
    return articles


# ── Article download ─────���────────────────────────────────────────────────

def download_article(session: ChurchSession, article: dict, year: int,
                     month: int, lang: str) -> dict | None:
    """Download a single Liahona article.

    Returns dict with all metadata + content, or None on failure.
    """
    page = fetch_api_page(session, article["uri"], lang)
    if not page:
        return None

    # Extract author from byline if not in TOC
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page.body_html, "html.parser")

    author = article.get("author", "")
    author_role = ""

    author_el = soup.select_one(".author-name")
    if author_el:
        raw = author_el.get_text(strip=True)
        author = re.sub(r"^(?:By|Por)\s+", "", raw, flags=re.IGNORECASE).strip()

    role_el = soup.select_one(".author-role")
    if role_el:
        author_role = role_el.get_text(strip=True)

    # Remove non-content elements
    for sel in (".byline", ".kicker", "footer", "header", "figure", "video",
                ".notes", ".study-note-ref", "sup", "sup.marker",
                "nav", ".manifest"):
        for el in soup.select(sel):
            el.decompose()

    # Convert to plain text
    content_html = str(soup)
    try:
        plain_text = html_to_structured_text(content_html)
    except RuntimeError as e:
        logger.warning("pandoc failed for %s: %s", article["slug"], e)
        return None

    if not plain_text or len(plain_text.strip()) < 50:
        logger.warning("Content too short for %s", article["slug"])
        return None

    # Extract footnotes
    footnotes = extract_footnotes_api(page.footnotes)
    fn_meta = footnotes_to_meta(footnotes)

    # Classify
    content_type = classify_section(article.get("section", ""))
    authority = authority_for_type(content_type)

    # Boost authority for known GA authors
    if author_role and any(t in author_role.lower() for t in
                           ("president", "presidente", "apostle", "apóstol",
                            "first presidency", "primera presidencia",
                            "quorum of the twelve", "quórum de los doce")):
        authority = max(authority, 65)
        if "leader" not in content_type:
            content_type = "leader_message"

    source_url = build_source_url(article["uri"], lang)

    meta = {
        "title": page.title or article["title"],
        "author": author,
        "author_role": author_role,
        "source": "Liahona",
        "source_url": source_url,
        "year": year,
        "month": month,
        "section": article.get("section", ""),
        "content_type": content_type,
        "category": "revistas",
        "subcategory": "Liahona",
        "lang": LANG_MAP.get(lang, lang),
        "authority": authority,
    }
    meta.update(fn_meta)

    return {
        "text": plain_text,
        "meta": meta,
        "slug": article["slug"],
    }


# ── Filename generation ────���──────────────────────────────────────────────

def make_filename(slug: str, title: str) -> str:
    """Create a filesystem-safe filename from slug.

    Uses the original slug from the Church site (already URL-safe).
    Falls back to sanitized title if slug is too short.
    """
    if len(slug) >= 3:
        return slug
    # Fallback: sanitize title
    clean = re.sub(r'[<>:"/\\|?*]', '', title).strip()
    clean = re.sub(r'\s+', '-', clean).lower()[:80]
    return clean or "untitled"


# ── Issue download orchestrator ─���─────────────────────────────────────────

def download_issue(session: ChurchSession, year: int, month: int, lang: str,
                   *, dry_run: bool = False, include_conference: bool = False,
                   checkpoint: Checkpoint | None = None) -> DownloadStats:
    """Download all articles for a single Liahona issue.

    Skips conference talks by default. With include_conference=True,
    downloads non-talk articles from conference issues.
    """
    stats = DownloadStats()
    is_conf = is_conference_month(year, month)

    if is_conf and not include_conference:
        logger.info("Skipping Liahona %d/%02d (%s) — conference issue", year, month, lang)
        return stats

    articles = discover_liahona_toc(session, year, month, lang)
    stats.pages = len(articles)

    if not articles:
        return stats

    corpus_lang = LANG_MAP.get(lang, lang)
    output_dir = CORPUS_ROOT / corpus_lang / "revistas" / "Liahona" / str(year) / f"{month:02d}"

    conf_skipped = 0

    for i, article in enumerate(articles, 1):
        slug = article["slug"]
        title = article["title"]

        # Skip conference talks in conference issues
        if is_conf and is_conference_talk_slug(slug):
            conf_skipped += 1
            continue

        # Check checkpoint
        ck_key = f"{year}/{month:02d}/{slug}"
        if checkpoint and checkpoint.is_done(ck_key):
            stats.skipped += 1
            continue

        # Check if file exists
        filename = make_filename(slug, title)
        txt_path = output_dir / f"{filename}.txt"
        if txt_path.exists():
            stats.skipped += 1
            if checkpoint:
                checkpoint.mark(ck_key)
            continue

        logger.info("[%d/%d] %s — %s", i, len(articles), article.get("author", "?"), title)

        if dry_run:
            section = article.get("section", "")
            ct = classify_section(section)
            logger.info("  [DRY] section=%s type=%s authority=%d", section, ct, authority_for_type(ct))
            stats.downloaded += 1
            continue

        result = download_article(session, article, year, month, lang)
        if result is None:
            stats.errors += 1
            continue

        write_corpus_file(output_dir, filename, result["text"], result["meta"])
        stats.downloaded += 1
        stats.footnotes_total += result["meta"].get("note_count", 0)
        stats.scripture_refs_total += len(result["meta"].get("scripture_refs", []))

        if checkpoint:
            checkpoint.mark(ck_key)
            checkpoint.save_if_needed(every=25)

        logger.info("  Saved: %s.txt (%d notes, %d refs)",
                    filename,
                    result["meta"].get("note_count", 0),
                    len(result["meta"].get("scripture_refs", [])))

    if conf_skipped:
        logger.info("  Skipped %d conference talks (already in corpus)", conf_skipped)

    return stats


# ── Year/range orchestrator ────���──────────────────────────────────────────

def discover_issue_months(session: ChurchSession, year: int, lang: str) -> list[int]:
    """Discover which months have Liahona issues for a given year.

    Fetches the year index page and extracts available month numbers.
    """
    uri = f"/liahona/{year}"
    page = fetch_api_page(session, uri, lang)
    if not page:
        # Fallback: try common months
        logger.warning("Cannot discover months for %d, trying all 12", year)
        return list(range(1, 13))

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page.body_html, "html.parser")

    months = set()
    for a in soup.select("a[href]"):
        href = a["href"]
        m = re.search(rf"/liahona/{year}/(\d{{2}})", href)
        if m:
            months.add(int(m.group(1)))

    result = sorted(months)
    logger.info("Liahona %d: found %d issues — months %s (%s)",
                year, len(result), result, lang)
    return result


def download_year(session: ChurchSession, year: int, lang: str,
                  *, dry_run: bool = False, include_conference: bool = False,
                  checkpoint: Checkpoint | None = None) -> DownloadStats:
    """Download all Liahona issues for a year."""
    total = DownloadStats()

    months = discover_issue_months(session, year, lang)
    for month in months:
        issue_stats = download_issue(
            session, year, month, lang,
            dry_run=dry_run,
            include_conference=include_conference,
            checkpoint=checkpoint,
        )
        total.pages += issue_stats.pages
        total.downloaded += issue_stats.downloaded
        total.skipped += issue_stats.skipped
        total.errors += issue_stats.errors
        total.footnotes_total += issue_stats.footnotes_total
        total.scripture_refs_total += issue_stats.scripture_refs_total

    return total


# ── CLI ──��────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Download Liahona magazine articles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Single issue:     %(prog)s --year 2024 --month 10
  Full year:        %(prog)s --year 2024
  Year range:       %(prog)s --year-from 2021 --year-to 2026
  Dry run:          %(prog)s --year 2024 --month 10 --dry-run
  With conference:  %(prog)s --year 2024 --include-conference
        """,
    )
    add_common_args(parser, include_resume=True)

    parser.add_argument("--year", type=int, help="Single year to download")
    parser.add_argument("--month", type=int, help="Specific month (1-12)")
    parser.add_argument("--year-from", type=int, help="Start year for range")
    parser.add_argument("--year-to", type=int, help="End year for range")
    parser.add_argument("--include-conference", action="store_true",
                        help="Include non-talk articles from conference issues")

    args = parser.parse_args()

    # Validate args
    if not args.year and not args.year_from:
        parser.error("Must specify --year or --year-from/--year-to")

    if args.month and not args.year:
        parser.error("--month requires --year")

    if args.month and not (1 <= args.month <= 12):
        parser.error("--month must be 1-12")

    # Determine year range
    if args.year and not args.year_from:
        years = [args.year]
    elif args.year_from:
        year_to = args.year_to or args.year_from
        years = list(range(args.year_from, year_to + 1))
    else:
        years = [args.year]

    languages = get_languages(args)
    session = ChurchSession(delay=args.delay)

    grand_total = DownloadStats()

    for lang in languages:
        logger.info("=" * 60)
        logger.info("Language: %s", lang)

        checkpoint = None
        if args.resume:
            checkpoint = Checkpoint("liahona", lang)
            checkpoint.load()
            logger.info("Resuming with %d already processed", len(checkpoint.processed))

        for year in years:
            if args.month:
                stats = download_issue(
                    session, year, args.month, lang,
                    dry_run=args.dry_run,
                    include_conference=args.include_conference,
                    checkpoint=checkpoint,
                )
            else:
                stats = download_year(
                    session, year, lang,
                    dry_run=args.dry_run,
                    include_conference=args.include_conference,
                    checkpoint=checkpoint,
                )

            stats.log_summary(f"Liahona {year} ({lang})")
            grand_total.pages += stats.pages
            grand_total.downloaded += stats.downloaded
            grand_total.skipped += stats.skipped
            grand_total.errors += stats.errors
            grand_total.footnotes_total += stats.footnotes_total
            grand_total.scripture_refs_total += stats.scripture_refs_total

        if checkpoint:
            checkpoint.save()

    logger.info("=" * 60)
    grand_total.log_summary("GRAND TOTAL")


if __name__ == "__main__":
    main()
