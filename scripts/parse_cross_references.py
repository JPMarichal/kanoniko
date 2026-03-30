"""P2 Phase 3 — Parse scripture cross-references from footnotes.

Reads .meta.json footnote data from both EN and ES corpus, extracts scripture
references, resolves abbreviations to canonical book slugs, and builds a
bidirectional cross-reference index.

Input:
  corpus/{lang}/scriptures/**/*.meta.json  (footnotes field)

Output:
  data/scripture_structure/cross_references.json
    List of {source: "volume/book/chapter:verse", target: "volume/book/chapter:verse",
             footnote_id, lang, bidirectional}

Usage:
  python scripts/parse_cross_references.py [--lang eng|spa|both] [--dry-run] [--stats]
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_ROOT / "corpus"
OUTPUT_PATH = PROJECT_ROOT / "data" / "scripture_structure" / "cross_references.json"

# ── Abbreviation → book slug mappings ────────────────────────────────────────
# Derived from actual footnote data analysis.
# \xa0 = non-breaking space, \u2014 = em dash

# English abbreviations (from churchofjesuschrist.org EN footnotes)
EN_ABBREV_TO_SLUG: dict[str, str] = {
    # Old Testament
    "Gen":          "genesis",
    "Ex":           "exodus",
    "Lev":          "leviticus",
    "Num":          "numbers",
    "Deut":         "deuteronomy",
    "Josh":         "joshua",
    "Judg":         "judges",
    "Ruth":         "ruth",
    "1\xa0Sam":     "1-samuel",
    "2\xa0Sam":     "2-samuel",
    "1\xa0Kgs":     "1-kings",
    "2\xa0Kgs":     "2-kings",
    "1\xa0Chr":     "1-chronicles",
    "2\xa0Chr":     "2-chronicles",
    "Ezra":         "ezra",
    "Neh":          "nehemiah",
    "Esth":         "esther",
    "Job":          "job",
    "Ps":           "psalms",
    "Prov":         "proverbs",
    "Eccl":         "ecclesiastes",
    "Song":         "song-of-solomon",
    "Isa":          "isaiah",
    "Jer":          "jeremiah",
    "Lam":          "lamentations",
    "Ezek":         "ezekiel",
    "Dan":          "daniel",
    "Hosea":        "hosea",
    "Joel":         "joel",
    "Amos":         "amos",
    "Obad":         "obadiah",
    "Jonah":        "jonah",
    "Micah":        "micah",
    "Nahum":        "nahum",
    "Hab":          "habakkuk",
    "Zeph":         "zephaniah",
    "Hag":          "haggai",
    "Zech":         "zechariah",
    "Mal":          "malachi",
    # New Testament
    "Matt":         "matthew",
    "Mark":         "mark",
    "Luke":         "luke",
    "John":         "john",
    "Acts":         "acts",
    "Rom":          "romans",
    "1\xa0Cor":     "1-corinthians",
    "2\xa0Cor":     "2-corinthians",
    "Gal":          "galatians",
    "Eph":          "ephesians",
    "Philip":       "philippians",
    "Col":          "colossians",
    "1\xa0Thes":    "1-thessalonians",
    "2\xa0Thes":    "2-thessalonians",
    "1\xa0Tim":     "1-timothy",
    "2\xa0Tim":     "2-timothy",
    "Titus":        "titus",
    "Philem":       "philemon",
    "Heb":          "hebrews",
    "James":        "james",
    "1\xa0Pet":     "1-peter",
    "2\xa0Pet":     "2-peter",
    "1\xa0Jn":      "1-john",
    "2\xa0Jn":      "2-john",
    "3\xa0Jn":      "3-john",
    "Jude":         "jude",
    "Rev":          "revelation",
    # Book of Mormon
    "1\xa0Ne":      "1-nephi",
    "2\xa0Ne":      "2-nephi",
    "Jacob":        "jacob",
    "Enos":         "enos",
    "Jarom":        "jarom",
    "Omni":         "omni",
    "W\xa0of\xa0M": "words-of-mormon",
    "Mosiah":       "mosiah",
    "Alma":         "alma",
    "Hel":          "helaman",
    "3\xa0Ne":      "3-nephi",
    "4\xa0Ne":      "4-nephi",
    "Morm":         "mormon",
    "Ether":        "ether",
    "Moro":         "moroni",
    # Doctrine and Covenants
    "D&C":          "_dc",       # Special: no book slug, volume=dc
    # Pearl of Great Price
    "Moses":        "moses",
    "Abr":          "abraham",
    "JS\u2014H":    "js-history",
    "JS\u2014M":    "js-matthew",
    "A\xa0of\xa0F": "articles-of-faith",
}

# Spanish abbreviations (from churchofjesuschrist.org ES footnotes)
ES_ABBREV_TO_SLUG: dict[str, str] = {
    # Old Testament
    "Gén":          "genesis",
    "Gen":          "genesis",
    "Éx":           "exodus",
    "Ex":           "exodus",
    "Lev":          "leviticus",
    "Núm":          "numbers",
    "Num":          "numbers",
    "Deut":         "deuteronomy",
    "Josué":        "joshua",
    "Josue":        "joshua",
    "Jue":          "judges",
    "Rut":          "ruth",
    "1\xa0Sam":     "1-samuel",
    "2\xa0Sam":     "2-samuel",
    "1\xa0Rey":     "1-kings",
    "2\xa0Rey":     "2-kings",
    "1\xa0Cró":     "1-chronicles",
    "1\xa0Cro":     "1-chronicles",
    "2\xa0Cró":     "2-chronicles",
    "2\xa0Cro":     "2-chronicles",
    "Esd":          "ezra",
    "Neh":          "nehemiah",
    "Ester":        "esther",
    "Job":          "job",
    "Sal":          "psalms",
    "Prov":         "proverbs",
    "Ecle":         "ecclesiastes",
    "Cant":         "song-of-solomon",
    "Isa":          "isaiah",
    "Jer":          "jeremiah",
    "Lam":          "lamentations",
    "Ezeq":         "ezekiel",
    "Dan":          "daniel",
    "Oseas":        "hosea",
    "Joel":         "joel",
    "Amós":         "amos",
    "Amos":         "amos",
    "Abd":          "obadiah",
    "Jonás":        "jonah",
    "Jonas":        "jonah",
    "Miq":          "micah",
    "Miqueas":      "micah",
    "Nahúm":        "nahum",
    "Nahum":        "nahum",
    "Hab":          "habakkuk",
    "Sof":          "zephaniah",
    "Hageo":        "haggai",
    "Zac":          "zechariah",
    "Mal":          "malachi",
    # New Testament
    "Mateo":        "matthew",
    "Mar":          "mark",
    "Marcos":       "mark",
    "Lucas":        "lucas",  # Will be normalized to "luke" below
    "Juan":         "john",
    "Hech":         "acts",
    "Rom":          "romans",
    "1\xa0Cor":     "1-corinthians",
    "2\xa0Cor":     "2-corinthians",
    "Gál":          "galatians",
    "Gal":          "galatians",
    "Efe":          "ephesians",
    "Filip":        "philippians",
    "Col":          "colossians",
    "1\xa0Tes":     "1-thessalonians",
    "2\xa0Tes":     "2-thessalonians",
    "1\xa0Tim":     "1-timothy",
    "2\xa0Tim":     "2-timothy",
    "Tito":         "titus",
    "Filem":        "philemon",
    "Heb":          "hebrews",
    "Stg":          "james",
    "1\xa0Pe":      "1-peter",
    "2\xa0Pe":      "2-peter",
    "1\xa0Juan":    "1-john",
    "2\xa0Juan":    "2-john",
    "3\xa0Juan":    "3-john",
    "Judas":        "jude",
    "Apoc":         "revelation",
    # Book of Mormon
    "1\xa0Ne":      "1-nephi",
    "2\xa0Ne":      "2-nephi",
    "Jacob":        "jacob",
    "Enós":         "enos",
    "Enos":         "enos",
    "Jarom":        "jarom",
    "Omni":         "omni",
    "Pal\xa0de\xa0Morm": "words-of-mormon",
    "Mos":          "mosiah",
    "Alma":         "alma",
    "Hel":          "helaman",
    "3\xa0Ne":      "3-nephi",
    "4\xa0Ne":      "4-nephi",
    "Morm":         "mormon",
    "Éter":         "ether",
    "Eter":         "ether",
    "Moro":         "moroni",
    # Doctrine and Covenants
    "DyC":          "_dc",       # Special: no book slug, volume=dc
    # Pearl of Great Price
    "Moisés":       "moses",
    "Moises":       "moses",
    "Abr":          "abraham",
    "JS\u2014H":    "js-history",
    "JS\u2014M":    "js-matthew",
    "AdeF":         "articles-of-faith",
}

# Fix: "lucas" slug doesn't exist — it's "luke" in corpus path
ES_ABBREV_TO_SLUG["Lucas"] = "luke"  # Corpus uses EN slugs for paths

# Book slug → volume mapping (for resolving corpus paths)
SLUG_TO_VOLUME: dict[str, str] = {}

# BOM
for s in ["1-nephi", "2-nephi", "jacob", "enos", "jarom", "omni",
          "words-of-mormon", "mosiah", "alma", "helaman", "3-nephi",
          "4-nephi", "mormon", "ether", "moroni"]:
    SLUG_TO_VOLUME[s] = "bom"

# OT
for s in ["genesis", "exodus", "leviticus", "numbers", "deuteronomy",
          "joshua", "judges", "ruth", "1-samuel", "2-samuel", "1-kings",
          "2-kings", "1-chronicles", "2-chronicles", "ezra", "nehemiah",
          "esther", "job", "psalms", "proverbs", "ecclesiastes",
          "song-of-solomon", "isaiah", "jeremiah", "lamentations",
          "ezekiel", "daniel", "hosea", "joel", "amos", "obadiah",
          "jonah", "micah", "nahum", "habakkuk", "zephaniah", "haggai",
          "zechariah", "malachi"]:
    SLUG_TO_VOLUME[s] = "ot"

# NT
for s in ["matthew", "mark", "luke", "john", "acts", "romans",
          "1-corinthians", "2-corinthians", "galatians", "ephesians",
          "philippians", "colossians", "1-thessalonians", "2-thessalonians",
          "1-timothy", "2-timothy", "titus", "philemon", "hebrews",
          "james", "1-peter", "2-peter", "1-john", "2-john", "3-john",
          "jude", "revelation"]:
    SLUG_TO_VOLUME[s] = "nt"

# PGP
for s in ["moses", "abraham", "js-matthew", "js-history", "articles-of-faith"]:
    SLUG_TO_VOLUME[s] = "pgp"

# D&C sentinel
SLUG_TO_VOLUME["_dc"] = "dc"


# ── Data structures ──────────────────────────────────────────────────────────

@dataclass
class ScriptureRef:
    """A resolved scripture reference pointing to a specific verse or range."""
    volume: str          # ot, nt, bom, dc, pgp
    book_slug: str       # e.g. "1-nephi", "sections" for D&C
    chapter: int
    verse_start: int
    verse_end: Optional[int] = None   # None if single verse

    @property
    def canonical_key(self) -> str:
        """Canonical string key for deduplication: 'volume/book/chapter:verse[-end]'."""
        base = f"{self.volume}/{self.book_slug}/{self.chapter}:{self.verse_start}"
        if self.verse_end and self.verse_end != self.verse_start:
            base += f"-{self.verse_end}"
        return base

    @property
    def chapter_key(self) -> str:
        """Chapter-level key (no verse): 'volume/book/chapter'."""
        return f"{self.volume}/{self.book_slug}/{self.chapter}"


@dataclass
class CrossReference:
    """A directional cross-reference from one verse to another."""
    source: str          # canonical_key of source verse
    target: str          # canonical_key of target verse
    source_chapter: str  # chapter_key of source (for file-level grouping)
    target_chapter: str  # chapter_key of target
    footnote_id: str     # e.g. "note1_a"
    lang: str            # "en" or "es"


@dataclass
class CrossRefIndex:
    """Complete cross-reference index with statistics."""
    references: list[CrossReference] = field(default_factory=list)
    unresolved: list[dict] = field(default_factory=list)  # refs we couldn't parse
    stats: dict = field(default_factory=dict)


# ── Building the abbreviation lookup ─────────────────────────────────────────

def _build_abbrev_lookup(lang: str) -> dict[str, str]:
    """Build a normalized abbreviation→slug lookup for the given language.

    Returns a dict where keys are abbreviation patterns (with dots stripped,
    NBSP normalized) and values are book slugs.
    """
    raw = EN_ABBREV_TO_SLUG if lang == "en" else ES_ABBREV_TO_SLUG
    lookup = {}
    for abbr, slug in raw.items():
        # Store original
        lookup[abbr] = slug
        # Also store with trailing dot stripped (footnotes use "Gen." but we match "Gen")
        lookup[abbr.rstrip(".")] = slug
    return lookup


def _build_abbrev_regexes(lookup: dict[str, str]) -> tuple[re.Pattern, re.Pattern]:
    """Build regexes for scripture references.

    Returns two patterns:
      1. Chapter:verse regex (captures: abbrev, chapter, verse_spec)
      2. Chapter-only regex (captures: abbrev, chapter) — for refs like "DyC 13."
    """
    # Sort abbreviations by length (longest first) to avoid partial matches
    abbrs = sorted(lookup.keys(), key=len, reverse=True)
    # Escape special regex characters in abbreviations
    escaped = [re.escape(a) for a in abbrs]
    abbr_pattern = "|".join(escaped)

    # Pattern 1: chapter:verse references
    verse_pattern = (
        rf"({abbr_pattern})"           # group 1: abbreviation
        r"\.?\s+"                       # optional dot + whitespace
        r"(\d+)"                        # group 2: chapter
        r":"                            # colon separator
        r"(\d+"                         # group 3 start: first verse
        r"(?:\s*\([^)]*\))?"           # optional parenthetical range
        r"(?:,\s*\d+(?:\s*\([^)]*\))?)*"  # optional comma-separated additional verses
        r")"                            # group 3 end
    )

    # Pattern 2: chapter-only references (e.g., "DyC 13." or "1 Ne. 8")
    # Must NOT be followed by a colon (which would be a chapter:verse ref)
    chapter_only_pattern = (
        rf"({abbr_pattern})"           # group 1: abbreviation
        r"\.?\s+"                       # optional dot + whitespace
        r"(\d+)"                        # group 2: chapter
        r"(?=[.;,)\s]|$)"             # followed by punctuation, space, or end
    )

    return re.compile(verse_pattern), re.compile(chapter_only_pattern)


# ── Reference parsing ────────────────────────────────────────────────────────

def _parse_verse_spec(verse_str: str) -> list[tuple[int, Optional[int]]]:
    """Parse a verse specification into (start, end) tuples.

    Examples:
      "3"                 → [(3, None)]
      "3 (3–5)"          → [(3, 5)]
      "25 (25, 28)"      → [(25, None), (28, None)]  — discrete verses
      "3, 50"            → [(3, None), (50, None)]
      "1 (1–4), 7"       → [(1, 4), (7, None)]
    """
    results = []

    # Split on comma at the top level (not inside parens)
    parts = _split_outside_parens(verse_str, ",")

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Check for parenthetical range: "3 (3–5)" or "25 (25, 28)"
        m = re.match(r"(\d+)\s*\(([^)]+)\)", part)
        if m:
            _primary = int(m.group(1))
            paren_content = m.group(2)
            # Check if range (3–5) or discrete (25, 28)
            range_m = re.match(r"(\d+)\s*[\u2013\-]\s*(\d+)", paren_content)
            if range_m:
                results.append((int(range_m.group(1)), int(range_m.group(2))))
            else:
                # Discrete verses in parens: treat each as individual
                for v in re.findall(r"\d+", paren_content):
                    results.append((int(v), None))
        else:
            # Simple verse number
            vm = re.match(r"(\d+)", part)
            if vm:
                results.append((int(vm.group(1)), None))

    return results if results else [(1, None)]  # fallback


def _split_outside_parens(text: str, sep: str) -> list[str]:
    """Split text by separator, but only outside parentheses."""
    parts = []
    current = ""
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += ch
    if current:
        parts.append(current)
    return parts


def parse_footnote_refs(
    text: str,
    abbrev_lookup: dict[str, str],
    verse_regex: re.Pattern,
    chapter_regex: re.Pattern,
) -> list[ScriptureRef]:
    """Parse all scripture references from a single footnote text.

    Skips non-scripture markers: TG, GEE, HEB, GR, IE, OR, BD, JST/TJS.
    """
    refs = []
    matched_spans: list[tuple[int, int]] = []  # track matched positions

    def _is_jst(abbr: str) -> bool:
        return abbr.startswith(("JST", "TJS", "See\xa0JST", "See JST",
                                "V\u00e9ase\xa0TJS", "V\u00e9ase TJS"))

    def _resolve_slug(abbr: str) -> Optional[tuple[str, str]]:
        """Returns (volume, book_slug) or None."""
        slug = abbrev_lookup.get(abbr)
        if not slug:
            return None
        volume = SLUG_TO_VOLUME.get(slug)
        if not volume:
            return None
        book_slug = "sections" if slug == "_dc" else slug
        return volume, book_slug

    # Pass 1: chapter:verse references
    for m in verse_regex.finditer(text):
        abbr = m.group(1)
        if _is_jst(abbr):
            continue

        resolved = _resolve_slug(abbr)
        if not resolved:
            continue

        volume, book_slug = resolved
        chapter = int(m.group(2))
        verse_spec = m.group(3)
        matched_spans.append((m.start(), m.end()))

        verse_tuples = _parse_verse_spec(verse_spec)
        for v_start, v_end in verse_tuples:
            refs.append(ScriptureRef(
                volume=volume,
                book_slug=book_slug,
                chapter=chapter,
                verse_start=v_start,
                verse_end=v_end,
            ))

    # Pass 2: chapter-only references (only where not already matched)
    for m in chapter_regex.finditer(text):
        # Skip if this position was already captured by verse regex
        if any(s <= m.start() < e for s, e in matched_spans):
            continue

        abbr = m.group(1)
        if _is_jst(abbr):
            continue

        resolved = _resolve_slug(abbr)
        if not resolved:
            continue

        volume, book_slug = resolved
        chapter = int(m.group(2))

        # Chapter-only ref: verse_start=0 as sentinel
        refs.append(ScriptureRef(
            volume=volume,
            book_slug=book_slug,
            chapter=chapter,
            verse_start=0,  # sentinel: whole-chapter reference
        ))

    return refs


# ── ES slug → EN slug reverse mapping ────────────────────────────────────────
# Used to normalize ES corpus paths to canonical EN-slug keys.
# Imported from extract_es_verses.py's EN_TO_ES_SLUG (reversed).

_ES_TO_EN_SLUG: dict[str, str] = {
    # OT
    "genesis": "genesis", "exodo": "exodus", "levitico": "leviticus",
    "numeros": "numbers", "deuteronomio": "deuteronomy", "josue": "joshua",
    "jueces": "judges", "rut": "ruth", "1-samuel": "1-samuel",
    "2-samuel": "2-samuel", "1-reyes": "1-kings", "2-reyes": "2-kings",
    "1-cronicas": "1-chronicles", "2-cronicas": "2-chronicles",
    "esdras": "ezra", "nehemias": "nehemiah", "ester": "esther",
    "job": "job", "salmos": "psalms", "proverbios": "proverbs",
    "eclesiastes": "ecclesiastes", "cantares": "song-of-solomon",
    "isaias": "isaiah", "jeremias": "jeremiah",
    "lamentaciones": "lamentations", "ezequiel": "ezekiel",
    "daniel": "daniel", "oseas": "hosea", "joel": "joel", "amos": "amos",
    "abdias": "obadiah", "jonas": "jonah", "miqueas": "micah",
    "nahum": "nahum", "habacuc": "habakkuk", "sofonias": "zephaniah",
    "hageo": "haggai", "zacarias": "zechariah", "malaquias": "malachi",
    # NT
    "mateo": "matthew", "marcos": "mark", "lucas": "luke", "juan": "john",
    "hechos": "acts", "romanos": "romans", "1-corintios": "1-corinthians",
    "2-corintios": "2-corinthians", "galatas": "galatians",
    "efesios": "ephesians", "filipenses": "philippians",
    "colosenses": "colossians", "1-tesalonicenses": "1-thessalonians",
    "2-tesalonicenses": "2-thessalonians", "1-timoteo": "1-timothy",
    "2-timoteo": "2-timothy", "tito": "titus", "filemon": "philemon",
    "hebreos": "hebrews", "santiago": "james", "1-pedro": "1-peter",
    "2-pedro": "2-peter", "1-juan": "1-john", "2-juan": "2-john",
    "3-juan": "3-john", "judas": "jude", "apocalipsis": "revelation",
    # BOM
    "1-nefi": "1-nephi", "2-nefi": "2-nephi", "jacob": "jacob",
    "enos": "enos", "jarom": "jarom", "omni": "omni",
    "palabras-de-mormon": "words-of-mormon", "mosiah": "mosiah",
    "alma": "alma", "helaman": "helaman", "3-nefi": "3-nephi",
    "4-nefi": "4-nephi", "mormon": "mormon", "eter": "ether",
    "moroni": "moroni",
    # D&C
    "secciones": "sections",
    "declaraciones-oficiales": "official-declarations",
    # PGP
    "moises": "moses", "abraham": "abraham",
    "jose-smith-mateo": "js-matthew", "jose-smith-historia": "js-history",
    "articulos-de-fe": "articles-of-faith",
}


def _normalize_chapter_key(chapter_key: str, lang: str) -> str:
    """Normalize a chapter_key to use EN slugs (canonical form).

    For lang="en", returns as-is. For lang="es", converts ES book slugs to EN.
    """
    if lang == "en":
        return chapter_key

    parts = chapter_key.split("/")
    if len(parts) == 3:
        volume, book, chapter = parts
        en_book = _ES_TO_EN_SLUG.get(book, book)
        return f"{volume}/{en_book}/{chapter}"
    return chapter_key


# ── Footnote collection ──────────────────────────────────────────────────────

def collect_footnotes(lang: str) -> dict[str, dict[str, str]]:
    """Collect all footnotes from .meta.json files for a language.

    Returns: {chapter_key: {footnote_id: text, ...}, ...}
    where chapter_key uses CANONICAL EN slugs (e.g. "bom/1-nephi/1").
    """
    lang_dir = CORPUS_DIR / lang / "scriptures"
    result = {}

    for meta_path in sorted(lang_dir.rglob("*.meta.json")):
        # Extract chapter key from path
        rel = meta_path.relative_to(lang_dir)
        parts = rel.parts
        # Remove .meta.json suffix to get chapter number
        chapter_file = parts[-1].replace(".meta.json", "")

        if len(parts) == 3:
            # volume/book/chapter.meta.json
            chapter_key = f"{parts[0]}/{parts[1]}/{chapter_file}"
        elif len(parts) == 2:
            # dc/chapter.meta.json (D&C has no book level)
            chapter_key = f"{parts[0]}/sections/{chapter_file}"
        else:
            continue

        # Normalize ES slugs to EN canonical form
        chapter_key = _normalize_chapter_key(chapter_key, lang)

        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

        footnotes = meta.get("footnotes", {})
        if footnotes:
            result[chapter_key] = footnotes

    return result


# ── Source verse resolution ──────────────────────────────────────────────────

def _footnote_to_source_ref(chapter_key: str, footnote_id: str) -> Optional[ScriptureRef]:
    """Convert a chapter_key + footnote_id to a ScriptureRef for the source verse.

    chapter_key: "bom/1-nephi/1"
    footnote_id: "note3_a" → verse 3
    """
    m = re.match(r"note(\d+)_[a-z]", footnote_id)
    if not m:
        return None

    verse_num = int(m.group(1))
    parts = chapter_key.split("/")

    if len(parts) == 3:
        volume, book_slug, chapter_str = parts
    else:
        return None

    return ScriptureRef(
        volume=volume,
        book_slug=book_slug,
        chapter=int(chapter_str),
        verse_start=verse_num,
    )


# ── Main pipeline ────────────────────────────────────────────────────────────

def build_cross_reference_index(langs: list[str] = ["en", "es"]) -> CrossRefIndex:
    """Build the complete cross-reference index from footnote data."""
    index = CrossRefIndex()
    type_counts = Counter()
    refs_per_lang = Counter()
    unresolved_abbrevs = Counter()

    for lang in langs:
        print(f"\nProcessing {lang} footnotes...")
        abbrev_lookup = _build_abbrev_lookup(lang)
        verse_regex, chapter_regex = _build_abbrev_regexes(abbrev_lookup)

        footnotes = collect_footnotes(lang)
        print(f"  Loaded {sum(len(fn) for fn in footnotes.values())} footnotes "
              f"from {len(footnotes)} chapters")

        lang_refs = 0
        lang_unresolved = 0

        for chapter_key, fn_dict in footnotes.items():
            for fn_id, fn_text in fn_dict.items():
                # Classify footnote content
                has_tg = "TG\xa0" in fn_text or "TG " in fn_text
                has_gee = "GEE\xa0" in fn_text or "GEE " in fn_text
                has_heb = fn_text.startswith("HEB\xa0") or fn_text.startswith("HEB ")
                has_gr = fn_text.startswith("GR\xa0") or fn_text.startswith("GR ")
                has_ie = (fn_text.startswith("IE\xa0") or fn_text.startswith("IE ")
                          or fn_text.startswith("Es\xa0decir")
                          or fn_text.startswith("O\xa0sea"))
                has_or = fn_text.startswith("OR\xa0") or fn_text.startswith("OR ")

                if has_tg:
                    type_counts["TG/GEE"] += 1
                if has_heb or has_gr:
                    type_counts["linguistic"] += 1
                if has_ie or has_or:
                    type_counts["explanatory"] += 1

                # Parse scripture references from this footnote
                target_refs = parse_footnote_refs(fn_text, abbrev_lookup, verse_regex, chapter_regex)

                has_bd = "BD\xa0" in fn_text or "BD " in fn_text

                if not target_refs:
                    # No scripture refs found — might be TG-only, linguistic, etc.
                    if not (has_tg or has_gee or has_heb or has_gr or has_ie
                            or has_or or has_bd):
                        # Truly unresolved
                        unresolved_abbrevs[fn_text[:60]] += 1
                        lang_unresolved += 1
                    continue

                type_counts["scripture_ref"] += 1

                # Resolve source verse
                source_ref = _footnote_to_source_ref(chapter_key, fn_id)
                if not source_ref:
                    continue

                # Create cross-references
                for target in target_refs:
                    xref = CrossReference(
                        source=source_ref.canonical_key,
                        target=target.canonical_key,
                        source_chapter=source_ref.chapter_key,
                        target_chapter=target.chapter_key,
                        footnote_id=fn_id,
                        lang=lang,
                    )
                    index.references.append(xref)
                    lang_refs += 1

        refs_per_lang[lang] = lang_refs
        print(f"  Extracted {lang_refs} cross-references")
        if lang_unresolved:
            print(f"  Unresolved footnotes: {lang_unresolved}")

    # Statistics
    index.stats = {
        "total_references": len(index.references),
        "per_lang": dict(refs_per_lang),
        "footnote_types": dict(type_counts),
    }

    if unresolved_abbrevs:
        index.unresolved = [
            {"text": text, "count": count}
            for text, count in unresolved_abbrevs.most_common(20)
        ]

    return index


def make_bidirectional(index: CrossRefIndex) -> tuple[list[dict], dict]:
    """Create bidirectional cross-references from the directional index.

    For every A→B reference, ensures B→A exists. Returns:
      - list of all bidirectional reference dicts
      - stats about reciprocity
    """
    # Build set of existing directional refs (source→target at chapter:verse level)
    existing: set[tuple[str, str]] = set()
    refs_by_pair: dict[tuple[str, str], CrossReference] = {}

    for xref in index.references:
        pair = (xref.source, xref.target)
        existing.add(pair)
        refs_by_pair[pair] = xref

    # Find missing reciprocals
    reciprocals_needed = set()
    already_bidirectional = 0
    new_reciprocals = 0

    for xref in index.references:
        reverse = (xref.target, xref.source)
        if reverse in existing:
            already_bidirectional += 1
        else:
            reciprocals_needed.add(reverse)
            new_reciprocals += 1

    # Build output: original refs marked, plus new reciprocals
    output = []

    # Original references
    for xref in index.references:
        reverse = (xref.target, xref.source)
        is_recip = reverse in existing
        output.append({
            "source": xref.source,
            "target": xref.target,
            "source_chapter": xref.source_chapter,
            "target_chapter": xref.target_chapter,
            "footnote_id": xref.footnote_id,
            "lang": xref.lang,
            "direction": "original",
            "has_reciprocal": is_recip,
        })

    # New reciprocal references (B→A where only A→B existed)
    for target, source in reciprocals_needed:
        # Find the original A→B to get metadata
        original = refs_by_pair.get((source, target))
        if not original:
            continue

        # Derive chapter keys
        target_parts = target.rsplit(":", 1)
        source_parts = source.rsplit(":", 1)
        target_chapter = target_parts[0] if len(target_parts) == 2 else target
        source_chapter = source_parts[0] if len(source_parts) == 2 else source

        output.append({
            "source": target,     # reversed
            "target": source,     # reversed
            "source_chapter": target_chapter,
            "target_chapter": source_chapter,
            "footnote_id": original.footnote_id,
            "lang": original.lang,
            "direction": "reciprocal",
            "has_reciprocal": True,
        })

    stats = {
        "original_refs": len(index.references),
        "already_bidirectional": already_bidirectional // 2,  # counted from both sides
        "new_reciprocals_added": len(reciprocals_needed),
        "total_bidirectional": len(output),
        "unique_pairs": len(existing | reciprocals_needed),
    }

    return output, stats


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Parse scripture cross-references from footnotes")
    parser.add_argument("--lang", choices=["eng", "spa", "both"], default="both",
                        help="Language to process (default: both)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse and report but don't write output file")
    parser.add_argument("--stats", action="store_true",
                        help="Show detailed statistics")
    args = parser.parse_args()

    # Map CLI lang to corpus lang codes
    if args.lang == "eng":
        langs = ["en"]
    elif args.lang == "spa":
        langs = ["es"]
    else:
        langs = ["en", "es"]

    # Build index
    index = build_cross_reference_index(langs)

    print(f"\n{'='*60}")
    print("P2 Phase 3 — Cross-Reference Parsing Report")
    print(f"{'='*60}")
    print(f"  Total directional references: {index.stats['total_references']}")
    for lang, count in index.stats["per_lang"].items():
        print(f"    {lang}: {count}")
    print(f"\n  Footnote type distribution:")
    for ftype, count in sorted(index.stats["footnote_types"].items(),
                                key=lambda x: -x[1]):
        print(f"    {ftype}: {count}")

    if index.unresolved:
        print(f"\n  Top unresolved footnotes:")
        for item in index.unresolved[:10]:
            print(f"    [{item['count']}] {item['text']}")

    # Make bidirectional
    print(f"\n{'='*60}")
    print("Bidirectional crossing")
    print(f"{'='*60}")

    bidi_refs, bidi_stats = make_bidirectional(index)

    print(f"  Original directional refs:    {bidi_stats['original_refs']}")
    print(f"  Already had reciprocal:       {bidi_stats['already_bidirectional']}")
    print(f"  New reciprocals added:        {bidi_stats['new_reciprocals_added']}")
    print(f"  Total bidirectional entries:   {bidi_stats['total_bidirectional']}")
    print(f"  Unique verse pairs:           {bidi_stats['unique_pairs']}")

    if args.stats:
        # Per-volume breakdown
        vol_counts = Counter()
        for ref in bidi_refs:
            src_vol = ref["source"].split("/")[0]
            tgt_vol = ref["target"].split("/")[0]
            vol_counts[f"{src_vol} -> {tgt_vol}"] += 1

        print(f"\n  Cross-volume distribution (top 20):")
        for pair, count in vol_counts.most_common(20):
            print(f"    {pair}: {count}")

    if not args.dry_run:
        # Write output
        output = {
            "stats": {**index.stats, **bidi_stats},
            "references": bidi_refs,
        }

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n  Written to: {OUTPUT_PATH}")
        size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
        print(f"  File size: {size_mb:.1f} MB")
    else:
        print(f"\n  [DRY RUN — no file written]")

    print(f"{'='*60}")


if __name__ == "__main__":
    main()
