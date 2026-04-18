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

## 5. Relación con otros docs

- `docs/postgres-migration.md` — plan general de la migración; este es la fase 0 del último módulo grande.
- `docs/kg-ingestion-refactor.md` — backlog R0-R8; este audit es en efecto el paso previo a "R9 port del cliente".
- `docs/project-memory/feedback_docs_sync.md` — la regla de mantener docs al día que gatilló este doc.
- `docs/project-memory/feedback_preseed_before_discovery.md` — el principio de Fase 0: preparar antes de ejecutar. Este doc lo aplica al port.
