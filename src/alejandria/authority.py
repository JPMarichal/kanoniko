"""Authority model — classifies corpus materials by doctrinal weight, rigor, and importance.

See docs/authority-model.md for the full design specification.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AuthorityMeta:
    """Authority metadata for a corpus document or chunk."""
    authority: int = 50         # Doctrinal authority (1-100)
    rigor: int = 50             # Methodological rigor (1-100)
    importance: str = "interesante"  # 4 I's: imprescindible, importante, interesante, irrelevante
    official: bool = False
    current: bool = True
    context: str | None = None       # Delivery context (general-conference, devotional, etc.)
    consensus: str | None = None     # individual, first-presidency, fp-q12
    audience: str | None = None      # adult, youth, children, leadership, general
    speaker_calling: str | None = None  # president, fp-counselor, q12, etc.

    def to_dict(self) -> dict:
        """Serialize to dict for embedding in metadata JSON."""
        d: dict = {
            "authority": self.authority,
            "rigor": self.rigor,
            "importance": self.importance,
            "official": self.official,
            "current": self.current,
        }
        if self.context:
            d["context"] = self.context
        if self.consensus:
            d["consensus"] = self.consensus
        if self.audience:
            d["audience"] = self.audience
        if self.speaker_calling:
            d["speaker_calling"] = self.speaker_calling
        return d


# ── Path-based authority derivation ────────────────────────────────────────

# Default authority by corpus source category
_SOURCE_DEFAULTS: dict[str, AuthorityMeta] = {
    "scriptures": AuthorityMeta(
        authority=100, rigor=100, importance="imprescindible",
        official=True, current=True, context="canon",
    ),
    "proclamations": AuthorityMeta(
        authority=90, rigor=95, importance="imprescindible",
        official=True, current=True, context="official-declaration",
    ),
    "general-conference": AuthorityMeta(
        authority=80, rigor=70, importance="imprescindible",
        official=True, current=True, context="general-conference",
        audience="adult",
    ),
    "manuals": AuthorityMeta(
        authority=60, rigor=65, importance="importante",
        official=True, current=True, audience="adult",
    ),
    "study-aids": AuthorityMeta(
        authority=57, rigor=70, importance="importante",
        official=True, current=True, audience="adult",
    ),
    "biographies": AuthorityMeta(
        authority=20, rigor=50, importance="interesante",
        official=False, current=True,
    ),
    "web": AuthorityMeta(
        authority=25, rigor=45, importance="interesante",
        official=False, current=True,
    ),
}

_FALLBACK = AuthorityMeta(
    authority=30, rigor=40, importance="interesante",
    official=False, current=True,
)


def _is_intro_file(filename: str) -> bool:
    """Check if a filename is an introductory/editorial material file."""
    return filename in {
        "introduction.txt", "introduction.meta.json",
        "title-page.txt", "title-page.meta.json",
        "chronological-order.txt", "chronological-order.meta.json",
        "explanation.txt", "explanation.meta.json",
        "epistle-dedicatory.txt", "epistle-dedicatory.meta.json",
    }


# ── Sub-category overrides for scriptures introductory material ──────────
# These files live under scriptures/ but are NOT canon text.

_SCRIPTURE_INTRO_OVERRIDES: dict[str, AuthorityMeta] = {
    # Ancient translated text — part of the sacred record (Moroni)
    "bofm-title": AuthorityMeta(
        authority=100, rigor=100, importance="imprescindible",
        official=True, current=True, context="canon",
    ),
    # Historical witness documents — foundational testimony, not revelation
    "testimony-three-witnesses": AuthorityMeta(
        authority=85, rigor=90, importance="imprescindible",
        official=True, current=True, context="foundational-witness",
    ),
    "testimony-eight-witnesses": AuthorityMeta(
        authority=85, rigor=90, importance="imprescindible",
        official=True, current=True, context="foundational-witness",
    ),
    "testimony-joseph-smith": AuthorityMeta(
        authority=85, rigor=90, importance="imprescindible",
        official=True, current=True, context="foundational-witness",
    ),
    # Modern editorial introductions — official but revisable
    "introduction": AuthorityMeta(
        authority=60, rigor=65, importance="importante",
        official=True, current=True, context="editorial",
    ),
    # Structural/reference material
    "explanation": AuthorityMeta(
        authority=55, rigor=60, importance="importante",
        official=True, current=True, context="editorial",
    ),
    "chronological-order": AuthorityMeta(
        authority=55, rigor=60, importance="interesante",
        official=True, current=True, context="editorial",
    ),
    # Publishing metadata — minimal doctrinal content
    "title-page": AuthorityMeta(
        authority=10, rigor=50, importance="irrelevante",
        official=True, current=True, context="publishing",
    ),
    # KJV historical artifact
    "epistle-dedicatory": AuthorityMeta(
        authority=15, rigor=40, importance="irrelevante",
        official=False, current=False, context="historical-artifact",
    ),
}


# ── Sub-category overrides for study-aids ─────────────────────────────────

_STUDY_AID_DEFAULTS: dict[str, AuthorityMeta] = {
    # GEE: composed by Correlation, no doctrinal disclaimer
    "guide-to-scriptures": AuthorityMeta(
        authority=60, rigor=75, importance="importante",
        official=True, current=True, context="study-aid",
    ),
    # TG: curated cross-canonical index — reference, not doctrine
    "topical-guide": AuthorityMeta(
        authority=55, rigor=80, importance="importante",
        official=True, current=True, context="study-aid",
    ),
    # BD: explicit disclaimer "not official doctrine", Cambridge-based
    "bible-dictionary": AuthorityMeta(
        authority=50, rigor=65, importance="importante",
        official=True, current=True, context="study-aid",
    ),
    # JST: inspired revision — higher authority than other aids
    "jst-appendix": AuthorityMeta(
        authority=90, rigor=85, importance="imprescindible",
        official=True, current=True, context="inspired-revision",
    ),
}


def derive_authority(source: str, rel_path: str = "") -> AuthorityMeta:
    """Derive authority metadata from corpus source category and path.

    Args:
        source: The source category (e.g., "scriptures", "general-conference").
                Typically from pipeline._extract_source().
        rel_path: The relative corpus path, for sub-category refinement.

    Returns:
        AuthorityMeta with default values for the source category.
        Callers can override individual fields from meta.json if available.
    """
    norm = rel_path.replace("\\", "/")

    # ── Scripture introductory material overrides ──
    if source == "scriptures":
        # Extract filename stem from path
        parts = norm.rstrip("/").split("/")
        if parts:
            filename = parts[-1]
            stem = filename.replace(".meta.json", "").replace(".txt", "")
            if stem in _SCRIPTURE_INTRO_OVERRIDES:
                override = _SCRIPTURE_INTRO_OVERRIDES[stem]
                return AuthorityMeta(
                    authority=override.authority,
                    rigor=override.rigor,
                    importance=override.importance,
                    official=override.official,
                    current=override.current,
                    context=override.context,
                    consensus=override.consensus,
                    audience=override.audience,
                    speaker_calling=override.speaker_calling,
                )

    # ── Study-aid sub-category overrides ──
    if source == "study-aids":
        for aid_key, aid_meta in _STUDY_AID_DEFAULTS.items():
            if aid_key in norm:
                return AuthorityMeta(
                    authority=aid_meta.authority,
                    rigor=aid_meta.rigor,
                    importance=aid_meta.importance,
                    official=aid_meta.official,
                    current=aid_meta.current,
                    context=aid_meta.context,
                    consensus=aid_meta.consensus,
                    audience=aid_meta.audience,
                    speaker_calling=aid_meta.speaker_calling,
                )

    base = _SOURCE_DEFAULTS.get(source, _FALLBACK)
    # Return a copy so callers can modify without affecting defaults
    return AuthorityMeta(
        authority=base.authority,
        rigor=base.rigor,
        importance=base.importance,
        official=base.official,
        current=base.current,
        context=base.context,
        consensus=base.consensus,
        audience=base.audience,
        speaker_calling=base.speaker_calling,
    )


# ── Delivery context modifier ─────────────────────────────────────────────

_CONTEXT_MODIFIERS: dict[str, float] = {
    "canon": 1.0,
    "general-conference": 1.0,
    "official-letter": 1.0,
    "stake-conference": 0.9,
    "devotional": 0.85,
    "book-official": 0.8,
    "book-unofficial": 0.7,
    "interview": 0.5,
}

# ── Consensus modifier ────────────────────────────────────────────────────

_CONSENSUS_MODIFIERS: dict[str, float] = {
    "fp-q12": 1.15,           # United First Presidency + Quorum of the Twelve
    "first-presidency": 1.10,  # United First Presidency
    "individual": 1.0,         # Single speaker (default)
}


def effective_authority(meta: AuthorityMeta) -> float:
    """Compute effective authority applying context and consensus modifiers.

    Returns a float score (typically 5-115) used for RAG reranking.
    """
    base = float(meta.authority)
    ctx_mod = _CONTEXT_MODIFIERS.get(meta.context or "", 1.0)
    cons_mod = _CONSENSUS_MODIFIERS.get(meta.consensus or "individual", 1.0)
    return base * ctx_mod * cons_mod


# ── 4 I's importance ──────────────────────────────────────────────────────

_IMPORTANCE_BOOST: dict[str, float] = {
    "imprescindible": 1.0,
    "importante": 0.7,
    "interesante": 0.4,
    "irrelevante": 0.0,
}


def importance_boost(importance: str) -> float:
    """Map importance category to a numeric boost factor (0.0 to 1.0)."""
    return _IMPORTANCE_BOOST.get(importance, 0.4)


# ── Contextual importance degradation ─────────────────────────────────────

# Degradation table: (query_type, base_importance) → effective_importance
# Only downgrades are allowed, never upgrades.
_DEGRADATION: dict[tuple[str, str], str] = {
    ("doctrinal", "interesante"): "irrelevante",
    ("soteriological", "importante"): "interesante",
    ("soteriological", "interesante"): "irrelevante",
}


def degrade_importance(base_importance: str, query_type: str) -> str:
    """Apply contextual degradation to importance based on query type.

    Teaching/preparation and exploratory queries preserve all levels.
    Doctrinal and soteriological queries filter out less relevant material.
    Imprescindible never degrades. Irrelevante is always filtered.
    """
    if base_importance == "imprescindible":
        return "imprescindible"
    if base_importance == "irrelevante":
        return "irrelevante"
    return _DEGRADATION.get((query_type, base_importance), base_importance)


# ── Query type classification ─────────────────────────────────────────────

import re

_QUERY_TYPE_PATTERNS: dict[str, list[str]] = {
    "soteriological": [
        r"\b(salva|salvation|exaltaci[oó]n|exaltation|vida eterna|eternal life)\b",
        r"\b(redenci[oó]n|redemption|arrepentimiento|repentance|expiaci[oó]n|atonement)\b",
        r"\b(ordenanza|ordinance|bautism|baptis|investidura|endowment|sellamiento|sealing)\b",
    ],
    "doctrinal": [
        r"\b(doctrina|doctrine|ense[ñn]anza|teaching|teolog|theological)\b",
        r"\b(qu[eé] ense[ñn]a|what does.*teach|qu[eé] dice la iglesia|what does the church say)\b",
        r"\b(es verdad que|is it true that|es correcto|is it correct)\b",
        r"\b(principio|principle|mandamiento|commandment)\b",
    ],
    "historical": [
        r"\b(histor|cu[aá]ndo|when did|d[oó]nde ocurri[oó]|where did.*happen)\b",
        r"\b(contexto hist[oó]rico|historical context|cronolog|chronolog)\b",
        r"\b(a[ñn]o|year|siglo|century|[eé]poca|era|period)\b",
    ],
    "teaching": [
        r"\b(discurso|talk|clase|class|lecci[oó]n|lesson|charla|presentaci[oó]n)\b",
        r"\b(preparar|prepare|ense[ñn]ar|teach|explicar.*ni[ñn]os|explain.*children)\b",
        r"\b(ilustraci[oó]n|illustration|ejemplo|example|analog[ií]a|analogy)\b",
        r"\b(noche de hogar|family home evening|devocional|devotional)\b",
    ],
}


def classify_query_type(question: str) -> str:
    """Classify the query type for authority weighting.

    Returns one of: "soteriological", "doctrinal", "historical",
    "teaching", "exploratory" (default).
    """
    q_lower = question.lower()
    scores: dict[str, int] = {}

    for qtype, patterns in _QUERY_TYPE_PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, q_lower))
        if score > 0:
            scores[qtype] = score

    if not scores:
        return "exploratory"

    return max(scores, key=scores.get)


# ── Authority label for display ───────────────────────────────────────────

def authority_label(meta: AuthorityMeta) -> str:
    """Human-readable authority label for display in search results."""
    if meta.authority >= 100:
        return "Canon"
    elif meta.authority >= 90:
        return "Quasi-canonical"
    elif meta.authority >= 78:
        return "Prophetic"
    elif meta.authority >= 65:
        return "Normative"
    elif meta.authority >= 57:
        return "Correlated"
    elif meta.authority >= 45:
        return "GA Official"
    elif meta.authority >= 35:
        return "GA Unofficial"
    elif meta.authority >= 25:
        return "Institutional"
    elif meta.authority >= 15:
        return "Scholarly"
    elif meta.authority >= 10:
        return "Historical"
    else:
        return "Reference"
