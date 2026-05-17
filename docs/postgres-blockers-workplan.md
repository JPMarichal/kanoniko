# Plan de Trabajo: Pendientes Bloqueantes para Workspace Migration

> **Objetivo:** Completar los pendientes críticos de la migración a Postgres antes de iniciar la migración a workspace uv + hatch.
> 
> **Tiempo estimado total:** 7-11 días (secuencial)

---

## Resumen de Pendientes

| ID | Pendiente | Prioridad | Tiempo Estimado | Dependencias |
|----|-----------|-----------|-----------------|--------------|
| 1 | PR #2: postgres-write-path | CRÍTICO | 3-5 días | Ninguna |
| 2 | PR #1: postgres-kg-client-rest | ALTA | 3-4 días | Ninguna |
| 3 | KG Refactor R1-R3 | MEDIA | 1-2 días | PR #2 |

**Orden recomendado:** PR #2 → PR #1 → KG Refactor R1-R3

---

## PR #2: postgres-write-path (CRÍTICO - 3-5 días)

### Objetivo
Portar el write path de ingesta a Postgres para eliminar dependencia de SQLite/Neo4j en escritura.

### Estado Actual
- ✅ `postgres_registry.py` existe pero no está integrado
- ✅ `postgres_profile_store.py` existe
- ❌ `ingestion/registry.py` aún usa SQLite
- ❌ `ingestion/pipeline.py` aún usa Neo4j UNWIND
- ❌ `_staging_profiles` quedó del migrador SQLite

### Tareas Detalladas

#### Día 1: Refactor Registry (0.5 días)

**Tarea 1.1:** Crear driver abstracto para registry
- [ ] Crear `src/alejandria/ingestion/registry_driver.py` con Protocol
- [ ] Implementar `SQLiteRegistryDriver` (wrapper actual)
- [ ] Implementar `PostgresRegistryDriver` usando `postgres_registry.py`
- [ ] Actualizar `registry.py` para usar driver via feature flag

**Tarea 1.2:** Integrar postgres_registry
- [ ] Mover lógica de `postgres_registry.py` a `PostgresRegistryDriver`
- [ ] Validar que `postgres_registry.py` tiene todos los métodos necesarios
- [ ] Tests de integración para ambos drivers

**Entregable:** `registry.py` refactorizado con driver abstracto

---

#### Día 1-2: Refactor Profile Store (1 día)

**Tarea 2.1:** Resolver `_staging_profiles`
- [ ] Investigar qué es `_staging_profiles` y por qué quedó del migrador
- [ ] Determinar si es necesario en Postgres o puede eliminarse
- [ ] Implementar solución apropiada (migrar o eliminar)

**Tarea 2.2:** Integrar postgres_profile_store
- [ ] Validar que `postgres_profile_store.py` tiene todos los métodos necesarios
- [ ] Integrar con driver abstracto (similar a registry)
- [ ] Tests de integración para ambos stores

**Entregable:** `profile_store.py` refactorizado con driver abstracto

---

#### Día 2-3: Refactor Pipeline (1.5 días)

**Tarea 3.1:** Unificar write path
- [ ] Reemplazar Neo4j UNWIND con Postgres COPY por batch
- [ ] Implementar entity profiles staging + resolve a `entity_id`
- [ ] Actualizar `pipeline.py` para usar Postgres write path
- [ ] Feature flag para cambiar entre Neo4j/Postgres write path

**Tarea 3.2:** Optimizar batch size
- [ ] Determinar batch size óptimo para COPY (probablemente 1000-5000)
- [ ] Implementar retry logic para batches fallidos
- [ ] Monitorear memory usage durante ingesta

**Entregable:** `pipeline.py` con write path unificado a Postgres

---

#### Día 3-4: Tests de Ingesta (1 día)

**Tarea 4.1:** Tests unitarios
- [ ] Tests para `SQLiteRegistryDriver`
- [ ] Tests para `PostgresRegistryDriver`
- [ ] Tests para `SQLiteProfileStore`
- [ ] Tests para `PostgresProfileStore`

**Tarea 4.2:** Tests de integración
- [ ] Test de ingesta completa con Postgres (subset pequeño de corpus)
- [ ] Comparar resultados con SQLite/Neo4j baseline
- [ ] Validar paridad de datos (mismas entities, relations, mentions)

**Tarea 4.3:** Smoke test
- [ ] Correr `scripts/postgres_pipeline_e2e_smoke.py`
- [ ] Validar que no hay errores
- [ ] Medir performance vs baseline

**Entregable:** Suite de tests completa y smoke test pasando

---

#### Día 4-5: Validación y Cleanup (1 día)

**Tarea 5.1:** Validación
- [ ] Correr ingesta completa con `ALEJANDRIA_STORAGE_BACKEND=postgres`
- [ ] Validar 31 golden queries con overlap ≥ 80%
- [ ] Monitorear latencia y errores

**Tarea 5.2:** Cleanup
- [ ] Remover código obsoleto de SQLite/Neo4j write path
- [ ] Actualizar documentación
- [ ] Code review

**Entregable:** PR lista para merge

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

## PR #1: postgres-kg-client-rest (ALTA - 3-4 días)

### Objetivo
Completar el port del KG client a Postgres (métodos restantes).

### Estado Actual
- ✅ 3 métodos implementados: `close`, `graph_summary`, `find_node`, `get_neighbors`
- ❌ 30 métodos con `NotImplementedError`
- ❌ Tiers 2c (8 métodos), 2d (2 métodos), 2e (validación completa) pendientes

### Tareas Detalladas

#### Día 1: Tier 2c - Métodos Typed Relations (1.5 días)

**Tarea 1.1:** `get_typed_relations`
- [ ] Implementar query Postgres con `ORDER BY confidence`
- [ ] Validar paridad con Neo4j oracle
- [ ] Tests de integración

**Tarea 1.2:** `get_typed_relations_batch`
- [ ] Implementar batch query optimizado
- [ ] Validar paridad con Neo4j oracle
- [ ] Tests de integración

**Tarea 1.3:** `get_documents_for_entity`
- [ ] Implementar query con JOIN a `entity_document_mentions`
- [ ] Validar paridad con Neo4j oracle
- [ ] Tests de integración

**Tarea 1.4:** `get_documents_for_entities_batch`
- [ ] Implementar batch query optimizado
- [ ] Validar paridad con Neo4j oracle
- [ ] Tests de integración

**Tarea 1.5:** `get_all_entity_mentions`
- [ ] Implementar query a `entity_document_mentions`
- [ ] Validar paridad con Neo4j oracle
- [ ] Tests de integración

**Tarea 1.6:** `get_disambiguated_counts`
- [ ] Implementar query de agregación
- [ ] Validar paridad con Neo4j oracle
- [ ] Tests de integración

**Tarea 1.7:** `find_nodes_batch`
- [ ] Implementar batch query optimizado
- [ ] Validar paridad con Neo4j oracle
- [ ] Tests de integración

**Tarea 1.8:** `get_parallel_passages`
- [ ] Implementar query con layer filter
- [ ] Validar paridad con Neo4j oracle
- [ ] Tests de integración

**Nota:** Todos los métodos deben usar `ORDER BY confidence` (ver lección en `kg-client-port-audit.md §6.5ter`)

**Entregable:** 8 métodos de Tier 2c implementados

---

#### Día 2: Tier 2d - Métodos Genealogy (1 día)

**Tarea 2.1:** `get_genealogy_tree`
- [ ] Implementar recursive CTE para genealogía
- [ ] Agregar LIMIT intermedio para evitar explosión de resultados
- [ ] Aplicar confidence ordering en SELECT final
- [ ] Validar paridad con Neo4j oracle (arreglar divergencia q14)
- [ ] Tests de integración

**Tarea 2.2:** `get_genealogy_path`
- [ ] Implementar recursive CTE para pathfinding
- [ ] Agregar LIMIT intermedio
- [ ] Aplicar confidence ordering en SELECT final
- [ ] Validar paridad con Neo4j oracle
- [ ] Tests de integración

**Entregable:** 2 métodos de Tier 2d implementados

---

#### Día 3: Tier 2e - Validación Completa (1 día)

**Tarea 3.1:** Expandir `capture_oracle`
- [ ] Extender `capture_oracle` para los 31 queries del golden set
- [ ] Validar paridad completa de todos los métodos
- [ ] Documentar cualquier divergencia aceptable

**Tarea 3.2:** Tests de regresión
- [ ] Correr todos los 31 queries del golden set
- [ ] Validar overlap ≥ 80% para cada query
- [ ] Investigar y arreglar queries con overlap < 80%

**Entregable:** Validación completa de paridad

---

#### Día 3-4: Cleanup y Validación (0.5 días)

**Tarea 4.1:** Cleanup
- [ ] Remover código obsoleto de Neo4j client
- [ ] Actualizar documentación
- [ ] Code review

**Tarea 4.2:** Validación final
- [ ] Correr suite completa de tests
- [ ] Validar que no hay `NotImplementedError` restantes
- [ ] Validar performance vs baseline

**Entregable:** PR lista para merge

---

### Criterios de Aceptación

- [ ] Todos los 34 métodos implementados (sin `NotImplementedError`)
- [ ] Todos los tests pasan
- [ ] Paridad ≥ 80% con Neo4j oracle para golden set
- [ ] Performance ≥ baseline (no degradation significativo)
- [ ] Documentación actualizada

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|-------|-------------|---------|------------|
| Recursive CTE diverge de Neo4j | Media | Alto | Validar paridad temprano, ajustar queries |
| Performance degradation en batch queries | Baja | Medio | Benchmark antes/después, optimizar |
| Divergencias semánticas complejas | Baja | Alto | Documentar, no bloquear por divergencias no críticas |

---

## KG Refactor R1-R3 (MEDIA - 1-2 días)

### Objetivo
Completar limpieza del KG según backlog R1-R3 de `kg-ingestion-refactor.md`.

### Estado Actual
- ✅ R0 (garbage + merges canonical) completado
- ✅ R7 (kill CO_OCCURS_WITH + ASSOCIATED_WITH llm_low) completado
- ❌ R1, R2, R3 pendientes

### Tareas Detalladas

#### Día 1: R1 - Cross-Language Honorific Merge (0.5 días)

**Tarea 1.1:** Extender `gazetteer_lookup.normalize`
- [ ] Agregar strip de honoríficos en normalize
- [ ] Honoríficos a manejar: "Señor Jesucristo", "Su Hijo Jesucristo", etc.
- [ ] Validar que merge funciona correctamente
- [ ] Tests de integración

**Entregable:** R1 completado

---

#### Día 1: R2 - Retention Policy (0.5 días)

**Tarea 2.1:** Validar R2
- [ ] Verificar que `prune_low_value` se ejecuta al final de cada KG rebuild
- [ ] Validar que funciona correctamente
- [ ] Tests de integración

**Nota:** Según `postgres-migration-status.md`, R2 ya está implementado. Solo requiere validación.

**Entregable:** R2 validado

---

#### Día 1-2: R3 - Filtros en Ingesta (1 día)

**Tarea 3.1:** Validar filtros R1/R3
- [ ] Verificar que `gazetteer_lookup.py` está centralizado
- [ ] Validar que `extractor.py` usa gate unificado
- [ ] Validar que `ner_candidates.py` usa gate unificado
- [ ] Tests de integración

**Nota:** Según `postgres-migration-status.md`, filtros R1/R3 ya están implementados. Solo requiere validación.

**Entregable:** R3 validado

---

### Criterios de Aceptación

- [ ] R1: Honoríficos cross-language merge funcionando
- [ ] R2: Retention policy validada
- [ ] R3: Filtros en ingesta centralizados y validados
- [ ] Todos los tests pasan
- [ ] Documentación actualizada

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|-------|-------------|---------|------------|
| R1 introduce bugs en gazetteer lookup | Baja | Medio | Tests exhaustivos, validación manual |
| R2/R3 ya no aplican (código cambió) | Baja | Bajo | Investigar estado actual, adaptar |

---

## Cronograma Sugerido

### Semana 1 (5 días)

| Día | Tarea | Responsable |
|-----|-------|-------------|
| Lunes | PR #2: Día 1 - Refactor Registry | Dev |
| Martes | PR #2: Día 2 - Refactor Profile Store | Dev |
| Miércoles | PR #2: Día 3 - Refactor Pipeline | Dev |
| Jueves | PR #2: Día 4 - Tests de Ingesta | Dev |
| Viernes | PR #2: Día 5 - Validación y Cleanup | Dev |

**Entregable fin de semana 1:** PR #2 lista para merge

---

### Semana 2 (5 días)

| Día | Tarea | Responsable |
|-----|-------|-------------|
| Lunes | PR #1: Día 1 - Tier 2c (parte 1) | Dev |
| Martes | PR #1: Día 2 - Tier 2c (parte 2) | Dev |
| Miércoles | PR #1: Día 3 - Tier 2d + Tier 2e | Dev |
| Jueves | PR #1: Día 4 - Cleanup y Validación | Dev |
| Viernes | KG Refactor R1-R3 | Dev |

**Entregable fin de semana 2:** PR #1 lista para merge + KG Refactor R1-R3 completado

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
