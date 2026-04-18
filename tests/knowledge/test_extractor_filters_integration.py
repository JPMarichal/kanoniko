"""Integration tests for the R1+R3 filters wired into KGExtractor.

Purpose: the unit tests in ``test_gazetteer_lookup.py`` prove that
``should_skip_ner_entity()`` rejects the right patterns. These tests prove
that the filter is **actually called** inside ``KGExtractor._extract_ner``.

If a future refactor accidentally unhooks the filter, these tests fail;
the unit tests would still pass, hiding the regression.

Each test constructs text where spaCy historically emitted contaminated
NER entities (confirmed by inspection of the live Neo4j before R0), and
asserts those no longer appear in ``result.entities``.
"""
from __future__ import annotations

import pytest

from alejandria.knowledge.extractor import KGExtractor


def _ner_only(result) -> list:
    """Return only NER-sourced entities (exclude gazetteer hits)."""
    return [e for e in result.entities if e.source == "ner"]


def _ner_names_lower(result) -> set[str]:
    return {e.name.lower() for e in _ner_only(result)}


# --------------------------------------------------------------------------- #
# Canonical gazetteer duplicates must NOT emerge as NER nodes
# --------------------------------------------------------------------------- #

def test_jesucristo_is_consumed_by_gazetteer_not_emitted_by_ner() -> None:
    """'Jesucristo' is a Spanish alias of 'Jesus Christ' in the gazetteer.
    Pre-R1, spaCy emitted a separate NER entity when it found it; post-R1 the
    filter skips it, and the gazetteer handles the canonical form."""
    extractor = KGExtractor()
    result = extractor.extract(
        "El profeta Nefi habló de Jesucristo y su obra redentora."
    )
    ner_names = _ner_names_lower(result)
    assert "jesucristo" not in ner_names, \
        "Jesucristo must not leak through NER — it is a gazetteer alias"


@pytest.mark.xfail(
    reason=(
        "Gazetteer currently has 'Church of Jesus Christ of Latter-day Saints' "
        "with aliases 'La Iglesia de Jesucristo de los Santos de los Últimos Días', "
        "'LDS Church', 'Iglesia SUD' — but NOT the standalone 'Iglesia' / 'La Iglesia'. "
        "Spanish texts routinely use the short form; R4 (procedure_corpus_addition) "
        "requires curators to add such aliases at gazetteer pre-seed time. "
        "When the gazetteer is extended, this xfail flips to XPASSED and is a signal "
        "to promote the test to a regular assertion."
    ),
    strict=True,
)
def test_iglesia_short_form_should_be_consumed_by_gazetteer() -> None:
    """Known gap: 'Iglesia' (short form) isn't in the gazetteer as an alias for
    the Church entity. Until R4 work closes that gap, NER can emit it."""
    extractor = KGExtractor()
    result = extractor.extract(
        "La Iglesia enseña el evangelio a través de sus profetas."
    )
    ner_names = _ner_names_lower(result)
    assert "iglesia" not in ner_names
    assert "la iglesia" not in ner_names


# --------------------------------------------------------------------------- #
# Archaic verb / KJV-fragment artifacts
# --------------------------------------------------------------------------- #

def test_archaic_verbs_never_in_ner_names() -> None:
    """Pre-R1 NER emitted things like 'Mary hath', 'Jacob begat Judas',
    'Jesus saith unto them'. The archaic_verb filter rejects these."""
    extractor = KGExtractor()
    result = extractor.extract(
        "And Mary hath said these things. Jacob begat Judah who spake often."
    )
    for e in _ner_only(result):
        lower = e.name.lower()
        for v in ("hath", "begat", "saith", "spake", "smote", "doth",
                  "shalt", "wilt", "cometh", "goeth", "maketh", "taketh",
                  "dwelt"):
            assert v not in lower.split(), (
                f"Archaic verb {v!r} leaked into NER entity {e.name!r}"
            )


# --------------------------------------------------------------------------- #
# URL-like fragments
# --------------------------------------------------------------------------- #

def test_urls_never_in_ner_names() -> None:
    """Pre-R1 we observed entities like ChurchofJesusChrist.org,
    FSY.ChurchofJesusChrist.org. The url_like filter rejects any name that
    matches an HTTP prefix, www., or a domain-suffix pattern."""
    extractor = KGExtractor()
    result = extractor.extract(
        "See ChurchofJesusChrist.org for resources or visit https://example.org."
    )
    for e in _ner_only(result):
        lower = e.name.lower()
        assert ".org" not in lower
        assert ".com" not in lower
        assert "www." not in lower
        assert "http" not in lower


# --------------------------------------------------------------------------- #
# Pronouns / stopwords
# --------------------------------------------------------------------------- #

def test_english_pronouns_never_in_ner_names() -> None:
    extractor = KGExtractor()
    result = extractor.extract("Thou shalt love thy neighbor. Ye are the salt.")
    ner_names = _ner_names_lower(result)
    for stopword in ("thou", "ye", "thy", "thine", "thee"):
        assert stopword not in ner_names


def test_spanish_pronouns_never_in_ner_names() -> None:
    extractor = KGExtractor()
    result = extractor.extract("Él habló y ellos escucharon. Su palabra perdura.")
    ner_names = _ner_names_lower(result)
    for stopword in ("él", "ellos", "ellas", "tú", "su"):
        assert stopword not in ner_names


# --------------------------------------------------------------------------- #
# Punctuation garbage and length outliers
# --------------------------------------------------------------------------- #

def test_pure_punctuation_never_in_ner_names() -> None:
    """'###' as object type was observed in the live KG (52k mentions). The
    all_punct filter rejects any string with no alphanumeric chars."""
    extractor = KGExtractor()
    result = extractor.extract("Section divider: ### and later: ---")
    for e in _ner_only(result):
        assert any(ch.isalnum() for ch in e.name), (
            f"All-punctuation entity leaked: {e.name!r}"
        )


def test_overlong_names_never_in_ner() -> None:
    """Run-on phrases (>80 chars) like old TOC titles should be rejected
    before emission."""
    extractor = KGExtractor()
    # Construct pathological text that previously produced long NER runs.
    text = (
        "St. Louis.--Fine scenery.--Visit relatives.--Poem.--Obtain genealogies.--"
        "Acknowledgment of the Lord's kind providences.--Commence an evening school."
    )
    result = extractor.extract(text)
    for e in _ner_only(result):
        assert len(e.name) <= 80, f"Overlong NER entity: {e.name!r} ({len(e.name)})"
