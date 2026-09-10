# Propuestas Arquitectónicas — Alejandría

Propuestas y análisis para la evolución arquitectónica. **Son insumos, no planes vigentes** —
la autoridad y el estado de cada artefacto están en [`../planning-index.md`](../planning-index.md);
el estado real del sistema en [`../system-spec.md`](../system-spec.md).

## Documentos presentes

| Archivo | Tema | Estado |
|---|---|---|
| [graph-enhanced-rag-evaluation.md](graph-enhanced-rag-evaluation.md) | Evalúa Graphify / GraphRAG / PPR para cerrar gaps de multi-hop y preguntas globales | Propuesta (2026-08-22). Versión autoritativa de este análisis. |
| [ppr-implementation-plan.md](ppr-implementation-plan.md) | Plan de implementación de Personalized PageRank sobre el KG en Postgres | Activo (2026-08-22, ETA 2026-09-05). Plan de referencia para PPR. Módulo: `src/alejandria/knowledge/pagerank.py`. |
| [ppr-baseline-metrics.json](ppr-baseline-metrics.json) | Métricas baseline del KG para PPR (tamaño, grado, densidad) | Captura 2026-08-22. |

## Relacionado, fuera de este directorio

- [`../ARCHITECTURE_PLAN.md`](../ARCHITECTURE_PLAN.md) — propuesta de split a microservicios.
  **No adoptada** — ver el banner del propio doc y `planning-index.md` §Contradicciones.

> Nota: versiones anteriores de este índice listaban `ARCHITECTURE_IMPROVEMENT_CHECKLIST.md`,
> `REPOSITORY_SPLIT_PROPOSAL.md`, `REPOSITORY_SPLIT_ANALYSIS.md` y `APPLICATION_PRODUCTS_INTEGRATION.md`.
> Esos archivos no existen en el repo; su contenido quedó consolidado en `../ARCHITECTURE_PLAN.md`.
