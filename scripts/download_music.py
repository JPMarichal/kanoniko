#!/usr/bin/env python3
"""Download music collections from churchofjesuschrist.org.

Collections:
  hymns               Classic Hymnal (333 hymns, EN+ES)
  hymns-home-church   New Hymnal for Home and Church (72 hymns, EN+ES)
  childrens-songbook  Children's Songbook (148 songs, EN+ES)
  youth-music         Youth Music albums (EN+ES)
  hymn-helps          Hymn study aids (About the Hymns EN only; usage guides EN+ES)

Metadata captured per hymn/song:
  - Lyrics with stanza structure
  - hymn_number: position in collection
  - author: text/lyrics author name and year
  - composer: music composer name and year
  - tune: tune name (hymns)
  - occasion: liturgical occasion (Worship, Sacrament, Prayer, etc.)
  - audio_urls: all media source links (.mp3, .aiff, .ogg)
  - scripture_refs: linked scripture citations
  - footnotes: always captured (full structured form)

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_music.py
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_music.py --collection hymns
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_music.py --collection hymns-home-church childrens-songbook
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_music.py --lang eng --dry-run

Requires: pandoc, requests, beautifulsoup4
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.church_scraper import (
    ChurchSession, TocEntry, ApiPage,
    fetch_api_page, discover_toc_api, discover_toc_html,
    html_to_structured_text, extract_footnotes_api,
    format_footnotes_text, footnotes_to_meta,
    write_corpus_file, build_source_url,
    add_common_args, get_languages,
    DownloadStats, CORPUS_ROOT, BASE_URL,
)
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

LANG_MAP = {"eng": "en", "spa": "es"}

# ── Youth Music: known album slugs (hub page 404s on API) ─────────────────
# Albums are individual manual entries under /study/manual/ or /study/music/
# Discovered via HTML hub at /music/youth-music/
_YOUTH_ALBUMS = [
    "/music/youth-music/hope-of-israel",
    "/music/youth-music/welcome-home",
    "/music/youth-music/raise-a-voice",
    "/music/youth-music/the-christ-child",
    "/music/youth-music/come-let-us-sing",
    "/music/youth-music/gather-israel",
]

# ── About the Hymns: EN-only — 72 entries parallel to new hymnal ─────────
_HYMN_HELPS_ABOUT_URI = "/manual/sacred-music-gospel-study-resource-pilot"
_HYMN_HELPS_ABOUT_LANG = "eng"  # EN only — no ES version

# ── Usage guide collections (bilingual) ──────────────────────────────────
_USAGE_GUIDES = [
    {
        "name": "using-the-hymnbook",
        "uri": "/manual/using-the-hymnbook",
        "link_contains": "using-the-hymnbook",
        "bilingual": True,
    },
    {
        "name": "using-the-songbook",
        "uri": "/manual/using-the-songbook",
        "link_contains": "using-the-songbook",
        "bilingual": True,
    },
    {
        "name": "using-hymns-for-home-and-church",
        "uri": "/music/using-hymns-for-home-and-church",
        "link_contains": "using-hymns-for-home-and-church",
        "bilingual": True,
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# Hymn attribute extraction
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class HymnAttributes:
    """Rich metadata extracted from a hymn/song page."""
    hymn_number: Optional[int] = None
    author: Optional[str] = None          # Text/lyrics author + year, e.g. "William W. Phelps, 1844"
    composer: Optional[str] = None        # Music composer + year
    tune: Optional[str] = None            # Tune name
    occasion: Optional[str] = None        # Liturgical/topical occasion
    first_line: Optional[str] = None      # Opening line of lyrics (traditional identifier)
    audio_urls: list[str] = field(default_factory=list)


def _extract_hymn_attributes(html: str, hymn_number: Optional[int] = None) -> HymnAttributes:
    """Parse HTML of a hymn/song page to extract rich structured metadata.

    Extracts:
    - Author (text) and composer (music) with year from attribution block
    - Tune name from tune/meter info
    - Occasion from topic/occasion tags
    - First line of lyrics
    - All audio source URLs (mp3, aiff, ogg, wav)
    """
    soup = BeautifulSoup(html, "html.parser")
    attrs = HymnAttributes(hymn_number=hymn_number)

    # ── Hymn number ──
    if hymn_number is None:
        # Try to extract from title or header spans
        for el in soup.find_all(["h1", "h2", "h3", "span"], limit=10):
            text = el.get_text(strip=True)
            m = re.match(r"^(\d+)\.", text)
            if m:
                try:
                    attrs.hymn_number = int(m.group(1))
                except ValueError:
                    pass
                break

    # ── Attribution block: "Text: Author Name, year" / "Music: Composer, year" ──
    # Typical HTML: <p class="attribution"> or <div class="attribution">
    # or plain <p> containing "Text:" / "Music:" / "Words:" / "Tune:" patterns
    for el in soup.find_all(["p", "div", "li", "span"]):
        text = el.get_text(" ", strip=True)

        if not attrs.author:
            m = re.match(
                r"(?:Text|Words?|Letra|Palabras?):\s*(.+?)(?:\s*\||$)",
                text, re.IGNORECASE
            )
            if m:
                attrs.author = m.group(1).strip(" ,;")

        if not attrs.composer:
            m = re.match(
                r"(?:Music|Música|Composer|Compositor):\s*(.+?)(?:\s*\||$)",
                text, re.IGNORECASE
            )
            if m:
                attrs.composer = m.group(1).strip(" ,;")

        if not attrs.tune:
            m = re.match(
                r"(?:Tune|Tonada|Melodía):\s*(.+?)(?:\s*\||$)",
                text, re.IGNORECASE
            )
            if m:
                attrs.tune = m.group(1).strip(" ,;")

        if not attrs.occasion:
            m = re.match(
                r"(?:Occasion|Ocasión|Topic|Tema):\s*(.+?)(?:\s*\||$)",
                text, re.IGNORECASE
            )
            if m:
                attrs.occasion = m.group(1).strip(" ,;")

    # ── Compact inline attribution: "Text and music: Name | Tune: NAME" ──
    # Church pages often put everything in one line separated by |
    for el in soup.select(".attribution, [class*='attribution'], [class*='hymn-info']"):
        line = el.get_text(" | ", strip=True)
        if not attrs.author:
            m = re.search(
                r"(?:Text|Words?|Letra|Palabras?)(?:\s+and\s+music)?:\s*([^|]+)",
                line, re.IGNORECASE
            )
            if m:
                attrs.author = m.group(1).strip(" ,;")
        if not attrs.composer:
            m = re.search(
                r"(?:Music|Música):\s*([^|]+)", line, re.IGNORECASE
            )
            if m:
                attrs.composer = m.group(1).strip(" ,;")
        if "text and music" in line.lower() or "texto y música" in line.lower():
            combined = re.search(
                r"(?:Text and music|Texto y música):\s*([^|]+)",
                line, re.IGNORECASE
            )
            if combined and not attrs.author:
                attrs.author = combined.group(1).strip(" ,;")
            if combined and not attrs.composer:
                attrs.composer = combined.group(1).strip(" ,;")

    # ── Audio URLs ──
    audio_exts = {".mp3", ".aiff", ".aif", ".ogg", ".wav", ".m4a"}
    for tag in soup.find_all(["audio", "source", "a"], href=True):
        src = tag.get("src") or tag.get("href") or ""
        if any(src.lower().endswith(ext) for ext in audio_exts):
            if src.startswith("/"):
                src = f"{BASE_URL}{src}"
            if src not in attrs.audio_urls:
                attrs.audio_urls.append(src)
    # Also check <source> tags inside <audio>
    for audio_el in soup.find_all("audio"):
        for src_el in audio_el.find_all("source"):
            src = src_el.get("src", "")
            if src:
                if src.startswith("/"):
                    src = f"{BASE_URL}{src}"
                if src not in attrs.audio_urls:
                    attrs.audio_urls.append(src)

    # ── First line of lyrics ──
    # Look for stanza/verse containers
    first_stanza = (
        soup.find(class_=re.compile(r"stanza|verse|lyric", re.I)) or
        soup.find("p", class_=re.compile(r"stanza|lyric", re.I))
    )
    if first_stanza:
        lines = [l.strip() for l in first_stanza.get_text("\n").split("\n") if l.strip()]
        if lines:
            attrs.first_line = lines[0][:120]

    return attrs


def _attrs_to_meta_fields(attrs: HymnAttributes) -> dict:
    """Convert HymnAttributes to meta.json-compatible dict (omits None/empty)."""
    d = {}
    if attrs.hymn_number is not None:
        d["hymn_number"] = attrs.hymn_number
    if attrs.author:
        d["author"] = attrs.author
    if attrs.composer:
        d["composer"] = attrs.composer
    if attrs.tune:
        d["tune"] = attrs.tune
    if attrs.occasion:
        d["occasion"] = attrs.occasion
    if attrs.first_line:
        d["first_line"] = attrs.first_line
    if attrs.audio_urls:
        d["audio_urls"] = attrs.audio_urls
    return d


# ═══════════════════════════════════════════════════════════════════════════
# Hymn number counter (ordinal position in TOC)
# ═══════════════════════════════════════════════════════════════════════════

def _assign_hymn_numbers(entries: list[TocEntry]) -> dict[str, int]:
    """Map entry slug to its 1-based position in the TOC."""
    return {entry.slug: i for i, entry in enumerate(entries, 1)}


# ═══════════════════════════════════════════════════════════════════════════
# Core download function
# ═══════════════════════════════════════════════════════════════════════════

def download_hymn_collection(
    session: ChurchSession,
    collection_name: str,
    manual_uri: str,
    link_contains: str,
    lang: str,
    output_dir: Path,
    authority: int = 65,
    tags: Optional[list[str]] = None,
    dry_run: bool = False,
    limit: int = 0,
) -> DownloadStats:
    """Download all pages from a hymn/song collection.

    Captures lyrics text + rich metadata (author, composer, tune, occasion,
    audio URLs, scripture refs, footnotes).
    """
    stats = DownloadStats()
    corpus_lang = LANG_MAP.get(lang, lang)

    logger.info("=== %s (%s) → %s ===", collection_name, lang, output_dir)

    # Discover TOC
    entries = discover_toc_api(session, manual_uri, lang, link_contains=link_contains)
    if not entries:
        logger.warning("  TOC discovery returned 0 entries for %s (%s)", collection_name, lang)
        return stats

    if limit:
        entries = entries[:limit]

    hymn_numbers = _assign_hymn_numbers(entries)
    stats.pages = len(entries)
    logger.info("  Discovered %d entries", len(entries))

    if dry_run:
        for entry in entries:
            logger.info("  [DRY RUN] %s", entry.title or entry.slug)
        stats.downloaded = len(entries)
        return stats

    output_dir.mkdir(parents=True, exist_ok=True)

    for i, entry in enumerate(entries, 1):
        slug = entry.slug
        # Sanitize slug for filename: remove -release-N suffixes etc.
        filename = re.sub(r"-release-\d+$", "", slug)
        txt_path = output_dir / f"{filename}.txt"

        if txt_path.exists():
            logger.debug("  [%d/%d] skip (exists): %s", i, len(entries), slug)
            stats.skipped += 1
            continue

        page = fetch_api_page(session, entry.uri, lang)
        if page is None:
            logger.warning("  [%d/%d] no content: %s", i, len(entries), slug)
            stats.errors += 1
            continue

        # Convert HTML to structured text (lyrics + prose)
        try:
            text = html_to_structured_text(page.body_html)
        except RuntimeError as e:
            logger.warning("  [%d/%d] pandoc failed for %s: %s", i, len(entries), slug, e)
            stats.errors += 1
            continue

        if not text.strip():
            logger.warning("  [%d/%d] empty text: %s", i, len(entries), slug)
            stats.errors += 1
            continue

        # Extract footnotes
        footnotes = extract_footnotes_api(page.footnotes)
        if footnotes:
            text += format_footnotes_text(footnotes, header="Notas")
        footnotes_meta = footnotes_to_meta(footnotes)
        stats.footnotes_total += footnotes_meta.get("note_count", 0)

        # Extract scripture refs from HTML links
        soup = BeautifulSoup(page.body_html, "html.parser")
        scripture_refs = []
        for a in soup.find_all("a", href=True):
            if "/study/scriptures/" in a["href"]:
                ref = a.get_text(strip=True)
                if ref and ref not in scripture_refs:
                    scripture_refs.append(ref)
        stats.scripture_refs_total += len(scripture_refs)

        # Extract rich hymn attributes
        hymn_attrs = _extract_hymn_attributes(
            page.body_html,
            hymn_number=hymn_numbers.get(slug)
        )

        # Build meta
        meta: dict = {
            "title":        page.title or entry.title,
            "collection":   collection_name,
            "category":     "music",
            "subcategory":  collection_name,
            "lang":         corpus_lang,
            "source_url":   build_source_url(entry.uri, lang),
            "authority":    authority,
            "official":     True,
        }
        if tags:
            meta["tags"] = tags
        meta.update(_attrs_to_meta_fields(hymn_attrs))
        meta.update(footnotes_meta)
        if scripture_refs:
            existing = meta.get("scripture_refs", [])
            meta["scripture_refs"] = list({r: None for r in (existing + scripture_refs)})

        write_corpus_file(output_dir, filename, text, meta)
        stats.downloaded += 1

        logger.info(
            "  [%d/%d] %s → %s (%d chars%s%s%s)",
            i, len(entries), entry.title[:50] if entry.title else slug, filename,
            len(text),
            f", author: {hymn_attrs.author[:30]}" if hymn_attrs.author else "",
            f", {len(hymn_attrs.audio_urls)} audio" if hymn_attrs.audio_urls else "",
            f", {len(scripture_refs)} refs" if scripture_refs else "",
        )

    stats.log_summary(f"{collection_name}/{lang}")
    return stats


def download_prose_collection(
    session: ChurchSession,
    collection_name: str,
    manual_uri: str,
    link_contains: str,
    lang: str,
    output_dir: Path,
    authority: int = 65,
    tags: Optional[list[str]] = None,
    dry_run: bool = False,
) -> DownloadStats:
    """Download a prose guide (using-the-hymnbook etc.) — no hymn attribute extraction."""
    stats = DownloadStats()
    corpus_lang = LANG_MAP.get(lang, lang)

    logger.info("=== %s (%s) ===", collection_name, lang)

    entries = discover_toc_api(session, manual_uri, lang, link_contains=link_contains)
    if not entries:
        logger.warning("  TOC returned 0 for %s (%s)", collection_name, lang)
        return stats

    stats.pages = len(entries)
    logger.info("  Discovered %d entries", len(entries))

    if dry_run:
        for entry in entries:
            logger.info("  [DRY RUN] %s", entry.title or entry.slug)
        stats.downloaded = len(entries)
        return stats

    output_dir.mkdir(parents=True, exist_ok=True)

    for i, entry in enumerate(entries, 1):
        filename = entry.slug
        txt_path = output_dir / f"{filename}.txt"

        if txt_path.exists():
            stats.skipped += 1
            continue

        page = fetch_api_page(session, entry.uri, lang)
        if page is None:
            stats.errors += 1
            continue

        try:
            text = html_to_structured_text(page.body_html)
        except RuntimeError as e:
            logger.warning("  pandoc failed for %s: %s", entry.slug, e)
            stats.errors += 1
            continue

        footnotes = extract_footnotes_api(page.footnotes)
        if footnotes:
            text += format_footnotes_text(footnotes, header="Notas")
        footnotes_meta = footnotes_to_meta(footnotes)

        soup = BeautifulSoup(page.body_html, "html.parser")
        scripture_refs = []
        for a in soup.find_all("a", href=True):
            if "/study/scriptures/" in a["href"]:
                ref = a.get_text(strip=True)
                if ref and ref not in scripture_refs:
                    scripture_refs.append(ref)

        meta: dict = {
            "title":        page.title or entry.title,
            "collection":   collection_name,
            "category":     "music",
            "subcategory":  collection_name,
            "lang":         corpus_lang,
            "source_url":   build_source_url(entry.uri, lang),
            "authority":    authority,
            "official":     True,
        }
        if tags:
            meta["tags"] = tags
        meta.update(footnotes_meta)
        if scripture_refs:
            meta["scripture_refs"] = scripture_refs

        write_corpus_file(output_dir, filename, text, meta)
        stats.downloaded += 1
        logger.info("  [%d/%d] %s → %s", i, len(entries), (page.title or entry.slug)[:60], filename)

    stats.log_summary(f"{collection_name}/{lang}")
    return stats


# ═══════════════════════════════════════════════════════════════════════════
# Youth music: album discovery from HTML hub
# ═══════════════════════════════════════════════════════════════════════════

def discover_youth_albums(session: ChurchSession) -> list[str]:
    """Discover youth music album URIs from the hub page HTML.

    Falls back to _YOUTH_ALBUMS if hub page fails.
    """
    hub_url = f"{BASE_URL}/music/youth-music"
    try:
        soup = session.fetch_html(hub_url)
        albums = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/music/youth-music/" in href and href != hub_url:
                # Extract path
                parsed = href.split("?")[0]
                if "/study/" in parsed:
                    uri = parsed.split("/study")[1]
                else:
                    uri = parsed if parsed.startswith("/") else f"/{parsed}"
                # Strip domain if present
                if "churchofjesuschrist.org" in uri:
                    uri = uri.split("churchofjesuschrist.org")[1]
                slug = uri.rstrip("/").split("/")[-1]
                if slug and uri not in albums and slug != "youth-music":
                    albums.append(uri)
        if albums:
            logger.info("Youth albums discovered from hub: %d", len(albums))
            return albums
    except Exception as e:
        logger.warning("Hub discovery failed: %s — using known album list", e)

    return _YOUTH_ALBUMS


def download_youth_music(
    session: ChurchSession,
    lang: str,
    output_root: Path,
    dry_run: bool = False,
) -> DownloadStats:
    """Download all youth music albums."""
    total_stats = DownloadStats()
    corpus_lang = LANG_MAP.get(lang, lang)

    album_uris = discover_youth_albums(session)
    logger.info("Youth music: %d albums, lang=%s", len(album_uris), lang)

    for album_uri in album_uris:
        album_slug = album_uri.rstrip("/").split("/")[-1]
        output_dir = output_root / corpus_lang / "music" / "youth-music" / album_slug

        stats = download_hymn_collection(
            session=session,
            collection_name=f"youth-music/{album_slug}",
            manual_uri=album_uri,
            link_contains=album_slug,
            lang=lang,
            output_dir=output_dir,
            authority=65,
            tags=["youth-music", "music", album_slug],
            dry_run=dry_run,
        )
        total_stats.pages += stats.pages
        total_stats.downloaded += stats.downloaded
        total_stats.skipped += stats.skipped
        total_stats.errors += stats.errors
        total_stats.footnotes_total += stats.footnotes_total
        total_stats.scripture_refs_total += stats.scripture_refs_total

    total_stats.log_summary(f"youth-music/{lang}")
    return total_stats


# ═══════════════════════════════════════════════════════════════════════════
# Collection registry
# ═══════════════════════════════════════════════════════════════════════════

ALL_COLLECTIONS = [
    "hymns",
    "hymns-home-church",
    "childrens-songbook",
    "youth-music",
    "hymn-helps",
]


def run_collection(
    session: ChurchSession,
    collection: str,
    langs: list[str],
    corpus_root: Path,
    dry_run: bool = False,
    limit: int = 0,
) -> DownloadStats:
    """Dispatch a collection download for one or more languages."""
    total = DownloadStats()

    def _add(s: DownloadStats):
        total.pages += s.pages
        total.downloaded += s.downloaded
        total.skipped += s.skipped
        total.errors += s.errors
        total.footnotes_total += s.footnotes_total
        total.scripture_refs_total += s.scripture_refs_total

    if collection == "hymns":
        for lang in langs:
            corpus_lang = LANG_MAP.get(lang, lang)
            _add(download_hymn_collection(
                session=session,
                collection_name="hymns",
                manual_uri="/manual/hymns",
                link_contains="hymns/",
                lang=lang,
                output_dir=corpus_root / corpus_lang / "music" / "hymns",
                authority=65,
                tags=["hymns", "worship", "music"],
                dry_run=dry_run,
                limit=limit,
            ))

    elif collection == "hymns-home-church":
        for lang in langs:
            corpus_lang = LANG_MAP.get(lang, lang)
            _add(download_hymn_collection(
                session=session,
                collection_name="hymns-for-home-and-church",
                manual_uri="/music/hymns-for-home-and-church",
                link_contains="hymns-for-home-and-church/",
                lang=lang,
                output_dir=corpus_root / corpus_lang / "music" / "hymns-for-home-and-church",
                authority=65,
                tags=["hymns", "new-hymnal", "worship", "music"],
                dry_run=dry_run,
                limit=limit,
            ))

    elif collection == "childrens-songbook":
        for lang in langs:
            corpus_lang = LANG_MAP.get(lang, lang)
            _add(download_hymn_collection(
                session=session,
                collection_name="childrens-songbook",
                manual_uri="/manual/childrens-songbook",
                link_contains="childrens-songbook/",
                lang=lang,
                output_dir=corpus_root / corpus_lang / "music" / "childrens-songbook",
                authority=65,
                tags=["childrens-songbook", "primary", "music"],
                dry_run=dry_run,
                limit=limit,
            ))

    elif collection == "youth-music":
        for lang in langs:
            _add(download_youth_music(session, lang, corpus_root, dry_run=dry_run))

    elif collection == "hymn-helps":
        # "About the Hymns" — EN only
        eng_langs = [l for l in langs if l == "eng"]
        if eng_langs:
            corpus_lang = LANG_MAP.get("eng", "en")
            _add(download_hymn_collection(
                session=session,
                collection_name="about-the-hymns",
                manual_uri=_HYMN_HELPS_ABOUT_URI,
                link_contains="sacred-music-gospel-study-resource-pilot",
                lang="eng",
                output_dir=corpus_root / corpus_lang / "music" / "hymn-helps" / "about-the-hymns",
                authority=65,
                tags=["hymn-helps", "music-history", "hymn-doctrine"],
                dry_run=dry_run,
            ))
        # Usage guides — bilingual
        for guide in _USAGE_GUIDES:
            for lang in langs:
                corpus_lang = LANG_MAP.get(lang, lang)
                _add(download_prose_collection(
                    session=session,
                    collection_name=guide["name"],
                    manual_uri=guide["uri"],
                    link_contains=guide["link_contains"],
                    lang=lang,
                    output_dir=corpus_root / corpus_lang / "music" / "hymn-helps" / guide["name"],
                    authority=65,
                    tags=["hymn-helps", "music-guidance"],
                    dry_run=dry_run,
                ))

    else:
        logger.error("Unknown collection: %s", collection)

    return total


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Download music collections from churchofjesuschrist.org",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join([
            "Collections:",
            "  hymns               Classic Hymnal (333 hymns, EN+ES)",
            "  hymns-home-church   New Hymnal for Home and Church (72 hymns, EN+ES)",
            "  childrens-songbook  Children's Songbook (148 songs, EN+ES)",
            "  youth-music         Youth Music albums (EN+ES)",
            "  hymn-helps          Hymn study aids (About: EN only; usage guides: EN+ES)",
            "  all                 All collections (default)",
        ]),
    )
    parser.add_argument(
        "--collection", nargs="+",
        metavar="COLLECTION",
        help="Collection(s) to download. Default: all",
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Limit entries per collection (0=all; useful for testing)",
    )
    add_common_args(parser)
    args = parser.parse_args()

    langs = get_languages(args)
    collections = args.collection or ["all"]
    if "all" in collections:
        collections = ALL_COLLECTIONS

    # Validate
    unknown = [c for c in collections if c not in ALL_COLLECTIONS]
    if unknown:
        parser.error(f"Unknown collections: {unknown}. Choose from: {ALL_COLLECTIONS}")

    session = ChurchSession(delay=args.delay)

    grand_total = DownloadStats()
    for collection in collections:
        logger.info("▶ Collection: %s | langs: %s", collection, langs)
        stats = run_collection(
            session=session,
            collection=collection,
            langs=langs,
            corpus_root=CORPUS_ROOT,
            dry_run=args.dry_run,
            limit=args.limit,
        )
        grand_total.pages += stats.pages
        grand_total.downloaded += stats.downloaded
        grand_total.skipped += stats.skipped
        grand_total.errors += stats.errors
        grand_total.footnotes_total += stats.footnotes_total
        grand_total.scripture_refs_total += stats.scripture_refs_total

    logger.info(
        "TOTAL: %d pages, %d downloaded, %d skipped, %d errors, %d footnotes, %d scripture refs",
        grand_total.pages, grand_total.downloaded, grand_total.skipped,
        grand_total.errors, grand_total.footnotes_total, grand_total.scripture_refs_total,
    )


if __name__ == "__main__":
    main()
