# P6 — Advanced Relations — Requirements

## Problem Statement

The current knowledge graph uses only co-occurrence-based relations (`RELATED_TO`, `EXISTS_DURING`, `MENTIONED_IN`). These are noisy and semantically flat — "Moses RELATED_TO Red Sea" doesn't capture that Moses *parted* the Red Sea. The graph needs typed, meaningful relationships.

## Functional Requirements

### FR-1: Typed Relations
Replace or supplement co-occurrence with semantically typed relations:

| Relation | Example |
|----------|---------|
| `FATHER_OF` | Abraham → Isaac |
| `MOTHER_OF` | Mary → Jesus |
| `BROTHER_OF` | Moses → Aaron |
| `SPOUSE_OF` | Adam → Eve |
| `SUCCESSOR_OF` | Joshua → Moses (as leader) |
| `PROPHESIED_ABOUT` | Isaiah → Christ |
| `TRAVELED_TO` | Paul → Rome |
| `FOUNDED` | Nephi → Nephite civilization |
| `TAUGHT` | Christ → Sermon on the Mount |
| `FULFILLED_BY` | Prophecy → Event |

### FR-2: Three Layers of Scripture Parallelism
Encode the three parallelism layers from `cross_references.py` into the graph:
1. **Direct parallels**: Same event narrated in different books (e.g., Creation in Genesis, Moses, Abraham)
2. **Editorial parallels**: Same period from different perspectives (e.g., Four Gospels, Kings/Chronicles)
3. **Thematic connections**: Same doctrine across volumes (e.g., Atonement in Isaiah, Alma, D&C)

### FR-3: NER → Gazetteer Feedback Loop
Entities discovered by spaCy NER that appear frequently should be candidates for gazetteer inclusion. The system should:
- Track NER-discovered entities and their frequency
- Surface top candidates for gazetteer addition
- Provide an API/CLI to promote NER entities to gazetteer entries

### FR-4: Relation Extraction via LLM
Use LLM (fast tier) to extract typed relations from key passages, similar to how profile generation works.

### FR-5: Temporal Relations
Link events and persons to time periods with more precision than the current `EXISTS_DURING`:
- `BORN_IN` period, `DIED_IN` period
- `REIGNED_DURING` period
- `OCCURRED_DURING` period

## Non-Functional Requirements

- Backward compatible — existing `RELATED_TO` relations remain functional
- Incremental — new relation types can be added without rebuilding the entire graph
- LLM costs manageable — batch extraction with fast tier

## Dependencies

- **P1 (Scripture Structure)**: Pericope awareness improves relation extraction context

## Out of Scope

- Visual graph exploration UI (covered by P5)
- Full temporal database (just period linkage)
