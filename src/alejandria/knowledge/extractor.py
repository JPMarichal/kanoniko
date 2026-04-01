"""Knowledge graph entity and relation extraction from text.

Hybrid approach:
1. Gazetteer-based matching — precise, bilingual, curated entities
2. spaCy NER — auto-discovers entities not in the gazetteer
3. Scripture citation regex — detects scripture references
4. Co-occurrence relation inference
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

_GAZETTEER_PATH = Path(__file__).parent / "gazetteers" / "entities.json"
_RELATIONS_PATH = Path(__file__).parent / "gazetteers" / "relations.json"

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

# Mapping from spaCy NER labels to our entity types
_SPACY_LABEL_MAP = {
    # English model labels
    "PERSON": "person",
    "GPE": "place",        # Geopolitical entity (countries, cities)
    "LOC": "place",        # Non-GPE locations (mountains, rivers)
    "FAC": "place",        # Facilities (temples, buildings)
    "NORP": "people",      # Nationalities, religious/political groups
    "ORG": "people",       # Organizations (tribes, churches)
    "EVENT": "period",     # Named events (Exodus, Pentecost)
    "LAW": "concept",      # Laws, commandments (Law of Moses)
    "WORK_OF_ART": "concept",  # Named works (Song of Solomon, Book of Life)
    "MONEY": "object",     # Monetary values (thirty pieces of silver, talents)
    "DATE": "period",      # Dates/time periods (third day, year of jubilee)
    "TIME": "period",      # Times of day (the ninth hour)
    "CARDINAL": None,      # Plain numbers — too noisy
    "ORDINAL": None,       # Ordinals — too noisy
    "QUANTITY": "object",  # Measures/quantities (five loaves, cubit)
    "LANGUAGE": "concept", # Languages (Hebrew, Aramaic, Greek)
    "PRODUCT": None,       # Rarely useful in scripture
    "PERCENT": None,       # Not relevant in scripture
    # Spanish model labels (mostly same but some additions)
    "PER": "person",       # es_core_news uses PER instead of PERSON
    "MISC": None,          # Too broad — skip
}

# Common words that spaCy misidentifies as entities in scripture text
_NER_STOPWORDS = frozenset({
    "god", "lord", "the lord", "spirit", "ghost", "son", "father",
    "dios", "señor", "el señor", "espíritu", "hijo", "padre",
    "o", "i", "yea", "behold", "verily", "thus", "lo", "he",
    "chapter", "verse", "psalm", "capítulo", "versículo",
    # Common DATE/TIME noise
    "today", "tomorrow", "yesterday", "hoy", "mañana", "ayer",
    "morning", "evening", "night", "day", "week", "year", "month",
    # Common MONEY/QUANTITY noise
    "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "twelve", "hundred", "thousand",
    "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
    "nueve", "diez", "doce", "cien", "mil",
})

# Minimum entity name length to avoid noise
_MIN_ENTITY_LEN = 2

# Scripture abbreviation pattern: term followed by "." or space + chapter:verse
# e.g., "Matt. 5:3", "Ps. 16:9", "Isa 40:1", "Deut. 28:1", "Luke 2:10"
# When a gazetteer term matches at a position where this pattern follows,
# the match is a scripture citation, not an entity mention.
_CITATION_AFTER_RE = re.compile(
    r"\.?\s*\d+(?::\d+(?:\s*[-–,]\s*\d+)*)?(?:\s*\([^)]+\))?"
)


@dataclass
class ExtractedEntity:
    name: str
    type: str
    span: tuple[int, int] = (0, 0)
    source: str = "gazetteer"  # "gazetteer" or "ner"


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


# Short gazetteer terms that collide with common words, split by language.
# A term is only excluded when processing text in that language.
# "On" is a stopword in English but NOT in Spanish, so Spanish texts will
# match On/Put/So directly while English texts use contextual phrases.
_STOPWORDS_EN = frozenset({
    "on", "so", "no", "or", "an", "as", "at", "be", "by", "do", "go",
    "he", "if", "in", "is", "it", "me", "my", "of", "to", "up", "us",
    "we", "am", "put", "set", "ye",
})
_STOPWORDS_ES = frozenset({
    "ha", "yo", "es", "en", "al", "el", "la", "lo", "un", "si", "ni",
    "ya", "no", "an", "as",
})
# Union of both for the static lookup/regex (built once at init time).
# The extract() method uses the language-specific set at runtime.
_STOPWORD_ALIASES = _STOPWORDS_EN | _STOPWORDS_ES

# Contextual phrase patterns for stopword-colliding entities.
# Each entry maps a canonical entity name and type to regex patterns that
# uniquely identify the entity in scriptural text. These are searched in a
# secondary pass after the main gazetteer regex.
# Format: (canonical_name, entity_type, [compiled_regex_patterns])
_CONTEXTUAL_PHRASES: list[tuple[str, str, list[re.Pattern]]] = [
    # On = Heliopolis, city in Egypt. Joseph married daughter of priest of On.
    ("On", "place", [
        re.compile(r"\bpriest of On\b", re.IGNORECASE),
        re.compile(r"\bcity of On\b", re.IGNORECASE),
        re.compile(r"\bOn,?\s+which is\b", re.IGNORECASE),
        re.compile(r"\bPoti-?pherah\b.*\bOn\b", re.IGNORECASE),
    ]),
    # Put/Phut = son of Ham, in the Table of Nations (Genesis 10)
    ("Phut", "person", [
        re.compile(r"\bHam[;,]\s*(?:and\s+)?(?:\w+[,;]\s*)*Put\b", re.IGNORECASE),
        re.compile(r"\bPut[,;]\s*and\s+Canaan\b", re.IGNORECASE),
        re.compile(r"\bCush[,;]\s*(?:and\s+)?(?:\w+[,;]\s*)*Put\b", re.IGNORECASE),
        re.compile(r"\bLibya\b.*\bPut\b", re.IGNORECASE),
        re.compile(r"\bPut\b.*\bLibya\b", re.IGNORECASE),
        re.compile(r"\bland of Put\b", re.IGNORECASE),
    ]),
    # So = king of Egypt (2 Kings 17:4)
    ("So", "person", [
        re.compile(r"\bSo\s+king of Egypt\b", re.IGNORECASE),
        re.compile(r"\bking So\b", re.IGNORECASE),
        re.compile(r"\bsent\s+messengers\s+to\s+So\b", re.IGNORECASE),
    ]),
    # No = No-amon / Thebes in Egypt (Nahum 3:8, Ezekiel 30:14-16)
    ("No", "place", [
        re.compile(r"\bNo[,-]\s*(?:Amon|amon)\b", re.IGNORECASE),
        re.compile(r"\bpopulous\s+No\b", re.IGNORECASE),
        re.compile(r"\bcity of No\b", re.IGNORECASE),
        re.compile(r"\bNo\s+shall\b.*\brent\b", re.IGNORECASE),
    ]),
]


class KGExtractor:
    """Extract entities and relations using gazetteers + spaCy NER."""

    def __init__(self, gazetteer_path: Path | None = None, relations_path: Path | None = None) -> None:
        self._gazetteer = self._load_gazetteer(gazetteer_path or _GAZETTEER_PATH)
        self._lookup = self._build_lookup()
        self._gazetteer_re = self._compile_gazetteer_regex()
        self._curated_relations = self._load_curated_relations(relations_path or _RELATIONS_PATH)
        # Language-specific lookups for terms that are stopwords in one language
        # but valid entity names in the other.
        self._en_only_stopwords = self._build_lang_specific_lookup(_STOPWORDS_EN - _STOPWORDS_ES)
        self._es_only_stopwords = self._build_lang_specific_lookup(_STOPWORDS_ES - _STOPWORDS_EN)
        self._nlp_en = None  # Lazy-loaded
        self._nlp_es = None  # Lazy-loaded
        self._ner_available = None  # None = not checked yet
        self._ner_tracker = None  # Lazy-loaded NERCandidateTracker

    def _load_gazetteer(self, path: Path) -> dict:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _load_curated_relations(path: Path) -> dict[tuple[str, str], list[tuple[str, dict]]]:
        """Load curated relations into a lookup: (from_name, to_name) -> [(rel_type, props), ...].

        Also indexes (to_name, from_name) for bidirectional relations.
        This allows the extractor to use typed relations instead of generic
        CO_OCCURS_WITH when two curated entities co-occur in the same chunk.
        """
        lookup: dict[tuple[str, str], list[tuple[str, dict]]] = {}
        if not path.exists():
            return lookup
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            logger.warning("Could not load curated relations from %s", path)
            return lookup

        for rel_type, relations in data.items():
            for rel in relations:
                from_name = rel["from"]["name"]
                to_name = rel["to"]["name"]
                props = {}
                for key in ("source_ref", "confidence", "role", "verse_range"):
                    if key in rel:
                        props[key] = rel[key]

                pair = (from_name.lower(), to_name.lower())
                lookup.setdefault(pair, [])
                lookup[pair].append((rel_type, props))

                if rel.get("bidirectional"):
                    reverse = (to_name.lower(), from_name.lower())
                    lookup.setdefault(reverse, [])
                    lookup[reverse].append((rel_type, props))

        logger.info("Loaded curated relation lookup: %d entity pairs", len(lookup))
        return lookup

    def _build_lookup(self) -> dict[str, list[tuple[str, str]]]:
        """Build a lowercase -> [(canonical_name, type), ...] lookup from gazetteers.

        Multiple entities can share the same alias (e.g., "Mary" maps to both
        Mary mother of Jesus and Mary sister of Martha). All are registered.
        Skips short terms that collide with common stopwords.
        """
        lookup: dict[str, list[tuple[str, str]]] = {}
        for entity_type, entries in self._gazetteer.items():
            for entry in entries:
                name = entry["name"]
                pair = (name, entity_type)
                key = name.lower()
                if key not in _STOPWORD_ALIASES:
                    lookup.setdefault(key, [])
                    if pair not in lookup[key]:
                        lookup[key].append(pair)
                # Map aliases
                for alias in entry.get("aliases", []):
                    if alias:
                        akey = alias.lower()
                        if akey not in _STOPWORD_ALIASES:
                            lookup.setdefault(akey, [])
                            if pair not in lookup[akey]:
                                lookup[akey].append(pair)
        return lookup

    def _build_lang_specific_lookup(
        self, stopwords: frozenset[str],
    ) -> dict[str, list[tuple[str, str]]]:
        """Build a lookup for terms that are stopwords in ONE language only.

        When processing Spanish text, we can safely match terms that are only
        stopwords in English (e.g., "on", "put", "so") via simple \\b regex
        because they won't cause false positives in Spanish.
        """
        lookup: dict[str, list[tuple[str, str]]] = {}
        for entity_type, entries in self._gazetteer.items():
            for entry in entries:
                name = entry["name"]
                pair = (name, entity_type)
                all_names = [name] + [a for a in entry.get("aliases", []) if a]
                for n in all_names:
                    key = n.lower()
                    if key in stopwords:
                        lookup.setdefault(key, [])
                        if pair not in lookup[key]:
                            lookup[key].append(pair)
        return lookup

    def _compile_gazetteer_regex(self) -> re.Pattern | None:
        """Compile a single regex that matches ALL gazetteer terms at once.

        This replaces the O(n*m) loop of individual regex searches with a
        single O(n) pass using alternation, dramatically faster for large
        gazetteers (2,400+ terms → single compiled regex).
        """
        if not self._lookup:
            return None
        # Sort by length descending so longer terms match first (e.g., "Mary Magdalene" before "Mary")
        terms = sorted(self._lookup.keys(), key=len, reverse=True)
        pattern = r"\b(" + "|".join(re.escape(t) for t in terms) + r")\b"
        try:
            return re.compile(pattern, re.IGNORECASE)
        except re.error:
            logger.warning("Failed to compile gazetteer regex (%d terms), falling back to loop", len(terms))
            return None

    def _load_ner_models(self) -> None:
        """Lazy-load spaCy models. Only loads once, marks unavailable on failure."""
        if self._ner_available is not None:
            return  # Already tried

        try:
            import spacy

            try:
                self._nlp_en = spacy.load("en_core_web_sm", disable=["parser", "lemmatizer"])
                logger.info("spaCy English NER model loaded")
            except OSError:
                logger.info("spaCy English model not available (en_core_web_sm)")

            try:
                self._nlp_es = spacy.load("es_core_news_sm", disable=["parser", "lemmatizer"])
                logger.info("spaCy Spanish NER model loaded")
            except OSError:
                logger.info("spaCy Spanish model not available (es_core_news_sm)")

            self._ner_available = self._nlp_en is not None or self._nlp_es is not None
            if not self._ner_available:
                logger.warning("No spaCy NER models available — using gazetteer only")
        except ImportError:
            logger.info("spaCy not installed — using gazetteer only")
            self._ner_available = False

    def extract(self, text: str, source_file: str = "") -> ExtractionResult:
        """Extract entities, relations, and scripture references from text.

        Pipeline:
        1. Gazetteer matching (precise, curated)
        2. spaCy NER (auto-discovery of unknown entities)
        3. Scripture citation regex
        4. Co-occurrence relation inference
        """
        result = ExtractionResult()
        text_lower = text.lower()

        # Detect language early — needed for stopword-aware matching
        lang = "en"
        if source_file:
            parts = source_file.replace("\\", "/").split("/")
            if parts and parts[0] == "es":
                lang = "es"

        # 1. Gazetteer-based entity extraction (takes precedence)
        #    Uses pre-compiled single regex for O(n) scanning instead of O(n*m) loop
        found_entities: dict[str, ExtractedEntity] = {}
        gazetteer_spans: set[tuple[int, int]] = set()

        if self._gazetteer_re:
            for match in self._gazetteer_re.finditer(text_lower):
                term = match.group(1).lower()
                # Skip if this match is part of a scripture citation
                # e.g., "Matt. 5:3", "Ps. 16:9", "Isa 40:1"
                after = text_lower[match.end():]
                if _CITATION_AFTER_RE.match(after):
                    continue
                for canonical, entity_type in self._lookup.get(term, []):
                    key = f"{canonical}:{entity_type}"
                    if key not in found_entities:
                        found_entities[key] = ExtractedEntity(
                            name=canonical,
                            type=entity_type,
                            span=(match.start(), match.end()),
                            source="gazetteer",
                        )
                        gazetteer_spans.add((match.start(), match.end()))
        else:
            # Fallback: individual regex per term (slow but correct)
            for term, candidates in self._lookup.items():
                pattern = r"\b" + re.escape(term) + r"\b"
                for match in re.finditer(pattern, text_lower):
                    after = text_lower[match.end():]
                    if _CITATION_AFTER_RE.match(after):
                        continue
                    for canonical, entity_type in candidates:
                        key = f"{canonical}:{entity_type}"
                        if key not in found_entities:
                            found_entities[key] = ExtractedEntity(
                                name=canonical,
                                type=entity_type,
                                span=(match.start(), match.end()),
                                source="gazetteer",
                            )
                            gazetteer_spans.add((match.start(), match.end()))

        # 1b. Contextual phrase matching for stopword-colliding entities.
        #     These terms (On, Put, So, No) are too short for \b matching but
        #     are real biblical entities. Match only in known phrases.
        for canonical, entity_type, patterns in _CONTEXTUAL_PHRASES:
            key = f"{canonical}:{entity_type}"
            if key in found_entities:
                continue
            for pat in patterns:
                m = pat.search(text)
                if m:
                    found_entities[key] = ExtractedEntity(
                        name=canonical,
                        type=entity_type,
                        span=(m.start(), m.end()),
                        source="gazetteer_contextual",
                    )
                    break

        # 1c. Cross-language stopword matching.
        #     Terms like "on", "put", "so" are stopwords in English but valid
        #     proper nouns in Spanish text (and vice versa). When processing
        #     Spanish, directly match English-only stopwords via \b regex.
        cross_lookup = self._en_only_stopwords if lang == "es" else self._es_only_stopwords
        for term, candidates in cross_lookup.items():
            pattern = r"\b" + re.escape(term) + r"\b"
            if re.search(pattern, text_lower):
                for canonical, entity_type in candidates:
                    key = f"{canonical}:{entity_type}"
                    if key not in found_entities:
                        found_entities[key] = ExtractedEntity(
                            name=canonical,
                            type=entity_type,
                            span=(0, 0),
                            source="gazetteer_crosslang",
                        )

        # 2. spaCy NER — discover entities not in the gazetteer
        self._load_ner_models()
        if self._ner_available:
            nlp = self._nlp_es if lang == "es" and self._nlp_es else self._nlp_en
            if nlp:
                ner_entities = self._extract_ner(nlp, text, found_entities, gazetteer_spans)
                for entity in ner_entities:
                    key = f"{entity.name}:{entity.type}"
                    if key not in found_entities:
                        found_entities[key] = entity
                        # Track NER discoveries for gazetteer feedback loop
                        self._track_ner_candidate(entity.name, entity.type, source_file)

        result.entities = list(found_entities.values())

        # 3. Scripture citation extraction
        for match in _SCRIPTURE_RE.finditer(text):
            ref = match.group(1).strip()
            result.scripture_refs.append(ref)
            key = f"{ref}:scripture"
            if key not in found_entities:
                result.entities.append(ExtractedEntity(
                    name=ref, type="scripture", source="regex",
                ))

        # 4. Relation extraction (co-occurrence based)
        result.relations = self._extract_relations(result.entities)

        return result

    def _extract_ner(
        self,
        nlp,
        text: str,
        found_entities: dict[str, ExtractedEntity],
        gazetteer_spans: set[tuple[int, int]],
    ) -> list[ExtractedEntity]:
        """Run spaCy NER and return entities not already found by gazetteer."""
        entities: list[ExtractedEntity] = []

        try:
            doc = nlp(text)
        except Exception:
            return entities

        # Collect all canonical names from gazetteer matches for overlap detection
        known_names_lower = set()
        for key in found_entities:
            name = key.split(":")[0]
            known_names_lower.add(name.lower())
            # Also add individual words for partial overlap detection
            for word in name.lower().split():
                if len(word) > 2:
                    known_names_lower.add(word)

        for ent in doc.ents:
            # Map spaCy label to our entity type
            entity_type = _SPACY_LABEL_MAP.get(ent.label_)
            if entity_type is None:
                continue

            name = ent.text.strip()

            # Skip if too short
            if len(name) < _MIN_ENTITY_LEN:
                continue

            # Skip common words that aren't real entities
            if name.lower() in _NER_STOPWORDS:
                continue

            # Skip if it overlaps with a gazetteer match (gazetteer takes precedence)
            if name.lower() in known_names_lower:
                continue

            # Skip purely numeric entities
            if name.replace(" ", "").isdigit():
                continue

            # Skip verse numbers that spaCy might pick up
            if re.match(r"^\d+\s+\w", name):
                continue

            # Skip entities that contain KJV/archaic verbs — NER artifacts like
            # "Mary hath", "Jacob begat Judas", "Jesus saith"
            if re.search(
                r"\b(?:hath|begat|saith|spake|smote|doth|shalt|wilt|cometh|goeth|maketh|taketh|dwelt)\b",
                name, re.IGNORECASE,
            ):
                continue

            # Clean up: remove leading numbers (verse numbers)
            name = re.sub(r"^\d+\s+", "", name).strip()
            if len(name) < _MIN_ENTITY_LEN:
                continue

            key = f"{name}:{entity_type}"
            if key not in found_entities:
                entities.append(ExtractedEntity(
                    name=name,
                    type=entity_type,
                    span=(ent.start_char, ent.end_char),
                    source="ner",
                ))

        return entities

    def _track_ner_candidate(self, name: str, entity_type: str, source_file: str) -> None:
        """Record NER-discovered entity for potential gazetteer promotion."""
        if self._ner_tracker is None:
            try:
                from alejandria.knowledge.ner_candidates import NERCandidateTracker
                self._ner_tracker = NERCandidateTracker()
            except Exception:
                self._ner_tracker = False  # type: ignore[assignment]
                return
        if self._ner_tracker is False:
            return
        try:
            self._ner_tracker.record(name, entity_type, source_file)
        except Exception:
            pass  # Don't fail extraction due to tracking issues

    def _extract_relations(self, entities: list[ExtractedEntity]) -> list[ExtractedRelation]:
        """Infer relations from co-occurring entities in the same chunk.

        Uses a two-tier approach:
        1. If a curated relation exists between two entities, use the typed relation
        2. Otherwise, fall back to type-based co-occurrence inference
        """
        relations: list[ExtractedRelation] = []
        seen: set[str] = set()

        for i, e1 in enumerate(entities):
            for e2 in entities[i + 1:]:
                if e1.name == e2.name:
                    continue

                # Tier 1: Check curated relations lookup
                pair = (e1.name.lower(), e2.name.lower())
                reverse_pair = (e2.name.lower(), e1.name.lower())
                curated = self._curated_relations.get(pair) or self._curated_relations.get(reverse_pair)

                if curated:
                    # Use the first curated relation type for this pair
                    rel_type, _props = curated[0]
                    # Determine direction: use pair order from curated data
                    if pair in self._curated_relations:
                        from_e, to_e = e1, e2
                    else:
                        from_e, to_e = e2, e1

                    key = f"{from_e.name}-{rel_type}-{to_e.name}"
                    if key not in seen:
                        relations.append(ExtractedRelation(
                            from_entity=from_e.name,
                            from_type=from_e.type,
                            relation=rel_type,
                            to_entity=to_e.name,
                            to_type=to_e.type,
                        ))
                        seen.add(key)
                    continue

                # Tier 2: Type-based co-occurrence inference
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
            return "BELONGS_TO"
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

        # Handbook entity type co-occurrence inference
        if types == frozenset(["calling", "organization"]):
            return "PRESIDES_OVER"
        if types == frozenset(["calling", "unit"]):
            return "PRESIDES_OVER"
        if types == frozenset(["calling", "ordinance"]):
            return "AUTHORIZED_TO_PERFORM"
        if types == frozenset(["calling", "council"]):
            return "MEMBER_OF"
        if types == frozenset(["organization", "unit"]):
            return "ORGANIZED_UNDER"
        if types == frozenset(["ordinance", "ordinance"]):
            return "PREREQUISITE_FOR"
        if types == frozenset(["ordinance", "concept"]):
            return "COVENANT_OF"
        if types == frozenset(["policy", "ordinance"]):
            return "GOVERNS_POLICY"
        if types == frozenset(["calling", "calling"]):
            return "REPORTS_TO"
        if types == frozenset(["unit", "unit"]):
            return "UNIT_CONTAINS"
        if types == frozenset(["organization", "organization"]):
            return "RELATED_TO"
        if types == frozenset(["program", "organization"]):
            return "ORGANIZED_UNDER"
        if types == frozenset(["document", "concept"]):
            return "RELATED_TO"

        return "CO_OCCURS_WITH"
