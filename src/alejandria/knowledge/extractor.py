"""Knowledge graph entity and relation extraction from text.

Uses gazetteer-based matching + regex patterns. No NLP model required for Phase 3.
spaCy NER can be layered on top in a later phase for open-domain entity discovery.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

_GAZETTEER_PATH = Path(__file__).parent / "gazetteers" / "entities.json"

# Scripture citation patterns: "1 Nephi 3:7", "Alma 32:21", "D&C 88:118", "John 3:16"
_SCRIPTURE_RE = re.compile(
    r"\b("
    r"(?:[1-4]\s?)?"  # Optional book number
    r"(?:Nephi|Nefi|Alma|Mosiah|Mos[ií]ah|Helaman|Helam[aá]n|Ether|[EÉ]ter|Mormon|Morm[oó]n|Moroni|Moron[ií]"
    r"|Jacob|Jacobo|Enos|Jarom|Omni|Words of Mormon"
    r"|Genesis|G[eé]nesis|Exodus|[EÉ]xodo|Leviticus|Lev[ií]tico|Numbers|N[uú]meros|Deuteronomy|Deuteronomio"
    r"|Joshua|Josu[eé]|Judges|Jueces|Ruth|Rut"
    r"|Samuel|Kings|Reyes|Chronicles|Cr[oó]nicas"
    r"|Psalms?|Salmos?|Proverbs|Proverbios|Ecclesiastes|Eclesiast[eé]s"
    r"|Isaiah|Isa[ií]as|Jeremiah|Jerem[ií]as|Ezekiel|Ezequiel|Daniel"
    r"|Hosea|Oseas|Joel|Amos|Am[oó]s|Obadiah|Abd[ií]as|Jonah|Jon[aá]s|Micah|Miqueas"
    r"|Nahum|Habakkuk|Habacuc|Zephaniah|Sofon[ií]as|Haggai|Hageo|Zechariah|Zacar[ií]as|Malachi|Malaqu[ií]as"
    r"|Matthew|Mateo|Mark|Marcos|Luke|Lucas|John|Juan"
    r"|Acts|Hechos|Romans|Romanos|Corinthians|Corintios|Galatians|G[aá]latas"
    r"|Ephesians|Efesios|Philippians|Filipenses|Colossians|Colosenses"
    r"|Thessalonians|Tesalonicenses|Timothy|Timoteo|Titus|Tito|Philemon|Filem[oó]n"
    r"|Hebrews|Hebreos|James|Santiago|Peter|Pedro|Jude|Judas|Revelation|Apocalipsis"
    r"|D&C|D\. ?y ?C\.?|Doctrine and Covenants|Doctrina y Convenios"
    r"|Abraham|Abrah[aá]n|Moses|Mois[eé]s|JS[—-]H|JS[—-]M"
    r"|Pearl of Great Price|Perla de Gran Precio)"
    r"\s+\d+(?::\d+(?:[-–]\d+)?)?)"  # Chapter and verse
    , re.IGNORECASE
)


@dataclass
class ExtractedEntity:
    name: str
    type: str
    span: tuple[int, int] = (0, 0)


@dataclass
class ExtractedRelation:
    from_entity: str
    from_type: str
    relation: str
    to_entity: str
    to_type: str


@dataclass
class ExtractionResult:
    entities: list[ExtractedEntity] = field(default_factory=list)
    relations: list[ExtractedRelation] = field(default_factory=list)
    scripture_refs: list[str] = field(default_factory=list)


class KGExtractor:
    """Extract entities and relations from text using gazetteers and patterns."""

    def __init__(self, gazetteer_path: Path | None = None) -> None:
        self._gazetteer = self._load_gazetteer(gazetteer_path or _GAZETTEER_PATH)
        self._lookup = self._build_lookup()

    def _load_gazetteer(self, path: Path) -> dict:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _build_lookup(self) -> dict[str, tuple[str, str]]:
        """Build a lowercase -> (canonical_name, type) lookup from gazetteers."""
        lookup: dict[str, tuple[str, str]] = {}
        for entity_type, entries in self._gazetteer.items():
            for entry in entries:
                name = entry["name"]
                # Map canonical name
                lookup[name.lower()] = (name, entity_type)
                # Map aliases
                for alias in entry.get("aliases", []):
                    if alias:
                        lookup[alias.lower()] = (name, entity_type)
        return lookup

    def extract(self, text: str, source_file: str = "") -> ExtractionResult:
        """Extract entities, relations, and scripture references from text."""
        result = ExtractionResult()
        text_lower = text.lower()

        # 1. Gazetteer-based entity extraction
        found_entities: dict[str, ExtractedEntity] = {}
        for term, (canonical, entity_type) in self._lookup.items():
            # Match whole words only
            pattern = r"\b" + re.escape(term) + r"\b"
            for match in re.finditer(pattern, text_lower):
                key = f"{canonical}:{entity_type}"
                if key not in found_entities:
                    found_entities[key] = ExtractedEntity(
                        name=canonical,
                        type=entity_type,
                        span=(match.start(), match.end()),
                    )

        result.entities = list(found_entities.values())

        # 2. Scripture citation extraction
        for match in _SCRIPTURE_RE.finditer(text):
            ref = match.group(1).strip()
            result.scripture_refs.append(ref)
            # Add as scripture entity
            key = f"{ref}:scripture"
            if key not in found_entities:
                result.entities.append(ExtractedEntity(name=ref, type="scripture"))

        # 3. Relation extraction (co-occurrence based)
        result.relations = self._extract_relations(result.entities)

        return result

    def _extract_relations(self, entities: list[ExtractedEntity]) -> list[ExtractedRelation]:
        """Infer relations from co-occurring entities in the same chunk."""
        relations: list[ExtractedRelation] = []
        seen: set[str] = set()

        for i, e1 in enumerate(entities):
            for e2 in entities[i + 1:]:
                if e1.name == e2.name:
                    continue

                # Generate contextual relations based on type combinations
                rel = self._infer_relation_type(e1, e2)
                if rel is None:
                    continue

                key = f"{e1.name}-{rel}-{e2.name}"
                reverse_key = f"{e2.name}-{rel}-{e1.name}"
                if key not in seen and reverse_key not in seen:
                    relations.append(ExtractedRelation(
                        from_entity=e1.name,
                        from_type=e1.type,
                        relation=rel,
                        to_entity=e2.name,
                        to_type=e2.type,
                    ))
                    seen.add(key)

        return relations

    @staticmethod
    def _infer_relation_type(e1: ExtractedEntity, e2: ExtractedEntity) -> str | None:
        """Infer a relation type from the types of two co-occurring entities."""
        types = frozenset([e1.type, e2.type])
        pair = (e1.type, e2.type)

        if types == frozenset(["person", "place"]):
            return "ASSOCIATED_WITH"
        if types == frozenset(["person", "concept"]):
            return "TEACHES"
        if types == frozenset(["person", "people"]):
            return "BELONGS_TO" if e1.type == "person" else "BELONGS_TO"
        if types == frozenset(["person", "object"]):
            return "ASSOCIATED_WITH"
        if types == frozenset(["concept", "scripture"]):
            return "REFERENCED_IN"
        if types == frozenset(["person", "scripture"]):
            return "REFERENCED_IN"
        if pair == ("person", "person"):
            return "CO_OCCURS_WITH"
        if pair == ("concept", "concept"):
            return "RELATED_TO"
        if types == frozenset(["person", "period"]):
            return "LIVED_DURING"
        if types == frozenset(["place", "period"]):
            return "EXISTS_DURING"

        return "CO_OCCURS_WITH"
