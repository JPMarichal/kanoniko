"""Alejandría MCP server — exposes corpus search, KG, and chat as native tools.

Run via: python -m alejandria.mcp_server
Or from Docker: docker exec -i alejandria-api python -m alejandria.mcp_server
"""

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
_profile_store: Any = None


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


def _get_profile_store():
    global _profile_store
    if _profile_store is None:
        try:
            from alejandria.knowledge.profile_store import ProfileStore
            _profile_store = ProfileStore(settings.sqlite_db_path)
        except Exception:
            pass
    return _profile_store


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS = [
    Tool(
        name="search_text",
        description=(
            "Full-text keyword search (BM25/FTS5) over the Alejandría corpus. "
            "Best for exact phrases, verse lookups, and keyword queries. Bilingual ES/EN."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "FTS query (supports AND, OR, NOT, phrases)"},
                "limit": {"type": "integer", "description": "Max results (default 10)", "default": 10},
                "source_filter": {"type": "string", "description": "Filter by path prefix (e.g. 'en/scriptures/bom')"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="search_semantic",
        description=(
            "Semantic (embedding) search — finds passages by meaning, not just keywords. "
            "Best for conceptual queries. Bilingual ES/EN. Requires Qdrant."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query in any language"},
                "limit": {"type": "integer", "default": 10},
                "source_filter": {"type": "string"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="search_hybrid",
        description=(
            "Combined textual + semantic search using Reciprocal Rank Fusion. "
            "Best general-purpose search — combines keyword precision with semantic understanding."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query in any language"},
                "limit": {"type": "integer", "default": 10},
                "source_filter": {"type": "string", "description": "Filter by path prefix"},
                "text_weight": {"type": "number", "default": 0.4},
                "semantic_weight": {"type": "number", "default": 0.6},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="kg_find",
        description=(
            "Search for entities (people, places, concepts, peoples, objects, periods) "
            "in the knowledge graph by partial name match."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Entity name to search"},
                "entity_type": {
                    "type": "string",
                    "description": "Filter: person, place, concept, people, object, period, scripture",
                },
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="kg_relations",
        description=(
            "Get typed relations for an entity from the knowledge graph. "
            "Shows family ties (FATHER_OF, SPOUSE_OF), prophecies, authorship, "
            "geographic links, priesthood, typology, and more. "
            "Confidence levels: curated > metadata > llm_high > llm_low > ner > co_occurrence."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Entity name (exact match)"},
                "confidence_min": {
                    "type": "string",
                    "description": "Minimum confidence level (default: ner)",
                    "default": "ner",
                },
                "rel_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter to specific relation types (e.g. ['FATHER_OF', 'SPOUSE_OF'])",
                },
                "limit": {"type": "integer", "default": 50},
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="kg_profile",
        description=(
            "Get a rich entity profile: summary, aliases, mention count, key passages, "
            "themes. Available for ~400 most prominent entities in the corpus."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "entity_name": {"type": "string", "description": "Entity name"},
                "entity_type": {"type": "string", "description": "Optional type filter"},
            },
            "required": ["entity_name"],
        },
    ),
    Tool(
        name="kg_neighbors",
        description="Get entities and relationships connected to a given entity in the knowledge graph.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Exact entity name"},
                "depth": {"type": "integer", "default": 1, "description": "Traversal depth (1-3)"},
                "limit": {"type": "integer", "default": 50},
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="kg_docs",
        description="Find all documents in the corpus that mention a specific entity.",
        inputSchema={
            "type": "object",
            "properties": {
                "entity_name": {"type": "string", "description": "Exact entity name"},
            },
            "required": ["entity_name"],
        },
    ),
    Tool(
        name="kg_summary",
        description="Get knowledge graph statistics: total nodes, relationships, counts by type.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="chat_ask",
        description=(
            "Ask a question and get a full RAG-powered answer grounded in the corpus. "
            "Runs the complete pipeline: hybrid search, KG lookup, cross-references, "
            "reranking, and LLM answer generation with citations. Bilingual ES/EN."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Question to answer"},
                "source_filter": {"type": "string", "description": "Filter by path prefix"},
                "tier": {
                    "type": "string",
                    "description": "Model tier: auto (default), fast, balanced, quality",
                    "default": "auto",
                },
            },
            "required": ["question"],
        },
    ),
    Tool(
        name="chat_classify",
        description="Classify a question's complexity and see which model tier/model would be used.",
        inputSchema={
            "type": "object",
            "properties": {
                "question": {"type": "string"},
            },
            "required": ["question"],
        },
    ),
    Tool(
        name="corpus_status",
        description="Get system health: indexed documents, chunks, vectors, graph nodes/relationships.",
        inputSchema={"type": "object", "properties": {}},
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
    elif name == "kg_find":
        return _do_kg_find(args)
    elif name == "kg_relations":
        return _do_kg_relations(args)
    elif name == "kg_profile":
        return _do_kg_profile(args)
    elif name == "kg_neighbors":
        return _do_kg_neighbors(args)
    elif name == "kg_docs":
        return _do_kg_docs(args)
    elif name == "kg_summary":
        return _do_kg_summary()
    elif name == "chat_ask":
        return _do_chat_ask(args)
    elif name == "chat_classify":
        return _do_chat_classify(args)
    elif name == "corpus_status":
        return _do_corpus_status()
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
                "reference": r.reference,
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
                "reference": r.reference,
            }
            for r in rows
        ],
    }


def _do_search_hybrid(args: dict) -> dict:
    from alejandria.embeddings.model import encode_single
    from alejandria.search.hybrid import reciprocal_rank_fusion

    ts = _get_textual()
    sem = _get_semantic()
    if sem is None:
        return {"error": "Hybrid search requires semantic search (Qdrant not connected)"}
    limit = args.get("limit", 10)
    fetch_limit = min(limit * 3, 100)
    text_rows = ts.search(query=args["query"], limit=fetch_limit,
                          file_path_filter=args.get("source_filter"))
    text_dicts = [
        {"chunk_id": r.chunk_id, "text": r.text, "score": r.score,
         "file_path": r.file_path, "chunk_index": r.chunk_index,
         "metadata": r.metadata, "reference": r.reference}
        for r in text_rows
    ]

    query_vector = encode_single(args["query"]).tolist()
    sem_rows = sem.search(query_vector=query_vector, limit=fetch_limit,
                          source_filter=args.get("source_filter"))
    sem_dicts = [
        {"chunk_id": r.chunk_id, "text": r.text, "score": r.score,
         "file_path": r.file_path, "chunk_index": r.chunk_index,
         "metadata": {}, "reference": r.reference}
        for r in sem_rows
    ]

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
                "reference": r.reference,
            }
            for r in merged
        ],
    }


def _do_kg_find(args: dict) -> dict:
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


def _do_kg_relations(args: dict) -> dict:
    neo4j = _get_neo4j()
    if neo4j is None:
        return {"error": "Knowledge graph unavailable (Neo4j not connected)"}
    results = neo4j.get_typed_relations(
        entity_name=args["name"],
        confidence_min=args.get("confidence_min", "ner"),
        rel_types=args.get("rel_types"),
        limit=args.get("limit", 50),
    )
    return {
        "name": args["name"],
        "count": len(results),
        "relations": [
            {
                "from": r["from_name"],
                "from_type": r["from_type"],
                "relation": r["rel_type"],
                "to": r["to_name"],
                "to_type": r["to_type"],
                "confidence": (r.get("props") or {}).get("confidence", ""),
                "source_ref": (r.get("props") or {}).get("source_ref", ""),
            }
            for r in results
        ],
    }


def _do_kg_profile(args: dict) -> dict:
    ps = _get_profile_store()
    if ps is None:
        return {"error": "Profile store unavailable"}
    profile = ps.get_profile(args["entity_name"], args.get("entity_type"))
    if profile is None:
        return {"error": f"No profile found for '{args['entity_name']}'"}
    return profile.to_dict()


def _do_kg_neighbors(args: dict) -> dict:
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


def _do_kg_docs(args: dict) -> dict:
    neo4j = _get_neo4j()
    if neo4j is None:
        return {"error": "Knowledge graph unavailable (Neo4j not connected)"}
    docs = neo4j.get_documents_for_entity(args["entity_name"])
    return {"entity": args["entity_name"], "documents": docs}


def _do_kg_summary() -> dict:
    neo4j = _get_neo4j()
    if neo4j is None:
        return {"error": "Knowledge graph unavailable (Neo4j not connected)"}
    return neo4j.graph_summary()


def _do_chat_ask(args: dict) -> dict:
    from alejandria.chat.models import get_available_models
    if not settings.llm_api_key and not get_available_models():
        return {"error": "Chat unavailable: no LLM API key configured"}
    from alejandria.chat.rag import RAGPipeline
    pipeline = RAGPipeline(
        textual_search=_get_textual(),
        semantic_search=_get_semantic(),
        neo4j_client=_get_neo4j(),
        profile_store=_get_profile_store(),
    )
    result = pipeline.ask(
        question=args["question"],
        source_filter=args.get("source_filter"),
        tier_override=args.get("tier"),
    )
    return {
        "answer": result.answer,
        "sources": [
            {
                "file_path": s.file_path,
                "chunk_index": s.chunk_index,
                "mode": s.mode,
                "reference": s.reference,
                "score": s.score,
                "authority": s.authority,
                "authority_label": s.authority_label,
            }
            for s in result.sources
        ],
        "graph_context": result.graph_context,
        "model": result.model,
        "tier": result.tier,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
    }


def _do_chat_classify(args: dict) -> dict:
    from alejandria.authority import classify_query_type
    from alejandria.chat.models import classify_complexity, select_model
    tier = classify_complexity(args["question"])
    model = select_model(tier)
    query_type = classify_query_type(args["question"])
    return {
        "question": args["question"],
        "tier": tier.value,
        "query_type": query_type,
        "model": {
            "id": model.id,
            "provider": model.provider,
            "model_name": model.model_name,
            "cost_input_per_1m": model.cost_input,
            "cost_output_per_1m": model.cost_output,
        } if model else None,
    }


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
