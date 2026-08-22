# wp_bc — WordPress Biografías Católicas

## Consumidor de Alejandría

wp_bc es un sitio WordPress con biografías de figuras católicas. Consume
Alejandría para enriquecer su contenido con búsqueda textual, semántica y KG.

## Integración

- **REST API**: `http://localhost:4300/` — desde PHP (WordPress) vía `wp_remote_get()`
- **MCP tools (opencode)**: definido en `wp_bc/opencode.json` como server `streamable-http` apuntando a `http://localhost:4300/mcp/`
- **MCP tools (Claude Code)**: definido en `wp_bc/.mcp.json` con la misma URL

## Symlink

`prods/wp_bc/` → `C:/own/wp_bc` (directory junction via `mklink /D`)

## KG Coverage (2026-07-05)

Se generaron seeds masivos desde `wp_bc/bin/authors-enriched.json` (762 entries)
+ enriquecimiento Wikidata (P22 father, P25 mother, P26 spouse, P40 child,
P3373 sibling, P27 nationality):

| Archivo | Entidades | Relaciones |
|---------|-----------|------------|
| `general-authorities.json` | 1,011 (incl. 14 roles + country entities) | 2,553 |
| `general-authorities-places.json` | 399 places | — |
| `bridge-data.json` | 762 entries (dates + image URLs) | — |

### Relaciones por tipo

| Tipo | Cantidad | Fuente | Uso en infobox |
|------|----------|--------|----------------|
| CALLED_AS | 963 | authors-enriched | `_author_callings` |
| BORN_IN | 529 | wikidata-places | `_author_birth_place` |
| NATIONALITY | 273 | Wikidata P27 | `_author_nationality` |
| DIED_IN | 240 | wikidata-places | `_author_death_place` |
| CHILD_OF | 122 | Wikidata P40 | `_author_children` |
| FATHER_OF | 93 | Wikidata P22 | `_author_father` |
| COUNSELOR_TO | 82 | Overlap matching | — |
| SPOUSE_OF | 81 | wikidata-claims | `_author_spouses` |
| SIBLING_OF | 79 | Wikidata P3373 | — |
| MOTHER_OF | 63 | Wikidata P25 | `_author_mother` |
| SUCCESSOR_OF | 16 | Sucesión presidencial | — |
| Family (hardcoded) | 12 | Church history | — |

### Puente KG → WordPress

`wp_bc/scripts/populate-from-kg.sh <post_id>` — script que:
1. Consulta la API de Alejandría (relations + find)
2. Lee `bridge-data.json` para fechas e imágenes
3. Escribe metadatos en WordPress via `wp post meta update`

Campos que llena: `_author_birth_date`, `_author_death_date`,
`_author_birth_place`, `_author_death_place`, `_author_nationality`,
`_author_father`, `_author_mother`, `_author_spouses`, `_author_callings`.

Batch: `wp_bc/scripts/populate-all-from-kg.sh [--dry-run] [limit=N]`

### Enriquecimiento Wikidata

`scripts/generate_kg_seeds.py` ahora consulta Wikidata API para:
- **P22** (father): 93 relaciones
- **P25** (mother): 63 relaciones
- **P26** (spouse): 81 relaciones
- **P40** (child): 122 relaciones
- **P3373** (sibling): 79 relaciones
- **P27** (nationality): 273 relaciones

Los spouse QIDs se resuelven vía `wbgetentities` (48/53 resueltos).
Datos guardados en `wp_bc/bin/wikidata-enrichment.json`.

### Gazetario NER

`entities.json` pasó de 2,195 → 2,935 persons (740 líderes modernos agregados).
Montado como bind-mount (`gazetteers/`) para actualizaciones sin rebuild.

### Flujo de Generación

1. `scripts/generate_kg_seeds.py` lee `authors-enriched.json` + enriquecimiento Wikidata
2. Genera `data/kg-seeds/general-authorities.json` y `data/kg-seeds/general-authorities-places.json`
3. Genera `data/gazetteer-extra.json` para merge en gazetteer
4. Genera `data/kg-seeds/bridge-data.json` con fechas e imágenes para el puente
5. `rebuild_kg` carga seeds (~2 min), luego NER sobre 353K chunks (~12-24h CPU)
