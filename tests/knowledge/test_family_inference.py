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


class TestUnconventionalCases:
    """Scripture cases where the naive model would fail — endogamy
    (close-kin marriage common in ancient Near East), legal vs biological
    parentage (Jesus), levirate marriage, onomastic multiplicity. The
    closure engine must not invent contradictions when these appear, and
    must leave room for human-curated qualifiers (role, source_ref) to
    distinguish interpretations."""

    # ── Endogamy: aunt-nephew, uncle-niece, half-sibling marriages ────────
    def test_amram_jochebed_aunt_nephew_marriage(self):
        """Ex 6:20 — Amram (son of Kohath, son of Levi) married Jochebed,
        his own father's sister (daughter of Levi). Under polygamy + tribal
        endogamy this was legitimate; the rabbinic/targumic tradition
        sometimes reads 'aunt' more broadly as 'kinswoman'.

        The engine must tolerate SPOUSE_OF(Amram, Jochebed) coexisting with
        Jochebed being related to Amram's father, and NOT fabricate a
        BROTHER_OF edge between Amram and Jochebed."""
        seed = _edges([
            ("Amram", "SPOUSE_OF", "Jochebed"),
            ("Levi", "FATHER_OF", "Jochebed"),
            ("Levi", "FATHER_OF", "Kohath"),
            ("Kohath", "FATHER_OF", "Amram"),
            ("Jochebed", "MOTHER_OF", "Moses"),
            ("Amram", "FATHER_OF", "Moses"),
        ])
        closure, _ = infer(seed)
        assert FamilyEdge("Jochebed", "SPOUSE_OF", "Amram") in closure
        # Engine must NOT claim Amram and Jochebed are siblings.
        assert FamilyEdge("Amram", "BROTHER_OF", "Jochebed") not in closure
        assert FamilyEdge("Jochebed", "SISTER_OF", "Amram") not in closure
        # Moses inherits Amram as father (already seeded).
        assert FamilyEdge("Amram", "FATHER_OF", "Moses") in closure

    def test_abraham_sarah_half_sister_spouse(self):
        """Gen 20:12 — Abraham to Abimelech: 'she is the daughter of my
        father, but not the daughter of my mother; and she became my wife.'
        Same father (Terah), different mothers, legitimate under the
        patriarchal convention. Must coexist."""
        seed = _edges([
            ("Abraham", "SPOUSE_OF", "Sarah"),
            ("Sarah", "SISTER_OF", "Abraham"),   # half-sister (same father)
            ("Terah", "FATHER_OF", "Abraham"),
            ("Terah", "FATHER_OF", "Sarah"),
        ])
        closure, _ = infer(seed)
        # All explicit edges preserved plus their symmetric/father mirrors.
        assert FamilyEdge("Sarah", "SPOUSE_OF", "Abraham") in closure
        assert FamilyEdge("Abraham", "SISTER_OF", "Sarah") in closure
        # Polygamy-safe MOTHER_OF NON-propagation still holds: engine
        # doesn't claim Sarah and Abraham share a mother.
        # (No MOTHER_OF seeds here, but pattern confirmed by other tests.)

    def test_nahor_milcah_uncle_niece(self):
        """Gen 11:29 — Nahor married Milcah, daughter of his brother Haran.
        Uncle-niece marriage. Engine must handle SPOUSE_OF(Nahor, Milcah)
        alongside BROTHER_OF(Nahor, Haran) + FATHER_OF(Haran, Milcah)
        without inventing anything."""
        seed = _edges([
            ("Nahor", "SPOUSE_OF", "Milcah"),
            ("Haran", "FATHER_OF", "Milcah"),
            ("Terah", "FATHER_OF", "Nahor"),
            ("Terah", "FATHER_OF", "Haran"),
            ("Nahor", "BROTHER_OF", "Haran"),
        ])
        closure, _ = infer(seed)
        assert FamilyEdge("Milcah", "SPOUSE_OF", "Nahor") in closure
        # Sibling-inference on Nahor↔Haran + Terah shared father: already
        # seeded. No spurious father claim for Milcah from being Nahor's
        # spouse.
        assert FamilyEdge("Nahor", "FATHER_OF", "Milcah") not in closure

    # ── Legal vs biological parentage (Jesus, levirate) ──────────────────
    def test_jesus_dual_genealogy_coexists(self):
        """Matt 1 traces Joseph's line (legal); Luke 3 traces what most
        early Christian and LDS commentary takes as Mary's line (though
        textually also via Joseph, differently reconciled). Both hand
        different ancestors to the same point. The engine stores both
        without picking one as canonical; role/source_ref qualifiers on
        the schema are how downstream queries distinguish them."""
        seed = _edges([
            ("Joseph", "FATHER_OF", "Jesus"),
            ("Mary", "MOTHER_OF", "Jesus"),
            # Matt 1:16 — Jacob is Joseph's father
            ("Jacob", "FATHER_OF", "Joseph"),
            # Luke 3:23 — Heli is Joseph's father (alternative tradition,
            # often read as Mary's father via levirate / legal adoption)
            ("Heli", "FATHER_OF", "Joseph"),
        ])
        closure, _ = infer(seed)
        # Both genealogies are preserved. Engine does not pick one.
        assert FamilyEdge("Jacob", "FATHER_OF", "Joseph") in closure
        assert FamilyEdge("Heli", "FATHER_OF", "Joseph") in closure
        # No spurious BROTHER_OF(Jacob, Heli) fabricated from co-fathering.
        assert FamilyEdge("Jacob", "BROTHER_OF", "Heli") not in closure

    # ── Paronymy / multiple names for the same person ────────────────────
    def test_paronyms_require_curation_not_inference(self):
        """The engine treats 'Saul' and 'Paul' as distinct nodes unless
        canonicalized via entity_aliases. This is intentional: textual
        aliasing belongs in the entity layer, not the relation-inference
        layer.

        Examples the system should eventually resolve via curated aliases
        (entity_aliases table, not code):
          - Jacob / Israel (Gen 32:28)
          - Abram / Abraham (Gen 17:5)
          - Sarai / Sarah (Gen 17:15)
          - Simon / Cephas / Peter
          - Saul / Paul (Acts 13:9)
          - Basemath / Mahalath, Adah / Basemath (Esau's wives —
            Gen 26:34, 28:9, 36:2-3 — multiple listings with conflicting
            names, resolved by assuming each wife had multiple names)
        """
        seed = _edges([
            ("Saul", "AUTHORED", "letters"),
            ("Paul", "AUTHORED", "letters"),
        ])
        closure, _ = infer(seed)
        # Without a curated alias, both stay as separate entities — this
        # is the correct default for a purely inferential engine.
        assert FamilyEdge("Saul", "AUTHORED", "letters") in closure
        assert FamilyEdge("Paul", "AUTHORED", "letters") in closure


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
