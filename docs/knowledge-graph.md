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
- `type`: Entity type (person, place, concept, people, object, period)
- `aliases`: Alternative names

### Entity Types

| Type | Description | Examples |
|------|-------------|---------|
| `person` | Individual people | Moses, Paul, Nephi |
| `place` | Geographic locations | Jerusalem, Mount Zion, Zarahemla |
| `concept` | Doctrinal/theological concepts | Faith, Covenant, Zion, Atonement |
| `people` | Peoples/groups/tribes | House of Israel, Nephites, Lamanites |
| `object` | Significant objects | Ark of the Covenant, Liahona, Urim and Thummim |
| `period` | Time periods | The last days, Millennium |

### Relationship Types

| Relation | Description |
|----------|-------------|
| `MENTIONED_IN` | Entity → Document link |
| `RELATED_TO` | Co-occurrence between entities |
| `EXISTS_DURING` | Entity → Period temporal link |

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
- ~9,000+ entity nodes
- ~460,000+ relationships
- ~1,800+ document nodes

## Key Classes

- `Neo4jClient` (`neo4j_client.py`): Graph driver wrapper
  - `merge_entity()`, `merge_document()`, `merge_relation()`
  - `find_node()`, `get_neighbors()`, `graph_summary()`
  - `get_all_entity_mentions()` — Bulk entity data for profile building
  - `get_documents_for_entity()` — Documents mentioning an entity
  - `clear_all()` — Drop all nodes/edges (for rebuild)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST /search/graph/find` | Search entities by name |
| `POST /search/graph/neighbors` | Get entity connections |
| `GET /search/graph/summary` | Graph statistics |
| `GET /search/graph/docs/{name}` | Documents for an entity |
| `POST /index/rebuild-kg` | Full graph rebuild (~15 min) |
