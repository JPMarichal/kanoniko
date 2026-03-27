"""Alejandría — FastAPI application entry point."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from alejandria.api.routes_docs import router as docs_router
from alejandria.api.routes_index import router as index_router
from alejandria.api.routes_search import router as search_router
from alejandria.api.schemas import HealthResponse
from alejandria.api.dependencies import get_registry, get_textual_search
from alejandria.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Bilingual text library with textual, semantic, and knowledge graph search.",
)

app.include_router(search_router)
app.include_router(index_router)
app.include_router(docs_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    textual = get_textual_search()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        fts_documents=textual.count_documents(),
        fts_chunks=textual.count_chunks(),
    )


def start() -> None:
    """Entry point for running with uvicorn programmatically."""
    import uvicorn

    uvicorn.run(
        "alejandria.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    start()
