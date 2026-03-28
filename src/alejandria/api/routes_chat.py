"""Chat (RAG) API endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from alejandria.api.dependencies import get_neo4j_client, get_semantic_search, get_textual_search
from alejandria.api.schemas import (
    ChatRequest,
    ChatResponse,
    ChatSourceItem,
)
from alejandria.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])


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

    result = pipeline.ask(question=req.question, source_filter=req.source_filter)

    return ChatResponse(
        answer=result.answer,
        sources=[
            ChatSourceItem(
                text=s.text[:500],
                file_path=s.file_path,
                chunk_index=s.chunk_index,
                score=s.score,
                mode=s.mode,
            )
            for s in result.sources
        ],
        graph_context=result.graph_context,
        model=result.model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )
