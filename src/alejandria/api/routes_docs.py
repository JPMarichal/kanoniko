"""Document listing API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from alejandria.api.schemas import DocumentListItem, DocumentListResponse
from alejandria.api.dependencies import get_registry
from alejandria.ingestion.registry import DocumentRegistry

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
def list_documents(
    registry: DocumentRegistry = Depends(get_registry),
) -> DocumentListResponse:
    records = registry.all_records()
    return DocumentListResponse(
        count=len(records),
        documents=[
            DocumentListItem(
                file_path=r.file_path,
                sha256=r.sha256,
                file_size=r.file_size,
                chunk_count=r.chunk_count,
                last_indexed=r.last_indexed,
                status=r.status,
            )
            for r in records
        ],
    )
