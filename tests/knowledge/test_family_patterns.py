"""Tests for deterministic family-relation extraction.

See docs/kg-noise-diagnostic.md §priority 2 — regex patterns complementing
the LLM relation extractor for obvious genealogical formulas that were
otherwise missed (Amaleki / Abinadom gap in Omni 1, etc.).
"""
from __future__ import annotations

import pytest

from alejandria.knowledge.family_patterns import FamilyHit, extract_family_hits


class TestSonOfPatterns:
    def test_comma_son_of_en(self):
        hits = extract_family_hits("Amaleki, son of Abinadom, wrote the record.")
        assert any(
            h.from_name == "Abinadom" and h.to_name == "Amaleki"
            and h.relation == "FATHER_OF"
            for h in hits
        )

    def test_comma_hijo_de_es(self):
        hits = extract_family_hits("Yo, Amalekí, hijo de Abinadom, escribí.")
        assert any(
            h.from_name == "Abinadom" and h.to_name == "Amalekí"
            and h.relation == "FATHER_OF"
            for h in hits
        )

    def test_the_son_of(self):
        hits = extract_family_hits("Nephi the son of Lehi returned to Jerusalem.")
        assert any(
            h.from_name == "Lehi" and h.to_name == "Nephi"
            and h.relation == "FATHER_OF"
            for h in hits
        )

    def test_daughter_of(self):
        hits = extract_family_hits("Sarah, daughter of Asher, bore children.")
        assert any(
            h.from_name == "Asher" and h.to_name == "Sarah"
            and h.relation == "FATHER_OF"
            for h in hits
        )

    def test_hija_de(self):
        hits = extract_family_hits("Sara, hija de Aser, tuvo hijos.")
        assert any(h.from_name == "Aser" and h.to_name == "Sara"
                   and h.relation == "FATHER_OF" for h in hits)


class TestSpousePatterns:
    def test_wife_of(self):
        hits = extract_family_hits("Sariah, wife of Lehi, departed.")
        assert any(h.from_name == "Lehi" and h.to_name == "Sariah"
                   and h.relation == "SPOUSE_OF" for h in hits)

    def test_esposa_de(self):
        hits = extract_family_hits("Saríah, esposa de Lehi, salió.")
        assert any(h.from_name == "Lehi" and h.to_name == "Saríah"
                   and h.relation == "SPOUSE_OF" for h in hits)

    def test_husband_of(self):
        hits = extract_family_hits("Lehi, husband of Sariah, was righteous.")
        assert any(h.from_name == "Sariah" and h.to_name == "Lehi"
                   and h.relation == "SPOUSE_OF" for h in hits)


class TestBegatPatterns:
    def test_begat_en(self):
        # "Abraham begat Isaac" → FATHER_OF(Abraham, Isaac)
        hits = extract_family_hits("And Abraham begat Isaac.")
        assert any(h.from_name == "Abraham" and h.to_name == "Isaac"
                   and h.relation == "FATHER_OF" for h in hits)

    def test_engendro_es(self):
        hits = extract_family_hits("Abraham engendró a Isaac.")
        assert any(h.from_name == "Abraham" and h.to_name == "Isaac"
                   and h.relation == "FATHER_OF" for h in hits)


class TestNegatives:
    def test_generic_prose_no_hits(self):
        assert extract_family_hits("The weather was pleasant.") == []

    def test_dedup_same_pair(self):
        # Same relation phrased twice — should deduplicate.
        text = ("Nephi the son of Lehi went. Later, Nephi, son of Lehi, "
                "returned.")
        hits = extract_family_hits(text)
        lehi_nephi = [
            h for h in hits
            if h.from_name == "Lehi" and h.to_name == "Nephi"
        ]
        assert len(lehi_nephi) == 1

    def test_self_reference_rejected(self):
        # Spurious regex match where X and Y are the same name → drop.
        hits = extract_family_hits("Juan, hijo de Juan, llegó.")
        assert not any(h.from_name == "Juan" and h.to_name == "Juan"
                       for h in hits)


class TestMultipleEntities:
    def test_multi_hits_in_passage(self):
        # Classic BoM lineage in Omni 1.
        text = (
            "Amarón entregó las planchas a Quemis, su hermano. Quemis, "
            "hijo de Jaron, las guardó. Después, Abinadom, hijo de Quemis, "
            "las recibió. Yo, Amalekí, hijo de Abinadom, escribo."
        )
        hits = extract_family_hits(text)
        pairs = {(h.from_name, h.to_name) for h in hits if h.relation == "FATHER_OF"}
        assert ("Jaron", "Quemis") in pairs
        assert ("Quemis", "Abinadom") in pairs
        assert ("Abinadom", "Amalekí") in pairs
