"""Scripture-aware metadata: detection, verse parsing, and reference generation.

Detects scripture files by path pattern, parses verse numbers from text,
and generates human-readable scripture references like "1 Nephi 1:1-5"
or "Mateo 1:25".
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import TypedDict


# ---------------------------------------------------------------------------
# Book registry
# ---------------------------------------------------------------------------

class BookNames(TypedDict):
    en: str
    es: str


# Maps directory-slug -> display names per language.
# Organised by volume for readability; merged into one flat dict at the end.

_BOM_BOOKS: dict[str, BookNames] = {
    "1-nephi":          {"en": "1 Nephi",            "es": "1 Nefi"},
    "2-nephi":          {"en": "2 Nephi",            "es": "2 Nefi"},
    "jacob":            {"en": "Jacob",              "es": "Jacob"},
    "enos":             {"en": "Enos",               "es": "Enós"},
    "jarom":            {"en": "Jarom",              "es": "Jarom"},
    "omni":             {"en": "Omni",               "es": "Omni"},
    "words-of-mormon":  {"en": "Words of Mormon",    "es": "Palabras de Mormón"},
    "mosiah":           {"en": "Mosiah",             "es": "Mosíah"},
    "alma":             {"en": "Alma",               "es": "Alma"},
    "helaman":          {"en": "Helaman",            "es": "Helamán"},
    "3-nephi":          {"en": "3 Nephi",            "es": "3 Nefi"},
    "4-nephi":          {"en": "4 Nephi",            "es": "4 Nefi"},
    "mormon":           {"en": "Mormon",             "es": "Mormón"},
    "ether":            {"en": "Ether",              "es": "Éter"},
    "moroni":           {"en": "Moroni",             "es": "Moroni"},
}

_OT_BOOKS: dict[str, BookNames] = {
    "genesis":          {"en": "Genesis",            "es": "Génesis"},
    "exodus":           {"en": "Exodus",             "es": "Éxodo"},
    "leviticus":        {"en": "Leviticus",          "es": "Levítico"},
    "numbers":          {"en": "Numbers",            "es": "Números"},
    "deuteronomy":      {"en": "Deuteronomy",        "es": "Deuteronomio"},
    "joshua":           {"en": "Joshua",             "es": "Josué"},
    "judges":           {"en": "Judges",             "es": "Jueces"},
    "ruth":             {"en": "Ruth",               "es": "Rut"},
    "1-samuel":         {"en": "1 Samuel",           "es": "1 Samuel"},
    "2-samuel":         {"en": "2 Samuel",           "es": "2 Samuel"},
    "1-kings":          {"en": "1 Kings",            "es": "1 Reyes"},
    "2-kings":          {"en": "2 Kings",            "es": "2 Reyes"},
    "1-chronicles":     {"en": "1 Chronicles",       "es": "1 Crónicas"},
    "2-chronicles":     {"en": "2 Chronicles",       "es": "2 Crónicas"},
    "ezra":             {"en": "Ezra",               "es": "Esdras"},
    "nehemiah":         {"en": "Nehemiah",           "es": "Nehemías"},
    "esther":           {"en": "Esther",             "es": "Ester"},
    "job":              {"en": "Job",                "es": "Job"},
    "psalms":           {"en": "Psalms",             "es": "Salmos"},
    "proverbs":         {"en": "Proverbs",           "es": "Proverbios"},
    "ecclesiastes":     {"en": "Ecclesiastes",       "es": "Eclesiastés"},
    "song-of-solomon":  {"en": "Song of Solomon",    "es": "Cantares"},
    "isaiah":           {"en": "Isaiah",             "es": "Isaías"},
    "jeremiah":         {"en": "Jeremiah",           "es": "Jeremías"},
    "lamentations":     {"en": "Lamentations",       "es": "Lamentaciones"},
    "ezekiel":          {"en": "Ezekiel",            "es": "Ezequiel"},
    "daniel":           {"en": "Daniel",             "es": "Daniel"},
    "hosea":            {"en": "Hosea",              "es": "Oseas"},
    "joel":             {"en": "Joel",               "es": "Joel"},
    "amos":             {"en": "Amos",               "es": "Amós"},
    "obadiah":          {"en": "Obadiah",            "es": "Abdías"},
    "jonah":            {"en": "Jonah",              "es": "Jonás"},
    "micah":            {"en": "Micah",              "es": "Miqueas"},
    "nahum":            {"en": "Nahum",              "es": "Nahúm"},
    "habakkuk":         {"en": "Habakkuk",           "es": "Habacuc"},
    "zephaniah":        {"en": "Zephaniah",          "es": "Sofonías"},
    "haggai":           {"en": "Haggai",             "es": "Hageo"},
    "zechariah":        {"en": "Zechariah",          "es": "Zacarías"},
    "malachi":          {"en": "Malachi",            "es": "Malaquías"},
}

_NT_BOOKS: dict[str, BookNames] = {
    "matthew":          {"en": "Matthew",            "es": "Mateo"},
    "mark":             {"en": "Mark",               "es": "Marcos"},
    "luke":             {"en": "Luke",               "es": "Lucas"},
    "john":             {"en": "John",               "es": "Juan"},
    "acts":             {"en": "Acts",               "es": "Hechos"},
    "romans":           {"en": "Romans",             "es": "Romanos"},
    "1-corinthians":    {"en": "1 Corinthians",      "es": "1 Corintios"},
    "2-corinthians":    {"en": "2 Corinthians",      "es": "2 Corintios"},
    "galatians":        {"en": "Galatians",          "es": "Gálatas"},
    "ephesians":        {"en": "Ephesians",          "es": "Efesios"},
    "philippians":      {"en": "Philippians",        "es": "Filipenses"},
    "colossians":       {"en": "Colossians",         "es": "Colosenses"},
    "1-thessalonians":  {"en": "1 Thessalonians",    "es": "1 Tesalonicenses"},
    "2-thessalonians":  {"en": "2 Thessalonians",    "es": "2 Tesalonicenses"},
    "1-timothy":        {"en": "1 Timothy",          "es": "1 Timoteo"},
    "2-timothy":        {"en": "2 Timothy",          "es": "2 Timoteo"},
    "titus":            {"en": "Titus",              "es": "Tito"},
    "philemon":         {"en": "Philemon",           "es": "Filemón"},
    "hebrews":          {"en": "Hebrews",            "es": "Hebreos"},
    "james":            {"en": "James",              "es": "Santiago"},
    "1-peter":          {"en": "1 Peter",            "es": "1 Pedro"},
    "2-peter":          {"en": "2 Peter",            "es": "2 Pedro"},
    "1-john":           {"en": "1 John",             "es": "1 Juan"},
    "2-john":           {"en": "2 John",             "es": "2 Juan"},
    "3-john":           {"en": "3 John",             "es": "3 Juan"},
    "jude":             {"en": "Jude",               "es": "Judas"},
    "revelation":       {"en": "Revelation",         "es": "Apocalipsis"},
}

_PGP_BOOKS: dict[str, BookNames] = {
    "moses":              {"en": "Moses",                  "es": "Moisés"},
    "abraham":            {"en": "Abraham",                "es": "Abraham"},
    "js-matthew":         {"en": "JS\u2014Matthew",        "es": "José Smith\u2014Mateo"},
    "js-history":         {"en": "JS\u2014History",        "es": "José Smith\u2014Historia"},
    "articles-of-faith":  {"en": "Articles of Faith",      "es": "Artículos de Fe"},
}

# Doctrine and Covenants has no book sub-division; the "book" level in the
# path is omitted (or the volume itself acts as the book).  We store a
# sentinel so format_reference can handle it.
_DC_VOLUME: BookNames = {"en": "D&C", "es": "DyC"}

# Flat registry: slug -> BookNames  (all volumes combined)
BOOK_REGISTRY: dict[str, BookNames] = {
    **_BOM_BOOKS,
    **_OT_BOOKS,
    **_NT_BOOKS,
    **_PGP_BOOKS,
}

# Volume slug -> set of book slugs that belong to it
VOLUME_BOOKS: dict[str, set[str]] = {
    "bom": set(_BOM_BOOKS),
    "ot":  set(_OT_BOOKS),
    "nt":  set(_NT_BOOKS),
    "pgp": set(_PGP_BOOKS),
    "dc":  set(),  # no book sub-level
}

# ---------------------------------------------------------------------------
# Path pattern
# ---------------------------------------------------------------------------

# Expected: {lang}/scriptures/{volume}/{book}/{chapter}.txt
# For D&C:  {lang}/scriptures/dc/{section}.txt  (no book level)
_SCRIPTURE_RE = re.compile(
    r"(?:^|[/\\])"
    r"(?P<lang>[a-z]{2})[/\\]"
    r"scriptures[/\\]"
    r"(?P<volume>[a-z]+)[/\\]"
    r"(?:(?P<book>[a-z0-9\-]+)[/\\])?"
    r"(?P<chapter>\d+)\.txt$",
    re.IGNORECASE,
)


@dataclass
class ScripturePath:
    lang: str
    volume: str
    book_slug: str | None
    chapter_num: int


def is_scripture(file_path: str) -> bool:
    """Return True if *file_path* matches the scripture directory convention."""
    return _SCRIPTURE_RE.search(file_path.replace("\\", "/")) is not None


def parse_scripture_path(file_path: str) -> dict[str, str | int | None] | None:
    """Extract scripture components from *file_path*.

    Returns a dict with keys ``lang``, ``volume``, ``book_slug``,
    ``chapter_num`` or ``None`` if the path is not a scripture.
    """
    m = _SCRIPTURE_RE.search(file_path.replace("\\", "/"))
    if m is None:
        return None

    volume = m.group("volume").lower()
    book_raw = m.group("book")
    book_slug: str | None = book_raw.lower() if book_raw else None

    # For D&C the "book" capture may actually be the section number directory
    # or absent entirely.  Normalise: if volume is dc, book_slug is None.
    if volume == "dc":
        # If there was a captured book group that is purely numeric, it is
        # really the chapter (section) — already captured as chapter.
        book_slug = None

    return {
        "lang": m.group("lang").lower(),
        "volume": volume,
        "book_slug": book_slug,
        "chapter_num": int(m.group("chapter")),
    }


# ---------------------------------------------------------------------------
# Verse parsing
# ---------------------------------------------------------------------------

_VERSE_LINE_RE = re.compile(r"^(\d+)\s+(.*)")


def parse_verses(text: str) -> list[tuple[int, str]]:
    """Parse numbered verses from *text*.

    Expected format — each line starts with a verse number followed by the
    verse body::

        1 I, Nephi, having been born of goodly parents...
        2 Yea, I make a record in the language of my father...

    Returns a list of ``(verse_number, verse_text)`` tuples **in file order**.
    Multi-line verses (continuation lines that do not start with a number) are
    appended to the previous verse.
    """
    verses: list[tuple[int, str]] = []
    for line in text.splitlines():
        line = line.rstrip()
        if not line:
            continue
        m = _VERSE_LINE_RE.match(line)
        if m:
            verses.append((int(m.group(1)), m.group(2)))
        elif verses:
            # Continuation of the previous verse
            num, body = verses[-1]
            verses[-1] = (num, body + " " + line.strip())
    return verses


# ---------------------------------------------------------------------------
# Verse-range detection for chunks
# ---------------------------------------------------------------------------


def get_verse_range(
    chunk_text: str,
    all_verses: list[tuple[int, str]],
) -> tuple[int, int] | None:
    """Determine the first and last verse numbers present in *chunk_text*.

    *all_verses* is the full list returned by :func:`parse_verses`.
    Returns ``(first_verse, last_verse)`` or ``None`` if no verses are found
    in the chunk.
    """
    found: list[int] = []
    for vnum, vtext in all_verses:
        # Check if a meaningful portion of the verse text appears in the chunk.
        # We use the first 60 characters (or the full text if shorter) to avoid
        # false positives on very short common phrases.
        snippet = vtext[:60]
        if snippet in chunk_text:
            found.append(vnum)
    if not found:
        return None
    return (min(found), max(found))


# ---------------------------------------------------------------------------
# Reference formatting
# ---------------------------------------------------------------------------


def format_reference(
    book_slug: str | None,
    volume: str,
    chapter: int,
    verse_start: int | None = None,
    verse_end: int | None = None,
    lang: str = "en",
) -> str:
    """Build a human-readable scripture reference string.

    Examples::

        >>> format_reference("1-nephi", "bom", 1, 1, 5)
        '1 Nephi 1:1-5'
        >>> format_reference("1-nephi", "bom", 1, 1, 5, lang="es")
        '1 Nefi 1:1-5'
        >>> format_reference(None, "dc", 76, 1, 5)
        'D&C 76:1-5'
        >>> format_reference(None, "dc", 76, 1, 5, lang="es")
        'DyC 76:1-5'
    """
    # --- Book / volume display name ---
    if volume == "dc":
        display_name = _DC_VOLUME[lang]
    elif book_slug and book_slug in BOOK_REGISTRY:
        display_name = BOOK_REGISTRY[book_slug][lang]
    else:
        # Fallback: capitalise the slug
        display_name = (book_slug or volume).replace("-", " ").title()

    # --- Verse suffix ---
    verse_part = ""
    if verse_start is not None:
        if verse_end is not None and verse_end != verse_start:
            verse_part = f":{verse_start}-{verse_end}"
        else:
            verse_part = f":{verse_start}"

    return f"{display_name} {chapter}{verse_part}"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def build_chunk_reference(
    file_path: str,
    chunk_text: str,
    full_text: str,
) -> str | None:
    """Return a scripture reference for a chunk, or ``None`` if not a scripture.

    Parameters
    ----------
    file_path:
        Path to the source file (may use ``/`` or ``\\``).
    chunk_text:
        The text of the chunk whose reference we want.
    full_text:
        The complete text of the source file (needed to parse all verses).
    """
    parsed = parse_scripture_path(file_path)
    if parsed is None:
        return None

    all_verses = parse_verses(full_text)
    vrange = get_verse_range(chunk_text, all_verses) if all_verses else None

    verse_start: int | None = None
    verse_end: int | None = None
    if vrange is not None:
        verse_start, verse_end = vrange

    return format_reference(
        book_slug=parsed["book_slug"],  # type: ignore[arg-type]
        volume=parsed["volume"],        # type: ignore[arg-type]
        chapter=parsed["chapter_num"],  # type: ignore[arg-type]
        verse_start=verse_start,
        verse_end=verse_end,
        lang=parsed["lang"],            # type: ignore[arg-type]
    )


def build_scripture_metadata(
    file_path: str,
    chunk_text: str,
    full_text: str,
) -> dict:
    """Build complete scripture metadata dict for a chunk.

    Returns a dict with keys: lang, volume, book, chapter, reference,
    verse_start, verse_end.  Returns empty dict if not a scripture.
    """
    parsed = parse_scripture_path(file_path)
    if parsed is None:
        return {}

    all_verses = parse_verses(full_text)
    vrange = get_verse_range(chunk_text, all_verses) if all_verses else None

    reference = build_chunk_reference(file_path, chunk_text, full_text)

    meta: dict = {
        "lang": parsed["lang"],
        "volume": parsed["volume"],
        "book": parsed["book_slug"],
        "chapter": parsed["chapter_num"],
    }
    if reference:
        meta["reference"] = reference
    if vrange:
        meta["verse_start"] = vrange[0]
        meta["verse_end"] = vrange[1]

    return meta
