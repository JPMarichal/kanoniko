"""GPU-accelerated full reindex — run from WSL with CUDA.

Runs the full Alejandria ingestion pipeline using GPU for embeddings,
connecting to Neo4j on localhost (Docker container). Vectors stored in SQLite via sqlite-vec.

Usage (from WSL):
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate alejandria
    cd /mnt/c/own/alejandria
    python scripts/gpu_reindex.py
"""

from __future__ import annotations

import os
import sys
import time

# Set environment for WSL → Docker services
os.environ.setdefault("ALEJANDRIA_CORPUS_PATH", "/mnt/c/own/alejandria/corpus")
os.environ.setdefault("ALEJANDRIA_SQLITE_DB_PATH", "/mnt/c/own/alejandria/data/sqlite/alejandria.db")
os.environ.setdefault("ALEJANDRIA_EMBEDDING_DEVICE", "cuda")
os.environ.setdefault("ALEJANDRIA_NEO4J_URI", "bolt://localhost:7687")
os.environ.setdefault("ALEJANDRIA_NEO4J_USER", "neo4j")
os.environ.setdefault("ALEJANDRIA_NEO4J_PASSWORD", "alejandria")

# Now import after env is set
from alejandria.config import settings
from alejandria.ingestion.pipeline import IngestionPipeline

def main():
    print("=" * 60)
    print("Alejandria GPU Reindex")
    print("=" * 60)
    print(f"  Corpus:    {settings.corpus_path}")
    print(f"  SQLite:    {settings.sqlite_db_path}")
    print(f"  Neo4j:     {settings.neo4j_uri}")
    print(f"  Device:    {settings.embedding_device}")

    # Verify GPU
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  GPU:       {torch.cuda.get_device_name(0)}")
        else:
            print("  WARNING: CUDA not available, falling back to CPU")
    except ImportError:
        print("  WARNING: PyTorch not installed")

    print("=" * 60)

    full = "--full" in sys.argv or "-f" in sys.argv
    print(f"\n  Mode: {'FULL reindex' if full else 'incremental'}")
    print()

    # Wire up dependencies (same as API's get_pipeline)
    from alejandria.ingestion.registry import make_document_registry
    from alejandria.search.textual import make_textual_search

    from pathlib import Path
    db_path = Path(settings.sqlite_db_path)
    registry = make_document_registry(db_path)
    textual = make_textual_search(db_path)

    semantic = None
    try:
        from alejandria.search.semantic import SemanticSearch
        semantic = SemanticSearch(db_path)
        print("  Semantic: sqlite-vec loaded")
    except Exception as e:
        print(f"  Semantic: unavailable ({e})")

    neo4j_client = None
    kg_extractor = None
    try:
        from alejandria.knowledge.neo4j_client import Neo4jClient
        from alejandria.knowledge.extractor import KGExtractor
        neo4j_client = Neo4jClient()
        kg_extractor = KGExtractor()
        print("  KG: connected to Neo4j")
    except Exception as e:
        print(f"  KG: unavailable ({e})")

    pipeline = IngestionPipeline(
        registry=registry,
        textual_search=textual,
        semantic_search=semantic,
        neo4j_client=neo4j_client,
        kg_extractor=kg_extractor,
    )

    t0 = time.time()
    stats = pipeline.run(full_reindex=full)
    elapsed = time.time() - t0

    print(f"\n{'=' * 60}")
    print("Reindex Complete")
    print(f"{'=' * 60}")
    print(f"  New files:     {stats.new_files}")
    print(f"  Updated files: {stats.updated_files}")
    print(f"  Deleted files: {stats.deleted_files}")
    print(f"  Total chunks:  {stats.total_chunks}")
    print(f"  Errors:        {stats.errors}")
    print(f"  Time:          {elapsed:.1f}s ({elapsed/60:.1f}m)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
