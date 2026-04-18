"""Integration tests for PostgresGraphClient (Fase 3 Tier 2a).

Validan los métodos ya implementados en el scaffold — graph_summary y
find_node. El resto raise NotImplementedError y no se testea aquí hasta
que se implementen (tiers 2b/2c/2d).

Corre contra el Postgres con datos reales (IONOS via SSH tunnel o bench).
Skip automático si no hay conexión.
"""
from __future__ import annotations

import pytest

psycopg = pytest.importorskip("psycopg")


def _pg_reachable_with_data() -> bool:
    from alejandria.storage.postgres.connection import get_connection
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM entities")
                n = cur.fetchone()[0]
        return n > 100
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _pg_reachable_with_data(),
    reason="Postgres not reachable or entities empty",
)


# --------------------------------------------------------------------------- #
# graph_summary
# --------------------------------------------------------------------------- #

def test_graph_summary_shape() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    summary = client.graph_summary()

    for key in ("total_entities", "total_relations", "entity_types", "top_rel_types"):
        assert key in summary, f"missing field {key}"

    assert isinstance(summary["total_entities"], int)
    assert isinstance(summary["total_relations"], int)
    assert isinstance(summary["entity_types"], dict)
    assert isinstance(summary["top_rel_types"], list)


def test_graph_summary_reasonable_numbers() -> None:
    """Sanity check: numbers should be in expected range post-R0+R7."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    summary = client.graph_summary()

    # Post-cleanup IONOS: ~811k entities, ~21M relations.
    assert 500_000 < summary["total_entities"] < 2_000_000
    assert 10_000_000 < summary["total_relations"] < 50_000_000


def test_graph_summary_top_rel_types_structure() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    summary = client.graph_summary()

    assert len(summary["top_rel_types"]) > 0
    for item in summary["top_rel_types"]:
        assert "type" in item and "count" in item
        assert isinstance(item["type"], str)
        assert isinstance(item["count"], int)

    # Top types descending
    counts = [item["count"] for item in summary["top_rel_types"]]
    assert counts == sorted(counts, reverse=True)


# --------------------------------------------------------------------------- #
# find_node
# --------------------------------------------------------------------------- #

def test_find_node_exact_canonical_match() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    results = client.find_node("Nephi", entity_type="person", limit=5)

    assert len(results) > 0
    names = {r["name"] for r in results}
    assert "Nephi" in names


def test_find_node_alias_resolution() -> None:
    """Spanish alias should find English canonical via entity_aliases JOIN."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    results = client.find_node("Nefi", entity_type="person", limit=10)

    if not results:
        pytest.skip("No 'Nefi' alias found — gazetteer didn't populate aliases table")
    names = {r["name"] for r in results}
    assert "Nephi" in names, f"'Nefi' alias should map to Nephi; got {names}"


def test_find_node_without_type_filter() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    results = client.find_node("Moroni", limit=10)

    assert len(results) > 0


def test_find_node_empty_query() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    assert client.find_node("") == []
    assert client.find_node("   ") == []


def test_find_node_nonexistent_returns_empty() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    results = client.find_node("xyzqzqzqNotExisting", limit=5)
    assert results == []


def test_find_node_score_ordering() -> None:
    """Results should be sorted by score desc."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    results = client.find_node("Nephi", limit=20)
    if len(results) < 2:
        pytest.skip("not enough results to check ordering")
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True), \
        f"results not sorted by score desc: {scores}"


def test_find_node_result_shape() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    results = client.find_node("Nephi", limit=1)
    assert len(results) == 1
    r = results[0]
    for field in ("id", "name", "type", "disambiguator", "score"):
        assert field in r, f"missing field {field}"
    assert isinstance(r["id"], int)
    assert isinstance(r["score"], float)


# --------------------------------------------------------------------------- #
# Factory
# --------------------------------------------------------------------------- #

def test_factory_returns_postgres_when_flag_set(monkeypatch) -> None:
    from alejandria.config import settings
    from alejandria.knowledge.postgres_graph_client import (
        PostgresGraphClient,
        make_graph_client,
    )

    monkeypatch.setattr(settings, "storage_backend", "postgres")
    client = make_graph_client()
    assert isinstance(client, PostgresGraphClient)


# --------------------------------------------------------------------------- #
# NotImplementedError surface — guard against silent portings
# --------------------------------------------------------------------------- #

def test_not_implemented_methods_raise_clearly() -> None:
    """Methods in tiers 2b/2c/2d/Fase4 should raise NotImplementedError
    with a message pointing at the audit doc. Fails loudly, not silently."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()

    for method_name, args, kwargs in [
        ("get_neighbors", ("x",), {}),
        ("get_documents_for_entity", ("x",), {}),
        ("get_typed_relations", ("x",), {}),
        ("get_genealogy_tree", ("x",), {}),
        ("get_genealogy_path", ("x", "y"), {}),
        ("merge_entity", ("x", "y"), {}),
        ("migrate_untyped_relations", (), {}),
    ]:
        fn = getattr(client, method_name)
        with pytest.raises(NotImplementedError):
            fn(*args, **kwargs)
