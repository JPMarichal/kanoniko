---
name: Always batch Neo4j operations
description: Neo4j writes must be batched (UNWIND) not individual — individual calls caused 19h rebuild vs 30min batched
type: feedback
---

Always batch Neo4j write operations using UNWIND, never individual merge calls per entity/relation.

**Why:** Individual merge_entity/merge_relation calls per chunk caused a 19h KG rebuild (34K chunks × ~670 calls each). Batching with UNWIND reduced it to ~30 min — a 40x improvement. The user had to explicitly ask me to stop and optimize when I recommended "let it run."

**How to apply:** Any loop that writes to Neo4j (rebuild_kg, run/full_reindex, incremental indexing) must accumulate operations and flush in batches (500 chunks). Use batch_merge_entities, batch_merge_relations, batch_link_entities_to_document, batch_merge_documents. Also applies to future operations — when an ETA exceeds expectations by 10x+, stop and optimize rather than waiting.
