"""Parser for General Conference talk HTML files.

Extracts structured metadata and clean content from the standardized HTML
format used in the Alejandría corpus conference downloads.

Key design decisions:
- Author names are stripped of title prefixes (Elder, President, Hermana, etc.)
- Callings are normalized to canonical forms matching the gazetteer
- Notes are parsed to extract scripture citations as structured references
- Content and notes are returned separately for flexible chunking
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser


# ── Title prefix stripping ──────────────────────────────────────────────────

# Ordered by length descending so longer prefixes match first.
# Handles: "el élder", "la hermana", "la presidenta", "el presidente",
#           "el obispo", "el hermano", "Elder", "President", "Sister", etc.
_TITLE_PREFIXES_RE = re.compile(
    r"^(?:el |la |los |las )?"
    r"(?:Elder|President[ea]?|Sister|Brother|Bishop|"
    r"[EÉéè]lder|Presidente|Presidenta|Hermana|Hermano|Obispo)"
    r"\s+",
    re.IGNORECASE,
)


def strip_author_title(raw_author: str) -> str:
    """Remove ecclesiastical title prefix from an author name.

    >>> strip_author_title("Elder Ulisses Soares")
    'Ulisses Soares'
    >>> strip_author_title("el élder Ulisses Soares")
    'Ulisses Soares'
    >>> strip_author_title("la hermana Tracy Y Browning")
    'Tracy Y Browning'
    >>> strip_author_title("President Dallin H Oaks")
    'Dallin H Oaks'
    >>> strip_author_title("Amy A Wright")
    'Amy A Wright'
    """
    # Normalize non-breaking spaces
    name = raw_author.replace("\xa0", " ").strip()
    return _TITLE_PREFIXES_RE.sub("", name).strip()


# ── Calling normalization ───────────────────────────────────────────────────

# Map variant calling strings to canonical forms matching the gazetteer.
# Keys are lowercase; matching is case-insensitive.
_CALLING_NORMALIZATIONS: dict[str, str] = {
    # First Presidency
    "president of the church": "President of the Church",
    "presidente de la iglesia": "President of the Church",
    "first counselor in the first presidency": "First Presidency",
    "primer consejero de la primera presidencia": "First Presidency",
    "second counselor in the first presidency": "First Presidency",
    "segundo consejero de la primera presidencia": "First Presidency",
    "counselor in the first presidency": "First Presidency",
    "consejero de la primera presidencia": "First Presidency",
    # Quorum of the Twelve
    "of the quorum of the twelve apostles": "Quorum of the Twelve Apostles",
    "of the quorum of the twelve": "Quorum of the Twelve Apostles",
    "del quórum de los doce apóstoles": "Quorum of the Twelve Apostles",
    "del cuórum de los doce apóstoles": "Quorum of the Twelve Apostles",
    "del quórum de los doce": "Quorum of the Twelve Apostles",
    "acting president of the quorum of the twelve apostles": "Quorum of the Twelve Apostles",
    "acting president of the council of the twelve": "Quorum of the Twelve Apostles",
    "president of the quorum of the twelve apostles": "Quorum of the Twelve Apostles",
    "presidente del quórum de los doce apóstoles": "Quorum of the Twelve Apostles",
    # Seventy
    "of the presidency of the seventy": "Presidency of the Seventy",
    "de la presidencia de los setenta": "Presidency of the Seventy",
    "of the first quorum of the seventy": "First Quorum of the Seventy",
    "del primer quórum de los setenta": "First Quorum of the Seventy",
    "of the second quorum of the seventy": "Second Quorum of the Seventy",
    "del segundo quórum de los setenta": "Second Quorum of the Seventy",
    "of the seventy": "Seventy",
    "de los setenta": "Seventy",
    "emeritus member of the seventy": "Seventy",
    "emeritus member of the first quorum of the seventy": "Seventy",
    # Presiding Bishopric
    "presiding bishop": "Presiding Bishopric",
    "obispo presidente": "Presiding Bishopric",
    "first counselor in the presiding bishopric": "Presiding Bishopric",
    "second counselor in the presiding bishopric": "Presiding Bishopric",
    "primer consejero del obispado presidente": "Presiding Bishopric",
    "segundo consejero del obispado presidente": "Presiding Bishopric",
    # Relief Society
    "relief society general president": "Relief Society General Presidency",
    "general president of the relief society": "Relief Society General Presidency",
    "presidenta general de la sociedad de socorro": "Relief Society General Presidency",
    "first counselor in the relief society general presidency": "Relief Society General Presidency",
    "second counselor in the relief society general presidency": "Relief Society General Presidency",
    # Young Women
    "young women general president": "Young Women General Presidency",
    "general president of the young women": "Young Women General Presidency",
    "presidenta general de las mujeres jóvenes": "Young Women General Presidency",
    "first counselor in the young women general presidency": "Young Women General Presidency",
    "second counselor in the young women general presidency": "Young Women General Presidency",
    # Primary
    "general primary president": "Primary General Presidency",
    "primary general president": "Primary General Presidency",
    "presidenta general de la primaria": "Primary General Presidency",
    "first counselor in the primary general presidency": "Primary General Presidency",
    "second counselor in the primary general presidency": "Primary General Presidency",
    # Sunday School
    "sunday school general president": "Sunday School General Presidency",
    "general president of the sunday school": "Sunday School General Presidency",
    "presidente general de la escuela dominical": "Sunday School General Presidency",
    "first counselor in the sunday school general presidency": "Sunday School General Presidency",
    "second counselor in the sunday school general presidency": "Sunday School General Presidency",
    # Young Men
    "young men general president": "Young Men General Presidency",
    "general president of the young men": "Young Men General Presidency",
    "first counselor in the young men general presidency": "Young Men General Presidency",
    "second counselor in the young men general presidency": "Young Men General Presidency",
    # Relief Society — Spanish counselors
    "primera consejera de la presidencia general de la sociedad de socorro": "Relief Society General Presidency",
    "segunda consejera de la presidencia general de la sociedad de socorro": "Relief Society General Presidency",
    # Young Women — Spanish counselors
    "primera consejera de la presidencia general de las mujeres jóvenes": "Young Women General Presidency",
    "segunda consejera de la presidencia general de las mujeres jóvenes": "Young Women General Presidency",
    # Primary — Spanish counselors
    "primera consejera de la presidencia general de la primaria": "Primary General Presidency",
    "segunda consejera de la presidencia general de la primaria": "Primary General Presidency",
    # Historical: Council of the Twelve (pre-1970s name)
    "of the council of the twelve": "Quorum of the Twelve Apostles",
    "del consejo de los doce": "Quorum of the Twelve Apostles",
    # Historical: First Council of the Seventy
    "of the first council of the seventy": "First Quorum of the Seventy",
    "del primer consejo de los setenta": "First Quorum of the Seventy",
    # Presidency of the First Quorum of the Seventy
    "of the presidency of the first quorum of the seventy": "Presidency of the Seventy",
    "de la presidencia del primer quórum de los setenta": "Presidency of the Seventy",
    # President of the Church (full form)
    "president of the church of jesus christ of latter-day saints": "President of the Church",
    "presidente de la iglesia de jesucristo de los santos de los últimos días": "President of the Church",
    # Acting President of the Twelve (Spanish)
    "presidente en funciones del cuórum de los doce apóstoles": "Quorum of the Twelve Apostles",
    "presidente en funciones del quórum de los doce apóstoles": "Quorum of the Twelve Apostles",
    # Secretary to the First Presidency
    "secretary to the first presidency": "Secretary to the First Presidency",
    "secretario de la primera presidencia": "Secretary to the First Presidency",
    # Church Auditing
    "managing director, church auditing department": "Church Auditing Department",
    "chairman, church audit committee": "Church Auditing Department",
    "church audit committee": "Church Auditing Department",
    "director gerente del departamento de auditorías de la iglesia": "Church Auditing Department",
    # Patriarch to the Church (historical)
    "patriarch to the church": "Patriarch to the Church",
    "patriarca de la iglesia": "Patriarch to the Church",
    # Unknown / unidentified
    "posición no identificada": "",
    # Presiding Bishopric (variant)
    "of the presiding bishopric": "Presiding Bishopric",
    "del obispado presidente": "Presiding Bishopric",
    # President of the Quorum — typo in data ("Tweleve")
    "president of the quorum of the tweleve apostles": "Quorum of the Twelve Apostles",
    # President of the Council of the Twelve (historical)
    "president of the council of the twelve": "Quorum of the Twelve Apostles",
    # Sunday School — Spanish counselors
    "primer consejero de la presidencia general de la escuela dominical": "Sunday School General Presidency",
    "segundo consejero de la presidencia general de la escuela dominical": "Sunday School General Presidency",
    # Young Men — Spanish
    "presidente general de los hombres jóvenes": "Young Men General Presidency",
    "primer consejero de la presidencia general de los hombres jóvenes": "Young Men General Presidency",
    "segundo consejero de la presidencia general de los hombres jóvenes": "Young Men General Presidency",
    # Recently released (retain the organization)
    "recently released primary general president": "Primary General Presidency",
    "recently released young women general president": "Young Women General Presidency",
    "recently released relief society general president": "Relief Society General Presidency",
    # Assistant to the Twelve (historical)
    "assistant to the council of the twelve": "Assistant to the Twelve",
    "assistant to the twelve": "Assistant to the Twelve",
}


def normalize_calling(raw_calling: str) -> str:
    """Normalize a calling string to its canonical gazetteer form.

    >>> normalize_calling("Of the Quorum of the Twelve Apostles")
    'Quorum of the Twelve Apostles'
    >>> normalize_calling("Del Cuórum de los Doce Apóstoles")
    'Quorum of the Twelve Apostles'
    >>> normalize_calling("First Counselor in the First Presidency")
    'First Presidency'
    """
    cleaned = raw_calling.replace("\xa0", " ").strip()
    key = cleaned.lower()
    if key in _CALLING_NORMALIZATIONS:
        return _CALLING_NORMALIZATIONS[key]
    # Return cleaned original if no normalization found
    return cleaned


# ── Scripture reference extraction from notes ───────────────────────────────

# Matches scripture references like "Matthew 13:45–46", "D&C 19:16, 18–19",
# "1 Nephi 3:7", "Mosiah 15:7", etc.
_SCRIPTURE_REF_RE = re.compile(
    r"(?:See\s+|Véase\s+|Ver\s+)?"
    r"((?:[123]\s+)?"
    r"(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|"
    r"(?:[12]\s+)?Samuel|(?:[12]\s+)?Kings|(?:[12]\s+)?Chronicles|Ezra|"
    r"Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|"
    r"Song of Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|"
    r"Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|"
    r"Haggai|Zechariah|Malachi|"
    r"Matthew|Mark|Luke|John|Acts|Romans|"
    r"(?:[12]\s+)?Corinthians|Galatians|Ephesians|Philippians|Colossians|"
    r"(?:[12]\s+)?Thessalonians|(?:[12]\s+)?Timothy|Titus|Philemon|"
    r"Hebrews|James|(?:[12]\s+)?Peter|(?:[123]\s+)?John|Jude|Revelation|"
    r"(?:[12]\s+)?Nephi|Jacob|Enos|Jarom|Omni|"
    r"Words of Mormon|Mosiah|Alma|Helaman|"
    r"(?:3\s+|4\s+)?Nephi|Mormon|Ether|Moroni|"
    r"Doctrine and Covenants|D&C|"
    r"Moses|Abraham|Joseph Smith[—–-]History|JS[—–-]H|"
    r"Articles of Faith|"
    # Spanish
    r"Génesis|Éxodo|Levítico|Números|Deuteronomio|Josué|Jueces|Rut|"
    r"(?:[12]\s+)?Reyes|(?:[12]\s+)?Crónicas|Esdras|"
    r"Nehemías|Ester|Salmos?|Proverbios|Eclesiastés|"
    r"Cantares|Isaías|Jeremías|Lamentaciones|Ezequiel|"
    r"Oseas|Amós|Abdías|Jonás|Miqueas|Nahúm|Habacuc|Sofonías|"
    r"Hageo|Zacarías|Malaquías|"
    r"Mateo|Marcos|Lucas|Juan|Hechos|Romanos|"
    r"(?:[12]\s+)?Corintios|Gálatas|Efesios|Filipenses|Colosenses|"
    r"(?:[12]\s+)?Tesalonicenses|(?:[12]\s+)?Timoteo|"
    r"Hebreos|Santiago|(?:[12]\s+)?Pedro|Judas|Apocalipsis|"
    r"(?:[12]\s+)?Nefi|Enós|Jarom|Omni|"
    r"Palabras de Mormón|Mosíah|Helamán|"
    r"Mormón|Éter|Moroní|"
    r"Doctrina y Convenios|DyC)"
    r"\s+\d+(?::\d+(?:\s*[,;–—-]\s*\d+)*)*)",
    re.IGNORECASE,
)


# ── HTML Parser ─────────────────────────────────────────────────────────────

@dataclass
class ConferenceTalk:
    """Parsed conference talk with structured metadata."""
    title: str = ""
    author_raw: str = ""       # Original with title prefix
    author: str = ""           # Normalized (prefix stripped)
    calling_raw: str = ""      # Original calling text
    calling: str = ""          # Normalized to canonical form
    conference_date: str = ""  # "YYYY-MM" format
    lang: str = ""             # "eng" or "spa"
    note_count: int = 0
    content: str = ""          # Clean text from div.content
    notes_text: str = ""       # Clean text from div.notes
    notes_raw: list[str] = field(default_factory=list)  # Individual note texts
    scripture_refs: list[str] = field(default_factory=list)  # From notes
    source_url: str = ""       # Original URL
    file_path: str = ""        # Relative path in corpus


class _TalkHTMLParser(HTMLParser):
    """State-machine HTML parser for conference talk files."""

    def __init__(self) -> None:
        super().__init__()
        self._div_stack: list[str] = []  # Track div classes
        self._current_class: str = ""
        self._in_tag: str | None = None  # 'h1', 'author', 'calling', 'metadata'
        self._in_content: bool = False
        self._in_notes: bool = False
        self._in_note_li: bool = False
        self._in_extraction: bool = False
        self._skip_tags: set[str] = {"style", "script"}
        self._skip_depth: int = 0

        self.title: str = ""
        self.author: str = ""
        self.calling: str = ""
        self.metadata: str = ""
        self.content_parts: list[str] = []
        self.notes_parts: list[str] = []
        self.note_items: list[str] = []
        self._current_note: list[str] = []
        self.extraction_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = dict(attrs)
        cls = attr_dict.get("class", "")

        if tag in self._skip_tags:
            self._skip_depth += 1
            return

        if tag == "div":
            self._div_stack.append(cls)
            if cls == "header":
                pass
            elif cls == "author":
                self._in_tag = "author"
            elif cls == "calling":
                self._in_tag = "calling"
            elif cls == "metadata":
                self._in_tag = "metadata"
            elif cls == "content":
                self._in_content = True
            elif cls == "notes":
                self._in_notes = True
            elif cls == "extraction-info":
                self._in_extraction = True

        elif tag == "h1" and self._div_stack and self._div_stack[-1] == "header":
            self._in_tag = "h1"

        elif tag == "li" and self._in_notes:
            self._in_note_li = True
            self._current_note = []

        elif tag == "p":
            if self._in_content:
                pass  # Text will be captured in handle_data
            elif self._in_notes:
                pass

        elif tag == "a" and self._in_extraction:
            href = attr_dict.get("href", "")
            if href:
                self.extraction_parts.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag in self._skip_tags and self._skip_depth > 0:
            self._skip_depth -= 1
            return

        if tag == "div" and self._div_stack:
            cls = self._div_stack.pop()
            if cls == "content":
                self._in_content = False
            elif cls == "notes":
                self._in_notes = False
            elif cls == "extraction-info":
                self._in_extraction = False
            self._in_tag = None

        elif tag in ("h1",):
            self._in_tag = None

        elif tag == "p" and self._in_content:
            self.content_parts.append("\n")

        elif tag == "li" and self._in_note_li:
            self._in_note_li = False
            note_text = " ".join(self._current_note).strip()
            if note_text:
                self.note_items.append(note_text)
            self._current_note = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return

        text = data

        if self._in_tag == "h1":
            self.title += text
        elif self._in_tag == "author":
            self.author += text
        elif self._in_tag == "calling":
            self.calling += text
        elif self._in_tag == "metadata":
            self.metadata += text
        elif self._in_content:
            self.content_parts.append(text)
        elif self._in_note_li:
            self._current_note.append(text)
        elif self._in_notes:
            self.notes_parts.append(text)
        elif self._in_extraction:
            self.extraction_parts.append(text)


def parse_conference_talk(html: str, file_path: str = "") -> ConferenceTalk:
    """Parse a conference talk HTML file into structured data.

    Args:
        html: Raw HTML content of the talk file.
        file_path: Relative path for metadata (e.g., "en/general-conference/2024/10/slug.html").

    Returns:
        ConferenceTalk with all extracted metadata and content.
    """
    parser = _TalkHTMLParser()
    parser.feed(html)

    talk = ConferenceTalk(file_path=file_path)

    # Title
    talk.title = parser.title.replace("\xa0", " ").strip()

    # Author — strip title prefix
    talk.author_raw = parser.author.replace("\xa0", " ").strip()
    talk.author = strip_author_title(talk.author_raw)

    # Calling — normalize
    talk.calling_raw = parser.calling.replace("\xa0", " ").strip()
    talk.calling = normalize_calling(talk.calling_raw)

    # Metadata line: "2024-10 | ENG | 23 notas"
    meta = parser.metadata.replace("\xa0", " ").strip()
    meta_parts = [p.strip() for p in meta.split("|")]
    if meta_parts:
        talk.conference_date = meta_parts[0]
    if len(meta_parts) > 1:
        talk.lang = meta_parts[1].lower().strip()
    if len(meta_parts) > 2:
        m = re.search(r"(\d+)", meta_parts[2])
        if m:
            talk.note_count = int(m.group(1))

    # Content — join and clean
    raw_content = "".join(parser.content_parts)
    # Remove superscript note markers that leaked as text
    raw_content = re.sub(r"\s*\d+\s*(?=\n)", "", raw_content)
    talk.content = re.sub(r"\n{3,}", "\n\n", raw_content).strip()

    # Notes
    talk.notes_raw = parser.note_items
    talk.notes_text = "\n".join(f"[{i+1}] {note}" for i, note in enumerate(parser.note_items))

    # Extract scripture references from notes
    for note in parser.note_items:
        for m in _SCRIPTURE_REF_RE.finditer(note):
            ref = m.group(1).strip()
            if ref and ref not in talk.scripture_refs:
                talk.scripture_refs.append(ref)

    # Source URL from extraction-info
    for part in parser.extraction_parts:
        if part.startswith("http"):
            talk.source_url = part
            break

    return talk
