"""Ingestion pipeline: scan corpus, detect changes, parse, chunk, and index."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from alejandria.config import settings
from alejandria.ingestion.chunker import chunk_text
from alejandria.ingestion.parsers import parse_file
from alejandria.ingestion.registry import DocumentRegistry
from alejandria.search.textual import TextualSearch

logger = logging.getLogger(__name__)


@dataclass
class IndexingStats:
    new_files: int = 0
    updated_files: int = 0
    deleted_files: int = 0
    errors: int = 0
    total_chunks: int = 0


class IngestionPipeline:
    """Orchestrates incremental ingestion from corpus to search indices."""

    def __init__(
        self,
        registry: DocumentRegistry,
        textual_search: TextualSearch,
    ) -> None:
        self._registry = registry
        self._textual = textual_search

    def run(self, full_reindex: bool = False) -> IndexingStats:
        """Execute an indexing run.

        Args:
            full_reindex: If True, drop all indices and reindex everything.
        """
        stats = IndexingStats()
        corpus_path = settings.corpus_path

        if not corpus_path.exists():
            logger.warning("Corpus path does not exist: %s", corpus_path)
            return stats

        # Collect current files on disk
        disk_files: dict[str, Path] = {}
        for ext in settings.supported_extensions:
            for path in corpus_path.rglob(f"*{ext}"):
                if path.is_file():
                    rel = str(path.relative_to(corpus_path))
                    disk_files[rel] = path

        # Get registry state
        registry_records = {r.file_path: r for r in self._registry.all_records()}

        if full_reindex:
            # Delete everything and re-ingest
            conn = self._textual.get_connection()
            with conn:
                for file_path in registry_records:
                    self._textual.delete_by_file(conn, file_path)
                    self._registry.delete(file_path)
            registry_records = {}

        # Detect deleted files
        for file_path in list(registry_records.keys()):
            if file_path not in disk_files:
                self._delete_file(file_path)
                stats.deleted_files += 1

        # Process new and modified files
        for rel_path, abs_path in disk_files.items():
            current_hash = DocumentRegistry.compute_hash(abs_path)
            record = registry_records.get(rel_path)

            if record is not None and record.sha256 == current_hash and not full_reindex:
                # Unchanged — skip
                continue

            is_update = record is not None
            try:
                chunk_count = self._ingest_file(rel_path, abs_path, current_hash)
                stats.total_chunks += chunk_count
                if is_update:
                    stats.updated_files += 1
                else:
                    stats.new_files += 1
            except Exception:
                logger.exception("Error ingesting %s", rel_path)
                self._registry.upsert(
                    file_path=rel_path,
                    sha256=current_hash,
                    file_size=abs_path.stat().st_size,
                    chunk_count=0,
                    status="error",
                )
                stats.errors += 1

        logger.info(
            "Indexing complete: new=%d updated=%d deleted=%d errors=%d chunks=%d",
            stats.new_files, stats.updated_files, stats.deleted_files,
            stats.errors, stats.total_chunks,
        )
        return stats

    def _ingest_file(self, rel_path: str, abs_path: Path, file_hash: str) -> int:
        """Parse, chunk, and index a single file. Returns chunk count."""
        # Delete old data if exists
        conn = self._textual.get_connection()
        with conn:
            self._textual.delete_by_file(conn, rel_path)

        # Parse
        text = parse_file(abs_path)
        if not text.strip():
            self._registry.upsert(
                file_path=rel_path,
                sha256=file_hash,
                file_size=abs_path.stat().st_size,
                chunk_count=0,
                status="indexed",
            )
            return 0

        # Chunk
        chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)

        # Build metadata
        metadata = json.dumps({
            "source": _extract_source(rel_path),
            "file": rel_path,
        })

        # Index into FTS
        conn = self._textual.get_connection()
        with conn:
            for chunk in chunks:
                self._textual.index_chunk(
                    conn=conn,
                    file_path=rel_path,
                    chunk_index=chunk.index,
                    text=chunk.text,
                    start_char=chunk.start_char,
                    end_char=chunk.end_char,
                    metadata=metadata,
                )

        # Update registry
        self._registry.upsert(
            file_path=rel_path,
            sha256=file_hash,
            file_size=abs_path.stat().st_size,
            chunk_count=len(chunks),
            status="indexed",
        )

        logger.info("Indexed %s (%d chunks)", rel_path, len(chunks))
        return len(chunks)

    def _delete_file(self, file_path: str) -> None:
        """Remove a file from all indices."""
        conn = self._textual.get_connection()
        with conn:
            self._textual.delete_by_file(conn, file_path)
        self._registry.delete(file_path)
        logger.info("Deleted from index: %s", file_path)


def _extract_source(rel_path: str) -> str:
    """Extract the top-level corpus subdirectory as the source category."""
    parts = rel_path.replace("\\", "/").split("/")
    return parts[0] if len(parts) > 1 else "root"
