---
name: Alejandría - Vision, Architecture Philosophy, and Roadmap
description: Deep vision for the system as a scripture study engine, corpus expansion strategy, and the role of the knowledge graph
type: project
---

## The Core Insight

The corpus is not just a collection of texts to search — it is the **accumulated knowledge base** that gives the system interpretive capability. Scriptures alone are the primary text, but without commentary they lack interpretive depth. Each layer of corpus (conference talks, manuals, commentaries, scholarly works) adds a new dimension of understanding.

A question like "Why does John mention the seamless coat?" cannot be answered from John 19 alone. It requires the commentary connecting it to the high priest's vestment in Exodus 28, the conference talk interpreting it christologically, and the institute manual explaining it for students.

## Three Layers of Scripture Parallelism

Parallelism is pervasive in LDS scriptures and is central to study:

**Layer 1 — Direct narrative parallels**: Same event, different books. Genesis 1 ↔ Moses 2 ↔ Abraham 4 (Creation). Detectable by KG (~80%) through entity/event isomorphism. The 20% gap is subtle linguistic differences (e.g., "Gods" vs "God") that carry theological weight.

**Layer 2 — Editorial parallels**: Same period narrated with different editorial purpose. The four Gospels (Matthew for Jews, Mark concise/action, Luke the historian, John the theologian). Also Kings ↔ Chronicles ↔ Samuel, Jude ↔ 2 Peter. KG can detect shared entities/events (~50%) and flag divergences, but cannot interpret *why* they differ — that requires editorial/scholarly knowledge.

**Layer 3 — Thematic trans-volume parallels**: Doctrinal themes recurring across all standard works. The Ten Commandments in Exodus, Deuteronomy, Mosiah, Sermon on the Mount, D&C. Typology (Joseph of Egypt as a type of Christ). KG resolves ~20-30% automatically (explicit citations). Subtle connections require either human annotation, LLM-assisted discovery, or — critically — **a richer corpus that contains the commentaries articulating these connections explicitly**.

**Key insight**: Layer 3 connections that are impossible to extract automatically from scripture text alone *will emerge naturally* when the corpus includes the scholarly and ecclesiastical commentaries that articulate them. The KG grows organically with the corpus.

## The KG's Role

The knowledge graph is excellent as a **representation and query tool** but limited as a **discovery tool** for deep thematic connections. The realistic strategy is hybrid:

1. **Automatic extraction** (spaCy + gazetteers): entities, places, explicit relations — already implemented
2. **Coded cross-references** (cross_references.py): expert knowledge, finite and verifiable — 35 groups implemented
3. **LLM as assisted annotator** (future): batch process where LLM reads chapter pairs and proposes thematic connections for validation
4. **Corpus-derived connections** (future): LDS scripture footnotes contain thousands of cross-references; if ingested, the KG absorbs them directly

## Corpus Expansion Roadmap

Ordered, not rushed:

1. **Current**: Scriptures from public sources (EN complete, ES BOM only). Training the infrastructure, proving the architecture.
2. **Scripture re-download** (planned): From the official Church site. Benefits: structured metadata (chapter headings, section summaries, footnotes, official cross-references), updated text, complete ES coverage for all volumes. This is NOT wasted work — the entire ingestion/chunking/RAG pipeline stays the same; only the data source changes and enriches.
3. **Tools**: Additional capabilities to make study more effective (to be defined as needs emerge).
4. **Conference General**: Decades of talks with author, title, date metadata. Requires its own chunking strategy (prose, not verses) and reference format ("Elder X, Title, Conference Month Year").
5. **Manuals and institute materials**: Pedagogical content with lesson structure.
6. **Commentaries and scholarly works**: The layer that unlocks Layer 3 thematic connections in the KG.
7. **Chat client UI**: The final product — a specialized RAG-based chat for scripture/gospel study.

## Citation Standards (All Material Types)

- **Scriptures**: Literal quotes with verse references — "text" (1 Nephi 3:7). Inline or block style.
- **Conference talks**: Author, "Title", Conference Month Year — "quote" (Elder X, "Title", Oct 2023)
- **Manuals/other**: Author, Title, source — as available from metadata
- **Critical rule**: Never paraphrase and present as direct quote. Never invent text. References must be verifiable.

## Architecture Principle

Each material type has its own problematics:
- **Scriptures**: verse-aware chunking, verse-level references, structural metadata (volume/book/chapter/verse)
- **Conference talks**: prose chunking with overlap, author/title/date metadata
- **Manuals**: lesson/chapter structure, pedagogical context
- **Web/articles**: HTML parsing, section structure

The pipeline discriminates by material type and applies the appropriate strategy. The `is_scripture()` / `_extract_source()` pattern is the model for future material-type handlers.
