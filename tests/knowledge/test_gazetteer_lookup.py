"""Tests for the shared gazetteer lookup + garbage filter.

Covers R1 + R3 of the KG ingestion refactor:
    * normalize() agrees between cleanup and ingestion layers
    * is_garbage() catches every pattern R0 deletes
    * is_canonical() finds gazetteer entries case-insensitively and via aliases
    * should_skip_ner_entity() is the union of both gates
"""
from __future__ import annotations

import pytest

from alejandria.knowledge.gazetteer_lookup import (
    MAX_NAME_LEN,
    MIN_NAME_LEN,
    clear_cache,
    is_canonical,
    is_garbage,
    load_alias_lookup,
    normalize,
    should_skip_ner_entity,
)


# --------------------------------------------------------------------------- #
# normalize()
# --------------------------------------------------------------------------- #

class TestNormalize:
    def test_empty(self):
        assert normalize("") == ""
        assert normalize(None) == ""  # type: ignore[arg-type]

    def test_case_and_trim(self):
        assert normalize("  Nephi  ") == "nephi"
        assert normalize("NEPHI") == "nephi"

    def test_leading_article_english(self):
        assert normalize("The Book of Mormon") == "book of mormon"
        assert normalize("the holy ghost") == "holy ghost"

    def test_leading_article_spanish(self):
        assert normalize("El Libro de Mormón") == "libro de mormón"
        assert normalize("La Iglesia") == "iglesia"
        assert normalize("Los Nefitas") == "nefitas"
        assert normalize("Las escrituras") == "escrituras"
        assert normalize("Un profeta") == "profeta"
        assert normalize("Una bendición") == "bendición"

    def test_internal_whitespace_collapsed(self):
        assert normalize("  Book    of   Mormon  ") == "book of mormon"

    def test_nfc_unicode(self):
        # "é" can be represented as composed (U+00E9) or decomposed (e + ́).
        # normalize() should map both to the same string.
        composed = "Lehí"            # é is U+00E9
        decomposed = "Lehi\u0301"     # e + combining acute
        assert normalize(composed) == normalize(decomposed)


# --------------------------------------------------------------------------- #
# is_garbage()
# --------------------------------------------------------------------------- #

class TestIsGarbage:
    @pytest.mark.parametrize("name", ["", "   ", None])
    def test_empty(self, name):
        assert is_garbage(name) == "empty"

    def test_nul_bytes(self):
        assert is_garbage("Nephi\x00text") == "nul_bytes"

    def test_too_short(self):
        assert is_garbage("AB") == "too_short"
        assert is_garbage("Él") == "too_short"  # 2 chars

    def test_too_long(self):
        name = "x" * (MAX_NAME_LEN + 1)
        assert is_garbage(name) == "too_long"

    def test_all_punct(self):
        assert is_garbage("###") == "all_punct"
        assert is_garbage("---") == "all_punct"
        assert is_garbage("***...***") == "all_punct"

    def test_url_like(self):
        assert is_garbage("ChurchofJesusChrist.org") == "url_like"
        assert is_garbage("https://example.com/path") == "url_like"
        assert is_garbage("www.foo.com") == "url_like"
        assert is_garbage("NiñosyJóvenes.LaIglesiadeJesucristo.org") == "url_like"

    def test_archaic_verb(self):
        assert is_garbage("Mary hath spoken") == "archaic_verb"
        assert is_garbage("Jacob begat Judah") == "archaic_verb"
        assert is_garbage("Jesus saith unto them") == "archaic_verb"

    def test_xref_fragment(self):
        assert is_garbage("See ALEPH") == "xref_fragment"
        assert is_garbage("Véase PROFETA") == "xref_fragment"
        assert is_garbage("SEE Thresh") == "xref_fragment"

    def test_pronoun_stopword(self):
        assert is_garbage("Thou") == "pronoun_stopword"
        assert is_garbage("Él") is not None  # either too_short OR pronoun_stopword OK
        assert is_garbage("Ye") is not None

    def test_valid_names_pass(self):
        assert is_garbage("Nephi") is None
        assert is_garbage("Jesus Christ") is None
        assert is_garbage("La Iglesia de Jesucristo de los Santos de los Últimos Días") is None
        assert is_garbage("Alma the Younger") is None


# --------------------------------------------------------------------------- #
# is_canonical() / gazetteer lookup
# --------------------------------------------------------------------------- #

class TestIsCanonical:
    def setup_method(self):
        clear_cache()  # start each test with a fresh lookup

    def test_lookup_loads(self):
        m = load_alias_lookup()
        assert isinstance(m, dict)
        # Gazetteer must contain at least the classic BoM personae.
        # If this breaks someone trimmed the gazetteer; update the test.
        assert len(m) > 100

    def test_canonical_match(self):
        # "Nephi" is a known gazetteer entry (person type).
        hit = is_canonical("Nephi")
        assert hit is not None
        assert hit[0] == "Nephi"
        assert hit[1] == "person"

    def test_case_insensitive(self):
        assert is_canonical("nephi") is not None
        assert is_canonical("NEPHI") is not None

    def test_alias_match(self):
        # "Nefi" is the Spanish alias of "Nephi" per entities.json.
        hit = is_canonical("Nefi")
        assert hit is not None
        assert hit[0] == "Nephi"

    def test_leading_article_stripped(self):
        # If the gazetteer has "Iglesia"/aliases, these variants should hit.
        a = is_canonical("La Iglesia")
        b = is_canonical("Iglesia")
        # Either both hit (preferred) or neither — what matters is consistency.
        assert (a is None) == (b is None)

    def test_non_match_returns_none(self):
        assert is_canonical("ZZZZZZZNonexistentEntity") is None


# --------------------------------------------------------------------------- #
# should_skip_ner_entity() — the combined gate
# --------------------------------------------------------------------------- #

class TestSkipNerEntity:
    def setup_method(self):
        clear_cache()

    def test_garbage_rejected(self):
        assert should_skip_ner_entity("###") == "all_punct"
        assert should_skip_ner_entity("ChurchofJesusChrist.org") == "url_like"
        assert should_skip_ner_entity("Mary hath spoken") == "archaic_verb"

    def test_canonical_rejected(self):
        # Canonical gazetteer matches must short-circuit: they are handled
        # by the gazetteer path, not by NER.
        assert should_skip_ner_entity("Nephi") == "canonical"
        assert should_skip_ner_entity("Nefi") == "canonical"

    def test_genuinely_new_entity_allowed(self):
        # A plausible unknown name that is neither garbage nor gazetteer should
        # pass the gate. If this ever starts returning a reason, the filter
        # has become too aggressive.
        assert should_skip_ner_entity("Zapotec governor") is None
