"""Alejandría MCP server — exposes search tools over stdio transport."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from alejandria.config import settings
from alejandria.search.textual import TextualSearch

logger = logging.getLogger(__name__)

app = Server("alejandria")

# ---------------------------------------------------------------------------
# Lazy singletons (same pattern as FastAPI dependencies)
# ---------------------------------------------------------------------------

_textual: TextualSearch | None = None
_semantic: Any = None
_neo4j: Any = None


def _get_textual() -> TextualSearch:
    global _textual
    if _textual is None:
        _textual = TextualSearch(settings.sqlite_db_path)
    return _textual


def _get_semantic():
    global _semantic
    if _semantic is None:
        try:
            from alejandria.search.semantic import SemanticSearch
            _semantic = SemanticSearch()
        except Exception:
            pass
    return _semantic


def _get_neo4j():
    global _neo4j
    if _neo4j is None:
        try:
            from alejandria.knowledge.neo4j_client import Neo4jClient
            _neo4j = Neo4jClient()
        except Exception:
            pass
    return _neo4j


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS = [
    Tool(
        name="search_text",
        description=(
            "Full-text search (BM25) over the Alejandría scripture/gospel corpus. "
            "Returns ranked text chunks matching the query. Bilingual ES/EN."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query text"},
                "limit": {"type": "integer", "description": "Max results (default 10)", "default": 10},
                "source_filter": {
                    "type": "string",
                    "description": "Filter by corpus subdirectory (e.g. 'scriptures', 'conference')",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="search_semantic",
        description=(
            "Semantic (embedding) search over the corpus using multilingual embeddings. "
            "Finds passages by meaning, not just keywords. Requires Qdrant."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query text"},
                "limit": {"type": "integer", "description": "Max results (default 10)", "default": 10},
                "source_filter": {"type": "string", "description": "Filter by corpus subdirectory"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="search_hybrid",
        description=(
            "Combined textual + semantic search using Reciprocal Rank Fusion. "
            "Best for general queries — combines keyword precision with semantic understanding."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query text"},
                "limit": {"type": "integer", "description": "Max results (default 10)", "default": 10},
                "source_filter": {"type": "string", "description": "Filter by corpus subdirectory"},
                "text_weight": {"type": "number", "description": "Weight for text results (default 0.4)"},
                "semantic_weight": {"type": "number", "description": "Weight for semantic results (default 0.6)"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="graph_find",
        description=(
            "Search for entities (people, places, concepts, peoples, objects) in the "
            "knowledge graph by partial name match."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Entity name to search"},
                "entity_type": {
                    "type": "string",
                    "description": "Filter by type: person, place, concept, people, object, period",
                },
                "limit": {"type": "integer", "description": "Max results (default 20)", "default": 20},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="graph_neighbors",
        description=(
            "Get entities and relationships connected to a given entity in the knowledge graph. "
            "Useful for exploring connections between people, places, and concepts."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Exact entity name"},
                "depth": {"type": "integer", "description": "Traversal depth (default 1, max 3)", "default": 1},
                "limit": {"type": "integer", "description": "Max results (default 50)", "default": 50},
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="graph_docs",
        description="Find documents that mention a specific entity in the knowledge graph.",
        inputSchema={
            "type": "object",
            "properties": {
                "entity_name": {"type": "string", "description": "Exact entity name"},
            },
            "required": ["entity_name"],
        },
    ),
    Tool(
        name="corpus_status",
        description="Get system health: indexed documents, chunks, vectors, graph nodes.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="ask",
        description=(
            "Ask a question about the scriptures or gospel and get an AI-generated answer "
            "grounded in the corpus. Uses RAG: retrieves from text, semantic, and knowledge "
            "graph search, then generates an answer with citations. Bilingual ES/EN."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Question to answer"},
                "source_filter": {"type": "string", "description": "Filter by corpus subdirectory"},
            },
            "required": ["question"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

@app.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        result = _dispatch(name, arguments)
        text = json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as exc:
        text = json.dumps({"error": str(exc)}, ensure_ascii=False)
    return [TextContent(type="text", text=text)]


def _dispatch(name: str, args: dict) -> dict:
    if name == "search_text":
        return _do_search_text(args)
    elif name == "search_semantic":
        return _do_search_semantic(args)
    elif name == "search_hybrid":
        return _do_search_hybrid(args)
    elif name == "graph_find":
        return _do_graph_find(args)
    elif name == "graph_neighbors":
        return _do_graph_neighbors(args)
    elif name == "graph_docs":
        return _do_graph_docs(args)
    elif name == "corpus_status":
        return _do_corpus_status()
    elif name == "ask":
        return _do_ask(args)
    else:
        return {"error": f"Unknown tool: {name}"}


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _do_search_text(args: dict) -> dict:
    ts = _get_textual()
    rows = ts.search(
        query=args["query"],
        limit=args.get("limit", 10),
        file_path_filter=args.get("source_filter"),
    )
    return {
        "query": args["query"],
        "mode": "text",
        "count": len(rows),
        "results": [
            {
                "text": r.text,
                "score": r.score,
                "file_path": r.file_path,
                "chunk_index": r.chunk_index,
            }
            for r in rows
        ],
    }


def _do_search_semantic(args: dict) -> dict:
    sem = _get_semantic()
    if sem is None:
        return {"error": "Semantic search unavailable (Qdrant not connected)"}
    from alejandria.embeddings.model import encode_single
    query_vector = encode_single(args["query"]).tolist()
    rows = sem.search(
        query_vector=query_vector,
        limit=args.get("limit", 10),
        source_filter=args.get("source_filter"),
    )
    return {
        "query": args["query"],
        "mode": "semantic",
        "count": len(rows),
        "results": [
            {
                "text": r.text,
                "score": r.score,
                "file_path": r.file_path,
                "chunk_index": r.chunk_index,
            }
            for r in rows
        ],
    }


def _do_search_hybrid(args: dict) -> dict:
    from dataclasses import asdict
    from alejandria.embeddings.model import encode_single
    from alejandria.search.hybrid import reciprocal_rank_fusion

    ts = _get_textual()
    sem = _get_semantic()
    if sem is None:
        return {"error": "Hybrid search requires semantic search (Qdrant not connected)"}
    limit = args.get("limit", 10)
    fetch_limit = min(limit * 3, 100)
    text_rows = ts.search(query=args["query"], limit=fetch_limit)
    text_dicts = [asdict(r) for r in text_rows]

    query_vector = encode_single(args["query"]).tolist()
    sem_rows = sem.search(query_vector=query_vector, limit=fetch_limit)
    sem_dicts = [asdict(r) for r in sem_rows]

    merged = reciprocal_rank_fusion(
        text_results=text_dicts,
        semantic_results=sem_dicts,
        limit=limit,
        text_weight=args.get("text_weight", 0.4),
        semantic_weight=args.get("semantic_weight", 0.6),
    )
    return {
        "query": args["query"],
        "mode": "hybrid",
        "count": len(merged),
        "results": [
            {
                "text": r.text,
                "combined_score": r.combined_score,
                "file_path": r.file_path,
                "chunk_index": r.chunk_index,
            }
            for r in merged
        ],
    }


def _do_graph_find(args: dict) -> dict:
    neo4j = _get_neo4j()
    if neo4j is None:
        return {"error": "Knowledge graph unavailable (Neo4j not connected)"}
    results = neo4j.find_node(
        search=args["query"],
        entity_type=args.get("entity_type"),
        limit=args.get("limit", 20),
    )
    return {
        "query": args["query"],
        "count": len(results),
        "results": [
            {"name": r["name"], "type": r["type"], "aliases": r.get("aliases")}
            for r in results
        ],
    }


def _do_graph_neighbors(args: dict) -> dict:
    neo4j = _get_neo4j()
    if neo4j is None:
        return {"error": "Knowledge graph unavailable (Neo4j not connected)"}
    depth = min(args.get("depth", 1), 3)
    result = neo4j.get_neighbors(
        name=args["name"],
        depth=depth,
        limit=args.get("limit", 50),
    )
    return {
        "name": args["name"],
        "nodes": result["nodes"],
        "edges": result["edges"],
    }


def _do_graph_docs(args: dict) -> dict:
    neo4j = _get_neo4j()
    if neo4j is None:
        return {"error": "Knowledge graph unavailable (Neo4j not connected)"}
    docs = neo4j.get_documents_for_entity(args["entity_name"])
    return {"entity": args["entity_name"], "documents": docs}


def _do_corpus_status() -> dict:
    ts = _get_textual()
    sem = _get_semantic()
    neo4j = _get_neo4j()
    result = {
        "fts_documents": ts.count_documents(),
        "fts_chunks": ts.count_chunks(),
        "semantic_available": sem is not None,
        "graph_available": neo4j is not None,
    }
    if sem is not None:
        try:
            result["semantic_vectors"] = sem.count()
        except Exception:
            pass
    if neo4j is not None:
        try:
            summary = neo4j.graph_summary()
            result["graph_nodes"] = summary["total_nodes"]
            result["graph_relationships"] = summary["total_relationships"]
        except Exception:
            pass
    return result


def _do_ask(args: dict) -> dict:
    from alejandria.config import settings
    if not settings.llm_api_key:
        return {"error": "Chat unavailable: ALEJANDRIA_LLM_API_KEY not set"}
    from alejandria.chat.rag import RAGPipeline
    pipeline = RAGPipeline(
        textual_search=_get_textual(),
        semantic_search=_get_semantic(),
        neo4j_client=_get_neo4j(),
    )
    result = pipeline.ask(
        question=args["question"],
        source_filter=args.get("source_filter"),
    )
    return {
        "answer": result.answer,
        "sources": [
            {"file_path": s.file_path, "chunk_index": s.chunk_index, "mode": s.mode}
            for s in result.sources
        ],
        "graph_context": result.graph_context,
        "model": result.model,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def start() -> None:
    """Synchronous entry point for the MCP server."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    start()
