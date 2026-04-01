---
name: Knowledge generation vision
description: Core vision — knowledge engine as foundation for ANY synthesis product (discourses, T-charts, timelines, concept maps, articles, chronologies), not just search or glossaries. Disambiguation and entity profiles are the critical middle layer.
type: project
---

## The Real Product: A Knowledge Engine for Unlimited Synthesis

The system is NOT a search engine with some extra features. It's a **knowledge engine** that enables ANY form of scripture study synthesis. The user should be able to ask for:

- A discourse on leadership lessons from Joshua and Moses
- A T-chart (concept | reference) on baptism by immersion
- A concept map on any doctrinal topic
- A chronology of Joseph of Egypt's life with ages at each event
- A timeline of Jesus's life up to age 12
- A blog article on the meanings of the number 40 in scripture
- A comparative analysis of the Nephite monetary system vs the NT
- A "Who's Who" dictionary for any book
- ...and anything else a scripture scholar might need

**Why:** The corpus contains all the raw material. What's missing is the structured, disambiguated, cross-referenced knowledge layer that lets an LLM synthesize ANY product on demand.

**How to apply:** NEVER design for specific output formats. Design the knowledge layer (entity profiles, relations, cross-references) to be queryable enough that ANY synthesis becomes possible. The chat RAG is just one consumer. A T-chart generator, a timeline builder, a discourse composer — all are different consumers of the same knowledge base.

## Architecture Implication

```
Layer 1: Corpus (raw text, bind-mounted)
Layer 2: Index (FTS + embeddings + KG — what we have now)
Layer 3: Knowledge (entity profiles, disambiguated relations, accumulated metadata)
Layer 4: Synthesis (LLM + templates that consume Layer 3 to produce any output)
```

Layer 3 is the critical missing piece. Without it, Layer 4 (any product) must re-derive everything from Layer 2 every time — slow, inconsistent, and limited by context windows.

## NER → Gazetteer Feedback Loop

The envisioned cycle:
1. Corpus → NER discovers new entities (auto-discovery)
2. Discovered entities feed back into gazetteer (auto-enrichment)
3. Enriched gazetteer improves next extraction pass
4. KG accumulates context per entity across all mentions
5. LLM disambiguates using accumulated context
6. Disambiguation generates metadata (bio, relations, references)
7. Metadata enriches gazetteer entries → cycle repeats

This transforms the gazetteer from a static input file into a **living, growing knowledge base**.

## Historical Name Changes

Entities change names over time in the text:
- Jerusalem = Salem (Gen 14:18) = Jebus (Judg 19:10) = City of David = Zion
- Jacob = Israel
- Babylon = Babel
- Saul = Paul, Simon = Peter = Cephas

These are **temporal SAME_AS relations** — the same referent with different names at different points in the narrative. Must be modeled in KG with temporal/contextual metadata.
