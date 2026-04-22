"""GPU-accelerated full reindex — run from WSL with CUDA.

Runs the Alejandria ingestion pipeline against Postgres IONOS using
GPU for embeddings. The SSH tunnel (localhost:15432) must be up
before invoking this script.

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

# Set environment for WSL → Postgres IONOS via SSH tunnel on the host.
os.environ.setdefault("ALEJANDRIA_CORPUS_PATH", "/mnt/c/own/alejandria/corpus")
os.environ.setdefault("ALEJANDRIA_SQLITE_DB_PATH", "/mnt/c/own/alejandria/data/sqlite/alejandria.db")
os.environ.setdefault("ALEJANDRIA_EMBEDDING_DEVICE", "cuda")
os.environ.setdefault("ALEJANDRIA_STORAGE_BACKEND", "postgres")
os.environ.setdefault("ALEJANDRIA_POSTGRES_HOST", "127.0.0.1")
os.environ.setdefault("ALEJANDRIA_POSTGRES_PORT", "15432")

# Now import after env is set
from alejandria.config import settings
from alejandria.ingestion.pipeline import IngestionPipeline


def main():
    print("=" * 60)
    print("Alejandria GPU Reindex")
    print("=" * 60)
    print(f"  Corpus:     {settings.corpus_path}")
    print(f"  Backend:    {settings.storage_backend}")
    print(f"  Postgres:   {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    print(f"  Device:     {settings.embedding_device}")

    # Verify GPU
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  GPU:        {torch.cuda.get_device_name(0)}")
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
    from alejandria.storage.chunk_writer import make_chunk_writer
    from alejandria.storage.kg_reader import make_kg_reader
    from alejandria.storage.kg_writer import make_kg_writer

    registry = make_document_registry()
    chunk_writer = make_chunk_writer()
    kg_writer = make_kg_writer()
    kg_reader = make_kg_reader()

    kg_extractor = None
    try:
        from alejandria.knowledge.extractor import KGExtractor
        kg_extractor = KGExtractor()
        print("  KG extractor: loaded")
    except Exception as exc:
        print(f"  KG extractor: unavailable ({exc})")

    pipeline = IngestionPipeline(
        registry=registry,
        chunk_writer=chunk_writer,
        kg_writer=kg_writer,
        kg_reader=kg_reader,
        kg_extractor=kg_extractor,
    )

    t0 = time.time()
    stats = pipeline.run(full_reindex=full)
    elapsed = time.time() - t0

    print(f"\n{'=' * 60}")
    print("Reindex Complete")
    print(f"{'=' * 60}")
    print(f"  New files:     {stats.new_files}")
    print(f"  Updated:       {stats.updated_files}")
    print(f"  Deleted:       {stats.deleted_files}")
    print(f"  Errors:        {stats.errors}")
    print(f"  Total chunks:  {stats.total_chunks}")
    print(f"  Elapsed:       {elapsed:.1f}s ({elapsed/60:.1f}m)")


if __name__ == "__main__":
    main()
