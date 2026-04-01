---
name: Proactive KG associations
description: Every new data association discovered during any process should be considered for the knowledge graph
type: feedback
---

Whenever a new association or relation is discovered (e.g., source_url for chapters, authorship from metadata, editorial context from study-intro), proactively consider adding it to the KG. Don't wait to be asked — any new linkable data is welcome.

**Why:** The user sees the KG as a living, growing asset. Every piece of structured data that can be linked is an opportunity to enrich the graph. The application should be proactive about this.

**How to apply:** When working on ingestion, scraping, or any data processing, always ask: "Is there a new association here that the KG should know about?" If yes, either add it directly or document it as a future KG integration point.
