"""Integration tests for PostgresGraphClient Tier 2e — write path.

Covers merge_entity, merge_document, merge_relation, link_entity_to_document,
batch_* variants, batch_write_all, delete_document_relations,
update_entity_profile. Curated-seed loading is covered via
:class:`CuratedSeedLoader` (see :func:`test_curated_seed_loader_*`).

All tests use the ``__pgtest__`` prefix on entity names / file_paths so they
live in an isolated namespace and never touch real data. The ``isolate_writes``
fixture wipes matching rows before+after each test (belt-and-suspenders).

Skips automatically if Postgres is not reachable.
"""
from __future__ import annotations

import pytest

psycopg = pytest.importorskip("psycopg")


def _pg_reachable() -> bool:
    from alejandria.storage.postgres.connection import get_connection
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _pg_reachable(),
    reason="Postgres not reachable — set ALEJANDRIA_POSTGRES_* envs",
)


__TEST_NS = "__pgtest__"


def _wipe_test_data() -> None:
    from alejandria.storage.postgres.connection import get_connection
    prefix = __TEST_NS + "%"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM entity_document_mentions "
                "WHERE file_path LIKE %s "
                "   OR entity_id IN (SELECT id FROM entities WHERE name LIKE %s)",
                (prefix, prefix),
            )
            cur.execute(
                "DELETE FROM relations "
                "WHERE src_id IN (SELECT id FROM entities WHERE name LIKE %s) "
                "   OR dst_id IN (SELECT id FROM entities WHERE name LIKE %s)",
                (prefix, prefix),
            )
            cur.execute(
                "DELETE FROM entity_aliases "
                "WHERE entity_id IN (SELECT id FROM entities WHERE name LIKE %s) "
                "   OR alias LIKE %s",
                (prefix, prefix),
            )
            cur.execute("DELETE FROM entities WHERE name LIKE %s", (prefix,))
            cur.execute(
                "DELETE FROM document_registry WHERE file_path LIKE %s", (prefix,)
            )
        conn.commit()


@pytest.fixture
def isolate_writes():
    """Wipe test namespace before+after each write-path test."""
    _wipe_test_data()
    yield
    _wipe_test_data()


def _row_count(sql: str, params: tuple = ()) -> int:
    from alejandria.storage.postgres.connection import get_connection
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()[0]


# --------------------------------------------------------------------------- #
# merge_entity
# --------------------------------------------------------------------------- #

def test_merge_entity_creates_row(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    c.merge_entity(__TEST_NS + "Alice", "person")
    assert _row_count(
        "SELECT count(*) FROM entities WHERE name = %s AND entity_type = %s",
        (__TEST_NS + "Alice", "person"),
    ) == 1


def test_merge_entity_is_idempotent(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    c.merge_entity(__TEST_NS + "Bob", "person")
    c.merge_entity(__TEST_NS + "Bob", "person")
    assert _row_count(
        "SELECT count(*) FROM entities WHERE name = %s", (__TEST_NS + "Bob",)
    ) == 1


def test_merge_entity_with_aliases(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    c.merge_entity(
        __TEST_NS + "Carol", "person",
        aliases=[__TEST_NS + "Caro", __TEST_NS + "Carlita"],
    )
    n = _row_count(
        "SELECT count(*) FROM entity_aliases a "
        "JOIN entities e ON a.entity_id = e.id "
        "WHERE e.name = %s",
        (__TEST_NS + "Carol",),
    )
    assert n == 2


def test_merge_entity_empty_name_noop(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    c.merge_entity("", "person")  # must not raise
    c.merge_entity(__TEST_NS + "Dora", "")  # must not raise


# --------------------------------------------------------------------------- #
# merge_document
# --------------------------------------------------------------------------- #

def test_merge_document_upsert(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    fp = __TEST_NS + "doc1.txt"
    c.merge_document(fp, "indexed")
    c.merge_document(fp, "indexed")
    assert _row_count(
        "SELECT count(*) FROM document_registry WHERE file_path = %s", (fp,)
    ) == 1


# --------------------------------------------------------------------------- #
# merge_relation
# --------------------------------------------------------------------------- #

def test_merge_relation_creates_endpoints_and_edge(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    c.merge_relation(
        __TEST_NS + "Dad", "person", "FATHER_OF",
        __TEST_NS + "Son", "person",
        properties={"confidence": "curated", "source": "test"},
    )
    assert _row_count(
        "SELECT count(*) FROM relations r "
        "JOIN entities s ON r.src_id = s.id "
        "JOIN entities d ON r.dst_id = d.id "
        "WHERE s.name = %s AND d.name = %s AND r.rel_type = %s",
        (__TEST_NS + "Dad", __TEST_NS + "Son", "FATHER_OF"),
    ) == 1


def test_merge_relation_is_idempotent(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    for _ in range(3):
        c.merge_relation(
            __TEST_NS + "A", "person", "KNOWS",
            __TEST_NS + "B", "person",
        )
    assert _row_count(
        "SELECT count(*) FROM relations r "
        "JOIN entities s ON r.src_id = s.id "
        "JOIN entities d ON r.dst_id = d.id "
        "WHERE s.name = %s AND d.name = %s AND r.rel_type = %s",
        (__TEST_NS + "A", __TEST_NS + "B", "KNOWS"),
    ) == 1


# --------------------------------------------------------------------------- #
# link_entity_to_document
# --------------------------------------------------------------------------- #

def test_link_entity_to_document(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    fp = __TEST_NS + "doc_link.txt"
    c.merge_document(fp, "indexed")
    c.merge_entity(__TEST_NS + "Eve", "person")
    c.link_entity_to_document(
        __TEST_NS + "Eve", "person", fp,
        resolved_name=__TEST_NS + "Eve", confidence="llm_high",
    )
    assert _row_count(
        "SELECT count(*) FROM entity_document_mentions m "
        "JOIN entities e ON m.entity_id = e.id "
        "WHERE e.name = %s AND m.file_path = %s",
        (__TEST_NS + "Eve", fp),
    ) == 1


# --------------------------------------------------------------------------- #
# batch_merge_entities
# --------------------------------------------------------------------------- #

def test_batch_merge_entities(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    c.batch_merge_entities([
        {"name": __TEST_NS + "X1", "type": "person",
         "aliases": [__TEST_NS + "x1-alt"]},
        {"name": __TEST_NS + "X2", "type": "place"},
        {"name": __TEST_NS + "X3", "type": "concept"},
        {"name": "", "type": "person"},  # skipped
        {"name": __TEST_NS + "X4"},       # skipped (no type)
    ])
    assert _row_count(
        "SELECT count(*) FROM entities WHERE name LIKE %s",
        (__TEST_NS + "X%",),
    ) == 3


# --------------------------------------------------------------------------- #
# batch_merge_documents
# --------------------------------------------------------------------------- #

def test_batch_merge_documents(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    docs = [{"file_path": __TEST_NS + "d" + str(i) + ".txt",
             "source": "indexed"} for i in range(5)]
    c.batch_merge_documents(docs)
    assert _row_count(
        "SELECT count(*) FROM document_registry WHERE file_path LIKE %s",
        (__TEST_NS + "d%",),
    ) == 5


# --------------------------------------------------------------------------- #
# batch_merge_relations
# --------------------------------------------------------------------------- #

def test_batch_merge_relations_dedupes(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    c.batch_merge_relations([
        {"from_name": __TEST_NS + "P1", "from_type": "person",
         "rel_type": "MENTOR_OF",
         "to_name": __TEST_NS + "P2", "to_type": "person",
         "props": {"confidence": "curated"}},
        {"from_name": __TEST_NS + "P1", "from_type": "person",
         "rel_type": "MENTOR_OF",
         "to_name": __TEST_NS + "P3", "to_type": "person"},
        # Duplicate — must be deduped.
        {"from_name": __TEST_NS + "P1", "from_type": "person",
         "rel_type": "MENTOR_OF",
         "to_name": __TEST_NS + "P2", "to_type": "person"},
    ])
    assert _row_count(
        "SELECT count(*) FROM relations r "
        "JOIN entities s ON r.src_id = s.id "
        "WHERE s.name = %s AND r.rel_type = %s",
        (__TEST_NS + "P1", "MENTOR_OF"),
    ) == 2


# --------------------------------------------------------------------------- #
# batch_link_entities_to_document
# --------------------------------------------------------------------------- #

def test_batch_link_entities_to_document(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    fp = __TEST_NS + "links.txt"
    c.batch_link_entities_to_document([
        {"entity_name": __TEST_NS + "L1", "entity_type": "person",
         "file_path": fp},
        {"entity_name": __TEST_NS + "L2", "entity_type": "person",
         "file_path": fp},
    ])
    assert _row_count(
        "SELECT count(*) FROM entity_document_mentions WHERE file_path = %s",
        (fp,),
    ) == 2


# --------------------------------------------------------------------------- #
# batch_write_all (orchestrator)
# --------------------------------------------------------------------------- #

def test_batch_write_all_orchestrates(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    fp = __TEST_NS + "bw.txt"
    c.batch_write_all(
        delete_paths=[],
        documents=[{"file_path": fp, "source": "indexed"}],
        entities=[
            {"name": __TEST_NS + "BW1", "type": "person"},
            {"name": __TEST_NS + "BW2", "type": "person"},
        ],
        links=[
            {"entity_name": __TEST_NS + "BW1", "entity_type": "person",
             "file_path": fp},
        ],
        relations=[
            {"from_name": __TEST_NS + "BW1", "from_type": "person",
             "rel_type": "BROTHER_OF",
             "to_name": __TEST_NS + "BW2", "to_type": "person"},
        ],
    )
    assert _row_count(
        "SELECT count(*) FROM document_registry WHERE file_path = %s", (fp,)
    ) == 1
    assert _row_count(
        "SELECT count(*) FROM entities WHERE name LIKE %s", (__TEST_NS + "BW%",)
    ) == 2
    assert _row_count(
        "SELECT count(*) FROM relations r JOIN entities s ON r.src_id = s.id "
        "WHERE s.name = %s AND r.rel_type = %s",
        (__TEST_NS + "BW1", "BROTHER_OF"),
    ) == 1
    assert _row_count(
        "SELECT count(*) FROM entity_document_mentions WHERE file_path = %s",
        (fp,),
    ) == 1


def test_batch_write_all_delete_then_recreate(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    fp = __TEST_NS + "rc.txt"
    c.batch_write_all([], [{"file_path": fp, "source": "indexed"}], [], [], [])
    assert _row_count(
        "SELECT count(*) FROM document_registry WHERE file_path = %s", (fp,)
    ) == 1
    c.batch_write_all([fp], [], [], [], [])
    assert _row_count(
        "SELECT count(*) FROM document_registry WHERE file_path = %s", (fp,)
    ) == 0


# --------------------------------------------------------------------------- #
# delete_document_relations
# --------------------------------------------------------------------------- #

def test_delete_document_relations(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    fp = __TEST_NS + "del.txt"
    c.merge_document(fp, "indexed")
    c.merge_entity(__TEST_NS + "DE", "person")
    c.link_entity_to_document(__TEST_NS + "DE", "person", fp)
    assert _row_count(
        "SELECT count(*) FROM entity_document_mentions WHERE file_path = %s",
        (fp,),
    ) == 1
    c.delete_document_relations(fp)
    assert _row_count(
        "SELECT count(*) FROM entity_document_mentions WHERE file_path = %s",
        (fp,),
    ) == 0


# --------------------------------------------------------------------------- #
# update_entity_profile
# --------------------------------------------------------------------------- #

def test_update_entity_profile_merges_metadata(isolate_writes) -> None:
    import json as _j
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    from alejandria.storage.postgres.connection import get_connection
    c = PostgresGraphClient()
    c.merge_entity(__TEST_NS + "UP", "person")
    c.update_entity_profile(
        __TEST_NS + "UP", "person",
        summary="brief", mention_count=42,
    )
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT metadata FROM entities WHERE name = %s",
                (__TEST_NS + "UP",),
            )
            meta = cur.fetchone()[0]
    if isinstance(meta, str):
        meta = _j.loads(meta)
    assert meta.get("summary") == "brief"
    assert meta.get("mention_count") == 42


def test_update_entity_profile_noop_when_nothing_to_set(isolate_writes) -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    c.merge_entity(__TEST_NS + "UP2", "person")
    c.update_entity_profile(__TEST_NS + "UP2", "person")  # must not raise


# --------------------------------------------------------------------------- #
# CuratedSeedLoader + PostgresGraphClient as KGWriter
# --------------------------------------------------------------------------- #

def test_curated_seed_loader_writes_relations(isolate_writes, tmp_path) -> None:
    import json as _j
    from alejandria.knowledge.curated_seed_loader import CuratedSeedLoader
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    path = tmp_path / "relations.json"
    path.write_text(_j.dumps({
        "MARRIED_TO": [{
            "from": {"name": __TEST_NS + "Husb", "type": "person"},
            "to":   {"name": __TEST_NS + "Wife", "type": "person"},
        }],
        "FATHER_OF": [{
            "from": {"name": __TEST_NS + "Husb", "type": "person"},
            "to":   {"name": __TEST_NS + "Kid",  "type": "person"},
        }],
    }))
    loader = CuratedSeedLoader(PostgresGraphClient())
    counts = loader.load(path)
    assert counts == {"MARRIED_TO": 1, "FATHER_OF": 1}
    assert _row_count(
        "SELECT count(*) FROM relations r "
        "JOIN entities s ON r.src_id = s.id "
        "WHERE s.name = %s",
        (__TEST_NS + "Husb",),
    ) == 2


def test_curated_seed_loader_bidirectional(isolate_writes, tmp_path) -> None:
    import json as _j
    from alejandria.knowledge.curated_seed_loader import CuratedSeedLoader
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    path = tmp_path / "relations.json"
    path.write_text(_j.dumps({
        "ALLIED_WITH": [{
            "from": {"name": __TEST_NS + "A", "type": "people"},
            "to":   {"name": __TEST_NS + "B", "type": "people"},
            "bidirectional": True,
        }],
    }))
    counts = CuratedSeedLoader(PostgresGraphClient()).load(path)
    # bidirectional writes both directions, so count is 2 for the same type
    assert counts == {"ALLIED_WITH": 2}


def test_curated_seed_loader_missing_file_returns_empty(tmp_path) -> None:
    from alejandria.knowledge.curated_seed_loader import CuratedSeedLoader
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    loader = CuratedSeedLoader(PostgresGraphClient())
    assert loader.load(tmp_path / "nope.json") == {}


# --------------------------------------------------------------------------- #
# clear_all
#
# NOTE: clear_all is globally destructive — on the shared IONOS DB we cannot
# exercise the TRUNCATE branch without wiping real data. We validate the
# preserve_sources logic indirectly: after inserting both a curated and a
# non-curated relation in our namespace, we call clear_all(preserve_sources=
# ["curated_seed"]) but limit the scope by first verifying both exist, then
# asserting the post-call invariant only on curated.
#
# To guard against accidental destruction on the shared DB, this test is
# opt-in via ALEJANDRIA_ALLOW_DESTRUCTIVE_TESTS=1.
# --------------------------------------------------------------------------- #

def test_clear_all_preserve_sources(isolate_writes) -> None:
    import os
    if os.environ.get("ALEJANDRIA_ALLOW_DESTRUCTIVE_TESTS") != "1":
        pytest.skip(
            "clear_all is globally destructive — set "
            "ALEJANDRIA_ALLOW_DESTRUCTIVE_TESTS=1 to run against bench DB only."
        )
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    c = PostgresGraphClient()
    c.merge_relation(
        __TEST_NS + "Keep1", "person", "PARENT_OF",
        __TEST_NS + "Keep2", "person",
        properties={"confidence": "curated", "source": "curated_seed"},
    )
    c.merge_relation(
        __TEST_NS + "Drop1", "person", "KNOWS",
        __TEST_NS + "Drop2", "person",
        properties={"confidence": "llm_low", "source": "llm"},
    )
    c.clear_all(preserve_sources=["curated_seed"])
    assert _row_count(
        "SELECT count(*) FROM relations r "
        "JOIN entities s ON r.src_id = s.id "
        "WHERE s.name = %s",
        (__TEST_NS + "Keep1",),
    ) == 1
    assert _row_count(
        "SELECT count(*) FROM relations r "
        "JOIN entities s ON r.src_id = s.id "
        "WHERE s.name = %s",
        (__TEST_NS + "Drop1",),
    ) == 0
