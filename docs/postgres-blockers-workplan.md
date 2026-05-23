# Plan de Trabajo: Pendientes Bloqueantes para Workspace Migration

> **Objetivo:** Completar los pendientes críticos de la migración a Postgres antes de iniciar la migración a workspace uv + hatch.
> 
> **Tiempo estimado total:** 0.5 días (solo R5 honorifics)

---

## Resumen de Pendientes

| ID | Pendiente | Prioridad | Tiempo Estimado | Dependencias |
|----|-----------|-----------|-----------------|--------------|
| 1 | PR #2: postgres-write-path | CRÍTICO | COMPLETADO | Ninguna |
| 2 | PR #1: postgres-kg-client-rest | ALTA | COMPLETADO | Ninguna |
| 3 | R5: Cross-Language Honorifics | MEDIA | 0.5 días | Ninguna |

**Orden recomendado:** PR #2 → PR #1 → R5

**Tiempo estimado total:** 0.5 días (solo R5 honorifics)

---

## PR #2: postgres-write-path (CRÍTICO - 1-2 días)

### Objetivo
Eliminar referencias restantes a Neo4j/SQLite en el write path de ingesta.

### Estado Actual (Actualizado 2026-05-17)

**YA COMPLETADO:**
- ✅ `registry.py` YA usa `PostgresDocumentRegistry` (SQLite retired in §3.4)
- ✅ `postgres_registry.py` completamente implementado
- ✅ `profile_store.py` YA usa `PostgresProfileStore` (SQLite retired in §3.4)
- ✅ `kg_writer.py` YA usa `PostgresKGWriter` (Neo4j retired in §3.3)

**PENDIENTE:**
- ❌ Método `build_profiles` en `pipeline.py` aún lee de Neo4j/SQLite (líneas 1652-1807)
- ❌ Referencias a Neo4j en comentarios y código en `pipeline.py`
- ❌ Validar que no hay otras referencias a Neo4j/SQLite en write path

### Tareas Detalladas

#### Día 1: Migrar build_profiles (1 día)

**Tarea 1.1:** Analizar método `build_profiles`
- [ ] Leer método `build_profiles` completo en `pipeline.py` (líneas 1652-1807)
- [ ] Entender qué hace: "Build metadata-only entity profiles from Neo4j + SQLite"
- [ ] Identificar qué queries hace a Neo4j y SQLite
- [ ] Determinar si es necesario o puede eliminarse

**Tarea 1.2:** Migrar build_profiles a Postgres
- [ ] Reescribir queries de Neo4j a Postgres (entities, relations, mentions)
- [ ] Reescribir queries de SQLite a Postgres (text snippets)
- [ ] Implementar usando `postgres_graph_client.py` y Postgres queries
- [ ] Validar que produce resultados equivalentes

**Tarea 1.3:** Integrar con Postgres profile store
- [ ] Usar `PostgresProfileStore` en lugar de SQLite
- [ ] Validar que `_staging_profiles` no es necesario (si existe)
- [ ] Tests de integración

**Entregable:** `build_profiles` migrado a Postgres

---

#### Día 1-2: Cleanup de referencias Neo4j (0.5 días)

**Tarea 2.1:** Actualizar comentarios en pipeline.py
- [ ] Reemplazar referencias a "Neo4j" con "Postgres"
- [ ] Actualizar descripciones de Phase 3 (líneas 374, 555, 755, 1017)
- [ ] Actualizar descripciones de skip_kg (línea 228)
- [ ] Actualizar descripción de build_profiles (línea 1652)

**Tarea 2.2:** Validar no hay otras referencias
- [ ] Buscar "Neo4j" en todo `src/alejandria/ingestion/`
- [ ] Buscar "sqlite" en `pipeline.py` (excepto imports históricos)
- [ ] Validar que no hay código condicional que aún use Neo4j/SQLite

**Tarea 2.3:** Remover código obsoleto
- [ ] Remover imports no usados de Neo4j/SQLite
- [ ] Remover código condicional obsoleto
- [ ] Validar que tests pasan

**Entregable:** `pipeline.py` sin referencias a Neo4j/SQLite

---

#### Día 2: Tests y Validación (0.5 días)

**Tarea 3.1:** Tests de build_profiles
- [ ] Test unitario de `build_profiles` con Postgres
- [ ] Validar paridad con versión anterior (si hay baseline)
- [ ] Validar performance vs baseline

**Tarea 3.2:** Smoke test
- [ ] Correr ingesta completa con subset pequeño de corpus
- [ ] Validar que `build_profiles` funciona correctamente
- [ ] Validar que no hay errores de Neo4j/SQLite

**Entregable:** Suite de tests y smoke test pasando

---

### Criterios de Aceptación

- [ ] Todos los tests pasan
- [ ] Ingesta completa con Postgres produce resultados equivalentes a SQLite/Neo4j
- [ ] Performance ≥ baseline (no degradation significativa)
- [ ] Feature flag funciona correctamente
- [ ] Documentación actualizada

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|-------|-------------|---------|------------|
| `_staging_profiles` complejo de migrar | Media | Alto | Investigar temprano, tener plan B |
| Performance degradation con COPY | Baja | Medio | Benchmark antes/después, optimizar batch size |
| Bugs en paridad de datos | Media | Alto | Tests exhaustivos, validación manual de subset |

---

## PR #1: postgres-kg-client-rest (COMPLETADO)

### Objetivo
Completar el port del KG client a Postgres (métodos restantes).

### Estado Actual (Actualizado 2026-05-17)

**YA COMPLETADO:**
- ✅ Tier 2a (3 métodos): `graph_summary`, `find_node`, `get_neighbors` - IMPLEMENTADOS
- ✅ Tier 2c mentions-based (4 métodos): `get_documents_for_entity`, `get_documents_for_entities_batch`, `get_all_entity_mentions`, `get_disambiguated_counts` - IMPLEMENTADOS
- ✅ Tier 2c relation-based (4 métodos): `find_nodes_batch`, `get_typed_relations`, `get_typed_relations_batch`, `get_parallel_passages` - IMPLEMENTADOS
- ✅ Tier 2d (2 métodos): `get_genealogy_tree`, `get_genealogy_path` - IMPLEMENTADOS
- ✅ NO hay métodos con `NotImplementedError`

**PENDIENTE:**
- ❌ Ninguno - KG client completamente implementado

---

## KG Refactor R1-R3 (MEDIA - 0.5 días)

### Objetivo
Completar el refactor del KG según backlog R1-R3.

### Estado Actual (Actualizado 2026-05-17)

**YA COMPLETADO:**
- ✅ R1: Filtro global de gazetteer (en código - `gazetteer_lookup.should_skip_ner_entity()`)
- ✅ R2: Retention policy (en código - `prune_low_value(min_freq=3, max_age_days=30)`)
- ✅ R3: Normalización al insertar (en código - `is_garbage()`)

**PARCIALMENTE PENDIENTE:**
- ⚠️ R5: Cross-language honorifics - expandido para "Iglesia", pendiente honorificos tipo "Señor Jesucristo", "Su Hijo Jesucristo"

**PENDIENTE:**
- ❌ Ninguno de R1-R3 - ya completados

### Tareas Detalladas

**Tarea única:** Completar R5 honorifics
- [ ] Agregar honorificos cross-language: "Señor Jesucristo", "Su Hijo Jesucristo", etc.
- [ ] Extender `gazetteer_lookup.normalize` para strip de honorificos
- [ ] Validar que merge funciona correctamente
- [ ] Tests de integración

---

## Cronograma Sugerido

### Día 1 (0.5 días)

| Día | Tarea | Responsable |
|-----|-------|-------------|
| Día 1 | R5: Cross-Language Honorific Merge | Dev |

**Entregable:** R5 honorifics completado

---

## Próximos Pasos Después de Completar Blockers

Una vez completados los blockers, se puede proceder con:

1. **Fase 0:** Validación de Stack Postgres (0.5 días)
2. **Fase 1-6:** Workspace Migration (5-7 días)
3. **PR #3:** postgres-cutover (opcional, 1-2 semanas)

---

## Recursos de Referencia

- `docs/postgres-migration-status.md` - Estado actual de migración
- `docs/postgres-migration.md` - Plan maestro de migración
- `docs/kg-client-port-audit.md` - Auditoría pre-port de KG client
- `docs/kg-ingestion-refactor.md` - Backlog R0-R10 de hygiene del KG
- `src/alejandria/knowledge/postgres_graph_client.py` - Implementación actual
- `src/alejandria/ingestion/postgres_registry.py` - Implementación actual

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-05-17 | Versión inicial del plan de trabajo | JPMarichal |
