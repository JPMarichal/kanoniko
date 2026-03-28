"""Chat (RAG) API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alejandria.api.dependencies import get_neo4j_client, get_semantic_search, get_textual_search
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
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Ask a question and get a RAG-powered answer grounded in the corpus."""
    if not settings.llm_api_key:
        raise HTTPException(
            503,
            "Chat is not available: LLM API key not configured. "
            "Set ALEJANDRIA_LLM_API_KEY in your .env file.",
        )

    from alejandria.chat.rag import RAGPipeline

    pipeline = RAGPipeline(
        textual_search=get_textual_search(),
        semantic_search=get_semantic_search(),
        neo4j_client=get_neo4j_client(),
    )

    result = pipeline.ask(
        question=req.question,
        source_filter=req.source_filter,
        provider_override=req.provider,
        model_override=req.model,
    )
    return _build_chat_response(result)


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
