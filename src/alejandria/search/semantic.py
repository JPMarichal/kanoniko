"""Semantic search using Qdrant vector database."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from alejandria.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SemanticSearchResult:
    chunk_id: int
    text: str
    score: float
    file_path: str
    chunk_index: int
    metadata: dict


class SemanticSearch:
    """Qdrant-backed semantic vector search."""

    COLLECTION = settings.qdrant_collection

    def __init__(self, host: str | None = None, port: int | None = None) -> None:
        self._client = QdrantClient(
            host=host or settings.qdrant_host,
            port=port or settings.qdrant_port,
        )
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = [c.name for c in self._client.get_collections().collections]
        if self.COLLECTION not in collections:
            self._client.create_collection(
                collection_name=self.COLLECTION,
                vectors_config=VectorParams(
                    size=settings.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Created Qdrant collection '%s'", self.COLLECTION)

    def upsert_chunks(
        self,
        ids: list[int],
        vectors: list[list[float]],
        payloads: list[dict],
    ) -> None:
        """Upsert chunk vectors with metadata payloads."""
        points = [
            PointStruct(id=id_, vector=vec, payload=payload)
            for id_, vec, payload in zip(ids, vectors, payloads)
        ]
        # Batch in groups of 100
        for i in range(0, len(points), 100):
            batch = points[i : i + 100]
            self._client.upsert(collection_name=self.COLLECTION, points=batch)

    def delete_by_file(self, file_path: str) -> None:
        """Delete all vectors for a given file."""
        self._client.delete(
            collection_name=self.COLLECTION,
            points_selector=Filter(
                must=[FieldCondition(key="file_path", match=MatchValue(value=file_path))]
            ),
        )

    def search(
        self,
        query_vector: list[float],
        limit: int = 20,
        source_filter: str | None = None,
    ) -> list[SemanticSearchResult]:
        """Search for similar vectors."""
        search_filter = None
        if source_filter:
            search_filter = Filter(
                must=[FieldCondition(key="source", match=MatchValue(value=source_filter))]
            )

        hits = self._client.query_points(
            collection_name=self.COLLECTION,
            query=query_vector,
            query_filter=search_filter,
            limit=limit,
            with_payload=True,
        ).points

        results = []
        for hit in hits:
            payload = hit.payload or {}
            results.append(SemanticSearchResult(
                chunk_id=hit.id,
                text=payload.get("text", ""),
                score=hit.score,
                file_path=payload.get("file_path", ""),
                chunk_index=payload.get("chunk_index", 0),
                metadata={
                    "source": payload.get("source", ""),
                    "file": payload.get("file_path", ""),
                },
            ))
        return results

    def count(self) -> int:
        info = self._client.get_collection(self.COLLECTION)
        return info.points_count

    def drop_collection(self) -> None:
        """Drop and recreate the collection (for full reindex)."""
        self._client.delete_collection(self.COLLECTION)
        self._ensure_collection()
