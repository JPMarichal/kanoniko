# KG Ingestion — backlog de refactorización

> **Estado:** agendado. Ejecución post-migración a Postgres (post Fase 5 de `postgres-migration.md`).
> **Origen:** análisis de `ner_candidates` durante Fase 2 de la migración (17-abr-2026).

Este documento captura los desperdicios identificados en el pipeline de ingesta del KG y las optimizaciones pendientes. Se mantiene separado del doc de migración porque la migración trata de **cambio de motor** mientras que este backlog trata de **cambio de pipeline** — son ortogonales. Mezclarlos durante la migración complicaría las comparaciones A/B del cutover.

---

## 1. Hallazgo principal — ner_candidates es mayormente desperdicio

Datos observados al cerrar la ingesta de 56,073 documentos / 309,089 chunks:

| Métrica | Valor | Implicación |
|---|---:|---|
| Total candidatos acumulados | **623,283** | |
| Con status ≠ 'candidate' | **0** | Mecanismo `promote()`/`dismiss()` nunca usado |
| Singletons (freq=1) | 206,184 (33 %) | Ruido puro |
| Freq 2-5 | 228,355 (37 %) | Ruido mayoritario |
| Freq >500 | 1,784 (0.3 %) | Casi todos duplicados del gazetteer |
| Freq >5000 | 118 (0.02 %) | **Todos** canónicos del gazetteer |
| Tamaño en Postgres | **207 MB** | De 2.7 GB totales |

Los top 15 por frecuencia son todos duplicados del gazetteer o basura de tokenización: `Church` (108k), `Iglesia` (85k), `Jesucristo` (67k), `###` (52k), `Cristo` (43k), `José Smith` (33k), `thou` clasificado como `place` (22k), etc.

**Valor real estimado:** ~1-2k candidatos (0.2 %) que realmente podrían descubrir entidades nuevas no-canónicas.

### 1.1 Alcance real — no es solo `ner_candidates`

**Actualización crítica (17-abr-2026):** verificación directa contra Neo4j live confirma que los mismos filtros laxos que llenan `ner_candidates` **pasan las entidades NER sin filtro al grafo principal**. En `src/alejandria/ingestion/pipeline.py:1694-1707`:

```python
extraction = self._kg_extractor.extract(text, source_file=file_path)
for entity in extraction.entities:          # ← incluye source="ner"
    batch_entities.append({"name": entity.name, "type": entity.type, ...})
    ...
```

Evidencia de contaminación en el KG actual:

| Entidad (Neo4j) | Tipo | Problema |
|---|---|---|
| `###` | object | Basura de tokenización |
| `thou` | place, people, person | Stopword clasificado 3 veces |
| `Jun.` | place, person | Abreviatura de mes |
| `Anticristo` | place | Concepto mal clasificado |
| `ChurchofJesusChrist.org` | place | URL como entidad |
| `FSY.ChurchofJesusChrist.org` | people | URL como entidad |
| `Hic de Virgine Maria Jesus Christus Natus Est` | people | Frase latina completa |
| `Cristo`, `Señor Jesucristo`, `Su Hijo Jesucristo` | person, people, person | Duplicados sin merge |

**Impacto en search (no solo storage):**
- `kg_profile("Jesucristo")` devuelve uno de N duplicados; pierde mentions/relaciones repartidas
- `kg_neighbors` incluye URLs y fragmentos como vecinos de entidades reales
- RAG reranking se sesga por estas entidades falsas
- Disambiguation gasta ciclos resolviendo contra candidatos que no existen

**Reclasificación de criticidad:** lo que antes estaba como "cleanup de ruido" es en realidad **un arreglo de calidad del search**. Subir prioridad.

---

## 2. Causas raíz — tres capas

### Capa 1 — Gap en la preparación de Fase 0

Cuando se añade material nuevo al corpus (`procedure_corpus_addition.md`), el paso de preparación incluye clasificación, autoridad, rating — pero **no exige pre-seed de entidades nuevas al gazetteer**. Si el material introduce entidades relevantes, el gazetteer no las conoce y spaCy las descubre como candidatos. Parte es esperado (es el propósito del discovery), pero muchas son canónicas que simplemente el curador no pre-seedó.

### Capa 2 — Bug: filtro de gazetteer por-chunk, no global

En `src/alejandria/knowledge/extractor.py:885-893`:

```python
# Collect all canonical names from gazetteer matches for overlap detection
known_names_lower = set()
for key in found_entities:               # ← iters over matches IN THIS CHUNK
    name = key.split(":")[0]
    known_names_lower.add(name.lower())
```

`known_names_lower` se construye **por chunk**, no contra el gazetteer global. Si spaCy encuentra `"Jesucristo"` pero el gazetteer en este chunk hizo match con `"Cristo"` (forma distinta), el overlap check falla y `"Jesucristo"` entra a `ner_candidates`.

El alias lookup global (`knowledge/neo4j_client.py:_build_alias_lookup`) ya existe y es usado en otros paths. Solo falta consultarlo en el registro de candidatos.

### Capa 3 — Sin política de retención

Un candidato se crea la primera vez que spaCy lo ve y se mantiene indefinidamente. Singletons y duplicados conviven con candidatos reales hasta el fin del universo.

---

## 3. Agenda priorizada

**Actualización 17-abr-2026:** reclasificación tras confirmar impacto en calidad de search (no solo storage). R0 es nuevo.

### [CRITICAL] R0 — Cleanup de KG existente (post-migración)

**Qué:** una vez migrado el KG a Postgres, ejecutar un script de limpieza one-shot:
1. Borrar entidades cuyo nombre es solo puntuación/símbolos (`###`, `---`, etc.)
2. Borrar entidades que matchean patrones de URL (`.org`, `http`, `www.`)
3. Borrar entidades cuyo `length(name) < 3` o `> 60`
4. Borrar entidades que son stopwords del idioma (`thou`, `shalt`, `hath`, etc.)
5. Merge de duplicados EN/ES vía gazetteer aliases (ej. `Cristo`, `Jesucristo`, `Jesus Christ` → 1 entidad canónica)
6. Reasignar relaciones a entidades merged antes de borrar duplicadas
7. CASCADE a `entity_aliases`, `relations`, `entity_profiles`

**Dónde:** `scripts/kg_cleanup.py` + reporte markdown con entidades borradas para auditoría.

**Esfuerzo:** ~4-6 h (código + revisión de casos límite + run + validación).

**Impacto esperado:**
- Reduce entidades del KG ~30-50 % (mi estimación tras ver los samples).
- Mejora precisión de `kg_profile`, `kg_neighbors`, RAG reranking.
- Reduce tamaño de tablas `entities` y `relations` en Postgres.

**Por qué post-migración y no ahora:** las queries de cleanup son 10x más simples en Postgres (regex, trigram, ILIKE) que en Cypher. Y la migración es el momento natural para cortar con el pasado contaminado.

### [HIGH] R1 — Filtro global de gazetteer en `record()`

**Qué:** `NERCandidateTracker.record()` debe consultar el alias lookup global antes de insertar. Si `name.lower()` está en el lookup, skip (ni INSERT ni increment). Añadir cache module-level (`functools.lru_cache`) para evitar rebuild por llamada.

**Dónde:** `src/alejandria/knowledge/ner_candidates.py:49-81`. Importar `_build_alias_lookup` de `neo4j_client.py` (o mover a un módulo compartido como `knowledge/gazetteers/lookup.py`).

**Esfuerzo:** ~1 h (código + 1 test).

**Impacto esperado:** reduce candidatos 5-10x. Los top-15 actuales desaparecen.

**Riesgo:** si el gazetteer tiene un alias muy genérico (`"él"`, `"Él"`), podría filtrar legítimos. Mitigar con longitud mínima de alias (≥3 chars) y lista de allowlist para términos conflictivos.

### [HIGH] R2 — Política de retención al cerrar ingesta

**Qué:** al final de un run de ingesta, correr:
```sql
DELETE FROM ner_candidates
WHERE frequency < 3
  AND last_seen < now() - interval '30 days';
```

**Dónde:** `src/alejandria/ingestion/pipeline.py` — al final de la fase 3, una sola query.

**Esfuerzo:** ~30 min.

**Impacto esperado:** reduce tabla ~3x adicional después de R1.

### [HIGH] R3 — Normalización al insertar

**Qué:** strip whitespace, NFC-normalize unicode, detectar garbage (`"###"`, solo puntuación, solo dígitos) y rechazar antes de INSERT.

**Dónde:** mismo `record()` de ner_candidates.py.

**Esfuerzo:** ~1 h.

**Impacto esperado:** elimina `###` y similares, deduplica entradas que solo difieren en whitespace.

### [MEDIUM] R4 — Update del procedure_corpus_addition

**Qué:** añadir como paso explícito: *"Si el material introduce entidades centrales (personajes principales, lugares narrativos, conceptos doctrinales específicos), pre-seedear al gazetteer ANTES de correr ingesta."* Con checklist.

**Dónde:** `docs/project-memory/procedure_corpus_addition.md`.

**Esfuerzo:** 30 min.

**Impacto esperado:** previene ruido en origen, no solo lo filtra downstream.

### [MEDIUM] R5 — Cross-language alias matching

**Qué:** hoy `"Church"` y `"Iglesia"` generan DOS candidatos separados. El gazetteer tiene ambos como aliases de la misma entidad canónica. Filtro R1 ya los mata, pero si se escapa alguno, detectar variantes ES↔EN via el gazetteer bilingüe.

**Esfuerzo:** ~1 h (reusa el alias lookup).

### [LOW/decisión] R6 — Destino del mecanismo de promoción

**Estado actual:** 0 promotions en 56k documentos. El código existe, los endpoints existen, nadie los ha llamado.

**Opciones:**
- **(a)** Usar activamente: crear skill `/ner-review` que liste top 50 candidatos no-canónicos y promueva/descarta interactivamente. Integra a los flujos existentes de Claude Code.
- **(b)** Auto-promover: si un candidato supera freq 1000 y no matchea gazetteer tras R1, auto-promover a gazetteer con flag `auto: true`.
- **(c)** Eliminar: borrar `NERCandidateTracker.promote/dismiss` + endpoints + tabla. Reemplazar por discovery on-demand (spaCy sobre corpus completo cuando el usuario pida, reporte markdown manual).

**Decisión pendiente** del usuario. La opción (c) maximiza simplicidad; (a) maximiza valor.

### [LOW] R7 — Kill co-occurrence relations

Relacionado al KG refactor completo (ver doc de migración §7 tabla original). Las relaciones `llm_low` derivadas de co-ocurrencia son ruido similar al de candidatos. Mejor reemplazar por similaridad semántica entre entidades (pgvector sobre embeddings de profile summaries), computada on-demand.

**Esfuerzo:** 1-2 días (cambio mayor).

### [LOW] R8 — Profile generation lazy

Ver doc de migración §7. Generar summaries solo para top-K por `mention_count` en ingesta; resto on-demand la primera vez que el chat las consulte.

**Esfuerzo:** 1-2 días.

---

## 4. Estimación total

| Prioridad | Items | Esfuerzo | Impacto acumulado |
|---|---|---|---|
| **CRITICAL** | **R0** | **~4-6 h** | **Limpia KG existente; restaura calidad de search/RAG** |
| HIGH | R1 + R2 + R3 | **~3 h** | Previene nueva contaminación; reduce ner_candidates 15-30x |
| MEDIUM | R4 + R5 | ~1.5 h | Previene reaparición del problema desde preparación |
| LOW/decisión | R6 | Variable | Dependiente de decisión del usuario |
| LOW | R7 + R8 | 2-4 días | Reduce ingesta fase 3 en 40-60 % (el gran lever estructural) |

**Plan de ataque actualizado:**

1. **Terminar migración a Postgres** (Fases 2-5 de `postgres-migration.md`) — necesario para tener el KG en un motor donde R0 es práctico.
2. **R0 (CRITICAL)** — script de cleanup del KG migrado. Es el primer trabajo *en* Postgres. Corrobora que el motor nuevo es la plataforma correcta para este tipo de higiene.
3. **R1 + R2 + R3** (HIGH) — aplicar los filtros en la ingesta para prevenir re-contaminación. Validar con re-ingesta parcial.
4. **R4** — actualizar procedimiento Fase 0 para que futuras adiciones no repitan el ciclo.
5. **R5** — merge cross-language si quedan duplicados escapados.
6. **Decidir R6** (destino del mecanismo de promoción).
7. **R7 + R8** — proyecto propio (candidato a slot P11 en `proj/`).

**ETA total para dejar el sistema sano:** ~2-3 días concentrados, a distribuir en ventanas post-migración.

---

## 4bis. Estado real al 2026-04-18

Ejecutado contra bench y luego contra IONOS — paridad verificada.

| Item | Estado | Detalle |
|---|---|---|
| R0 | ✅ Ejecutado en IONOS | -8,807 entities, -2.5M relations, duplicados canonical merged. |
| R1 | ✅ En código | `gazetteer_lookup.should_skip_ner_entity()` + filtros en `extractor.py` y `ner_candidates.record()`. 27 tests. |
| R2 | ✅ En código | `NERCandidateTracker.prune_low_value(min_freq=3, max_age_days=30)` llamado al final de cada KG rebuild. |
| R3 | ✅ En código | `is_garbage()` con mismos buckets que R0 — lo que el cleanup borra es lo que la ingesta rechaza. |
| R4 | ✅ Doc + aliases iniciales | `procedure_corpus_addition.md` §4a reforzado. Aliases "Iglesia"/"La Iglesia"/"the Church" añadidos a "Church of Jesus Christ of Latter-day Saints" al detectar el gap en integration tests. |
| R5 | Parcial | Cross-language expandido para "Iglesia". Pendiente: honorificos tipo "Señor Jesucristo", "Su Hijo Jesucristo" — requieren normalización adicional o entries específicas. |
| R6 | Decisión pendiente | ner_candidates — el mecanismo sigue inactivo (0 promotions). R2 mitiga el crecimiento; decisión sobre (a) usar, (b) auto-promover, (c) eliminar, abierta. |
| R7 | ✅ Ejecutado en IONOS | Kill de 27.8M CO_OCCURS_WITH + 5M ASSOCIATED_WITH llm_low + 549k RELATED_TO llm_low. DB 11 GB → 5.8 GB. |
| R8 | Pendiente | Profile generation lazy — no crítico hasta que la ingesta escriba a Postgres. |

**R9 nuevo — Pre-port audit del `neo4j_client.py`** (derivado de este trabajo): el cliente actual se construyó sobre datos sucios; muchos métodos asumen patterns que R7 eliminó. Auditoría separada en `docs/kg-client-port-audit.md`.

## 5. Cross-references

- [postgres-migration.md](postgres-migration.md) — la migración de motor que precede este trabajo.
- [benchmarks/postgres-migration/VALIDATION.md](../benchmarks/postgres-migration/VALIDATION.md) — dónde se detectó el problema con datos reales.
- `src/alejandria/knowledge/extractor.py:885-913` — sitio del bug de filtro por-chunk.
- `src/alejandria/knowledge/ner_candidates.py:49-81` — sitio para añadir filtro global en `record()`.
- `src/alejandria/knowledge/neo4j_client.py:22-45` — `_build_alias_lookup()` que ya hace lo que necesitamos.
- `docs/project-memory/procedure_corpus_addition.md` — procedimiento Fase 0 que requiere actualización (R4).
- `proj/00-backlog.md` — backlog formal; este trabajo puede promoverse a proyecto propio si R7+R8 se consolidan.
