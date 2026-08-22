# PPR Implementation Plan — Alejandría Graph-Enhanced RAG

**Objetivo:** Implementar Personalized PageRank (PPR) sobre el knowledge graph existente en Postgres para habilitar retrieval multi-hop eficiente.

**Alcance:** PPR como modo de retrieval adicional dentro de `chat_ask` y como endpoint experimental en `/search/graph/pagerank`.

**Fecha de inicio:** 2026-08-22  
**ETA completitud:** 2026-09-05 (2 semanas)

---

## Fase 0: Medición baseline (Día 1-2)

### Tareas

1. **Medir tamaño del KG**
   - Query: `SELECT count(*) FROM entities` y `SELECT count(*) FROM relations`
   - Calcular grado promedio: `SELECT avg(degree) FROM (SELECT count(*) as degree FROM relations GROUP BY src_id) t`
   - Determinar si el grafo cabe en memoria (criterio: < 500K nodos, < 2M aristas)

2. **Medir latencia baseline de `chat_ask`**
   - Ejecutar 10 queries multi-hop etiquetadas (ej: "¿Cómo se relaciona la ley de Moisés con la expiación?")
   - Registrar: latencia P50/P95, tokens consumidos, recall@10

3. **Evaluar densidad del grafo**
   - Si grado promedio < 2: considerar agregar co-occurrence edges antes de PPR
   - Si grado promedio >= 2: proceder con PPR directo

**Entregable:** Documento `docs/architecture-proposals/ppr-baseline-metrics.md` con métricas baseline.

**ETA:** 2 días

---

## Fase 1: Prototipo PPR in-memory (Día 3-7)

### Tareas

1. **Implementar `src/alejandria/knowledge/pagerank.py`** ✅ DONE
   - `_load_graph_from_postgres()`: carga grafo desde tabla `relations`
   - `_resolve_entity_ids()`: resuelve nombres a ids via gazetteer + ILIKE
   - `pagerank_search()`: algoritmo power iteration con NetworkX
   - Soporte para personalization vector, damping factor, max_iter, tol

2. **Implementar endpoint experimental**
   - `POST /search/graph/pagerank` en `routes_graph.py` ✅ DONE
   - Request: `{"query_entities": [...], "alpha": 0.5, "top_k": 20}`
   - Response: lista de entidades rankeadas con score y chunk_count

3. **Tests unitarios**
   - `tests/knowledge/test_pagerank.py`
   - Test 1: grafo pequeño conocido, verificar scores PPR
   - Test 2: seed entities no existentes → retorno vacío
   - Test 3: grafo con 3 nodos en línea, seed en extremo → scores decrecen correctamente
   - Test 4: alpha=0 → random walk uniforme
   - Test 5: alpha=1 → solo seeds tienen score

4. **Integración manual**
   - Probar endpoint con curl/Postman contra API corriendo
   - Validar tiempos de respuesta con KG real

**Entregable:** Módulo PPR funcionando + endpoint experimental + tests unitarios.

**ETA:** 5 días

---

## Fase 2: Integración con `chat_ask` (Día 8-10)

### Tareas

1. **Modo experimental en `chat_ask`**
   - Agregar parámetro `graph_mode: str = "auto"` al request de chat
   - Valores: `auto`, `vector_only`, `ppr`, `hybrid`
   - `auto`: clasifica query; si es multi-hop, usa PPR expansion
   - `ppr`: fuerza PPR expansion sobre vector seeds
   - `hybrid`: fusiona vector results + PPR results

2. **Clasificador de queries (simple)**
   - Reglas + LLM ligero para detectar si la query es multi-hop
   - Heurísticas iniciales: presencia de múltiples entidades conocidas, palabras clave ("relación", "conecta", "cómo se relaciona")
   - Si confianza < 0.6, fallback a hybrid

3. **Fusión de resultados**
   - Vector search: top-k chunks por embedding similarity
   - PPR: top-k entities por pagerank score → chunks asociados
   - Fusión: Reciprocal Rank Fusion (RRF) o weighted sum

4. **Tests de integración**
   - Test end-to-end: `chat_ask` con `graph_mode=ppr` sobre query multi-hop
   - Comparar resultados vs. `graph_mode=vector_only`

**Entregable:** `chat_ask` con modo PPR experimental + clasificador de queries + tests E2E.

**ETA:** 3 días

---

## Fase 3: Optimización y hardening (Día 11-12)

### Tareas

1. **Caching de grafo**
   - Cachear el grafo en memoria (NetworkX) con TTL de 5 minutos
   - Invalidar cache cuando se detecte cambio en `schema_version` o `relations`
   - Esto evita cargar el grafo completo en cada request

2. **Subgraph loading inteligente**
   - En lugar de cargar todo el grafo, cargar solo:
     a. Entidades semilla (resueltas desde la query)
     b. Sus vecinos directos (1-hop)
     c. Vecinos de vecinos (2-hop)
   - Query SQL: `SELECT src_id, dst_id FROM relations WHERE src_id = ANY(%s) OR dst_id = ANY(%s)`
   - Limitar a 50K edges por request

3. **Métricas y logging**
   - Loggear: entidades semilla, nodos cargados, aristas, iteraciones PPR, latencia total
   - Agregar métricas a `/health` o endpoint dedicado

4. **Documentación**
   - Actualizar `docs/architecture-proposals/graph-enhanced-rag-evaluation.md` con resultados
   - Documentar endpoint en `docs/api-reference.md`

**Entregable:** PPR production-ready con caching, subgraph loading, y métricas.

**ETA:** 2 días

---

## Resumen de timeline

| Fase | Descripción | Días | ETA |
|------|-------------|------|-----|
| 0 | Medición baseline | 1-2 | 2026-08-23 |
| 1 | Prototipo PPR + endpoint + tests | 3-7 | 2026-08-28 |
| 2 | Integración chat_ask + clasificador | 8-10 | 2026-08-31 |
| 3 | Optimización + hardening + docs | 11-12 | 2026-09-05 |

**Total: 12 días hábiles (2 semanas)**

---

## Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| KG demasiado grande para memoria | Media | Alto | Medir en Fase 0; si > 500K nodos, implementar CTE recursiva en Postgres. |
| PPR no mejora recall vs. vector | Baja | Alto | Evaluar en Fase 1 con queries etiquetadas; si no mejora, ajustar alpha o agregar pesos. |
| Latencia PPR > 500ms | Media | Medio | Subgraph loading + caching en Fase 3; medir en cada fase. |
| Entity resolution falla | Baja | Medio | Usar gazetteer existente; agregar fallback a ILIKE. |
| Drift en KG | Baja | Bajo | PPR es solo lectura; no afecta escritura. |

---

## Criterios de éxito

| Métrica | Baseline | Objetivo |
|---------|----------|----------|
| Recall@10 multi-hop | TBD (Fase 0) | +15% |
| Tokens/query multi-hop | TBD (Fase 0) | -30% |
| Latencia P95 PPR | N/A | < 500ms overhead |
| Tiempo carga grafo | N/A | < 2s (con caching) |
| Cobertura seeds | N/A | > 90% seeds resueltos a entidades |

---

## Próximos pasos después de PPR

1. **Incremental KG updates** (Jigsaw-LightRAG pattern)
2. **Community detection + summarization** (Leiden sobre KG existente)
3. **Query router adaptativo** (clasificar queries → vector / graph / hybrid)

Ver `docs/architecture-proposals/graph-enhanced-rag-evaluation.md` para el roadmap completo.
