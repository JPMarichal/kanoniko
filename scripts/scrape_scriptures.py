"""
P2 Phase 2 — Scrape scripture verses from churchofjesuschrist.org.

Downloads all 5 standard works from the official Church site for a given language,
extracts verse text, and writes corpus files in the standard format: "N Verse text.\\n"

Also collects metadata (chapter summary, footnotes, cross-references) and saves it
alongside the verse files for future Phase 3 use.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_scriptures.py --lang eng
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/scrape_scriptures.py --lang spa
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup, Tag

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STRUCTURE_DIR = PROJECT_ROOT / "data" / "scripture_structure"
CORPUS_DIR = PROJECT_ROOT / "corpus"

BASE_URL = "https://www.churchofjesuschrist.org"

# Delay between requests (seconds) — be polite
REQUEST_DELAY = 0.5

# ── Site URL slugs for each book ────────────────────────────────────────────
# Maps: (volume_slug, corpus_book_slug) → (site_volume, site_book_slug)
# Site uses different abbreviations than our corpus slugs.

SITE_VOLUME_MAP = {
    "ot": "ot",
    "nt": "nt",
    "bom": "bofm",
    "dc": "dc-testament",
    "pgp": "pgp",
}

SITE_BOOK_MAP = {
    # OT
    ("ot", "genesis"): "gen",
    ("ot", "exodus"): "ex",
    ("ot", "leviticus"): "lev",
    ("ot", "numbers"): "num",
    ("ot", "deuteronomy"): "deut",
    ("ot", "joshua"): "josh",
    ("ot", "judges"): "judg",
    ("ot", "ruth"): "ruth",
    ("ot", "1-samuel"): "1-sam",
    ("ot", "2-samuel"): "2-sam",
    ("ot", "1-kings"): "1-kgs",
    ("ot", "2-kings"): "2-kgs",
    ("ot", "1-chronicles"): "1-chr",
    ("ot", "2-chronicles"): "2-chr",
    ("ot", "ezra"): "ezra",
    ("ot", "nehemiah"): "neh",
    ("ot", "esther"): "esth",
    ("ot", "job"): "job",
    ("ot", "psalms"): "ps",
    ("ot", "proverbs"): "prov",
    ("ot", "ecclesiastes"): "eccl",
    ("ot", "song-of-solomon"): "song",
    ("ot", "isaiah"): "isa",
    ("ot", "jeremiah"): "jer",
    ("ot", "lamentations"): "lam",
    ("ot", "ezekiel"): "ezek",
    ("ot", "daniel"): "dan",
    ("ot", "hosea"): "hosea",
    ("ot", "joel"): "joel",
    ("ot", "amos"): "amos",
    ("ot", "obadiah"): "obad",
    ("ot", "jonah"): "jonah",
    ("ot", "micah"): "micah",
    ("ot", "nahum"): "nahum",
    ("ot", "habakkuk"): "hab",
    ("ot", "zephaniah"): "zeph",
    ("ot", "haggai"): "hag",
    ("ot", "zechariah"): "zech",
    ("ot", "malachi"): "mal",
    # NT
    ("nt", "matthew"): "matt",
    ("nt", "mark"): "mark",
    ("nt", "luke"): "luke",
    ("nt", "john"): "john",
    ("nt", "acts"): "acts",
    ("nt", "romans"): "rom",
    ("nt", "1-corinthians"): "1-cor",
    ("nt", "2-corinthians"): "2-cor",
    ("nt", "galatians"): "gal",
    ("nt", "ephesians"): "eph",
    ("nt", "philippians"): "philip",
    ("nt", "colossians"): "col",
    ("nt", "1-thessalonians"): "1-thes",
    ("nt", "2-thessalonians"): "2-thes",
    ("nt", "1-timothy"): "1-tim",
    ("nt", "2-timothy"): "2-tim",
    ("nt", "titus"): "titus",
    ("nt", "philemon"): "philem",
    ("nt", "hebrews"): "heb",
    ("nt", "james"): "james",
    ("nt", "1-peter"): "1-pet",
    ("nt", "2-peter"): "2-pet",
    ("nt", "1-john"): "1-jn",
    ("nt", "2-john"): "2-jn",
    ("nt", "3-john"): "3-jn",
    ("nt", "jude"): "jude",
    ("nt", "revelation"): "rev",
    # BoM
    ("bom", "1-nephi"): "1-ne",
    ("bom", "2-nephi"): "2-ne",
    ("bom", "jacob"): "jacob",
    ("bom", "enos"): "enos",
    ("bom", "jarom"): "jarom",
    ("bom", "omni"): "omni",
    ("bom", "words-of-mormon"): "w-of-m",
    ("bom", "mosiah"): "mosiah",
    ("bom", "alma"): "alma",
    ("bom", "helaman"): "hel",
    ("bom", "3-nephi"): "3-ne",
    ("bom", "4-nephi"): "4-ne",
    ("bom", "mormon"): "morm",
    ("bom", "ether"): "ether",
    ("bom", "moroni"): "moro",
    # D&C
    ("dc", "sections"): "dc",
    ("dc", "official-declarations"): "od",
    # PGP
    ("pgp", "moses"): "moses",
    ("pgp", "abraham"): "abr",
    ("pgp", "js-matthew"): "js-m",
    ("pgp", "js-history"): "js-h",
    ("pgp", "articles-of-faith"): "a-of-f",
}

# ES corpus uses Spanish slugs; EN uses English slugs
# Import from extract_es_verses.py
EN_TO_ES_SLUG = {
    "genesis": "genesis", "exodus": "exodo", "leviticus": "levitico",
    "numbers": "numeros", "deuteronomy": "deuteronomio", "joshua": "josue",
    "judges": "jueces", "ruth": "rut", "1-samuel": "1-samuel",
    "2-samuel": "2-samuel", "1-kings": "1-reyes", "2-kings": "2-reyes",
    "1-chronicles": "1-cronicas", "2-chronicles": "2-cronicas", "ezra": "esdras",
    "nehemiah": "nehemias", "esther": "ester", "job": "job", "psalms": "salmos",
    "proverbs": "proverbios", "ecclesiastes": "eclesiastes",
    "song-of-solomon": "cantares", "isaiah": "isaias", "jeremiah": "jeremias",
    "lamentations": "lamentaciones", "ezekiel": "ezequiel", "daniel": "daniel",
    "hosea": "oseas", "joel": "joel", "amos": "amos", "obadiah": "abdias",
    "jonah": "jonas", "micah": "miqueas", "nahum": "nahum", "habakkuk": "habacuc",
    "zephaniah": "sofonias", "haggai": "hageo", "zechariah": "zacarias",
    "malachi": "malaquias",
    "matthew": "mateo", "mark": "marcos", "luke": "lucas", "john": "juan",
    "acts": "hechos", "romans": "romanos", "1-corinthians": "1-corintios",
    "2-corinthians": "2-corintios", "galatians": "galatas", "ephesians": "efesios",
    "philippians": "filipenses", "colossians": "colosenses",
    "1-thessalonians": "1-tesalonicenses", "2-thessalonians": "2-tesalonicenses",
    "1-timothy": "1-timoteo", "2-timothy": "2-timoteo", "titus": "tito",
    "philemon": "filemon", "hebrews": "hebreos", "james": "santiago",
    "1-peter": "1-pedro", "2-peter": "2-pedro", "1-john": "1-juan",
    "2-john": "2-juan", "3-john": "3-juan", "jude": "judas",
    "revelation": "apocalipsis",
    "1-nephi": "1-nefi", "2-nephi": "2-nefi", "jacob": "jacob", "enos": "enos",
    "jarom": "jarom", "omni": "omni", "words-of-mormon": "palabras-de-mormon",
    "mosiah": "mosiah", "alma": "alma", "helaman": "helaman",
    "3-nephi": "3-nefi", "4-nephi": "4-nefi", "mormon": "mormon",
    "ether": "eter", "moroni": "moroni",
    "sections": "secciones", "official-declarations": "declaraciones-oficiales",
    "moses": "moises", "abraham": "abraham", "js-matthew": "jose-smith-mateo",
    "js-history": "jose-smith-historia", "articles-of-faith": "articulos-de-fe",
}


def corpus_book_slug(en_slug: str, lang: str) -> str:
    """Get the corpus book slug for a given language."""
    if lang == "eng":
        return en_slug
    return EN_TO_ES_SLUG.get(en_slug, en_slug)


def build_chapter_url(volume_slug: str, book_slug: str, chapter_num: int,
                      lang: str, chapter_type: str = "standard") -> str:
    """Build the URL for a specific chapter on the Church site."""
    site_vol = SITE_VOLUME_MAP[volume_slug]
    lang_param = lang  # "eng" or "spa"

    if chapter_type == "facsimile":
        # Facsimiles: /study/scriptures/pgp/abr/fac-N
        return f"{BASE_URL}/study/scriptures/{site_vol}/abr/fac-{chapter_num}?lang={lang_param}"

    site_book = SITE_BOOK_MAP[(volume_slug, book_slug)]
    return f"{BASE_URL}/study/scriptures/{site_vol}/{site_book}/{chapter_num}?lang={lang_param}"


# ── HTML parsing ─────────────────────────────────────────────────────────────

def clean_verse_text(verse_el: Tag) -> str:
    """Extract clean verse text from a <p class='verse'> element.

    Removes footnote markers (<sup class='marker'>) while keeping the annotated words.
    Preserves clarity-word spans (italic words in KJV tradition).
    Normalizes whitespace.
    """
    # Remove all <sup class="marker"> elements (footnote letter markers)
    for sup in verse_el.find_all("sup", class_="marker"):
        sup.decompose()

    # Remove verse-number span
    for vn in verse_el.find_all("span", class_="verse-number"):
        vn.decompose()

    # Remove icon/button elements (associated content icons on verse 1)
    for icon in verse_el.find_all("span", class_=lambda c: c and "iconPointer" in str(c)):
        icon.decompose()
    for btn in verse_el.find_all("button"):
        btn.decompose()
    for svg in verse_el.find_all("svg"):
        svg.decompose()

    # Get text, normalize spaces
    text = verse_el.get_text()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_verse_number(verse_el: Tag) -> Optional[int]:
    """Extract verse number from a verse element."""
    # Try verse-number span
    vn = verse_el.find("span", class_="verse-number")
    if vn:
        num_text = vn.get_text().strip()
        try:
            return int(num_text)
        except ValueError:
            pass

    # Try data-eng-ref attribute (e.g., "1:1" → verse 1)
    ref = verse_el.get("data-eng-ref", "")
    if ":" in ref:
        try:
            return int(ref.split(":")[-1])
        except ValueError:
            pass

    # Try id attribute (e.g., "p1" → verse 1)
    pid = verse_el.get("id", "")
    if pid.startswith("p"):
        try:
            return int(pid[1:])
        except ValueError:
            pass

    return None


def extract_metadata(soup: BeautifulSoup) -> dict:
    """Extract chapter metadata: summary, footnotes, cross-references."""
    metadata = {}

    # Chapter summary
    summary_el = soup.find("p", class_=lambda c: c and "study-summary" in str(c))
    if summary_el:
        metadata["summary"] = summary_el.get_text().strip()

    # Page title (book title)
    h1 = soup.find("h1")
    if h1:
        metadata["title"] = h1.get_text().strip()

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        metadata["meta_description"] = meta_desc.get("content", "")

    # Footnotes — EN uses "note1_a", ES uses "note1a" (no underscore)
    footnotes = {}
    for li in soup.find_all("li", id=lambda i: i and re.match(r"note\d+_?[a-z]$", str(i))):
        note_id = li.get("id")
        note_text = li.get_text().strip()
        if note_text:
            # Normalize to consistent format: "note{verse}_{letter}"
            normalized_id = re.sub(r"^(note\d+)([a-z])$", r"\1_\2", note_id)
            footnotes[normalized_id] = note_text
    if footnotes:
        metadata["footnotes"] = footnotes

    return metadata


def extract_facsimile_text(soup: BeautifulSoup) -> str:
    """Extract facsimile explanation text.

    Facsimile pages have figure explanations (Fig. 1, Fig. 2, etc.)
    in <p> elements with id like 'figure1_p1', 'figure1_title1', etc.
    """
    lines = []
    for p in soup.find_all("p", id=lambda i: i and i.startswith("figure")):
        text = p.get_text().strip()
        text = re.sub(r"\s+", " ", text)
        if text:
            lines.append(text)
    return "\n".join(lines)


def extract_prose_text(soup: BeautifulSoup) -> str:
    """Extract prose content from non-verse pages (Official Declarations).

    Collects all <p> elements with id='pN' that are part of the main content,
    and joins them as a single block of text (verse number 1).
    """
    paragraphs = []
    for p in soup.find_all("p", id=lambda i: i and re.match(r"p\d+$", str(i))):
        # Remove footnote markers
        for sup in p.find_all("sup", class_="marker"):
            sup.decompose()
        text = p.get_text()
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            paragraphs.append(text)
    return " ".join(paragraphs)


def scrape_chapter(url: str, session: requests.Session, ca_bundle: str,
                   chapter_type: str = "standard") -> Optional[dict]:
    """Scrape a single chapter page. Returns dict with verses and metadata."""
    try:
        r = session.get(url, timeout=30, verify=ca_bundle or True)
        r.raise_for_status()
        # Server reports ISO-8859-1 but content is UTF-8
        r.encoding = "utf-8"
    except requests.RequestException as e:
        print(f"    ERROR fetching {url}: {e}", file=sys.stderr)
        return None

    soup = BeautifulSoup(r.text, "lxml")

    # Extract verses
    verse_elements = soup.find_all("p", class_=lambda c: c and "verse" in str(c))
    verses = []
    for vel in verse_elements:
        num = extract_verse_number(vel)
        text = clean_verse_text(vel)
        if num is not None and text:
            verses.append((num, text))

    # For prose chapters (Official Declarations), extract as single block
    if not verses and chapter_type == "prose":
        prose = extract_prose_text(soup)
        if prose:
            verses = [(1, prose)]

    # For facsimile chapters, extract figure explanations
    if not verses and chapter_type == "facsimile":
        fac_text = extract_facsimile_text(soup)
        if fac_text:
            # Store with verse_num=0 as sentinel for "raw text, no verse number"
            verses = [(0, fac_text)]

    # Extract metadata
    metadata = extract_metadata(soup)

    return {"verses": verses, "metadata": metadata}


# ── Checkpoint / resume ──────────────────────────────────────────────────────

def load_checkpoint(checkpoint_path: Path) -> set:
    """Load set of already-processed corpus paths."""
    if checkpoint_path.exists():
        return set(checkpoint_path.read_text(encoding="utf-8").strip().split("\n"))
    return set()


def save_checkpoint(checkpoint_path: Path, processed: set):
    """Save processed corpus paths to checkpoint file."""
    checkpoint_path.write_text("\n".join(sorted(processed)) + "\n", encoding="utf-8")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scrape scriptures from churchofjesuschrist.org")
    parser.add_argument("--lang", required=True, choices=["eng", "spa"], help="Language to scrape")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY, help="Delay between requests (seconds)")
    parser.add_argument("--volume", help="Scrape only this volume (ot, nt, bom, dc, pgp)")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--dry-run", action="store_true", help="Fetch but don't write files")
    parser.add_argument("--save-metadata", action="store_true", help="Save metadata JSON alongside verse files")
    args = parser.parse_args()

    lang_dir = "en" if args.lang == "eng" else "es"
    corpus_lang_dir = CORPUS_DIR / lang_dir / "scriptures"

    # Load chapter list from P1 structure
    with open(STRUCTURE_DIR / "chapters.json", encoding="utf-8") as f:
        chapters = json.load(f)

    # Assign corpus paths to facsimiles (they have corpus_path=None in the structure)
    for c in chapters:
        if c["chapter_type"] == "facsimile" and not c.get("corpus_path"):
            c["corpus_path"] = f"pgp/abraham/facsimile-{c['chapter_num']}.txt"

    # Filter to chapters with a corpus path
    chapters = [c for c in chapters if c.get("corpus_path")]

    if args.volume:
        chapters = [c for c in chapters if c["volume_slug"] == args.volume]

    # Checkpoint
    checkpoint_path = PROJECT_ROOT / "data" / f"scrape_checkpoint_{args.lang}.txt"
    processed = load_checkpoint(checkpoint_path) if args.resume else set()

    # Session with persistent connection
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; AlejandriaBot/1.0; scripture-study)"})
    ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE", "")

    stats = {"new": 0, "modified": 0, "unchanged": 0, "errors": 0, "skipped": 0}
    total = len(chapters)

    print(f"Scraping {total} chapters in {args.lang}...")
    print(f"  Corpus dir: {corpus_lang_dir}")
    print(f"  Delay: {args.delay}s between requests")
    if args.resume:
        print(f"  Resuming: {len(processed)} already processed")
    print()

    for i, ch in enumerate(chapters):
        corpus_path = ch["corpus_path"]  # e.g., "ot/genesis/1.txt"
        vol = ch["volume_slug"]
        book = ch["book_slug"]
        chapter_num = ch["chapter_num"]

        # Skip if already processed (resume mode)
        if corpus_path in processed:
            stats["skipped"] += 1
            continue

        # Build URL
        url = build_chapter_url(vol, book, chapter_num, args.lang, ch["chapter_type"])

        # Progress
        if (i + 1) % 50 == 0 or i == 0:
            print(f"  [{i+1}/{total}] {ch['reference_en']}...")

        # Scrape
        result = scrape_chapter(url, session, ca_bundle, chapter_type=ch["chapter_type"])
        if result is None:
            stats["errors"] += 1
            continue

        verses = result["verses"]
        if not verses:
            print(f"    WARNING: No verses found for {corpus_path} ({url})")
            stats["errors"] += 1
            continue

        # Sort by verse number
        verses.sort(key=lambda v: v[0])

        # Assemble content
        lines = []
        for num, text in verses:
            if num == 0:
                # Raw text (facsimiles) — no verse number prefix
                lines.append(text)
            else:
                lines.append(f"{num} {text}")
        content = "\n".join(lines) + "\n"

        # Determine target file path
        if lang_dir == "es":
            # Convert EN slug to ES slug for book directories
            parts = corpus_path.split("/")
            es_book = EN_TO_ES_SLUG.get(parts[1], parts[1])
            target = corpus_lang_dir / parts[0] / es_book / parts[2]
        else:
            target = corpus_lang_dir / Path(corpus_path)

        if not args.dry_run:
            # Compare with existing
            if target.exists():
                existing = target.read_text(encoding="utf-8")
                if existing == content:
                    stats["unchanged"] += 1
                else:
                    stats["modified"] += 1
                    target.write_text(content, encoding="utf-8")
            else:
                stats["new"] += 1
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")

            # Save metadata if requested
            if args.save_metadata and result["metadata"]:
                meta_path = target.with_suffix(".meta.json")
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(result["metadata"], f, ensure_ascii=False, indent=2)
        else:
            print(f"    [dry-run] Would write {len(verses)} verses to {target}")
            stats["new"] += 1

        # Track progress
        processed.add(corpus_path)

        # Checkpoint every 100 chapters
        if len(processed) % 100 == 0:
            save_checkpoint(checkpoint_path, processed)

        # Rate limit
        time.sleep(args.delay)

    # Final checkpoint
    save_checkpoint(checkpoint_path, processed)

    # Report
    print(f"\n{'='*60}")
    print(f"P2 Phase 2 — Scrape Report ({args.lang})")
    print(f"{'='*60}")
    print(f"  Total chapters:  {total}")
    print(f"  New files:       {stats['new']}")
    print(f"  Modified files:  {stats['modified']}")
    print(f"  Unchanged files: {stats['unchanged']}")
    print(f"  Skipped:         {stats['skipped']}")
    print(f"  Errors:          {stats['errors']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
