"""Smoke test for the Postgres write-path (ChunkWriter + KGWriter + KGReader).

Exercises each Protocol against Postgres IONOS using a namespaced synthetic
file path (`__pgwsmoke__/...`) so it never touches real corpus rows.

Usage (inside the container, with the SSH tunnel up on the host):

    ALEJANDRIA_STORAGE_BACKEND=postgres \\
    ALEJANDRIA_POSTGRES_HOST=127.0.0.1 \\
    ALEJANDRIA_POSTGRES_PORT=15432 \\
    python -m scripts.postgres_writepath_smoke

Exits non-zero on any failure. Self-cleans its test rows on exit.
"""
from __future__ import annotations

import sys
import traceback

from alejandria.config import settings


_NS = "__pgwsmoke__/"


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _clean(conn) -> None:
    """Remove any rows in the test namespace before+after."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM chunks WHERE file_path LIKE %s", (_NS + "%",))
        cur.execute(
            "DELETE FROM document_registry WHERE file_path LIKE %s",
            (_NS + "%",),
        )
        cur.execute(
            "DELETE FROM entities WHERE name LIKE %s",
            (_NS + "%",),
        )
    conn.commit()


def test_chunk_writer() -> None:
    from alejandria.storage.chunk_writer import ChunkRecord, make_chunk_writer
    from alejandria.storage.postgres_chunk_writer import PostgresChunkWriter

    cw = make_chunk_writer()
    _assert(isinstance(cw, PostgresChunkWriter), f"expected Postgres writer, got {type(cw).__name__}")

    file_path = _NS + "sample.txt"
    records = [
        ChunkRecord(
            file_path=file_path,
            chunk_index=i,
            text=f"Hello world chunk {i}",
            language="en",
            reference=f"Smoke {i}",
            start_char=0,
            end_char=20,
            metadata={"source": "smoke", "lang": "en"},
        )
        for i in range(3)
    ]

    ids = cw.insert_chunks(records)
    _assert(len(ids) == 3, f"expected 3 ids, got {ids}")
    _assert(all(isinstance(i, int) and i > 0 for i in ids), f"bad ids: {ids}")
    print(f"  insert_chunks OK — ids={ids}")

    # embeddings
    dim = settings.embedding_dim
    vectors = [[0.1] * dim, [0.2] * dim, [0.3] * dim]
    payloads = [{"text": r.text, "file_path": file_path, "chunk_index": r.chunk_index} for r in records]
    cw.upsert_embeddings(ids=ids, vectors=vectors, payloads=payloads)
    print("  upsert_embeddings OK")

    # reads
    all_chunks = [c for c in cw.iter_all_chunks() if c["file_path"].startswith(_NS)]
    _assert(len(all_chunks) == 3, f"iter_all_chunks found {len(all_chunks)} in namespace (expected 3)")
    print(f"  iter_all_chunks OK — {len(all_chunks)} chunks in namespace")

    hits = cw.find_chunks_with_patterns(file_paths=[file_path], text_patterns=["chunk 1"])
    _assert(len(hits) == 1, f"find_chunks_with_patterns: expected 1 hit, got {len(hits)}")
    _assert(hits[0]["chunk_index"] == 1, f"wrong chunk: {hits}")
    print("  find_chunks_with_patterns OK")

    # delete
    cw.delete_by_file(file_path)
    remaining = [c for c in cw.iter_all_chunks() if c["file_path"] == file_path]
    _assert(len(remaining) == 0, f"delete_by_file left {len(remaining)} rows")
    print("  delete_by_file OK")


def test_kg_writer_and_reader() -> None:
    from alejandria.storage.kg_reader import make_kg_reader
    from alejandria.storage.kg_writer import make_kg_writer
    from alejandria.storage.postgres_kg_reader import PostgresKGReader
    from alejandria.storage.postgres_kg_writer import PostgresKGWriter

    kw = make_kg_writer()
    _assert(isinstance(kw, PostgresKGWriter), f"expected Postgres kw, got {type(kw).__name__}")

    kr = make_kg_reader()
    _assert(isinstance(kr, PostgresKGReader), f"expected Postgres kr, got {type(kr).__name__}")

    # minimal write path exercise
    kw.merge_entity(name=_NS + "Abraham", entity_type="person", aliases=[])
    kw.merge_entity(name=_NS + "Isaac", entity_type="person", aliases=[])
    kw.merge_relation(
        from_name=_NS + "Abraham", from_type="person",
        rel_type="FATHER_OF",
        to_name=_NS + "Isaac", to_type="person",
        properties={"confidence": "curated", "source": "smoke"},
    )
    print("  merge_entity + merge_relation OK")

    kw.batch_merge_documents([{"file_path": _NS + "doc1.txt", "source": "smoke"}])
    kw.batch_link_entities_to_document([
        {"entity_name": _NS + "Abraham", "entity_type": "person", "file_path": _NS + "doc1.txt"},
    ])
    print("  batch_merge_documents + batch_link_entities_to_document OK")

    # read path narrow surface
    mentions = kr.get_all_entity_mentions()
    ns_mentions = [m for m in mentions if m.get("name", "").startswith(_NS)]
    _assert(len(ns_mentions) >= 1, f"get_all_entity_mentions missed namespace rows (total {len(mentions)})")
    print(f"  get_all_entity_mentions OK — {len(ns_mentions)} in namespace")

    dc = kr.get_disambiguated_counts()
    print(f"  get_disambiguated_counts OK — {len(dc)} keys returned")


def main() -> int:
    backend = (settings.storage_backend or "").lower()
    if backend != "postgres":
        print(f"ERROR: ALEJANDRIA_STORAGE_BACKEND must be 'postgres', got {backend!r}", file=sys.stderr)
        return 2

    from alejandria.storage.postgres.connection import get_connection

    try:
        print("== cleanup before ==")
        with get_connection() as conn:
            _clean(conn)

        print("== ChunkWriter ==")
        test_chunk_writer()

        print("== KGWriter + KGReader ==")
        test_kg_writer_and_reader()

        print("\nSMOKE OK")
        return 0
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        try:
            with get_connection() as conn:
                _clean(conn)
            print("== cleanup after OK ==")
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    sys.exit(main())
