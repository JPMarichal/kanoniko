---
name: status
description: Check the full status of the Alejandría system — containers, API health, indexing, KG stats.
---

# System Status Check

Check the complete status of the Alejandría system.

## Checks to Run

1. **Container status**:
```bash
docker ps --filter name=alejandria --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

2. **API health**:
```bash
curl -s http://localhost:4300/health | python -m json.tool
```

3. **Indexing status**:
Use `mcp__alejandria__index_status` or:
```bash
curl -s http://localhost:4300/index/status | python -m json.tool
```

4. **Knowledge Graph stats**:
Use `mcp__alejandria__kg_summary` or:
```bash
curl -s http://localhost:4300/search/graph/summary | python -m json.tool
```

5. **Available models**:
```bash
curl -s http://localhost:4300/chat/models | python -c "import sys,json; d=json.load(sys.stdin); [print(f'  {m[\"id\"]:30s} {m[\"tier\"]:10s} {\"OK\" if m[\"available\"] else \"NO KEY\"}') for m in d['models']]"
```

## Report Format
Summarize the health of each component:
- API: running/down
- Neo4j: connected/disconnected
- Qdrant: connected/disconnected
- Documents indexed: count
- KG entities/relations: counts
- LLM models available: list
