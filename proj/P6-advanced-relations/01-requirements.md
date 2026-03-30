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

### FR-9: Scripture Hierarchy (Canon Structure as Graph)
Model the canonical structure as a navigable graph, supporting both the **short chain** (common reference) and the **long chain** (full editorial structure):

**Short chain:** Volume → Book → Chapter → Verse
```
(Old Testament)-[:CONTAINS]->(Psalms)-[:CONTAINS]->(Psalms 73)-[:CONTAINS]->(Psalms 73:1)
```

**Long chain:** Volume → Division → Book → Part → Chapter → Pericope → Verse
```
(Old Testament)-[:CONTAINS]->(Poetry & Wisdom)-[:CONTAINS]->(Psalms)-[:CONTAINS]->(Book III)-[:CONTAINS]->(Psalms 73)-[:CONTAINS]->(vv. 1-12 "The prosperity of the wicked")-[:CONTAINS]->(Psalms 73:1)
```

**Node types:**
| Node | Examples |
|------|----------|
| `Volume` | Old Testament, New Testament, Book of Mormon, D&C, Pearl of Great Price |
| `Division` | Pentateuch, Poetry & Wisdom, Major Prophets; Gospels, Pauline Epistles; Small Plates, Large Plates |
| `Book` | Genesis, Psalms, 1 Nephi, D&C, Moses |
| `Part` | Book I–V of Psalms, "Record of Zeniff" (Mosiah 9–22), "Words of Alma" (Alma 5–44) |
| `Chapter` | Genesis 1, Psalms 73, D&C 76 |
| `Pericope` | "The Beatitudes" (Matt 5:3-12), "Alma on faith" (Alma 32:26-43) |
| `Verse` | Already exists as `ScriptureVerse` |

**Relations:**
- `CONTAINS` / `PART_OF` — hierarchical containment (bidirectional navigation)
- `NEXT` / `PREVIOUS` — sequential ordering within the same level (chapter→chapter, verse→verse)

**Properties on hierarchy nodes:**
- `source_url` — Official Church site URL (from `.meta.json`, both languages)
- `summary` — Chapter summary (from `.meta.json`)
- `study_intro` — Historical/editorial context (D&C, PGP, BofM sections)
- `subtitle` — Book subtitle or date (PGP, BofM ch1, 1-2 Samuel, 1-2 Kings)
- `section_headings` — Superscriptions and pericope markers
- `lang` — Language code for language-specific properties

**Motivating use cases:**
- "¿Cuáles son las epístolas paulinas?" — Traverse Division→Book under "Pauline Epistles"
- "¿Qué libros componen las Planchas Menores?" — Traverse Division→Book under "Small Plates"
- "Siguiente capítulo" — Follow `NEXT` relation from current Chapter node
- "¿A qué parte del Libro de Mormón pertenece el registro de Zeniff?" — Traverse Chapter→Part

### FR-10: Metadata-Derived Relations
Extract structured relations from `.meta.json` fields that are already scraped, without requiring LLM or NER — pure parsing of curated editorial content.

**From `study_intro` (D&C — 140 sections, PGP, BofM):**
- `REVEALED_TO`: Section → Person — "Revelation given to Joseph Smith..."
- `REVEALED_AT`: Section → Place — "...in Hiram, Ohio"
- `REVEALED_ON`: Section → Date — "...on November 1, 1831"
- `OCCASIONED_BY`: Section → Event/Context — "during a special conference of elders"

D&C study_intro is structured prose with consistent patterns across 140 sections — highly parseable with regex + lightweight LLM fallback.

**From `summary` (all 1,587 chapters × 2 languages):**
- `CHAPTER_TEACHES`: Chapter → Concept — summaries are the most concentrated source of chapter-level topics
- Feeds FR-7 (didactic relations): summaries state what a chapter is *about*, which is exactly what `DEFINES`/`ILLUSTRATES` needs for Forma T
- More precise than running NER over full chapter text

**From `section_headings` (Psalms, BofM, OD 1):**
- `AUTHORED`: Chapter → Person — Psalm superscriptions ("A Psalm of David", "Salmo de Asaf")
- BofM book prefaces — dense entity mentions for entity linking

**From `subtitle` (PGP, BofM ch1, 1-2 Samuel, 1-2 Kings):**
- `WRITTEN_DURING`: Chapter → Period — PGP subtitles are dates ("June 1830", "Junio de 1830")
- `DESCRIBED_AS`: Book → Description — BofM subtitles ("His Reign and Ministry")

**Motivating use cases:**
- "¿Cuándo fue revelada DyC 76?" — Query `REVEALED_ON` from Section 76
- "¿Qué secciones fueron dadas en Kirtland?" — Query `REVEALED_AT` filtered by place
- "¿Qué capítulos enseñan sobre la fe?" — Query `CHAPTER_TEACHES` → "faith"/"fe"
- "¿Cuándo se escribió Moisés 1?" — Query `WRITTEN_DURING` from subtitle "(June 1830)"

### FR-11: Extended Relation Taxonomy

The core typed relations in FR-1 cover family and authorship. This FR extends the taxonomy to cover the full range of scriptural relationships — from Sunday School basics to scholarly analysis — organized by domain.

#### 11a. Citations and Intertextuality

| Relation | Example | Properties |
|----------|---------|------------|
| `QUOTES` | Paul quotes Isaiah; Jesus quotes Deuteronomy; Nephi quotes Isaiah | `source_ref`, `target_ref`, `verbatim` (boolean: textual vs paraphrase) |
| `ALLUDES_TO` | Hebrews alludes to Melchizedek narrative; Revelation alludes to Daniel | `source_ref`, `target_ref`, `confidence` |
| `JST_OF` | JST Genesis 14 → KJV Genesis 14 | `verse_range`, `change_type` (addition, clarification, restoration) |

**JST (Joseph Smith Translation):** A distinctive LDS resource. Where JST variants exist, model the relationship between KJV and JST text. Properties indicate the nature of the change: added material, clarified meaning, or restored lost content. Cross-reference with the JST appendix in LDS scriptures.

**Motivating use cases:**
- "¿Dónde cita Pablo a Isaías?" — Traverse `QUOTES` from Paul filtered to Isaiah
- "¿Qué pasajes del AT cita Jesús?" — All `QUOTES` from Jesus to OT books
- "¿En qué difiere la TJS de Génesis 14?" — Traverse `JST_OF` with change details
- "Muéstrame todas las citas de Isaías en el Libro de Mormón" — `QUOTES` from BofM books to Isaiah, with parallel text display

#### 11b. Typology, Symbolism, and Prophecy

| Relation | Example | Properties |
|----------|---------|------------|
| `TYPE_OF` | Melchizedek → Christ; Isaac's sacrifice → Atonement; Moses' serpent → Crucifixion | `source_ref`, `typological_aspect` |
| `ANTITYPE_OF` | Christ → Paschal Lamb (fulfillment of the type) | `source_ref` |
| `SYMBOLIZES` | Olive tree → House of Israel; bread → body of Christ; water → living water; veil → separation from God | `source_ref`, `context` |
| `PROPHECY_OF` | Isaiah 7:14 → Virgin birth; 1 Nephi 13 → Columbus/Americas | `source_ref`, `fulfillment_ref`, `status` (fulfilled, pending, dual) |
| `FULFILLED_BY` | Prophecy → Event/Person (already in FR-1, extended here) | `partial` (boolean: dual fulfillment) |
| `DUAL_FULFILLMENT` | Isaiah 7:14 → Maher-shalal-hash-baz (immediate) + Christ (ultimate) | `immediate_ref`, `ultimate_ref` |

**Dual fulfillment** is critical in LDS hermeneutics — many OT prophecies have both a near and a far fulfillment. Isaiah is the primary case, but Daniel, Ezekiel, and Joel also exhibit this pattern extensively.

**Motivating use cases:**
- "¿Cómo es Melquisedec tipo de Cristo?" — Traverse `TYPE_OF` with `typological_aspect` listing parallels
- "¿Qué profecías de Isaías se cumplieron en Cristo?" — `PROPHECY_OF` filtered by fulfillment in NT
- "¿Qué simboliza el olivo en Jacob 5?" — `SYMBOLIZES` from olive tree with source in Jacob 5

#### 11c. Extended Genealogy and Lineage

| Relation | Example | Properties |
|----------|---------|------------|
| `DESCENDANT_OF` | Jesus → David → Abraham (transitive, avoids full chain traversal) | `generations` (count or "many") |
| `ANCESTOR_OF` | Abraham → Jesus | `generations` |
| `TRIBE_OF` | Paul → Benjamin; Jesus → Judah | `source_ref` |
| `LINEAGE_OF` | Jesus → Davidic line; Aaron → Aaronic/Levitical | `lineage_type` (royal, priestly, prophetic) |
| `ADOPTED_BY` | Moses → Pharaoh's daughter; Esther → Mordecai | `source_ref` |

**Motivating use cases:**
- "¿De qué tribu era Pablo?" — Direct `TRIBE_OF` lookup
- "¿Quiénes son los descendientes de Abraham en las escrituras?" — Traverse `DESCENDANT_OF`
- "Línea de sucesión desde David hasta Cristo" — Chain `FATHER_OF` or `DESCENDANT_OF` with `lineage_type=royal`

#### 11d. Covenants and Laws

| Relation | Example | Properties |
|----------|---------|------------|
| `COVENANT_WITH` | God → Abraham; God → Israel at Sinai; God → Lehi | `covenant_type` (Abrahamic, Mosaic, new/everlasting), `condition`, `promise`, `sign` (circumcision, baptism, sacrament) |
| `RENEWED_BY` | Abrahamic covenant → renewed through Isaac → Jacob → Joseph Smith | `source_ref`, `dispensation` |
| `COMMANDED` | God → "Thou shalt not kill"; God → "Build an ark" | `recipient`, `source_ref`, `context` |
| `OBEYED` | Abraham → sacrifice of Isaac; Nephi → obtain plates | `source_ref` |
| `DISOBEYED` | Jonah → go to Nineveh; Saul → destroy Amalekites completely | `source_ref`, `consequence` |
| `SUPERSEDED_BY` | Law of Moses → Law of the Gospel; animal sacrifice → sacrament | `source_ref`, `transition_event` |
| `GOVERNED_BY` | Israel → Law of Moses; Church → Word of Wisdom | `period_start`, `period_end` |

**LDS covenant theology** distinguishes between the covenant *path* (individual ordinances: baptism, confirmation, endowment, sealing) and the covenant *relationship* (God's promises to peoples/nations). Both should be modeled.

**Motivating use cases:**
- "¿Cuál es el convenio abrahámico y cómo se renueva?" — Traverse `COVENANT_WITH` + `RENEWED_BY` chain
- "¿Qué mandamientos desobedeció Saúl?" — `DISOBEYED` from Saul
- "¿Qué reemplazó la ley de Moisés?" — `SUPERSEDED_BY` from Law of Moses

#### 11e. Priesthood, Ordinances, and Keys

| Relation | Example | Properties |
|----------|---------|------------|
| `ORDAINED_BY` | Aaron ordained by Moses; Twelve ordained by Christ | `office`, `source_ref` |
| `BAPTIZED_BY` | Jesus → John the Baptist; Alma baptizes at waters of Mormon | `source_ref`, `location` |
| `CONFIRMED_BY` | Laying on of hands for the Holy Ghost | `source_ref` |
| `SEALED_BY` | Elijah's sealing power; temple ordinances | `source_ref`, `ordinance_type` |
| `HOLDS_PRIESTHOOD` | Aaron → Aaronic; Melchizedek → Melchizedek | `order`, `source_ref` |
| `KEYBEARER_OF` | Peter → keys of the kingdom; Elijah → sealing keys; Moses → gathering of Israel | `keys`, `source_ref`, `conferred_to` |
| `CONFERRED_KEYS_TO` | Peter/James/John → Joseph Smith; Moses → Joseph Smith (D&C 110) | `keys`, `source_ref`, `date` |
| `PERFORMED_ORDINANCE` | Alma → baptism; Moroni → sacrament prayers | `ordinance_type`, `source_ref` |

**LDS priesthood theology** is highly structured: two orders, specific offices, keys associated with individuals and dispensations. The restoration narrative in D&C 13, 20, 27, 84, 107, 110, 128 provides precise source references for every priesthood event.

**Motivating use cases:**
- "¿Quién restauró el sacerdocio aarónico?" — `CONFERRED_KEYS_TO` with `keys=Aaronic priesthood`
- "¿Qué llaves se restauraron en el templo de Kirtland?" — `CONFERRED_KEYS_TO` filtered by D&C 110
- "¿Quién bautizó a quién en el Libro de Mormón?" — Traverse `BAPTIZED_BY` in BofM

#### 11f. Milagros, Visiones, and Señales

| Relation | Example | Properties |
|----------|---------|------------|
| `PERFORMED` | Moses → parting Red Sea; Jesus → raising Lazarus; Nephi → struck his brothers | `miracle_type`, `source_ref` |
| `WITNESSED` | Three Witnesses → gold plates; shepherds → angelic announcement | `source_ref`, `nature` (physical, visionary) |
| `SAW_IN_VISION` | Lehi → tree of life; John → new Jerusalem; Joseph Smith → Father and Son | `source_ref`, `vision_content` |
| `APPEARED_TO` | Christ → Nephites; Moroni → Joseph Smith; Angel → Alma the Younger | `source_ref`, `nature` (corporeal, visionary, angelic) |
| `TRANSLATED` | Enoch → city of Enoch; Three Nephites; Moses (disputed); Elijah | `source_ref` |

**Motivating use cases:**
- "¿Qué milagros hizo Eliseo?" — `PERFORMED` from Elisha
- "¿Quiénes vieron a Cristo resucitado?" — `APPEARED_TO` from Christ post-resurrection
- "¿Qué vio Lehi en su visión del árbol de la vida?" — `SAW_IN_VISION` from Lehi + vision content
- "¿Qué personas fueron trasladadas?" — All `TRANSLATED` relations

#### 11g. Discursos and Enseñanza

| Relation | Example | Properties |
|----------|---------|------------|
| `SPOKE_TO` | Jesus → Pharisees; Abinadi → King Noah; Samuel the Lamanite → Nephites | `source_ref`, `context` (confrontation, teaching, warning) |
| `DISCOURSE_ABOUT` | Sermon on the Mount → Beatitudes; Alma 32 → faith; King Benjamin's speech → service | `source_ref`, `verse_range` |
| `RECORDED_BY` | King Benjamin's speech → scribes; Jesus's words → Matthew/Mark/Luke/John | `source_ref` |
| `ADDRESSED_TO` | Epistle → recipient (Romans → church at Rome; Moroni 9 → Moroni from Mormon) | `source_ref` |

#### 11h. Military, Political, and Social Relations

| Relation | Example | Properties |
|----------|---------|------------|
| `CONQUERED` | Nebuchadnezzar → Jerusalem; Lamanites → Zarahemla | `source_ref`, `date` |
| `ALLIED_WITH` | Israel → Judah (at times); Nephites → people of Ammon | `period_start`, `period_end` |
| `CAPTIVE_OF` | Israel → Babylon; people of Limhi → Lamanites | `source_ref`, `period` |
| `REBELLED_AGAINST` | Korah → Moses; Amalickiah → Moroni; Lucifer → God | `source_ref`, `outcome` |
| `JUDGED` | Deborah judged Israel; Alma the Younger as chief judge | `source_ref`, `office` (judge, king, governor) |
| `RULED_OVER` | Solomon → United Kingdom; Mosiah → Zarahemla | `period_start`, `period_end` |
| `LED_ARMY` | Joshua; Captain Moroni; Gideon | `source_ref`, `campaign` |

#### 11i. Conversion, Repentance, and Spiritual Transformation

| Relation | Example | Properties |
|----------|---------|------------|
| `CONVERTED_BY` | Alma → angelic visitation; Paul → Damascus road; King Lamoni → Ammon's teaching | `source_ref`, `agent` (person, event, experience) |
| `REPENTED_OF` | David → Bathsheba; Nineveh → wickedness; Alma → persecuting church | `source_ref`, `outcome` |
| `FELL_AWAY` | Judas → betrayal; Sherem → anti-Christ; Korihor → anti-Christ | `source_ref`, `nature` |
| `RETURNED_TO` | Prodigal son → father; Alma → the faith | `source_ref` |

### FR-12: LDS Dispensational and Restoration Theology

Relations unique to Latter-day Saint theology, not found in standard Bible study tools. These distinguish Alejandría from Logos/BibleHub and serve the core user base.

#### 12a. Dispensations and Restoration

| Relation | Example | Properties |
|----------|---------|------------|
| `DISPENSATION_HEAD` | Adam, Enoch, Noah, Abraham, Moses, Christ, Joseph Smith | `dispensation_name`, `source_ref` |
| `RESTORED` | Joseph Smith → baptism; Elijah → sealing keys; Peter/James/John → Melchizedek priesthood | `what_restored`, `source_ref`, `date` |
| `APOSTASY_IN` | Great Apostasy → after Christ's apostles; Nephite apostasy → 4 Nephi | `source_ref`, `period` |
| `DISPENSATION_OF` | Doctrine/Ordinance → Dispensation — tracks when a truth was available | `first_revealed`, `lost_during`, `restored_in` |

#### 12b. Plan of Salvation

| Relation | Example | Properties |
|----------|---------|------------|
| `STAGE_OF` | Pre-mortal existence, Mortal life, Spirit world, Resurrection, Judgment → Plan of Salvation | `order`, `source_ref` |
| `TEACHES_ABOUT` | Alma 40 → Spirit world; D&C 76 → Degrees of glory; Abraham 3 → Pre-mortal life | `source_ref` |
| `DEGREE_OF_GLORY` | Celestial, Terrestrial, Telestial → described in D&C 76 | `requirements`, `description`, `source_ref` |

#### 12c. Temple and Sacred Ordinances

| Relation | Example | Properties |
|----------|---------|------------|
| `PREFIGURED_BY` | Temple endowment → Mosaic tabernacle rituals; sealing → Elijah's promise | `source_ref` |
| `TEMPLE_AT` | Solomon's Temple → Jerusalem; Kirtland Temple → Kirtland; Nephite Temple → Bountiful | `period`, `source_ref` |
| `ORDINANCE_FOR_DEAD` | Baptism for the dead → D&C 128; 1 Cor 15:29 | `source_ref`, `doctrinal_basis` |

#### 12d. Book of Mormon Specific

| Relation | Example | Properties |
|----------|---------|------------|
| `RECORD_KEPT_BY` | Small plates → Nephi through Amaleki; Large plates → Nephi through Mormon | `plate_set`, `period` |
| `ABRIDGED_BY` | Mormon → Mosiah through 3 Nephi; Moroni → Ether | `source_record`, `source_ref` |
| `LOST_MANUSCRIPT` | 116 pages → Martin Harris; D&C 10 explains non-retranslation | `source_ref` |
| `WITNESS_OF` | Three Witnesses → gold plates; Eight Witnesses → gold plates | `witness_type` (spiritual, physical), `source_ref` |
| `HEBRAISM_IN` | Chiasmus → Alma 36; cognate accusative → "dreamed a dream" | `literary_device`, `source_ref` |
| `COLOPHON_IN` | "I, Nephi, having been born..." → 1 Nephi 1:1; "I, Mormon, make a record..." → 3 Nephi 5:8 | `source_ref` |

#### 12e. Pearl of Great Price Specific

| Relation | Example | Properties |
|----------|---------|------------|
| `COUNCIL_PARTICIPANT` | Jehovah, Michael, Lucifer → Council in Heaven (Abraham 3) | `role` (chosen, rejected), `source_ref` |
| `WAR_IN_HEAVEN` | Michael → led hosts; Lucifer → cast out | `role`, `source_ref` |
| `FACSIMILE_DEPICTS` | Facsimile 1 → Abraham on altar; Facsimile 2 → Kolob | `figure_num`, `interpretation`, `source_ref` |

### FR-13: Literary and Linguistic Analysis

Relations supporting scholarly scripture study — structural, linguistic, and text-critical analysis comparable to academic tools.

#### 13a. Literary Structure

| Relation | Example | Properties |
|----------|---------|------------|
| `CHIASM_IN` | Alma 36; Mosiah 3:18-19; many Isaiah passages | `center_point`, `verse_range`, `confidence` |
| `INCLUSIO_IN` | Psalm 8 (opens and closes with "O LORD our Lord") | `framing_phrase`, `verse_range` |
| `PARALLELISM_IN` | Synonymous, antithetic, synthetic, climactic | `parallelism_type`, `verse_range`, `source_ref` |
| `ACROSTIC_IN` | Psalm 119 (each stanza begins with successive Hebrew letter); Proverbs 31:10-31 | `structure`, `verse_range` |
| `GENRE_OF` | Chapter/Book → Genre | `genre` (narrative, poetry, law, prophecy, apocalyptic, epistle, wisdom, psalm, lament, parable, genealogy, oracle) |

#### 13b. Linguistic Relations

| Relation | Example | Properties |
|----------|---------|------------|
| `TRANSLATES_AS` | Mashiach → Cristo → Ungido; Elohim → Gods/Dios; Ruach → Spirit/Espíritu | `source_lang`, `target_lang`, `semantic_range` |
| `DERIVED_FROM` | Christ → Christos → Mashiach | `etymology` |
| `WORD_STUDY` | "hesed" (lovingkindness/mercy/covenant love) → used 248 times in OT | `frequency`, `semantic_range`, `key_passages` |
| `HAPAX_LEGOMENON` | Word appearing only once in the corpus | `source_ref`, `proposed_meaning` |
| `COGNATE_OF` | Hebrew ברא (bara) → Arabic برأ (bara'a) | `language`, `significance` |

**Strong's-like capability:** While we don't have original-language texts, the `TRANSLATES_AS` and `WORD_STUDY` relations enable a basic concordance-like experience. Key Hebrew/Greek terms can be linked to every passage where they appear, with semantic range notes — similar to what BibleHub's interlinear provides.

#### 13c. Text-Critical and Source Relations

| Relation | Example | Properties |
|----------|---------|------------|
| `VARIANT_OF` | KJV reading → JST reading → critical text reading | `variant_type`, `manuscripts`, `preferred` |
| `POSSIBLE_SOURCE` | 2 Nephi 12-24 ← Isaiah 2-14; Moroni 7 ← possible sermon source | `dependency_type` (quotation, allusion, shared source), `confidence` |
| `EDITORIAL_NOTE` | "And thus we see..." passages in Alma → Mormon's editorial voice | `editor`, `source_ref`, `note_type` (summary, theological comment, transition) |
| `INTERPOLATION` | Suspected later insertions or editorial additions | `evidence`, `scholarly_consensus`, `source_ref` |

#### 13d. Cross-Reference Networks (Treasury of Scripture Knowledge style)

| Relation | Example | Properties |
|----------|---------|------------|
| `SEE_ALSO` | Topical Guide entry → multiple passages | `topic`, `relevance` |
| `COMPARE` | "Compare with 2 Nephi 17" (footnote in Isaiah 7) | `source_ref`, `target_ref`, `comparison_type` |
| `BIBLE_DICTIONARY_ENTRY` | Entity → BD article | `article_name`, `key_facts` |

### FR-14: Extraction Quality, Model Strategy, and Performance

Define the quality framework governing how relations are extracted, verified, stored, and served — ensuring precision at scale without unbounded LLM costs.

#### 14a. Confidence Levels and Provenance

Every relation carries:
- `confidence` — `curated` (human-verified seed data), `metadata` (parsed from `.meta.json`), `llm_high` (LLM with strong textual evidence), `llm_low` (LLM inference), `ner` (auto-discovered, unverified)
- `source` — How the relation was extracted: `seed`, `metadata_parse`, `llm_extract`, `ner_cooccurrence`, `cross_ref`
- `source_ref` — The passage that supports the relation (empty for co-occurrence)
- `verified` — Boolean, initially false for LLM/NER extractions; true for curated and metadata

**Query behavior:** Consumers can filter by confidence. RAG uses all levels but weights `curated` > `metadata` > `llm_high` > `llm_low` > `ner`. The chat endpoint may show confidence indicators to the user.

#### 14b. Model Tier Strategy

Extraction tasks vary in complexity. Assign each to the cheapest model tier that achieves acceptable precision:

| Task | Model Tier | Rationale |
|------|-----------|-----------|
| Metadata parsing (study_intro, superscriptions) | **None (regex)** | Structured text, deterministic patterns |
| Genealogy from curated data | **None (seed file)** | Human-curated, highest precision |
| Entity attribute extraction (titles, roles) | **Fast** (Haiku) | Short passages, constrained output schema |
| Typed relation extraction (family, travel, military) | **Fast** (Haiku) | Pattern recognition over 1-2 paragraphs |
| Typological/symbolic relations | **Balanced** (Sonnet) | Requires theological reasoning |
| Discourse analysis, chiastic structures | **Balanced** (Sonnet) | Structural pattern recognition over larger spans |
| Complex intertextuality (quotes, allusions) | **Balanced** (Sonnet) | Cross-book comparison |
| Dual fulfillment classification | **Quality** (Opus) | Requires nuanced theological judgment |
| Verification of LLM-extracted relations | **Fast** (Haiku) | Binary yes/no with source passage |

**Cost control:**
- Batch extraction: process top entities/passages first (by mention count), diminishing returns after ~500
- Cache LLM results: store raw extraction output for re-processing without re-calling
- Two-pass strategy: Fast tier extracts candidates, Balanced/Quality tier verifies ambiguous cases only

#### 14c. Token Optimization

- **Input compression:** Send only the relevant verse range + entity context to the LLM, not entire chapters. For a 30-verse chapter, extract relations per pericope (5-10 verses) with entity pre-identification from gazetteer
- **Output schema:** Use structured JSON output with constrained field names to minimize output tokens. Example: `{"r": "FATHER_OF", "from": "Abraham", "to": "Isaac", "ref": "Gen 21:3", "c": "curated"}` — ~50 tokens vs 200+ for natural language
- **Batch prompts:** Group multiple passages in a single prompt when extracting the same relation type (e.g., all Psalm superscriptions in one call)
- **Incremental extraction:** Only process new/modified chunks (SHA-256 change detection already exists in ingestion pipeline)

#### 14d. Graph Performance

- **Indexing:** Composite indexes on `(node_type, name)`, `(relation_type, confidence)`, `(source_ref)` for fast filtered traversals
- **Materialized paths:** For frequent traversals (ancestor chains, covenant chains, dispensation sequences), store pre-computed path summaries as relation properties to avoid deep recursive queries at query time
- **Relation count management:** With 50+ relation types and 30,000+ nodes, total edge count may reach 500K–1M. Neo4j handles this well, but query patterns should use directed traversals with depth limits, not unbounded `MATCH` patterns
- **Bilingual deduplication:** Relations extracted from EN and ES text for the same entity pair should be merged, not duplicated. Keep both `source_ref` values (EN and ES) on a single relation edge

#### 14e. Precision over Recall

For a scripture study tool, **false relations are worse than missing ones** — a wrong `FATHER_OF` link is more damaging than a missing one. Design principles:

- Prefer curated seed data over LLM extraction for high-stakes relations (genealogy, priesthood, covenant)
- Require `source_ref` for every non-co-occurrence relation — if the LLM cannot cite a passage, the relation is not stored
- Two-source rule for controversial relations: require evidence from at least two independent passages before storing at `llm_high` confidence
- Never store relations that contradict curated data — if LLM says X is father of Y but seed data says Z is father of Y, flag for human review rather than overwriting
- Human review queue for relations with `llm_low` confidence on theologically sensitive topics (typology, dispensational claims, priesthood lineage)

## Non-Functional Requirements

- Backward compatible — existing `RELATED_TO` relations remain functional
- Incremental — new relation types can be added without rebuilding the entire graph
- LLM costs manageable — batch extraction with tiered model assignment (FR-14b)
- Bilingual — relations are language-neutral; properties carry both EN and ES source refs
- Auditable — every relation carries provenance (`source`, `confidence`, `source_ref`)
- Precision-first — false relations are worse than missing ones (FR-14e)

## Dependencies

- **P1 (Scripture Structure)**: Pericope awareness improves relation extraction context
- **P2 (Scripture Corpus)**: `.meta.json` fields (`study_intro`, `subtitle`, `section_headings`, `source_url`) are the data source for FR-9 and FR-10

## Out of Scope

- Visual graph exploration UI (covered by P5)
- Map rendering UI — FR-6 provides the data (coordinates, routes); visualization is a consumer concern
- Full temporal database with absolute dating (approximate periods and relative ordering suffice)
- Archaeological precision — coordinates are approximate, sufficient for study maps, not academic cartography
- Original-language text hosting (Hebrew, Greek, Reformed Egyptian) — we model linguistic relations via `TRANSLATES_AS` but do not store source-language corpora
- Automated scholarly consensus tracking — `INTERPOLATION` and `VARIANT_OF` are populated from curated sources, not auto-detected
