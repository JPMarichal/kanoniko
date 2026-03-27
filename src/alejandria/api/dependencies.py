"""FastAPI dependency injection for shared services."""

from __future__ import annotations

from functools import lru_cache

from alejandria.config import settings
from alejandria.ingestion.pipeline import IngestionPipeline
from alejandria.ingestion.registry import DocumentRegistry
from alejandria.search.textual import TextualSearch


@lru_cache
def get_registry() -> DocumentRegistry:
    return DocumentRegistry(settings.sqlite_db_path)


@lru_cache
def get_textual_search() -> TextualSearch:
    return TextualSearch(settings.sqlite_db_path)


@lru_cache
def get_pipeline() -> IngestionPipeline:
    return IngestionPipeline(
        registry=get_registry(),
        textual_search=get_textual_search(),
    )
