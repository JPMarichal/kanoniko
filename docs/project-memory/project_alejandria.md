---
name: Alejandría - Project Vision
description: Independent containerized text library with textual, semantic, and KG search over LDS church literature and related materials
type: project
---

Alejandría is an independent, containerized text library system with three search modes: textual (full-text), semantic (embeddings), and knowledge graph.

**Corpus:** LDS Church canonical books (scriptures), general conference talks, biographies, manuals, web page downloads, and broad related literature. Formats: md, txt, html, json.

**Key decisions:**
- Independent service with its own git repo, NOT an extension of existing MCPs
- Containerized (Docker) for: auto server startup, isolation from host, CI/CD
- Corpus is NOT containerized — bind-mounted, it's the first thing that scales
- Local embedding model: paraphrase-multilingual-MiniLM-L12-v2 (bilingual ES/EN)
- Bilingual corpus: Spanish and English
- API port: 4300
- Interface priority: REST API → MCP adapter → CLI → UI
- Not exclusive to Claude Code — independent REST services, optionally consumed via MCP
- A secondary ETL system may handle format conversion/ingestion
- Template systems planned for format standardization
- Incremental ingestion is a priority (SHA-256 change detection)

**KG model:** Nodes = concepts, people, characters, places, peoples, objects, periods. Relations = mentions, defines, contradicts, themes, and more to be discovered as corpus is explored.

**Why:** User wants a self-contained, portable knowledge system over religious and historical texts that can be queried by any client.

**How to apply:** Design all components as containerized microservices with REST APIs. Prioritize offline/local operation. Keep architecture modular so search backends can evolve independently.
