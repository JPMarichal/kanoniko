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


class IngestionPipeline:
    """Orchestrates incremental ingestion from corpus to search indices."""

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

        # Clear existing KG data
        logger.info("KG rebuild: clearing existing graph...")
        self._neo4j.clear_all()

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

        for i, row in enumerate(rows):
            file_path = row[0] if isinstance(row, (list, tuple)) else row["file_path"]
            text = row[2] if isinstance(row, (list, tuple)) else row["text"]

            # Ensure document node exists
            if file_path not in documents_seen:
                source = _extract_source(file_path)
                self._neo4j.merge_document(file_path, source)
                documents_seen.add(file_path)

            # Extract entities and relations
            extraction = self._kg_extractor.extract(text, source_file=file_path)

            for entity in extraction.entities:
                self._neo4j.merge_entity(entity.name, entity.type)
                self._neo4j.link_entity_to_document(entity.name, entity.type, file_path)
                entities_found += 1

            for rel in extraction.relations:
                self._neo4j.merge_relation(
                    from_name=rel.from_entity,
                    from_type=rel.from_type,
                    rel_type=rel.relation,
                    to_name=rel.to_entity,
                    to_type=rel.to_type,
                )
                relations_found += 1

            if (i + 1) % 500 == 0:
                logger.info(
                    "KG rebuild: %d/%d chunks (%.0f%%), %d entities, %d relations so far...",
                    i + 1, total_chunks, (i + 1) / total_chunks * 100,
                    entities_found, relations_found,
                )

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
            for term, (canonical, _) in self._kg_extractor._lookup.items():
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

                # Build key passages: pick top N by relevance (first mention per document)
                seen_docs: set[str] = set()
                key_passages: list[dict] = []
                for row in rows:
                    fp = row[0] if isinstance(row, (list, tuple)) else row["file_path"]
                    if fp in seen_docs:
                        continue
                    seen_docs.add(fp)

                    text = row[2] if isinstance(row, (list, tuple)) else row["text"]
                    ref = row[3] if isinstance(row, (list, tuple)) else row["reference"]

                    # Extract snippet — try each name variant, use first match
                    snippet = None
                    for sn in unique_names:
                        if sn.lower() in text.lower():
                            snippet = _extract_snippet(text, sn, max_len=200)
                            break
                    if snippet is None:
                        snippet = text[:200] + ("..." if len(text) > 200 else "")

                    passage = {"reference": ref or fp, "snippet": snippet}
                    key_passages.append(passage)
                    if len(key_passages) >= max_passages:
                        break

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

        elapsed = time.time() - start
        stats = {
            "entities_processed": len(profiles),
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


def _extract_lang(rel_path: str) -> str | None:
    """Extract language code from the corpus path, or None if not detected."""
    parts = rel_path.replace("\\", "/").split("/")
    if parts and parts[0] in ("en", "es"):
        return parts[0]
    return None


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
