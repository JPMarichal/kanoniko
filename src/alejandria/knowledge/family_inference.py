"""Closure rules over the family-relation graph.

Once `family_patterns.extract_family_hits` has populated the obvious
explicit relations (FATHER_OF / MOTHER_OF / BROTHER_OF / SISTER_OF /
SPOUSE_OF), this module derives the implications:

    Symmetry
    --------
        BROTHER_OF(A, B)  ⇒  BROTHER_OF(B, A)
        SISTER_OF (A, B)  ⇒  SISTER_OF (B, A)
        SPOUSE_OF (A, B)  ⇒  SPOUSE_OF (B, A)

    Sibling-implies-shared-FATHER (only)
    ------------------------------------
        BROTHER_OF(A, B) ∧ FATHER_OF(P, B)  ⇒  FATHER_OF(P, A)
        SISTER_OF (A, B) ∧ FATHER_OF(P, B)  ⇒  FATHER_OF(P, A)

We deliberately do NOT propagate MOTHER_OF via sibling because polygamy
was common and permitted in large swaths of the source corpus (OT
patriarchs, Jacob with Leah/Rachel/Bilhah/Zilpah, David, Solomon, early
Restoration). Half-siblings share the father but have different mothers:
Ishmael and Isaac (Gen 16, 21); Joseph and Reuben (Gen 29–30). Applying
the rule to MOTHER_OF would fabricate wrong-mother edges at scale.

For the same reason we also do NOT derive sibling-from-co-children
(`FATHER_OF(P,X) ∧ FATHER_OF(P,Y) ⇒ BROTHER_OF(X,Y)`): under polygamy,
two children of the same father may not share a mother, and gender
signal is also unreliable (BROTHER_OF vs SISTER_OF). Add SIBLING_OF as
a generic relation later if the schema grows and half-sibling
ambiguity is acceptable.

FATHER_OF inference IS safe under polygamy because polygamous marriages
in this corpus are one-man-multiple-wives, not multi-husband — siblings
(full or half) always share the father.

The closure runs to a fixed point: each pass adds zero or more edges, and
we stop when a pass adds nothing new. With at most a few thousand family
edges this converges in 2–4 passes.

Usage:
    from alejandria.knowledge.family_inference import FamilyEdge, infer

    # Seed with explicit edges:
    seed = {FamilyEdge("Abraham", "FATHER_OF", "Isaac"),
            FamilyEdge("Esau", "BROTHER_OF", "Jacob"),
            FamilyEdge("Isaac", "FATHER_OF", "Jacob")}
    closed, derived = infer(seed)
    # `closed`  = seed ∪ derived (full closure)
    # `derived` = only the new edges (with .reason for audit)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class FamilyEdge:
    """A directed family-relation edge.

    Equality and hashing key off (from, relation, to) ONLY — `reason` is
    audit metadata and must not partition otherwise-identical edges. This
    matters when callers do `seed_edge in closure` after inference enriches
    the same edge with a derivation reason.
    """
    from_name: str
    relation: str   # FATHER_OF / MOTHER_OF / SPOUSE_OF / BROTHER_OF / SISTER_OF
    to_name: str
    reason: str = field(default="", compare=False, hash=False)


def _key(e: FamilyEdge) -> tuple[str, str, str]:
    return (e.from_name, e.relation, e.to_name)


_SYMMETRIC = frozenset({"BROTHER_OF", "SISTER_OF", "SPOUSE_OF"})
# Only FATHER_OF propagates via sibling — see module docstring (polygamy).
_SIBLING_PARENT_RELS = frozenset({"FATHER_OF"})
_SIBLING_RELS = frozenset({"BROTHER_OF", "SISTER_OF"})


def infer(seed: Iterable[FamilyEdge]) -> tuple[set[FamilyEdge], list[FamilyEdge]]:
    """Compute the closure of `seed` under the rules above.

    Returns (closure, newly_derived) where:
      * closure = seed ∪ derived
      * newly_derived only contains edges NOT in the seed (with `.reason` set)
    """
    closure: dict[tuple[str, str, str], FamilyEdge] = {
        _key(e): e for e in seed
    }
    derived: list[FamilyEdge] = []

    def add(edge: FamilyEdge) -> bool:
        k = _key(edge)
        if k in closure:
            return False
        closure[k] = edge
        derived.append(edge)
        return True

    changed = True
    while changed:
        changed = False
        # snapshot to iterate without mutating
        snapshot = list(closure.values())

        # Rule 1: symmetry
        for e in snapshot:
            if e.relation in _SYMMETRIC and e.from_name != e.to_name:
                mirror = FamilyEdge(
                    from_name=e.to_name,
                    relation=e.relation,
                    to_name=e.from_name,
                    reason=f"symmetry of {e.relation}",
                )
                if add(mirror):
                    changed = True

        # Rule 2: sibling-implies-shared-FATHER (not mother — see docstring)
        # Build a small index: child → list of father names
        fathers_of: dict[str, list[str]] = {}
        for e in snapshot:
            if e.relation in _SIBLING_PARENT_RELS:
                fathers_of.setdefault(e.to_name, []).append(e.from_name)
        for e in snapshot:
            if e.relation not in _SIBLING_RELS:
                continue
            a, b = e.from_name, e.to_name
            for father in fathers_of.get(b, ()):
                inferred = FamilyEdge(
                    from_name=father,
                    relation="FATHER_OF",
                    to_name=a,
                    reason=f"{e.relation}({a},{b}) ∧ FATHER_OF({father},{b})",
                )
                if add(inferred):
                    changed = True

    return set(closure.values()), derived


__all__ = ["FamilyEdge", "infer"]
