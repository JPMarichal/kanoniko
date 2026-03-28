"""Model registry and tiered selection for LLM routing.

Defines available models organized by tier (fast/balanced/quality),
provides a heuristic complexity classifier, and routes questions
to the appropriate model based on estimated complexity.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Tier(str, Enum):
    """Model tiers ordered by capability and cost."""
    FAST = "fast"           # Cheapest — simple lookups, internal pipeline calls
    BALANCED = "balanced"   # Good quality/cost ratio — most questions
    QUALITY = "quality"     # Best quality — complex analysis


@dataclass(frozen=True)
class ModelDef:
    """Definition of an available LLM model."""
    id: str
    provider: str           # "anthropic", "gemini", "openai"
    model_name: str         # API model identifier
    tier: Tier
    cost_input: float       # USD per 1M input tokens
    cost_output: float      # USD per 1M output tokens
    preview: bool = False   # Whether this is a preview/experimental model


# Known models — ordered by preference within each tier.
# When multiple models share a tier, the first available one is used.
MODEL_REGISTRY: list[ModelDef] = [
    # --- Fast tier (internal pipeline calls: expansion, reranking) ---
    ModelDef("gemini-2.5-flash-lite", "gemini", "gemini-2.5-flash-lite", Tier.FAST, 0.15, 0.60),
    ModelDef("gemini-3.1-flash-lite", "gemini", "gemini-3.1-flash-lite-preview", Tier.FAST, 0.15, 0.60, preview=True),

    # --- Balanced tier (most user questions) ---
    ModelDef("gemini-2.5-flash", "gemini", "gemini-2.5-flash", Tier.BALANCED, 0.30, 2.50),

    # --- Quality tier (complex theological analysis) ---
    # Gemini 3 Flash: A- quality, excellent cost/quality ratio ($0.40/$1.60)
    ModelDef("gemini-3-flash", "gemini", "gemini-3-flash-preview", Tier.QUALITY, 0.40, 1.60, preview=True),
    # DeepSeek V3: best cost/quality for deep analysis ($0.27/$1.10) — needs api.deepseek.com access
    ModelDef("deepseek-v3", "deepseek", "deepseek-chat", Tier.QUALITY, 0.27, 1.10),
    # DeepSeek R1: reasoning model ($0.55/$2.19) — needs api.deepseek.com access
    ModelDef("deepseek-r1", "deepseek", "deepseek-reasoner", Tier.QUALITY, 0.55, 2.19),
    # Claude Haiku 4.5: premium fallback ($1.00/$5.00)
    ModelDef("claude-haiku-4.5", "anthropic", "claude-haiku-4-5-20251001", Tier.QUALITY, 1.00, 5.00),
    # GPT-4.1-mini: OpenAI alternative ($0.40/$1.60) — needs OpenAI key
    ModelDef("gpt-4.1-mini", "openai", "gpt-4.1-mini", Tier.QUALITY, 0.40, 1.60),
]


def get_api_key(provider: str) -> str:
    """Get the API key for a given provider from settings."""
    from alejandria.config import settings

    provider = provider.lower()
    # Check provider-specific keys first, fall back to legacy keys
    if provider == "anthropic":
        return settings.llm_anthropic_api_key or settings.llm_api_key or ""
    elif provider == "gemini":
        return settings.llm_gemini_api_key or settings.llm_alt_api_key or ""
    elif provider == "openai":
        return settings.llm_openai_api_key or ""
    elif provider == "deepseek":
        return settings.llm_deepseek_api_key or ""
    return ""


def get_available_models() -> list[ModelDef]:
    """Return models that have a valid API key configured."""
    return [m for m in MODEL_REGISTRY if get_api_key(m.provider)]


def select_model(tier: Tier) -> ModelDef | None:
    """Select the best available model for a given tier.

    Returns the first model in the tier that has a configured API key.
    If no model is available in the requested tier, falls back to the
    nearest available tier (up for quality, down for cost).
    """
    available = get_available_models()
    if not available:
        return None

    # Try exact tier match first
    for model in available:
        if model.tier == tier:
            return model

    # Fallback: find nearest tier
    tier_order = [Tier.FAST, Tier.BALANCED, Tier.QUALITY]
    requested_idx = tier_order.index(tier)

    # Search upward (more capable) first
    for i in range(requested_idx + 1, len(tier_order)):
        for model in available:
            if model.tier == tier_order[i]:
                logger.info("No %s model available, falling back to %s (%s)", tier.value, model.id, model.tier.value)
                return model

    # Then search downward (cheaper)
    for i in range(requested_idx - 1, -1, -1):
        for model in available:
            if model.tier == tier_order[i]:
                logger.info("No %s model available, falling back to %s (%s)", tier.value, model.id, model.tier.value)
                return model

    return available[0]  # Last resort


def select_model_by_id(model_id: str) -> ModelDef | None:
    """Find a specific model by its ID."""
    for model in MODEL_REGISTRY:
        if model.id == model_id:
            return model
    return None


# ---------------------------------------------------------------------------
# Complexity classifier — heuristic, no LLM cost
# ---------------------------------------------------------------------------

# Patterns that suggest complex, analytical questions
_COMPLEX_PATTERNS = [
    # Theological analysis
    r"\b(teolog|doctrinal|doctrina|theological|symbolism|simbolismo)\b",
    r"\b(reconcil|contradict|paradox|paradoja|contradic)\b",
    r"\b(interpret|significado profundo|deeper meaning|exeges|hermeneu)\b",
    r"\b(compara.*(?:y|and|con|with).*(?:y|and|con|with))\b",  # compare X and Y and Z
    # Multi-source synthesis
    r"\b(todos los|all the|every|cada uno de los|throughout)\b.*\b(libro|book|escritura|scripture|standard work)\b",
    r"\b(evoluci[oó]n|evolution|development|progres|histor)\b.*\b(doctrin|concept|ense[ñn]anza|teaching)\b",
    # Broad open-ended
    r"\b(explain|explica|analyze|analiza|discuss|discute|elaborate|desarrolla)\b.*\b(relaci[oó]n|relationship|connection|conexi[oó]n|significance|importancia)\b",
    r"\b(por qu[eé]|why)\b.*\b(import|signific|matter|relevant)\b",
    r"[\u00bf].*\b(c[oó]mo se relaciona|how does.*relate|what is the significance)\b",
]

# Patterns that suggest simple, factual lookups
_SIMPLE_PATTERNS = [
    # Direct verse/reference lookups
    r"\b(d[oó]nde dice|where does it say|qu[eé] dice|what does.*say)\b",
    r"\b(cita|quote|vers[ií]culo|verse)\b.*\d",
    r"\b(cu[aá]l es el|what is the)\b.*\b(vers[ií]culo|verse|pasaje|passage)\b",
    # Single fact questions
    r"\b(qui[eé]n (es|fue|era)|who (is|was))\b",
    r"\b(cu[aá]ntos|how many|cu[aá]ndo|when did)\b",
    r"\b(d[oó]nde (naci[oó]|muri[oó]|viv[ií])|where (was born|died|lived))\b",
    # List requests (usually straightforward)
    r"\b(lista|list|enumera|enumerate)\b.*\b(nombre|name|hijo|son|tribu|tribe)\b",
]

# Question length thresholds
_SHORT_QUESTION_WORDS = 12   # Below this → likely simple
_LONG_QUESTION_WORDS = 30    # Above this → likely complex


def classify_complexity(question: str) -> Tier:
    """Classify a question's complexity to determine the appropriate model tier.

    Uses heuristic patterns — no LLM call needed.

    Returns:
        Tier.FAST: Simple factual lookups (verse references, who/what/where)
        Tier.BALANCED: Standard questions (most queries)
        Tier.QUALITY: Complex analysis (theological comparison, multi-source synthesis)
    """
    q_lower = question.lower().strip()
    word_count = len(q_lower.split())

    # Check complex patterns
    complex_score = 0
    for pattern in _COMPLEX_PATTERNS:
        if re.search(pattern, q_lower, re.IGNORECASE):
            complex_score += 1

    # Check simple patterns
    simple_score = 0
    for pattern in _SIMPLE_PATTERNS:
        if re.search(pattern, q_lower, re.IGNORECASE):
            simple_score += 1

    # Length factor
    if word_count >= _LONG_QUESTION_WORDS:
        complex_score += 1
    elif word_count <= _SHORT_QUESTION_WORDS:
        simple_score += 1

    # Multiple question marks suggest compound question
    if question.count("?") >= 2:
        complex_score += 1

    # Decision
    if complex_score >= 2:
        return Tier.QUALITY
    elif complex_score == 1 and simple_score == 0:
        return Tier.QUALITY
    elif simple_score >= 2 or (simple_score >= 1 and complex_score == 0):
        return Tier.FAST
    else:
        return Tier.BALANCED


def estimate_cost(model: ModelDef, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost in USD for a given model and token counts."""
    return (input_tokens / 1_000_000 * model.cost_input) + (output_tokens / 1_000_000 * model.cost_output)
