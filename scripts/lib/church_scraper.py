"""Shared infrastructure for downloading content from churchofjesuschrist.org.

Consolidates patterns common to all download/scrape scripts:
- Two access strategies: API v3 (prose) and HTML direct (verses/structured)
- TOC/index discovery
- HTML → text conversion (pandoc for prose, BS4 for verses)
- Footnote extraction and formatting (ALWAYS captured — they carry
  scripture cross-refs, historical context, and doctrinal commentary
  that are indispensable for KG relations and RAG enrichment)
- Rate-limited session management
- Checkpoint/resume for large scrapes
- Consistent .txt + .meta.json output
- Standard CLI arguments

Usage:
    from scripts.lib.church_scraper import (
        ChurchSession, ApiPage, fetch_api_page, fetch_html_page,
        discover_toc_api, discover_toc_html,
        html_to_structured_text, extract_verses,
        extract_footnotes_api, extract_footnotes_html, format_footnotes,
        write_corpus_file, Checkpoint, add_common_args, CORPUS_ROOT,
    )
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────

BASE_URL = "https://www.churchofjesuschrist.org"
API_URL = f"{BASE_URL}/study/api/v3/language-pages/type/content"
CORPUS_ROOT = Path(__file__).resolve().parent.parent.parent / "corpus"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

LANG_MAP = {"eng": "en", "spa": "es"}
DEFAULT_DELAY = 0.5
USER_AGENT = "Mozilla/5.0 (compatible; AlejandriaBot/1.0; scripture-study)"


# ═══════════════════════════════════════════════════════════════════════════
# Session management
# ═══════════════════════════════════════════════════════════════════════════

class ChurchSession:
    """Rate-limited requests session for churchofjesuschrist.org."""

    def __init__(self, delay: float = DEFAULT_DELAY):
        self.delay = delay
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": USER_AGENT})

        ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE", "")
        if ca_bundle:
            self._session.verify = ca_bundle

        self._last_request = 0.0

    def _rate_limit(self):
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request = time.time()

    def get(self, url: str, **kwargs) -> requests.Response:
        self._rate_limit()
        kwargs.setdefault("timeout", 30)
        resp = self._session.get(url, **kwargs)
        resp.raise_for_status()
        return resp

    def fetch_json(self, uri: str, lang: str) -> dict:
        """Fetch from the Church API v3. `uri` has NO /study prefix."""
        resp = self.get(API_URL, params={"lang": lang, "uri": uri})
        return resp.json()

    def fetch_html(self, url: str) -> BeautifulSoup:
        """Fetch a page and return parsed HTML."""
        resp = self.get(url)
        resp.encoding = "utf-8"
        return BeautifulSoup(resp.text, "html.parser")


# ═══════════════════════════════════════════════════════════════════════════
# API page data
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ApiPage:
    """Parsed result from a Church API v3 content fetch."""
    title: str
    body_html: str
    footnotes: dict  # raw structured footnotes from API
    meta: dict       # full meta block from API
    uri: str = ""
    lang: str = ""


def fetch_api_page(session: ChurchSession, uri: str, lang: str) -> Optional[ApiPage]:
    """Fetch a single page via the API v3 and return structured data.

    Args:
        uri: Content path WITHOUT /study prefix (e.g., /manual/jesus-the-christ/chapter-1)
        lang: "eng" or "spa"

    Returns ApiPage or None if content is empty/missing.
    """
    try:
        data = session.fetch_json(uri, lang)
    except requests.HTTPError as e:
        logger.warning("API fetch failed for %s (%s): %s", uri, lang, e)
        return None

    body = data.get("content", {}).get("body", "")
    if not body or len(body) < 200:
        return None

    return ApiPage(
        title=data.get("meta", {}).get("title", ""),
        body_html=body,
        footnotes=data.get("content", {}).get("footnotes", {}) or {},
        meta=data.get("meta", {}),
        uri=uri,
        lang=lang,
    )


# ═══════════════════════════════════════════════════════════════════════════
# TOC / index discovery
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TocEntry:
    """A single entry discovered from a table of contents."""
    uri: str     # API uri (no /study prefix)
    slug: str    # last path segment
    title: str   # human-readable title


def discover_toc_api(session: ChurchSession, parent_uri: str, lang: str,
                     link_contains: str, slug_filter: Optional[set] = None) -> list[TocEntry]:
    """Discover content pages from a TOC page via the API.

    Args:
        parent_uri: TOC page uri (e.g., /manual/jesus-the-christ)
        lang: "eng" or "spa"
        link_contains: substring that hrefs must contain (e.g., "jesus-the-christ")
        slug_filter: if provided, only include slugs in this set

    Returns list of TocEntry sorted by discovery order.
    """
    try:
        data = session.fetch_json(parent_uri, lang)
    except requests.HTTPError as e:
        logger.error("Cannot fetch TOC at %s: %s", parent_uri, e)
        return []

    body = data.get("content", {}).get("body", "")
    return _parse_toc_links(body, link_contains, slug_filter)


def discover_toc_html(session: ChurchSession, url: str,
                      link_contains: str, slug_filter: Optional[set] = None) -> list[TocEntry]:
    """Discover content pages from a TOC page via direct HTML fetch.

    Args:
        url: full URL of the TOC page
        link_contains: substring that hrefs must contain
        slug_filter: if provided, only include slugs in this set
    """
    try:
        soup = session.fetch_html(url)
    except requests.HTTPError as e:
        logger.error("Cannot fetch TOC at %s: %s", url, e)
        return []

    return _parse_toc_links(str(soup), link_contains, slug_filter)


def _parse_toc_links(html: str, link_contains: str,
                     slug_filter: Optional[set]) -> list[TocEntry]:
    """Parse <a> links from HTML to extract TOC entries."""
    soup = BeautifulSoup(html, "html.parser")
    entries = []
    seen = set()

    for a in soup.select(f'a[href*="{link_contains}"]'):
        href = a.get("href", "").split("?")[0]
        title = a.get_text(strip=True)

        if "/study/" in href:
            uri = href.split("/study")[1]
        elif href.startswith("/"):
            uri = href
        else:
            parsed = urlparse(href)
            uri = parsed.path
            if "/study/" in uri:
                uri = uri.split("/study")[1]

        slug = uri.rstrip("/").split("/")[-1]

        if not slug or slug in seen:
            continue
        if slug_filter is not None and slug not in slug_filter:
            continue

        seen.add(slug)
        entries.append(TocEntry(uri=uri, slug=slug, title=title))

    return entries


# ═══════════════════════════════════════════════════════════════════════════
# Footnotes — ALWAYS extract, they are essential content
#
# Footnotes carry:
# - Scripture cross-references (intertextuality relations for KG)
# - Historical/linguistic commentary (doctrinal context for RAG)
# - See-also links to related topics
# - Original language notes, variant readings
# These are NOT disposable metadata — they are content.
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Footnote:
    """A single footnote with its marker and content."""
    id: str           # e.g., "1", "note3_a"
    marker: str       # display marker: "1", "a", "1a"
    text: str         # plain text content (HTML stripped)
    references: list[str] = field(default_factory=list)  # scripture ref URIs


def extract_footnotes_api(raw: dict) -> list[Footnote]:
    """Extract footnotes from the API v3 `content.footnotes` structure.

    The API returns footnotes as a dict keyed by ID, each with:
    - marker: display label
    - text: HTML content
    - referenceUris: list of linked URIs
    """
    if not isinstance(raw, dict) or not raw:
        return []

    footnotes = []
    for key in sorted(raw.keys(), key=lambda k: (int(k) if k.isdigit() else 0, k)):
        note = raw[key]
        if not isinstance(note, dict):
            continue

        marker = note.get("marker", key)
        html_text = note.get("text", "")
        plain = BeautifulSoup(html_text, "html.parser").get_text(strip=True) if html_text else ""

        refs = []
        for uri in note.get("referenceUris", []):
            if isinstance(uri, str):
                refs.append(uri)

        if plain or refs:
            footnotes.append(Footnote(id=key, marker=marker, text=plain, references=refs))

    return footnotes


# Regex for HTML footnote IDs: note1_a, note1a, note12_c
_FOOTNOTE_ID_RE = re.compile(r"note\d+_?[a-z]$")


def extract_footnotes_html(soup: BeautifulSoup) -> list[Footnote]:
    """Extract footnotes from HTML page <li> elements in the footnote section.

    Handles both EN format (note1_a) and ES format (note1a, no underscore).
    """
    footnotes = []
    for li in soup.find_all("li", id=_FOOTNOTE_ID_RE):
        note_id = li.get("id", "")

        # Extract marker from <span class="marker"> or first text
        marker_el = li.find("span", class_="marker")
        marker = marker_el.get_text(strip=True) if marker_el else note_id

        # Extract scripture reference links
        refs = []
        for a in li.find_all("a", href=True):
            href = a["href"]
            if "/study/scriptures/" in href:
                ref_text = a.get_text(strip=True)
                if ref_text:
                    refs.append(ref_text)

        # Full text
        text = re.sub(r"\s+", " ", li.get_text()).strip()

        if text:
            footnotes.append(Footnote(id=note_id, marker=marker, text=text, references=refs))

    return footnotes


def format_footnotes_text(footnotes: list[Footnote], header: str = "Notas") -> str:
    """Format footnotes as a plain-text endnotes section appended to content.

    Returns empty string if no footnotes.
    """
    if not footnotes:
        return ""

    lines = [f"\n\n---\n{header}\n"]
    for fn in footnotes:
        line = f"  {fn.marker}. {fn.text}"
        lines.append(line)

    return "\n".join(lines)


def footnotes_to_meta(footnotes: list[Footnote]) -> dict:
    """Convert footnotes to metadata-friendly format.

    Returns dict with:
    - note_count: total count
    - scripture_refs: deduplicated list of scripture references found in notes
    - footnotes: list of {marker, text} for full preservation
    """
    if not footnotes:
        return {"note_count": 0}

    scripture_refs = []
    notes_list = []
    for fn in footnotes:
        notes_list.append({"marker": fn.marker, "text": fn.text})
        for ref in fn.references:
            if ref not in scripture_refs:
                scripture_refs.append(ref)

    result = {"note_count": len(footnotes), "footnotes": notes_list}
    if scripture_refs:
        result["scripture_refs"] = scripture_refs

    return result


# ═══════════════════════════════════════════════════════════════════════════
# HTML → text conversion
# ═══════════════════════════════════════════════════════════════════════════

# Elements to always remove before text extraction
_REMOVE_SELECTORS = (
    "img", "nav", "figure", "video", ".manifest",
    "p.reference", "p.short-reference",
    "sup.marker", ".study-note-ref",
)

_HEADING_MAP = {"h1": "#", "h2": "##", "h3": "###", "h4": "####"}


def html_to_structured_text(html: str, keep_headings: bool = True) -> str:
    """Convert HTML to structured plain text via pandoc.

    Best for prose content (manuals, books, talks). Preserves heading
    hierarchy with markdown-style markers.

    Args:
        html: raw HTML content
        keep_headings: if True, convert h1-h4 to # markers
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content elements
    for sel in _REMOVE_SELECTORS:
        for el in soup.select(sel):
            el.decompose()

    # Convert headings to markdown markers before pandoc
    if keep_headings:
        for tag_name, marker in _HEADING_MAP.items():
            for h in soup.find_all(tag_name):
                text = h.get_text(strip=True)
                h.replace_with(f"\n\n{marker} {text}\n\n")

    # Convert sidebars to marked blocks
    for aside in soup.find_all("aside"):
        inner = aside.decode_contents()
        aside.replace_with(f"\n\n[SIDEBAR]\n{inner}\n[/SIDEBAR]\n\n")

    # Pandoc conversion
    result = subprocess.run(
        ["pandoc", "-f", "html", "-t", "plain", "--wrap=none"],
        input=str(soup).encode("utf-8"),
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pandoc failed: {result.stderr.decode('utf-8', errors='replace')}")

    text = result.stdout.decode("utf-8").strip()
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text


def extract_verses(soup: BeautifulSoup) -> list[tuple[int, str]]:
    """Extract numbered verses from HTML (scripture pages).

    Returns list of (verse_number, verse_text) tuples.
    """
    verses = []
    for vel in soup.find_all("p", class_=lambda c: c and "verse" in str(c)):
        num = _extract_verse_number(vel)
        text = _clean_verse_text(vel)
        if num is not None and text:
            verses.append((num, text))
    return sorted(verses, key=lambda v: v[0])


def _extract_verse_number(el: Tag) -> Optional[int]:
    """Extract verse number from a verse element."""
    vn = el.find("span", class_="verse-number")
    if vn:
        try:
            return int(vn.get_text().strip())
        except ValueError:
            pass

    ref = el.get("data-eng-ref", "")
    if ":" in ref:
        try:
            return int(ref.split(":")[-1])
        except ValueError:
            pass

    pid = el.get("id", "")
    if pid.startswith("p"):
        try:
            return int(pid[1:])
        except ValueError:
            pass

    return None


def _clean_verse_text(el: Tag) -> str:
    """Extract clean text from a verse element, removing footnote markers."""
    for sup in el.find_all("sup", class_="marker"):
        sup.decompose()
    for vn in el.find_all("span", class_="verse-number"):
        vn.decompose()
    for btn in el.find_all("button"):
        btn.decompose()
    for svg in el.find_all("svg"):
        svg.decompose()
    for icon in el.find_all("span", class_=lambda c: c and "iconPointer" in str(c)):
        icon.decompose()

    text = re.sub(r"\s+", " ", el.get_text()).strip()
    return text


def extract_prose(soup: BeautifulSoup) -> str:
    """Extract prose text from non-verse HTML (introductions, declarations).

    Collects paragraphs from .body-block or <article>, preserving
    paragraph separation with double newlines.
    """
    body = soup.find("div", class_="body-block") or soup.find("article")
    if not body:
        return ""

    paragraphs = []
    for el in body.find_all(["p", "li", "h2", "h3", "h4"]):
        if el.find_parent("footer") or el.find_parent("nav"):
            continue

        for sup in el.find_all("sup", class_="marker"):
            sup.decompose()

        text = re.sub(r"\s+", " ", el.get_text()).strip()
        if text:
            classes = el.get("class", [])
            if isinstance(classes, list) and "signature" in classes:
                text = f"— {text}"
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


# ═══════════════════════════════════════════════════════════════════════════
# Scripture reference extraction
# ═══════════════════════════════════════════════════════════════════════════

# Broad pattern matching common scripture citation forms
_SCRIPTURE_REF_PATTERN = re.compile(
    r"(?:\d\s+)?(?:(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|"
    r"Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|"
    r"Song of Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|"
    r"Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|"
    r"Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|"
    r"Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|"
    r"James|Peter|Jude|Revelation|"
    r"Nephi|Jacob|Enos|Jarom|Omni|Mosiah|Alma|Helaman|Mormon|Ether|Moroni|"
    r"D&C|Doctrine and Covenants|Moses|Abraham|JS[—-]H|JS[—-]M|"
    r"Génesis|Éxodo|Salmos?|Isaías|Mateo|Marcos|Lucas|Juan|Hechos|Romanos|"
    r"Nefi|DyC|Doctrina y Convenios|Moisés|Abrahán)"
    r"\s+\d+(?::\d+(?:[–-]\d+)?)?)"
)


def extract_scripture_refs_from_text(text: str) -> list[str]:
    """Extract scripture references from plain text using pattern matching."""
    refs = []
    for m in _SCRIPTURE_REF_PATTERN.finditer(text):
        ref = m.group(0).strip()
        if ref and ref not in refs:
            refs.append(ref)
    return refs


def extract_scripture_refs_from_html(soup: BeautifulSoup) -> list[str]:
    """Extract scripture references from <a> links pointing to /study/scriptures/."""
    refs = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/study/scriptures/" in href:
            text = a.get_text(strip=True)
            if text and text not in refs:
                refs.append(text)
    return refs


# ═══════════════════════════════════════════════════════════════════════════
# Corpus output
# ═══════════════════════════════════════════════════════════════════════════

def write_corpus_file(output_dir: Path, filename: str, text: str, meta: dict):
    """Write a .txt + .meta.json pair to the corpus.

    Args:
        output_dir: target directory (created if needed)
        filename: base name without extension
        text: plain text content
        meta: metadata dict
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    txt_path = output_dir / f"{filename}.txt"
    meta_path = output_dir / f"{filename}.meta.json"

    txt_path.write_text(text + "\n", encoding="utf-8")
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return txt_path


def build_source_url(uri: str, lang: str) -> str:
    """Build the full public URL from an API uri."""
    return f"{BASE_URL}/study{uri}?lang={lang}"


# ═══════════════════════════════════════════════════════════════════════════
# Checkpoint / resume
# ═══════════════════════════════════════════════════════════════════════════

class Checkpoint:
    """File-based checkpoint for resumable scraping."""

    def __init__(self, name: str, lang: str):
        self.path = PROJECT_ROOT / "data" / f"scrape_{name}_{lang}_checkpoint.txt"
        self.processed: set[str] = set()

    def load(self) -> set[str]:
        if self.path.exists():
            self.processed = set(self.path.read_text(encoding="utf-8").strip().split("\n"))
            self.processed.discard("")
        return self.processed

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("\n".join(sorted(self.processed)) + "\n", encoding="utf-8")

    def mark(self, key: str):
        self.processed.add(key)

    def is_done(self, key: str) -> bool:
        return key in self.processed

    def save_if_needed(self, every: int = 50) -> bool:
        """Save checkpoint if count is a multiple of `every`."""
        if len(self.processed) % every == 0:
            self.save()
            return True
        return False


# ═══════════════════════════════════════════════════════════════════════════
# CLI helpers
# ═══════════════════════════════════════════════════════════════════════════

def add_common_args(parser, include_resume: bool = False, include_limit: bool = False):
    """Add standard CLI arguments for church download scripts.

    Always adds: --lang, --dry-run, --delay
    Optionally: --resume, --limit, --list-only
    """
    parser.add_argument("--lang", help="Language: eng or spa (default: both)")
    parser.add_argument("--dry-run", action="store_true",
                        help="List pages without downloading")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY,
                        help=f"Delay between requests in seconds (default: {DEFAULT_DELAY})")

    if include_resume:
        parser.add_argument("--resume", action="store_true",
                            help="Resume from checkpoint")
    if include_limit:
        parser.add_argument("--limit", type=int, default=0,
                            help="Limit number of pages to download (0=all)")
        parser.add_argument("--list-only", action="store_true",
                            help="Only list entries, don't download content")


def get_languages(args) -> list[str]:
    """Return language list from parsed args."""
    if hasattr(args, "lang") and args.lang:
        return [args.lang]
    return ["eng", "spa"]


# ═══════════════════════════════════════════════════════════════════════════
# Stats tracking
# ═══════════════════════════════════════════════════════════════════════════

class DownloadStats:
    """Simple counter for download progress."""

    def __init__(self):
        self.pages = 0
        self.downloaded = 0
        self.skipped = 0
        self.errors = 0
        self.footnotes_total = 0
        self.scripture_refs_total = 0

    def to_dict(self) -> dict:
        return {
            "pages": self.pages,
            "downloaded": self.downloaded,
            "skipped": self.skipped,
            "errors": self.errors,
            "footnotes_total": self.footnotes_total,
            "scripture_refs_total": self.scripture_refs_total,
        }

    def log_summary(self, label: str = ""):
        prefix = f"{label}: " if label else ""
        logger.info(
            "%s%d pages, %d downloaded, %d skipped, %d errors, %d footnotes, %d scripture refs",
            prefix, self.pages, self.downloaded, self.skipped, self.errors,
            self.footnotes_total, self.scripture_refs_total,
        )
