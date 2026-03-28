"""FastAPI dependency injection for shared services."""

from __future__ import annotations

import logging
from functools import lru_cache

from alejandria.config import settings
from alejandria.ingestion.pipeline import IngestionPipeline
from alejandria.ingestion.registry import DocumentRegistry
from alejandria.search.textual import TextualSearch

logger = logging.getLogger(__name__)


@lru_cache
def get_registry() -> DocumentRegistry:
    return DocumentRegistry(settings.sqlite_db_path)


@lru_cache
def get_textual_search() -> TextualSearch:
    return TextualSearch(settings.sqlite_db_path)


@lru_cache
def get_semantic_search():
    """Get SemanticSearch instance, or None if Qdrant/sentence-transformers unavailable."""
    try:
        from alejandria.search.semantic import SemanticSearch

        return SemanticSearch()
    except Exception:
        logger.warning("Semantic search unavailable (Qdrant not connected or deps missing)")
        return None


@lru_cache
def get_neo4j_client():
    """Get Neo4jClient instance, or None if Neo4j unavailable."""
    try:
        from alejandria.knowledge.neo4j_client import Neo4jClient

        return Neo4jClient()
    except Exception:
        logger.warning("Neo4j unavailable (not connected or deps missing)")
        return None


@lru_cache
def get_kg_extractor():
    """Get KGExtractor instance, or None if unavailable."""
    try:
        from alejandria.knowledge.extractor import KGExtractor

        return KGExtractor()
    except Exception:
        logger.warning("KG extractor unavailable")
        return None


@lru_cache
def get_pipeline() -> IngestionPipeline:
    return IngestionPipeline(
        registry=get_registry(),
        textual_search=get_textual_search(),
        semantic_search=get_semantic_search(),
        neo4j_client=get_neo4j_client(),
        kg_extractor=get_kg_extractor(),
    )
