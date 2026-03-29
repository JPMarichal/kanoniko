# P7 — Deep Disambiguation — Requirements

## Problem Statement

The current disambiguation works at the entity profile level: "Judas" is split into 7 variants with distinct summaries. But at the passage level, the system doesn't know *which* Judas is mentioned in a specific verse. When Matthew 26:47 says "Judas, one of the twelve", the system registers a generic "Judas" mention rather than specifically "Judas Iscariot".

## Functional Requirements

### FR-1: Per-Mention Disambiguation
For each mention of an ambiguous entity in a chunk, determine which specific individual/place/concept is meant.

### FR-2: Contextual Clues
Use surrounding text to disambiguate:
- **Companions**: "Judas...one of the twelve" → Judas Iscariot
- **Location**: "Mary...at the feet of Jesus" in Bethany → Mary of Bethany
- **Time period**: "James" in Acts → James son of Zebedee (before Acts 12) or James brother of Jesus (after)
- **Modifiers**: "Judas Iscariot", "Judas surnamed Barsabas" → direct match

### FR-3: Disambiguation Confidence
Each resolved mention should carry a confidence score:
- **High**: Direct modifier present ("Judas Iscariot")
- **Medium**: Contextual clues strong (companions, location)
- **Low**: Ambiguous, multiple candidates possible

### FR-4: Graph Enrichment
Resolved mentions create specific entity-document links in Neo4j:
- Instead of: `Judas MENTIONED_IN Matthew 26` (generic)
- Produce: `Judas Iscariot MENTIONED_IN Matthew 26` (specific)

### FR-5: Profile Accuracy
Entity profiles should reflect disambiguated mention counts, not generic totals.

## Non-Functional Requirements

- Must handle the full corpus without excessive LLM costs
- Disambiguation rules should be data-driven where possible, LLM only for hard cases
- Backward compatible with existing generic mentions

## Dependencies

- None (builds on existing profile disambiguation)

## Out of Scope

- Cross-document coreference resolution ("he", "she", "the prophet")
- Historical identity debates (are James the brother of Jesus and James the Just the same person?)
