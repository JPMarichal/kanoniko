# P8 — Synthesis Engine — Requirements

## Problem Statement

The current system answers questions but cannot produce structured knowledge artifacts. The vision is a 4th architectural layer (corpus → index → knowledge → **synthesis**) that generates discourses, T-charts, timelines, concept maps, articles, and comparative analyses from the accumulated knowledge.

## Functional Requirements

### FR-1: Discourse Generation
Given a topic and parameters (length, audience, tone), generate a structured discourse/talk with scripture citations grounded in the corpus.

### FR-2: T-Charts / Comparisons
Given two or more concepts or entities, produce a structured comparison table with dimensions drawn from the corpus. Example: "Compare the ministries of Peter and Paul."

### FR-3: Timelines
Given a person, event, or period, produce a chronological sequence of events with dates/references from the corpus. Example: "Timeline of Moses' life."

### FR-4: Concept Maps
Given a central concept, produce a structured map of related concepts, persons, events, and references. Example: "Concept map of the Atonement."

### FR-5: Study Articles
Given a topic, produce a well-structured study article with sections, citations, and cross-references. Example: "Article on the role of covenants in the Plan of Salvation."

### FR-6: Output Formats
All synthesis outputs should be available in:
- Structured JSON (for UI consumption)
- Markdown (for export/reading)
- Plain text

## Non-Functional Requirements

- Grounded: all claims must be traceable to corpus sources
- Cost-aware: use appropriate LLM tier (quality tier for synthesis)
- Cacheable: identical requests should return cached results

## Dependencies

- **P5 (Chat Client UI)**: UI to display synthesis artifacts
- **P6 (Advanced Relations)**: Richer graph data improves synthesis quality

## Out of Scope

- Audio/video generation
- Slide deck generation
- Real-time collaborative editing
