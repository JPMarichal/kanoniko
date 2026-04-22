"""FastAPI dependency injection for shared services.

Optional services (KG graph client, KG extractor, semantic search, etc.)
use retry-on-None caching: if a service is unavailable at first call,
subsequent calls retry the initialization instead of permanently
caching None.
"""

from __future__ import annotations

import logging
import threading
from functools import lru_cache

from alejandria.config import settings
from alejandria.ingestion.pipeline import IngestionPipeline
from alejandria.ingestion.registry import DocumentRegistry, make_document_registry
from alejandria.search.textual import TextualSearch, make_textual_search
from alejandria.storage.chunk_writer import make_chunk_writer
from alejandria.storage.kg_reader import make_kg_reader
from alejandria.storage.kg_writer import make_kg_writer

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
    """Cached accessor — :class:`PostgresDocumentRegistry`."""
    return make_document_registry()


@lru_cache
def get_textual_search():
    """Cached accessor — :class:`TextualSearch` over Postgres tsvector."""
    return make_textual_search()


# ── Optional services (retry until available) ──

@_cache_success
def get_semantic_search():
    """Get semantic search (pgvector HNSW), or None if unavailable."""
    try:
        from alejandria.search.semantic import make_semantic_search

        return make_semantic_search()
    except Exception:
        logger.warning("Semantic search unavailable (backend deps missing)")
        return None


@_cache_success
def get_graph_client():
    """Get the KG graph client, or None if unreachable.

    Post §3.3 Neo4j retirement this always returns a
    :class:`PostgresGraphClient` over Postgres IONOS. The retry-on-None
    wrapper remains to degrade gracefully if the DB is momentarily
    unreachable (SSH tunnel dropped, etc.).
    """
    try:
        from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

        return PostgresGraphClient()
    except Exception:
        logger.warning("Graph client unavailable (Postgres unreachable?)")
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
    """Get ProfileStore (Postgres) for entity profiles.

    Returns ``None`` if construction fails (import error, DB unreachable)
    so RAG/chat degrade gracefully rather than crashing.
    """
    try:
        from alejandria.knowledge.profile_store import make_profile_store

        return make_profile_store()
    except Exception:
        logger.warning("ProfileStore unavailable")
        return None


@lru_cache
def get_chunk_writer():
    """Get the ChunkWriter (Postgres)."""
    return make_chunk_writer()


@_cache_success
def get_kg_writer():
    """Get the KGWriter, or None if the backend is unreachable."""
    try:
        return make_kg_writer()
    except Exception:
        logger.warning("KG writer unavailable")
        return None


@_cache_success
def get_kg_reader():
    """Get the KGReader, or None if the backend is unreachable."""
    try:
        return make_kg_reader()
    except Exception:
        logger.warning("KG reader unavailable")
        return None


@lru_cache
def get_pipeline() -> IngestionPipeline:
    return IngestionPipeline(
        registry=get_registry(),
        chunk_writer=get_chunk_writer(),
        kg_writer=get_kg_writer(),
        kg_reader=get_kg_reader(),
        kg_extractor_factory=get_kg_extractor,
        profile_store=get_profile_store(),
    )
