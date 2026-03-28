"""Chat (RAG) API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alejandria.api.dependencies import get_neo4j_client, get_profile_store, get_semantic_search, get_textual_search
from alejandria.api.schemas import (
    ChatRequest,
    ChatResponse,
    ChatSourceItem,
)
from alejandria.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])


def _build_chat_response(result) -> ChatResponse:
    """Convert a RAGPipeline result to an API ChatResponse."""
    return ChatResponse(
        answer=result.answer,
        sources=[
            ChatSourceItem(
                text=s.text[:500],
                file_path=s.file_path,
                chunk_index=s.chunk_index,
                score=s.score,
                mode=s.mode,
                reference=s.reference,
            )
            for s in result.sources
        ],
        graph_context=result.graph_context,
        model=result.model,
        tier=result.tier,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Ask a question and get a RAG-powered answer grounded in the corpus."""
    from alejandria.chat.models import get_available_models

    if not settings.llm_api_key and not get_available_models():
        raise HTTPException(
            503,
            "Chat is not available: no LLM API key configured. "
            "Set ALEJANDRIA_LLM_API_KEY or provider-specific keys in your .env file.",
        )

    from alejandria.chat.rag import RAGPipeline

    pipeline = RAGPipeline(
        textual_search=get_textual_search(),
        semantic_search=get_semantic_search(),
        neo4j_client=get_neo4j_client(),
        profile_store=get_profile_store(),
    )

    result = pipeline.ask(
        question=req.question,
        source_filter=req.source_filter,
        provider_override=req.provider,
        model_override=req.model,
        tier_override=req.tier,
    )
    return _build_chat_response(result)


@router.get("/models")
def chat_models() -> dict:
    """List available models and their tiers, costs, and availability."""
    from alejandria.chat.models import (
        MODEL_REGISTRY, get_api_key, classify_complexity, Tier,
    )

    models = []
    for m in MODEL_REGISTRY:
        has_key = bool(get_api_key(m.provider))
        models.append({
            "id": m.id,
            "provider": m.provider,
            "model_name": m.model_name,
            "tier": m.tier.value,
            "cost_input_per_1m": m.cost_input,
            "cost_output_per_1m": m.cost_output,
            "preview": m.preview,
            "available": has_key,
        })

    return {
        "answer_tier": settings.llm_answer_tier,
        "internal_tier": settings.llm_internal_tier,
        "tiers": {
            "fast": "Simple factual lookups — cheapest model",
            "balanced": "Standard questions — good quality/cost ratio",
            "quality": "Complex analysis — best available model",
        },
        "models": models,
    }


@router.post("/classify")
def chat_classify(req: ChatRequest) -> dict:
    """Preview how a question would be classified without running the full pipeline."""
    from alejandria.chat.models import classify_complexity, select_model

    tier = classify_complexity(req.question)
    model = select_model(tier)

    return {
        "question": req.question,
        "tier": tier.value,
        "model": {
            "id": model.id,
            "provider": model.provider,
            "model_name": model.model_name,
            "cost_input_per_1m": model.cost_input,
            "cost_output_per_1m": model.cost_output,
        } if model else None,
    }


@router.post("/compare")
def chat_compare(req: ChatRequest) -> dict:
    """Run the same question through two LLM providers for A/B comparison.

    Uses the primary LLM (ALEJANDRIA_LLM_*) and the alternative
    (ALEJANDRIA_LLM_ALT_*). Returns both answers side by side with token
    counts for cost analysis.
    """
    if not settings.llm_api_key:
        raise HTTPException(503, "Primary LLM API key not configured.")
    if not settings.llm_alt_provider or not settings.llm_alt_api_key:
        raise HTTPException(
            503,
            "Alternative LLM not configured. Set ALEJANDRIA_LLM_ALT_PROVIDER, "
            "ALEJANDRIA_LLM_ALT_MODEL, and ALEJANDRIA_LLM_ALT_API_KEY.",
        )

    from alejandria.chat.rag import RAGPipeline

    pipeline = RAGPipeline(
        textual_search=get_textual_search(),
        semantic_search=get_semantic_search(),
        neo4j_client=get_neo4j_client(),
        profile_store=get_profile_store(),
    )

    # Run with primary model (retrieval is done once, shared)
    result_a = pipeline.ask(question=req.question, source_filter=req.source_filter)

    # Swap to alternative model and run answer generation only
    # (reuse the same retrieved sources)
    original_provider = settings.llm_provider
    original_model = settings.llm_model
    original_key = settings.llm_api_key

    try:
        settings.llm_provider = settings.llm_alt_provider
        settings.llm_model = settings.llm_alt_model
        settings.llm_api_key = settings.llm_alt_api_key

        result_b = pipeline.ask(question=req.question, source_filter=req.source_filter)
    finally:
        # Restore original settings
        settings.llm_provider = original_provider
        settings.llm_model = original_model
        settings.llm_api_key = original_key

    def _cost_estimate(provider: str, in_tok: int, out_tok: int) -> float:
        """Estimate cost in USD based on known pricing."""
        pricing = {
            "anthropic": (1.00, 5.00),    # Haiku 4.5
            "gemini": (0.30, 2.50),        # Gemini 2.5 Flash
            "openai": (0.15, 0.60),        # GPT-4o-mini
        }
        p_in, p_out = pricing.get(provider, (1.0, 5.0))
        return (in_tok / 1_000_000 * p_in) + (out_tok / 1_000_000 * p_out)

    return {
        "question": req.question,
        "model_a": {
            "provider": original_provider,
            "model": result_a.model,
            "answer": result_a.answer,
            "input_tokens": result_a.input_tokens,
            "output_tokens": result_a.output_tokens,
            "estimated_cost": _cost_estimate(
                original_provider, result_a.input_tokens, result_a.output_tokens,
            ),
        },
        "model_b": {
            "provider": settings.llm_alt_provider,
            "model": result_b.model,
            "answer": result_b.answer,
            "input_tokens": result_b.input_tokens,
            "output_tokens": result_b.output_tokens,
            "estimated_cost": _cost_estimate(
                settings.llm_alt_provider, result_b.input_tokens, result_b.output_tokens,
            ),
        },
        "sources": [
            {
                "reference": s.reference,
                "file_path": s.file_path,
                "mode": s.mode,
            }
            for s in result_a.sources
        ],
    }
