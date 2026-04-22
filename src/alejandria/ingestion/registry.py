"""Document registry — tracks indexed files and their content hashes.

This module exposes a :class:`DocumentRegistry` Protocol and a
:func:`make_document_registry` factory. The concrete implementation lives
in :mod:`alejandria.ingestion.postgres_registry`. The transitional
SQLite implementation was retired in §3.4.

Consumers should import :class:`DocumentRegistry` (for type hints),
:class:`FileRecord`, :func:`compute_hash`, and :func:`make_document_registry`.
They should not import the concrete classes directly — that defeats the
factory dispatch and ties the caller to a specific backend.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass
class FileRecord:
    """One row of the document registry.

    ``last_indexed`` is an ISO-8601 UTC string regardless of backend, so
    callers don't have to care whether the storage layer uses TEXT or
    TIMESTAMPTZ internally.
    """

    file_path: str
    sha256: str
    file_size: int
    chunk_count: int
    last_indexed: str
    status: str  # 'indexed' | 'error' | 'pending'


@runtime_checkable
class DocumentRegistry(Protocol):
    """Minimal interface for file-level index tracking.

    Only methods actually consumed by the rest of the codebase are exposed.
    Backend-specific conveniences (connection management, DDL, etc.) are
    implementation details.
    """

    def get_record(self, file_path: str) -> FileRecord | None: ...

    def upsert(
        self,
        file_path: str,
        sha256: str,
        file_size: int,
        chunk_count: int,
        status: str = "indexed",
    ) -> None: ...

    def delete(self, file_path: str) -> None: ...

    def all_records(self) -> list[FileRecord]: ...

    def count(self) -> int: ...

    def errors(self) -> list[FileRecord]: ...


def compute_hash(path: Path) -> str:
    """SHA-256 digest of a file's bytes. Backend-agnostic, pure IO."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            h.update(block)
    return h.hexdigest()


def make_document_registry(db_path: Path | None = None) -> DocumentRegistry:
    """Return the document registry over Postgres IONOS.

    ``db_path`` is accepted for backwards compat and ignored — the
    registry reads connection info from ``settings.postgres_*``.
    """
    from alejandria.ingestion.postgres_registry import PostgresDocumentRegistry

    return PostgresDocumentRegistry()
