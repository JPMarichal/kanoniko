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
    """Match Neo4jClient.graph_summary shape exactly — callers must be agnostic."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    summary = client.graph_summary()

    for key in ("total_nodes", "total_relationships", "nodes_by_type", "relationships_by_type"):
        assert key in summary, f"missing field {key}"

    assert isinstance(summary["total_nodes"], int)
    assert isinstance(summary["total_relationships"], int)
    assert isinstance(summary["nodes_by_type"], list)
    assert isinstance(summary["relationships_by_type"], list)


def test_graph_summary_reasonable_numbers() -> None:
    """Sanity check: numbers should be in expected range post-R0+R7."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    summary = client.graph_summary()

    # Post-cleanup IONOS: ~811k entities, ~21M relations.
    assert 500_000 < summary["total_nodes"] < 2_000_000
    assert 10_000_000 < summary["total_relationships"] < 50_000_000


def test_graph_summary_types_lists_structure() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    summary = client.graph_summary()

    for list_field in ("nodes_by_type", "relationships_by_type"):
        assert len(summary[list_field]) > 0, f"{list_field} is empty"
        for item in summary[list_field]:
            assert "type" in item and "count" in item
            assert isinstance(item["type"], str)
            assert isinstance(item["count"], int)
        counts = [item["count"] for item in summary[list_field]]
        assert counts == sorted(counts, reverse=True), \
            f"{list_field} not sorted by count desc"


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
    """Methods still pending (parallels + write path) should raise NotImplementedError.
    Fails loudly so callers discover the gap at test-time, not silently."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()

    for method_name, args, kwargs in [
        ("get_parallel_passages", ("path/x.txt",), {}),
        ("merge_entity", ("x", "y"), {}),
        ("migrate_untyped_relations", (), {}),
    ]:
        fn = getattr(client, method_name)
        with pytest.raises(NotImplementedError):
            fn(*args, **kwargs)


# --------------------------------------------------------------------------- #
# Tier 2d: genealogy
# --------------------------------------------------------------------------- #

def test_get_genealogy_tree_shape() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    tree = client.get_genealogy_tree("Lehi", direction="both", depth=3, lang="en")

    for field in ("name", "name_alt", "type", "relation", "spouses", "parents", "children"):
        assert field in tree, f"missing field {field}"
    assert tree["name"] == "Lehi"
    assert tree["relation"] is None  # root node has no incoming relation
    assert isinstance(tree["spouses"], list)
    assert isinstance(tree["parents"], list)
    assert isinstance(tree["children"], list)


def test_get_genealogy_tree_lehi_descendants_has_sons() -> None:
    """Post family backfill (+168% FATHER_OF), Lehi should have 4-6 BoM sons."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    tree = client.get_genealogy_tree("Lehi", direction="down", depth=1, lang="en")

    child_names = {c["name"] for c in tree["children"]}
    expected = {"Nephi", "Laman", "Lemuel", "Sam", "Jacob", "Joseph"}
    overlap = child_names & expected
    assert len(overlap) >= 3, (
        f"expected ≥3 of {expected} as Lehi's children, got {child_names}"
    )


def test_get_genealogy_tree_nephi_ancestors_has_lehi() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    tree = client.get_genealogy_tree("Nephi", direction="up", depth=2, lang="en")

    parent_names = {p["name"] for p in tree["parents"]}
    assert "Lehi" in parent_names, (
        f"Lehi should appear as Nephi's parent; got {parent_names}"
    )


def test_get_genealogy_tree_depth_clamped() -> None:
    """depth > 10 is clamped; depth < 1 is clamped to 1."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()

    tree_low = client.get_genealogy_tree("Lehi", direction="down", depth=0, lang="en")
    tree_high = client.get_genealogy_tree("Lehi", direction="down", depth=50, lang="en")

    # Both should return without errors; tree shape valid.
    assert "children" in tree_low
    assert "children" in tree_high


def test_get_genealogy_tree_lang_alt_name() -> None:
    """lang='es' should surface Spanish alias from gazetteer when available."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    tree_en = client.get_genealogy_tree("Nephi", direction="up", depth=1, lang="en")
    tree_es = client.get_genealogy_tree("Nephi", direction="up", depth=1, lang="es")

    assert tree_en["name_alt"] is None  # EN mode returns None
    # ES mode: Nephi's Spanish alias "Nefi" exists in gazetteer
    assert tree_es["name_alt"] == "Nefi", (
        f"expected 'Nefi' as ES alt; got {tree_es['name_alt']!r}"
    )


def test_get_genealogy_tree_empty_name() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    tree = client.get_genealogy_tree("", direction="both", depth=3, lang="en")
    assert tree["name"] == ""
    assert tree["children"] == []
    assert tree["parents"] == []


def test_get_genealogy_path_shape() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    result = client.get_genealogy_path("Lehi", "Nephi")

    for field in ("person1", "person2", "path_length", "path", "edges"):
        assert field in result


def test_get_genealogy_path_lehi_to_nephi() -> None:
    """Direct parent-child: path_length should be 1."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    result = client.get_genealogy_path("Lehi", "Nephi")

    assert result["path_length"] >= 1
    assert result["path_length"] <= 3  # direct or at most via sibling/spouse
    # The path must contain both endpoints
    names = [n["name"] for n in result["path"]]
    assert "Lehi" in names and "Nephi" in names


def test_get_genealogy_path_no_path_returns_empty() -> None:
    """Nonexistent second person returns path_length -1."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    result = client.get_genealogy_path("Lehi", "xyzNonExistentPerson")

    assert result["path_length"] == -1
    assert result["path"] == []
    assert result["edges"] == []


def test_get_genealogy_path_alias_resolution() -> None:
    """Same result whether query via canonical or alias."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    canonical = client.get_genealogy_path("Lehi", "Nephi")
    alias = client.get_genealogy_path("Lehi", "Nefi")

    assert canonical["path_length"] == alias["path_length"]


# --------------------------------------------------------------------------- #
# get_neighbors (Tier 2b)
# --------------------------------------------------------------------------- #

def test_get_neighbors_returns_shape() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    result = client.get_neighbors("Nephi", depth=1, limit=20)

    assert isinstance(result, dict)
    assert set(result.keys()) == {"nodes", "edges"}
    assert isinstance(result["nodes"], list)
    assert isinstance(result["edges"], list)


def test_get_neighbors_nephi_depth_1_includes_family() -> None:
    """Post R0+R7, Nephi's 1-hop neighbors should include at least some
    of the BoM family (Lehi, Laman, Lemuel, Sam, Jacob, Joseph) via
    curated relations."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    result = client.get_neighbors("Nephi", depth=1, limit=100)

    neighbor_names = {n["name"] for n in result["nodes"]}
    expected_family = {"Lehi", "Laman", "Lemuel", "Sam", "Jacob", "Joseph"}
    overlap = neighbor_names & expected_family
    assert len(overlap) >= 3, (
        f"expected ≥3 of {expected_family} in neighbors, got overlap={overlap}. "
        f"Sample neighbors: {sorted(neighbor_names)[:20]}"
    )


def test_get_neighbors_empty_entity_returns_empty() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    assert client.get_neighbors("") == {"nodes": [], "edges": []}
    assert client.get_neighbors("xyzNotInDB") == {"nodes": [], "edges": []}


def test_get_neighbors_respects_limit() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    result = client.get_neighbors("Jesus Christ", depth=1, limit=10)
    assert len(result["edges"]) <= 10


def test_get_neighbors_relation_types_filter() -> None:
    """When relation_types given, returned edges must all have those types."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    result = client.get_neighbors(
        "Nephi", depth=1, relation_types=["BROTHER_OF"], limit=30
    )
    if result["edges"]:
        for edge in result["edges"]:
            assert edge["type"] == "BROTHER_OF", (
                f"relation_types filter leaked: got {edge['type']}"
            )


def test_get_neighbors_alias_resolves_to_canonical() -> None:
    """Search by Spanish alias ('Nefi') should yield same neighbors as canonical
    ('Nephi'). Validates the gazetteer resolution step."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    r_canonical = client.get_neighbors("Nephi", depth=1, limit=50)
    r_alias = client.get_neighbors("Nefi", depth=1, limit=50)

    canonical_names = {n["name"] for n in r_canonical["nodes"]}
    alias_names = {n["name"] for n in r_alias["nodes"]}
    overlap = canonical_names & alias_names
    # Expect substantial overlap (should be identical modulo LIMIT ordering).
    assert len(overlap) >= min(5, len(canonical_names) // 2), (
        f"alias resolution broken: canonical={len(canonical_names)}, "
        f"alias={len(alias_names)}, overlap={len(overlap)}"
    )


def test_get_neighbors_depth_2_recursive() -> None:
    """depth=2 should use the recursive CTE path; must not explode."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    result = client.get_neighbors("Nephi", depth=2, limit=50)

    assert len(result["nodes"]) <= 50  # respects limit
    assert len(result["nodes"]) >= 1   # at least some neighbors at depth 2


# --------------------------------------------------------------------------- #
# Tier 2c: mentions-based + typed_relations
# --------------------------------------------------------------------------- #

def test_get_documents_for_entity_returns_real_docs() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient

    client = PostgresGraphClient()
    docs = client.get_documents_for_entity("Nephi")

    assert len(docs) > 0, "Nephi should be mentioned in many corpus docs"
    for d in docs[:3]:
        assert "file_path" in d and "source" in d
        assert isinstance(d["file_path"], str) and d["file_path"]


def test_get_documents_for_entity_empty_name() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    assert client.get_documents_for_entity("") == []
    assert client.get_documents_for_entity("   ") == []


def test_get_documents_for_entity_alias_resolution() -> None:
    """'Nefi' (ES alias) should resolve to same docs as 'Nephi' (canonical)."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    canonical = {d["file_path"] for d in client.get_documents_for_entity("Nephi")}
    via_alias = {d["file_path"] for d in client.get_documents_for_entity("Nefi")}
    if not canonical or not via_alias:
        pytest.skip("corpus doesn't have Nephi mentions under either form")
    overlap = canonical & via_alias
    assert len(overlap) >= min(5, len(canonical) // 2), (
        f"alias resolution failed: canonical={len(canonical)} alias={len(via_alias)} overlap={len(overlap)}"
    )


def test_get_documents_for_entities_batch_shape() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    result = client.get_documents_for_entities_batch(["Nephi", "Lehi", "NonexistentXYZ"])

    assert set(result.keys()) == {"Nephi", "Lehi", "NonexistentXYZ"}
    assert len(result["Nephi"]) > 0
    assert len(result["Lehi"]) > 0
    assert result["NonexistentXYZ"] == []


def test_get_documents_for_entities_batch_empty() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    assert client.get_documents_for_entities_batch([]) == {}


def test_get_all_entity_mentions_shape_and_ordering() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    mentions = client.get_all_entity_mentions()

    assert len(mentions) > 100, "expect thousands of entities with mentions"
    for m in mentions[:3]:
        for field in ("name", "type", "aliases", "doc_count", "file_paths"):
            assert field in m
        assert isinstance(m["aliases"], list)
        assert isinstance(m["file_paths"], list)
        assert m["doc_count"] == len(set(m["file_paths"]))

    # Sorted by doc_count desc
    counts = [m["doc_count"] for m in mentions[:50]]
    assert counts == sorted(counts, reverse=True)


def test_get_disambiguated_counts_shape() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    counts = client.get_disambiguated_counts()

    # May be empty if no resolved_name entries — that's acceptable.
    for key, per_resolved in list(counts.items())[:3]:
        assert isinstance(key, tuple) and len(key) == 2
        assert isinstance(per_resolved, dict)
        for resolved_name, n in per_resolved.items():
            assert isinstance(resolved_name, str) and resolved_name
            assert isinstance(n, int) and n > 0


def test_find_nodes_batch_returns_results() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    results = client.find_nodes_batch(["Nephi", "Lehi", "Moroni"], limit_per=5)

    assert len(results) > 0
    for r in results[:3]:
        assert "name" in r and "type" in r and "aliases" in r
        assert isinstance(r["aliases"], list)


def test_find_nodes_batch_empty() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    assert client.find_nodes_batch([]) == []


def test_get_typed_relations_shape() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    rels = client.get_typed_relations("Nephi", limit=20)

    assert len(rels) > 0
    for r in rels[:3]:
        for field in ("from_name", "from_type", "rel_type", "to_name", "to_type", "props"):
            assert field in r
        assert isinstance(r["props"], dict)
        # props must carry confidence tag
        assert "confidence" in r["props"]


def test_get_typed_relations_confidence_min_filter() -> None:
    """confidence_min='metadata' must drop llm_low/ner rows."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    rels = client.get_typed_relations("Nephi", confidence_min="metadata", limit=50)

    allowed = {"curated", "metadata"}
    for r in rels:
        conf = r["props"].get("confidence")
        assert conf in allowed, f"found {conf!r} despite confidence_min=metadata"


def test_get_typed_relations_rel_types_filter() -> None:
    """rel_types filter must be strict."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    rels = client.get_typed_relations("Lehi", rel_types=["FATHER_OF"], limit=50)

    for r in rels:
        assert r["rel_type"] == "FATHER_OF"


def test_get_typed_relations_curated_first() -> None:
    """Post R0+R7 +family backfill, curated relations should dominate top of the list."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    rels = client.get_typed_relations("Nephi", limit=10)

    if rels:
        top_confidences = [r["props"].get("confidence") for r in rels[:5]]
        # At least one of the top 5 should be curated post-cleanup.
        assert "curated" in top_confidences, (
            f"expected curated in top 5 but got {top_confidences}"
        )


def test_get_typed_relations_batch_shape() -> None:
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    rels = client.get_typed_relations_batch(["Nephi", "Lehi"], limit_per=10)

    assert len(rels) > 0
    for r in rels[:3]:
        for field in ("from_name", "from_type", "rel_type", "to_name", "to_type", "props"):
            assert field in r


def test_get_typed_relations_batch_excludes_mentioned_in() -> None:
    """MENTIONED_IN lives in a separate table now, but defensively: batch must
    not emit it even if relations table were to gain such rows."""
    from alejandria.knowledge.postgres_graph_client import PostgresGraphClient
    client = PostgresGraphClient()
    rels = client.get_typed_relations_batch(["Nephi"], limit_per=100)
    for r in rels:
        assert r["rel_type"] != "MENTIONED_IN"
