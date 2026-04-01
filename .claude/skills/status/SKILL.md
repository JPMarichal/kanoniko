---
name: status
description: Check the full status of the Alejandría system — containers, API health, indexing, KG stats. Uses native Docker Engine in Ubuntu WSL.
---

# System Status Check

Check the complete status of the Alejandría system running on the native Docker Engine (Ubuntu-20.04 WSL).

## Docker Command Prefix

All docker commands must run through WSL with Rancher Desktop paths stripped:

```bash
wsl -d Ubuntu-20.04 -u root -e bash -c 'export PATH=$(echo "$PATH" | tr ":" "\n" | grep -v -i "rancher" | tr "\n" ":") && export DOCKER_CONFIG=/tmp/alejandria-docker-config && <COMMAND>'
```

## Checks to Run

1. **Container status**:
```bash
wsl -d Ubuntu-20.04 -u root -e bash -c 'export PATH=$(echo "$PATH" | tr ":" "\n" | grep -v -i "rancher" | tr "\n" ":") && export DOCKER_CONFIG=/tmp/alejandria-docker-config && /usr/bin/docker ps --filter name=alejandria --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
```

2. **GPU visibility**:
```bash
wsl -d Ubuntu-20.04 -e bash -c "nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader"
```

3. **API health**:
```bash
curl -s http://localhost:4300/health | python -m json.tool
```

4. **Indexing status**:
Use `mcp__alejandria__corpus_status` or:
```bash
curl -s http://localhost:4300/index/status | python -m json.tool
```

5. **Knowledge Graph stats**:
Use `mcp__alejandria__kg_summary` or:
```bash
curl -s http://localhost:4300/search/graph/summary | python -m json.tool
```

6. **Available models**:
```bash
curl -s http://localhost:4300/chat/models | python -c "import sys,json; d=json.load(sys.stdin); [print(f'  {m[\"id\"]:30s} {m[\"tier\"]:10s} {\"OK\" if m[\"available\"] else \"NO KEY\"}') for m in d['models']]"
```

## Report Format
Summarize the health of each component:
- Docker Engine: running/stopped (Ubuntu-20.04 WSL)
- GPU: model, VRAM used/total
- API: running/down, embedding device (cpu/cuda)
- Neo4j: connected/disconnected
- Qdrant: connected/disconnected
- Documents indexed: count
- KG entities/relations: counts
- LLM models available: list
