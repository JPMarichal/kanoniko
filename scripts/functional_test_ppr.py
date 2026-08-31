#!/usr/bin/env python3
"""Functional tests for PPR implementation.

Tests the actual PPR module and RAG pipeline components with real Postgres data.
No API server required.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

from alejandria.knowledge.pagerank import pagerank_search, invalidate_pagerank_cache
from alejandria.chat.rag import RAGPipeline


def test_ppr_direct():
    """Test PPR directly with real entity names from the KG."""
    print("=" * 60)
    print("TEST 1: PPR direct con entidades reales")
    print("=" * 60)

    test_cases = [
        (["Nephi"], 10),
        (["Lehi"], 10),
        (["Nephi", "Lehi"], 15),
        (["Jesus Christ"], 10),
        (["Alma"], 10),
    ]

    for entities, top_k in test_cases:
        print(f"\nQuery: {entities} (top_k={top_k})")
        start = time.time()
        results = pagerank_search(query_entities=entities, alpha=0.5, top_k=top_k)
        elapsed = time.time() - start

        print(f"  Tiempo: {elapsed:.3f}s")
        print(f"  Resultados: {len(results)}")

        if results:
            print(f"  Top 3:")
            for r in results[:3]:
                print(f"    - {r['name']} ({r['entity_type']}): score={r['pagerank_score']:.6f}, chunks={r['chunk_count']}")
        else:
            print("  (sin resultados)")

    print("\n" + "=" * 60)


def test_ppr_cache():
    """Test PPR graph caching."""
    print("\nTEST 2: Caching del grafo PPR")
    print("=" * 60)

    # First call - cache miss
    start = time.time()
    results1 = pagerank_search(query_entities=["Nephi"], top_k=5)
    t1 = time.time() - start
    print(f"  Primera llamada (cache miss): {t1:.3f}s, {len(results1)} resultados")

    # Second call - should hit cache
    start = time.time()
    results2 = pagerank_search(query_entities=["Lehi"], top_k=5)
    t2 = time.time() - start
    print(f"  Segunda llamada (cache hit): {t2:.3f}s, {len(results2)} resultados")

    speedup = t1 / t2 if t2 > 0 else float('inf')
    print(f"  Speedup: {speedup:.1f}x")

    # Invalidate cache
    invalidate_pagerank_cache()
    print("  Cache invalidado")

    # Third call - cache miss again
    start = time.time()
    results3 = pagerank_search(query_entities=["Alma"], top_k=5)
    t3 = time.time() - start
    print(f"  Tercera llamada (post-invalidation): {t3:.3f}s, {len(results3)} resultados")

    print("=" * 60)


def test_ppr_edge_cases():
    """Test PPR edge cases."""
    print("\nTEST 3: Edge cases")
    print("=" * 60)

    # Empty query
    results = pagerank_search(query_entities=[])
    print(f"  Query vacía: {results} (esperado: [])")

    # Unknown entity
    results = pagerank_search(query_entities=["NonexistentEntityXYZ123"])
    print(f"  Entidad desconocida: {results} (esperado: [])")

    # Alpha extremes
    results_alpha0 = pagerank_search(query_entities=["Nephi"], alpha=0.0, top_k=5)
    results_alpha1 = pagerank_search(query_entities=["Nephi"], alpha=1.0, top_k=5)
    print(f"  alpha=0.0: {len(results_alpha0)} resultados")
    print(f"  alpha=1.0: {len(results_alpha1)} resultados")

    print("=" * 60)


def test_kg_stats():
    """Show KG statistics."""
    print("\nTEST 4: Estadísticas del KG")
    print("=" * 60)

    from alejandria.storage.postgres.connection import get_connection
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM entities")
            entities = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM relations")
            relations = cur.fetchone()[0]
            cur.execute("SELECT count(DISTINCT rel_type) FROM relations")
            rel_types = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM chunks")
            chunks = cur.fetchone()[0]

    print(f"  Entidades: {entities}")
    print(f"  Relaciones: {relations}")
    print(f"  Tipos de relación: {rel_types}")
    print(f"  Chunks: {chunks}")

    print("=" * 60)


def test_chat_ppr_integration():
    """Test that chat pipeline can extract entities and run PPR."""
    print("\nTEST 5: Integración PPR en RAG pipeline")
    print("=" * 60)

    try:
        pipeline = RAGPipeline(
            textual_search=None,
            semantic_search=None,
            graph_client=None,
            profile_store=None,
        )

        # Test entity extraction (no LLM needed)
        test_questions = [
            "¿Cómo se relaciona Nephi con Lehi?",
            "¿Qué dijo Jesus Christ sobre el amor?",
            "Who is Alma and what is his relationship with Ammon?",
        ]

        for q in test_questions:
            print(f"\nPregunta: {q}")
            entities = pipeline._extract_entities_from_question(q)
            print(f"  Entidades extraídas: {entities}")

    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PRUEBAS DE FUNCIONAMIENTO — PPR Alejandría")
    print("=" * 60)

    try:
        test_kg_stats()
        test_ppr_direct()
        test_ppr_cache()
        test_ppr_edge_cases()
        test_chat_ppr_integration()

        print("\n" + "=" * 60)
        print("TODAS LAS PRUEBAS COMPLETADAS")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
