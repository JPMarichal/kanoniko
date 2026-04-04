---
name: documentation-first
description: Protocolo obligatorio de investigación documentation-first. Activar ANTES de cualquier web search cuando la pregunta pueda estar cubierta por el corpus de Alejandría (escrituras, manuales de la Iglesia, conferencias generales, doctrina) o por la documentación técnica del workspace (knowledge-assistant-mcp). El orden es siempre corpus local → KBA → web.
---

# Documentation-First Research Protocol

Protocolo obligatorio que establece el orden de consulta para cualquier investigación o pregunta. **El corpus local y la documentación indexada siempre se consultan primero; la web es complemento, no fuente primaria.**

---

## Principio

Si el corpus existe y está indexado, usarlo. De otra manera, carece de sentido tener corpus, KBA e índices.

---

## Fuentes Disponibles y Su Cobertura

### 1. Alejandría (corpus doctrinal/religioso)

**Herramientas MCP:** `mcp__alejandria__*`

| Herramienta | Uso |
|:------------|:----|
| `chat_ask` | RAG completo: búsqueda + KG + reranking + respuesta con citas. **La más poderosa para preguntas complejas.** |
| `search_hybrid` | Búsqueda textual + semántica. Ideal para explorar qué hay disponible sobre un tema. |
| `search_semantic` | Solo búsqueda semántica. Útil cuando los términos exactos varían. |
| `search_text` | Solo búsqueda textual. Útil para citas exactas o referencias específicas. |
| `kg_find` | Buscar entidades (personas, lugares, conceptos) en el knowledge graph. |
| `kg_profile` | Perfil enriquecido de una entidad (~400 entidades principales). |
| `kg_neighbors` | Entidades conectadas a una entidad dada (1-3 niveles de profundidad). |
| `kg_relations` | Relaciones tipadas de una entidad (parentesco, autoría, sacerdocio, etc.). |
| `kg_docs` | Documentos del corpus que mencionan una entidad específica. |
| `corpus_status` | Estado del sistema (documentos, chunks, vectores, nodos). |
| `kg_summary` | Estadísticas del knowledge graph. |

**Cobertura del corpus:**
- Manual General / General Handbook (ES + EN, actualizado a marzo 2026)
- Discursos de conferencia general (históricos y recientes)
- Escrituras (Biblia, Libro de Mormón, Doctrina y Convenios, Perla de Gran Precio)
- Manuales de estudio (Ven Sígueme, Instituto, Seminario, Enseñanzas de Presidentes)
- Otros materiales oficiales de la Iglesia

### 2. Knowledge Assistant (documentación técnica del workspace)

**Herramientas MCP:** `mcp__knowledge-assistant-mcp__*`

| Herramienta | Uso |
|:------------|:----|
| `search_documentation` | Búsqueda semántica en `_gitDocs/`, `.docs/`, `.agent/`, `.github/` |
| `search_code_symbols` | Búsqueda de símbolos de código (clases, funciones, métodos) |
| `index_status` | Estado del índice de documentación |

**Cobertura:** Documentación técnica del workspace de desarrollo (arquitectura, procedimientos, patrones, flujos de datos).

### 3. Web Search

**Herramienta:** `WebSearch`

**Cobertura:** Todo lo que NO está en los corpus anteriores:
- Manuales obsoletos/descontinuados (pre-2010)
- Noticias y artículos de Church News, Deseret News, etc.
- Artículos académicos y de terceros
- Información secular/técnica general
- Eventos recientes no indexados aún

---

## Protocolo de Ejecución

### Paso 1 — Clasificar la pregunta

Antes de buscar, determinar la **naturaleza** de la pregunta:

| Tipo de pregunta | Fuente primaria | Fuente complementaria |
|:-----------------|:----------------|:----------------------|
| Doctrina, escrituras, enseñanzas proféticas | Alejandría (`chat_ask` o `search_hybrid`) | Web solo si el corpus no cubre |
| Manual General / políticas actuales de la Iglesia | Alejandría (`search_hybrid` con `source_filter`) | Web para contexto histórico |
| Historia de cambios en la Iglesia | Alejandría primero → Web para lo no indexado | Ambas se complementan |
| Discursos de conferencia general | Alejandría (`search_hybrid` o `kg_docs`) | Web solo para conferencias muy recientes |
| Documentación técnica del workspace | Knowledge Assistant (`search_documentation`) | N/A |
| Código fuente y símbolos | Knowledge Assistant (`search_code_symbols`) + Grep/Glob | N/A |
| Información secular, noticias, artículos externos | Web Search directamente | N/A |

### Paso 2 — Consultar corpus local PRIMERO

**Para preguntas doctrinales/eclesiásticas:**

```
1. mcp__alejandria__search_hybrid  → explorar qué hay sobre el tema (limit: 10-15)
2. mcp__alejandria__chat_ask       → si necesitas una respuesta articulada con citas
3. mcp__alejandria__kg_find        → si hay entidades relevantes (personas, conceptos)
4. mcp__alejandria__kg_profile     → para entidades principales (~400 disponibles)
```

**Para preguntas técnicas del workspace:**

```
1. mcp__knowledge-assistant-mcp__search_documentation → buscar en docs indexados
2. Grep / Glob → buscar en código fuente
```

### Paso 3 — Evaluar cobertura

Después de consultar el corpus, evaluar:

- **Cobertura completa:** El corpus respondió la pregunta. → Responder sin web search.
- **Cobertura parcial:** El corpus tiene parte de la información. → Complementar con web search **solo para lo faltante**.
- **Sin cobertura:** El tema no está en el corpus. → Proceder con web search.

**Documentar la decisión internamente:** "El corpus cubre X pero no Y; busco Y en la web."

### Paso 4 — Complementar con web (solo si es necesario)

Cuando se use web search como complemento:
- Ser específico en las queries (no repetir lo que el corpus ya respondió).
- Priorizar fuentes oficiales (churchofjesuschrist.org, newsroom, thechurchnews.com).
- Citar tanto fuentes del corpus como de la web en la respuesta.

---

## Reglas de Oro

1. **Nunca hacer web search sin haber consultado el corpus primero** (cuando la pregunta entra en su cobertura).
2. **Alejandría es la fuente de verdad** para material actual de la Iglesia. La web complementa con contexto histórico y artículos de terceros.
3. **Si el corpus tiene la respuesta, no buscar en la web.** Evitar búsquedas redundantes.
4. **Usar `chat_ask` para preguntas complejas** que requieren síntesis de múltiples fuentes dentro del corpus.
5. **Usar `search_hybrid` para exploración** cuando no se sabe qué hay disponible sobre un tema.
6. **Usar el knowledge graph** (`kg_find`, `kg_profile`, `kg_relations`) para preguntas sobre personas, relaciones, y conceptos doctrinales.

---

## Anti-patrones (NO hacer)

- ❌ Ir directo a web search para preguntas sobre el Manual General.
- ❌ Hacer 5+ web searches sin haber consultado Alejandría una sola vez.
- ❌ Ignorar el knowledge graph cuando la pregunta es sobre una persona o concepto específico.
- ❌ Usar web search para buscar escrituras o discursos de conferencia general.
- ❌ Duplicar búsquedas: si el corpus ya respondió, no buscar lo mismo en la web.

---

## Checklist Rápido

- [ ] Clasifiqué la pregunta (doctrinal, técnica, secular, histórica)
- [ ] Consulté el corpus apropiado PRIMERO (Alejandría o KBA)
- [ ] Evalué la cobertura antes de decidir si complementar con web
- [ ] Si usé web, fue solo para lo que el corpus no cubría
- [ ] En la respuesta, cité fuentes del corpus cuando las usé
