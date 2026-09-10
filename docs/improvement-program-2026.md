# Programa de Modernización — Alejandría 2026

> **Tipo:** documento vivo de planificación y **tracking**. Actualizar el estado de los ítems y las
> tablas al avanzar.
> **Rationale:** [improvement-analysis-2026.md](improvement-analysis-2026.md) (SWOT, evidencia,
> tecnologías, evaluación del roadmap).
> **Autoridad y solapamientos:** [planning-index.md](planning-index.md). Estado actual del sistema:
> [system-spec.md](system-spec.md). Formato de proyectos: [`proj/CONVENTIONS.md`](../proj/CONVENTIONS.md).
> **Creado:** 2026-09-09 · **Última actualización:** 2026-09-09

---

## 0. Propósito y reglas de seguimiento

Dividir el "elefante" (deuda estructural + oportunidades tecnológicas 2026) en **7 fases**
secuenciadas, cada una con objetivo único, ítems con checkbox, dependencias y un **gate de salida**
verificable. Ninguna feature nueva de producto (P5 UI, P8 Synthesis) arranca hasta que las Fases
A–C pasen su gate. La cadena de corpus (Fase G) es independiente del motor y avanza con capacidad libre.

**Estados de ítem:** `[ ]` pendiente · `[~]` en progreso · `[x]` hecho · `[-]` descartado.
**Estados de fase:** `Planning` · `In Progress` · `Blocked` · `Review` · `Done`.

Al cerrar una fase: marcar el gate, fechar, y añadir un `NN-fase-X-report.md` en la carpeta `proj/`
correspondiente (mismo patrón que `proj/P1-scripture-structure/04-phase1-report.md`).

---

## 1. Mapa de fases

| Fase | Nombre | Proyecto(s) | Depende de | Puede solaparse con | Estado |
|---|---|---|---|---|---|
| **A** | Doc-sync + cleanup (Postgres ya migrado y validado 31/31 — A0 2026-09-09; ~1 día) | P0 | — | F | In Progress (A0 ✅) |
| **B** | Modernización de retrieval | P11 | A | C, F |Planning |
| **C** | Extracción de KG v2 | P12 | A | B, D | Planning |
| **D** | Higiene de KG (standing) | WI-3 | A, C2 | E | Planning |
| **E** | RAG avanzado y ahorro de tokens | (transversal) | B, C | D | Planning |
| **F** | Infra y contenedores (Podman ya migrado 2026-07; queda F2/F3) | (transversal) | — | A, B | Parcial |
| **G** | Corpus | P2✅ / P3 / P4 / P13 | — | todas | En curso |

Ruta crítica: **A → B/C (paralelo) → E**. D acompaña a C. F y G corren en paralelo desde el día 1.

---

## 2. Fase A — Doc-sync + cleanup (P0)

**Objetivo original:** cerrar la migración a Postgres. **Tras A0 (2026-09-09): la migración ya está
hecha y validada en `main`** (31/31 golden queries). El objetivo real es solo **sincronizar los
docs de arquitectura** que aún describen Neo4j/Qdrant/SQLite, más limpieza opcional. ~1 día. No es
un blocker de tamaño real — P11/P12/WI-3 pueden arrancar en cuanto los docs sean confiables.
**Detalle + evidencia:** [`proj/P0-postgres-cutover/00-state-audit.md`](../proj/P0-postgres-cutover/00-state-audit.md).

**A0 — auditoría de estado ✅ (2026-09-09).** Primera pasada corrió por error contra el branch
abandonado `workspace-migration`; corregida contra `main`. Certezas sobre **`main`**:
- Neo4j y SQLite/`sqlite-vec`: **retirados** — 0 deps, sin `neo4j_client.py`, sin servicio en compose.
- Write-path de ingesta: **portado** — `pipeline.py` escribe solo vía `alejandria.storage.*` a Postgres.
- `PostgresGraphClient`: **completo** — 0 `NotImplementedError`.
- **31/31 golden queries: reales, commiteadas y en verde.** `tests/parity/golden_queries.yaml` (31),
  `oracle_neo4j.json`, `oracle_postgres.json`, `VALIDATION-TIER2AB.md`; commit
  `ecd885fc8d` "feat(kg): close §3.2 — 31/31 golden queries passing on Postgres". El branch
  `workspace-migration` los había **borrado** (`8c0701c1d6`), de ahí que la 1ª pasada no los viera.
- `import alejandria.main` falla solo por `ModuleNotFoundError: mcp` — la `.venv` del checkout no
  tiene el SDK `mcp` instalado. Es entorno, no código; `uv sync` lo arregla.
- `CLAUDE.md` es **correcto**. `postgres-migration-status.md` y `project_postgres_source_of_truth.md`
  son snapshots de abril desactualizados.
- **Decisión del usuario (2026-09-09):** `main` es canónico; `workspace-migration` abandonado; se
  mantiene el paquete plano `src/alejandria` (el split a 4 paquetes fue el intento abandonado). Con
  eso, **Fase F / F5 queda cerrada** ("¿4 paquetes o 1?" → "1, ya").

- [x] **A0** Auditoría (2 pasadas) → `00-state-audit.md`. Rescope aplicado.
- [ ] **A1** Doc-sync: `architecture.md`, `stack.md`, `knowledge-graph.md`,
      `search-{textual,semantic,hybrid}.md`, `docs/README.md` → un solo store Postgres +
      `PostgresGraphClient`, con notas históricas donde aporten. Reword de strings stale en
      `postgres_graph_client.py` (docstrings "Same shape as Neo4jClient") y `api/schemas.py`.
- [ ] **A2** Cerrar `postgres-migration-status.md` + `project_postgres_source_of_truth.md` con
      header "completo desde `ecd885fc8d`" + puntero a `tests/parity/`.
- [ ] **A3** *(opcional)* Cleanup: borrar el `packages/` sin trackear de `main`; con OK del usuario,
      `git branch -D workspace-migration` + `git stash drop` del WIP parkeado.
- [ ] **A4** *(opcional / puede ir a P11)* Cablear `tests/parity/compare_oracles.py` a `pytest`
      para que 31/31 sea gate, no script manual.

**Gate de salida A:**
- `grep -rniE "neo4j|qdrant|sqlite" docs/*.md` → solo notas históricas explícitas.
- `architecture.md` + `stack.md` describen Postgres-only + `PostgresGraphClient`.
- `postgres-migration-status.md` lee "completo".

**Esfuerzo estimado:** ~1 día (era 3–4 semanas; casi todo estaba hecho y validado).

---

## 3. Fase B — Modernización de retrieval (P11)

**Objetivo:** subir recall y precisión del retrieval y quitar una llamada LLM del camino de query.
**Detalle:** `proj/P11-retrieval-modernization/`.

- [ ] **B1** Añadir servicio **TEI (Text-Embeddings-Inference v1.9)** al `docker-compose`; sacar
      `sentence-transformers` in-process. Config de `cache_dir` a `D:\myapps\ai-models`.
- [ ] **B2** Cambiar el modelo de embeddings a **BGE-M3** (1024 dim). Migración de esquema pgvector
      (`vector(1024)` o `halfvec(1024)` + reindex HNSW); re-embeder los ~217K chunks (bench: ~10 min GPU).
- [ ] **B3** **Hybrid nativo**: incorporar el vector sparse de BGE-M3; decidir si retira el `search/hybrid.py`
      RRF+FTS custom o lo complementa. Documentar la decisión.
- [ ] **B4** **Reranker cross-encoder** (`bge-reranker-v2-m3`) servido por TEI; sustituye la llamada
      LLM de reranking en `chat/rag.py` (`_rerank()`).
- [ ] **B5** **Contextual Retrieval / Late Chunking** en index-time (Anthropic Batch API + prompt
      caching para el contexto por chunk; o late chunking sin LLM). Aplicar primero a un subcorpus y medir.
- [ ] **B6** Bench A/B con el golden set + RAGAS (recall@k, nDCG, faithfulness, context precision)
      antes/después. Guardar en `benchmarks/retrieval-modernization/`.

**Gate de salida B:**
- recall@10 y faithfulness ≥ baseline + margen acordado; sin regresión en QA simple.
- Llamadas LLM por pregunta: 4 → 3 (con Fase E → 2).
- p95 de `search_semantic` < 500 ms sostenido.

**Esfuerzo estimado:** 3–4 semanas.

---

## 4. Fase C — Extracción de KG v2 (P12)

**Objetivo:** pasar de "grafo rico en esquema, pobre en aristas" a un grafo con relaciones tipadas
reales pobladas, y sacar la Fase 3 de ingesta del CPU.
**Detalle:** `proj/P12-kg-extraction-v2/`. Absorbe la parte "relaciones" de P6.

- [ ] **C1** Fix del **bug de filtro gazetteer por-chunk → global** en `knowledge/extractor.py`
      (`known_names_lower` contra el alias lookup global) y en `ner_candidates.record()`. Ref:
      `kg-ingestion-refactor.md §2 Capa 2`.
- [ ] **C2** Integrar **GLiNER2 / GLiREL** como extractor primario NER + RE. Esquema de inferencia =
      los 7 tipos de entidad + los 67 tipos de relación de `knowledge-graph.md`. Corre en **GPU batch**
      en la Fase 3 de ingesta, reemplazando spaCy `sm`. Caché de resultados por hash de chunk.
- [ ] **C3** Mantener el **gazetteer como pase de precisión** (primero) — alta precisión sobre
      entidades canónicas bíblicas.
- [ ] **C4** **LLM batch schema-bound** (Anthropic Batch API + prompt caching del esquema/instrucciones)
      solo para: top-K entidades por `mention_count` y capítulos marcados como ambiguos/narrativos.
      Emite relaciones con confianza `llm_high`.
- [ ] **C5** Reingesta parcial validada; medir ruido contra el gold standard n=300
      (`data/kg-diagnostic/manual_labels_300.csv`). Objetivo: <15 % de ruido por tipo.

**Gate de salida C:**
- Relaciones tipadas reales pobladas para ≥ N tipos de los 67 (definir N al arrancar).
- Ruido en gold standard < 15 % por tipo (`object` incluido).
- Fase 3 de ingesta ya no es CPU-bound (medir chunks/min con GPU).

**Esfuerzo estimado:** 4–5 semanas. Puede solaparse con Fase B.

---

## 5. Fase D — Higiene de KG (WI-3, standing)

**Objetivo:** limpiar el KG existente y convertir la higiene en práctica recurrente, no one-shot.
**Detalle:** `proj/00-backlog.md` → WI-3.

- [ ] **D1** **R10 type-correctness**: muestra estratificada ~500/tipo + ground truth; reglas
      deterministas (regex scripture refs, lookup de lugares europeos, detector de frases numéricas);
      cleanup por lotes contra Postgres con auditoría JSONL. Ref: `kg-ingestion-refactor.md §4bis R10`.
- [ ] **D2** **Entity resolution / dedup a escala** — EDC (Extract-Define-Canonicalize) o cluster de
      embeddings de profile summaries + LLM-judge; merge de duplicados no-canónicos con reasignación
      de relaciones antes de borrar.
- [ ] **D3** **R5** honoríficos cross-language ("Señor Jesucristo", "Su Hijo Jesucristo" → "Jesucristo")
      — extender `gazetteer_lookup.normalize` con strip de honoríficos.
- [ ] **D4** **Decidir R6** — mecanismo `ner_candidates.promote/dismiss` (0 promociones históricas):
      (a) usar activamente vía skill `/ner-review`, (b) auto-promover sobre umbral, (c) eliminar.
- [ ] **D5** Institucionalizar: `scripts/kg_hygiene.py` + checklist en `procedure_corpus_addition.md`,
      cadencia cada N meses.

**Gate de salida D (primera vuelta):**
- Gold standard estable o mejor tras el pase.
- Proceso documentado y re-ejecutable con un comando.

**Esfuerzo estimado:** 2–3 semanas iniciales + recurrente. Depende de C2 (no re-limpiar lo que el
extractor viejo vuelve a ensuciar).

---

## 6. Fase E — RAG avanzado y ahorro de tokens

**Objetivo:** bajar tokens del camino de query ~50 % y del trabajo offline ~95 %; mejorar multi-hop.

- [ ] **E1** Fusionar **query expansion + entity extraction** en 1 llamada LLM (`chat/rag.py`
      `_expand_query()` + extracción). 4 → 3 llamadas; con B4 → 2.
- [ ] **E2** **Prompt caching** en el system prompt y few-shots de las llamadas internas.
- [ ] **E3** **Batch API** para todo el trabajo offline: generación de perfiles, extracción KG (C4),
      backfills, contextual retrieval (B5).
- [~] **E4** **PPR / graph-enhanced retrieval** — **ya en curso con plan propio**:
      `docs/architecture-proposals/ppr-implementation-plan.md` (2026-08-22) +
      `graph-enhanced-rag-evaluation.md`; módulo `src/alejandria/knowledge/pagerank.py` ya existe,
      baseline en `ppr-baseline-metrics.json`. **No re-planificar aquí** — seguir ese plan; este
      ítem solo trackea su cierre y su integración en `chat_ask` / `/search/graph/pagerank`.
- [ ] **E5** **Perfiles lazy (R8)**: generar summaries solo para top-K por `mention_count` en ingesta;
      resto on-demand en la primera consulta.

**Gate de salida E:**
- −50 % tokens en query-path (medido con `POST /chat/compare` / logs de tokens).
- −~95 % en offline (batch + cache).
- Multi-hop F1 ≥ baseline (medido por el plan de PPR, no aquí).

**Esfuerzo estimado:** 2–3 semanas (E4 tiene su propio plan y ETA).

---

## 7. Fase F — Infra y contenedores

**Objetivo:** dev sin SSH tunnel obligatorio, compose mínimo. *(La unificación de engine ya no
aplica: la migración a Podman se completó el 2026-07-04 —
`docs/project-memory/project_podman_migration.md`.)*

- [x] **F1** ~~Unificar engines Docker~~ — **hecho**: contenedores migrados a Podman
      (`podman-machine-default`), `docker/docker-compose.podman.yml`, `scripts/gpu-podman.sh`
      (2026-07-04). `docker.md` debe reflejarlo → P0·T1.
- [ ] **F2** **TEI como servicio de compose** (viene de B1) + servicio de reranker — sobre
      `docker/docker-compose.podman.yml`.
- [ ] **F3** **Postgres local en container** para dev (paridad de esquema, sin tunnel en el loop);
      el tunnel a IONOS queda para operaciones sobre la autoridad.
- [x] **F4** Contenedor **Neo4j** ya decomisionado (confirmado A0 — no está en `docker/*.yml`).
- [x] **F5** ~~Revisar 4 paquetes `uv`/`hatch` vs 1~~ — **cerrado por decisión del usuario (2026-09-09)**:
      se mantiene el paquete plano `src/alejandria`; el split fue el intento abandonado
      `workspace-migration`. Cleanup del `packages/` sin trackear y de la rama abandonada → P0·A3.

**Gate de salida F:**
- `podman compose -f docker/docker-compose.podman.yml config` lista: `api`, `ollama`, `postgres`,
  `tei` (+ `reranker`). Nada más.
- Onboarding en máquina limpia sin configurar SSH tunnel para desarrollo local.

**Esfuerzo estimado:** ~1 semana (F1 ya hecho). Corre en paralelo con A/B.

---

## 8. Fase G — Corpus (incubador existente, re-secuenciado)

**Objetivo:** corpus vivo y más profundo; habilitar Layer 3 de paralelismos. Independiente del motor.

- [ ] **G1** Verificar cobertura ES completa (P2 cerró EN+ES; confirmar que no quedan gaps).
- [ ] **G2** **Reactivar P3 — ETL Templates** (estado actual `Deferred`): templates por tipo de
      material (discursos, manuales, institute, CES). Normalización, extracción de metadata, validación.
- [ ] **G3** **P4 — Corpus Expansion**: revistas (*Liahona/Ensign*), manuales de instituto,
      comentarios y obra académica (la capa que desbloquea Layer 3 en el KG).
- [ ] **G4** **Church content API** para footnotes → cross-references directos al KG (miles, gratis).
- [ ] **G5** **P13 — Genealogías Escriturales** (renumerado; era "P10" en `roadmap.md`): tras C2,
      extracción híbrida regex + LLM batch de "begat / engendró a" + API `/kg/genealogy/{person}`.

**Gate de salida G:** sin gate único — es continuo. Métrica: nº de tipos de material con template ETL,
cobertura de corpus por Layer.

---

## 9. Roadmap actualizado (tabla viva)

| # | Proyecto | Prioridad | Fase | Estado | Depende de |
|---|---|---|---|---|---|
| **P0** | Doc-sync + cleanup (Postgres migration ✅ & 31/31 parity per A0; ~1 día) | Media | A | In Progress | — |
| **P11** | Retrieval modernization | **Alta** | B | Planning | P0 |
| **P12** | KG extraction v2 | **Alta** | C | Planning | P0 |
| **WI-3** | KG hygiene (standing) | Alta | D | Planning | P0, P12·C2 |
| P1 | Scripture Structure: Long Chain | Highest | G | Complete | — |
| P2 | Scripture Refresh / Corpus Completion | High | G | Complete | — |
| P3 | ETL Templates | High | G | **Reactivar** (era Deferred) | — |
| P4 | Corpus Expansion | High | G | Complete / continuo | P3 |
| P5 | Chat Client UI | Medium | post B+C | Planning | P0, P11, P12 |
| P6 | Advanced Relations (Layer 2/3 + feedback loop; relaciones → P12) | Medium | post C | Parcial | P1, P12 |
| P7 | Deep Disambiguation | Medium | post C | Parcial | P12 |
| P8 | Synthesis Engine / Discursos | Media (producto) | post B+C | Planning | P5, P6 |
| P9 | ~~Fine-Tuning~~ → absorbido por P11 | Lower | B | Deferred | — |
| P10 | Handbook KG Model | Medium | — | Complete | — |
| **P13** | Genealogías Escriturales (renumerado desde "P10" en roadmap.md) | Medium | G / post C | Planning | P12 |

---

## 10. Riesgos del programa

| ID | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| PR-1 | Fase A se alarga y bloquea B/C | Alto | A tiene feature flag; B2/C2 pueden prototiparse en un branch sobre datos actuales sin esperar A4 |
| PR-2 | BGE-M3 1024 dim presiona RAM del VPS M | Medio | `halfvec` (mitad de storage); si aprieta, upgrade a VPS L (€10–15/mo) — trigger T3 de `vector-db-options.md` |
| PR-3 | 6 GB de VRAM no alcanzan para embeddings + reranker + GLiNER concurrentes | Medio | TEI residente para embeddings+reranker (~2 GB); GLiNER solo en ventanas de ingesta; LLM siempre en la nube |
| PR-4 | GLiREL zero-shot no alcanza precisión en dominio arcaico | Medio | Gazetteer se mantiene como pase de precisión; LLM batch como red de seguridad para top-K; medir contra gold n=300 antes de reemplazar spaCy del todo |
| PR-5 | Bus factor — un solo dev, muchas fases | Alto | Fases con gate cerrado y report; no abrir fase nueva con otra en `In Progress` salvo los solapes permitidos (§1) |
| PR-6 | Deriva de docs durante el programa | Medio | Regla ya existente: cambio de comportamiento ⇒ doc en el mismo commit; endurecer `scripts/pre-commit-sync.sh` |

---

## 11. Bitácora

| Fecha | Fase | Nota |
|---|---|---|
| 2026-09-09 | — | Creación del programa a partir de `improvement-analysis-2026.md`. Todas las fases en `Planning` salvo G (en curso). |
| 2026-09-09 | A | **A0, 1ª pasada** (branch equivocado: `workspace-migration`). Concluyó "branch roto, 38 imports muertos". |
| 2026-09-09 | A | **A0, 2ª pasada (corregida, contra `main`).** Usuario aclara: `main` es el sistema; `workspace-migration` abandonado. Certezas: Postgres migration **hecha y validada** (31/31 golden queries commiteadas, `ecd885fc8d`); `CLAUDE.md` correcto; el branch abandonado había **borrado** los archivos de paridad. **Fase A rescopeada** de 3–4 sem → **~1 día de doc-sync**. Decisión: mantener `src/alejandria` plano → **Fase F5 cerrada**. Ver `proj/P0-postgres-cutover/00-state-audit.md`. |
