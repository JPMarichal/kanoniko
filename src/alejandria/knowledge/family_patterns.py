"""Deterministic family-relation extraction from scripture text.

Complements `relation_extractor_llm.py`: the LLM is expensive and runs on
a subset of chunks; these patterns are cheap regex that fire on every
extraction, catching the common explicit formulations that show up over
and over in BoM/OT genealogies but that the LLM layer either missed or
was never invoked on.

Supported patterns (EN + ES):

    X, son of Y                 -> FATHER_OF(Y, X)
    X the son of Y              -> FATHER_OF(Y, X)
    X, hijo de Y                -> FATHER_OF(Y, X)
    X, daughter of Y            -> FATHER_OF(Y, X)  (if Y male; we don't know
                                                     so we emit FATHER_OF; the
                                                     LLM layer can refine)
    X, hija de Y
    X, wife of Y                -> SPOUSE_OF(Y, X)
    X, esposa de Y
    Y begat X                   -> FATHER_OF(Y, X)
    Y engendró a X

Integration: called from `KGExtractor.extract()` after entities are
resolved. Emits `ExtractedRelation` objects keyed to the detected spans.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

# Connective phrases that link an entity to its relative. Required before the
# second name so we don't accidentally match arbitrary text.
#
# Relation marker conventions:
#   FATHER_OF        — group(1) is the CHILD, group(2) is the PARENT.
#                      Emit FATHER_OF(parent=group2, child=group1).
#   FATHER_OF_FWD    — group(1) is the PARENT, group(2) is the CHILD.
#                      Emit FATHER_OF(parent=group1, child=group2).
#   MOTHER_OF_FWD    — same shape as FATHER_OF_FWD but for mothers.
#   SPOUSE_OF        — group(1) is one spouse, group(2) is the other.
#                      Emit SPOUSE_OF(group2, group1).
#   BROTHER_OF       — group(1) and group(2) are both siblings.
#                      Emit BROTHER_OF(group1, group2). Symmetry handled by
#                      the inference engine, not duplicated here.
#   SISTER_OF        — same as BROTHER_OF.
#
# Direction tag rule: any rel ending in `_FWD` means group1 → group2.
# Without `_FWD`, the principal is group2 (the parent / partner mentioned
# AFTER the connective phrase) — matching the natural English/Spanish
# phrasing "X, son of Y" / "X, esposa de Y".
_FAMILY_PATTERNS = [
    # ── EN: parent via child reference ────────────────────────────────────
    ("en", "father", r",\s+(?:the\s+)?son\s+of\s+", "FATHER_OF"),
    ("en", "father", r"\s+the\s+son\s+of\s+", "FATHER_OF"),
    ("en", "father", r",\s+(?:the\s+)?daughter\s+of\s+", "FATHER_OF"),
    ("en", "father", r"\s+the\s+daughter\s+of\s+", "FATHER_OF"),
    # ── EN: parent via parent reference (X, father/mother of Y) ───────────
    ("en", "father_fwd", r",\s+(?:the\s+)?father\s+of\s+", "FATHER_OF_FWD"),
    ("en", "father_fwd", r"\s+the\s+father\s+of\s+", "FATHER_OF_FWD"),
    ("en", "mother_fwd", r",\s+(?:the\s+)?mother\s+of\s+", "MOTHER_OF_FWD"),
    ("en", "mother_fwd", r"\s+the\s+mother\s+of\s+", "MOTHER_OF_FWD"),
    # ── EN: spouse ────────────────────────────────────────────────────────
    ("en", "spouse", r",\s+(?:the\s+)?wife\s+of\s+", "SPOUSE_OF"),
    ("en", "spouse", r",\s+(?:the\s+)?husband\s+of\s+", "SPOUSE_OF"),
    # ── EN: siblings ─────────────────────────────────────────────────────
    ("en", "sibling_m", r",\s+(?:the\s+)?brother\s+of\s+", "BROTHER_OF"),
    ("en", "sibling_m", r"\s+the\s+brother\s+of\s+", "BROTHER_OF"),
    ("en", "sibling_f", r",\s+(?:the\s+)?sister\s+of\s+", "SISTER_OF"),
    ("en", "sibling_f", r"\s+the\s+sister\s+of\s+", "SISTER_OF"),
    # ── EN: begat ────────────────────────────────────────────────────────
    ("en", "father_fwd", r"\s+begat\s+", "FATHER_OF_FWD"),
    # ── ES: parent via child reference ───────────────────────────────────
    ("es", "father", r",\s+hijo\s+de\s+", "FATHER_OF"),
    ("es", "father", r",\s+hija\s+de\s+", "FATHER_OF"),
    ("es", "father", r"\s+(?:el\s+)?hijo\s+de\s+", "FATHER_OF"),
    ("es", "father", r"\s+(?:la\s+)?hija\s+de\s+", "FATHER_OF"),
    # ── ES: parent via parent reference (X, padre/madre de Y) ────────────
    ("es", "father_fwd", r",\s+(?:el\s+)?padre\s+de\s+", "FATHER_OF_FWD"),
    ("es", "father_fwd", r"\s+(?:el\s+)?padre\s+de\s+", "FATHER_OF_FWD"),
    ("es", "mother_fwd", r",\s+(?:la\s+)?madre\s+de\s+", "MOTHER_OF_FWD"),
    ("es", "mother_fwd", r"\s+(?:la\s+)?madre\s+de\s+", "MOTHER_OF_FWD"),
    # ── ES: spouse ───────────────────────────────────────────────────────
    ("es", "spouse", r",\s+(?:la\s+)?esposa\s+de\s+", "SPOUSE_OF"),
    ("es", "spouse", r",\s+(?:el\s+)?esposo\s+de\s+", "SPOUSE_OF"),
    ("es", "spouse", r",\s+(?:la\s+)?mujer\s+de\s+", "SPOUSE_OF"),
    # ── ES: siblings ─────────────────────────────────────────────────────
    ("es", "sibling_m", r",\s+(?:el\s+)?hermano\s+de\s+", "BROTHER_OF"),
    ("es", "sibling_m", r"\s+(?:el\s+)?hermano\s+de\s+", "BROTHER_OF"),
    ("es", "sibling_f", r",\s+(?:la\s+)?hermana\s+de\s+", "SISTER_OF"),
    ("es", "sibling_f", r"\s+(?:la\s+)?hermana\s+de\s+", "SISTER_OF"),
    # ── ES: engendró ─────────────────────────────────────────────────────
    ("es", "father_fwd", r"\s+engendró\s+a\s+", "FATHER_OF_FWD"),
    ("es", "father_fwd", r"\s+engendró\s+à\s+", "FATHER_OF_FWD"),  # OCR variant
]

@dataclass(frozen=True)
class FamilyHit:
    """A detected family relation in text, before entity-name resolution."""
    from_name: str  # the parent / spouse
    to_name: str    # the child / spouse
    relation: str   # FATHER_OF / SPOUSE_OF
    span: tuple[int, int]


# A "name" here is capitalized words; we do NOT use IGNORECASE because the
# initial capital is the primary signal for proper-noun detection. Cap at
# 4 words to avoid runaway matches. Letter class accepts Latin-1 accented
# forms used in the corpus.
_NAME_RE = (
    r"[A-ZÁÉÍÓÚÑÇ][A-Za-zÁÉÍÓÚÑáéíóúñÇç\-']{1,30}"
    r"(?:\s+[A-ZÁÉÍÓÚÑÇ][A-Za-zÁÉÍÓÚÑáéíóúñÇç\-']{1,30}){0,3}"
)

# Function words that sometimes start a captured "name" because they begin a
# sentence (And, But, Now, Luego, Entonces …). We strip them off the front
# of each captured name before emitting.
_LEADING_STRIP_RE = re.compile(
    r"^(?:And|But|Now|Then|For|So|Yet|Also|O|Behold|Verily|"
    r"Likewise|Otherwise|Furthermore|Moreover|However|Nevertheless|"
    r"Thus|Hence|Therefore|Meanwhile|Besides|Indeed|Truly|Wherefore|"
    r"Y|Pero|Entonces|Luego|Porque|Mas|Sino|Asimismo|Además|"
    r"Por\s+(?:lo\s+)?tanto|Por\s+eso|Por\s+ende|Al\s+contrario|"
    r"Sin\s+embargo|No\s+obstante|"
    r"He\s+aquí)\s+"
)

# Non-person indicator words. If a captured "name" STARTS with one of these,
# the capture is almost certainly a place, epithet, or title — not a person.
# These leak in because NER picks up any capitalized phrase.
_NON_PERSON_PREFIXES = frozenset({
    # English places/titles
    "Mount", "City", "Land", "Valley", "River", "Sea", "Lake", "Plains",
    "North", "South", "East", "West", "Great", "Lesser", "New", "Old",
    "Upper", "Lower", "King", "Queen", "Lord", "Sir", "Lady", "Saint",
    "Prince", "Princess", "Captain", "General", "Elder", "Brother",
    "Sister", "Father", "Mother",
    # Spanish places/titles
    "Monte", "Ciudad", "Tierra", "Valle", "Río", "Mar", "Lago", "Llanura",
    "Norte", "Sur", "Este", "Oeste", "Grande", "Menor", "Nueva", "Nuevo",
    "Viejo", "Alto", "Bajo", "Rey", "Reina", "Señor", "Señora", "San",
    "Santa", "Príncipe", "Princesa", "Capitán", "General",
    # Nationality/ethnonym words NER captures as names
    "Syrian", "SYRIAN", "Egyptian", "Greek", "Roman", "Jew", "Jewish",
    "Sirio", "Egipcio", "Griego", "Romano", "Judío",
    "Reubenite", "Reubenites", "Rubenita",
})


def _is_person_candidate(name: str) -> bool:
    """Return False if `name` is obviously not a person — ALL CAPS fragment,
    place/title prefix, single-char token, etc."""
    if not name:
        return False
    # Reject if all tokens are uppercase AND length > 3 (WILLIAM, SYRIAN…)
    tokens = name.split()
    if tokens and all(t.isupper() and len(t) > 1 for t in tokens):
        return False
    # Reject if first token is a non-person indicator
    first = tokens[0] if tokens else ""
    if first in _NON_PERSON_PREFIXES:
        return False
    # Accept
    return True


def _build_search_re(prefix: str) -> re.Pattern:
    """Build a regex that captures (child, parent) around a family-prefix phrase.

    Names are case-sensitive (must start capitalized); the connective phrase
    is made case-insensitive via an inline flag on just that segment.
    """
    return re.compile(rf"({_NAME_RE})(?i:{prefix})({_NAME_RE})")


_SEARCH_PATTERNS = [
    (lang, kind, _build_search_re(rx), rel)
    for (lang, kind, rx, rel) in _FAMILY_PATTERNS
]


_CONJUNCTION_ONLY = frozenset({
    "And", "But", "Now", "Then", "For", "So", "Yet", "Also",
    "Behold", "Verily",
    "Y", "Pero", "Entonces", "Luego", "Porque", "Mas", "Sino",
    "Shared", "Named",  # past-tense verbs NER occasionally capitalizes
})


def _clean(name: str) -> str:
    """Strip leading sentence-starter conjunctions from a captured name.

    Returns an empty string if the cleaned name is itself a bare conjunction
    (e.g. text like "the brother of And he…" where the capture is just "And"
    without a trailing word — no regex strip can fire). Empty return rejects
    the hit at the caller.
    """
    s = name.strip()
    # Apply twice to catch chained "And Now X" sequences.
    for _ in range(2):
        s = _LEADING_STRIP_RE.sub("", s).strip()
    if s in _CONJUNCTION_ONLY:
        return ""
    return s


def extract_family_hits(text: str) -> list[FamilyHit]:
    """Scan `text` for explicit family-relation formulas, return the hits.

    The caller is responsible for resolving each name to a canonical entity
    in its gazetteer/NER; this layer is purely pattern-based.
    """
    hits: list[FamilyHit] = []
    for (_lang, _kind, rx, rel) in _SEARCH_PATTERNS:
        for m in rx.finditer(text):
            left = _clean(m.group(1))
            right = _clean(m.group(2))
            if not left or not right or left.lower() == right.lower():
                continue
            # Reject non-person captures (ALL CAPS, place prefix, title).
            if not _is_person_candidate(left) or not _is_person_candidate(right):
                continue
            # Reject same-person fragments: one name is a substring of the
            # other after lowercase comparison (e.g. "Smith" vs "Joseph Smith").
            ll, rl = left.lower(), right.lower()
            if ll != rl and (ll in rl or rl in ll):
                continue
            # Reject "brother of Jared" epithet — in the BoM, "the brother of
            # Jared" is a standing title (Mahonri Moriancumer). Any pair with
            # Jared as the SIBLING here is almost certainly the epithet
            # cascading; real sibling pairs for Jared (e.g. with his actual
            # relatives) are extremely rare.
            if rel in {"BROTHER_OF", "SISTER_OF"} and right == "Jared":
                continue
            # Direction: `_FWD` means group1 → group2 ("X begat Y", "X, father of Y");
            # symmetric rels (BROTHER_OF, SISTER_OF) keep group1 → group2 too;
            # default ("X, son of Y", "X, wife of Y") flips so the principal
            # mentioned after the connective phrase ends up as `from_name`.
            if rel.endswith("_FWD"):
                base = rel[:-4]
                hits.append(FamilyHit(
                    from_name=left, to_name=right,
                    relation=base, span=m.span(),
                ))
            elif rel in {"BROTHER_OF", "SISTER_OF"}:
                hits.append(FamilyHit(
                    from_name=left, to_name=right,
                    relation=rel, span=m.span(),
                ))
            else:
                hits.append(FamilyHit(
                    from_name=right, to_name=left,
                    relation=rel, span=m.span(),
                ))
    # Deduplicate: same (from, to, relation), keep earliest span.
    seen = {}
    for h in hits:
        key = (h.from_name.lower(), h.to_name.lower(), h.relation)
        if key not in seen or h.span[0] < seen[key].span[0]:
            seen[key] = h
    return list(seen.values())


__all__ = ["FamilyHit", "extract_family_hits"]
