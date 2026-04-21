"""End-to-end smoke: run :class:`IngestionPipeline` against Postgres IONOS.

Creates a small synthetic document inside the corpus under a namespaced
directory (``__pgwsmoke__/``), runs the full pipeline via
``ingest_paths``, and verifies rows landed in:

* ``document_registry``
* ``chunks`` (+ FTS via the generated tsvector)
* ``chunk_embeddings`` (if the encoder is available)

Then deletes the file and cleans the namespaced rows. Self-contained.

Usage (one-off container with ``--network host`` and the SSH tunnel up)::

    docker run --rm --network host \\
      -v ...:/app/corpus -v ...:/app/src \\
      -e ALEJANDRIA_STORAGE_BACKEND=postgres \\
      -e ALEJANDRIA_CORPUS_PATH=/app/corpus \\
      ... docker-api python /app/scripts/postgres_pipeline_e2e_smoke.py
"""
from __future__ import annotations

import shutil
import sys
import traceback
from pathlib import Path
from unittest.mock import patch

from alejandria.config import settings


_NS = "__pgwsmoke__"


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _clean_db() -> None:
    from alejandria.storage.postgres.connection import get_connection

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "DELETE FROM chunks WHERE file_path LIKE %s", (f"%{_NS}%",)
        )
        cur.execute(
            "DELETE FROM document_registry WHERE file_path LIKE %s",
            (f"%{_NS}%",),
        )
        conn.commit()


def _clean_fs(corpus_path: Path) -> None:
    for lang in ("en", "es"):
        target = corpus_path / lang / _NS
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)


def _seed_doc(corpus_path: Path) -> str:
    """Create a synthetic doc, return its corpus-relative path."""
    target_dir = corpus_path / "en" / _NS
    target_dir.mkdir(parents=True, exist_ok=True)
    doc = target_dir / "doc1.txt"
    doc.write_text(
        "This is a synthetic test document for the Postgres write-path smoke. "
        "It mentions Abraham and Isaac so the KG extractor has something to chew on. "
        "Abraham was a prophet; Isaac was his son. "
        "Multiple sentences ensure we generate at least one full chunk.",
        encoding="utf-8",
    )
    return f"en/{_NS}"


def _run_pipeline(rel_dir: str) -> None:
    from alejandria.ingestion.pipeline import IngestionPipeline
    from alejandria.ingestion.registry import make_document_registry
    from alejandria.storage.chunk_writer import make_chunk_writer

    # KG is optional — skip_kg=True keeps the smoke test lean and
    # independent of the spaCy model download in the container.
    pipeline = IngestionPipeline(
        registry=make_document_registry(),
        chunk_writer=make_chunk_writer(),
    )
    stats = pipeline.ingest_paths([rel_dir], skip_kg=True)
    print(
        f"  ingest_paths: new={stats.new_files} updated={stats.updated_files} "
        f"chunks={stats.total_chunks} errors={stats.errors}"
    )
    _assert(stats.errors == 0, f"errors: {stats.errors}")
    _assert(stats.new_files + stats.updated_files >= 1, "no files processed")
    _assert(stats.total_chunks >= 1, "no chunks produced")


def _verify_postgres() -> None:
    from alejandria.storage.postgres.connection import get_connection

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM document_registry WHERE file_path LIKE %s",
            (f"%{_NS}%",),
        )
        doc_count = int(cur.fetchone()[0])
        cur.execute(
            "SELECT COUNT(*) FROM chunks WHERE file_path LIKE %s",
            (f"%{_NS}%",),
        )
        chunk_count = int(cur.fetchone()[0])
        cur.execute(
            """
            SELECT COUNT(*)
            FROM chunk_embeddings ce
            JOIN chunks c ON c.id = ce.chunk_id
            WHERE c.file_path LIKE %s
            """,
            (f"%{_NS}%",),
        )
        emb_count = int(cur.fetchone()[0])
        # FTS check: tsv is a generated column, so just confirm it's non-null
        # on the inserted rows.
        cur.execute(
            "SELECT COUNT(*) FROM chunks WHERE file_path LIKE %s AND tsv IS NOT NULL",
            (f"%{_NS}%",),
        )
        tsv_count = int(cur.fetchone()[0])

    print(
        f"  postgres: docs={doc_count} chunks={chunk_count} "
        f"embeddings={emb_count} tsv_populated={tsv_count}"
    )
    _assert(doc_count >= 1, "no document_registry row")
    _assert(chunk_count >= 1, "no chunks")
    _assert(tsv_count == chunk_count, "tsvector not populated for every chunk")
    # embeddings may be 0 if the encoder isn't available; log and continue
    if emb_count == 0:
        print("  (note: no embeddings — encoder unavailable in this context)")
    else:
        _assert(emb_count == chunk_count, f"embedding count {emb_count} != chunk count {chunk_count}")


def main() -> int:
    backend = (settings.storage_backend or "").lower()
    if backend != "postgres":
        print(
            f"ERROR: ALEJANDRIA_STORAGE_BACKEND must be 'postgres', got {backend!r}",
            file=sys.stderr,
        )
        return 2

    corpus_path = Path(settings.corpus_path)
    if not corpus_path.is_dir():
        print(f"ERROR: corpus_path {corpus_path} is not a directory", file=sys.stderr)
        return 2

    try:
        print("== cleanup before ==")
        _clean_db()
        _clean_fs(corpus_path)

        print("== seed synthetic doc ==")
        rel_dir = _seed_doc(corpus_path)
        print(f"  rel_dir={rel_dir}")

        print("== run pipeline.ingest_paths ==")
        _run_pipeline(rel_dir)

        print("== verify Postgres rows ==")
        _verify_postgres()

        print("\nE2E SMOKE OK")
        return 0
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        try:
            _clean_db()
            _clean_fs(corpus_path)
            print("== cleanup after OK ==")
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    sys.exit(main())
