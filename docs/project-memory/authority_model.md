---
name: Authority Model
description: Three-axis authority model implemented in src/alejandria/authority.py — doctrinal authority, rigor, 4 I's, official/current booleans, context/consensus modifiers, audience, speaker calling, hymn doctrinal scale
type: project
---

Authority model fully designed (docs/authority-model.md) and implemented (src/alejandria/authority.py).

**Three axes:** authority (1-100), rigor (1-100), 4 I's (imprescindible/importante/interesante/irrelevante)
**Booleans:** official, current
**Modifiers:** delivery context (×0.5 to ×1.0), consensus (×1.0 to ×1.15 per D&C 107:27)
**Attributes:** audience (adult/youth/children/leadership/general), speaker_calling, hymn_doctrinal

**Implementation touchpoints:**
- `authority.py`: AuthorityMeta, derive_authority(), effective_authority(), classify_query_type(), degrade_importance()
- `pipeline.py`: derives authority from corpus path, stores in SQLite metadata + Qdrant payloads
- `rag.py`: authority boost in scoring, authority labels in reranker prompt + context, SYSTEM_PROMPT updated
- `schemas.py` + `routes_chat.py` + `mcp_server.py`: authority/authority_label exposed in API responses
- `chat/classify`: now returns query_type alongside tier

**Requires full reindex** after deploy to populate authority metadata in existing chunks.

**Why:** RAG reranking needs hard numeric authority. Different query types (doctrinal vs historical vs teaching) weight axes differently. The 4 I's contextual degradation filters speculation.

**How to apply:** Deploy, full reindex, verify authority labels appear in search/chat results.
