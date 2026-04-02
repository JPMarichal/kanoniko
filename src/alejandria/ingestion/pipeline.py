"""Ingestion pipeline: scan corpus, detect changes, parse, chunk, and index."""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from alejandria.authority import derive_authority
from alejandria.config import settings
from alejandria.ingestion.chunker import chunk_scripture, chunk_text
from alejandria.ingestion.parsers import parse_file
from alejandria.ingestion.registry import DocumentRegistry
from alejandria.ingestion.conference_parser import ConferenceTalk, parse_conference_talk
from alejandria.ingestion.scripture_meta import (
    build_chunk_reference,
    build_scripture_metadata,
    is_scripture,
)
from alejandria.search.textual import TextualSearch

# Optional profile store
try:
    from alejandria.knowledge.profile_store import EntityProfile, ProfileStore

    _PROFILES_AVAILABLE = True
except ImportError:
    _PROFILES_AVAILABLE = False

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


@dataclass
class IndexingProgress:
    """Live progress tracking for background indexing."""

    running: bool = False
    current_file: str = ""
    files_processed: int = 0
    files_total: int = 0
    start_time: float = 0.0
    last_stats: IndexingStats | None = None
    error_message: str | None = None

    @property
    def percent(self) -> float:
        if self.files_total == 0:
            return 0.0
        return round(self.files_processed / self.files_total * 100, 1)

    @property
    def elapsed(self) -> float:
        if self.start_time == 0:
            return 0.0
        return round(time.time() - self.start_time, 1)

    @property
    def eta_seconds(self) -> float | None:
        if self.files_processed == 0 or not self.running:
            return None
        rate = self.files_processed / self.elapsed if self.elapsed > 0 else 0
        if rate == 0:
            return None
        remaining = self.files_total - self.files_processed
        return round(remaining / rate, 0)


@dataclass
class _FileData:
    """Intermediate data for a file being indexed across pipeline phases."""

    rel_path: str
    abs_path: Path
    file_hash: str
    source: str
    lang: str | None
    chunks: list  # list of Chunk objects from chunker
    chunk_ids: list[int]  # FTS row IDs
    chunk_references: list[str | None]
    auth_meta: object  # AuthorityMetadata
    full_text: str
    vectors: object | None = None  # NDArray set in phase 2
    conference_talk: ConferenceTalk | None = None  # Parsed conference metadata


class IngestionPipeline:
    """Orchestrates incremental ingestion from corpus to search indices."""

    # Class-level lock to prevent concurrent indexing runs
    _index_lock = threading.Lock()

    def __init__(
        self,
        registry: DocumentRegistry,
        textual_search: TextualSearch,
        semantic_search: SemanticSearch | None = None,
        neo4j_client: Neo4jClient | None = None,
        kg_extractor: KGExtractor | None = None,
        profile_store: ProfileStore | None = None,
    ) -> None:
        self._registry = registry
        self._textual = textual_search
        self._semantic = semantic_search
        self._neo4j = neo4j_client
        self._kg_extractor = kg_extractor
        self._profile_store = profile_store
        self.progress = IndexingProgress()

    # Sources to preserve in Neo4j during full reindex
    PRESERVED_NEO4J_SOURCES = ["topical_guide"]

    def ingest_paths(self, paths: list[str]) -> IndexingStats:
        """Index specific corpus paths (files or directories) without scanning the full corpus.

        Args:
            paths: Relative corpus paths (e.g. ["en/proclamations/", "es/proclamations/doc.txt"]).
                   Directories are expanded to all supported files within.

        Raises:
            RuntimeError: If another indexing run is already in progress.
        """
        if not self._index_lock.acquire(blocking=False):
            raise RuntimeError("Indexing already in progress")

        try:
            return self._ingest_paths_impl(paths)
        finally:
            self._index_lock.release()

    def _ingest_paths_impl(self, paths: list[str]) -> IndexingStats:
        """Internal implementation for targeted path ingestion."""
        stats = IndexingStats()
        self.progress = IndexingProgress(running=True, start_time=time.time())
        corpus_path = settings.corpus_path

        try:
            # Resolve paths to actual files
            disk_files: dict[str, Path] = {}
            for p in paths:
                abs_p = corpus_path / p.replace("\\", "/")
                if abs_p.is_file() and abs_p.suffix in settings.supported_extensions:
                    rel = str(abs_p.relative_to(corpus_path))
                    disk_files[rel] = abs_p
                elif abs_p.is_dir():
                    for ext in settings.supported_extensions:
                        for f in abs_p.rglob(f"*{ext}"):
                            if f.is_file():
                                rel = str(f.relative_to(corpus_path))
                                disk_files[rel] = f

            if not disk_files:
                logger.warning("No indexable files found in paths: %s", paths)
                return stats

            # Get registry state only for these files
            registry_records = {r.file_path: r for r in self._registry.all_records()}

            # Build list of files to process
            to_process: list[tuple[str, Path, str, bool]] = []
            for rel_path, abs_path in disk_files.items():
                current_hash = DocumentRegistry.compute_hash(abs_path)
                record = registry_records.get(rel_path)

                if record is not None and record.sha256 == current_hash and record.status == "indexed":
                    continue

                is_update = record is not None
                to_process.append((rel_path, abs_path, current_hash, is_update))

            self.progress.files_total = len(to_process)
            logger.info(
                "Targeted ingest: %d files to process (%d resolved, %d unchanged)",
                len(to_process), len(disk_files), len(disk_files) - len(to_process),
            )

            # Reuse the same 3-phase pipeline
            # Phase 1 (CPU): Parse, chunk, FTS
            file_data_list: list[_FileData] = []
            for i, (rel_path, abs_path, current_hash, is_update) in enumerate(to_process):
                self.progress.current_file = rel_path
                self.progress.files_processed = i
                try:
                    fd = self._prepare_file(rel_path, abs_path, current_hash)
                    if fd is not None:
                        file_data_list.append(fd)
                        stats.total_chunks += len(fd.chunks)
                    if is_update:
                        stats.updated_files += 1
                    else:
                        stats.new_files += 1
                except Exception:
                    logger.exception("Error preparing %s", rel_path)
                    self._registry.upsert(
                        file_path=rel_path, sha256=current_hash,
                        file_size=abs_path.stat().st_size, chunk_count=0, status="error",
                    )
                    stats.errors += 1

            total_chunks = sum(len(fd.chunks) for fd in file_data_list)

            # Phase 2 (GPU): Batch-encode
            if self._semantic and _SEMANTIC_AVAILABLE and total_chunks > 0:
                all_texts = [c.text for fd in file_data_list for c in fd.chunks]
                all_vectors = encode(all_texts, batch_size=256)
                offset = 0
                for fd in file_data_list:
                    n = len(fd.chunks)
                    fd.vectors = all_vectors[offset:offset + n]
                    offset += n

            # Phase 3 (I/O): Qdrant + Neo4j
            for fd in file_data_list:
                self.progress.current_file = fd.rel_path
                try:
                    self._index_file_data(fd)
                except Exception:
                    logger.exception("Error indexing %s", fd.rel_path)
                    stats.errors += 1

            self.progress.files_processed = len(to_process)

            if (stats.new_files or stats.updated_files) and self._profile_store:
                staled = self._profile_store.mark_all_stale()
                if staled:
                    logger.info("Marked %d entity profiles as stale", staled)

            logger.info(
                "Targeted ingest complete: new=%d updated=%d errors=%d chunks=%d in %.1fs",
                stats.new_files, stats.updated_files, stats.errors, stats.total_chunks,
                self.progress.elapsed,
            )
            return stats

        finally:
            self.progress.last_stats = stats
            self.progress.running = False
            self.progress.current_file = ""

    def run(self, full_reindex: bool = False) -> IndexingStats:
        """Execute an indexing run with mutex protection.

        Args:
            full_reindex: If True, drop all indices and reindex everything.

        Raises:
            RuntimeError: If another indexing run is already in progress.
        """
        if not self._index_lock.acquire(blocking=False):
            raise RuntimeError("Indexing already in progress")

        try:
            return self._run_impl(full_reindex)
        finally:
            self._index_lock.release()

    def _run_impl(self, full_reindex: bool) -> IndexingStats:
        """Internal implementation of indexing run with progress tracking.

        Uses a 3-phase pipeline to maximize GPU utilization:
          Phase 1 (CPU): Parse, chunk, build metadata, index FTS → collect chunk IDs
          Phase 2 (GPU): Batch-encode ALL chunks across all files in one call
          Phase 3 (I/O): Batch-upsert vectors to Qdrant + KG extraction to Neo4j
        """
        stats = IndexingStats()
        self.progress = IndexingProgress(running=True, start_time=time.time())
        corpus_path = settings.corpus_path

        try:
            if not corpus_path.exists():
                logger.warning("Corpus path does not exist: %s", corpus_path)
                return stats

            # Pre-index backup (SQLite + Qdrant snapshot)
            try:
                from alejandria.backup import pre_index_backup
                backup_result = pre_index_backup()
                logger.info("Pre-index backup: %s", backup_result)
            except Exception:
                logger.warning("Pre-index backup failed — continuing without backup", exc_info=True)

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
                    self._neo4j.clear_all(
                        preserve_sources=self.PRESERVED_NEO4J_SOURCES,
                    )
                registry_records = {}

            # Detect deleted files
            for file_path in list(registry_records.keys()):
                if file_path not in disk_files:
                    self._delete_file(file_path)
                    stats.deleted_files += 1

            # Build list of files to process (skip unchanged)
            to_process: list[tuple[str, Path, str, bool]] = []
            for rel_path, abs_path in disk_files.items():
                current_hash = DocumentRegistry.compute_hash(abs_path)
                record = registry_records.get(rel_path)

                if (
                    record is not None
                    and record.sha256 == current_hash
                    and record.status == "indexed"
                    and not full_reindex
                ):
                    continue

                is_update = record is not None
                to_process.append((rel_path, abs_path, current_hash, is_update))

            self.progress.files_total = len(to_process)
            logger.info(
                "Indexing: %d files to process (%d on disk, %d unchanged)",
                len(to_process), len(disk_files),
                len(disk_files) - len(to_process),
            )

            # ── Phase 1 (CPU): Parse, chunk, FTS index, collect data ──
            logger.info("Phase 1/3: Parsing, chunking, FTS indexing...")
            file_data_list: list[_FileData] = []

            for i, (rel_path, abs_path, current_hash, is_update) in enumerate(to_process):
                self.progress.current_file = rel_path
                self.progress.files_processed = i

                try:
                    fd = self._prepare_file(rel_path, abs_path, current_hash)
                    if fd is not None:
                        file_data_list.append(fd)
                        stats.total_chunks += len(fd.chunks)
                    if is_update:
                        stats.updated_files += 1
                    else:
                        stats.new_files += 1
                except Exception:
                    logger.exception("Error preparing %s", rel_path)
                    self._registry.upsert(
                        file_path=rel_path,
                        sha256=current_hash,
                        file_size=abs_path.stat().st_size,
                        chunk_count=0,
                        status="error",
                    )
                    stats.errors += 1

            total_chunks = sum(len(fd.chunks) for fd in file_data_list)
            logger.info(
                "Phase 1 done: %d files parsed, %d total chunks in %.1fs",
                len(file_data_list), total_chunks, self.progress.elapsed,
            )

            # ── Phase 2 (GPU): Batch-encode all chunks at once ──
            if self._semantic and _SEMANTIC_AVAILABLE and total_chunks > 0:
                logger.info("Phase 2/3: Batch-encoding %d chunks...", total_chunks)
                all_texts = []
                for fd in file_data_list:
                    all_texts.extend(c.text for c in fd.chunks)

                all_vectors = encode(all_texts, batch_size=256)

                # Distribute vectors back to each file's data
                offset = 0
                for fd in file_data_list:
                    n = len(fd.chunks)
                    fd.vectors = all_vectors[offset:offset + n]
                    offset += n

                logger.info("Phase 2 done: %d vectors encoded in %.1fs", total_chunks, self.progress.elapsed)
            else:
                logger.info("Phase 2/3: Skipped (semantic search not available)")

            # ── Phase 3 (I/O): Qdrant upsert + Neo4j KG extraction ──
            logger.info("Phase 3/3: Upserting vectors + KG extraction...")
            for i, fd in enumerate(file_data_list):
                self.progress.current_file = fd.rel_path
                self.progress.files_processed = len(to_process) - len(file_data_list) + i

                try:
                    self._index_file_data(fd)
                except Exception:
                    logger.exception("Error indexing %s", fd.rel_path)
                    stats.errors += 1

                if (i + 1) % 100 == 0:
                    logger.info(
                        "Phase 3 progress: %d/%d files (%.1f%%)",
                        i + 1, len(file_data_list), (i + 1) / len(file_data_list) * 100,
                    )

            self.progress.files_processed = len(to_process)

            # Mark profiles stale if corpus changed
            if (stats.new_files or stats.updated_files or stats.deleted_files) and self._profile_store:
                staled = self._profile_store.mark_all_stale()
                if staled:
                    logger.info("Marked %d entity profiles as stale after corpus change", staled)

            logger.info(
                "Indexing complete: new=%d updated=%d deleted=%d errors=%d chunks=%d in %.1fs",
                stats.new_files, stats.updated_files, stats.deleted_files,
                stats.errors, stats.total_chunks, self.progress.elapsed,
            )
            return stats

        finally:
            self.progress.last_stats = stats
            self.progress.running = False
            self.progress.current_file = ""

    def _prepare_file(self, rel_path: str, abs_path: Path, file_hash: str) -> _FileData | None:
        """Phase 1: Parse, chunk, build metadata, index into FTS. Returns file data for phases 2-3."""
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
                file_path=rel_path, sha256=file_hash,
                file_size=abs_path.stat().st_size, chunk_count=0, status="indexed",
            )
            return None

        # Chunk
        scripture_file = is_scripture(rel_path)
        if scripture_file:
            chunks = chunk_scripture(text, target_words=150, max_words=300)
        else:
            chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)

        # Build per-chunk scripture references
        chunk_references: list[str | None] = []
        for chunk in chunks:
            ref = build_chunk_reference(rel_path, chunk.text, text) if scripture_file else None
            chunk_references.append(ref)

        # Parse conference talk metadata if applicable
        conference_talk: ConferenceTalk | None = None
        if _is_conference(rel_path) and abs_path.suffix.lower() in (".html", ".htm"):
            try:
                raw_html = abs_path.read_text(encoding="utf-8")
                conference_talk = parse_conference_talk(raw_html, file_path=rel_path)
            except Exception:
                logger.warning("Failed to parse conference talk metadata: %s", rel_path, exc_info=True)

        # Build base metadata
        base_meta: dict = {"source": source, "file": rel_path}
        if lang:
            base_meta["lang"] = lang
        if scripture_file:
            smeta = build_scripture_metadata(rel_path, chunks[0].text if chunks else "", text)
            base_meta.update({k: v for k, v in smeta.items() if k not in ("reference", "verse_start", "verse_end")})
        if conference_talk:
            base_meta["author"] = conference_talk.author
            base_meta["title"] = conference_talk.title
            if conference_talk.calling:
                base_meta["calling"] = conference_talk.calling
            if conference_talk.conference_date:
                base_meta["conference_date"] = conference_talk.conference_date

        auth_meta = derive_authority(source, rel_path)
        base_meta["auth"] = auth_meta.to_dict()
        metadata_str = json.dumps(base_meta)

        # Index into FTS — collect chunk IDs for Qdrant
        chunk_ids: list[int] = []
        conn = self._textual.get_connection()
        with conn:
            for chunk, ref in zip(chunks, chunk_references):
                cid = self._textual.index_chunk(
                    conn=conn, file_path=rel_path, chunk_index=chunk.index,
                    text=chunk.text, start_char=chunk.start_char, end_char=chunk.end_char,
                    metadata=metadata_str, reference=ref,
                )
                chunk_ids.append(cid)

        return _FileData(
            rel_path=rel_path, abs_path=abs_path, file_hash=file_hash,
            source=source, lang=lang, chunks=chunks, chunk_ids=chunk_ids,
            chunk_references=chunk_references, auth_meta=auth_meta, full_text=text,
            conference_talk=conference_talk,
        )

    def _index_file_data(self, fd: _FileData) -> None:
        """Phase 3: Upsert vectors to Qdrant + KG extraction to Neo4j."""
        # Qdrant upsert (vectors were computed in phase 2)
        if self._semantic and _SEMANTIC_AVAILABLE and fd.vectors is not None:
            auth_dict = fd.auth_meta.to_dict()
            # Conference-specific payload fields
            conf_fields: dict = {}
            if fd.conference_talk:
                ct = fd.conference_talk
                conf_fields = {
                    "author": ct.author,
                    "title": ct.title,
                    **({"calling": ct.calling} if ct.calling else {}),
                    **({"conference_date": ct.conference_date} if ct.conference_date else {}),
                }
            payloads = [
                {
                    "text": c.text,
                    "file_path": fd.rel_path,
                    "chunk_index": c.index,
                    "source": fd.source,
                    "reference": ref,
                    **({"lang": fd.lang} if fd.lang else {}),
                    "authority": auth_dict["authority"],
                    "rigor": auth_dict["rigor"],
                    "importance": auth_dict["importance"],
                    "official": auth_dict["official"],
                    **conf_fields,
                }
                for c, ref in zip(fd.chunks, fd.chunk_references)
            ]
            self._semantic.upsert_chunks(
                ids=fd.chunk_ids,
                vectors=[v.tolist() for v in fd.vectors],
                payloads=payloads,
            )

        # Neo4j KG extraction (batched per file)
        if self._neo4j and self._kg_extractor:
            self._neo4j.delete_document_relations(fd.rel_path)
            self._neo4j.batch_merge_documents([{"file_path": fd.rel_path, "source": fd.source}])
            batch_ents: list[dict] = []
            batch_lnks: list[dict] = []
            batch_rels: list[dict] = []
            seen_ents: set[tuple[str, str]] = set()
            seen_lnks: set[tuple[str, str, str]] = set()
            for chunk in fd.chunks:
                extraction = self._kg_extractor.extract(chunk.text, source_file=fd.rel_path)
                for entity in extraction.entities:
                    ekey = (entity.name, entity.type)
                    if ekey not in seen_ents:
                        seen_ents.add(ekey)
                        batch_ents.append({"name": entity.name, "type": entity.type, "aliases": []})
                    lkey = (entity.name, entity.type, fd.rel_path)
                    if lkey not in seen_lnks:
                        seen_lnks.add(lkey)
                        batch_lnks.append({"entity_name": entity.name, "entity_type": entity.type, "file_path": fd.rel_path})
                for rel in extraction.relations:
                    batch_rels.append({
                        "from_name": rel.from_entity, "from_type": rel.from_type,
                        "rel_type": rel.relation,
                        "to_name": rel.to_entity, "to_type": rel.to_type,
                        "props": {},
                    })

            # Conference-specific KG enrichment: DELIVERED_BY + CITES
            if fd.conference_talk:
                ct = fd.conference_talk
                # Speaker entity + DELIVERED_BY relation (talk → person)
                if ct.author:
                    speaker_key = (ct.author, "person")
                    if speaker_key not in seen_ents:
                        seen_ents.add(speaker_key)
                        batch_ents.append({"name": ct.author, "type": "person", "aliases": []})
                    batch_rels.append({
                        "from_name": ct.title, "from_type": "talk",
                        "rel_type": "DELIVERED_BY",
                        "to_name": ct.author, "to_type": "person",
                        "props": {
                            "confidence": "metadata",
                            **({"calling": ct.calling} if ct.calling else {}),
                            **({"date": ct.conference_date} if ct.conference_date else {}),
                        },
                    })
                    # Link speaker to document
                    spk_lkey = (ct.author, "person", fd.rel_path)
                    if spk_lkey not in seen_lnks:
                        seen_lnks.add(spk_lkey)
                        batch_lnks.append({"entity_name": ct.author, "entity_type": "person", "file_path": fd.rel_path})

                # Talk entity (so DELIVERED_BY and CITES have a source node)
                talk_key = (ct.title, "talk")
                if talk_key not in seen_ents:
                    seen_ents.add(talk_key)
                    batch_ents.append({"name": ct.title, "type": "talk", "aliases": []})
                talk_lkey = (ct.title, "talk", fd.rel_path)
                if talk_lkey not in seen_lnks:
                    seen_lnks.add(talk_lkey)
                    batch_lnks.append({"entity_name": ct.title, "entity_type": "talk", "file_path": fd.rel_path})

                # Conference event entity + talk PART_OF conference
                if ct.conference_date:
                    conf_name = _conference_event_name(ct.conference_date)
                    conf_key = (conf_name, "conference")
                    if conf_key not in seen_ents:
                        seen_ents.add(conf_key)
                        batch_ents.append({"name": conf_name, "type": "conference", "aliases": [ct.conference_date]})
                    batch_rels.append({
                        "from_name": ct.title, "from_type": "talk",
                        "rel_type": "PART_OF",
                        "to_name": conf_name, "to_type": "conference",
                        "props": {"confidence": "metadata"},
                    })

                # CITES relations: talk → scripture_reference (with context from note)
                for ref in ct.scripture_refs:
                    ref_key = (ref, "scripture_reference")
                    if ref_key not in seen_ents:
                        seen_ents.add(ref_key)
                        batch_ents.append({"name": ref, "type": "scripture_reference", "aliases": []})
                    # Find the note text that contains this reference for context
                    note_context = ""
                    for note in ct.notes_raw:
                        if ref in note:
                            note_context = note
                            break
                    batch_rels.append({
                        "from_name": ct.title, "from_type": "talk",
                        "rel_type": "CITES",
                        "to_name": ref, "to_type": "scripture_reference",
                        "props": {
                            "confidence": "metadata",
                            **({"note_context": note_context[:500]} if note_context else {}),
                            **({"date": ct.conference_date} if ct.conference_date else {}),
                        },
                    })

                # Calling entity + CALLED_AS relation if available
                if ct.calling:
                    call_key = (ct.calling, "calling")
                    if call_key not in seen_ents:
                        seen_ents.add(call_key)
                        batch_ents.append({"name": ct.calling, "type": "calling", "aliases": []})
                    batch_rels.append({
                        "from_name": ct.author, "from_type": "person",
                        "rel_type": "CALLED_AS",
                        "to_name": ct.calling, "to_type": "calling",
                        "props": {
                            "confidence": "metadata",
                            **({"date": ct.conference_date} if ct.conference_date else {}),
                        },
                    })

            self._neo4j.batch_merge_entities(batch_ents)
            self._neo4j.batch_link_entities_to_document(batch_lnks)
            self._neo4j.batch_merge_relations(batch_rels)

        # Update registry
        self._registry.upsert(
            file_path=fd.rel_path, sha256=fd.file_hash,
            file_size=fd.abs_path.stat().st_size,
            chunk_count=len(fd.chunks), status="indexed",
        )

    def _ingest_file(self, rel_path: str, abs_path: Path, file_hash: str) -> int:
        """Parse, chunk, and index a single file. Returns chunk count. (Legacy single-file path.)"""
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

        # Derive authority metadata from corpus path
        auth_meta = derive_authority(source, rel_path)
        base_meta["auth"] = auth_meta.to_dict()

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
            auth_dict = auth_meta.to_dict()
            payloads = [
                {
                    "text": c.text,
                    "file_path": rel_path,
                    "chunk_index": c.index,
                    "source": source,
                    "reference": ref,
                    **({"lang": lang} if lang else {}),
                    "authority": auth_dict["authority"],
                    "rigor": auth_dict["rigor"],
                    "importance": auth_dict["importance"],
                    "official": auth_dict["official"],
                }
                for c, ref in zip(chunks, chunk_references)
            ]
            self._semantic.upsert_chunks(
                ids=chunk_ids,
                vectors=[v.tolist() for v in vectors],
                payloads=payloads,
            )

        # Index into Neo4j (knowledge graph) — batched per file
        if self._neo4j and self._kg_extractor:
            self._neo4j.delete_document_relations(rel_path)
            self._neo4j.batch_merge_documents([{"file_path": rel_path, "source": source}])
            batch_ents: list[dict] = []
            batch_lnks: list[dict] = []
            batch_rels: list[dict] = []
            seen_ents: set[tuple[str, str]] = set()
            seen_lnks: set[tuple[str, str, str]] = set()
            for chunk in chunks:
                extraction = self._kg_extractor.extract(chunk.text, source_file=rel_path)
                for entity in extraction.entities:
                    ekey = (entity.name, entity.type)
                    if ekey not in seen_ents:
                        seen_ents.add(ekey)
                        batch_ents.append({"name": entity.name, "type": entity.type, "aliases": []})
                    lkey = (entity.name, entity.type, rel_path)
                    if lkey not in seen_lnks:
                        seen_lnks.add(lkey)
                        batch_lnks.append({"entity_name": entity.name, "entity_type": entity.type, "file_path": rel_path})
                for rel in extraction.relations:
                    batch_rels.append({
                        "from_name": rel.from_entity, "from_type": rel.from_type,
                        "rel_type": rel.relation,
                        "to_name": rel.to_entity, "to_type": rel.to_type,
                        "props": {},
                    })
            self._neo4j.batch_merge_entities(batch_ents)
            self._neo4j.batch_link_entities_to_document(batch_lnks)
            self._neo4j.batch_merge_relations(batch_rels)

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

    def rebuild_vectors(self) -> dict:
        """Rebuild ONLY semantic vectors from already-indexed chunks in SQLite.

        Reads chunk text + metadata from SQLite, batch-encodes on GPU, and
        upserts to Qdrant. No filesystem I/O — ideal for GPU migration.

        Returns stats dict.
        """
        if not self._semantic or not _SEMANTIC_AVAILABLE:
            return {"error": "Semantic search not available"}

        start = time.time()

        # Drop and recreate Qdrant collection
        logger.info("Vector rebuild: dropping Qdrant collection...")
        self._semantic.drop_collection()

        # Read all chunks from SQLite
        conn = self._textual.get_connection()
        rows = conn.execute(
            "SELECT rowid, file_path, chunk_index, text, metadata, reference "
            "FROM chunks ORDER BY file_path, chunk_index"
        ).fetchall()
        conn.close()

        total = len(rows)
        logger.info("Vector rebuild: encoding %d chunks...", total)

        # Batch-encode ALL texts in one GPU call
        all_texts = [r[3] if isinstance(r, (list, tuple)) else r["text"] for r in rows]
        all_vectors = encode(all_texts, batch_size=256)

        logger.info("Vector rebuild: encoding done in %.1fs, upserting to Qdrant...", time.time() - start)

        # Batch upsert to Qdrant in groups of 500
        batch_size = 500
        for i in range(0, total, batch_size):
            batch_rows = rows[i:i + batch_size]
            batch_vectors = all_vectors[i:i + batch_size]

            ids = []
            vectors = []
            payloads = []

            for row, vec in zip(batch_rows, batch_vectors):
                rowid = row[0] if isinstance(row, (list, tuple)) else row["rowid"]
                file_path = row[1] if isinstance(row, (list, tuple)) else row["file_path"]
                chunk_index = row[2] if isinstance(row, (list, tuple)) else row["chunk_index"]
                text = row[3] if isinstance(row, (list, tuple)) else row["text"]
                metadata_str = row[4] if isinstance(row, (list, tuple)) else row["metadata"]
                reference = row[5] if isinstance(row, (list, tuple)) else row["reference"]

                meta = json.loads(metadata_str) if metadata_str else {}
                auth = meta.get("auth", {})

                ids.append(rowid)
                vectors.append(vec.tolist())
                payloads.append({
                    "text": text,
                    "file_path": file_path,
                    "chunk_index": chunk_index,
                    "source": meta.get("source", ""),
                    "reference": reference,
                    **({"lang": meta.get("lang")} if meta.get("lang") else {}),
                    "authority": auth.get("authority", 0),
                    "rigor": auth.get("rigor", 0),
                    "importance": auth.get("importance", 0),
                    "official": auth.get("official", False),
                })

            self._semantic.upsert_chunks(ids=ids, vectors=vectors, payloads=payloads)

            if (i + batch_size) % 5000 == 0 or i + batch_size >= total:
                logger.info(
                    "Vector rebuild: %d/%d upserted (%.0f%%)",
                    min(i + batch_size, total), total,
                    min(i + batch_size, total) / total * 100,
                )

        elapsed = time.time() - start
        stats = {
            "chunks_encoded": total,
            "elapsed_seconds": round(elapsed, 1),
        }
        logger.info("Vector rebuild complete: %d chunks in %.1fs", total, elapsed)
        return stats

    def rebuild_kg(self) -> dict:
        """Rebuild ONLY the knowledge graph from already-indexed chunks in SQLite.

        This is much faster than full_reindex because it skips parsing,
        chunking, embedding, FTS, and Qdrant — only reads chunk text from
        SQLite and runs the KG extractor against the current gazetteers.

        Returns stats dict with counts.
        """
        if not self._neo4j or not self._kg_extractor:
            return {"error": "Neo4j or KG extractor not available"}

        import time

        start = time.time()

        # Clear existing KG data (preserve external imports like TG)
        logger.info("KG rebuild: clearing existing graph...")
        self._neo4j.clear_all(preserve_sources=self.PRESERVED_NEO4J_SOURCES)

        # Load scripture structural entities and relations (P1 Phase 3)
        try:
            from alejandria.knowledge.scripture_structure import get_structure
            structure = get_structure()
            structural_entities = structure.get_structural_entities()
            structural_relations = structure.get_structural_relations()
            for se in structural_entities:
                self._neo4j.merge_entity(se["name"], se["type"],
                                          aliases=[se["name_es"]] if se["name_es"] != se["name_en"] else [])
            for sr in structural_relations:
                self._neo4j.merge_relation(
                    from_name=sr["from_name"], from_type=sr["from_type"],
                    rel_type=sr["relation"],
                    to_name=sr["to_name"], to_type=sr["to_type"],
                    properties={"source": "scripture_structure", "confidence": "curated"},
                )
            logger.info(
                "KG rebuild: loaded %d structural entities, %d structural relations",
                len(structural_entities), len(structural_relations),
            )
        except Exception:
            logger.warning("Failed to load scripture structure — continuing without it", exc_info=True)

        # Read all chunks from SQLite
        conn = self._textual.get_connection()
        rows = conn.execute(
            "SELECT file_path, chunk_index, text FROM chunks ORDER BY file_path, chunk_index"
        ).fetchall()
        conn.close()

        total_chunks = len(rows)
        logger.info("KG rebuild: processing %d chunks...", total_chunks)

        entities_found = 0
        relations_found = 0
        documents_seen: set[str] = set()

        # Batch accumulators — flush every BATCH_SIZE chunks
        BATCH_SIZE = 500
        batch_entities: list[dict] = []
        batch_relations: list[dict] = []
        batch_links: list[dict] = []
        batch_documents: list[dict] = []

        def _flush_batch() -> None:
            """Send accumulated batch to Neo4j."""
            nonlocal batch_entities, batch_relations, batch_links, batch_documents
            if batch_documents:
                self._neo4j.batch_merge_documents(batch_documents)
                batch_documents = []
            if batch_entities:
                # Deduplicate entities within batch (same name+type)
                seen = set()
                deduped = []
                for e in batch_entities:
                    key = (e["name"], e["type"])
                    if key not in seen:
                        seen.add(key)
                        deduped.append(e)
                self._neo4j.batch_merge_entities(deduped)
                batch_entities = []
            if batch_links:
                # Deduplicate links
                seen_links = set()
                deduped_links = []
                for lnk in batch_links:
                    key = (lnk["entity_name"], lnk["entity_type"], lnk["file_path"])
                    if key not in seen_links:
                        seen_links.add(key)
                        deduped_links.append(lnk)
                self._neo4j.batch_link_entities_to_document(deduped_links)
                batch_links = []
            if batch_relations:
                self._neo4j.batch_merge_relations(batch_relations)
                batch_relations = []

        for i, row in enumerate(rows):
            file_path = row[0] if isinstance(row, (list, tuple)) else row["file_path"]
            text = row[2] if isinstance(row, (list, tuple)) else row["text"]

            # Ensure document node exists
            if file_path not in documents_seen:
                source = _extract_source(file_path)
                batch_documents.append({"file_path": file_path, "source": source})
                documents_seen.add(file_path)

            # Extract entities and relations
            extraction = self._kg_extractor.extract(text, source_file=file_path)

            for entity in extraction.entities:
                batch_entities.append(
                    {"name": entity.name, "type": entity.type, "aliases": []}
                )
                batch_links.append(
                    {"entity_name": entity.name, "entity_type": entity.type, "file_path": file_path}
                )
                entities_found += 1

            for rel in extraction.relations:
                batch_relations.append({
                    "from_name": rel.from_entity,
                    "from_type": rel.from_type,
                    "rel_type": rel.relation,
                    "to_name": rel.to_entity,
                    "to_type": rel.to_type,
                    "props": {},
                })
                relations_found += 1

            if (i + 1) % BATCH_SIZE == 0:
                _flush_batch()
                logger.info(
                    "KG rebuild: %d/%d chunks (%.0f%%), %d entities, %d relations so far...",
                    i + 1, total_chunks, (i + 1) / total_chunks * 100,
                    entities_found, relations_found,
                )

        # Flush remaining
        _flush_batch()

        # Mark all profiles stale after KG rebuild
        if self._profile_store:
            staled = self._profile_store.mark_all_stale()
            if staled:
                logger.info("Marked %d entity profiles as stale after KG rebuild", staled)

        elapsed = time.time() - start
        stats = {
            "chunks_processed": total_chunks,
            "documents": len(documents_seen),
            "entity_mentions": entities_found,
            "relation_mentions": relations_found,
            "elapsed_seconds": round(elapsed, 1),
        }
        logger.info(
            "KG rebuild complete: %d chunks, %d entities, %d relations in %.1fs",
            total_chunks, entities_found, relations_found, elapsed,
        )
        return stats

    def build_metadata_profiles(
        self,
        entity_types: list[str] | None = None,
        max_entities: int = 0,
        max_passages: int = 10,
    ) -> dict:
        """Build metadata-only entity profiles from Neo4j + SQLite.

        Phase 1 of entity profiles — no LLM calls, purely computational.
        Reads entity mentions from Neo4j, fetches text snippets from SQLite
        chunks, and stores aggregated profiles in ProfileStore.

        Args:
            entity_types: Filter to specific types (e.g. ["person"]). None = all.
            max_entities: Limit how many entities to process. 0 = all.
            max_passages: Max key passages per entity.

        Returns stats dict.
        """
        if not self._neo4j:
            return {"error": "Neo4j not available"}
        if not self._profile_store:
            return {"error": "ProfileStore not available"}

        import time

        start = time.time()

        # Build reverse lookup: canonical_name -> all aliases (from gazetteer)
        gazetteer_aliases: dict[str, list[str]] = {}
        if self._kg_extractor:
            for term, candidates in self._kg_extractor._lookup.items():
                for canonical, _ in candidates:
                    if canonical not in gazetteer_aliases:
                        gazetteer_aliases[canonical] = []
                    if term.lower() != canonical.lower():
                        gazetteer_aliases[canonical].append(term)

        # 1. Bulk query: all entities with their documents from Neo4j
        logger.info("Profile build: querying entity mentions from Neo4j...")
        all_mentions = self._neo4j.get_all_entity_mentions()

        if entity_types:
            type_set = set(entity_types)
            all_mentions = [m for m in all_mentions if m["type"] in type_set]

        if max_entities > 0:
            all_mentions = all_mentions[:max_entities]

        total = len(all_mentions)
        logger.info("Profile build: processing %d entities...", total)

        # 2. For each entity, query SQLite chunks from its documents, extract snippets
        profiles: list[EntityProfile] = []
        conn = self._textual.get_connection()

        try:
            for i, mention in enumerate(all_mentions):
                name = mention["name"]
                entity_type = mention["type"]
                aliases = mention.get("aliases") or []
                file_paths = mention["file_paths"]
                doc_count = mention["doc_count"]

                # Build searchable names: canonical + Neo4j aliases + gazetteer aliases
                search_names = [name]
                if aliases and isinstance(aliases, list):
                    search_names.extend(a for a in aliases if a)
                # Add gazetteer aliases (often richer than Neo4j's)
                for ga in gazetteer_aliases.get(name, []):
                    search_names.append(ga)
                # Deduplicate preserving order
                seen_names: set[str] = set()
                unique_names: list[str] = []
                for sn in search_names:
                    if sn.lower() not in seen_names:
                        seen_names.add(sn.lower())
                        unique_names.append(sn)

                # Query chunks that contain ANY of the searchable names
                placeholders = ",".join("?" * len(file_paths))
                like_clauses = " OR ".join(["LOWER(text) LIKE ?"] * len(unique_names))
                like_params = [f"%{sn.lower()}%" for sn in unique_names]
                rows = conn.execute(
                    f"SELECT file_path, chunk_index, text, reference "
                    f"FROM chunks WHERE file_path IN ({placeholders}) "
                    f"AND ({like_clauses}) "
                    f"ORDER BY file_path, chunk_index",
                    [*file_paths, *like_params],
                ).fetchall()

                mention_count = len(rows)

                # Extract books from file_paths
                books = sorted({_extract_book(fp) for fp in file_paths if _extract_book(fp)})

                # Build key passages with volume diversity.
                # Group candidate passages by corpus volume, then round-robin
                # to ensure coverage across OT, NT, BoM, D&C, PGP, conference, etc.
                candidates_by_volume: dict[str, list[dict]] = {}
                seen_docs: set[str] = set()
                for row in rows:
                    fp = row[0] if isinstance(row, (list, tuple)) else row["file_path"]
                    if fp in seen_docs:
                        continue
                    seen_docs.add(fp)

                    text = row[2] if isinstance(row, (list, tuple)) else row["text"]
                    ref = row[3] if isinstance(row, (list, tuple)) else row["reference"]

                    snippet = None
                    for sn in unique_names:
                        if sn.lower() in text.lower():
                            snippet = _extract_snippet(text, sn, max_len=200)
                            break
                    if snippet is None:
                        snippet = text[:200] + ("..." if len(text) > 200 else "")

                    vol = _extract_volume(fp)
                    candidates_by_volume.setdefault(vol, []).append(
                        {"reference": ref or fp, "snippet": snippet}
                    )

                # Round-robin across volumes: 1 per volume first, then fill remaining
                key_passages: list[dict] = []
                vol_iters = {v: iter(ps) for v, ps in candidates_by_volume.items()}
                while len(key_passages) < max_passages and vol_iters:
                    exhausted = []
                    for vol, it in vol_iters.items():
                        if len(key_passages) >= max_passages:
                            break
                        p = next(it, None)
                        if p is None:
                            exhausted.append(vol)
                        else:
                            key_passages.append(p)
                    for vol in exhausted:
                        del vol_iters[vol]

                profile = EntityProfile(
                    entity_name=name,
                    entity_type=entity_type,
                    mention_count=mention_count,
                    document_count=doc_count,
                    books=books,
                    key_passages=key_passages,
                    aliases=[n for n in unique_names[1:] if n],  # all names except canonical
                    status="metadata",
                )
                profiles.append(profile)

                if (i + 1) % 200 == 0:
                    logger.info(
                        "Profile build: %d/%d entities (%.0f%%)...",
                        i + 1, total, (i + 1) / total * 100,
                    )
        finally:
            conn.close()

        # 3. Batch upsert into ProfileStore
        logger.info("Profile build: saving %d profiles...", len(profiles))
        self._profile_store.upsert_batch(profiles)

        # 4. Clean up orphan profiles (entities that no longer exist in Neo4j)
        valid_keys = {(p.entity_name, p.entity_type) for p in profiles}
        orphans_deleted = self._profile_store.delete_orphans(valid_keys)
        if orphans_deleted:
            logger.info("Profile build: deleted %d orphan profiles", orphans_deleted)

        elapsed = time.time() - start
        stats = {
            "entities_processed": len(profiles),
            "orphans_deleted": orphans_deleted,
            "elapsed_seconds": round(elapsed, 1),
        }
        logger.info("Profile build complete: %d entities in %.1fs", len(profiles), elapsed)
        return stats

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


def _is_conference(rel_path: str) -> bool:
    """Check if a file is a general conference talk by corpus path."""
    parts = rel_path.replace("\\", "/").split("/")
    return len(parts) >= 2 and "general-conference" in parts


_MONTH_TO_SEASON = {"04": "April", "10": "October"}


def _conference_event_name(date_str: str) -> str:
    """Build a human-readable conference event name from 'YYYY-MM'.

    >>> _conference_event_name("2024-10")
    'General Conference October 2024'
    >>> _conference_event_name("1971-04")
    'General Conference April 1971'
    """
    parts = date_str.split("-")
    year = parts[0] if parts else date_str
    month = _MONTH_TO_SEASON.get(parts[1], parts[1]) if len(parts) > 1 else ""
    return f"General Conference {month} {year}".strip()


def _extract_lang(rel_path: str) -> str | None:
    """Extract language code from the corpus path, or None if not detected."""
    parts = rel_path.replace("\\", "/").split("/")
    if parts and parts[0] in ("en", "es"):
        return parts[0]
    return None


def _extract_volume(rel_path: str) -> str:
    """Extract the corpus volume/category from a file path.

    Returns a broad grouping used for diverse passage selection.
    Examples:
        en/scriptures/ot/genesis/1.txt -> ot
        en/scriptures/nt/matthew/1.txt -> nt
        en/scriptures/bom/alma/32.txt -> bom
        en/scriptures/dc-testament/dc/1.txt -> dc
        en/scriptures/pgp/moses/1.txt -> pgp
        en/general-conference/2023/04/talk.txt -> conference
        en/manuals/gospel-principles/1.txt -> manuals
    """
    parts = rel_path.replace("\\", "/").split("/")
    if "scriptures" in parts:
        idx = parts.index("scriptures")
        if idx + 1 < len(parts):
            vol = parts[idx + 1].lower()
            # Normalize volume names
            if "old-testament" in vol or vol == "ot":
                return "ot"
            if "new-testament" in vol or vol == "nt":
                return "nt"
            if "book-of-mormon" in vol or vol == "bom":
                return "bom"
            if "dc-testament" in vol or "doctrine" in vol or vol == "dc":
                return "dc"
            if "pearl" in vol or vol == "pgp":
                return "pgp"
            return vol
    if "general-conference" in parts or "conference" in parts:
        return "conference"
    if "manuals" in parts:
        return "manuals"
    if "biographies" in parts:
        return "biographies"
    if "web" in parts:
        return "web"
    return "other"


def _extract_book(rel_path: str) -> str | None:
    """Extract the book name from a corpus file path.

    Examples:
        en/scriptures/book-of-mormon/alma/32.txt -> Alma
        es/scriptures/old-testament/genesis/1.txt -> Genesis
        en/general-conference/2023/04/talk.txt -> general-conference/2023/04
    """
    parts = rel_path.replace("\\", "/").split("/")
    # Scripture files: lang/scriptures/volume/book/chapter.txt
    if len(parts) >= 4 and "scriptures" in parts:
        idx = parts.index("scriptures")
        if idx + 2 < len(parts):
            return parts[idx + 2].replace("-", " ").title()
    # Non-scripture: return category/subdirectory
    if len(parts) >= 3:
        return "/".join(parts[1:-1])
    return None


def _extract_snippet(text: str, entity_name: str, max_len: int = 200) -> str:
    """Extract a short snippet from text centered around the entity mention."""
    idx = text.lower().find(entity_name.lower())
    if idx == -1:
        return text[:max_len] + ("..." if len(text) > max_len else "")

    # Center the window around the mention
    half = max_len // 2
    start = max(0, idx - half)
    end = min(len(text), idx + len(entity_name) + half)
    snippet = text[start:end].strip()

    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet
