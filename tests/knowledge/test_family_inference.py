"""Tests for family-relation closure rules.

See `src/alejandria/knowledge/family_inference.py` for the rule statement.
"""
from __future__ import annotations

from alejandria.knowledge.family_inference import FamilyEdge, infer


def _edges(pairs):
    """Convenience: build a set of FamilyEdges from (from, rel, to) tuples."""
    return {FamilyEdge(f, r, t) for f, r, t in pairs}


class TestSymmetry:
    def test_brother_symmetric(self):
        seed = _edges([("Aaron", "BROTHER_OF", "Moses")])
        closure, derived = infer(seed)
        assert FamilyEdge("Moses", "BROTHER_OF", "Aaron") in closure
        # The mirror appears among derived
        assert any(d.relation == "BROTHER_OF" and d.from_name == "Moses"
                   for d in derived)

    def test_spouse_symmetric(self):
        seed = _edges([("Abraham", "SPOUSE_OF", "Sarah")])
        closure, _ = infer(seed)
        assert FamilyEdge("Sarah", "SPOUSE_OF", "Abraham") in closure

    def test_father_NOT_symmetric(self):
        seed = _edges([("Abraham", "FATHER_OF", "Isaac")])
        closure, _ = infer(seed)
        assert not any(
            e.from_name == "Isaac" and e.relation == "FATHER_OF"
            and e.to_name == "Abraham"
            for e in closure
        )


class TestSiblingImpliesParent:
    def test_brother_inherits_parent(self):
        # Quemis is brother of Amarón; Omni is father of Amarón.
        # Therefore Omni is father of Quemis.
        seed = _edges([
            ("Quemis", "BROTHER_OF", "Amarón"),
            ("Omni", "FATHER_OF", "Amarón"),
        ])
        closure, derived = infer(seed)
        assert FamilyEdge("Omni", "FATHER_OF", "Quemis") in closure
        assert any(
            d.from_name == "Omni" and d.to_name == "Quemis"
            and "BROTHER_OF" in d.reason
            for d in derived
        )

    def test_sister_inherits_parent(self):
        seed = _edges([
            ("Miriam", "SISTER_OF", "Moses"),
            ("Amram", "FATHER_OF", "Moses"),
        ])
        closure, _ = infer(seed)
        assert FamilyEdge("Amram", "FATHER_OF", "Miriam") in closure

    def test_brother_does_NOT_inherit_mother(self):
        """Polygamy: half-siblings share the father but often have different
        mothers. Ishmael (by Hagar) and Isaac (by Sarah) are both sons of
        Abraham. BROTHER_OF(Ishmael, Isaac) ∧ MOTHER_OF(Sarah, Isaac) must
        NOT infer MOTHER_OF(Sarah, Ishmael) — that's factually wrong."""
        seed = _edges([
            ("Ishmael", "BROTHER_OF", "Isaac"),
            ("Sarah", "MOTHER_OF", "Isaac"),
            ("Abraham", "FATHER_OF", "Isaac"),
        ])
        closure, _ = infer(seed)
        # Father propagates (shared under polygamy):
        assert FamilyEdge("Abraham", "FATHER_OF", "Ishmael") in closure
        # Mother does NOT propagate:
        assert FamilyEdge("Sarah", "MOTHER_OF", "Ishmael") not in closure

    def test_chained_inference_closes(self):
        # Symmetry creates BROTHER_OF in both directions, so the parent
        # edge is derived in both runs without infinite loop.
        seed = _edges([
            ("Quemis", "BROTHER_OF", "Amarón"),
            ("Omni", "FATHER_OF", "Amarón"),
        ])
        closure, _ = infer(seed)
        # Both direct edges and their inferred consequences
        assert FamilyEdge("Quemis", "BROTHER_OF", "Amarón") in closure
        assert FamilyEdge("Amarón", "BROTHER_OF", "Quemis") in closure
        assert FamilyEdge("Omni", "FATHER_OF", "Quemis") in closure
        assert FamilyEdge("Omni", "FATHER_OF", "Amarón") in closure


class TestNoOverreach:
    def test_no_sibling_from_co_children(self):
        # Co-children don't infer BROTHER_OF (lacks gender signal).
        seed = _edges([
            ("Lehi", "FATHER_OF", "Nephi"),
            ("Lehi", "FATHER_OF", "Sam"),
        ])
        _, derived = infer(seed)
        assert not any(d.relation in ("BROTHER_OF", "SISTER_OF") for d in derived)

    def test_seed_preserved(self):
        seed = _edges([("A", "FATHER_OF", "B")])
        closure, derived = infer(seed)
        assert seed.issubset(closure)
        assert derived == []  # no rule fires


class TestScripturalCases:
    """Specific scriptural cases flagged by the user as must-work."""

    def test_haran_brother_of_abraham(self):
        """Gen 11:26 — Terah fathered Abram, Nahor, and Haran. Haran is
        brother of Abraham, so should share Terah as father."""
        seed = _edges([
            ("Haran", "BROTHER_OF", "Abraham"),
            ("Terah", "FATHER_OF", "Abraham"),
        ])
        closure, _ = infer(seed)
        assert FamilyEdge("Haran", "BROTHER_OF", "Abraham") in closure
        assert FamilyEdge("Abraham", "BROTHER_OF", "Haran") in closure
        assert FamilyEdge("Terah", "FATHER_OF", "Haran") in closure

    def test_abigail_sister_of_david(self):
        """1 Chr 2:13-16 — Jesse fathered David, and David's sisters were
        Zeruiah and Abigail."""
        seed = _edges([
            ("Abigail", "SISTER_OF", "David"),
            ("Jesse", "FATHER_OF", "David"),
        ])
        closure, _ = infer(seed)
        assert FamilyEdge("Abigail", "SISTER_OF", "David") in closure
        assert FamilyEdge("David", "SISTER_OF", "Abigail") in closure  # symmetry
        assert FamilyEdge("Jesse", "FATHER_OF", "Abigail") in closure

    def test_amaron_brother_of_quemis(self):
        """Omni 1:9 — Quemis is brother of Amarón. With Omni as father of
        Amarón (Omni 1:3), inference should give Omni as father of Quemis."""
        seed = _edges([
            ("Quemis", "BROTHER_OF", "Amarón"),
            ("Omni", "FATHER_OF", "Amarón"),
        ])
        closure, _ = infer(seed)
        assert FamilyEdge("Omni", "FATHER_OF", "Quemis") in closure

    def test_jesus_brothers_matt_13_55(self):
        """Matt 13:55 — 'Is not his mother called Mary? and his brethren,
        James, and Joses, and Simon, and Judas?'

        All four brothers share Joseph as (legal) father. Mary is mother
        of Jesus; whether she's also mother of these brothers is a
        theological question (Mormon/Catholic views differ), so the engine
        must NOT propagate MOTHER_OF via sibling — the caller decides."""
        seed = _edges([
            ("James", "BROTHER_OF", "Jesus"),
            ("Joses", "BROTHER_OF", "Jesus"),
            ("Simon", "BROTHER_OF", "Jesus"),
            ("Judas", "BROTHER_OF", "Jesus"),
            ("Joseph", "FATHER_OF", "Jesus"),
            ("Mary", "MOTHER_OF", "Jesus"),
        ])
        closure, _ = infer(seed)
        # All four brothers inherit Joseph as father.
        for sib in ("James", "Joses", "Simon", "Judas"):
            assert FamilyEdge("Joseph", "FATHER_OF", sib) in closure
        # None inherit Mary as mother.
        for sib in ("James", "Joses", "Simon", "Judas"):
            assert FamilyEdge("Mary", "MOTHER_OF", sib) not in closure
        # Symmetry still fills in mutual brother edges.
        assert FamilyEdge("Jesus", "BROTHER_OF", "James") in closure
        assert FamilyEdge("Jesus", "BROTHER_OF", "Judas") in closure


class TestOmniLineage:
    def test_quemis_to_omni_inferred(self):
        """Real testigo case: Omni 1 says "Quemis, mi hermano [de Amarón]"
        and "yo, Amarón, hijo de Omni". Together → Quemis is son of Omni."""
        seed = _edges([
            ("Quemis", "BROTHER_OF", "Amarón"),    # explicit in Omni 1:9
            ("Omni", "FATHER_OF", "Amarón"),        # explicit in Omni 1:3
            ("Quemis", "FATHER_OF", "Abinadom"),    # explicit in Omni 1:10
            ("Abinadom", "FATHER_OF", "Amalekí"),   # explicit in Omni 1:12
        ])
        closure, derived = infer(seed)
        # The originally missing edge:
        assert FamilyEdge("Omni", "FATHER_OF", "Quemis") in closure
        # And Amaleki's full ancestry should be reachable transitively.
