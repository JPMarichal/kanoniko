"""Alejandría CLI — command-line interface for searching the corpus."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from typing import Any

import click

from alejandria.config import settings
from alejandria.search.textual import TextualSearch


def _json_out(data: Any) -> None:
    click.echo(json.dumps(data, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Lazy loaders
# ---------------------------------------------------------------------------

def _textual() -> TextualSearch:
    return TextualSearch(settings.sqlite_db_path)


def _semantic():
    try:
        from alejandria.search.semantic import SemanticSearch
        return SemanticSearch()
    except Exception:
        return None


def _neo4j():
    try:
        from alejandria.knowledge.neo4j_client import Neo4jClient
        return Neo4jClient()
    except Exception:
        return None


def _encode(query: str) -> list[float]:
    from alejandria.embeddings.model import encode_single
    return encode_single(query).tolist()


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(settings.app_version, prog_name="alejandria")
def cli() -> None:
    """Alejandría — bilingual scripture/gospel corpus search."""
    pass


# ---------------------------------------------------------------------------
# Search commands
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("query")
@click.option("-n", "--limit", default=10, help="Max results")
@click.option("-s", "--source", default=None, help="Filter by corpus subdirectory")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
def text(query: str, limit: int, source: str | None, as_json: bool) -> None:
    """Full-text search (BM25)."""
    ts = _textual()
    rows = ts.search(query=query, limit=limit, file_path_filter=source)
    if as_json:
        _json_out({"query": query, "mode": "text", "count": len(rows), "results": [asdict(r) for r in rows]})
        return
    if not rows:
        click.echo("No results found.")
        return
    for i, r in enumerate(rows, 1):
        click.echo(f"\n--- [{i}] {r.file_path} (chunk {r.chunk_index}, score {r.score:.4f}) ---")
        click.echo(r.text[:500])


@cli.command()
@click.argument("query")
@click.option("-n", "--limit", default=10, help="Max results")
@click.option("-s", "--source", default=None, help="Filter by corpus subdirectory")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
def semantic(query: str, limit: int, source: str | None, as_json: bool) -> None:
    """Semantic (embedding) search."""
    sem = _semantic()
    if sem is None:
        click.echo("Error: Semantic search unavailable (Qdrant not connected)", err=True)
        sys.exit(1)
    query_vector = _encode(query)
    rows = sem.search(query_vector=query_vector, limit=limit, source_filter=source)
    if as_json:
        _json_out({"query": query, "mode": "semantic", "count": len(rows), "results": [asdict(r) for r in rows]})
        return
    if not rows:
        click.echo("No results found.")
        return
    for i, r in enumerate(rows, 1):
        click.echo(f"\n--- [{i}] {r.file_path} (chunk {r.chunk_index}, score {r.score:.4f}) ---")
        click.echo(r.text[:500])


@cli.command()
@click.argument("query")
@click.option("-n", "--limit", default=10, help="Max results")
@click.option("-s", "--source", default=None, help="Filter by corpus subdirectory")
@click.option("--text-weight", default=0.4, help="Text weight (default 0.4)")
@click.option("--semantic-weight", default=0.6, help="Semantic weight (default 0.6)")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
def hybrid(query: str, limit: int, source: str | None, text_weight: float, semantic_weight: float, as_json: bool) -> None:
    """Hybrid search (text + semantic with RRF)."""
    from alejandria.search.hybrid import reciprocal_rank_fusion

    ts = _textual()
    sem = _semantic()
    if sem is None:
        click.echo("Error: Hybrid search requires semantic search", err=True)
        sys.exit(1)
    fetch_limit = min(limit * 3, 100)
    text_rows = ts.search(query=query, limit=fetch_limit, file_path_filter=source)
    text_dicts = [asdict(r) for r in text_rows]

    query_vector = _encode(query)
    sem_rows = sem.search(query_vector=query_vector, limit=fetch_limit, source_filter=source)
    sem_dicts = [asdict(r) for r in sem_rows]

    merged = reciprocal_rank_fusion(
        text_results=text_dicts, semantic_results=sem_dicts,
        limit=limit, text_weight=text_weight, semantic_weight=semantic_weight,
    )
    if as_json:
        _json_out({"query": query, "mode": "hybrid", "count": len(merged), "results": [asdict(r) for r in merged]})
        return
    if not merged:
        click.echo("No results found.")
        return
    for i, r in enumerate(merged, 1):
        click.echo(f"\n--- [{i}] {r.file_path} (chunk {r.chunk_index}, score {r.combined_score:.4f}) ---")
        click.echo(r.text[:500])


# ---------------------------------------------------------------------------
# Graph commands
# ---------------------------------------------------------------------------

@cli.group()
def graph() -> None:
    """Knowledge graph commands."""
    pass


@graph.command("find")
@click.argument("query")
@click.option("-t", "--type", "entity_type", default=None, help="Entity type filter")
@click.option("-n", "--limit", default=20, help="Max results")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
def graph_find(query: str, entity_type: str | None, limit: int, as_json: bool) -> None:
    """Search entities by name."""
    neo4j = _neo4j()
    if neo4j is None:
        click.echo("Error: Knowledge graph unavailable", err=True)
        sys.exit(1)
    results = neo4j.find_node(search=query, entity_type=entity_type, limit=limit)
    if as_json:
        _json_out(results)
        return
    if not results:
        click.echo("No entities found.")
        return
    for r in results:
        aliases = f" (aka: {', '.join(r.get('aliases', []))})" if r.get("aliases") else ""
        click.echo(f"  [{r['type']}] {r['name']}{aliases}")


@graph.command("neighbors")
@click.argument("name")
@click.option("-d", "--depth", default=1, help="Traversal depth (max 3)")
@click.option("-n", "--limit", default=50, help="Max results")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
def graph_neighbors(name: str, depth: int, limit: int, as_json: bool) -> None:
    """Get connected entities."""
    neo4j = _neo4j()
    if neo4j is None:
        click.echo("Error: Knowledge graph unavailable", err=True)
        sys.exit(1)
    result = neo4j.get_neighbors(name=name, depth=min(depth, 3), limit=limit)
    if as_json:
        _json_out(result)
        return
    if not result["nodes"]:
        click.echo(f"No neighbors found for '{name}'.")
        return
    click.echo(f"Neighbors of {name}:")
    for n in result["nodes"]:
        click.echo(f"  [{n['type']}] {n['name']}")
    click.echo(f"\nRelationships:")
    for e in result["edges"]:
        src = e.get("source") or e.get("from", "?")
        rel = e.get("relation") or e.get("type", "?")
        tgt = e.get("target") or e.get("to", "?")
        click.echo(f"  {src} --[{rel}]--> {tgt}")


@graph.command("summary")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
def graph_summary(as_json: bool) -> None:
    """Show graph statistics."""
    neo4j = _neo4j()
    if neo4j is None:
        click.echo("Error: Knowledge graph unavailable", err=True)
        sys.exit(1)
    summary = neo4j.graph_summary()
    if as_json:
        _json_out(summary)
        return
    click.echo(f"Nodes: {summary['total_nodes']}")
    click.echo(f"Relationships: {summary['total_relationships']}")
    click.echo("By type:")
    for t in summary["nodes_by_type"]:
        click.echo(f"  {t['type']}: {t['count']}")


# ---------------------------------------------------------------------------
# System commands
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("question")
@click.option("-s", "--source", default=None, help="Filter by corpus subdirectory")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
def ask(question: str, source: str | None, as_json: bool) -> None:
    """Ask a question (RAG-powered answer from the corpus)."""
    from alejandria.config import settings
    if not settings.llm_api_key:
        click.echo("Error: ALEJANDRIA_LLM_API_KEY not set in .env", err=True)
        sys.exit(1)
    from alejandria.chat.rag import RAGPipeline
    from alejandria.knowledge.profile_store import ProfileStore
    pipeline = RAGPipeline(
        textual_search=_textual(),
        semantic_search=_semantic(),
        neo4j_client=_neo4j(),
        profile_store=ProfileStore(settings.sqlite_db_path),
    )
    result = pipeline.ask(question=question, source_filter=source)
    if as_json:
        _json_out({
            "answer": result.answer,
            "sources": [
                {"file_path": s.file_path, "chunk_index": s.chunk_index, "mode": s.mode}
                for s in result.sources
            ],
            "graph_context": result.graph_context,
            "model": result.model,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
        })
        return
    click.echo(result.answer)
    click.echo(f"\n--- Sources ({len(result.sources)}) ---")
    for s in result.sources:
        click.echo(f"  [{s.mode}] {s.file_path} chunk {s.chunk_index}")
    click.echo(f"\n[{result.model} | {result.input_tokens} in / {result.output_tokens} out]")


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
def status(as_json: bool) -> None:
    """Show system status."""
    ts = _textual()
    sem = _semantic()
    neo4j = _neo4j()
    data = {
        "version": settings.app_version,
        "fts_documents": ts.count_documents(),
        "fts_chunks": ts.count_chunks(),
        "semantic_available": sem is not None,
        "graph_available": neo4j is not None,
    }
    if sem is not None:
        try:
            data["semantic_vectors"] = sem.count()
        except Exception:
            pass
    if neo4j is not None:
        try:
            s = neo4j.graph_summary()
            data["graph_nodes"] = s["total_nodes"]
        except Exception:
            pass
    if as_json:
        _json_out(data)
        return
    click.echo(f"Alejandría v{data['version']}")
    click.echo(f"  FTS: {data['fts_documents']} docs, {data['fts_chunks']} chunks")
    click.echo(f"  Semantic: {'available' if data['semantic_available'] else 'unavailable'}"
               + (f" ({data.get('semantic_vectors', '?')} vectors)" if data["semantic_available"] else ""))
    click.echo(f"  Graph: {'available' if data['graph_available'] else 'unavailable'}"
               + (f" ({data.get('graph_nodes', '?')} nodes)" if data["graph_available"] else ""))


@cli.command()
@click.option("--full", is_flag=True, help="Full reindex (clear and rebuild)")
def index(full: bool) -> None:
    """Run corpus indexing."""
    from alejandria.api.dependencies import get_pipeline
    pipeline = get_pipeline()
    stats = pipeline.run(full_reindex=full)
    click.echo(f"Indexing complete:")
    click.echo(f"  New: {stats['new_files']}, Updated: {stats['updated_files']}, "
               f"Deleted: {stats['deleted_files']}, Errors: {stats['errors']}")
    click.echo(f"  Total chunks: {stats['total_chunks']}")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
