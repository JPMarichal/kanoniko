"""Shared gazetteer alias lookup + garbage filter for the ingestion pipeline.

Why this exists: R1 + R3 of the KG ingestion refactor
(see docs/kg-ingestion-refactor.md). Three places used to contain
overlapping copies of gazetteer / garbage logic:

    * knowledge/neo4j_client.py::_build_alias_lookup
    * storage/postgres/kg_cleanup.py::load_gazetteer_canonical_map + _normalize
    * knowledge/extractor.py (inline regexes for archaic verbs, URLs, etc.)

Consolidating them here means:
    * one normalize() — kg_cleanup and ingestion agree on what's "the same name"
    * one garbage filter — cleanup deletes exactly what ingestion refuses to create
    * one gazetteer map — same canonical truth everywhere, cached once per process

All functions are safe to import at module load time — the gazetteer file is
read lazily via lru_cache, so the cost is paid on first call.
"""
from __future__ import annotations

import json
import re
import string
import unicodedata
from functools import lru_cache
from pathlib import Path

_GAZETTEER_PATH = Path(__file__).parent / "gazetteers" / "entities.json"

# Min/max reasonable entity name length. Matches R0 cleanup rules.
MIN_NAME_LEN = 3
MAX_NAME_LEN = 80

_LEADING_ARTICLE_RE = re.compile(
    r"^(the|el|la|los|las|un|una)\s+",
    flags=re.IGNORECASE,
)

# URL-like patterns: catches http(s)://, www., and common domain suffixes even
# without a scheme (e.g. ChurchofJesusChrist.org).
_URL_RE = re.compile(
    r"(https?://|www\.|[A-Za-z0-9][A-Za-z0-9-]*\.(org|com|net|edu|gov|io)\b)",
    flags=re.IGNORECASE,
)

# Archaic KJV/LDS-scripture verbs that NER confuses with entity names
# (e.g. "Mary hath spoken", "Jacob begat Judah").
_ARCHAIC_VERBS = (
    "hath", "saith", "spake", "smote", "doth", "shalt", "wilt",
    "cometh", "goeth", "maketh", "taketh", "dwelt", "begat",
)
_ARCHAIC_VERB_RE = re.compile(
    r"\b(" + "|".join(_ARCHAIC_VERBS) + r")\b",
    flags=re.IGNORECASE,
)

# Common pronouns / tokens that NER sometimes tags as entities in scripture.
_PRONOUN_STOPWORDS = frozenset({
    "thou", "thee", "thy", "thine", "ye", "he", "she", "it",
    "him", "her", "us", "we", "they", "them",
    "el", "él", "ella", "ellos", "ellas", "nos", "nosotros",
    "yo", "tú", "tu", "su", "mi", "me", "te", "se",
})

# Cross-reference fragments that should never become entities.
_XREF_PREFIX_RE = re.compile(r"^(see |véase )", flags=re.IGNORECASE)

# Scripture reference patterns: "Matthew 3:3", "1 Nephi 3:7", "Alma 55:17",
# "Jer 38:21", "DyC 76:22-24", "Nahum 2", "Lucas 13:11–17". The NER layer
# frequently emits these as `person` or `object` nodes — they pollute ~6 % of
# the person sample and ~9 % of objects (see docs/kg-noise-diagnostic.md).
_SCRIPTURE_BOOK_RE = (
    r"(?:"
    r"gen(?:esis)?|génesis|exod(?:us|o)?|ex|éxodo|lev(?:iticus|[íi]tico)?|"
    r"num(?:bers|eros)?|n[uú]meros|deut(?:eronom(?:y|io))?|"
    r"josh(?:ua)?|josu[ée]|judg(?:es)?|jueces|ruth|rut|"
    r"sam(?:uel)?|k(?:in)?gs?|reyes|chr(?:on(?:icles)?)?|cr[oó]n(?:icas)?|"
    r"ezra|esdras|neh(?:emiah|em[íi]as)?|esth(?:er)?|ester|job|"
    r"ps(?:alms?|\.)?|salmos?|prov(?:erbs|erbios)?|eccl(?:esiastes|esiast[eé]s)?|"
    r"song(?:s)?|cant(?:ares)?|isa(?:iah|[íi]as)?|jer(?:emiah|em[íi]as)?|"
    r"lam(?:entations|entaciones)?|ezek(?:iel)?|ezequiel|dan(?:iel)?|"
    r"hos(?:ea)?|oseas|joel|amos|am[oó]s|obad(?:iah|[íi]as)?|abd[íi]as|"
    r"jon(?:ah|[aá]s)?|mic(?:ah)?|miqueas|nah(?:um|[uú]m)?|hab(?:akkuk|acuc)?|"
    r"zeph(?:aniah)?|sofon[íi]as|hag(?:gai|eo)?|zech(?:ariah)?|zec|"
    r"zacar[íi]as|mal(?:achi|aqu[íi]as)?|"
    r"matt(?:hew)?|mt|mateo|mark|mk|marcos|luke|lk|lucas|john|jn|juan|"
    r"acts|hechos|rom(?:ans|anos)?|ro|cor(?:inthians|intios)?|"
    r"gal(?:atians|atas|átas)?|eph(?:esians|esios)?|phil(?:ippians|ipenses)?|"
    r"col(?:ossians|osenses)?|thess(?:alonians)?|tesalonicenses|"
    r"tim(?:othy|oteo)?|tit(?:us|o)?|phlm|filem[oó]n|"
    r"heb(?:rews|reos)?|jas|james|jms|santiago|pet(?:er)?|pedro|jude|judas|"
    r"rev(?:elation)?|rv|apocalipsis|"
    r"nephi|nefi|jacob|enos|en[óo]s|jarom|omni|mosiah|mos[íi]ah|alma|"
    r"hel(?:aman|am[áa]n)?|mormon|morm[óo]n|ether|[éeE]ter|moroni|"
    r"d(?:&|y)c|dc|dyc|moses|mois[ée]s|abr(?:aham)?|jsh|jsm|js-h|js-m"
    r")"
)
_SCRIPTURE_REF_RE = re.compile(
    rf"^\s*(?:read\s+|ver\s+|véase\s+|see\s+)?(?:\d\s+)?{_SCRIPTURE_BOOK_RE}"
    r"\.?\s+\d+(?:[:\.\-–]\s*\d+)?",
    flags=re.IGNORECASE,
)

# Mojibake: UTF-8 bytes that were double-decoded as latin-1 / cp1252. Common
# shapes: "â€™", "â€œ", "Ã¡", "Ã©", "Ã³", "Â­" (soft hyphen), "ÏÎ±Î³" (Greek
# through latin-1). We reject entities containing ≥2 of these glyphs — a
# single "â" can appear legitimately in names like "María Ángel" when mis-
# normalized, so we require clustering.
_MOJIBAKE_PAIR_RE = re.compile(
    r"Ã[¡¢£¤¥¦§¨©ª«®¯°±²³´µ¶·¸¹º»Ã]|â€[™œ\u009d\u009ctm\s]|Â[­·¦¥]|Ï[Î€¬†]|[ÏÎ]{2,}"
)

# HTML/markup fragments that escaped the parser: open/close tags, inline
# attributes, stray entity-encoded strings.
_HTML_RE = re.compile(
    r"<\s*/?\s*[a-z][a-z0-9]*(?:\s+[^>]*)?>|"
    r"\b(?:id|class|href|src|rel|style|data-\w+)\s*=\s*[\"']|"
    r"&(?:amp|lt|gt|quot|nbsp|#\d+);"
)


# --------------------------------------------------------------------------- #
# Normalization — shared by cleanup and ingestion
# --------------------------------------------------------------------------- #

def normalize(name: str) -> str:
    """Normalize an entity name for equality / gazetteer lookup.

    Steps: NFC, strip + lowercase, drop leading article (the/el/la/los/las/
    un/una), collapse internal whitespace. Same function used by R0 cleanup so
    the two layers agree on what "equal" means.
    """
    if not name:
        return ""
    s = unicodedata.normalize("NFC", name).strip().lower()
    s = _LEADING_ARTICLE_RE.sub("", s)
    s = re.sub(r"\s+", " ", s)
    return s


# --------------------------------------------------------------------------- #
# Gazetteer lookup
# --------------------------------------------------------------------------- #

@lru_cache(maxsize=1)
def load_alias_lookup() -> dict[str, tuple[str, str]]:
    """Return dict[normalize(alias_or_name)] = (canonical_name, canonical_type).

    Read once per process; the gazetteer file rarely changes at runtime.
    """
    out: dict[str, tuple[str, str]] = {}
    if not _GAZETTEER_PATH.exists():
        return out
    try:
        data = json.loads(_GAZETTEER_PATH.read_text(encoding="utf-8"))
    except Exception:
        return out
    for etype, entries in data.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            canonical = entry.get("name", "")
            if not canonical:
                continue
            key = normalize(canonical)
            if key and key not in out:
                out[key] = (canonical, etype)
            for alias in entry.get("aliases") or []:
                akey = normalize(alias)
                if akey and akey not in out:
                    out[akey] = (canonical, etype)
    return out


def is_canonical(name: str) -> tuple[str, str] | None:
    """Return (canonical_name, canonical_type) if ``name`` matches a gazetteer
    entry or alias after normalization; else None."""
    if not name:
        return None
    return load_alias_lookup().get(normalize(name))


def clear_cache() -> None:
    """Invalidate the alias lookup cache (used after promoting a new entity
    to the gazetteer at runtime, and in tests)."""
    load_alias_lookup.cache_clear()


# --------------------------------------------------------------------------- #
# Garbage filter — shared with R0 cleanup criteria
# --------------------------------------------------------------------------- #

def is_garbage(name: str) -> str | None:
    """Return the rejection reason if ``name`` is garbage, else None.

    Criteria mirror the R0 cleanup rules in
    ``storage/postgres/kg_cleanup.py`` so that what cleanup deletes is
    exactly what ingestion refuses to create.

    Reasons (stable strings):
        empty, nul_bytes, too_short, too_long, all_punct, url_like,
        archaic_verb, xref_fragment, pronoun_stopword, scripture_ref,
        mojibake, html_fragment.
    """
    if name is None or not name.strip():
        return "empty"
    if "\x00" in name:
        return "nul_bytes"

    stripped = name.strip()
    length = len(stripped)
    if length < MIN_NAME_LEN:
        return "too_short"
    if length > MAX_NAME_LEN:
        return "too_long"

    # All-punctuation / whitespace: no alphanumeric chars at all.
    if not any(ch.isalnum() for ch in stripped):
        return "all_punct"

    if _URL_RE.search(stripped):
        return "url_like"

    if _HTML_RE.search(stripped):
        return "html_fragment"

    if _MOJIBAKE_PAIR_RE.search(stripped):
        return "mojibake"

    if _SCRIPTURE_REF_RE.match(stripped):
        return "scripture_ref"

    if _ARCHAIC_VERB_RE.search(stripped):
        return "archaic_verb"

    if _XREF_PREFIX_RE.match(stripped):
        return "xref_fragment"

    if stripped.lower() in _PRONOUN_STOPWORDS:
        return "pronoun_stopword"

    return None


# --------------------------------------------------------------------------- #
# Combined ingestion gate
# --------------------------------------------------------------------------- #

def should_skip_ner_entity(name: str) -> str | None:
    """Return a reason string if the NER-extracted name should NOT become a
    new entity node / candidate; None if it's safe to emit.

    Reasons: the ``is_garbage`` reasons, plus ``canonical`` if the name matches
    a gazetteer entry and therefore should be handled by the gazetteer path,
    not re-created as a fresh node.
    """
    reason = is_garbage(name)
    if reason is not None:
        return reason
    if is_canonical(name) is not None:
        return "canonical"
    return None


__all__ = [
    "MIN_NAME_LEN",
    "MAX_NAME_LEN",
    "clear_cache",
    "is_canonical",
    "is_garbage",
    "load_alias_lookup",
    "normalize",
    "should_skip_ner_entity",
]
