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
| `AUTHORED` | David → Psalm 23, Mormon → Book of Alma (as compiler) |
| `COMPILED_BY` | Mormon → 3 Nephi (editorial compilation, distinct from authorship) |
| `CONTINUED_BY` | Moroni → Book of Mormon (completed father's work) |

**Authorship properties:**
- `role` — `author`, `compiler`, `editor`, `continuator`, `scribe` (distinguishes Mormon as compiler from Nephi as author)
- `verse_range` — When authorship changes within a document (e.g., Omni: Omni wrote vv. 1-3, Amaron vv. 4-8, Chemish v. 9)
- `source_ref` — The passage where authorship is stated or transitions (e.g., "Yo, Quemis, lo poco que escribo...")

**Motivating use cases:**
- "¿Quiénes son los autores del libro de Omni?" — Query `AUTHORED` relations targeting Omni, ordered by `verse_range`
- "¿Cuáles salmos escribió Asaf?" — Query `AUTHORED` with source = Asaf, filtering to Psalms
- "¿Qué escribió Mormón vs. qué compiló?" — Distinguish `AUTHORED` (Mormon 1-7) from `COMPILED_BY` (Mosiah through 3 Nephi)
- "Separa lo escrito por Mormón de lo escrito por Moroni" — Query both persons' `AUTHORED`/`CONTINUED_BY` relations

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

### FR-5: Event Nodes and Temporal Relations
Model events as first-class nodes in the graph, linked to persons, places, and time:

**Event nodes** — New node type `event` representing discrete happenings:
- Examples: "Massacre of the Innocents", "Census of Quirinius", "Crossing the Red Sea"
- Properties: `name`, `description`, `approximate_date` (optional), `source_refs`

**Place-event relations:**
- `HAPPENED_AT`: Event → Place (e.g., Massacre of the Innocents → Bethlehem)
- `LOCATED_IN`: Place → Place hierarchy (e.g., Bethlehem → Judea)

**Temporal relations:**
- `BEFORE` / `AFTER`: Event → Event (explicit chronological ordering)
- `DURING`: Event → Period (e.g., Census → Reign of Augustus)
- `BORN_IN` / `DIED_IN`: Person → Period
- `REIGNED_DURING`: Person → Period
- `OCCURRED_DURING`: Event → Period

**Motivating use case:** "¿Qué sucedió primero, la matanza en Belén o el censo en Belén?" — Today the system retrieves Matthew 2 and Luke 2 passages and delegates chronological reasoning entirely to the LLM. With event nodes and `BEFORE`/`AFTER` relations, the graph itself can answer sequence questions structurally, without depending on LLM inference over raw text.

### FR-6: Geospatial Properties for Places
Enrich `place` nodes with coordinates and metadata to enable maps, routes, and spatial queries:

**Place node properties:**
- `latitude` / `longitude` — Approximate coordinates (modern or estimated ancient location)
- `place_type` — Taxonomy: `city`, `region`, `river`, `mountain`, `sea`, `desert`, `building` (temple, synagogue)
- `existence_period` — When the place was relevant (e.g., Zarahemla: ~200 BC–~400 AD)
- `aliases` — Time-aware name list: `[{name, lang, period_start, period_end}]` (replaces plain string aliases; includes modern names, e.g., Mesopotamia → Iraq)

**Spatial relations (time-aware):**

Containment and political belonging change over time. All spatial relations carry optional `period_start` and `period_end` properties to model this:

- `LOCATED_IN`: Place → Place (geographic containment: Haran → Paddan-Aram)
- `CAPITAL_OF`: Place → Place (political role: Samaria → Kingdom of Israel, ~930–~722 BC)
- `PROVINCE_OF` / `PART_OF`: Place → Place (administrative belonging: Samaria → Persian Empire, ~530–~330 BC)
- `NEAR`: Place → Place (geographic proximity, e.g., Bethany → Jerusalem)
- `BORDERS`: Place → Place (regions: Samaria borders Judea)

**Temporal properties on spatial relations:**
```
(Samaria)-[:CAPITAL_OF {period_start: "~930 BC", period_end: "~722 BC"}]->(Kingdom of Israel)
(Samaria)-[:PROVINCE_OF {period_start: "~530 BC", period_end: "~330 BC"}]->(Persian Empire)
(Samaria)-[:PROVINCE_OF {period_start: "~63 BC", period_end: "~6 AD"}]->(Roman Republic)
```

**Place name evolution:**

Places change names over time. Model via `RENAMED_TO` relations with period, or multiple alias entries with temporal validity:

| Place | Period | Name |
|-------|--------|------|
| Jerusalem | ~2000 BC | Salem |
| Jerusalem | ~1400 BC– | Jerusalem / Yerushalayim |
| Jerusalem | ~135 AD– | Aelia Capitolina |
| Samaria (city) | ~870 BC | Samaria / Shomron |
| Samaria (city) | ~27 BC– | Sebaste |

Implementation: `aliases` property on place nodes becomes a list of `{name, lang, period_start, period_end}` objects instead of plain strings.

**Motivating use cases:**
- "¿A qué reino pertenecía Samaria en tiempos de Eliseo?" — Query `CAPITAL_OF`/`PART_OF` filtered by period
- "¿Cómo se llamaba Jerusalén en tiempos de Abraham?" — Query time-aware aliases
- "Muéstrame cómo cambió el mapa político entre los reinos divididos y el periodo romano" — Two snapshots of `PART_OF`/`PROVINCE_OF` relations filtered by period

**Route reconstruction:**
Combine `TRAVELED_TO` (FR-1) with place coordinates and temporal ordering (FR-5) to reconstruct journeys:
- Paul's missionary journeys: Antioch → Cyprus → Perga → Iconium → ...
- Exodus route: Goshen → Red Sea → Sinai → Kadesh Barnea → ...
- Lehi's family: Jerusalem → Red Sea coast → Nahom → Bountiful → ...

Each leg is an ordered sequence of `TRAVELED_TO` relations with `order` property on the relationship, grouped by journey (e.g., `journey: "Paul's Second Missionary Journey"`).

**Motivating use cases:**
- "Muéstrame la ruta del éxodo en un mapa" — Query `TRAVELED_TO` chain for Moses, render coordinates as polyline
- "¿Qué ciudades visitó Pablo en Asia Menor?" — Spatial filter on place coordinates within region bounds
- "Cronología y geografía del ministerio de Cristo" — Combine FR-5 temporal ordering with FR-6 coordinates for an animated timeline-map

### FR-7: Didactic Relations (Forma T support)
Distinguish between passages that *mention* a concept and passages that *teach* it. This enables structured study reports (Forma T) where each row pairs a concept with its best teaching passage.

**New relations:**
- `DEFINES`: Passage → Concept — The passage provides a clear definition (e.g., Éter 12:6 defines faith)
- `ILLUSTRATES`: Passage → Concept — The passage illustrates the concept through narrative or example (e.g., Enós 1:4 illustrates fervent prayer)
- `CONTRASTS`: Concept → Concept — Two concepts are taught in opposition (e.g., works of the flesh vs fruit of the Spirit in Galatians 5)

**Relation properties:**
- `didactic_weight` — How clearly and directly the passage teaches the concept (high = quotable definition, low = tangential mention)
- `verse_range` — Specific verses within the chunk (e.g., "6-7" within Éter 12), not just the whole document

**Distinction from `MENTIONED_IN`:**
`MENTIONED_IN` means the entity name appears in the document. `DEFINES`/`ILLUSTRATES` mean the passage is a *good reference* for studying that concept — suitable for citation in a Forma T.

**Motivating use case:** "Genera una Forma T sobre la fe" — Query all concepts with `DEFINES`/`ILLUSTRATES` relations to "fe", rank by `didactic_weight`, order by a didactic sequence (definition → prerequisite → process → fruits), and pair each concept with its best verse range.

### FR-8: Entity Attributes and Titles (Passive Verification)
Capture descriptive attributes — titles, roles, offices, designations — as first-class relations in the graph, linked to their source documents. This enables **passive verification**: when a consumer queries an entity's neighbors, descriptive metadata surfaces automatically, reducing the risk of false categorical claims (e.g., "X is never called Y").

**New relations:**
- `HAS_TITLE`: Person → Title/Designation (e.g., Paul → Apostle, Moses → Prophet)
- `HAS_ROLE`: Person → Role (e.g., Paul → Pharisee, Paul → Tentmaker, Matthew → Tax Collector)
- `CALLED_BY_NAME`: Person → Name/Alias with context (e.g., Paul → Saul, Jacob → Israel, Peter → Cephas)

**Relation properties:**
- `source_ref` — The specific passage where the title/role is assigned (e.g., "Hechos 14:14", "Hechos 23:6")
- `attributed_by` — Who assigns the title: `narrator` (Luke calls him apostle), `self` (Paul claims apostleship), `divine` (God calls him "instrumento escogido"), `other` (Agrippa calls him...)
- `context` — Brief note when the attribution is conditional or disputed (e.g., "Paul defends his apostleship — questioned by some in Corinth")

**Distinction from aliases:**
Current entity aliases are flat strings for search matching. `HAS_TITLE` / `HAS_ROLE` are semantically richer: they carry provenance, attribution source, and document links — making them queryable and verifiable.

**Motivating use case:** "¿Es Pablo llamado apóstol en Hechos?" — Today this requires a text search and careful reading. With `HAS_TITLE` relations, the graph answers structurally:
```
(Paul)-[:HAS_TITLE {source_ref: "Hechos 14:4", attributed_by: "narrator"}]->(Apostle)
(Paul)-[:HAS_TITLE {source_ref: "Hechos 14:14", attributed_by: "narrator"}]->(Apostle)
```

**Broader value:** Any time an agent or RAG pipeline queries an entity's neighbors, titles and roles surface alongside family relations, places visited, and concepts taught — providing a richer, self-correcting context that reduces dependence on the LLM's parametric memory.

## Non-Functional Requirements

- Backward compatible — existing `RELATED_TO` relations remain functional
- Incremental — new relation types can be added without rebuilding the entire graph
- LLM costs manageable — batch extraction with fast tier

## Dependencies

- **P1 (Scripture Structure)**: Pericope awareness improves relation extraction context

## Out of Scope

- Visual graph exploration UI (covered by P5)
- Map rendering UI — FR-6 provides the data (coordinates, routes); visualization is a consumer concern
- Full temporal database with absolute dating (approximate periods and relative ordering suffice)
- Archaeological precision — coordinates are approximate, sufficient for study maps, not academic cartography
