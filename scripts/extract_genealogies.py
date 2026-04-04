#!/usr/bin/env python3
from __future__ import annotations

"""P10 Phase 1: Extract genealogical relations from formal scripture chapters.

Reads structured genealogy chapters (Genesis 5, 10, 11, Matthew 1, Luke 3,
1 Chronicles 1-9, Ether 1, etc.), applies regex-based extraction, resolves
names against the entity gazetteer, and outputs a JSON file compatible with
the existing load_curated_relations.py infrastructure.

Usage:
    python scripts/extract_genealogies.py                    # full extraction
    python scripts/extract_genealogies.py --dry-run          # report only
    python scripts/extract_genealogies.py --chapters gen5    # single chapter
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
ENTITIES_PATH = ROOT / "src" / "alejandria" / "knowledge" / "gazetteers" / "entities.json"
EXISTING_RELS_PATH = ROOT / "src" / "alejandria" / "knowledge" / "gazetteers" / "relations.json"
DEFAULT_OUTPUT = ROOT / "data" / "genealogy_relations.json"
NEW_ENTITIES_OUTPUT = ROOT / "data" / "genealogy_new_entities.txt"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Relation:
    from_name: str
    to_name: str
    rel_type: str  # FATHER_OF, MOTHER_OF, SPOUSE_OF, DESCENDANT_OF, ORDAINED_BY
    source_ref: str
    from_type: str = "person"
    to_type: str = "person"

    @property
    def key(self) -> tuple:
        return (self.from_name, self.rel_type, self.to_name)


@dataclass
class ChapterResult:
    chapter_id: str
    relations: list[Relation] = field(default_factory=list)
    new_entities: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Chapter registry
# ---------------------------------------------------------------------------

@dataclass
class ChapterSpec:
    chapter_id: str
    ref_prefix_en: str
    ref_prefix_es: str
    vol: str
    slug_en: str
    slug_es: str
    chapters: list[int]
    pattern: str  # begat, begat_dense, sons_of, son_of_reverse, narrative
    verse_range: tuple[int, int] | None = None  # optional verse filter


CHAPTER_REGISTRY: list[ChapterSpec] = [
    # Group A: "X begat Y" linear
    ChapterSpec("gen5", "Genesis", "Génesis", "ot", "genesis", "genesis", [5], "begat"),
    ChapterSpec("gen11", "Genesis", "Génesis", "ot", "genesis", "genesis", [11], "begat", (10, 32)),
    ChapterSpec("gen25", "Genesis", "Génesis", "ot", "genesis", "genesis", [25], "begat_narrative"),
    ChapterSpec("gen46", "Genesis", "Génesis", "ot", "genesis", "genesis", [46], "sons_of"),
    ChapterSpec("moses6", "Moses", "Moisés", "pgp", "moses", "moises", [6], "begat"),
    ChapterSpec("moses8", "Moses", "Moisés", "pgp", "moses", "moises", [8], "begat"),
    ChapterSpec("ruth4", "Ruth", "Rut", "ot", "ruth", "rut", [4], "begat", (18, 22)),

    # Group A-dense: Matthew 1
    ChapterSpec("matt1", "Matthew", "Mateo", "nt", "matthew", "mateo", [1], "begat_dense", (1, 16)),

    # Group B: "The sons of X" lists
    ChapterSpec("gen10", "Genesis", "Génesis", "ot", "genesis", "genesis", [10], "sons_of"),
    ChapterSpec("gen36", "Genesis", "Génesis", "ot", "genesis", "genesis", [36], "sons_of"),
    ChapterSpec("1chr1", "1 Chronicles", "1 Crónicas", "ot", "1-chronicles", "1-cronicas", [1], "chronicles"),
    ChapterSpec("1chr2", "1 Chronicles", "1 Crónicas", "ot", "1-chronicles", "1-cronicas", [2], "sons_of"),
    ChapterSpec("1chr3a", "1 Chronicles", "1 Crónicas", "ot", "1-chronicles", "1-cronicas", [3], "narrative", (1, 9)),
    ChapterSpec("1chr3", "1 Chronicles", "1 Crónicas", "ot", "1-chronicles", "1-cronicas", [3], "sons_of"),
    ChapterSpec("1chr4", "1 Chronicles", "1 Crónicas", "ot", "1-chronicles", "1-cronicas", [4], "sons_of"),
    ChapterSpec("1chr5", "1 Chronicles", "1 Crónicas", "ot", "1-chronicles", "1-cronicas", [5], "sons_of"),
    ChapterSpec("1chr6", "1 Chronicles", "1 Crónicas", "ot", "1-chronicles", "1-cronicas", [6], "sons_of"),
    ChapterSpec("1chr7", "1 Chronicles", "1 Crónicas", "ot", "1-chronicles", "1-cronicas", [7], "sons_of"),
    ChapterSpec("1chr8", "1 Chronicles", "1 Crónicas", "ot", "1-chronicles", "1-cronicas", [8], "sons_of"),
    ChapterSpec("1chr9", "1 Chronicles", "1 Crónicas", "ot", "1-chronicles", "1-cronicas", [9], "sons_of"),

    # Group C: "was the son of" reverse
    ChapterSpec("luke3", "Luke", "Lucas", "nt", "luke", "lucas", [3], "son_of_reverse", (23, 38)),
    ChapterSpec("ether1", "Ether", "Éter", "bom", "ether", "eter", [1], "son_of_reverse", (6, 32)),

    # Group D: Narrative mixed (Phase 1)
    ChapterSpec("gen4", "Genesis", "Génesis", "ot", "genesis", "genesis", [4], "narrative"),

    # ===================================================================
    # PHASE 2: Narrative genealogies
    # ===================================================================

    # --- Genesis Patriarchs ---
    ChapterSpec("gen16", "Genesis", "Génesis", "ot", "genesis", "genesis", [16], "narrative"),
    ChapterSpec("gen17", "Genesis", "Génesis", "ot", "genesis", "genesis", [17], "narrative"),
    ChapterSpec("gen19", "Genesis", "Génesis", "ot", "genesis", "genesis", [19], "narrative", (30, 38)),
    ChapterSpec("gen21", "Genesis", "Génesis", "ot", "genesis", "genesis", [21], "narrative"),
    ChapterSpec("gen22", "Genesis", "Génesis", "ot", "genesis", "genesis", [22], "narrative", (20, 24)),
    ChapterSpec("gen24", "Genesis", "Génesis", "ot", "genesis", "genesis", [24], "narrative"),
    ChapterSpec("gen28", "Genesis", "Génesis", "ot", "genesis", "genesis", [28], "narrative"),
    ChapterSpec("gen29", "Genesis", "Génesis", "ot", "genesis", "genesis", [29], "narrative"),
    ChapterSpec("gen30", "Genesis", "Génesis", "ot", "genesis", "genesis", [30], "narrative"),
    ChapterSpec("gen34", "Genesis", "Génesis", "ot", "genesis", "genesis", [34], "narrative", (1, 6)),
    ChapterSpec("gen35", "Genesis", "Génesis", "ot", "genesis", "genesis", [35], "begat_narrative", (16, 29)),
    ChapterSpec("gen38", "Genesis", "Génesis", "ot", "genesis", "genesis", [38], "narrative"),
    ChapterSpec("gen41", "Genesis", "Génesis", "ot", "genesis", "genesis", [41], "narrative", (45, 52)),

    # --- Exodus / Numbers ---
    ChapterSpec("exod2", "Exodus", "Éxodo", "ot", "exodus", "exodo", [2], "narrative"),
    ChapterSpec("exod6", "Exodus", "Éxodo", "ot", "exodus", "exodo", [6], "sons_of", (14, 27)),
    ChapterSpec("num26", "Numbers", "Números", "ot", "numbers", "numeros", [26], "sons_of"),

    # --- Judges ---
    ChapterSpec("judg11", "Judges", "Jueces", "ot", "judges", "jueces", [11], "narrative", (1, 2)),
    ChapterSpec("judg13", "Judges", "Jueces", "ot", "judges", "jueces", [13], "narrative", (1, 24)),

    # --- 1 Samuel ---
    ChapterSpec("1sam1", "1 Samuel", "1 Samuel", "ot", "1-samuel", "1-samuel", [1], "narrative"),
    ChapterSpec("1sam9", "1 Samuel", "1 Samuel", "ot", "1-samuel", "1-samuel", [9], "narrative", (1, 2)),
    ChapterSpec("1sam14", "1 Samuel", "1 Samuel", "ot", "1-samuel", "1-samuel", [14], "narrative", (49, 51)),
    ChapterSpec("1sam16", "1 Samuel", "1 Samuel", "ot", "1-samuel", "1-samuel", [16], "narrative"),
    ChapterSpec("1sam17", "1 Samuel", "1 Samuel", "ot", "1-samuel", "1-samuel", [17], "narrative", (12, 14)),
    ChapterSpec("1sam18", "1 Samuel", "1 Samuel", "ot", "1-samuel", "1-samuel", [18], "narrative", (17, 28)),
    ChapterSpec("1sam25", "1 Samuel", "1 Samuel", "ot", "1-samuel", "1-samuel", [25], "narrative", (1, 44)),

    # --- 2 Samuel ---
    ChapterSpec("2sam3", "2 Samuel", "2 Samuel", "ot", "2-samuel", "2-samuel", [3], "narrative", (2, 5)),
    ChapterSpec("2sam5", "2 Samuel", "2 Samuel", "ot", "2-samuel", "2-samuel", [5], "narrative", (13, 16)),
    ChapterSpec("2sam11", "2 Samuel", "2 Samuel", "ot", "2-samuel", "2-samuel", [11], "narrative", (1, 27)),
    ChapterSpec("2sam13", "2 Samuel", "2 Samuel", "ot", "2-samuel", "2-samuel", [13], "narrative", (1, 5)),

    # --- 1 Kings ---
    ChapterSpec("1kgs1", "1 Kings", "1 Reyes", "ot", "1-kings", "1-reyes", [1], "narrative", (5, 13)),
    ChapterSpec("1kgs11", "1 Kings", "1 Reyes", "ot", "1-kings", "1-reyes", [11], "narrative", (26, 43)),
    ChapterSpec("1kgs14", "1 Kings", "1 Reyes", "ot", "1-kings", "1-reyes", [14], "narrative"),
    ChapterSpec("1kgs16", "1 Kings", "1 Reyes", "ot", "1-kings", "1-reyes", [16], "narrative"),

    # --- 2 Kings ---
    ChapterSpec("2kgs8", "2 Kings", "2 Reyes", "ot", "2-kings", "2-reyes", [8], "narrative", (16, 27)),
    ChapterSpec("2kgs11", "2 Kings", "2 Reyes", "ot", "2-kings", "2-reyes", [11], "narrative", (1, 3)),

    # --- Book of Mormon ---
    ChapterSpec("1ne2", "1 Nephi", "1 Nefi", "bom", "1-nephi", "1-nefi", [2], "narrative", (1, 5)),
    ChapterSpec("1ne7", "1 Nephi", "1 Nefi", "bom", "1-nephi", "1-nefi", [7], "narrative"),
    ChapterSpec("1ne16", "1 Nephi", "1 Nefi", "bom", "1-nephi", "1-nefi", [16], "narrative", (7, 7)),
    ChapterSpec("mosiah7", "Mosiah", "Mosíah", "bom", "mosiah", "mosiah", [7], "son_of_reverse", (9, 13)),
    ChapterSpec("alma10", "Alma", "Alma", "bom", "alma", "alma", [10], "son_of_reverse", (2, 3)),
    ChapterSpec("ether6", "Ether", "Éter", "bom", "ether", "eter", [6], "narrative", (14, 29)),
    ChapterSpec("ether7", "Ether", "Éter", "bom", "ether", "eter", [7], "begat_narrative"),
    ChapterSpec("ether8", "Ether", "Éter", "bom", "ether", "eter", [8], "begat_narrative"),
    ChapterSpec("ether9", "Ether", "Éter", "bom", "ether", "eter", [9], "begat_narrative"),
    ChapterSpec("ether10", "Ether", "Éter", "bom", "ether", "eter", [10], "begat_narrative"),
    ChapterSpec("ether11", "Ether", "Éter", "bom", "ether", "eter", [11], "begat_narrative"),

    # --- Pearl of Great Price ---
    ChapterSpec("abr1", "Abraham", "Abraham", "pgp", "abraham", "abraham", [1], "narrative", (20, 27)),

    # ===================================================================
    # PHASE 3: Exhaustive coverage
    # ===================================================================

    # --- 2 Chronicles royal lineages ---
    ChapterSpec("2chr11", "2 Chronicles", "2 Crónicas", "ot", "2-chronicles", "2-cronicas", [11], "narrative", (18, 23)),
    ChapterSpec("2chr13", "2 Chronicles", "2 Crónicas", "ot", "2-chronicles", "2-cronicas", [13], "narrative", (1, 2)),
    ChapterSpec("2chr21", "2 Chronicles", "2 Crónicas", "ot", "2-chronicles", "2-cronicas", [21], "narrative", (1, 17)),
    ChapterSpec("2chr22", "2 Chronicles", "2 Crónicas", "ot", "2-chronicles", "2-cronicas", [22], "narrative", (1, 12)),
    ChapterSpec("2chr24", "2 Chronicles", "2 Crónicas", "ot", "2-chronicles", "2-cronicas", [24], "narrative", (1, 22)),
    ChapterSpec("2chr26", "2 Chronicles", "2 Crónicas", "ot", "2-chronicles", "2-cronicas", [26], "narrative", (1, 3)),
    ChapterSpec("2chr27", "2 Chronicles", "2 Crónicas", "ot", "2-chronicles", "2-cronicas", [27], "narrative", (1, 9)),
    ChapterSpec("2chr29", "2 Chronicles", "2 Crónicas", "ot", "2-chronicles", "2-cronicas", [29], "narrative", (1, 1)),
    ChapterSpec("2chr33", "2 Chronicles", "2 Crónicas", "ot", "2-chronicles", "2-cronicas", [33], "narrative", (1, 25)),
    ChapterSpec("2chr34", "2 Chronicles", "2 Crónicas", "ot", "2-chronicles", "2-cronicas", [34], "narrative", (1, 22)),
    ChapterSpec("2chr36", "2 Chronicles", "2 Crónicas", "ot", "2-chronicles", "2-cronicas", [36], "narrative", (1, 11)),

    # --- Ezra / Nehemiah ---
    ChapterSpec("ezra7", "Ezra", "Esdras", "ot", "ezra", "esdras", [7], "son_of_reverse", (1, 5)),
    ChapterSpec("neh12", "Nehemiah", "Nehemías", "ot", "nehemiah", "nehemias", [12], "begat_narrative", (10, 35)),

    # --- Prophetic books ---
    ChapterSpec("jer1", "Jeremiah", "Jeremías", "ot", "jeremiah", "jeremias", [1], "narrative", (1, 3)),
    ChapterSpec("ezek1", "Ezekiel", "Ezequiel", "ot", "ezekiel", "ezequiel", [1], "narrative", (1, 3)),
    ChapterSpec("hosea1", "Hosea", "Oseas", "ot", "hosea", "oseas", [1], "narrative", (1, 9)),
    ChapterSpec("isa1", "Isaiah", "Isaías", "ot", "isaiah", "isaias", [1], "narrative", (1, 1)),
    ChapterSpec("jonah1", "Jonah", "Jonás", "ot", "jonah", "jonas", [1], "narrative", (1, 1)),
    ChapterSpec("zeph1", "Zephaniah", "Sofonías", "ot", "zephaniah", "sofonias", [1], "son_of_reverse", (1, 1)),
    ChapterSpec("zech1", "Zechariah", "Zacarías", "ot", "zechariah", "zacarias", [1], "son_of_reverse", (1, 1)),
    ChapterSpec("joel1", "Joel", "Joel", "ot", "joel", "joel", [1], "narrative", (1, 1)),

    # --- NT scattered ---
    ChapterSpec("acts7", "Acts", "Hechos", "nt", "acts", "hechos", [7], "begat_narrative", (8, 29)),
    ChapterSpec("heb11", "Hebrews", "Hebreos", "nt", "hebrews", "hebreos", [11], "narrative", (11, 24)),

    # --- Book of Mormon late ---
    ChapterSpec("4ne1", "4 Nephi", "4 Nefi", "bom", "4-nephi", "4-nefi", [1], "narrative"),
    ChapterSpec("hel2", "Helaman", "Helamán", "bom", "helaman", "helaman", [2], "narrative", (1, 2)),
    ChapterSpec("hel3", "Helaman", "Helamán", "bom", "helaman", "helaman", [3], "narrative"),
    ChapterSpec("mormon1", "Mormon", "Mormón", "bom", "mormon", "mormon", [1], "narrative", (1, 5)),
    ChapterSpec("3ne5", "3 Nephi", "3 Nefi", "bom", "3-nephi", "3-nefi", [5], "narrative", (12, 20)),
    ChapterSpec("moroni9", "Moroni", "Moroni", "bom", "moroni", "moroni", [9], "narrative", (1, 4)),

    # --- D&C ---
    ChapterSpec("dc27", "Doctrine and Covenants", "Doctrina y Convenios", "dc", "sections", "secciones", [27], "narrative", (5, 13)),
    ChapterSpec("dc84", "Doctrine and Covenants", "Doctrina y Convenios", "dc", "sections", "secciones", [84], "priesthood_lineage", (6, 16)),
    ChapterSpec("dc107", "Doctrine and Covenants", "Doctrina y Convenios", "dc", "sections", "secciones", [107], "priesthood_lineage", (40, 53)),
]


# ---------------------------------------------------------------------------
# KJV name map: names in KJV text → canonical gazetteer names
# These are names that appear in formal genealogy chapters but differ from
# the gazetteer canonical form.
# ---------------------------------------------------------------------------

KJV_NAME_MAP: dict[str, str] = {
    # Matthew 1 / Luke 3 KJV names → modern/canonical
    "Judas": "Judah",
    "Phares": "Perez",
    "Esrom": "Hezron",
    "Aram": "Ram",
    "Naasson": "Nahshon",
    "Salmon": "Salmon",
    "Booz": "Boaz",
    "Ozias": "Uzziah",
    "Joatham": "Jotham",
    "Achaz": "Ahaz",
    "Ezekias": "Hezekiah",
    "Manasses": "Manasseh",
    "Josias": "Josiah",
    "Jechonias": "Jeconiah",
    "Salathiel": "Shealtiel",
    "Zorobabel": "Zerubbabel",
    "Roboam": "Rehoboam",
    "Abia": "Abijah",
    "Josaphat": "Jehoshaphat",
    "Thamar": "Tamar",
    "Rachab": "Rahab",
    "Urias": "Uriah",
    # 1 Chronicles name variants
    "Sheth": "Seth",
    "Henoch": "Enoch",
    "Jered": "Jared",
    "Abram": "Abraham",
    "Israel": "Jacob (patriarch)",
    "Jacob": "Jacob (patriarch)",  # In genealogy context, Jacob = patriarch, not BoM
    # Luke 3 additional names
    "Noe": "Noah",
    "Sem": "Shem",
    "Mathusala": "Methuselah",
    "Maleleel": "Mahalaleel",
    "Jose": "Joses",
    "Thara": "Terah",
    "Nachor": "Nahor",
    "Saruch": "Serug",
    "Ragau": "Reu",
    "Phalec": "Peleg",
    "Heber": "Eber",
    "Sala": "Shelah",
    # Phase 2: Judges / Samuel / Kings name variants
    "Ishui": "Ishvi",
    "Melchi-shua": "Malchishua",
    "Abinoam": "Ahinoam",       # wife of Saul (1 Sam 14:50)
    "Joram": "Jehoram",          # shortened form (2 Kings 8)
    "Nebat": "Nebat",            # father of Jeroboam (keep as-is)
    "Ethbaal": "Ethbaal",        # father of Jezebel
    "Chileab": "Chileab",        # son of David (2 Sam 3:3), also called Daniel
    "Zeruah": "Zeruah",          # mother of Jeroboam
    # Phase 2: Genesis patriarchal names
    "Bethuel": "Bethuel",
    "Milcah": "Milcah",
    "Bilhah": "Bilhah",
    "Zilpah": "Zilpah",
    "Asenath": "Asenath",
    "Pharez": "Perez",           # Genesis 38 KJV spelling
    "Zarah": "Zerah",            # Genesis 38 KJV spelling
    # Phase 2: Book of Mormon
    "Zeniff": "Zeniff",
    "Aminadi": "Aminadi",
    "Egyptus": "Egyptus",
    # Phase 3: 2 Chronicles / Prophets / D&C
    "Michaiah": "Micaiah",
    "Maachah": "Maacah",           # 2 Chr 11 — wife of Rehoboam
    "Jehoshabeath": "Jehosheba",   # 2 Chr 22:11 = 2 Kgs 11:2
    "Jehoahaz": "Jehoahaz",
    "Hizkiah": "Hezekiah",        # Zephaniah 1:1 short form
    "Amittai": "Amittai",
    "Beeri": "Beeri",
    "Diblaim": "Diblaim",
    "Buzi": "Buzi",
    "Pethuel": "Pethuel",
    "Cushi": "Cushi",
}

# Gentilicios / peoples — not persons, filter from "sons of" lists
GENTILICS = {
    "Jebusite", "Amorite", "Girgashite", "Hivite", "Arkite",
    "Sinite", "Arvadite", "Zemarite", "Hamathite", "Ludim",
    "Anamim", "Lehabim", "Naphtuhim", "Pathrusim", "Casluhim",
    "Caphthorim", "Philistines",
}

# Words that look like names but aren't — filter from extraction
STOP_NAMES = {
    "And", "Now", "She", "The", "His", "Her", "But", "For", "Then",
    "These", "Which", "All", "Also", "Who", "When", "Where", "Thus",
    "Some", "Many", "Both", "They", "Were", "Was", "Are", "Not",
    "God", "Lord", "So", "He", "It", "Behold", "Because", "Therefore",
    "Son", "Syrian", "Ephrathite", "Ammonitess", "Jezreelitess", "Carmelite",
    "Book", "Spirit", "Holy", "Priesthood", "According", "From", "Unto",
}

# Known place names that leak into genealogical lists
PLACE_NAMES = {
    "Beth-lehem", "Beth-shean", "Dor", "Megiddo", "Taanach", "Lod",
    "Ataroth", "Ono", "Gath", "Gaza", "Aijalon", "Zorah", "Ophrah",
    "Jabez", "Tekoa", "Bethlehem", "Kirjath-jearim",
    # Phase 2: Kings / Samuel context
    "Geshur", "Jezreel", "Samaria", "Hebron", "Tirzah", "Ramah",
    "Carmel", "Gilead", "Gibeah", "Ramathaim-zophim", "Jerusalem",
    "Maon", "Paran", "Zidon", "Baal", "Padan-aram", "Chaldea",
    "Beth-lehem-judah", "Ashtaroth", "Golan", "Tabor", "Zereda",
    # Phase 3: 2 Chronicles / prophetic contexts
    "Anathoth", "Beer-sheba", "Libnah", "Mareshah",
}


# ---------------------------------------------------------------------------
# Entity resolver
# ---------------------------------------------------------------------------

class EntityResolver:
    def __init__(self, entities_path: Path):
        self.canonical: set[str] = set()
        self.alias_map: dict[str, str] = {}
        self._load(entities_path)
        self.unresolved: set[str] = set()

    def _load(self, path: Path) -> None:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for entries in data.values():
            for entry in entries:
                name = entry["name"]
                self.canonical.add(name)
                for alias in entry.get("aliases", []):
                    self.alias_map[alias] = name

    def resolve(self, raw_name: str) -> str | None:
        """Resolve a raw name to its canonical form. Returns None for invalid names."""
        # 0. Filter stopwords and places
        if raw_name in STOP_NAMES or raw_name in PLACE_NAMES:
            return None

        # 1. KJV map
        if raw_name in KJV_NAME_MAP:
            mapped = KJV_NAME_MAP[raw_name]
            if mapped in self.canonical:
                return mapped
            raw_name = mapped

        # 2. Exact match
        if raw_name in self.canonical:
            return raw_name

        # 3. Alias match
        if raw_name in self.alias_map:
            return self.alias_map[raw_name]

        # 4. Unresolved — track and return as-is
        self.unresolved.add(raw_name)
        return raw_name


# ---------------------------------------------------------------------------
# Verse parser
# ---------------------------------------------------------------------------

def parse_verses(text: str, verse_range: tuple[int, int] | None = None) -> list[tuple[int, str]]:
    """Parse verse-numbered text into (verse_num, content) pairs."""
    verses = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(\d+)\s+(.*)", line)
        if m:
            vnum = int(m.group(1))
            content = m.group(2)
            if verse_range and (vnum < verse_range[0] or vnum > verse_range[1]):
                continue
            verses.append((vnum, content))
    return verses


# ---------------------------------------------------------------------------
# Pattern extractors
# ---------------------------------------------------------------------------

# Reusable name pattern
NAME_EN = r"([A-Z][a-z]+(?:-[A-Z]?[a-z]+)*)"
NAME_ES = r"([A-Z][a-záéíóúñ]+(?:-[A-Z]?[a-záéíóúñ]+)*)"


def _add(rels: list[Relation], from_name: str | None, to_name: str | None,
         rel_type: str, ref: str, dedup: bool = True) -> None:
    """Helper: add relation only if both names resolved and not duplicate."""
    if not from_name or not to_name or from_name == to_name:
        return
    if dedup and any(r.from_name == from_name and r.to_name == to_name and r.rel_type == rel_type for r in rels):
        return
    rels.append(Relation(from_name, to_name, rel_type, ref))


def extract_begat(verses: list[tuple[int, str]], ref_prefix: str, resolver: EntityResolver) -> list[Relation]:
    """Pattern A: 'X begat Y' linear chains.

    ref_prefix should already include chapter, e.g., 'Genesis 5'.
    Refs will be 'Genesis 5:3', 'Genesis 5:6', etc.
    """
    rels = []
    re_begat = re.compile(rf"{NAME_EN}\s+begat\s+{NAME_EN}")
    re_begat_multi = re.compile(rf"begat\s+(.+?)(?:\.|;|$)")
    re_called = re.compile(r"called (?:(?:she |he )?his|her) name\s+" + NAME_EN)

    for vnum, text in verses:
        ref = f"{ref_prefix}:{vnum}"

        # Direct "X begat Y" matches
        for m in re_begat.finditer(text):
            father = resolver.resolve(m.group(1))
            child = resolver.resolve(m.group(2))
            _add(rels, father, child, "FATHER_OF", ref)

        # "begat a son... called his name X" (Gen 5:3, 5:28-29)
        if "begat a son" in text or "begat a daughter" in text:
            m_called = re_called.search(text)
            if m_called:
                child = resolver.resolve(m_called.group(1))
                # Find the subject (the person who begat)
                m_subj = re.match(rf".*?{NAME_EN}\s+(?:lived|begat)", text)
                if m_subj:
                    father = resolver.resolve(m_subj.group(1))
                    _add(rels, father, child, "FATHER_OF", ref)

        # Multi-child: "Noah begat Shem, Ham, and Japheth"
        for m in re_begat_multi.finditer(text):
            child_text = m.group(1).strip()
            if "," in child_text or " and " in child_text:
                start = m.start()
                pre = text[:start]
                m_father = re.search(rf"{NAME_EN}\s*$", pre)
                if m_father:
                    father = resolver.resolve(m_father.group(1))
                    children = split_name_list(child_text)
                    for c in children:
                        child = resolver.resolve(c)
                        _add(rels, father, child, "FATHER_OF", ref)

    return rels


def extract_begat_dense(verses: list[tuple[int, str]], ref_prefix: str, resolver: EntityResolver) -> list[Relation]:
    """Pattern A-dense: Matthew 1 dense begat chains with maternal notes."""
    rels = []
    re_begat = re.compile(rf"{NAME_EN}\s+begat\s+{NAME_EN}")
    re_begat_of = re.compile(rf"{NAME_EN}\s+begat\s+{NAME_EN}\s+of\s+{NAME_EN}")
    re_begat_husband = re.compile(rf"{NAME_EN}\s+begat\s+{NAME_EN}\s+the\s+husband\s+of\s+{NAME_EN}")

    for vnum, text in verses:
        ref = f"{ref_prefix} 1:{vnum}"

        # Special: "Jacob begat Joseph the husband of Mary"
        m_husband = re_begat_husband.search(text)
        if m_husband:
            father = resolver.resolve(m_husband.group(1))
            child = resolver.resolve(m_husband.group(2))
            wife = resolver.resolve(m_husband.group(3))
            _add(rels, father, child, "FATHER_OF", ref)
            _add(rels, child, wife, "SPOUSE_OF", ref)
            if "was born" in text:
                m_born = re.search(r"was born\s+" + NAME_EN, text)
                if m_born:
                    child_of_mary = resolver.resolve(m_born.group(1))
                    _add(rels, wife, child_of_mary, "MOTHER_OF", ref)
            continue

        # "X begat Y of Z" — mother noted
        for m in re_begat_of.finditer(text):
            father = resolver.resolve(m.group(1))
            child = resolver.resolve(m.group(2))
            mother = resolver.resolve(m.group(3))
            _add(rels, father, child, "FATHER_OF", ref)
            _add(rels, mother, child, "MOTHER_OF", ref)

        # Standard "X begat Y"
        for m in re_begat.finditer(text):
            father = resolver.resolve(m.group(1))
            child = resolver.resolve(m.group(2))
            _add(rels, father, child, "FATHER_OF", ref)

    return rels


def extract_sons_of(verses: list[tuple[int, str]], ref_prefix: str, resolver: EntityResolver, ch: int) -> list[Relation]:
    """Pattern B: 'The sons of X; A, B, C' lists plus embedded begat."""
    rels = []
    re_sons = re.compile(rf"[Tt]he (?:sons|children) of {NAME_EN}(?:[;:,]| were)\s*(.+?)(?:\.|$)")
    re_begat = re.compile(rf"{NAME_EN}\s+begat\s+{NAME_EN}")
    re_bare = re.compile(rf"(?:she )?bare\s+(.+?)(?:\.|;|$)")
    re_son_of = re.compile(rf"{NAME_EN}\s+the\s+son\s+of\s+{NAME_EN}")
    re_firstborn = re.compile(rf"[Tt]he firstborn of {NAME_EN},?\s+{NAME_EN}")

    for vnum, text in verses:
        ref = f"{ref_prefix} {ch}:{vnum}"

        # "The sons of X; A, B, C"
        for m in re_sons.finditer(text):
            father = resolver.resolve(m.group(1))
            children_text = m.group(2)
            children = split_name_list(children_text)
            for c in children:
                if c in GENTILICS or c.startswith("the "):
                    continue
                child = resolver.resolve(c)
                _add(rels, father, child, "FATHER_OF", ref)

        # "The firstborn of X, Y"
        for m in re_firstborn.finditer(text):
            father = resolver.resolve(m.group(1))
            child = resolver.resolve(m.group(2))
            _add(rels, father, child, "FATHER_OF", ref)

        # Embedded "X begat Y"
        for m in re_begat.finditer(text):
            father = resolver.resolve(m.group(1))
            child = resolver.resolve(m.group(2))
            _add(rels, father, child, "FATHER_OF", ref)

        # "she bare X, and Y"
        for m in re_bare.finditer(text):
            children_text = m.group(1)
            children = split_name_list(children_text)
            m_mother = re.search(rf"(?:sons|children) of {NAME_EN}", text)
            if not m_mother:
                m_mother = re.search(rf"{NAME_EN}.*?bare", text)
            if m_mother:
                mother_name = resolver.resolve(m_mother.group(1))
                for c in children:
                    if c in GENTILICS:
                        continue
                    child = resolver.resolve(c)
                    _add(rels, mother_name, child, "MOTHER_OF", ref)

        # "X the son of Y"
        for m in re_son_of.finditer(text):
            child = resolver.resolve(m.group(1))
            father = resolver.resolve(m.group(2))
            _add(rels, father, child, "FATHER_OF", ref)

        # "the names of his two daughters" + "the name of the firstborn X"
        if "daughter" in text:
            re_name_of = re.compile(rf"name of the (?:firstborn|younger|elder|other)\s+{NAME_EN}")
            # Find the father context (e.g., "sons of Saul" earlier)
            m_father = re.search(rf"sons of {NAME_EN}", text)
            father = resolver.resolve(m_father.group(1)) if m_father else None
            for m_d in re_name_of.finditer(text):
                daughter = resolver.resolve(m_d.group(1))
                _add(rels, father, daughter, "FATHER_OF", ref)

    return rels


def extract_chronicles_1(verses: list[tuple[int, str]], ref_prefix: str, resolver: EntityResolver) -> list[Relation]:
    """Special handler for 1 Chronicles 1 — mixed patterns including implicit lists."""
    rels = []

    # Verses 1-4: implicit linear chain (Adam, Sheth, Enosh, ...)
    chain_names = []
    for vnum, text in verses:
        if vnum > 4:
            break
        # Extract comma-separated names
        names = re.findall(r"([A-Z][a-z]+(?:-[A-Z]?[a-z]+)*)", text)
        chain_names.extend(names)

    # Create FATHER_OF chain
    for i in range(len(chain_names) - 1):
        father = resolver.resolve(chain_names[i])
        child = resolver.resolve(chain_names[i + 1])
        _add(rels, father, child, "FATHER_OF", f"{ref_prefix} 1:1")

    # Verses 24-27: another implicit chain (Shem, Arphaxad, Shelah, ...)
    chain2_names = []
    for vnum, text in verses:
        if vnum < 24 or vnum > 27:
            continue
        names = re.findall(r"([A-Z][a-z]+(?:-[A-Z]?[a-z]+)*)", text)
        chain2_names.extend(names)

    for i in range(len(chain2_names) - 1):
        father = resolver.resolve(chain2_names[i])
        child = resolver.resolve(chain2_names[i + 1])
        _add(rels, father, child, "FATHER_OF", f"{ref_prefix} 1:24")

    # Verses 5+: standard sons_of + begat patterns
    sons_rels = extract_sons_of(
        [(v, t) for v, t in verses if v >= 5],
        ref_prefix, resolver, 1,
    )

    # Merge avoiding duplicates
    seen = {r.key for r in rels}
    for r in sons_rels:
        if r.key not in seen:
            rels.append(r)
            seen.add(r.key)

    return rels


def extract_son_of_reverse(verses: list[tuple[int, str]], ref_prefix: str, resolver: EntityResolver, ch: int, chapter_id: str) -> list[Relation]:
    """Pattern C: 'was the son of' reverse chains (Luke 3, Ether 1)."""
    rels = []

    if chapter_id == "luke3":
        # Luke 3:23-38 — chain: "the son of Joseph, which was the son of Heli, ..."
        # Collect all names in order (child → ... → Adam)
        chain: list[str] = []
        full_text = " ".join(text for _, text in verses)

        # Start: "the son of Joseph"
        m_start = re.search(r"the son of (\w+)", full_text)
        if m_start:
            chain.append(m_start.group(1))

        # Continue: "which was the son of X"
        for m in re.finditer(r"which was the son of (\w+)", full_text):
            chain.append(m.group(1))

        # Build FATHER_OF pairs: chain[i+1] is father of chain[i]
        for i in range(len(chain) - 1):
            child = resolver.resolve(chain[i])
            father = resolver.resolve(chain[i + 1])
            vnum = 23 + (i // 5)
            if vnum > 38:
                vnum = 38
            _add(rels, father, child, "FATHER_OF", f"{ref_prefix} 3:{vnum}")

        # Add Jesus → Joseph (legal/adoptive father)
        if chain:
            joseph = resolver.resolve(chain[0])
            _add(rels, joseph, "Jesus Christ", "FATHER_OF", f"{ref_prefix} 3:23")

    elif chapter_id == "ether1":
        # Ether 1:6-32 — "X was the son of Y" / "X was a descendant of Y"
        re_son = re.compile(rf"{NAME_EN}\s+was\s+(?:a descendant of|the son of)\s+{NAME_EN}")
        re_son2 = re.compile(rf"who was the son of\s+{NAME_EN}")

        for vnum, text in verses:
            ref = f"{ref_prefix} 1:{vnum}"

            for m in re_son.finditer(text):
                child = resolver.resolve(m.group(1))
                father = resolver.resolve(m.group(2))
                if "descendant" in m.group(0):
                    _add(rels, child, father, "DESCENDANT_OF", ref)
                else:
                    _add(rels, father, child, "FATHER_OF", ref)

            # "who was the son of X" (continuation within same verse, e.g., Ether 1:16, 1:32)
            for m in re_son2.finditer(text):
                father = resolver.resolve(m.group(1))
                m_child = re_son.search(text)
                if m_child:
                    parent_of_prev = resolver.resolve(m_child.group(2))
                    _add(rels, father, parent_of_prev, "FATHER_OF", ref)

    else:
        # Generic son_of_reverse: "X the son of Y, the son of Z" chains
        # Works for Ezra 7, Zephaniah 1, Zechariah 1, etc.
        full_text = " ".join(text for _, text in verses)

        # Find the starting person: "X the son of Y"
        chain: list[str] = []
        m_start = re.search(rf"{NAME_EN},?\s+the son of\s+{NAME_EN}", full_text)
        if m_start:
            chain.append(m_start.group(1))
            chain.append(m_start.group(2))

        # Continue: ", the son of X" / "The son of X"
        for m in re.finditer(r"[Tt]he son of\s+" + NAME_EN, full_text):
            name = m.group(1)
            if chain and name != chain[-1]:
                chain.append(name)

        # Build FATHER_OF pairs
        for i in range(len(chain) - 1):
            child = resolver.resolve(chain[i])
            father = resolver.resolve(chain[i + 1])
            ref = f"{ref_prefix} {ch}:{verses[0][0]}"
            _add(rels, father, child, "FATHER_OF", ref)

    return rels


def extract_narrative(verses: list[tuple[int, str]], ref_prefix: str, resolver: EntityResolver, ch: int) -> list[Relation]:
    """Pattern D: Mixed narrative genealogy (Genesis 4, plus Phase 2 expansions)."""
    rels = []
    re_begat = re.compile(rf"{NAME_EN}\s+begat\s+{NAME_EN}")
    re_bare = re.compile(r"bare\s+" + NAME_EN + r"\b(?!\s+(?:a|the)\s+)")  # exclude "bare X a/the Nth son"
    # "bare X a/the son" — X is the father, not child
    re_bare_father = re.compile(r"bare\s+" + NAME_EN + r"\b\s+(?:a|the)\s+(?:\w+\s+)?(?:son|daughter)")
    re_called = re.compile(r"called (?:(?:she |he )?his|her) name\s+" + NAME_EN)
    re_knew_wife = re.compile(rf"{NAME_EN}\s+knew\s+(?:his wife|{NAME_EN}\s+his wife)")
    re_born = re.compile(rf"unto {NAME_EN} was born\s+{NAME_EN}")
    re_wife = re.compile(rf"{NAME_EN}\s+took\s+unto him\s+(?:two )?wives?.*?name.*?was\s+{NAME_EN}")

    # Phase 2 patterns
    # "the daughter of X" / "X the daughter of Y"
    re_daughter_of = re.compile(rf"{NAME_EN}(?:,)?\s+(?:the )?daughter of\s+{NAME_EN}")
    # "X the wife of Y" / "the wife of X"
    re_wife_of = re.compile(rf"{NAME_EN}(?:,)?\s+(?:the )?wife of\s+{NAME_EN}")
    # "his wife X" / "his wife was X"
    re_his_wife = re.compile(rf"(?:{NAME_EN}(?:'s| his) wife(?: was)?\s+{NAME_EN})")
    # "the name of X's wife was Y" / "the name of his wife Y"
    re_name_wife = re.compile(rf"name of (?:{NAME_EN}'s|his|her) wife (?:was )?{NAME_EN}")
    # "his mother's name was X" (Kings regnal formula)
    re_mother_name = re.compile(rf"(?:his|her) mother(?:'s name)? was\s+{NAME_EN}")
    # "X the mother of Y"
    re_mother_of = re.compile(rf"{NAME_EN}\s+the mother of\s+{NAME_EN}")
    # "X reigned in his stead" (Kings succession)
    re_reigned_stead = re.compile(rf"{NAME_EN}\s+(?:his son )?reigned in his stead")
    # "X the son of Y" (common in Kings/Samuel)
    re_son_of = re.compile(rf"{NAME_EN}\s+the son of\s+{NAME_EN}")
    # "X, of Y the Z-ess" — David's sons born-of-mother pattern (2 Sam 3:2-5)
    re_child_of_mother = re.compile(rf"(?:his (?:firstborn|second|third|fourth|fifth|sixth)\s+(?:was\s+)?)?{NAME_EN},?\s+of\s+{NAME_EN}")
    # "the son of X" / "who was the son of X" (narrative usage)
    re_son_of_bare = re.compile(rf"the son of\s+{NAME_EN}")
    # "he had two wives; the name of the one was X, and the name of the other Y"
    re_two_wives = re.compile(rf"the name of the (?:one|other|younger|elder|firstborn) (?:was )?{NAME_EN}")
    # "the daughters of X" / "X had two daughters"
    re_daughters_of = re.compile(rf"{NAME_EN} had (?:two |three )?daughters")
    # "took to wife X" / "took X to wife"
    re_took_wife = re.compile(rf"took (?:to wife|him(?:self)? a wife)\s+{NAME_EN}")
    re_took_wife2 = re.compile(rf"took\s+{NAME_EN}\s+to (?:be his )?wife")
    # "X bare a son, and called his name Y" (narrative birth)
    re_bare_son_called = re.compile(r"(?:bare|bear) a son.*?called his name\s+" + NAME_EN)
    # "who was born to X" / "born to X"
    re_born_to = re.compile(rf"born to\s+{NAME_EN}")
    # "X was the father of Y" / "X the father of Y"
    re_father_of = re.compile(rf"{NAME_EN}\s+(?:was )?the father of\s+{NAME_EN}")

    current_father: str | None = None
    current_mother: str | None = None
    # Track the last named king for "reigned in his stead" pattern
    last_king: str | None = None
    # Track pending births: "bare X a son" in one verse, "called his name Y" in the next
    pending_birth: bool = False

    # Track whether we're inside a "sons born to X" list (2 Sam 3, 5; 1 Chr 3)
    in_sons_list: bool = False

    for vnum, text in verses:
        ref = f"{ref_prefix} {ch}:{vnum}"

        # End of sons list on topic change (check BEFORE detecting new list start)
        if in_sons_list and ("¶" in text or "came to pass" in text):
            in_sons_list = False

        # "unto X were sons born" / "these were born unto him" — sets current_father for child lists
        m_unto_born = re.search(rf"unto {NAME_EN} were (?:sons|children|daughters) born", text)
        if m_unto_born:
            current_father = resolver.resolve(m_unto_born.group(1))
            in_sons_list = True
        m_born_unto = re.search(r"(?:these|there) were born unto (?:him|her)", text)
        if m_born_unto:
            in_sons_list = True
        # "these be the names of those that were born unto him" (2 Sam 5:14)
        if "born unto him" in text or "born unto David" in text:
            in_sons_list = True
        # "sons and daughters born to X" (2 Sam 5:13)
        m_born_to_x = re.search(rf"born to\s+{NAME_EN}", text)
        if m_born_to_x and ("sons" in text or "daughters" in text or "children" in text):
            current_father = resolver.resolve(m_born_to_x.group(1))
            in_sons_list = True
        # "Now these were the sons of David" (1 Chr 3:1)
        m_sons_of = re.search(rf"(?:these were|sons of)\s+{NAME_EN}(?:,\s+which were born)", text)
        if m_sons_of:
            current_father = resolver.resolve(m_sons_of.group(1))
            in_sons_list = True

        # "X knew his wife / X knew Eve his wife"
        m_knew = re_knew_wife.search(text)
        if m_knew:
            current_father = resolver.resolve(m_knew.group(1))
            if m_knew.group(2):
                wife = resolver.resolve(m_knew.group(2))
                _add(rels, current_father, wife, "SPOUSE_OF", ref)

        # "he went in also unto X" / "he went in unto her" — sets husband context
        m_went_in = re.search(rf"went in (?:also )?unto\s+{NAME_EN}", text)
        if m_went_in:
            wife = resolver.resolve(m_went_in.group(1))
            # If we can find the subject (husband), set current_father
            m_subj = re.search(rf"{NAME_EN}\s+(?:went|did)", text)
            if m_subj:
                husband = resolver.resolve(m_subj.group(1))
                if husband:
                    current_father = husband

        # Track mothers early: "Leah conceived" / "X conceived" / "she conceived" with name in verse
        m_conceive = re.search(rf"{NAME_EN}\s+conceived", text)
        if m_conceive:
            mother = resolver.resolve(m_conceive.group(1))
            if mother:
                current_mother = mother
        elif "she conceived" in text or "conceived again" in text:
            # Try to find the named woman in this verse (e.g., "God hearkened unto Leah, and she conceived")
            m_named = re.search(rf"unto\s+{NAME_EN}", text)
            if m_named:
                mother = resolver.resolve(m_named.group(1))
                if mother:
                    current_mother = mother

        # "Zilpah ... maid bare" / "X bare Y a son" — set mother from named woman before "bare"
        if re_bare_father.search(text) and "bare" in text:
            bare_pos = text.index("bare")
            is_maid = "maid" in text[:bare_pos] or "handmaid" in text[:bare_pos]
            # For "maid" pattern, use FIRST name (the maid); otherwise use LAST name before "bare"
            best_mother = None
            for m_pre in re.finditer(rf"{NAME_EN}", text):
                if m_pre.start() < bare_pos:
                    candidate = resolver.resolve(m_pre.group(1))
                    if candidate and candidate != current_father:
                        if is_maid:
                            best_mother = candidate
                            break  # first valid name = the maid
                        else:
                            best_mother = candidate  # keep updating = last name
            if best_mother:
                current_mother = best_mother

        # "bare X a/the son" — X is the father (e.g., "bare Jacob a son")
        for m in re_bare_father.finditer(text):
            father = resolver.resolve(m.group(1))
            if father:
                current_father = father
            pending_birth = True

        # "bare X" (but not "bare X a son")
        for m in re_bare.finditer(text):
            child = resolver.resolve(m.group(1))
            _add(rels, current_father, child, "FATHER_OF", ref)
            if current_mother:
                _add(rels, current_mother, child, "MOTHER_OF", ref)

        # "called his/her name X" (after "bare a son/daughter" — same or previous verse)
        if "bare a son" in text or "bear a son" in text or "bare a daughter" in text or re_bare_father.search(text) or pending_birth:
            m_called = re_called.search(text)
            if m_called:
                child = resolver.resolve(m_called.group(1))
                _add(rels, current_father, child, "FATHER_OF", ref)
                if current_mother:
                    _add(rels, current_mother, child, "MOTHER_OF", ref)
                pending_birth = False

        # "unto X was born Y"
        for m in re_born.finditer(text):
            father = resolver.resolve(m.group(1))
            child = resolver.resolve(m.group(2))
            _add(rels, father, child, "FATHER_OF", ref)

        # "X begat Y" (Cain's line)
        for m in re_begat.finditer(text):
            father = resolver.resolve(m.group(1))
            child = resolver.resolve(m.group(2))
            _add(rels, father, child, "FATHER_OF", ref)
            if father:
                current_father = father

        # "X took unto him wives... Adah... Zillah"
        m_wife = re_wife.search(text)
        if m_wife:
            husband = resolver.resolve(m_wife.group(1))
            wife = resolver.resolve(m_wife.group(2))
            if husband:
                current_father = husband
            _add(rels, husband, wife, "SPOUSE_OF", ref)
            m_other = re.search(r"the other\s+" + NAME_EN, text)
            if m_other:
                wife2 = resolver.resolve(m_other.group(1))
                _add(rels, husband, wife2, "SPOUSE_OF", ref)

        # "X bare Y" with named mother
        for m_match in re.finditer(rf"{NAME_EN}\s+(?:bare|she also bare)\s+{NAME_EN}", text):
            mother = resolver.resolve(m_match.group(1))
            child = resolver.resolve(m_match.group(2))
            _add(rels, mother, child, "MOTHER_OF", ref)

        # --- Phase 2 new patterns ---

        # "X the son of Y" (common in Kings/Samuel/Judges)
        # In sons-list context (2 Sam 3:2-5), "the son of X" means X is MOTHER, not father
        for m in re_son_of.finditer(text):
            child = resolver.resolve(m.group(1))
            parent = resolver.resolve(m.group(2))
            if in_sons_list:
                _add(rels, parent, child, "MOTHER_OF", ref)
                _add(rels, current_father, child, "FATHER_OF", ref)
            else:
                _add(rels, parent, child, "FATHER_OF", ref)
            if child:
                last_king = child

        # "X was the father of Y" / "X the father of Y"
        for m in re_father_of.finditer(text):
            father = resolver.resolve(m.group(1))
            child = resolver.resolve(m.group(2))
            _add(rels, father, child, "FATHER_OF", ref)

        # "his mother's name was X" — mother of current king/subject
        m_mother = re_mother_name.search(text)
        if m_mother:
            mother = resolver.resolve(m_mother.group(1))
            # Find the subject: look for "son of" or last named king
            subject = last_king
            for m_sub in re_son_of.finditer(text):
                subject = resolver.resolve(m_sub.group(1))
            _add(rels, mother, subject, "MOTHER_OF", ref)

        # "X the mother of Y"
        for m in re_mother_of.finditer(text):
            mother = resolver.resolve(m.group(1))
            child = resolver.resolve(m.group(2))
            _add(rels, mother, child, "MOTHER_OF", ref)

        # "X reigned in his stead" — succession implies FATHER_OF
        m_reigned = re_reigned_stead.search(text)
        if m_reigned:
            successor = resolver.resolve(m_reigned.group(1))
            # "his son reigned" variant — last_king is the father
            if "his son" in m_reigned.group(0):
                _add(rels, last_king, successor, "FATHER_OF", ref)
            # Check for explicit "son of" in the same verse
            elif re_son_of.search(text):
                pass  # already handled by re_son_of above
            else:
                # Default: predecessor is father if succession implies it
                _add(rels, last_king, successor, "FATHER_OF", ref)
            if successor:
                last_king = successor

        # "the daughter of X" — FATHER_OF relation
        for m in re_daughter_of.finditer(text):
            daughter = resolver.resolve(m.group(1))
            father = resolver.resolve(m.group(2))
            _add(rels, father, daughter, "FATHER_OF", ref)

        # "X the wife of Y" / "wife of X"
        for m in re_wife_of.finditer(text):
            wife = resolver.resolve(m.group(1))
            husband = resolver.resolve(m.group(2))
            _add(rels, husband, wife, "SPOUSE_OF", ref)

        # "X's wife Y" / "his wife was X"
        for m in re_his_wife.finditer(text):
            husband = resolver.resolve(m.group(1))
            wife = resolver.resolve(m.group(2))
            _add(rels, husband, wife, "SPOUSE_OF", ref)

        # "name of X's wife was Y"
        for m in re_name_wife.finditer(text):
            wife = resolver.resolve(m.group(2) if m.group(2) else m.group(1))
            husband_name = m.group(1)
            if husband_name and husband_name not in ("his", "her"):
                husband = resolver.resolve(husband_name)
                _add(rels, husband, wife, "SPOUSE_OF", ref)
            elif current_father:
                _add(rels, current_father, wife, "SPOUSE_OF", ref)

        # "he took to wife X" / "took X to wife"
        m_tw = re_took_wife.search(text) or re_took_wife2.search(text)
        if m_tw:
            wife = resolver.resolve(m_tw.group(1))
            # Find the husband from context
            m_sub = re_son_of.search(text)
            husband = resolver.resolve(m_sub.group(1)) if m_sub else last_king
            _add(rels, husband, wife, "SPOUSE_OF", ref)

        # "X, of Y" — child-of-mother pattern (2 Sam 3:2-5)
        for m in re_child_of_mother.finditer(text):
            child = resolver.resolve(m.group(1))
            mother = resolver.resolve(m.group(2))
            if child and mother:
                _add(rels, mother, child, "MOTHER_OF", ref)
                # David (or current father) is the father
                _add(rels, current_father, child, "FATHER_OF", ref)

        # Pure name lists in sons_list context (2 Sam 5:14-16, 1 Chr 3:5-8)
        # Only fire when no more specific patterns (child_of_mother, son_of) matched this verse
        has_specific_match = bool(re_child_of_mother.search(text) or re_son_of.search(text))
        if in_sons_list and current_father and not has_specific_match:
            all_names = re.findall(rf"(?:and\s+)?{NAME_EN}", text)
            # Filter: only if text looks like a name list (3+ names, no verb patterns)
            if len(all_names) >= 3 and not re.search(r"\b(?:begat|bare|son of|reigned|died)\b", text):
                # Exclude current_father from the children list
                father_name = current_father
                for raw in all_names:
                    name = resolver.resolve(raw)
                    if name and name != father_name and name not in STOP_NAMES and name not in PLACE_NAMES:
                        _add(rels, current_father, name, "FATHER_OF", ref)
                # Check for "of X the daughter of Y" — mother pattern (1 Chr 3:5)
                m_of_mother = re.search(rf"of\s+{NAME_EN}", text)
                if m_of_mother:
                    mother = resolver.resolve(m_of_mother.group(1))
                    if mother and mother != father_name and mother not in STOP_NAMES:
                        for raw in all_names:
                            name = resolver.resolve(raw)
                            if name and name != mother and name != father_name and name not in STOP_NAMES and name not in PLACE_NAMES:
                                _add(rels, mother, name, "MOTHER_OF", ref)

        # "Laban had two daughters" / "X had daughters"
        m_daughters = re_daughters_of.search(text)
        if m_daughters:
            father = resolver.resolve(m_daughters.group(1))
            if father:
                current_father = father
            # Find the daughter names: "name of the elder was X" etc.
            for m_name in re_two_wives.finditer(text):
                daughter = resolver.resolve(m_name.group(1))
                _add(rels, father, daughter, "FATHER_OF", ref)

        # "he had two wives; the name of the one was X" — without daughters pattern
        if "two wives" in text and not re_daughters_of.search(text):
            m_subj = re.search(rf"name was {NAME_EN}", text)
            if m_subj:
                husband = resolver.resolve(m_subj.group(1))
                # but "name was X" is the husband if it comes before "two wives"
                # Actually "his name was Elkanah... he had two wives; the name of the one was Hannah"
                pass  # handled by re_two_wives + context
            for m_name in re_two_wives.finditer(text):
                wife = resolver.resolve(m_name.group(1))
                _add(rels, current_father, wife, "SPOUSE_OF", ref)

        # "born to X, son of Y" (Gen 24 pattern)
        for m in re_born_to.finditer(text):
            parent = resolver.resolve(m.group(1))
            # Find the child (subject before "born to")
            m_child = re.search(rf"{NAME_EN}.*?(?:who was )?born to", text)
            if m_child:
                child = resolver.resolve(m_child.group(1))
                _add(rels, parent, child, "FATHER_OF", ref)

        # "she called his name X" / "called his name X" with birth context
        m_called_name = re_called.search(text)
        if m_called_name and "bare a son" not in text and "bear a son" not in text:
            # Check if there's a birth context (same verse or pending from previous)
            if "conceived" in text or "bare" in text or pending_birth:
                child = resolver.resolve(m_called_name.group(1))
                if current_mother:
                    _add(rels, current_mother, child, "MOTHER_OF", ref)
                if current_father:
                    _add(rels, current_father, child, "FATHER_OF", ref)
                pending_birth = False

        # "gave him Rachel his daughter to wife" / "gave unto his daughter X"
        m_gave = re.search(rf"gave (?:him |unto )?{NAME_EN} his daughter", text)
        if m_gave:
            daughter = resolver.resolve(m_gave.group(1))
            _add(rels, current_father, daughter, "FATHER_OF", ref)
            # If "to wife" follows, it's also a marriage
            if "to wife" in text or "to be his wife" in text:
                # The receiver (husband) is the implicit subject — use last_king or search context
                m_subj = re.search(rf"gave (?:him|{NAME_EN})", text)
                if m_subj and m_subj.group(0) == "gave him":
                    # "him" = contextual husband, often mentioned earlier
                    pass  # SPOUSE_OF will be picked up by re_wife_of or context

        # "he took Leah his daughter" (Laban giving Leah to Jacob)
        m_took_daughter = re.search(rf"took {NAME_EN} his daughter", text)
        if m_took_daughter:
            daughter = resolver.resolve(m_took_daughter.group(1))
            _add(rels, current_father, daughter, "FATHER_OF", ref)

        # "my father's name was X" (BoM first-person: Mormon 1:5)
        # Handle both straight (') and curly (\u2019) apostrophes
        m_my_father = re.search(rf"(?:my|his) father(?:['\u2019]s name)? was\s+{NAME_EN}", text)
        if m_my_father:
            father = resolver.resolve(m_my_father.group(1))
            # Find the narrator: "I, X" pattern
            m_narrator = re.search(rf"I,?\s+{NAME_EN}", text)
            if m_narrator:
                child = resolver.resolve(m_narrator.group(1))
                _add(rels, father, child, "FATHER_OF", ref)

        # "X, who was the son of Y" (Hel 2:2)
        m_who_son = re.search(rf"{NAME_EN},?\s+who was the son of\s+{NAME_EN}", text)
        if m_who_son:
            child = resolver.resolve(m_who_son.group(1))
            father = resolver.resolve(m_who_son.group(2))
            _add(rels, father, child, "FATHER_OF", ref)

        # "a (pure) descendant of X" (3 Ne 5:20, Mormon 1:5)
        m_descendant = re.search(rf"(?:I,?\s+{NAME_EN},?\s+)?(?:being )?a (?:pure )?descendant of\s+{NAME_EN}", text)
        if m_descendant:
            descendant = resolver.resolve(m_descendant.group(1)) if m_descendant.group(1) else None
            ancestor = resolver.resolve(m_descendant.group(2))
            if not descendant:
                # Try "I, X" earlier in text
                m_i = re.search(rf"I(?:,|\s+am)\s+{NAME_EN}", text)
                if m_i:
                    descendant = resolver.resolve(m_i.group(1))
            _add(rels, ancestor, descendant, "DESCENDANT_OF", ref)

        # Track named persons for context: "X died" / "X, he that kept"
        # NOTE: must fire BEFORE "his son X" so last_king is set for same-verse succession
        m_died = re.search(rf"{NAME_EN}(?:,.*?)?\s+died", text)
        if m_died:
            person = resolver.resolve(m_died.group(1))
            if person:
                last_king = person

        # "his son X kept it" / "his eldest son X" — succession (BoM: 4 Ne 1, Hel 3)
        m_his_son = re.search(rf"his (?:eldest )?son\s+{NAME_EN}", text)
        if m_his_son:
            child = resolver.resolve(m_his_son.group(1))
            _add(rels, last_king, child, "FATHER_OF", ref)
            if child:
                last_king = child

        # "gave unto the eldest the name of X" / "unto the youngest, the name of Y"
        for m_named in re.finditer(rf"(?:the )?name of\s+{NAME_EN}", text):
            if "eldest" in text or "youngest" in text:
                child = resolver.resolve(m_named.group(1))
                if child and child not in STOP_NAMES:
                    _add(rels, last_king, child, "FATHER_OF", ref)

    return rels


def extract_priesthood_lineage(verses: list[tuple[int, str]], ref_prefix: str, resolver: EntityResolver, ch: int) -> list[Relation]:
    """D&C 84 & 107 — priesthood authority/ordination lineage.

    Extracts ORDAINED_BY relations from:
    - "X received it under the hand of Y" (D&C 84)
    - "From X to Y, who was ordained by the hand of Z" (D&C 107)
    - Implicit ordination chains in D&C 107:42-52
    """
    rels = []
    # "under/by the hand of X" — the ordainer
    re_under_hand = re.compile(rf"(?:under|by) the hand of (?:his )?(?:father[- ]in[- ]law,?\s+)?{NAME_EN}")
    # "From X to Y" (D&C 107:42 pattern)
    re_from_to = re.compile(rf"[Ff]rom {NAME_EN} to {NAME_EN}")
    # Track the current ordinand for "under the hand of" chains
    prev_person: str | None = None

    for vnum, text in verses:
        ref = f"{ref_prefix} {ch}:{vnum}"

        # D&C 84 pattern: "X received it under the hand of Y" / "X under the hand of Y"
        m_hand = re_under_hand.search(text)
        if m_hand:
            ordainer = resolver.resolve(m_hand.group(1))
            # Find the ordinand: first capitalized name in the verse, or "sons of X"
            ordinand = None
            m_subj = re.search(rf"(?:sons of |And )?{NAME_EN}", text)
            if m_subj:
                ordinand = resolver.resolve(m_subj.group(1))
            if ordinand and ordainer:
                _add(rels, ordainer, ordinand, "ORDAINED_BY", ref)
                prev_person = ordinand

        # D&C 107 pattern: "From Adam to Seth" or implicit ordination pairs
        for m in re_from_to.finditer(text):
            ordainer = resolver.resolve(m.group(1))
            ordinand = resolver.resolve(m.group(2))
            _add(rels, ordainer, ordinand, "ORDAINED_BY", ref)

        # D&C 107:44-52: "Enos was ordained... by the hand of Adam"
        m_ordained = re.search(rf"{NAME_EN} was .*?ordained", text)
        if m_ordained:
            ordinand = resolver.resolve(m_ordained.group(1))
            if m_hand:
                ordainer = resolver.resolve(m_hand.group(1))
                _add(rels, ordainer, ordinand, "ORDAINED_BY", ref)

    return rels


def extract_begat_narrative(verses: list[tuple[int, str]], ref_prefix: str, resolver: EntityResolver, ch: int) -> list[Relation]:
    """Genesis 25 — mix of begat, sons-of lists, and narrative births."""
    rels = []

    # Combine both begat and sons_of patterns
    begat_rels = extract_begat(verses, f"{ref_prefix} {ch}", resolver)
    sons_rels = extract_sons_of(verses, ref_prefix, resolver, ch)
    narrative_rels = extract_narrative(verses, ref_prefix, resolver, ch)

    seen: set[tuple] = set()
    for r in begat_rels + sons_rels + narrative_rels:
        if r.key not in seen:
            rels.append(r)
            seen.add(r.key)

    return rels


# ---------------------------------------------------------------------------
# Name list splitter
# ---------------------------------------------------------------------------

def split_name_list(text: str) -> list[str]:
    """Split 'A, and B, and C' or 'A, B, C, and D' into individual names."""
    # Remove parenthetical notes
    text = re.sub(r"\(.*?\)", "", text)
    # Remove leading "and "
    text = re.sub(r"^and\s+", "", text.strip())
    # Split on ", and ", ", ", or " and "
    parts = re.split(r",\s+and\s+|,\s+|\s+and\s+", text)
    names = []
    for p in parts:
        p = p.strip().rstrip(".")
        # Extract just the name (first capitalized word or hyphenated)
        m = re.match(r"([A-Z][a-z]+(?:-[A-Z]?[a-z]+)*)", p)
        if m:
            name = m.group(1)
            if name not in GENTILICS and len(name) > 1:
                names.append(name)
    return names


# ---------------------------------------------------------------------------
# Main extraction logic
# ---------------------------------------------------------------------------

def read_chapter(lang: str, vol: str, slug: str, ch: int) -> str | None:
    """Read a chapter file from the corpus."""
    path = CORPUS / lang / "scriptures" / vol / slug / f"{ch}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def extract_chapter(spec: ChapterSpec, resolver: EntityResolver) -> ChapterResult:
    """Extract genealogical relations from a chapter spec."""
    result = ChapterResult(chapter_id=spec.chapter_id)

    for ch in spec.chapters:
        text = read_chapter("en", spec.vol, spec.slug_en, ch)
        if not text:
            print(f"  WARNING: File not found for {spec.chapter_id} ch {ch} (EN)")
            continue

        verses = parse_verses(text, spec.verse_range)
        if not verses:
            continue

        # Build chapter-aware ref prefix: "Genesis 5" for begat → "Genesis 5:3"
        ch_ref = f"{spec.ref_prefix_en} {ch}"

        if spec.pattern == "begat":
            rels = extract_begat(verses, ch_ref, resolver)
        elif spec.pattern == "begat_dense":
            rels = extract_begat_dense(verses, spec.ref_prefix_en, resolver)
        elif spec.pattern == "sons_of":
            rels = extract_sons_of(verses, spec.ref_prefix_en, resolver, ch)
        elif spec.pattern == "chronicles":
            rels = extract_chronicles_1(verses, spec.ref_prefix_en, resolver)
        elif spec.pattern == "son_of_reverse":
            rels = extract_son_of_reverse(verses, spec.ref_prefix_en, resolver, ch, spec.chapter_id)
        elif spec.pattern == "narrative":
            rels = extract_narrative(verses, spec.ref_prefix_en, resolver, ch)
        elif spec.pattern == "begat_narrative":
            rels = extract_begat_narrative(verses, spec.ref_prefix_en, resolver, ch)
        elif spec.pattern == "priesthood_lineage":
            rels = extract_priesthood_lineage(verses, spec.ref_prefix_en, resolver, ch)
        else:
            print(f"  WARNING: Unknown pattern '{spec.pattern}' for {spec.chapter_id}")
            rels = []

        result.relations.extend(rels)

    return result


def load_existing_relations(path: Path) -> set[tuple]:
    """Load existing curated relations for deduplication."""
    if not path.exists():
        return set()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    keys = set()
    for rel_type, relations in data.items():
        for r in relations:
            keys.add((r["from"]["name"], rel_type, r["to"]["name"]))
    return keys


def build_output(relations: list[Relation]) -> dict:
    """Build the output JSON in relations.json format."""
    output: dict[str, list] = defaultdict(list)
    for r in relations:
        output[r.rel_type].append({
            "from": {"name": r.from_name, "type": r.from_type},
            "to": {"name": r.to_name, "type": r.to_type},
            "source_ref": r.source_ref,
            "confidence": "curated",
            "source": "genealogy_extraction",
            "bidirectional": False,
        })
    return dict(output)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="P10 Phase 1: Extract genealogical relations from scripture")
    parser.add_argument("--dry-run", action="store_true", help="Report only, don't write files")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSON path")
    parser.add_argument("--chapters", nargs="*", help="Specific chapter IDs to process (default: all)")
    args = parser.parse_args()

    print("=" * 60)
    print("P10 Phase 1: Genealogy Extraction from Formal Chapters")
    print("=" * 60)

    # Load entity resolver
    print(f"\nLoading entity gazetteer from {ENTITIES_PATH.name}...")
    resolver = EntityResolver(ENTITIES_PATH)
    print(f"  {len(resolver.canonical)} canonical names, {len(resolver.alias_map)} aliases")

    # Load existing relations for dedup
    existing = load_existing_relations(EXISTING_RELS_PATH)
    print(f"  {len(existing)} existing curated relations loaded for dedup")

    # Select chapters
    specs = CHAPTER_REGISTRY
    if args.chapters:
        specs = [s for s in specs if s.chapter_id in args.chapters]
        if not specs:
            print(f"ERROR: No matching chapters for {args.chapters}")
            print(f"Available: {[s.chapter_id for s in CHAPTER_REGISTRY]}")
            sys.exit(1)

    # Extract
    all_relations: list[Relation] = []
    dedup_count = 0
    internal_seen: set[tuple] = set()

    print(f"\n{'Chapter':<20} {'FATHER_OF':>10} {'MOTHER_OF':>10} {'SPOUSE_OF':>10} {'DESC_OF':>10} {'ORD_BY':>8} {'Dedup':>6} {'New Ent':>8}")
    print("-" * 85)

    for spec in specs:
        result = extract_chapter(spec, resolver)

        # Dedup: internal + existing
        new_rels = []
        ch_dedup = 0
        for r in result.relations:
            if r.key in internal_seen or r.key in existing:
                ch_dedup += 1
                continue
            internal_seen.add(r.key)
            new_rels.append(r)

        dedup_count += ch_dedup

        # Count by type
        counts = defaultdict(int)
        for r in new_rels:
            counts[r.rel_type] += 1

        # New entities for this chapter
        new_ents = [n for n in resolver.unresolved]  # cumulative, reported at end

        print(f"  {spec.chapter_id:<18} {counts.get('FATHER_OF', 0):>10} {counts.get('MOTHER_OF', 0):>10} {counts.get('SPOUSE_OF', 0):>10} {counts.get('DESCENDANT_OF', 0):>10} {counts.get('ORDAINED_BY', 0):>8} {ch_dedup:>6} {'':>8}")

        all_relations.extend(new_rels)

    # Summary
    total_counts = defaultdict(int)
    for r in all_relations:
        total_counts[r.rel_type] += 1

    print("-" * 85)
    print(f"  {'TOTAL':<18} {total_counts.get('FATHER_OF', 0):>10} {total_counts.get('MOTHER_OF', 0):>10} {total_counts.get('SPOUSE_OF', 0):>10} {total_counts.get('DESCENDANT_OF', 0):>10} {total_counts.get('ORDAINED_BY', 0):>8} {dedup_count:>6} {len(resolver.unresolved):>8}")
    print(f"\n  Total new relations: {len(all_relations)}")
    print(f"  Deduplicated (internal + existing): {dedup_count}")
    print(f"  New entity candidates: {len(resolver.unresolved)}")

    if resolver.unresolved:
        print(f"\n  Unresolved names (not in gazetteer):")
        for name in sorted(resolver.unresolved):
            print(f"    - {name}")

    # Write output
    if not args.dry_run:
        output = build_output(all_relations)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\n  Output written to: {args.output}")

        # Write new entities report
        if resolver.unresolved:
            with open(NEW_ENTITIES_OUTPUT, "w", encoding="utf-8") as f:
                f.write("# New entity candidates from genealogy extraction\n")
                f.write("# Add these to entities.json after review\n\n")
                for name in sorted(resolver.unresolved):
                    f.write(f"{name}\n")
            print(f"  New entities report: {NEW_ENTITIES_OUTPUT}")

        print(f"\n  To load into Neo4j:")
        print(f"    python scripts/load_curated_relations.py --relations-file {args.output} --dry-run")
        print(f"    python scripts/load_curated_relations.py --relations-file {args.output}")
    else:
        print("\n  [DRY RUN — no files written]")


if __name__ == "__main__":
    main()
