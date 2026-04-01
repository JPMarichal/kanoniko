# Knowledge Graph

Neo4j-based knowledge graph storing entities, relations, and document connections extracted from the corpus.

## Graph Model

### Node Types

| Label | Description | Examples |
|-------|-------------|---------|
| `Entity` | Named entity from corpus | Persons, places, concepts, etc. |
| `Document` | Source document (file) | `en/scriptures/nt/matthew/1.txt` |

Entity nodes have properties:
- `name`: Canonical entity name
- `type`: Entity type (see table below)
- `aliases`: Alternative names

### Entity Types

**Corpus entities (scripture, biographies, manuals):**

| Type | Description | Examples |
|------|-------------|---------|
| `person` | Individual people | Moses, Paul, Nephi |
| `place` | Geographic locations | Jerusalem, Mount Zion, Zarahemla |
| `concept` | Doctrinal/theological concepts | Faith, Covenant, Zion, Atonement |
| `people` | Peoples/groups/tribes | House of Israel, Nephites, Lamanites |
| `object` | Significant objects | Ark of the Covenant, Liahona, Urim and Thummim |
| `period` | Time periods | The last days, Millennium |

**Institutional entities (General Handbook):**

| Type | Description | Examples |
|------|-------------|---------|
| `organization` | Church organizations | Relief Society, Primary, Sunday School |
| `calling` | Ecclesiastical callings | Bishop, Stake President, EQ President |
| `council` | Governing/advisory councils | Ward Council, Bishopric, Stake Presidency |
| `ordinance` | Sacred ordinances | Baptism, Sacrament, Temple Endowment |
| `unit` | Organizational units | Ward, Stake, Branch, District |
| `program` | Church programs | Seminary, Come Follow Me, Welfare Program |
| `policy` | Key policies | Law of Chastity, Word of Wisdom, Law of Tithing |
| `document` | Reference documents | General Handbook, For the Strength of Youth |

### Relationship Types

**Core relations:**

| Relation | Description |
|----------|-------------|
| `MENTIONED_IN` | Entity → Document link |
| `RELATED_TO` | Co-occurrence between entities |
| `EXISTS_DURING` | Entity → Period temporal link |

**Scripture structure (P1 Phase 3):**

| Relation | Description |
|----------|-------------|
| `PART_OF` | Structural containment: Book → Division → Volume |

**Organizational (handbook):**

| Relation | Description |
|----------|-------------|
| `PRESIDES_OVER` | Calling → Organization/Unit |
| `COUNSELOR_TO` | Calling → Calling |
| `REPORTS_TO` | Calling → Calling |
| `MEMBER_OF` | Calling → Council |
| `ORGANIZED_UNDER` | Organization → Unit |
| `UNIT_CONTAINS` | Unit → Unit |

**Authority and ordinances:**

| Relation | Description |
|----------|-------------|
| `AUTHORIZED_TO_PERFORM` | Calling → Ordinance |
| `KEYS_FOR` | Calling → Ordinance/Authority |
| `PREREQUISITE_FOR` | Ordinance → Ordinance |
| `COVENANT_OF` | Ordinance → Concept |
| `GOVERNS_POLICY` | Policy → Ordinance/Process |

## Gazetteers

Curated entity dictionaries in `knowledge/gazetteers/entities.json`. Each entry has:
- `name`: Canonical name (English)
- `aliases`: Alternative names and spellings (including Spanish)

The gazetteer covers ~2,400+ terms across all entity types, with special attention to biblical persons, places, and LDS-specific entities.

## Multi-Alias Lookup

The lookup system supports multiple entities sharing the same alias:
- `"Mary"` → Mary (mother of Jesus) AND Mary (sister of Martha)
- `"Judas"` → Multiple Judas individuals

When an alias matches multiple entities, ALL are registered in the KG. The profile disambiguation system later separates them.

## Graph Statistics (typical)

After a full corpus indexing:
- ~75,000+ entity nodes (including 501 structural scripture nodes)
- ~7,000,000+ relationships
- ~19,700+ document nodes

## Key Classes

- `Neo4jClient` (`neo4j_client.py`): Graph driver wrapper
  - `merge_entity()`, `merge_document()`, `merge_relation()` — single-item ops
  - `batch_merge_entities()`, `batch_merge_documents()`, `batch_merge_relations()`, `batch_link_entities_to_document()` — batch ops (UNWIND)
  - `find_node()`, `get_neighbors()`, `graph_summary()`
  - `get_all_entity_mentions()` — Bulk entity data for profile building
  - `get_documents_for_entity()` — Documents mentioning an entity
  - `clear_all()` — Batched delete of all nodes/edges (for rebuild)
- `ScriptureStructure` (`scripture_structure.py`): Long-chain resolution (P1 Phase 3)
  - Volume → Division → Book → Part → Pericope hierarchy
  - `get_structural_entities()` / `get_structural_relations()` — 501 entities, 496 PART_OF relations

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST /search/graph/find` | Search entities by name |
| `POST /search/graph/neighbors` | Get entity connections |
| `GET /search/graph/summary` | Graph statistics |
| `GET /search/graph/docs/{name}` | Documents for an entity |
| `POST /index/rebuild-kg` | Full graph rebuild (~27 min with batching) |
