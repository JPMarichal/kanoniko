# Authority Levels — Person Classification System

## Purpose

Classify authors and historical figures by their ecclesiastical authority or
scholarly standing for KG entity metadata and RAG weighting. Answers the
question: *"What weight should this person's statements carry on a given
topic?"*

This is **not** the same as "callings" (specific positions held). A person's
authority level is a stable category — their highest sustained or commissioned
ecclesiastical office, or their scholarly standing if non-LDS.  It encodes
*institutional proximity* to LDS doctrine and governance.

## Taxonomy

| # | Label | Description | Examples | Default authority score |
|---|-------|-------------|----------|------------------------|
| 1 | `autoridad_general` | Sustained by general conference as General Authority | Apostles, First Presidency, Seventies (1st/2nd Q), Presiding Bishopric, Presiding Patriarch | 85 |
| 2 | `lider_general_iglesia` | Called by FP/Q12 to a Church-wide general presidency or general board | RS/YM/YW/Primary/SS General Presidencies, general secretaries | 68 |
| 3 | `lider_local_iglesia` | Called to lead a stake, district, ward, or mission | Stake presidents, bishops, mission presidents, high councilors | 50 |
| 4 | `erudito_sud` | LDS scholar affiliated with Church Education System or similar | BYU/CEU professors, Church historians, apologists (e.g. FARMS/FAIR) | 40 |
| 5 | `autor_independiente_sud` | LDS-authored works outside official or academic channels | Independent LDS writers, bloggers, self-published authors | 30 |
| 6 | `erudito_evangelico` | Non-LDS Protestant scholar writing on LDS topics | Evangelical countercult authors, Protestant historians | 20 |
| 7 | `autor_independiente_evangelico` | Non-LDS Protestant author without academic affiliation | Independent evangelical writers, bloggers | 15 |
| 8 | `autor_primeros_siglos` | Pre-Nicene / early Church father (ca. 100–500 AD) | Justin Martyr, Irenaeus, Tertullian, Augustine | 25 |
| 9 | `primeros_padres` | LDS-era precursors or early Restoration figures before 1830 | Restorationist movement figures (Sidney Rigdon pre-1830, etc.) | 45 |
| 10 | `academico_neutral` | Academic author without LDS or evangelical affiliation | Secular historians, sociologists of religion, religious studies scholars | 15 |
| 11 | `autor_independiente` | Author without identifiable affiliation | Independent writers, journalists, general public | 10 |

## Implementation in the KG

Stored in `entities.metadata` JSONB on `person` nodes:

```json
{
    "authority_tier": "autoridad_general",
    "authority_label": "Autoridad General",
    "authority_score": 85
}
```

### Source of truth

- For LDS figures in the wp_bc dataset: derived from `callings[]` in
  `authors-enriched.json`.  The highest calling maps to the tier.
- For non-LDS figures: manually assigned from `description` or external
  source, stored in the seed JSON.
- Mapping from calling slugs to tier is defined in `generate_kg_seeds.py`.

### Relation to document authority model

The document-level `AuthorityMeta` in `authority.py` assigns doctrinal weight
to *corpus materials*.  Entity-level authority_tier assigns weight to the
*person* who authored a statement.  Combined, they answer:

> "How authoritative is this document about this topic by this person?"

## Event Model — Biographical and Historical Chronology

### Purpose

Model events in the KG for chronological querying: timelines, biographical
milestones, and historical narrative.  Enables queries like "What events
happened during Spencer W. Kimball's presidency?" or "Show Joseph Smith's
life timeline."

### Types of events

| Type | Description | Example |
|------|-------------|---------|
| **Biographical** | Birth, death, ordination, marriage | "Birth of Spencer W. Kimball (1895)" |
| **Calling** | Sustained to a calling or office | "Sustained as President of the Church (1973)" |
| **Historical** | Broader Church / world event | "Priesthood revelation (1978)", "Kirtland Temple dedication (1836)" |

### Entity structure

Events are stored as `entity_type = "event"` in the entities table.
Temporal data in `properties` JSONB on relations.

### Relation types

| Relation | From | To | Purpose |
|----------|------|----|---------|
| `BIRTH_OF` | event | person | Birth of a person |
| `DEATH_OF` | event | person | Death of a person |
| `CALLING_OF` | event | person | Called/sustained to an office |
| `PARTICIPATED_IN` | person | event | Person participated in event |
| `INITIATED` | person | event | Person initiated/caused event |
| `OVERSAW` | person | event | Person presided over / directed event |
| `OCCURRED_DURING` | event | period | Temporal placement |
| `PRECEDED_BY` | event | event | Chronological ordering |
| `FOLLOWED_BY` | event | event | Inverse of PRECEDED_BY |
| `LOCATED_IN` | event | place | Geographic location |
| `CAUSED` | event | event | Causal relationship |
| `DOCUMENTED_IN` | event | document | Source document for the event |
| `AFFECTED` | event | person/people/place | What the event impacted |

### Temporal properties on relations

Any event-related relation can carry temporal data in `properties`:

```json
{
    "confidence": "curated",
    "year": 1978,
    "year_end": null,
    "date": "1978-06-01",
    "date_precision": "month",
    "era": "modern"
}
```

`date_precision` values: `year`, `month`, `day`, `decade`, `century`, `circa`, `range`.

### Seed format for events

Events are seeded from `general-authorities-events.json` and
`historical-events.json`:

```json
{
    "name": "Historical Events — Church milestones",
    "confidence": "curated",
    "entities": [
        {"name": "Birth of Joseph Smith (1805)", "type": "event"},
        {"name": "First Vision (1820)", "type": "event"},
        {"name": "Organization of the Church (1830)", "type": "event"}
    ],
    "relations": [
        {
            "subject": "Birth of Joseph Smith (1805)",
            "subject_type": "event",
            "predicate": "BIRTH_OF",
            "object": "Joseph Smith",
            "object_type": "person",
            "properties": {"year": 1805}
        },
        {
            "subject": "Organization of the Church (1830)",
            "subject_type": "event",
            "predicate": "INITIATED",
            "object": "Joseph Smith",
            "object_type": "person",
            "properties": {"year": 1830}
        },
        {
            "subject": "First Vision (1820)",
            "subject_type": "event",
            "predicate": "PRECEDED_BY",
            "object": "Birth of Joseph Smith (1805)",
            "object_type": "event",
            "properties": {}
        }
    ]
}
```

### Corpus sources for events

The corpus contains chronologies that can be parsed into events:

| Source | Coverage | Format |
|--------|----------|--------|
| `Teachings of Presidents — historical-summary.txt` | 17 presidents | Structured chronology per president |
| `cronologia-general-de-los-eventos-de-la-historia-de-la-iglesia` | 1805-1846, 53 events | Bulleted event list |
| `global-histories/XX-chronology.txt` | 100+ countries | Per-country dating of Church milestones |
| `dc-historical-resources/chronology.txt` | D&C sections 1805-1844 | 1,129-line date:event table |
| `daughters-in-my-kingdom/important-events-in-the-history-of-relief-society.txt` | RS history 1830-present | Date-stamped entries |
| `Doctrine and Covenants chronological table` | 1828-1844, D&C sections | Date:location:section mapping |
| `relief-society/important-events` | RS history 1830-present | Date-stamped entries |
