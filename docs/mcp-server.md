# MCP Server

Model Context Protocol adapter that exposes Alejandria's search capabilities as tools for AI assistants.

## Overview

The MCP server runs over stdio transport and provides 8 tools that map to the REST API functionality. This allows AI assistants like Claude to search the corpus, explore the knowledge graph, and ask questions directly.

## Tools

| Tool | Description |
|------|-------------|
| `search_text` | Full-text search (BM25) |
| `search_semantic` | Semantic search (embeddings) |
| `search_hybrid` | Combined text + semantic with RRF |
| `graph_find` | Search entities by name |
| `graph_neighbors` | Get entity connections |
| `graph_docs` | Documents mentioning an entity |
| `corpus_status` | System health and statistics |
| `ask` | RAG-powered Q&A |

## Configuration

Example MCP client configuration (`mcp-config.example.json`):

```json
{
  "mcpServers": {
    "alejandria": {
      "command": "python",
      "args": ["-m", "alejandria.mcp_server"],
      "env": {
        "ALEJANDRIA_SQLITE_DB_PATH": "/path/to/alejandria.db",
        "ALEJANDRIA_LLM_API_KEY": "your-key"
      }
    }
  }
}
```

## Running

```bash
# Direct execution
python -m alejandria.mcp_server

# Or via entry point
alejandria-mcp
```

## Implementation

`src/alejandria/mcp_server.py` — Uses the `mcp` Python SDK with lazy-loaded service singletons (same pattern as FastAPI dependencies).
