# R0 Cleanup — validación post-ejecución

> **Fecha:** 2026-04-18 · **Rama:** `feature/postgres-migration`
> **Script:** `src/alejandria/storage/postgres/kg_cleanup.py`
> **Agenda:** [kg-ingestion-refactor.md §3 R0](../../docs/kg-ingestion-refactor.md)

Primer paso post-migración: limpiar la contaminación del KG heredada de la ingesta anterior. Objetivos (del backlog R0): eliminar garbage (URLs, puntuación, stopwords, xref fragments, outliers de longitud) y unificar duplicados canónicos vía gazetteer.

---

## 1. Resumen ejecutivo

| Métrica | Antes | Después | Delta |
|---|---:|---:|---:|
| Entities | 820,761 | **811,954** | **–8,807** (–1.1 %) |
| Relations | 57,030,709 | **54,530,858** | **–2,499,851** (–4.4 %) |
| DB total | 11 GB | **10 GB** (tras `VACUUM FULL`) | **–9 %** |
| Duración cleanup | — | 287.5 s | — |

El cambio en conteo es pequeño (1.1 % de entidades, 4.4 % de relaciones), pero el **impacto en calidad del search es desproporcionado**: las entidades merged absorbieron miles de relaciones que antes estaban diluidas.

---

## 2. Desglose por fase

### Phase 1 — Garbage eliminado (4,371 entidades únicas)

| Bucket | Rows | Ejemplos representativos |
|---|---:|---|
| `too_long` (>80 chars) | 2,152 | "St. Louis.--Fine scenery.--Visit relatives.--Poem.--Obtain genealogies.--Acknowledgment" |
| `too_short` (<3 chars) | 1,073 | "LA", "Él", "O" |
| `url_like` | 613 | "NiñosyJóvenes.LaIglesiadeJesucristo.org" |
| `xref_fragment` (See ...) | 392 | "See ALEPH", "See Thresh" |
| `all_punct` | 101 | "###", "---" |
| `archaic_verb` | 72 | contains "hath/saith/begat/shalt/..." |
| `pronoun_stopword` | 67 | "Thou", "Ye", "Él" |

*(La suma bruta es 4,470 con doble-cuenta por overlaps; tras dedup al DELETE el total efectivo es 4,371 filas.)*

### Phase 2 — Gazetteer merges (1,244 grupos, 4,436 losers)

Top 10 merges por tamaño:

| Canonical (tipo) | Losers absorbidos |
|---|---:|
| Holy Ghost (person) | 52 |
| Jesus Christ (person) | 49 |
| Plan of Salvation (concept) | 30 |
| Prophet (concept) | 26 |
| Church of Jesus Christ of Latter-day Saints (concept) | 23 |
| Sabbath (concept) | 23 |
| Apostle (concept) | 21 |
| Kingdom of God (concept) | 21 |
| Family Proclamation (document) | 21 |
| New Covenant (concept) | 21 |

### Impacto sobre la tabla `relations`

| Operación | Rows afectadas |
|---|---:|
| Reassigned (src_id o dst_id reapuntado a winner) | 3,318,794 |
| Self-loops eliminados (src=dst tras merge) | 3,733 |
| Duplicados eliminados (mismo src+dst+rel_type) | 1,439,333 |
| **Total filas eliminadas de relations** | **~2,500,000** |

**El merge dedupeó 1.4M relaciones** — esto es la recompensa real del trabajo. Cada vez que dos entidades duplicadas (`Jesus Christ` y `Jesucristo`) tenían la misma relación con un tercero, pasa a ser una sola fila.

---

## 3. Verificación funcional

### kg_neighbors("Nephi") — antes vs después

**Antes (validación Fase 2):**
```
Iglesia
La Iglesia de Jesucristo de los Santos de los Últimos Días
Unir · Autoridades Generales · Él · Su Iglesia · Pautas
Sociedad de Socorro · Espíritu Santo · Escuela Dominical
```
Todos BELONGS_TO — absurdos (un profeta del Libro de Mormón "pertenece a" la Sociedad de Socorro).

**Después del cleanup:**
```
Exodus 14            ALLUDES_TO
Exodus 14            ALLUDES_TO
1 Nephi              AUTHORED   ← señal real
2 Nephi              AUTHORED   ← señal real
Arcade               BELONGS_TO
Eurasian             BELONGS_TO
the ministry of the saints  BELONGS_TO
church did multiply  BELONGS_TO
treasury             BELONGS_TO
Navy                 BELONGS_TO
```

**Análisis:**
- **Ganancia visible:** las relaciones `AUTHORED 1 Nephi / 2 Nephi` (curadas, confianza alta) ahora aparecen en los primeros resultados. Antes estaban sepultadas porque el query devolvía primero los BELONGS_TO masivos producto de duplicados.
- **Ruido residual:** `Arcade`, `Navy`, `Eurasian` como `BELONGS_TO Nephi` — son `llm_low` extraction artifacts que R0 no tocó. Son candidatos claros para R7 (kill low-confidence relations).

---

## 4. Limitaciones conocidas de R0

El cleanup fue deliberadamente conservador. Casos no resueltos:

1. **Duplicados fuera del gazetteer**: entidades como `Señor Jesucristo`, `Su Hijo Jesucristo`, `Jesucristo Cumplir`, `Jesucristo Normas` siguen separadas porque no matchean literalmente alguna entry del gazetteer. **Solución:** R5 del backlog (matching con aliases cross-language + normalización de honoríficos).

2. **Artefactos de extracción concatenada**: `Jesucristo - Normas`, `Jesucristo Normas` son errores donde spaCy/LLM juntaron "Jesucristo" con palabras adyacentes. **Solución:** R1-R3 (filtros en ingesta para prevenir origen).

3. **Relations `llm_low` masivas**: 29M CO_OCCURS_WITH + 5M ASSOCIATED_WITH sobreviven. Explican ~45% del peso de `relations`. **Solución:** R7 del backlog. **Prioridad subida de LOW a HIGH** tras este resultado — es el lever para que el Postgres sea net-smaller que el stack actual.

4. **Residual garbage**: frases latinas (`Hic de Virgine Maria Jesus Christus Natus Est`), títulos de charlas absorbidos como personas (`Covenant Confidence through Jesus Christ`), etc. Tamaño: <0.5% de entities. Candidatos a R5 o revisión manual.

---

## 5. Audit trail

Audit logs escritos en `/tmp/kg-cleanup-audit/` (dentro del container ephemeral, se pierden al salir):
- `garbage_deleted.jsonl` — sample de primeras 30 eliminaciones de garbage con reason
- `merges.jsonl` — 1,244 merges con canonical_name + winner_id + loser_ids

Para retener el audit en la máquina host, montar `-v $(pwd)/audit:/audit` durante el apply.

---

## 6. Próximos pasos

1. **R7 (upgrade a HIGH)**: eliminar CO_OCCURS_WITH y ASSOCIATED_WITH con `confidence='llm_low'`. Único camino para que Postgres total < 8 GB.
2. **R5**: expansion de merges con heurísticas de honoríficos y cross-language sobre el gazetteer.
3. **R1-R3**: filtros en ingesta futura para prevenir que el pipeline vuelva a generar este ruido.
4. **Validación de paridad**: correr 50-100 queries de referencia contra el stack Neo4j (live) vs el Postgres limpio para medir overlap de resultados.

Con R0 + R7 aplicados, el Postgres debería bajar a ~6-7 GB (vs 8.1 GB del stack actual SQLite+Neo4j) y con la calidad del KG saneada.
