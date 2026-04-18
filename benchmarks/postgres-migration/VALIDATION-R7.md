# R7 — Kill de relations ruido (CO_OCCURS_WITH + llm_low vagos)

> **Fecha:** 2026-04-18 · **Rama:** `feature/postgres-migration`
> **Script:** `src/alejandria/storage/postgres/kg_r7_kill_noise.py`
> **Agenda:** [kg-ingestion-refactor.md §3 R7](../../docs/kg-ingestion-refactor.md) — subido de LOW a HIGH tras R0.

El peso de `relations` tras R0 seguía en 7.6 GB porque el 61 % de sus filas eran edges `CO_OCCURS_WITH` / `ASSOCIATED_WITH` / `RELATED_TO` con `confidence='llm_low'` — ruido derivado de co-ocurrencia en chunks. Se pueden regenerar on-demand vía pgvector sobre embeddings de entidades cuando una query los necesite.

---

## 1. Resumen ejecutivo

| Métrica | Antes R7 | Después R7 | Delta |
|---|---:|---:|---:|
| Relations | 54,530,858 | **21,240,727** | **–33,290,131 (–61 %)** |
| DB total | 10 GB | **5.8 GB** | **–4.2 GB (–42 %)** |
| Duración | — | 132.6 s (delete 67.6 s + VACUUM FULL) | — |

### Comparación definitiva con el stack actual

| Stack | Tamaño |
|---|---:|
| SQLite live | 3.5 GB |
| Neo4j live | 4.6 GB |
| **Total actual** | **8.1 GB** |
| **Postgres post-R0+R7** | **5.8 GB** |
| **Ahorro neto** | **–2.3 GB (–28 %)** |

**El caso de negocio de storage se recupera**. Tras la migración cruda había crecido +36 %; tras R0 + R7 termina en **–28 %**. Todos los demás beneficios del plan (multi-máquina, backup a GitHub, stack unificado, velocidad de escritura) siguen vigentes.

---

## 2. Qué se borró

Tier **conservador** (default):

| rel_type | confidence | Rows borrados |
|---|---|---:|
| CO_OCCURS_WITH | llm_low (100 %) | 27,766,340 |
| ASSOCIATED_WITH | llm_low | 4,974,901 |
| RELATED_TO | llm_low | 548,890 |
| **Total** | | **33,290,131** |

**No tocado**: confidence IN ('curated', 'metadata', 'llm_high') OR verified=TRUE. Tampoco rel_types con carga semántica aunque sean llm_low: TEACHES, BELONGS_TO, LIVED_DURING, REFERENCED_IN, EXISTS_DURING.

### Tier agresivo (disponible vía `--aggressive`)

El mismo script con `--aggressive` borra además llm_low de BELONGS_TO/LIVED_DURING/EXISTS_DURING/REFERENCED_IN/TEACHES (~20M más). No se aplicó aquí porque esas relaciones sí portan semántica (Nephi→AUTHORED→1 Nephi es BELONGS_TO type; podría perderse señal). Se reevalúa tras medir calidad en Fase 3.

---

## 3. Estado final del Postgres

| Tabla | Tamaño | Rows |
|---|---:|---:|
| `relations` | **2.95 GB** | 21,240,727 |
| `chunks` | 1.72 GB | 309,089 |
| `chunk_embeddings` | 750 MB | 217,370 |
| `ner_candidates` | 207 MB | 623,283 |
| `entities` | 177 MB | 811,954 |
| `document_registry` | 18 MB | 56,073 |
| **DB total** | **5.8 GB** | |

### Distribución de relations remanentes

| rel_type | confidence | count |
|---|---|---:|
| REFERENCED_IN | llm_low | 6,205,494 |
| BELONGS_TO | llm_low | 5,703,686 |
| LIVED_DURING | llm_low | 4,413,222 |
| TEACHES | llm_low | 3,231,166 |
| EXISTS_DURING | llm_low | 1,429,499 |
| CITES | metadata | 193,978 |
| AUTHORED_BY | metadata | 20,071 |
| PART_OF | metadata | 17,813 |
| COVENANT_OF | llm_low | 14,304 |
| (otros) | curated/metadata | ~5,500 |

**20.98M llm_low + ~240k metadata + ~1.5k curated**. Los llm_low que quedan tienen al menos un rel_type semánticamente acotado — no son el "catch-all" que CO_OCCURS_WITH representaba.

---

## 4. Validación funcional — comparación temporal

### `kg_neighbors("Nephi" person)` a lo largo de la migración

**Estado 1 — Post-migración cruda (contaminado):**
```
Iglesia                                         BELONGS_TO
La Iglesia de Jesucristo SUD                    BELONGS_TO
Autoridades Generales                           BELONGS_TO
Él                                              BELONGS_TO
Sociedad de Socorro                             BELONGS_TO
Escuela Dominical                               BELONGS_TO
```
*Absurdo: profeta del Libro de Mormón "pertenece a" la Sociedad de Socorro.*

**Estado 2 — Post-R0 (merges + garbage):**
```
Exodus 14                ALLUDES_TO
1 Nephi                  AUTHORED     ← señal real emergente
2 Nephi                  AUTHORED     ← señal real emergente
Arcade                   BELONGS_TO
Eurasian                 BELONGS_TO
the ministry of the saints  BELONGS_TO
church did multiply      BELONGS_TO
treasury                 BELONGS_TO
Navy                     BELONGS_TO
```
*Aparecen AUTHORED curated, pero aún mezclados con BELONGS_TO ruidoso (Navy, Arcade).*

**Estado 3 — Post-R7 (este cleanup):**
```
Exodus 14                scripture   ALLUDES_TO        curated
1 Nephi                  scripture   AUTHORED          curated
2 Nephi                  scripture   AUTHORED          curated
Lehi                     person      BLESSED_BY        curated
Jerusalem                place       BORN_IN           curated
Sam                      person      BROTHER_OF        curated
Lemuel                   person      BROTHER_OF        curated
Laman                    person      BROTHER_OF        curated
Jacob                    person      BROTHER_OF        curated
Joseph                   person      BROTHER_OF        curated
Mormon                   person      DESCENDANT_OF     curated
Amos                     person      FATHER_OF         curated*
Ruler over his brothers  role        FOREORDAINED_AS   curated
Nephite civilization     concept     FOUNDED           curated
King                     concept     HAS_ROLE          curated
```

*(\* Amos FATHER_OF Nephi apunta a otro Nephi — hijo de Helamán, hijo de Amos en 3 Nefi; es issue de disambiguación, no de cleanup.)*

**Todas las 15 respuestas son `curated`** — el núcleo curado del Libro de Mormón por fin domina el resultado sin necesidad de filtros ad-hoc en la query.

---

## 5. Limitaciones + siguiente iteración

1. **Ruido llm_low restante en rel_types semánticos** (REFERENCED_IN, BELONGS_TO, LIVED_DURING, TEACHES, EXISTS_DURING) suma ~20.9M filas. Parte será útil, parte no. R5 del backlog + validación en Fase 3 decidirán si hay que correr `--aggressive`.

2. **Tabla `ner_candidates` (207 MB, 623k rows)** sigue siendo la tabla más desproporcionada en relación a su uso: cero promotions en historia. Candidato a R6 (decidir destino) — no toqué en R7 porque es dominio aparte.

3. **pgvector HNSW (750 MB)** puede comprimirse ~50 % usando `halfvec` (float16). Trabajo futuro tras validar recall acceptable.

---

## 6. Próximo paso recomendado

Ya con el Postgres en 5.8 GB y el KG saneado, el camino natural es:

**Fase 3 — Portar módulos a Postgres**:
- `search/textual.py` → `search/postgres_textual.py` (tsvector + ts_rank)
- `search/semantic.py` → `search/postgres_semantic.py` (pgvector HNSW)
- `knowledge/neo4j_client.py` → `knowledge/postgres_graph_client.py` (CTEs recursivos sobre `relations`)
- Feature flag `ALEJANDRIA_BACKEND=sqlite|postgres` para correr ambos stacks en paralelo y validar paridad.

**Fase 0 IONOS** puede arrancar en paralelo: provisionar Postgres 16 en el VPS, aplicar DDL, correr los migradores + R0 + R7 allá.
