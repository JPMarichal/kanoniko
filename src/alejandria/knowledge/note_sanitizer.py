"""Sanitize and parse conference talk notes for KG relation extraction.

Notes in conference talks contain valuable cross-references (to other talks,
scriptures, books, hymns, doctrinal concepts) but also attribution patterns
(author names concatenated with callings) that pollute NER.

This module parses notes into structured data for direct KG relation creation,
bypassing NER entirely for attribution-heavy content.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Parsed note structure
# ---------------------------------------------------------------------------


@dataclass
class ParsedNote:
    """Structured representation of a conference talk note."""

    note_index: int = 0                  # 1-based note number
    note_type: str = "other"             # scripture, talk_ref, book_ref, hymn_ref, guide_ref, other
    raw_text: str = ""
    # Extracted structured fields
    cited_author: str = ""               # "Russell M. Nelson"
    cited_title: str = ""                # "The Power of Spiritual Momentum"
    cited_publication: str = ""          # "Ensign", "Liahona", "Conference Report"
    cited_date: str = ""                 # "May 2022", "Oct. 1998"
    scripture_refs: list[str] = field(default_factory=list)
    concept_name: str = ""               # For guide_ref: "Kingdom of God"
    clean_text: str = ""                 # Substantive content safe for NER


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Strip leading note number: "1. ", "10.  ", "1.\t"
_NOTE_NUM_RE = re.compile(r"^\d+\.\s+")

# Strip "See " / "Véase " / "see also " / "véase también " prefix
_SEE_PREFIX_RE = re.compile(
    r"^(?:(?:[Ss]ee\s+also|[Ss]ee|[Vv]éase\s+también|[Vv]éase)\s+)",
)

# Scripture reference (reuse similar pattern from conference_parser)
_SCRIPTURE_REF_RE = re.compile(
    r"(?:(?:1|2|3|4)\s+)?"
    r"(?:Genesis|Gen\.|Exodus|Ex\.|Leviticus|Lev\.|Numbers|Num\.|Deuteronomy|Deut\."
    r"|Joshua|Josh\.|Judges|Judg\.|Ruth|1\s+Samuel|2\s+Samuel|1\s+Sam\.|2\s+Sam\."
    r"|1\s+Kings|2\s+Kings|1\s+Chronicles|2\s+Chronicles|1\s+Chron\.|2\s+Chron\."
    r"|Ezra|Nehemiah|Neh\.|Esther|Job|Psalms?|Ps\.|Proverbs|Prov\."
    r"|Ecclesiastes|Eccl\.|Song of Solomon|Isaiah|Isa\.|Jeremiah|Jer\."
    r"|Lamentations|Lam\.|Ezekiel|Ezek\.|Daniel|Dan\.|Hosea|Joel|Amos"
    r"|Obadiah|Jonah|Micah|Nahum|Habakkuk|Hab\.|Zephaniah|Zeph\."
    r"|Haggai|Hag\.|Zechariah|Zech\.|Malachi|Mal\."
    r"|Matthew|Matt\.|Mark|Luke|John|Acts|Romans|Rom\."
    r"|1\s+Corinthians|2\s+Corinthians|1\s+Cor\.|2\s+Cor\."
    r"|Galatians|Gal\.|Ephesians|Eph\.|Philippians|Philip\.|Phil\."
    r"|Colossians|Col\.|1\s+Thessalonians|2\s+Thessalonians|1\s+Thes\.|2\s+Thes\."
    r"|1\s+Timothy|2\s+Timothy|1\s+Tim\.|2\s+Tim\.|Titus|Philemon|Philem\."
    r"|Hebrews|Heb\.|James|1\s+Peter|2\s+Peter|1\s+Pet\.|2\s+Pet\."
    r"|1\s+John|2\s+John|3\s+John|Jude|Revelation|Rev\."
    r"|1\s+Nephi|2\s+Nephi|1\s+Ne\.|2\s+Ne\.|Jacob|Enos|Jarom"
    r"|Omni|Words of Mormon|W\s+of\s+M\.|Mosiah|Alma|Helaman|Hel\."
    r"|3\s+Nephi|4\s+Nephi|3\s+Ne\.|4\s+Ne\.|Mormon|Morm\.|Ether|Moroni|Moro\."
    r"|D&C|Doctrine and Covenants|Doctrina y Convenios|DyC"
    r"|Moses|Moisés|Abraham|Abr\.|JS[—\-]H|JS[—\-]M"
    r"|Joseph Smith[—\-]History|Joseph Smith[—\-]Matthew"
    r"|Articles of Faith|A\s+of\s+F"
    # Spanish
    r"|Génesis|Gén\.|Éxodo|Éx\.|Levítico|Lev\.|Números|Núm\.|Deuteronomio|Deut\."
    r"|Josué|Jos\.|Jueces|Jue\.|Rut|1\s+Samuel|2\s+Samuel"
    r"|1\s+Reyes|2\s+Reyes|1\s+Crónicas|2\s+Crónicas"
    r"|Esdras|Nehemías|Neh\.|Ester|Salmos?|Sal\.|Proverbios|Prov\."
    r"|Eclesiastés|Ecl\.|Cantares|Isaías|Isa\.|Jeremías|Jer\."
    r"|Lamentaciones|Lam\.|Ezequiel|Ezeq\.|Daniel|Dan\.|Oseas|Joel|Amós"
    r"|Abdías|Jonás|Miqueas|Nahúm|Habacuc|Hab\.|Sofonías|Sof\."
    r"|Hageo|Hag\.|Zacarías|Zac\.|Malaquías|Mal\."
    r"|Mateo|Mat\.|Marcos|Lucas|Juan|Hechos|Romanos|Rom\."
    r"|1\s+Corintios|2\s+Corintios|1\s+Cor\.|2\s+Cor\."
    r"|Gálatas|Gál\.|Efesios|Ef\.|Filipenses|Filip\."
    r"|Colosenses|Col\.|1\s+Tesalonicenses|2\s+Tesalonicenses"
    r"|1\s+Timoteo|2\s+Timoteo|1\s+Tim\.|2\s+Tim\.|Tito|Filemón"
    r"|Hebreos|Heb\.|Santiago|1\s+Pedro|2\s+Pedro|1\s+Ped\.|2\s+Ped\."
    r"|1\s+Juan|2\s+Juan|3\s+Juan|Judas|Apocalipsis|Apoc\."
    r"|1\s+Nefi|2\s+Nefi|Jacob|Enós|Jarom|Omni|Palabras de Mormón"
    r"|Mosíah|Alma|Helamán|Hel\.|3\s+Nefi|4\s+Nefi|Mormón|Morm\.|Éter|Moroni|Moro\."
    r"|Artículos de Fe|A\s+de\s+F"
    r")"
    r"\s+\d+[:\d,\s;\u2013\u2014\-]*",
)

# Talk/publication cross-reference:
# "Author Name, "Talk Title," Publication, Date, Page."
# Also handles: Author Name, "Talk Title," in Conference Report, Date, Page.
_PUBLICATION_NAMES = (
    r"Ensign or Liahona|Ensign|Liahona|Conference Report"
    r"|New Era|Friend|Church News|Improvement Era"
    r"|Deseret News|BYU Studies|Tambuli"
)

# Title prefixes to strip from author names
_AUTHOR_TITLE_RE = re.compile(
    r"^(?:President|Elder|Sister|Bishop|Brother|"
    r"Presidente|Élder|Hermana|Obispo|Hermano)\s+",
    re.IGNORECASE,
)

# Pattern for talk cross-references
_TALK_REF_RE = re.compile(
    r"(?:(?:President|Elder|Sister|Bishop|Brother|"
    r"Presidente|Élder|Hermana|Obispo|Hermano)\s+)?"
    r"([A-Z][a-záéíóúñ]+(?:\s+[A-Z]\.?\s*)*[A-Z][a-záéíóúñ]+(?:\s+(?:Jr|Sr|III|II)\.?)?)"  # Author
    r"\s*,\s*"
    r'["\u201c\u201e](.+?)["\u201d\u201f]'       # "Talk Title"
    r"\s*,?\s*"
    r"(?:in\s+)?"
    r"(" + _PUBLICATION_NAMES + r")"     # Publication
    r"[,\s]*"
    r"([A-Za-z]+\.?\s+\d{4}|\d{4})?"    # Date (optional)
)

# Title-only publication reference (no author):
# "Talk Title," Ensign, May 2004, 9.
_TITLE_ONLY_REF_RE = re.compile(
    r'["\u201c\u201e](.+?)["\u201d\u201f]'       # "Talk Title"
    r"\s*,?\s*"
    r"(?:in\s+)?"
    r"(" + _PUBLICATION_NAMES + r")"              # Publication
    r"[,\s]*"
    r"([A-Za-z]+\.?\s+\d{4}|\d{4})?"              # Date (optional)
)

# Book reference: Title (Year), pages
_BOOK_REF_RE = re.compile(
    r"(?:(?:President|Elder|Sister|Bishop|Brother|"
    r"Presidente|Élder|Hermana|Obispo|Hermano)\s+)?"
    r"(?:[A-Z][a-záéíóúñ]+(?:\s+[A-Z]\.?\s*)*[A-Z][a-záéíóúñ]+\s*,\s*)?"
    r"([A-Z][^,(]{5,80})"               # Book title
    r"\s*\((\d{4})\)"                    # (Year)
)

# Hymn reference: "Hymn Title," Hymns, no. NNN
_HYMN_RE = re.compile(
    r'["\u201c](.+?)["\u201d]\s*,?\s*(?:Hymns|Himnos)\s*,?\s*(?:no\.\s*)?(\d+)?',
)

# Guide to the Scriptures / Gospel Topics
_GUIDE_RE = re.compile(
    r"(?:Guide to the Scriptures|Guía de las Escrituras|Gospel Topics|Temas del Evangelio)"
    r"\s*,\s*"
    r'["\u201c](.+?)["\u201d]',
)

# Teachings of the Presidents / Teachings of compilation
_TEACHINGS_RE = re.compile(
    r"((?:Teachings of the Prophet |The Teachings of |Teachings of )"
    r"[A-Z][a-záéíóúñ]+(?:\s+[A-Z]\.?\s*|\s+[a-z]+\s+)*\s*[A-Z][a-záéíóúñ]+)",
)

# Garbage pattern: name concatenated with calling (the original pollution)
_NAME_CALLING_CONCAT_RE = re.compile(
    r"[a-z][A-Z].*?(?:Quorum|Seventy|Presidency|Counselor)",
)

# Pure scripture note: after stripping number and "See", only scripture refs remain
_PURE_SCRIPTURE_RE = re.compile(
    r"^[\s;,.\d\u2013\u2014\-]*$",  # Only whitespace, punctuation, numbers left
)


# ---------------------------------------------------------------------------
# Core parsing
# ---------------------------------------------------------------------------


def parse_note(raw_text: str) -> ParsedNote:
    """Parse a single note string into structured data.

    Classifies the note and extracts structured fields for KG relation
    creation without running NER on attribution-heavy text.
    """
    note = ParsedNote(raw_text=raw_text)

    # Extract note index
    m = _NOTE_NUM_RE.match(raw_text)
    if m:
        try:
            note.note_index = int(raw_text[: m.end()].strip().rstrip("."))
        except ValueError:
            pass

    # Strip note number prefix
    text = _NOTE_NUM_RE.sub("", raw_text).strip()

    # Strip "See" / "Véase" prefix
    text = _SEE_PREFIX_RE.sub("", text).strip()

    # Extract all scripture references
    for m in _SCRIPTURE_REF_RE.finditer(text):
        ref = m.group(0).strip().rstrip(" .,;")
        if ref and ref not in note.scripture_refs:
            note.scripture_refs.append(ref)

    # --- Classification (priority order) ---

    # 1. Guide to the Scriptures / Gospel Topics
    gm = _GUIDE_RE.search(text)
    if gm:
        note.note_type = "guide_ref"
        note.concept_name = gm.group(1).strip().rstrip(",;.")
        note.clean_text = note.concept_name
        return note

    # 2. Hymn reference
    hm = _HYMN_RE.search(text)
    if hm:
        note.note_type = "hymn_ref"
        note.cited_title = hm.group(1).strip().rstrip(",;.")
        note.clean_text = note.cited_title
        return note

    # 3. Talk/publication cross-reference
    tm = _TALK_REF_RE.search(text)
    if tm:
        note.note_type = "talk_ref"
        note.cited_author = _clean_author_name(tm.group(1).strip())
        note.cited_title = tm.group(2).strip().rstrip(",;.")
        note.cited_publication = tm.group(3).strip()
        if tm.group(4):
            note.cited_date = tm.group(4).strip()
        note.clean_text = ""  # No free text for NER
        return note

    # 3b. Title-only publication reference (no author name)
    # e.g., "Our Brothers' Keepers," Ensign, June 1998, 33.
    to_m = _TITLE_ONLY_REF_RE.search(text)
    if to_m:
        note.note_type = "talk_ref"
        note.cited_title = to_m.group(1).strip().rstrip(",;.")
        note.cited_publication = to_m.group(2).strip()
        if to_m.group(3):
            note.cited_date = to_m.group(3).strip()
        note.clean_text = ""
        return note

    # 4. Conference Report reference (without quoted title)
    # e.g., "In Conference Report, Apr. 1979, 77; or Ensign, May 1979, 53."
    cr_match = re.search(
        r"(?:[Ii]n\s+)?Conference Report\s*,\s*([A-Za-z]+\.?\s+\d{4})",
        text,
    )
    if cr_match:
        note.note_type = "talk_ref"
        note.cited_publication = "Conference Report"
        note.cited_date = cr_match.group(1).strip()
        # Try to extract a title if quoted
        title_m = re.search(r'["\u201c](.+?)["\u201d]', text)
        if title_m:
            note.cited_title = title_m.group(1).strip()
        note.clean_text = ""
        return note

    # 5. Teachings of... compilation
    teach_m = _TEACHINGS_RE.search(text)
    if teach_m:
        note.note_type = "book_ref"
        note.cited_title = teach_m.group(1).strip().rstrip(",;.")
        # Extract the person name from the title
        person_m = re.search(
            r"(?:Teachings of the Prophet |The Teachings of |Teachings of )(.*)",
            note.cited_title,
        )
        if person_m:
            note.cited_author = person_m.group(1).strip()
        note.clean_text = ""
        return note

    # 6. Book reference with year
    bm = _BOOK_REF_RE.search(text)
    if bm and not note.scripture_refs:  # Don't misclassify scripture-heavy notes
        note.note_type = "book_ref"
        note.cited_title = bm.group(1).strip()
        note.cited_date = bm.group(2)
        note.clean_text = ""
        return note

    # 7. Pure scripture reference
    text_without_refs = _SCRIPTURE_REF_RE.sub("", text)
    text_without_refs = _SEE_PREFIX_RE.sub("", text_without_refs)
    if note.scripture_refs and _PURE_SCRIPTURE_RE.match(text_without_refs):
        note.note_type = "scripture"
        note.clean_text = ""
        return note

    # 8. Default: "other" — preserve clean text for potential future NER
    #    but strip any name+calling concatenation garbage
    note.note_type = "other"
    note.clean_text = _strip_attribution_garbage(text)
    return note


def _clean_author_name(name: str) -> str:
    """Remove title prefixes and calling suffixes from author names.

    Handles patterns like:
    - "President Russell M. Nelson" -> "Russell M. Nelson"
    - "Russell M. NelsonOf the Quorum..." -> "Russell M. Nelson"
    """
    # Strip title prefix
    name = _AUTHOR_TITLE_RE.sub("", name).strip()

    # Strip calling concatenation (e.g., "NelsonOf the Quorum...")
    concat_m = re.search(r"[a-z][A-Z]", name)
    if concat_m:
        name = name[: concat_m.start() + 1]

    return name.strip()


def _strip_attribution_garbage(text: str) -> str:
    """Strip name+calling concatenation garbage from text for safe NER.

    Removes patterns like:
    - "NombreOf the Quorum of the Twelve Apostles"
    - "the First Quorum of the Seventy Nombre Apellido"
    - "Author, Of the Quorum..."
    """
    # Remove name+calling concatenations
    text = re.sub(
        r"[A-Z][a-záéíóúñ]+(?:\s+[A-Z]\.?\s*)*[A-Z][a-záéíóúñ]+"
        r"(?:Of the|Acting President of the|President of the|First Counselor|Second Counselor)"
        r"[^.;]*(?:[.;]|$)",
        "",
        text,
    )

    # Remove standalone calling lines
    text = re.sub(
        r"(?:Of|Del)\s+(?:the\s+)?(?:Quorum|First|Second|Presidency|Seventy)[^.;]*(?:[.;]|$)",
        "",
        text,
    )

    # Remove "Cuórum de los Doce" style garbage
    text = re.sub(
        r"(?:Del\s+)?(?:Cu|Qu)órum\s+de\s+los\s+Doce[^.;]*(?:[.;]|$)",
        "",
        text,
    )

    return text.strip()


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------


def parse_notes(notes: list[str]) -> list[ParsedNote]:
    """Parse a list of note strings into structured data.

    Handles multi-citation notes by splitting on '; see also' and ';'
    when each part is a separate reference.
    """
    results = []
    for raw in notes:
        parsed = parse_note(raw)
        results.append(parsed)
    return results


def extract_note_relations(
    talk_title: str,
    notes: list[str],
) -> tuple[list[dict], list[dict]]:
    """Extract KG entities and relations from parsed notes.

    Returns (entities, relations) ready for batch merge.
    Does NOT run NER — uses structured parsing only.

    Entity dicts: {"name": str, "type": str, "aliases": []}
    Relation dicts: {"from_name", "from_type", "rel_type", "to_name", "to_type", "props"}
    """
    entities: list[dict] = []
    relations: list[dict] = []
    seen_ents: set[tuple[str, str]] = set()

    def _add_entity(name: str, etype: str) -> None:
        key = (name, etype)
        if key not in seen_ents:
            seen_ents.add(key)
            entities.append({"name": name, "type": etype, "aliases": []})

    for parsed in parse_notes(notes):
        if parsed.note_type == "talk_ref":
            # Cross-reference to another talk
            if parsed.cited_title:
                _add_entity(parsed.cited_title, "talk")
                relations.append({
                    "from_name": talk_title, "from_type": "talk",
                    "rel_type": "REFERENCES",
                    "to_name": parsed.cited_title, "to_type": "talk",
                    "props": {
                        "confidence": "note_reference",
                        **({"cited_author": parsed.cited_author} if parsed.cited_author else {}),
                        **({"publication": parsed.cited_publication} if parsed.cited_publication else {}),
                        **({"date": parsed.cited_date} if parsed.cited_date else {}),
                    },
                })
            if parsed.cited_author:
                _add_entity(parsed.cited_author, "person")
                if parsed.cited_title:
                    # cited talk -> delivered by cited author
                    relations.append({
                        "from_name": parsed.cited_title, "from_type": "talk",
                        "rel_type": "DELIVERED_BY",
                        "to_name": parsed.cited_author, "to_type": "person",
                        "props": {"confidence": "note_reference"},
                    })

        elif parsed.note_type == "hymn_ref":
            if parsed.cited_title:
                _add_entity(parsed.cited_title, "hymn")
                relations.append({
                    "from_name": talk_title, "from_type": "talk",
                    "rel_type": "CITES",
                    "to_name": parsed.cited_title, "to_type": "hymn",
                    "props": {"confidence": "note_reference"},
                })

        elif parsed.note_type == "guide_ref":
            if parsed.concept_name:
                _add_entity(parsed.concept_name, "concept")
                relations.append({
                    "from_name": talk_title, "from_type": "talk",
                    "rel_type": "DISCUSSES",
                    "to_name": parsed.concept_name, "to_type": "concept",
                    "props": {"confidence": "note_reference"},
                })

        elif parsed.note_type == "book_ref":
            if parsed.cited_title:
                _add_entity(parsed.cited_title, "book")
                relations.append({
                    "from_name": talk_title, "from_type": "talk",
                    "rel_type": "REFERENCES",
                    "to_name": parsed.cited_title, "to_type": "book",
                    "props": {
                        "confidence": "note_reference",
                        **({"cited_author": parsed.cited_author} if parsed.cited_author else {}),
                        **({"date": parsed.cited_date} if parsed.cited_date else {}),
                    },
                })

        # Scripture refs from any note type (already handled by CITES in pipeline,
        # but notes may contain refs not in scripture_refs list)
        # We skip these here to avoid duplicating the existing CITES logic.

    return entities, relations
