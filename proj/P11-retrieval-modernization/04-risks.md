# P11 — Retrieval Modernization — Risks

## R1: BGE-M3 1024-dim pressures IONOS VPS M RAM

**Descripción:** 217K vectores × 1024 dim ≈ 4× el storage actual (384 dim, ~750 MB) → ~3 GB +
HNSW. En un VPS M con `shared_buffers` de 512 MB, el índice puede no caber en memoria y degradar
la latencia de query.

**Impacto:** Medio-Alto — p95 semántico podría superar el trigger T1 de `vector-db-options.md`.

**Probabilidad:** Media.

**Mitigación:**
1. `halfvec(1024)` — mitad de storage con pérdida de precisión despreciable a esta escala.
2. Medir tamaño real de `chunk_embeddings` tras re-embed (trigger T3 = >5 GB).
3. Si aprieta: upgrade a IONOS VPS L (8 GB RAM, €10–15/mo) — es el primer paso previsto en §5 de
   `vector-db-options.md`.
4. Evaluar `pgvector` iterative index scan / `ef_search` tuning antes de escalar hardware.

**Criterio de aceptación:** p95 `search_semantic` < 500 ms sostenido 1 semana post-migración.

---

## R2: 6 GB de VRAM no alcanzan para embeddings + reranker concurrentes

**Descripción:** TEI con BGE-M3 (~2–2.5 GB) + `bge-reranker-v2-m3` (~2 GB) + el modelo de embeddings
que ya compartía GPU con Ollama deja poco margen en 6 GB, sobre todo si hay ingesta (GLiNER de P12)
en simultáneo.

**Impacto:** Medio.

**Probabilidad:** Media.

**Mitigación:**
1. TEI residente solo para query-time (embeddings + reranker); GLiNER de P12 corre en ventanas de
   ingesta, no concurrente.
2. Cuantización: TEI soporta modelos en FP16/INT8; usar la variante más chica que pase el eval.
3. LLM siempre en la nube — nunca cargar un 7B local junto a TEI.
4. `docs/performance.md` §"GPU sharing" — actualizar el presupuesto de VRAM.

**Criterio de aceptación:** query-path estable con TEI residente; ingesta y query no compiten por VRAM.

---

## R3: BGE-M3 no mejora (o empeora) el recall en dominio escritural arcaico

**Descripción:** BGE-M3 está entrenado en web/QA general. El inglés KJV y el español escritural
pueden no beneficiarse tanto como un corpus moderno; incluso podría perder frente al MiniLM
afinado al uso actual.

**Impacto:** Medio — invalidaría la premisa de la Fase B.

**Probabilidad:** Baja-Media.

**Mitigación:**
1. **Eval harness primero (Phase 1)** — no migrar nada sin baseline.
2. Probar también `intfloat/multilingual-e5-large-instruct` y `ibm-granite/granite-embedding-...-r2`
   en el mismo harness antes de comprometerse.
3. Mantener la columna 384-dim hasta que el candidato gane en recall@10 Y faithfulness.
4. Contextual Retrieval (FR-5) puede cerrar la brecha si el modelo base queda parejo.

**Criterio de aceptación:** el modelo elegido gana al baseline en recall@10 y faithfulness; si
ninguno gana, se documenta y se conserva MiniLM, priorizando FR-4/FR-5.

---

## R4: Reemplazar el RRF custom rompe casos que hoy funcionan

**Descripción:** `search/hybrid.py` y sus modos (`hybrid`, `cross-ref`, `kg-boost`, `footnote-xref`)
están afinados a mano. Sustituirlos por hybrid nativo de BGE-M3 puede regresar en consultas de
enumeración o de cita exacta.

**Impacto:** Medio.

**Probabilidad:** Media.

**Mitigación:**
1. Decisión explícita en `03-hybrid-decision.md`: **complementar** por defecto, no reemplazar.
2. Mantener FTS para exact-phrase y enumeración; añadir sparse como señal adicional.
3. Bench por tipo de query (factual, enumeración, multi-entidad, cita exacta), no solo agregado.

**Criterio de aceptación:** ningún tipo de query regresa >5 % en recall@10.

---

## R5: Coste de Contextual Retrieval sobre 309K chunks

**Descripción:** Un blurb LLM por chunk × 309K chunks, aunque sea fast-tier + batch, tiene coste y
tiempo no triviales.

**Impacto:** Bajo-Medio.

**Probabilidad:** Cierta si se elige la variante LLM.

**Mitigación:**
1. **Late chunking primero** — no necesita LLM; medir si alcanza.
2. Si se usa la variante LLM: Anthropic Batch API (−50 %) + prompt caching del documento padre
   (−90 % en la parte repetida) → coste ~95 % menor que naïve.
3. Aplicar solo a subcorpus donde el eval muestre ganancia (docs largos, mucha referencia cruzada).

**Criterio de aceptación:** ganancia en top-20 failure rate que supere el coste, medida en RAGAS.

---

## Matriz resumen

| ID | Riesgo | Impacto | Probabilidad | Fase |
|----|--------|---------|--------------|------|
| R1 | RAM VPS M con 1024 dim | Medio-Alto | Media | 2 |
| R2 | VRAM insuficiente embeddings+reranker | Medio | Media | 2, 4 |
| R3 | BGE-M3 no mejora dominio arcaico | Medio | Baja-Media | 1, 2 |
| R4 | Reemplazar RRF regresa casos | Medio | Media | 3 |
| R5 | Coste de Contextual Retrieval | Bajo-Medio | Cierta (variante LLM) | 5 |
