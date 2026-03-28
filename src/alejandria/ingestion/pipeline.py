"""Ingestion pipeline: scan corpus, detect changes, parse, chunk, and index."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from alejandria.config import settings
from alejandria.ingestion.chunker import chunk_scripture, chunk_text
from alejandria.ingestion.parsers import parse_file
from alejandria.ingestion.registry import DocumentRegistry
from alejandria.ingestion.scripture_meta import (
    build_chunk_reference,
    build_scripture_metadata,
    is_scripture,
)
from alejandria.search.textual import TextualSearch

logger = logging.getLogger(__name__)

# Optional semantic search — None when Qdrant is not available
try:
    from alejandria.embeddings.model import encode
    from alejandria.search.semantic import SemanticSearch

    _SEMANTIC_AVAILABLE = True
except ImportError:
    _SEMANTIC_AVAILABLE = False

# Optional knowledge graph
try:
    from alejandria.knowledge.extractor import KGExtractor
    from alejandria.knowledge.neo4j_client import Neo4jClient

    _KG_AVAILABLE = True
except ImportError:
    _KG_AVAILABLE = False


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
        semantic_search: SemanticSearch | None = None,
        neo4j_client: Neo4jClient | None = None,
        kg_extractor: KGExtractor | None = None,
    ) -> None:
        self._registry = registry
        self._textual = textual_search
        self._semantic = semantic_search
        self._neo4j = neo4j_client
        self._kg_extractor = kg_extractor

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
            # Delete registry records after FTS connection is released
            for file_path in registry_records:
                self._registry.delete(file_path)
            if self._semantic:
                self._semantic.drop_collection()
            if self._neo4j:
                self._neo4j.clear_all()
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

            if (
                record is not None
                and record.sha256 == current_hash
                and record.status == "indexed"
                and not full_reindex
            ):
                # Unchanged and successfully indexed — skip
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
        source = _extract_source(rel_path)
        lang = _extract_lang(rel_path)

        # Delete old data if exists
        conn = self._textual.get_connection()
        with conn:
            self._textual.delete_by_file(conn, rel_path)
        if self._semantic:
            self._semantic.delete_by_file(rel_path)

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

        # Chunk — use verse-aware chunking for scriptures
        scripture_file = is_scripture(rel_path)
        if scripture_file:
            chunks = chunk_scripture(text, target_words=150, max_words=300)
        else:
            chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)

        # Build per-chunk scripture references
        chunk_references: list[str | None] = []
        for chunk in chunks:
            if scripture_file:
                ref = build_chunk_reference(rel_path, chunk.text, text)
            else:
                ref = None
            chunk_references.append(ref)

        # Build base metadata
        base_meta: dict = {"source": source, "file": rel_path}
        if lang:
            base_meta["lang"] = lang
        # Add scripture-level metadata from first chunk (volume, book, etc.)
        if scripture_file:
            smeta = build_scripture_metadata(rel_path, chunks[0].text if chunks else "", text)
            base_meta.update({k: v for k, v in smeta.items() if k not in ("reference", "verse_start", "verse_end")})

        metadata_str = json.dumps(base_meta)

        # Index into FTS — collect chunk IDs for Qdrant
        chunk_ids: list[int] = []
        conn = self._textual.get_connection()
        with conn:
            for chunk, ref in zip(chunks, chunk_references):
                cid = self._textual.index_chunk(
                    conn=conn,
                    file_path=rel_path,
                    chunk_index=chunk.index,
                    text=chunk.text,
                    start_char=chunk.start_char,
                    end_char=chunk.end_char,
                    metadata=metadata_str,
                    reference=ref,
                )
                chunk_ids.append(cid)

        # Index into Qdrant (semantic)
        if self._semantic and _SEMANTIC_AVAILABLE:
            chunk_texts = [c.text for c in chunks]
            vectors = encode(chunk_texts)
            payloads = [
                {
                    "text": c.text,
                    "file_path": rel_path,
                    "chunk_index": c.index,
                    "source": source,
                    "reference": ref,
                    **({"lang": lang} if lang else {}),
                }
                for c, ref in zip(chunks, chunk_references)
            ]
            self._semantic.upsert_chunks(
                ids=chunk_ids,
                vectors=[v.tolist() for v in vectors],
                payloads=payloads,
            )

        # Index into Neo4j (knowledge graph)
        if self._neo4j and self._kg_extractor:
            self._neo4j.delete_document_relations(rel_path)
            self._neo4j.merge_document(rel_path, source)
            for chunk in chunks:
                extraction = self._kg_extractor.extract(chunk.text, source_file=rel_path)
                for entity in extraction.entities:
                    self._neo4j.merge_entity(entity.name, entity.type)
                    self._neo4j.link_entity_to_document(entity.name, entity.type, rel_path)
                for rel in extraction.relations:
                    self._neo4j.merge_relation(
                        from_name=rel.from_entity,
                        from_type=rel.from_type,
                        rel_type=rel.relation,
                        to_name=rel.to_entity,
                        to_type=rel.to_type,
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
        if self._semantic:
            self._semantic.delete_by_file(file_path)
        if self._neo4j:
            self._neo4j.delete_document_relations(file_path)
        self._registry.delete(file_path)
        logger.info("Deleted from index: %s", file_path)


def _extract_source(rel_path: str) -> str:
    """Extract the source category from the corpus path.

    New bilingual layout:  {lang}/{category}/...  -> category
    Legacy flat layout:    {category}/...          -> category
    """
    parts = rel_path.replace("\\", "/").split("/")
    # New layout: en/scriptures/... or es/general-conference/...
    if len(parts) >= 2 and parts[0] in ("en", "es"):
        return parts[1] if len(parts) > 2 else parts[0]
    # Legacy flat layout
    return parts[0] if len(parts) > 1 else "root"


def _extract_lang(rel_path: str) -> str | None:
    """Extract language code from the corpus path, or None if not detected."""
    parts = rel_path.replace("\\", "/").split("/")
    if parts and parts[0] in ("en", "es"):
        return parts[0]
    return None
