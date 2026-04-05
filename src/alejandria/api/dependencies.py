"""FastAPI dependency injection for shared services.

Optional services (Neo4j, sqlite-vec, KG extractor) use retry-on-None caching:
if a service is unavailable at first call, subsequent calls retry the
initialization instead of permanently caching None.
"""

from __future__ import annotations

import logging
import threading
from functools import lru_cache

from alejandria.config import settings
from alejandria.ingestion.pipeline import IngestionPipeline
from alejandria.ingestion.registry import DocumentRegistry
from alejandria.search.textual import TextualSearch

logger = logging.getLogger(__name__)


def _cache_success(func):
    """Cache the return value only if it is not None. Thread-safe."""
    lock = threading.Lock()
    result = None
    resolved = False

    def wrapper():
        nonlocal result, resolved
        if resolved:
            return result
        with lock:
            if resolved:
                return result
            value = func()
            if value is not None:
                result = value
                resolved = True
            return value

    wrapper.__wrapped__ = func
    return wrapper


# ── Required services (always cached) ──

@lru_cache
def get_registry() -> DocumentRegistry:
    return DocumentRegistry(settings.sqlite_db_path)


@lru_cache
def get_textual_search() -> TextualSearch:
    return TextualSearch(settings.sqlite_db_path)


# ── Optional services (retry until available) ──

@_cache_success
def get_semantic_search():
    """Get SemanticSearch instance, or None if sqlite-vec/sentence-transformers unavailable."""
    try:
        from alejandria.search.semantic import SemanticSearch

        return SemanticSearch(settings.sqlite_db_path)
    except Exception:
        logger.warning("Semantic search unavailable (sqlite-vec not loaded or deps missing)")
        return None


@_cache_success
def get_neo4j_client():
    """Get Neo4jClient instance, or None if Neo4j unavailable."""
    try:
        from alejandria.knowledge.neo4j_client import Neo4jClient

        return Neo4jClient()
    except Exception:
        logger.warning("Neo4j unavailable (not connected or deps missing)")
        return None


@_cache_success
def get_kg_extractor():
    """Get KGExtractor instance, or None if unavailable."""
    try:
        from alejandria.knowledge.extractor import KGExtractor

        return KGExtractor()
    except Exception:
        logger.warning("KG extractor unavailable")
        return None


@lru_cache
def get_profile_store():
    """Get ProfileStore instance for entity profiles."""
    try:
        from alejandria.knowledge.profile_store import ProfileStore

        return ProfileStore(settings.sqlite_db_path)
    except Exception:
        logger.warning("ProfileStore unavailable")
        return None


@lru_cache
def get_pipeline() -> IngestionPipeline:
    return IngestionPipeline(
        registry=get_registry(),
        textual_search=get_textual_search(),
        semantic_search_factory=get_semantic_search,
        neo4j_client_factory=get_neo4j_client,
        kg_extractor_factory=get_kg_extractor,
        profile_store=get_profile_store(),
    )
