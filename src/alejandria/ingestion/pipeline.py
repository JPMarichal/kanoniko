"""Ingestion pipeline: scan corpus, detect changes, parse, chunk, and index."""

from __future__ import annotations

import concurrent.futures
import json
import logging
import os
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

from alejandria.authority import derive_authority
from alejandria.config import settings
from alejandria.ingestion.chunker import chunk_handbook, chunk_scripture, chunk_text
from alejandria.ingestion.parsers import parse_file
from alejandria.ingestion.registry import DocumentRegistry
from alejandria.ingestion.conference_parser import (
    ConferenceTalk,
    conference_talk_from_meta,
    parse_conference_talk,
)
from alejandria.knowledge.note_sanitizer import extract_note_relations
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
    # Per-phase tracking
    phase: int = 0            # 1=parse+FTS, 2=embeddings, 3=vectors+KG, 0=idle/done
    phase_start_time: float = 0.0
    phase_2_chunks: int = 0   # total chunks to encode (set at phase 2 start)
    phase_3_total: int = 0    # total files for phase 3
    phase_3_done: int = 0     # files completed in phase 3
    # Phase 3 chunk-weighted ETA — chunk count is proportional to actual work
    phase_3_chunks_total: int = 0   # total chunks across all phase-3 files (known after phase 1)
    phase_3_chunks_done: int = 0    # chunks from completed phase-3 files
    # Rolling window: deque of (timestamp, chunks_done) at each file completion (last 100)
    _phase_3_window: deque = field(default_factory=lambda: deque(maxlen=100), repr=False)

    @property
    def phase_name(self) -> str:
        return {1: "parse_fts", 2: "embeddings", 3: "vectors_kg"}.get(self.phase, "")

    @property
    def percent(self) -> float:
        if self.files_total == 0:
            return 0.0
        return round(self.files_processed / self.files_total * 100, 1)

    @property
    def phase_percent(self) -> float:
        if self.phase == 1:
            return self.percent
        if self.phase == 2:
            return 100.0 if self.phase_2_chunks > 0 else 0.0
        if self.phase == 3 and self.phase_3_total > 0:
            return round(self.phase_3_done / self.phase_3_total * 100, 1)
        return 0.0

    @property
    def elapsed(self) -> float:
        if self.start_time == 0:
            return 0.0
        return round(time.time() - self.start_time, 1)

    @property
    def phase_elapsed(self) -> float:
        if self.phase_start_time == 0:
            return 0.0
        return round(time.time() - self.phase_start_time, 1)

    @property
    def eta_seconds(self) -> float | None:
        if not self.running:
            return None
        elapsed = self.phase_elapsed
        if self.phase == 3 and self.phase_3_chunks_total > 0 and self.phase_3_chunks_done > 0:
            # Use rolling window (last 100 files) for responsive chunk-rate estimate
            if len(self._phase_3_window) >= 2:
                oldest_ts, oldest_chunks = self._phase_3_window[0]
                newest_ts, newest_chunks = self._phase_3_window[-1]
                window_elapsed = newest_ts - oldest_ts
                window_chunks = newest_chunks - oldest_chunks
                if window_elapsed > 0 and window_chunks > 0:
                    rate = window_chunks / window_elapsed
                    remaining = self.phase_3_chunks_total - self.phase_3_chunks_done
                    return round(remaining / rate, 0)
            # Fallback to cumulative rate if window not populated yet
            if elapsed > 0:
                rate = self.phase_3_chunks_done / elapsed
                remaining = self.phase_3_chunks_total - self.phase_3_chunks_done
                return round(remaining / rate, 0)
        if self.phase == 1 and self.files_processed > 0 and elapsed > 0:
            rate = self.files_processed / elapsed
            remaining = self.files_total - self.files_processed
            return round(remaining / rate, 0)
        return None


@dataclass
class _FileData:
    """Intermediate data for a file being indexed across pipeline phases."""

    rel_path: str
    abs_path: Path
    file_hash: str
    source: str
    lang: str | None
    chunks: list  # list of Chunk objects from chunker
    chunk_ids: list[int]  # FTS row IDs — filled in by _fts_insert, empty after _parse_file_cpu
    chunk_references: list[str | None]
    auth_meta: object  # AuthorityMetadata
    full_text: str
    metadata_str: str = ""  # JSON-serialized base metadata, built in _parse_file_cpu
    vectors: object | None = None  # NDArray set in phase 2
    conference_talk: ConferenceTalk | None = None  # Parsed conference metadata
    meta_json: dict | None = None  # Companion .meta.json content (music, manuals, etc.)


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
        *,
        semantic_search_factory: callable | None = None,
        neo4j_client_factory: callable | None = None,
        kg_extractor_factory: callable | None = None,
    ) -> None:
        self._registry = registry
        self._textual = textual_search
        self._semantic_direct = semantic_search
        self._neo4j_direct = neo4j_client
        self._kg_extractor_direct = kg_extractor
        self._semantic_factory = semantic_search_factory
        self._neo4j_factory = neo4j_client_factory
        self._kg_extractor_factory = kg_extractor_factory
        self._profile_store = profile_store
        self.progress = IndexingProgress()

    @property
    def _semantic(self):
        if self._semantic_direct is not None:
            return self._semantic_direct
        if self._semantic_factory is not None:
            result = self._semantic_factory()
            if result is not None:
                self._semantic_direct = result
            return result
        return None

    @property
    def _neo4j(self):
        if self._neo4j_direct is not None:
            return self._neo4j_direct
        if self._neo4j_factory is not None:
            result = self._neo4j_factory()
            if result is not None:
                self._neo4j_direct = result
            return result
        return None

    @property
    def _kg_extractor(self):
        if self._kg_extractor_direct is not None:
            return self._kg_extractor_direct
        if self._kg_extractor_factory is not None:
            result = self._kg_extractor_factory()
            if result is not None:
                self._kg_extractor_direct = result
            return result
        return None

    # Sources to preserve in Neo4j during full reindex
    PRESERVED_NEO4J_SOURCES = ["topical_guide"]

    def ingest_paths(self, paths: list[str], *, force: bool = False) -> IndexingStats:
        """Index specific corpus paths (files or directories) without scanning the full corpus.

        Args:
            paths: Relative corpus paths (e.g. ["en/proclamations/", "es/proclamations/doc.txt"]).
                   Directories are expanded to all supported files within.
            force: If True, re-index even if the file hash hasn't changed.

        Raises:
            RuntimeError: If another indexing run is already in progress.
        """
        if not self._index_lock.acquire(blocking=False):
            raise RuntimeError("Indexing already in progress")

        try:
            return self._ingest_paths_impl(paths, force=force)
        finally:
            self._index_lock.release()

    def _ingest_paths_impl(self, paths: list[str], *, force: bool = False) -> IndexingStats:
        """Internal implementation for targeted path ingestion."""
        stats = IndexingStats()
        self.progress = IndexingProgress(running=True, start_time=time.time())
        corpus_path = settings.corpus_path

        try:
            # Resolve paths to actual files
            disk_files: dict[str, Path] = {}
            for p in paths:
                abs_p = corpus_path / p.replace("\\", "/")
                if abs_p.is_file() and abs_p.suffix in settings.supported_extensions and not abs_p.name.endswith(".meta.json"):
                    rel = str(abs_p.relative_to(corpus_path))
                    disk_files[rel] = abs_p
                elif abs_p.is_dir():
                    for ext in settings.supported_extensions:
                        for f in abs_p.rglob(f"*{ext}"):
                            if f.is_file() and not f.name.endswith(".meta.json"):
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

                if not force and record is not None and record.sha256 == current_hash and record.status == "indexed":
                    continue

                is_update = record is not None
                to_process.append((rel_path, abs_path, current_hash, is_update))

            self.progress.files_total = len(to_process)
            logger.info(
                "Targeted ingest: %d files to process (%d resolved, %d unchanged)",
                len(to_process), len(disk_files), len(disk_files) - len(to_process),
            )

            # 3-phase pipeline (same as _run_impl)
            n_workers = min(os.cpu_count() or 4, 8)
            self.progress.phase = 1
            self.progress.phase_start_time = time.time()
            file_data_list: list[_FileData] = []

            # Phase 1a: Delete old data for updates only
            updates = [(rp, ap, h) for rp, ap, h, is_upd in to_process if is_upd]
            if updates:
                conn_del = self._textual.get_connection()
                with conn_del:
                    for rel_path, _, _ in updates:
                        self._textual.delete_by_file(conn_del, rel_path)
                conn_del.close()
                if self._semantic:
                    for rel_path, _, _ in updates:
                        self._semantic.delete_by_file(rel_path)

            # Phase 1b: Parse in parallel
            parse_map: dict[str, _FileData | None] = {}
            errored: set[str] = set()
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=n_workers, thread_name_prefix="parse"
            ) as executor:
                future_to_file = {
                    executor.submit(self._parse_file_cpu, rel_path, abs_path, current_hash):
                    (rel_path, abs_path, current_hash, is_update)
                    for rel_path, abs_path, current_hash, is_update in to_process
                }
                for i, future in enumerate(concurrent.futures.as_completed(future_to_file)):
                    rel_path, abs_path, current_hash, is_update = future_to_file[future]
                    self.progress.current_file = rel_path
                    self.progress.files_processed = i
                    try:
                        parse_map[rel_path] = future.result()
                    except Exception:
                        logger.exception("Error parsing %s", rel_path)
                        errored.add(rel_path)
                        self._registry.upsert(
                            file_path=rel_path, sha256=current_hash,
                            file_size=abs_path.stat().st_size, chunk_count=0, status="error",
                        )
                        stats.errors += 1

            # Phase 1c: FTS insert (serial, single connection)
            conn_fts = self._textual.get_connection()
            try:
                for rel_path, abs_path, current_hash, is_update in to_process:
                    if rel_path in errored:
                        continue
                    fd = parse_map.get(rel_path)
                    if fd is None:
                        self._registry.upsert(
                            file_path=rel_path, sha256=current_hash,
                            file_size=abs_path.stat().st_size, chunk_count=0, status="indexed",
                        )
                        if is_update:
                            stats.updated_files += 1
                        else:
                            stats.new_files += 1
                        continue
                    try:
                        self._fts_insert(fd, conn_fts)
                        file_data_list.append(fd)
                        stats.total_chunks += len(fd.chunks)
                        if is_update:
                            stats.updated_files += 1
                        else:
                            stats.new_files += 1
                    except Exception:
                        logger.exception("Error inserting FTS for %s", rel_path)
                        self._registry.upsert(
                            file_path=rel_path, sha256=current_hash,
                            file_size=abs_path.stat().st_size, chunk_count=0, status="error",
                        )
                        stats.errors += 1
            finally:
                conn_fts.close()

            total_chunks = sum(len(fd.chunks) for fd in file_data_list)

            # Phase 2 (GPU): Batch-encode
            self.progress.phase = 2
            self.progress.phase_start_time = time.time()
            self.progress.phase_2_chunks = total_chunks
            if self._semantic and _SEMANTIC_AVAILABLE and total_chunks > 0:
                all_texts = [c.text for fd in file_data_list for c in fd.chunks]
                all_vectors = encode(all_texts, batch_size=256)
                offset = 0
                for fd in file_data_list:
                    n = len(fd.chunks)
                    fd.vectors = all_vectors[offset:offset + n]
                    offset += n

            # Phase 3 (I/O): Qdrant + Neo4j
            self.progress.phase = 3
            self.progress.phase_start_time = time.time()
            self.progress.phase_3_total = len(file_data_list)
            self.progress.phase_3_done = 0
            self.progress.phase_3_chunks_total = sum(len(fd.chunks) for fd in file_data_list)
            self.progress.phase_3_chunks_done = 0
            self.progress._phase_3_window.clear()
            for i, fd in enumerate(file_data_list):
                self.progress.current_file = fd.rel_path
                try:
                    self._index_file_data(fd)
                except Exception:
                    logger.exception("Error indexing %s", fd.rel_path)
                    stats.errors += 1

                self.progress.phase_3_done = i + 1
                self.progress.phase_3_chunks_done += len(fd.chunks)
                self.progress._phase_3_window.append(
                    (time.time(), self.progress.phase_3_chunks_done)
                )

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
            # Exclude .meta.json — those are metadata sidecars, not content.
            disk_files: dict[str, Path] = {}
            for ext in settings.supported_extensions:
                for path in corpus_path.rglob(f"*{ext}"):
                    if path.is_file() and not path.name.endswith(".meta.json"):
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

            # Apply KG seeds before processing — ensures research-phase knowledge
            # is in the graph before NER extraction runs on individual files
            if self._neo4j and self._kg_extractor:
                seed_entities, seed_relations = _load_kg_seeds()
                if seed_entities:
                    self._neo4j.batch_merge_entities(seed_entities)
                if seed_relations:
                    self._neo4j.batch_merge_relations(seed_relations)

                # Load curated relations from gazetteers/relations.json (P6 Phase 1)
                try:
                    from alejandria.knowledge.extractor import _RELATIONS_PATH
                    if _RELATIONS_PATH.exists():
                        counts = self._neo4j.load_curated_relations(_RELATIONS_PATH)
                        total_curated = sum(counts.values())
                        logger.info(
                            "Loaded %d curated relations across %d types",
                            total_curated, len([c for c in counts.values() if c > 0]),
                        )
                except Exception:
                    logger.warning("Failed to load curated relations", exc_info=True)

            # ── Phase 1 (CPU): Parse (parallel) + FTS index (serial, single conn) ──
            n_workers = min(os.cpu_count() or 4, 8)
            self.progress.phase = 1
            self.progress.phase_start_time = time.time()
            logger.info(
                "Phase 1/3: Parsing %d files (parallel, %d workers) + FTS indexing...",
                len(to_process), n_workers,
            )
            file_data_list: list[_FileData] = []

            # 1a: Delete old data for updated files only (serial, batched in one connection)
            updates = [(rp, ap, h) for rp, ap, h, is_upd in to_process if is_upd]
            if updates:
                conn_del = self._textual.get_connection()
                with conn_del:
                    for rel_path, _, _ in updates:
                        self._textual.delete_by_file(conn_del, rel_path)
                conn_del.close()
                if self._semantic:
                    for rel_path, _, _ in updates:
                        self._semantic.delete_by_file(rel_path)
                logger.info("Phase 1a: deleted old data for %d updated files", len(updates))

            # 1b: Parse + chunk in parallel (no SQLite)
            parse_map: dict[str, _FileData | None] = {}
            errored: set[str] = set()
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=n_workers, thread_name_prefix="parse"
            ) as executor:
                future_to_file = {
                    executor.submit(self._parse_file_cpu, rel_path, abs_path, current_hash):
                    (rel_path, abs_path, current_hash, is_update)
                    for rel_path, abs_path, current_hash, is_update in to_process
                }
                for i, future in enumerate(concurrent.futures.as_completed(future_to_file)):
                    rel_path, abs_path, current_hash, is_update = future_to_file[future]
                    self.progress.current_file = rel_path
                    self.progress.files_processed = i
                    try:
                        parse_map[rel_path] = future.result()
                    except Exception:
                        logger.exception("Error parsing %s", rel_path)
                        errored.add(rel_path)
                        self._registry.upsert(
                            file_path=rel_path, sha256=current_hash,
                            file_size=abs_path.stat().st_size, chunk_count=0, status="error",
                        )
                        stats.errors += 1

            # 1c: FTS insert (serial, single shared connection)
            conn_fts = self._textual.get_connection()
            try:
                for rel_path, abs_path, current_hash, is_update in to_process:
                    if rel_path in errored:
                        continue
                    fd = parse_map.get(rel_path)
                    if fd is None:
                        # Empty file — register with 0 chunks
                        self._registry.upsert(
                            file_path=rel_path, sha256=current_hash,
                            file_size=abs_path.stat().st_size, chunk_count=0, status="indexed",
                        )
                        if is_update:
                            stats.updated_files += 1
                        else:
                            stats.new_files += 1
                        continue
                    try:
                        self._fts_insert(fd, conn_fts)
                        file_data_list.append(fd)
                        stats.total_chunks += len(fd.chunks)
                        if is_update:
                            stats.updated_files += 1
                        else:
                            stats.new_files += 1
                    except Exception:
                        logger.exception("Error inserting FTS for %s", rel_path)
                        self._registry.upsert(
                            file_path=rel_path, sha256=current_hash,
                            file_size=abs_path.stat().st_size, chunk_count=0, status="error",
                        )
                        stats.errors += 1
            finally:
                conn_fts.close()

            total_chunks = sum(len(fd.chunks) for fd in file_data_list)
            logger.info(
                "Phase 1 done: %d files parsed, %d total chunks in %.1fs",
                len(file_data_list), total_chunks, self.progress.elapsed,
            )

            # ── Phase 2 (GPU): Batch-encode all chunks at once ──
            self.progress.phase = 2
            self.progress.phase_start_time = time.time()
            self.progress.phase_2_chunks = total_chunks
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
            phase_3_start = time.time()
            self.progress.phase = 3
            self.progress.phase_start_time = phase_3_start
            self.progress.phase_3_total = len(file_data_list)
            self.progress.phase_3_done = 0
            self.progress.phase_3_chunks_total = sum(len(fd.chunks) for fd in file_data_list)
            self.progress.phase_3_chunks_done = 0
            self.progress._phase_3_window.clear()
            logger.info("Phase 3/3: Upserting vectors + KG extraction...")
            for i, fd in enumerate(file_data_list):
                self.progress.current_file = fd.rel_path
                self.progress.files_processed = len(to_process) - len(file_data_list) + i

                try:
                    self._index_file_data(fd)
                except Exception:
                    logger.exception("Error indexing %s", fd.rel_path)
                    stats.errors += 1

                self.progress.phase_3_done = i + 1
                self.progress.phase_3_chunks_done += len(fd.chunks)
                self.progress._phase_3_window.append(
                    (time.time(), self.progress.phase_3_chunks_done)
                )

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

    def _parse_file_cpu(self, rel_path: str, abs_path: Path, file_hash: str) -> _FileData | None:
        """CPU-bound parse + chunk + metadata build. No SQLite. Safe for ThreadPoolExecutor.

        Returns _FileData with chunk_ids=[] (not yet inserted into FTS).
        Returns None if the file is empty after parsing.
        """
        source = _extract_source(rel_path)
        lang = _extract_lang(rel_path)

        text = parse_file(abs_path)
        if not text.strip():
            return None

        scripture_file = is_scripture(rel_path)
        handbook_file = _is_handbook(rel_path)
        if scripture_file:
            chunks = chunk_scripture(text, target_words=150, max_words=300)
        elif handbook_file:
            chunks = chunk_handbook(text, settings.chunk_size, settings.chunk_overlap)
        else:
            chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)

        chunk_references: list[str | None] = [
            build_chunk_reference(rel_path, chunk.text, text) if scripture_file
            else chunk.reference if handbook_file
            else None
            for chunk in chunks
        ]

        conference_talk: ConferenceTalk | None = (
            _load_conference_metadata(abs_path, rel_path) if _is_conference(rel_path) else None
        )

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

        file_meta_json = _load_meta_json(rel_path, settings.corpus_path)

        return _FileData(
            rel_path=rel_path, abs_path=abs_path, file_hash=file_hash,
            source=source, lang=lang, chunks=chunks, chunk_ids=[],
            chunk_references=chunk_references, auth_meta=auth_meta, full_text=text,
            metadata_str=json.dumps(base_meta),
            conference_talk=conference_talk,
            meta_json=file_meta_json or None,
        )

    def _fts_insert(self, fd: _FileData, conn) -> None:
        """Insert parsed chunks into FTS5. Fills fd.chunk_ids in-place. Must run serially."""
        with conn:
            for chunk, ref in zip(fd.chunks, fd.chunk_references):
                cid = self._textual.index_chunk(
                    conn=conn, file_path=fd.rel_path, chunk_index=chunk.index,
                    text=chunk.text, start_char=chunk.start_char, end_char=chunk.end_char,
                    metadata=fd.metadata_str, reference=ref,
                )
                fd.chunk_ids.append(cid)

    def _prepare_file(self, rel_path: str, abs_path: Path, file_hash: str) -> _FileData | None:
        """Phase 1 (single-file path): parse, chunk, delete old data, insert FTS.

        Used by legacy callers. For bulk indexing prefer the parallel Phase 1 in
        _run_impl / _ingest_paths_impl which calls _parse_file_cpu + _fts_insert directly.
        """
        # Always treat as potential update (safe — delete is a no-op for new files)
        conn = self._textual.get_connection()
        with conn:
            self._textual.delete_by_file(conn, rel_path)
        if self._semantic:
            self._semantic.delete_by_file(rel_path)

        fd = self._parse_file_cpu(rel_path, abs_path, file_hash)
        if fd is None:
            self._registry.upsert(
                file_path=rel_path, sha256=file_hash,
                file_size=abs_path.stat().st_size, chunk_count=0, status="indexed",
            )
            return None

        conn = self._textual.get_connection()
        self._fts_insert(fd, conn)
        return fd

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

                # Note-derived KG relations: cross-references, hymns, concepts, books
                # Uses structured parsing (not NER) to avoid name+calling pollution
                if ct.notes_raw:
                    note_ents, note_rels = extract_note_relations(ct.title, ct.notes_raw)
                    for ne in note_ents:
                        ekey = (ne["name"], ne["type"])
                        if ekey not in seen_ents:
                            seen_ents.add(ekey)
                            batch_ents.append(ne)
                        # Link note-derived entities to document
                        lkey = (ne["name"], ne["type"], fd.rel_path)
                        if lkey not in seen_lnks:
                            seen_lnks.add(lkey)
                            batch_lnks.append({
                                "entity_name": ne["name"],
                                "entity_type": ne["type"],
                                "file_path": fd.rel_path,
                            })
                    batch_rels.extend(note_rels)

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

            # Structured meta.json KG enrichment: author, composer, tune, occasion
            # Handles music (hymns, songs) and other materials with rich metadata.
            # Creates person/concept entities and typed relations from meta.json fields,
            # complementing what NER extracts from text.
            if fd.meta_json:
                _enrich_kg_from_meta(
                    fd.meta_json, fd.rel_path,
                    batch_ents, batch_lnks, batch_rels,
                    seen_ents, seen_lnks,
                )

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

        # Chunk — use verse-aware chunking for scriptures, section-aware for handbook
        scripture_file = is_scripture(rel_path)
        handbook_file = _is_handbook(rel_path)
        if scripture_file:
            chunks = chunk_scripture(text, target_words=150, max_words=300)
        elif handbook_file:
            chunks = chunk_handbook(text, settings.chunk_size, settings.chunk_overlap)
        else:
            chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)

        # Build per-chunk references (scripture verse refs, handbook section refs, or None)
        chunk_references: list[str | None] = []
        for chunk in chunks:
            if scripture_file:
                ref = build_chunk_reference(rel_path, chunk.text, text)
            elif handbook_file:
                ref = chunk.reference
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

        # Ensure Neo4j indexes for query performance (P6 Phase 14)
        try:
            from alejandria.knowledge.indexes import ensure_indexes
            ensure_indexes(self._neo4j._driver)
        except Exception:
            logger.warning("Failed to create indexes — continuing without them", exc_info=True)

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

        # Apply KG seeds — research-phase knowledge asserted before NER
        # Seeds encode entities and relations discovered during corpus preparation.
        # Applied here so they exist before NER runs, giving them priority.
        seed_entities, seed_relations = _load_kg_seeds()
        if seed_entities:
            self._neo4j.batch_merge_entities(seed_entities)
        if seed_relations:
            self._neo4j.batch_merge_relations(seed_relations)

        # Load curated relations from gazetteers/relations.json (P6 Phase 1)
        # These are high-confidence typed relations (family trees, callings,
        # authorship, etc.) that must be in the graph with curated confidence.
        try:
            from alejandria.knowledge.extractor import _RELATIONS_PATH
            if _RELATIONS_PATH.exists():
                counts = self._neo4j.load_curated_relations(_RELATIONS_PATH)
                total_curated = sum(counts.values())
                logger.info(
                    "KG rebuild: loaded %d curated relations across %d types",
                    total_curated, len([c for c in counts.values() if c > 0]),
                )
        except Exception:
            logger.warning("Failed to load curated relations — continuing without them", exc_info=True)

        # Load scripture hierarchy into Neo4j (P6 Phase 6)
        try:
            from alejandria.knowledge.hierarchy_loader import load_hierarchy
            h_counts = load_hierarchy(self._neo4j._driver)
            logger.info("KG rebuild: hierarchy loaded — %d chapters, %d contains rels", h_counts.get("chapters", 0), h_counts.get("contains", 0))
        except Exception:
            logger.warning("Failed to load hierarchy — continuing without it", exc_info=True)

        # Load parallel narratives (P6 Phase 2)
        try:
            from alejandria.knowledge.parallels import load_parallels
            p_counts = load_parallels(self._neo4j._driver)
            logger.info("KG rebuild: parallels loaded — %d narratives, %d relations", p_counts.get("narratives", 0), p_counts.get("relations", 0))
        except Exception:
            logger.warning("Failed to load parallels — continuing without them", exc_info=True)

        # Extract metadata relations (P6 Phase 7) — depends on hierarchy (reads Chapter nodes)
        try:
            from alejandria.knowledge.metadata_relations import extract_metadata_relations
            m_counts = extract_metadata_relations(self._neo4j._driver)
            logger.info("KG rebuild: metadata relations — %d total", m_counts.get("total", 0))
        except Exception:
            logger.warning("Failed to extract metadata relations — continuing without them", exc_info=True)

        # Load cross-references (P6 Phase 8)
        try:
            from alejandria.knowledge.cross_ref_loader import load_cross_refs
            cr_counts = load_cross_refs(self._neo4j._driver)
            logger.info("KG rebuild: cross-refs — %d verses, %d rels", cr_counts.get("verse_nodes", 0), cr_counts.get("relationships", 0))
        except Exception:
            logger.warning("Failed to load cross-refs — continuing without them", exc_info=True)

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

            # Ensure document node exists + load meta.json once per document
            if file_path not in documents_seen:
                source = _extract_source(file_path)
                batch_documents.append({"file_path": file_path, "source": source})
                documents_seen.add(file_path)
                # Structured meta.json enrichment (author, composer, tune, occasion, etc.)
                file_meta = _load_meta_json(file_path, settings.corpus_path)
                if file_meta:
                    _enrich_kg_from_meta(
                        file_meta, file_path,
                        batch_entities, batch_links, batch_relations,
                        set(),  # dedup handled by batch_merge semantics in Neo4j
                        set(),
                    )

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


def _enrich_kg_from_meta(
    meta: dict,
    file_path: str,
    batch_ents: list[dict],
    batch_lnks: list[dict],
    batch_rels: list[dict],
    seen_ents: set[tuple[str, str]],
    seen_lnks: set[tuple[str, str, str]],
) -> None:
    """Enrich KG from structured meta.json fields.

    Creates entities and typed relations that NER cannot reliably infer from text.
    This is the ONLY path for KG knowledge derived from structured metadata —
    it must be called for every indexed file that has a companion meta.json.

    Supported fields and the relations they produce:

      title (str)            → `work` node (anchor for all relations below)
      author (str)           → work -[AUTHORED_BY]->  person
      composer (str)         → work -[COMPOSED_BY]->  person
      tune (str)             → work -[HAS_TUNE]->     concept
      occasion (str)         → work -[ASSOCIATED_WITH]-> concept
      book (str)             → work -[PART_OF]->      work  (parent volume)
      scripture_refs (list)  → work -[CITES]-> scripture_reference (×N)

      parallel_events (list) → Harmony of the Gospels structured table:
                               event node per row;
                               event -[DESCRIBED_IN]-> scripture_reference (per col)
                               scripture_ref -[PARALLEL_ACCOUNT_OF]-> scripture_ref
                               (upper-triangle cross-column pairs only)

      events (list)          → Bible Chronology structured table:
                               period node per date;
                               event -[OCCURRED_DURING]-> period
                               event -[PRECEDED_BY]-> previous_event (time-ordered)

    To support a new structured meta.json field, add a handler here AND document
    it in docs/download-scripts.md under "Campos KG soportados en _enrich_kg_from_meta".
    """
    import re as _re

    title = meta.get("title", "")
    if not title or not isinstance(title, str):
        return  # Need a work title as the relation subject

    work_key = (title, "work")
    if work_key not in seen_ents:
        seen_ents.add(work_key)
        batch_ents.append({"name": title, "type": "work", "aliases": []})
    work_lkey = (title, "work", file_path)
    if work_lkey not in seen_lnks:
        seen_lnks.add(work_lkey)
        batch_lnks.append({"entity_name": title, "entity_type": "work", "file_path": file_path})

    def _add_person(field: str, rel_type: str) -> None:
        raw = meta.get(field, "")
        if not raw or not isinstance(raw, str):
            return
        # Strip trailing year: "William W. Phelps, 1844" → "William W. Phelps"
        name = _re.split(r",?\s*\d{4}", raw)[0].strip()
        if len(name) < 3:
            return
        pkey = (name, "person")
        if pkey not in seen_ents:
            seen_ents.add(pkey)
            batch_ents.append({"name": name, "type": "person", "aliases": []})
        plkey = (name, "person", file_path)
        if plkey not in seen_lnks:
            seen_lnks.add(plkey)
            batch_lnks.append({"entity_name": name, "entity_type": "person", "file_path": file_path})
        batch_rels.append({
            "from_name": title, "from_type": "work",
            "rel_type": rel_type,
            "to_name": name, "to_type": "person",
            "props": {"confidence": "metadata", "source_field": field},
        })

    def _add_concept(field: str, rel_type: str) -> None:
        value = meta.get(field, "")
        if not value or not isinstance(value, str) or len(value) < 2:
            return
        ckey = (value, "concept")
        if ckey not in seen_ents:
            seen_ents.add(ckey)
            batch_ents.append({"name": value, "type": "concept", "aliases": []})
        clkey = (value, "concept", file_path)
        if clkey not in seen_lnks:
            seen_lnks.add(clkey)
            batch_lnks.append({"entity_name": value, "entity_type": "concept", "file_path": file_path})
        batch_rels.append({
            "from_name": title, "from_type": "work",
            "rel_type": rel_type,
            "to_name": value, "to_type": "concept",
            "props": {"confidence": "metadata", "source_field": field},
        })

    _add_person("author", "AUTHORED_BY")
    _add_person("composer", "COMPOSED_BY")
    _add_concept("tune", "HAS_TUNE")
    _add_concept("occasion", "ASSOCIATED_WITH")

    # book field: create a parent work node and a PART_OF relation
    # e.g., "Chapter 1" -[PART_OF]-> "Jesus the Christ"
    book = meta.get("book", "")
    if book and isinstance(book, str) and len(book) >= 3 and book != title:
        bkey = (book, "work")
        if bkey not in seen_ents:
            seen_ents.add(bkey)
            batch_ents.append({"name": book, "type": "work", "aliases": []})
        blkey = (book, "work", file_path)
        if blkey not in seen_lnks:
            seen_lnks.add(blkey)
            batch_lnks.append({"entity_name": book, "entity_type": "work", "file_path": file_path})
        batch_rels.append({
            "from_name": title, "from_type": "work",
            "rel_type": "PART_OF",
            "to_name": book, "to_type": "work",
            "props": {"confidence": "metadata"},
        })

    # scripture_refs: work -[CITES]-> scripture_reference
    # Mirrors the conference-talk CITES enrichment for any corpus document
    # that stores scripture references in meta.json (e.g., PME, study plans).
    for ref in meta.get("scripture_refs", []):
        if not isinstance(ref, str) or not ref.strip():
            continue
        ref_key = (ref, "scripture_reference")
        if ref_key not in seen_ents:
            seen_ents.add(ref_key)
            batch_ents.append({"name": ref, "type": "scripture_reference", "aliases": []})
        batch_rels.append({
            "from_name": title, "from_type": "work",
            "rel_type": "CITES",
            "to_name": ref, "to_type": "scripture_reference",
            "props": {"confidence": "metadata"},
        })

    # parallel_events: Harmony of the Gospels meta.json field.
    # Each entry maps one gospel event to its refs across 4–5 gospel columns
    # (matthew, mark, luke, john_lds). Creates:
    #   - An `event` node per event
    #   - event -[DESCRIBED_IN]-> scripture_reference (one per ref per column)
    #   - scripture_reference -[PARALLEL_ACCOUNT_OF]-> scripture_reference
    #     for every cross-column pair (same event, different volume)
    for pe in meta.get("parallel_events", []):
        ev_name = pe.get("event", "")
        if not ev_name or not isinstance(ev_name, str):
            continue

        ev_key = (ev_name, "event")
        if ev_key not in seen_ents:
            seen_ents.add(ev_key)
            batch_ents.append({
                "name": ev_name, "type": "event",
                "aliases": [],
                **({"location": pe["location"]} if pe.get("location") else {}),
            })
        ev_lkey = (ev_name, "event", file_path)
        if ev_lkey not in seen_lnks:
            seen_lnks.add(ev_lkey)
            batch_lnks.append({"entity_name": ev_name, "entity_type": "event",
                                "file_path": file_path})

        # Collect refs by column — skip non-column keys
        gospel_cols = ("matthew", "mark", "luke", "john_lds")
        cols_with_refs: list[tuple[str, list[str]]] = []
        for col in gospel_cols:
            refs = pe.get(col, [])
            if not isinstance(refs, list):
                continue
            valid = [r for r in refs if isinstance(r, str) and r.strip()]
            if valid:
                cols_with_refs.append((col, valid))

        # DESCRIBED_IN: event → each ref
        for _col, refs in cols_with_refs:
            for ref in refs:
                rkey = (ref, "scripture_reference")
                if rkey not in seen_ents:
                    seen_ents.add(rkey)
                    batch_ents.append({"name": ref, "type": "scripture_reference",
                                       "aliases": []})
                batch_rels.append({
                    "from_name": ev_name, "from_type": "event",
                    "rel_type": "DESCRIBED_IN",
                    "to_name": ref, "to_type": "scripture_reference",
                    "props": {"confidence": "metadata", "source": "harmony"},
                })

        # PARALLEL_ACCOUNT_OF: between refs in different gospel columns.
        # Only assert A→B (not B→A) by iterating upper triangle of column pairs.
        for i in range(len(cols_with_refs)):
            for j in range(i + 1, len(cols_with_refs)):
                _col_a, refs_a = cols_with_refs[i]
                _col_b, refs_b = cols_with_refs[j]
                for ref_a in refs_a:
                    for ref_b in refs_b:
                        batch_rels.append({
                            "from_name": ref_a, "from_type": "scripture_reference",
                            "rel_type": "PARALLEL_ACCOUNT_OF",
                            "to_name": ref_b, "to_type": "scripture_reference",
                            "props": {
                                "confidence": "metadata",
                                "event": ev_name,
                                "source": "harmony",
                            },
                        })

    # events: Bible Chronology meta.json field.
    # Each entry has date, event description, optional synchronisms and persons.
    # Creates:
    #   - A `period` node per unique date string
    #   - An `event` node per event
    #   - event -[OCCURRED_DURING]-> period
    #   - Consecutive events: event_N -[PRECEDED_BY]-> event_{N-1}
    #     (ordered by date_sort; only within the same meta.json file)
    chron_events = meta.get("events", [])
    if chron_events:
        # Sort by date_sort (int, negative = B.C.) for PRECEDED_BY chain
        def _sort_key(e: dict) -> int:
            ds = e.get("date_sort")
            return ds if isinstance(ds, int) else 0

        sorted_events = sorted(chron_events, key=_sort_key)
        prev_ev_name: str = ""

        for ce in sorted_events:
            ev_desc = ce.get("event", "")
            date_str = ce.get("date", "")
            if not ev_desc or not isinstance(ev_desc, str):
                continue

            # Period node for this date
            if date_str:
                period_key = (date_str, "period")
                if period_key not in seen_ents:
                    seen_ents.add(period_key)
                    batch_ents.append({"name": date_str, "type": "period", "aliases": []})
                period_lkey = (date_str, "period", file_path)
                if period_lkey not in seen_lnks:
                    seen_lnks.add(period_lkey)
                    batch_lnks.append({"entity_name": date_str, "entity_type": "period",
                                       "file_path": file_path})

            # Event node
            chron_ev_key = (ev_desc, "event")
            if chron_ev_key not in seen_ents:
                seen_ents.add(chron_ev_key)
                batch_ents.append({"name": ev_desc, "type": "event", "aliases": []})
            ev_lkey2 = (ev_desc, "event", file_path)
            if ev_lkey2 not in seen_lnks:
                seen_lnks.add(ev_lkey2)
                batch_lnks.append({"entity_name": ev_desc, "entity_type": "event",
                                   "file_path": file_path})

            # OCCURRED_DURING
            if date_str:
                batch_rels.append({
                    "from_name": ev_desc, "from_type": "event",
                    "rel_type": "OCCURRED_DURING",
                    "to_name": date_str, "to_type": "period",
                    "props": {"confidence": "metadata", "source": "bible-chronology"},
                })

            # PRECEDED_BY (chain: this event preceded by the previous one in time)
            if prev_ev_name:
                batch_rels.append({
                    "from_name": ev_desc, "from_type": "event",
                    "rel_type": "PRECEDED_BY",
                    "to_name": prev_ev_name, "to_type": "event",
                    "props": {"confidence": "metadata", "source": "bible-chronology"},
                })

            prev_ev_name = ev_desc


_KG_SEEDS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "kg-seeds"


def _load_kg_seeds() -> tuple[list[dict], list[dict]]:
    """Load all KG seed files from data/kg-seeds/.

    Seeds encode research-phase knowledge: entities and typed relations that
    the KG should assert before NER extraction. They are loaded at the start
    of every rebuild_kg run and every full indexing run, ensuring the KG
    baseline is always consistent regardless of what text NER discovers.

    Returns (entities, relations) as lists ready for batch_merge_* calls.
    """
    seeds_dir = _KG_SEEDS_DIR
    if not seeds_dir.exists():
        return [], []

    entities: list[dict] = []
    relations: list[dict] = []

    for seed_file in sorted(seeds_dir.glob("*.json")):
        try:
            seed = json.loads(seed_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("KG seed load failed: %s — %s", seed_file.name, e)
            continue

        confidence = seed.get("confidence", "curated")

        for ent in seed.get("entities", []):
            name = ent.get("name", "")
            etype = ent.get("type", "concept")
            if name and etype:
                entities.append({
                    "name": name,
                    "type": etype,
                    "aliases": ent.get("aliases", []),
                })

        for rel in seed.get("relations", []):
            subject = rel.get("subject", "")
            obj = rel.get("object", "")
            predicate = rel.get("predicate", "")
            if not (subject and obj and predicate):
                continue
            relations.append({
                "from_name": subject,
                "from_type": rel.get("subject_type", "concept"),
                "rel_type": predicate,
                "to_name": obj,
                "to_type": rel.get("object_type", "concept"),
                "props": {
                    "confidence": confidence,
                    **({"source_ref": rel["source_ref"]} if rel.get("source_ref") else {}),
                },
            })

    if entities or relations:
        logger.info(
            "KG seeds loaded: %d entities, %d relations from %d files",
            len(entities), len(relations),
            sum(1 for _ in seeds_dir.glob("*.json")),
        )
    return entities, relations


def _load_meta_json(rel_path: str, corpus_path: Path) -> dict:
    """Load companion .meta.json for a corpus file. Returns {} if not found or invalid."""
    base = rel_path
    for ext in (".txt", ".html", ".htm", ".md"):
        if base.endswith(ext):
            base = base[: -len(ext)]
            break
    meta_path = corpus_path / f"{base}.meta.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


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


def _is_handbook(rel_path: str) -> bool:
    """Check if a file belongs to the General Handbook by corpus path."""
    normalized = rel_path.replace("\\", "/")
    return "manuals/general-handbook" in normalized


def _load_conference_metadata(abs_path: Path, rel_path: str) -> ConferenceTalk | None:
    """Load conference talk metadata from HTML or companion .meta.json.

    Precedence:
    1. HTML files → parse_conference_talk (legacy, full extraction)
    2. Any file with a .meta.json sibling → conference_talk_from_meta
    """
    try:
        if abs_path.suffix.lower() in (".html", ".htm"):
            raw_html = abs_path.read_text(encoding="utf-8")
            return parse_conference_talk(raw_html, file_path=rel_path)

        # Look for companion .meta.json (e.g. talk.txt → talk.meta.json)
        meta_path = abs_path.with_suffix(".meta.json")
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            return conference_talk_from_meta(meta, file_path=rel_path)
    except Exception:
        logger.warning("Failed to load conference talk metadata: %s", rel_path, exc_info=True)

    return None


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
