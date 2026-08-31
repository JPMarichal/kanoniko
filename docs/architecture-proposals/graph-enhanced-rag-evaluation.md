# Graph-Enhanced RAG: Evaluación de alternativas y hoja de ruta para Alejandría

**Estado:** Propuesta  
**Fecha:** 2026-08-22  
**Autores:** Juan Pablo Marichal + investigación de campo  
**Ámbito:** Arquitectura de búsqueda y recuperación (RAG pipeline)

---

## 1. Contexto y motivación

Alejandría cuenta con un stack de recuperación híbrida funcional: FTS5 (tsvector), embeddings (`paraphrase-multilingual-MiniLM-L12-v2`), knowledge graph en Postgres 16 + pgvector (67 relation types, 12 categorías, 6 tiers de confianza), y MCP tools nativas (`kg_relations`, `kg_profile`, `kg_neighbors`, `search_hybrid`, `chat_ask`).

Sin embargo, existen gaps reconocidos:

- **Preguntas globales/comprehensivas** ("¿cuáles son los temas doctrinales principales del Libro de Mormón?") no tienen un retrieval mode dedicado.
- **Razonamiento multi-hop** depende de que el LLM infiera conexiones en el prompt, no de traversal estructurado sobre el grafo.
- **Actualizaciones incrementales del KG** no están implementadas; se desconoce el comportamiento actual ante ingestiones parciales.

Este documento evalúa si herramientas emergentes (Graphify, GraphRAG) cierran esos gaps, y define un plan de acción realista.

---

## 2. Alternativas evaluadas y descartadas

### 2.1 Graphify (`graphifyy` / Graphify-Labs)

| Dimensión | Evaluación |
|-----------|------------|
| **Dominio** | Diseñado para codebases (tree-sitter AST, imports, call graphs). No aplica a corpus textual doctrinal. |
| **Extracción KG** | Genérica por LLM. Pierde los 7 gazetteers y 67 relation types específicos del dominio SUD ya invertidos en Alejandría. |
| **Store** | `graph.json` (NetworkX) o Neo4j. Alejandría retiró Neo4j en §3.3; Postgres es la fuente única de verdad. |
| **Referencias versiculares** | No entiende formato `1 Nefi 3:7` ni estructura volumen/libro/capítulo. |
| **Incremental** | Basado en git hooks + SHA256. El corpus de Alejandría es bind-mounted y ya tiene SHA-256 change detection propio. |
| **Veredicto** | **No adoptar.** No resuelve ningún gap y representa regresión en especificidad doctrinal y madurez del stack. |

### 2.2 GraphRAG completo (Microsoft)

| Dimensión | Evaluación |
|-----------|------------|
| **Extracción KG** | Reemplazaría spaCy + gazetteers por extracción LLM genérica. Costo de indexación alto (~$4–7 vs ~$0.15 con enfoques ligeros). |
| **Store** | Asume graph DB separada (Neo4j/FalkorDB). Alejandría no necesita otro store. |
| **Actualizaciones** | Requiere reextracción completa del grafo ante cambios. Incompatible con incremental ingestion existente. |
| **Precisión doctrinal** | Un extractor genérico no captura entidades específicas del dominio SUD con la precisión de los gazetteers actuales. |
| **Valor agregado único** | Community detection + resúmenes jerárquicos. Todo lo demás ya existe en Alejandría. |
| **Veredicto** | **No adoptar como reemplazo.** Es posible adoptar selectivamente la capa de community detection (§4.3) sin reemplazar el stack. |

---

## 3. Propuestas viables priorizadas

### 3.1 PPR sobre el KG existente (HippoRAG / TERAG pattern)

**Objetivo:** Habilitar retrieval multi-hop eficiente sin reextraer el grafo.

**Descripción:**
```
1. Vector search (search_hybrid) encuentra chunks semilla.
2. Se extraen entidades de la pregunta con LLM ligero (o NER local).
3. Personalized PageRank se ejecuta sobre el grafo de Postgres:
   - Los nodos entidad semilla reciben score inicial.
   - El score se propaga por las aristas (relaciones) del KG.
   - Se recuperan los chunks asociados a las entidades con mayor PPR score.
4. El LLM genera respuesta con el contexto expandido.
```

**Beneficios:**
- **Tokens:** PPR es matemático puro; cero LLM calls en retrieval.
- **Velocidad:** Un paso de traversión vs. múltiples iteraciones de agentic RAG.
- **Precisión:** Encuentra caminos multi-hop que vector search pierde.

**Esfuerzo:** Bajo. Agrega una CTE recursiva o procedimiento almacenado en Postgres. No requiere nuevos stores.

**Riesgos:**
- El KG actual debe estar suficientemente denso para que PPR propague scores útiles. Si hay pocas relaciones por entidad, el efecto se diluye.
- Mitigación: medir grado promedio de nodos antes de implementar; si es bajo, complementar con co-occurrence edges.

**Métricas de éxito:**
- Recall@10 en queries multi-hop: +15% vs. baseline vector-only.
- Tokens por query multi-hop: -30%.
- Latencia P95: < 500ms overhead vs. baseline.

---

### 3.2 Incremental KG updates (Jigsaw-LightRAG pattern)

**Objetivo:** Actualizar el KG solo para documentos delta, sin rebuild completo.

**Descripción:**
```
Documento nuevo/modificado → detectado por SHA-256 (ya existe).
  → Extraer entidades/relaciones solo de ese documento.
  → Resolver entidades contra el KG existente (entity resolution).
  → Solo re-validar entidades/relaciones tocadas.
  → Documentos sin cambios: reusar subgrafo, cero costo.
```

**Beneficios:**
- **Velocidad:** Indexación de un archivo nuevo: ~2-3s (hoy) + extracción KG delta (segundos).
- **Tokens:** Cero costo en documentos sin cambios.
- **Precisión:** Menos drift por reextracción completa; preserva correcciones humanas.

**Esfuerzo:** Medio. Requiere un pipeline de delta extraction y un merge resolver contra Postgres.

**Riesgos:**
- Entity resolution imperfecta puede crear duplicados en ingesta incremental.
- Mitigación: usar el mismo resolver que el ingestion pipeline actual; agregar validación de duplicados post-merge.

**Métricas de éxito:**
- Tiempo de ingesta incremental: < 5s por archivo (incluyendo KG update).
- Costo de tokens en ingesta: 0 para archivos sin cambios.
- Paridad de calidad: KG después de 15 iteraciones incrementales = KG de rebuild completo (medir por ED3 o similar).

---

### 3.3 Community detection + summarization (GraphRAG local/global search)

**Objetivo:** Responder preguntas comprehensivas sobre el corpus usando resúmenes jerárquicos de comunidades doctrinales.

**Descripción:**
```
1. Batch job: extraer grafo de entidades/relaciones desde Postgres.
2. Aplicar algoritmo Leiden (o CPM) sobre el grafo.
3. Por cada comunidad: generar resumen con LLM (nombre, entidades clave, hallazgos).
4. Guardar comunidades y resúmenes en Postgres.
5. Nueva MCP tool: kg_global_search(query)
   - Clasifica si es local o global.
   - Local: usa kg_relations/kg_neighbors existentes.
   - Global: recupera resúmenes de comunidades relevantes, genera respuesta agregada.
```

**Beneficios:**
- **Precisión en preguntas globales:** Mejora 50-70% en comprehensividad vs. RAG puro (dato de Microsoft).
- **Tokens en consulta:** Resúmenes compactos vs. recuperar cientos de chunks.

**Esfuerzo:** Medio. Requiere implementar Leiden en Python (graspologic o networkx-backbone), job batch de generación de resúmenes, y nueva MCP tool.

**Riesgos:**
- Comunidades muy grandes o muy pequeñas degradan la calidad de los resúmenes.
- Mitigación: tuning de resolución Leiden; max_cluster_size; excluir utility hubs del ranking.

**Métricas de éxito:**
- Cobertura: % de entidades cubiertas por al menos una comunidad (>95% objetivo).
- Calidad de resúmenes: evaluación humana o RAGAS sobre un set de preguntas globales.
- Latencia de kg_global_search: < 2s P95.

---

### 3.4 Fine-tuning de NER/RE en dominio doctrinal

**Objetivo:** Mejorar la precisión de extracción de entidades y relaciones específicas del dominio SUD.

**Descripción:**
```
1. Usar el KG curado existente (6 tiers) como dataset de entrenamiento.
2. Generar pares (texto, entidades, relaciones) del corpus.
3. Fine-tune de NER (entity types) y RE (relation types) sobre modelo compacto
   (DeBERTa-v3-base, Llama 3.x 8B, o Qwen 2.5 7B).
4. Pipeline híbrido: NER fino para recall alto + gazetteers/reglas para precisión.
5. LLM grande solo para casos ambiguos (fallback).
```

**Beneficios:**
- **Precisión:** Mejora la extracción de entidades doctrinales específicas.
- **Tokens:** Reduce dependencia de LLM calls en indexación.
- **Velocidad:** Modelo local vs. API calls.

**Esfuerzo:** Alto. Requiere dataset de entrenamiento, infra de fine-tuning, y validación.

**Riesgos:**
- Overfitting al corpus actual; dificultad para generalizar a nuevos documentos.
- Mitigación: data augmentation con sinónimos y paráfrasis; validación hold-out en documentos no vistos.

**Métricas de éxito:**
- F1 de NER en test set doctrinal: > 0.90.
- Reducción de llm_high/llm_low tiers en favor de ner/co_occurrence de mayor confianza.
- Costo de indexación: -40% vs. pipeline actual.

---

### 3.5 Query Router adaptativo

**Objetivo:** Asignar cada pregunta al modo de retrieval óptimo.

**Descripción:**
```
User query → Query Classifier (LLM ligero o reglas)
  ├── Factoid / verse lookup → FTS5 exacto o vector simple
  ├── Entity-centric → kg_profile + kg_relations
  ├── Multi-hop / relational → Vector seed → Graph expansion (PPR o traversal)
  ├── Global / thematic → Community summaries (si existen) o search_hybrid ampliado
  └── Ambiguous → Ejecutar ambos paths y fusionar
```

**Beneficios:**
- **Velocidad:** Preguntas simples sin overhead de graph traversal.
- **Tokens:** No gasta tokens en modos costosos cuando no son necesarios.
- **Precisión:** Cada query type usa el retrieval mode óptimo.

**Esfuerzo:** Medio. Requiere clasificador de queries y routing logic en el API gateway o en `chat_ask`.

**Riesgos:**
- Clasificación errónea enruta a modo subóptimo.
- Mitigación: fallback a hybrid path ante baja confianza; logging de clasificación para iterar.

**Métricas de éxito:**
- Latencia P95 de factoid queries: < 200ms.
- Precisión por modo: mejora >5% vs. modo único para todos los queries.
- Tasa de fallback a hybrid: < 10%.

---

## 4. Comparativa de propuestas

| Propuesta | Impacto tokens | Impacto velocidad | Impacto precisión | Esfuerzo | Compatibilidad |
|-----------|----------------|-------------------|-------------------|----------|----------------|
| **3.1 PPR sobre KG** | Alto | Alto | Alto | Bajo | ✅ Directa |
| **3.2 Incremental KG** | Alto | Alto | Medio | Medio | ✅ Directa |
| **3.3 Community detection** | Medio | Medio | Alto | Medio | ✅ Directa |
| **3.4 Fine-tune NER/RE** | Alto | Alto | Alto | Alto | ⚠️ Requiere dataset |
| **3.5 Query Router** | Alto | Alto | Alto | Medio | ✅ Directa |

---

## 5. Hoja de ruta

### Fase 1 — Quick wins (semanas 1-4)

1. **Implementar PPR sobre KG existente** (§3.1)
   - Medir grado promedio de nodos en el KG actual.
   - Implementar CTE recursiva o procedimiento almacenado para PPR.
   - Exponer como nuevo modo en `chat_ask` o como MCP tool experimental.
   - Evaluar en set de queries multi-hop etiquetadas.

2. **Diagnosticar incremental KG updates** (§3.2)
   - Auditar el pipeline de ingesta actual: ¿qué pasa con el KG cuando se agrega un archivo?
   - Documentar el estado actual (append? rebuild? no hace nada?).
   - Diseñar delta extraction + merge resolver.

### Fase 2 — Capacidades core (meses 2-4)

3. **Implementar incremental KG updates** (§3.2)
   - Construir delta extraction pipeline.
   - Integrar con el SHA-256 change detection existente.
   - Validar paridad con rebuild completo (ED3 o evaluación equivalente).

4. **Implementar query router** (§3.5)
   - Clasificador de queries (empezar con reglas + LLM ligero).
   - Routing a FTS5 / vector / graph / global.
   - Logging y métricas por modo.

### Fase 3 — Madurez (meses 5-8)

5. **Implementar community detection + summarization** (§3.3)
   - Batch job de Leiden sobre KG existente.
   - Generación de resúmenes de comunidades con LLM.
   - Nueva MCP tool `kg_global_search`.
   - Evaluación humana en preguntas doctrinales globales.

6. **Optimizar PPR + Router combinados**
   - PPR como modo de graph expansion en el router.
   - A/B testing de estrategias de fusión (vector + graph).

### Fase 4 — Excelencia (cuando haya dataset)

7. **Fine-tune de NER/RE doctrinal** (§3.4)
   - Solo después de tener dataset de entrenamiento suficiente.
   - Validación rigurosa en hold-out doctrinal.

---

## 6. Métricas de éxito globales

| Métrica | Baseline (hoy) | Objetivo Fase 2 | Objetivo Fase 3 |
|---------|---------------|-----------------|-----------------|
| Recall@10 multi-hop | TBD (medir) | +15% | +25% |
| Tokens/query multi-hop | TBD | -30% | -50% |
| Latencia P95 factoid | TBD | < 200ms | < 200ms |
| Latencia P95 multi-hop | TBD | < 500ms | < 500ms |
| Tiempo ingesta incremental | TBD | < 5s/archivo | < 5s/archivo |
| Cobertura communities | N/A | N/A | >95% entidades |
| Precisión NER doctrinal | TBD | N/A | F1 > 0.90 |

**Nota:** Las métricas baseline deben medirse antes de implementar cualquier cambio. Propuesta: crear un evaluation set de 100-300 queries doctrinales etiquetadas (inspirado en RAGAS / ED3) en Fase 1.

---

## 7. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| KG insuficientemente denso para PPR | Media | Alto | Medir grado promedio de nodos; agregar co-occurrence edges si es necesario. |
| Drift en KG incremental | Media | Medio | Validación periódica contra rebuild completo; entity resolution robusta. |
| Comunidades de baja calidad | Media | Medio | Tuning de resolución Leiden; excluir utility hubs; revisión humana de resúmenes. |
| Clasificación errónea de queries | Baja | Medio | Fallback a hybrid path; logging extensivo para iterar. |
| Overfitting en fine-tune NER/RE | Media | Medio | Data augmentation; validación hold-out; monitorear drift. |

---

## 8. Decisiones pendientes

1. **¿Implementar PPR en Postgres (CTE recursiva) o en aplicación (NetworkX)?**
   - Postgres: ventaja de ejecutar cerca de los datos; desventaja: CTE recursiva puede ser lenta en grafos grandes.
   - NetworkX: ventaja de flexibilidad; desventaja: necesita cargar el grafo en memoria.
   - **Recomendación:** Prototipo en NetworkX para medir performance; si el grafo cabe en memoria (< 1M nodos), migrar a procedimiento almacenado para producción.

2. **¿Usar algoritmo Leiden o CPM para community detection?**
   - Leiden: garantiza comunidades conectadas, más rápido.
   - CPM: produce jerarquías naturales, mejor para resúmenes multi-nivel.
   - **Recomendación:** Empezar con Leiden; evaluar CPM si se necesita mayor granularidad jerárquica.

3. **¿Dónde almacenar community summaries?**
   - Tabla `kg_communities` en Postgres (mantiene fuente única de verdad).
   - No Neo4j; no duplicar store.

4. **¿Query router en API (FastAPI) o en MCP server?**
   - API: acceso único para todos los clients.
   - MCP: cada tool individual decide.
   - **Recomendación:** Router en API (`chat_ask`), MCP tools consumen el modo ya resuelto.

---

## 9. Referencias

- Microsoft GraphRAG: https://github.com/microsoft/graphrag
- TERAG (Token-Efficient Graph RAG): arXiv 2509.18667
- HippoRAG (NeurIPS 2024): https://github.com/OSU-NLP-Group/HippoRAG
- LightRAG (HKUDS, EMNLP 2025): https://github.com/HKUDS/LightRAG
- Jigsaw-LightRAG (incremental KG): IOP Science 2026, doi:10.1088/3050-287X/ae4a3e
- Graphify: https://github.com/Graphify-Labs/graphify
- Graphify RAG (standalone): https://github.com/srt180/graphify-rag
- Production RAG 2026: https://1337skills.com/blog/2026-06-12-production-rag-2026-hybrid-search-reranking-graphrag/
- Hybrid RAG patterns: https://venturebeat.com/orchestration/architectural-patterns-for-graph-enhanced-rag-moving-beyond-vector-search-in-production
- RAG vs GraphRAG evaluation: arXiv 2502.11371

---

## 10. Seguimiento

| Fecha | Evento | Decisión |
|-------|--------|----------|
| 2026-08-22 | Creación del documento | Aprobado para Fase 1 |
| 2026-08-22 | Fase 0 completada | KG baseline: 8,894 nodes, 5,872 edges, avg degree 2.37. In-memory NetworkX viable. |
| 2026-08-22 | Fase 1 completada | PPR implementado en `src/alejandria/knowledge/pagerank.py`. Endpoint `/search/graph/pagerank`. 11 tests pasan. |
| 2026-08-22 | Fase 2 completada | `graph_mode` integrado en `chat_ask` via `RAGPipeline.ask()`. Modos: auto, vector_only, ppr, hybrid. |
| 2026-08-22 | Fase 3 completada | Graph caching con TTL 5min. Subgraph loading por seed neighborhood. Métricas baseline guardadas en `ppr-baseline-metrics.json`. |
| | | |
| | | |

**Template de reunión de seguimiento:**

```
Fecha:
Asistentes:
Revisión de métricas baseline:
  - Recall@10 multi-hop:
  - Tokens/query multi-hop:
  - Latencia P95 factoid:
  - Tiempo ingesta incremental:

Ajustes a propuestas:
  -

Nuevos riesgos identificados:
  -

Próxima revisión:
```

---

*Documento generado en sesión de investigación 2026-08-22. Actualizar en cada revisión de arquitectura.*
