# Auditoría pre-port del `knowledge/neo4j_client.py`

> **Estado:** agendado. Ejecución antes del port a `postgres_graph_client.py` (Fase 3 parte final).
> **Origen:** durante la validación de Fase 3 (sesión 2026-04-18), el usuario flagueó que portar el cliente Neo4j tal cual correría el riesgo de "importar" asunciones construidas sobre datos sucios — análogo al gap del gazetteer "Iglesia" que detectamos en tests y al principio de Fase 0 (preparar antes de ingestar).

Este doc es el **Fase 0 del port del KG client**: inventariar qué hay, qué sigue siendo valioso tras R0+R7 cleanup, qué es deuda, qué falta, y qué queremos en el cliente nuevo.

---

## 0. Caveat de calidad de datos (2026-04-18)

Antes de empezar la auditoría es clave reconocer un hecho: **la tabla `entities` tiene ~50-60 % de filas con `entity_type` mal clasificado** a pesar de R0+R7. Ejemplos: `"John 2:1"` como `period`, `"the Cathedral St. Lorenzo"` como `people`, `"Burgundy"` como `person`.

Esto se agenda como **R10 — Type correctness pass** en [`kg-ingestion-refactor.md`](kg-ingestion-refactor.md) y es **independiente** de la migración a Postgres. No bloquea el port del cliente.

Consecuencia operativa **para esta auditoría**: cuando analicemos cada método del cliente Neo4j, hay que preguntarse si asume **precisión del `entity_type`**. Métodos que filtran por tipo (ej. `find_entities_by_type('scripture')`) van a devolver resultados envenenados hoy — tras R10 no, pero el port debe tenerlo en cuenta:

- Añadir defensas en las queries (JOIN con regex para validar scripture refs en runtime).
- O asumir que R10 corre ANTES de cutover (y documentarlo).
- O aceptar la imperfección y cubrirla con reranking downstream en RAG.

Esta decisión va por-método en §2.1 — columna nueva: **"¿Asume type correctness?"**.

---

## 1. Por qué hace falta auditar primero

El `neo4j_client.py` actual (~1000 líneas) creció sobre datos que:

- Contenían 29M `CO_OCCURS_WITH` que ahora no existen (R7 los eliminó).
- Tenían 4,436 duplicados de canonical que R0 colapsó.
- Incluían ~8,800 entidades basura (URLs, `###`, pronombres) que R0 borró.
- Sufrían de gaps de gazetteer que detectamos y estamos cerrando (R4 ongoing).

Además, algunos módulos del cliente (ej. `_build_alias_lookup` en `neo4j_client.py:22-44`) **ya fueron migrados a `knowledge/gazetteer_lookup.py`** durante R1+R3. Portarlos otra vez sería duplicación.

**Principio guía** (del propio usuario): *"el trabajo de ingesta se prepara primero en Fase 0"* — aplicado aquí: **el port se diseña primero en la auditoría, no se descubren problemas a mitad de implementación.**

---

## 2. Qué auditar — checklist obligatorio antes del primer método portado

### 2.1 Inventario de métodos públicos

Enumerar todos los métodos de `Neo4jClient` con columnas:

| Método | Callers (grep) | Usa relation types que R7 mató? | Usa alias lookup local (duplicado de gazetteer_lookup)? | Asume type correctness? | ¿Deprecado? |
|---|---|---|---|---|---|

Criterio "usa relation types que R7 mató":
- `CO_OCCURS_WITH`, `ASSOCIATED_WITH` (solo llm_low), `RELATED_TO` (solo llm_low) → **método devuelve resultados vacíos o degradados post-R7**.

### 2.2 Callers reales

Por cada método, grep en `src/` para ver quién lo llama. Si 0 callers → candidato a borrar en el port. Si >0 callers → listar archivos para el cutover.

Comando:
```bash
grep -rn "neo4j_client\.\|_neo4j\.\|self\._driver\." src/alejandria/ | grep -v knowledge/neo4j_client.py
```

### 2.3 Dependencias removibles

- `_build_alias_lookup()` — ya existe en `gazetteer_lookup.py`. El nuevo cliente debe importar desde ahí, no re-implementar.
- `clear_all(preserve_sources=…)` — patrón Neo4j específico (MATCH/DELETE). En Postgres la semántica cambia: TRUNCATE … RESTART IDENTITY CASCADE, o DELETE WHERE source NOT IN (…). Verificar qué fuentes se "preservan" y si sigue teniendo sentido tras R7.
- Batch methods (`batch_merge_entities`, `batch_merge_relations`) — Neo4j UNWIND ≠ Postgres COPY. El patrón de uso desde el pipeline hay que revisarlo: COPY es todo-o-nada, UNWIND es por-lote.

### 2.4 Patrones de query Cypher → SQL

Cypher permite lookups multi-hop en una sola query (`MATCH (a)-[r*1..3]->(b)`). El equivalente Postgres es recursive CTE (ya usado en R0). Por cada query recursiva:
- Verificar que los indices existentes (`relations_src_type_idx`, `relations_dst_type_idx`, `relations_type_idx`, `relations_category_idx`) cubren el access pattern.
- Confirmar el patrón "LIMIT intermedio en recursive CTE" que documentamos en `postgres-migration.md §2.3` (hard cap de 5000 filas para evitar blow-up con hubs).

### 2.5 Métodos post-R7 que perdieron sentido

Candidatos a NO portar sin reemplazo:
- Cualquier método que rankea por "cantidad de CO_OCCURS_WITH entre dos entidades" — esa señal ya no existe; reemplazar por similaridad pgvector entre embeddings de perfiles.
- Métodos que exponen el grafo "denso" (all-neighbors sin filtro de `confidence`) — tras R7 el grafo es 61% más chico, muchos patterns de uso ya ganan claridad sin cambio.

### 2.6 Gaps descubiertos a cerrar antes del port

Inspirados por el hallazgo "Iglesia":
- Confirmar que todos los aliases canónicos que aparecen en queries hard-coded del cliente (si los hay) están en el gazetteer.
- Tests de paridad contra queries de referencia reales (no solo sintéticos) — Neo4j y Postgres deben devolver el mismo top-K para 50 queries canonical.

---

## 3. Entregables de la auditoría

1. **Tabla de métodos** con las 5 columnas de §2.1 (Markdown, committable).
2. **Port plan priorizado**:
   - `KEEP_AS_IS` — método trivialmente portable.
   - `REWRITE` — método que cambia semántica por R7 o CTE.
   - `CONSOLIDATE` — método que debe importar de un módulo compartido en vez de re-implementar.
   - `DEPRECATE` — método sin callers o sin sentido post-cleanup.
3. **Lista de golden queries**: 50 queries con input + output esperado, contra la DB limpia. Se usan para tests de paridad del nuevo cliente.
4. **Lista de gaps de gazetteer**: aliases que faltan según los patterns de queries. Estos se añaden a `entities.json` antes de escribir el nuevo cliente — no después.

---

## 4. Criterios de arranque del port propiamente dicho

Solo empezar a escribir `postgres_graph_client.py` cuando:

- [ ] La tabla del §2.1 esté completa.
- [ ] Los métodos `DEPRECATE` estén documentados con razón.
- [ ] Las golden queries estén seleccionadas con input + expected top-K.
- [ ] Los gaps del gazetteer identificados estén cerrados (commits a `entities.json`).
- [ ] El plan esté revisado por el usuario.

Este doc es el contrato: si algo queda dudoso, se anota aquí antes de empezar a codear. El port es implementación, no descubrimiento.

---

---

## 6. Resultados de la auditoría (2026-04-18)

**Metodología**: grep de cada método public de `neo4j_client.py` contra `src/alejandria/**/*.py` para callers reales. Lectura de cada método para detectar uso de relation types post-R7 y dependencias removibles.

### 6.1 Hallazgo #1 — Gap estructural MENTIONED_IN (CRÍTICO) ✅ RESUELTO 2026-04-18

**Decisión tomada**: **Opción A** (tabla `entity_document_mentions`).

**Implementación**:
- `ddl.sql`: tabla nueva con PK `(entity_id, file_path, resolved_name)`, FKs a `entities` y `document_registry` con CASCADE.
- `schema.py`: `SCHEMA_VERSION=2` stamp.
- `migrate_neo4j.py::migrate_entity_document_mentions()` — nuevo paso streaming que cruza Neo4j con el id_map + valid file_paths y hace COPY.

**Resultado real en IONOS (2026-04-18)**:
- 3,546,277 mentions migradas en 131.6 s.
- Skipped 284,365 por entity desconocida (R0 las borró/mergeó) + 154,193 por file_path no en document_registry (docs pre-ingesta limpia). Cuentas cuadran exacto con los 3,984,835 edges originales.
- Tabla pesa 954 MB (con índices). DB total pasa de 5.8 → 6.6 GB (+14 %); sigue siendo -18 % vs stack SQLite+Neo4j combinado (8.1 GB).

**Validación funcional**:
```sql
SELECT m.file_path FROM entity_document_mentions m
JOIN entities e ON e.id = m.entity_id
WHERE e.name = 'Nephi' AND e.entity_type = 'person' LIMIT 10;
```
→ Devuelve 10 docs reales (abinadi, articles-of-faith, etc.), confirma que `get_documents_for_entity`, `get_documents_for_entities_batch`, `get_all_entity_mentions`, y `get_disambiguated_counts` son portables.

**Los 6 métodos antes BLOCKED son ahora REWRITE normales**. El gap cerró limpio.

### 6.1-legacy — Análisis original del hallazgo

El migrador Neo4j→Postgres explícitamente saltó 3,984,835 edges `Entity→Document` (diseño §2 del `postgres-migration.md`) porque el schema destino no tiene tabla puente entity↔document. **Pero 4 métodos del cliente dependen de esos edges**:

| Método | Cypher actual | Callers reales | Impacto si port ingenuo |
|---|---|---|---|
| `get_documents_for_entity(name)` | `MATCH (e:Entity {name:$n})-[:MENTIONED_IN]->(d)` | api/routes_graph.py:163, mcp_server.py:537 (**MCP tool kg_docs**) | Devuelve `[]` → MCP tool pierde función |
| `get_documents_for_entities_batch(names)` | `MATCH (e:Entity)-[:MENTIONED_IN]->(d) WHERE e.name IN $names` | chat/rag.py:432 (**RAG pipeline**) | RAG pierde resolución entidad→doc |
| `get_all_entity_mentions()` | `MATCH (e:Entity)-[:MENTIONED_IN]->(d)` | pipeline.py:1805 (profile generation) | Profile generation no encuentra menciones |
| `get_disambiguated_counts()` | `MATCH (e)-[r:MENTIONED_IN]->(d) RETURN r.resolved_name, count(*)` | pipeline.py:1808 | Sin disambiguation counts → staleness tracking roto |

**Decisión pendiente** (no la tomo yo, la traigo para review):

- **Opción A — Tabla nueva `entity_document_mentions`** en Postgres + DDL v2 + re-migración Neo4j que incluya Entity→Document edges. ~+6M rows, ~+500 MB en tabla + índices. Método: añadir a `ddl.sql`, bump `SCHEMA_VERSION=2`, `migrate_neo4j.py` extendido con query separada para Entity→Document edges. ETA ~1 día implementación + 10 min run.

- **Opción B — Derivar on-the-fly** desde `chunks`. Las `chunks.metadata` contienen info de entidades mencionadas por chunk (ya que el pipeline las extrajo durante ingesta). Pero hoy no hay índice explícito entity→chunk; habría que reprocesar. Más trabajo que A.

- **Opción C — Re-ingesta** con el pipeline nuevo escribiendo directo a Postgres. Resuelve el gap de forma natural. Requiere completar Fase 3-5 primero. Circular.

**Recomendación**: **Opción A** para destrabar el port. Es el camino más corto con el menor cambio de scope.

### 6.2 Hallazgo #2 — `migrate_untyped_relations()` es dead code post-R7

`neo4j_client.py:716-750` reclasifica relaciones llm_low en `CO_OCCURS_WITH / RELATED_TO / ASSOCIATED_WITH / TEACHES / BELONGS_TO / REFERENCED_IN` a tipos más específicos usando keyword matching sobre nombres.

Tras R7, los primeros 3 **ya no existen**. Los últimos 3 sobreviven pero no se reclasifican en runtime — el método nunca encontrará patterns que ya fueron borrados.

**Clasificación: DEPRECATE.** También el endpoint API `api/routes_index.py:202` (`POST /index/migrate-relations`) que lo expone debería retirarse.

### 6.3 Hallazgo #3 — `_build_alias_lookup()` es duplicado

Ya existe en `knowledge/gazetteer_lookup.py::load_alias_lookup()` — mismo schema (dict[normalized_alias] → (canonical_name, entity_type)) con cobertura más robusta (NFC, strip artículos). **CONSOLIDATE**: el nuevo cliente importa de `gazetteer_lookup`, elimina la versión local.

### 6.4 Inventario completo de métodos públicos (34)

Leyenda:
- **KEEP** = portable 1:1 a Postgres (queries simples, schema ya cubre)
- **REWRITE** = lógica cambia (CTEs recursivos, schema nuevo, semántica post-R7/R10)
- **CONSOLIDATE** = usar módulo compartido en vez de re-implementar
- **DEPRECATE** = sin callers, o sin sentido post-cleanup
- **BLOCKED** = requiere decisión externa (p.ej. hallazgo #1)

| # | Método | Callers externos | Clasificación | Notas |
|---|---|---|---|---|
| 1 | `_build_alias_lookup` (module) | neo4j_client interno | **CONSOLIDATE** | Usar `gazetteer_lookup.load_alias_lookup` |
| 2 | `__init__` | DI | KEEP | Construct psycopg connection pool |
| 3 | `_cached` | interno | KEEP | TTL cache helper (conservar semántica) |
| 4 | `_ensure_indexes` | pipeline.py:1538 | DEPRECATE | Postgres crea índices via DDL; no hace falta en runtime |
| 5 | `close` | DI | KEEP | conn.close() |
| 6 | `merge_entity(name, type, aliases)` | pipeline.py:1549 | REWRITE | `INSERT ... ON CONFLICT (name, entity_type, disambiguator) DO UPDATE`. Aliases → tabla `entity_aliases` |
| 7 | `merge_document(file_path, source)` | 0 externos (indirecto via batch) | KEEP | `document_registry` ya existe |
| 8 | `merge_relation(...)` | pipeline.py:1552 | REWRITE | INSERT a `relations` con resolve de nombres → ids |
| 9 | `link_entity_to_document(...)` | 0 externos directos | **BLOCKED** | Necesita Opción A del Hallazgo #1 |
| 10 | `batch_merge_entities` | pipeline, relation_extractor_llm | REWRITE | `COPY ... ON CONFLICT` via unlogged staging + INSERT |
| 11 | `batch_merge_documents` | pipeline 3 sitios | REWRITE | COPY a `document_registry` |
| 12 | `batch_merge_relations` | pipeline, relation_extractor_llm | REWRITE | Resolve names→ids en staging temp, COPY a `relations` |
| 13 | `batch_link_entities_to_document` | pipeline 3 sitios | **BLOCKED** | Hallazgo #1 |
| 14 | `batch_delete_documents` | 0 externos directos | KEEP | `DELETE FROM document_registry WHERE file_path = ANY(%s)` |
| 15 | `batch_write_all(...)` | pipeline.py:435 | REWRITE | Orquestador: llama a los batch_merge_*. Thin wrapper |
| 16 | `delete_document_relations(file_path)` | pipeline 3 sitios | REWRITE | `DELETE FROM relations WHERE src_id IN (entities del file)` — caveat: requiere Hallazgo #1 resuelto si cubre entity→document |
| 17 | `_resolve_name(name)` | interno | CONSOLIDATE | Import de `gazetteer_lookup` |
| 18 | `_resolve_names(names)` | interno | CONSOLIDATE | Idem |
| 19 | **`find_node(search, entity_type, limit)`** | **routes_graph, cli, mcp** | **REWRITE** | `SELECT ... WHERE name ILIKE '%q%' OR id IN (SELECT entity_id FROM entity_aliases WHERE alias ILIKE '%q%')`. Usa `pg_trgm` para fuzzy. ⚠️ **type correctness caveat** (R10): filtro por `entity_type` devuelve resultados envenenados hasta R10 |
| 20 | **`get_neighbors(name, depth, limit)`** | **routes_graph, cli, mcp, rag** | **REWRITE** | Recursive CTE con LIMIT intermedio (patrón ya documentado en postgres-migration §2.3) |
| 21 | `get_documents_for_entity(name)` | routes_graph, mcp | **BLOCKED** | Hallazgo #1 |
| 22 | `get_documents_for_entities_batch` | chat/rag.py:432 | **BLOCKED** | Hallazgo #1 |
| 23 | `find_nodes_batch(searches, limit_per)` | chat/rag.py:426 | REWRITE | UNION de find_node por batch; o query con `ANY(%s)` y ranking |
| 24 | `get_typed_relations_batch(...)` | chat/rag.py:1199 | REWRITE | Filter por `rel_type` / `category` sobre `relations` + JOIN a entities |
| 25 | `graph_summary()` | routes_graph, cli, mcp, main | REWRITE | Agregados simples (count entities, relations, top types) |
| 26 | `get_all_entity_mentions()` | pipeline.py:1805 | **BLOCKED** | Hallazgo #1 |
| 27 | `get_disambiguated_counts()` | pipeline.py:1808 | **BLOCKED** | Hallazgo #1 — alternativa: derivar de `relations.properties->>'resolved_name'` si existe el meta |
| 28 | `update_entity_profile(...)` | profile_generator (indirecto) | REWRITE | UPDATE sobre `entity_profiles` (tabla ya existe) |
| 29 | `load_curated_relations(path)` | routes_index, pipeline 2 sitios | REWRITE | Parse JSON + INSERT batch a `relations` con `confidence='curated'` |
| 30 | `migrate_untyped_relations(batch_size)` | routes_index.py:202 | **DEPRECATE** | Hallazgo #2; retirar endpoint API también |
| 31 | `get_parallel_passages(...)` | routes_graph.py:128 | REWRITE | Queries sobre `relations` con `rel_type IN ('PARALLEL_ACCOUNT_OF', ...)` + JOIN |
| 32 | **`get_typed_relations(...)`** | **routes_graph, mcp** | **REWRITE** | Filter por src/dst + rel_type/category; paginación; ⚠️ type correctness caveat |
| 33 | `clear_all(preserve_sources)` | pipeline.py:624, 1533 | REWRITE | `TRUNCATE entities, entity_aliases, relations RESTART IDENTITY CASCADE` — la semántica `preserve_sources` se traduce a `DELETE ... WHERE source NOT IN (...)` si hace falta |
| 34 | **`get_genealogy_tree(person, direction, depth, lang)`** | **routes_genealogy, mcp** | **REWRITE** | Recursive CTE del patrón postgres-migration §2.3 con LIMIT intermedio. ⚠️ `lang` param implica `_alt_name` lookup (consolidate con gazetteer) |
| 35 | `get_genealogy_path(name1, name2)` | routes_genealogy, mcp | REWRITE | Recursive CTE bidireccional (o 2 unidireccionales con intersection) |
| 36 | `_alt_name(canonical, lang)` | interno (genealogy) | CONSOLIDATE | `gazetteer_lookup` puede exponer alias bilingüe |
| 37 | `_attach_ancestors` | interno (genealogy) | KEEP | Helper puro sobre dicts post-query |
| 38 | `_attach_descendants` | interno (genealogy) | KEEP | Idem |

### 6.5 Resumen cuantitativo

| Clasificación | Count | Comentario |
|---|---:|---|
| KEEP | 6 | Trivialmente portables o puros helpers sobre dicts |
| REWRITE | 16 | Lógica ajusta: CTEs recursivos, resolve de nombres a ids, ON CONFLICT, agregados SQL |
| CONSOLIDATE | 4 | Usar `gazetteer_lookup` compartido |
| DEPRECATE | 2 | `_ensure_indexes` (DDL cubre), `migrate_untyped_relations` (dead code post-R7) |
| **BLOCKED** | **6** | **Dependen de Hallazgo #1 (MENTIONED_IN)** |

### 6.6 Gaps de gazetteer identificados durante la auditoría

Candidatos a añadir a `entities.json` **antes** del port para que queries tipo `find_node("Burgundy")` no se envenenen por type correctness R10:

- `Burgundy`, `Marseilles`, `Savoy`, `Fontainbleau`, `Lombardy` — regiones europeas que aparecen en biografías (McAllister, Loveland) pero mal clasificadas como `person`/`people`.
- Evaluar además: `Mount Gandoglia`, `Cathedral St. Lorenzo`, y otros edificios/geografías italianas del contexto Chester Loveland.

**No es urgente para el port** (R10 los atrapa) pero vale la pena pre-seedar cuando haya un corpus expansion hacia materiales biográficos con geografía europea.

### 6.7 Golden queries — pendiente

Selección de ~50 queries de referencia con input + expected top-K para el test de paridad. **Se define tras cerrar decisión de Opción A del Hallazgo #1** — depende de qué métodos existirán en el nuevo cliente.

### 6.8 Criterios de arranque

- [x] §2.1 Inventario completo: ✅ 34 métodos catalogados.
- [x] §2.5 Métodos DEPRECATE documentados: ✅ 2 métodos (`_ensure_indexes`, `migrate_untyped_relations`).
- [ ] Decisión de usuario sobre Hallazgo #1 (Opción A/B/C).
- [ ] Golden queries curadas: depende de anterior.
- [ ] Gaps críticos de gazetteer cerrados: pendientes (no bloqueantes).

**Siguiente paso recomendado**: aprobación de **Opción A (tabla `entity_document_mentions` + re-migración con Entity→Document edges)** o alternativa. Con esa decisión se desbloquean los 6 métodos BLOCKED y puede iniciarse el port.

---

## 5. Relación con otros docs

- `docs/postgres-migration.md` — plan general de la migración; este es la fase 0 del último módulo grande.
- `docs/kg-ingestion-refactor.md` — backlog R0-R8; este audit es en efecto el paso previo a "R9 port del cliente".
- `docs/project-memory/feedback_docs_sync.md` — la regla de mantener docs al día que gatilló este doc.
- `docs/project-memory/feedback_preseed_before_discovery.md` — el principio de Fase 0: preparar antes de ejecutar. Este doc lo aplica al port.
