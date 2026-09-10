# P12 — KG Extraction v2 — Risks

## R1: GLiREL zero-shot precision insufficient on archaic/domain text

**Descripción:** GLiNER/GLiREL están entrenados en texto general. El inglés KJV ("Jacob begat
Judas") y el español escritural pueden producir extracciones pobres o relaciones mal tipadas entre
los 67 tipos.

**Impacto:** Alto — sería el core del proyecto fallando.

**Probabilidad:** Media.

**Mitigación:**
1. **Eval offline primero (Phase 2)** sobre muestra de 5–10k chunks contra el gold n=300 antes de
   tocar el pipeline.
2. El **gazetteer se mantiene como pase de precisión** — GLiNER solo cubre lo no canónico.
3. **LLM batch (FR-4)** como red de seguridad para el subconjunto difícil.
4. Reducir el esquema de relaciones a los ~15–20 tipos de mayor valor primero; ampliar después.
5. Patrones deterministas (`family_patterns.py`) se conservan para "begat/engendró".

**Criterio de aceptación:** el modelo elegido supera a spaCy `sm` en precisión de entidad en la
muestra; si no, se mantiene gazetteer+deterministas y se prioriza FR-4.

---

## R2: Esquema de 67 relaciones sobrecarga al extractor y degrada todo

**Descripción:** Pasar 67 labels de relación + 7 de entidad en cada llamada de inferencia zero-shot
puede diluir la señal (los modelos GLiNER rinden mejor con esquemas acotados) y volver lento el batch.

**Impacto:** Medio.

**Probabilidad:** Media-Alta.

**Mitigación:**
1. Esquema por **categoría** (familia, gobernanza, profético, …) — 1 pasada por categoría relevante
   al tipo de documento, no 67 labels juntos.
2. Enrutar por tipo de material: discursos no necesitan el esquema de genealogía.
3. Medir latencia por configuración en Phase 2; elegir el trade-off.

**Criterio de aceptación:** throughput de Phase 3 mejora vs spaCy CPU pese al esquema.

---

## R3: WI-3 y P12 se pisan (limpieza vs nueva extracción)

**Descripción:** Si la limpieza masiva (WI-3 / R10) corre antes de que el extractor v2 esté en
producción, se limpia un KG que el extractor viejo vuelve a ensuciar en la siguiente ingesta.

**Impacto:** Medio — trabajo desperdiciado.

**Probabilidad:** Alta si no se secuencia.

**Mitigación:**
1. Dependencia explícita en el programa: **Fase D empieza después de P12·M3**.
2. Hasta M3, WI-3 solo hace diseño (muestreo, reglas), no ejecución masiva.

**Criterio de aceptación:** el primer pase masivo de WI-3 ocurre con `KG_EXTRACTOR=gliner` ya activo.

---

## R4: Caché por hash de chunk invalida de más tras cambios de esquema

**Descripción:** Si el esquema de extracción cambia (se añaden tipos), el caché por SHA-256 de
chunk queda obsoleto pero el hash del texto no cambió ⇒ no se re-extrae.

**Impacto:** Medio.

**Probabilidad:** Cierta cuando se itere el esquema.

**Mitigación:**
1. Clave de caché = `hash(chunk_text) + hash(schema_version)`.
2. Bump de `schema_version` fuerza re-extracción controlada.
3. Documentar en `entity-extraction.md`.

**Criterio de aceptación:** cambiar el esquema y reingerir re-extrae los chunks afectados.

---

## R5: VRAM — GLiNER en ingesta compite con TEI de P11

**Descripción:** GLiNER (<500M, ~1–1.5 GB) durante la Fase 3 de ingesta, sumado a TEI residente
(embeddings+reranker de P11), puede exceder 6 GB.

**Impacto:** Medio.

**Probabilidad:** Media.

**Mitigación:**
1. Ingesta y query-time no concurrentes por diseño (la ingesta es batch, offline).
2. Si hace falta, TEI se baja durante corridas de ingesta grandes y se re-levanta.
3. GLiNER en INT8.
4. Coordinar con `docs/performance.md` §GPU budget.

**Criterio de aceptación:** una corrida de ingesta completa no OOM-ea la GPU.

---

## Matriz resumen

| ID | Riesgo | Impacto | Probabilidad | Fase |
|----|--------|---------|--------------|------|
| R1 | GLiREL zero-shot flojo en dominio | Alto | Media | 2 |
| R2 | Esquema de 67 relaciones sobrecarga | Medio | Media-Alta | 2, 3 |
| R3 | WI-3 y P12 se pisan | Medio | Alta (sin secuenciar) | 3, 4 |
| R4 | Caché por hash obsoleto tras cambio de esquema | Medio | Cierta | 3 |
| R5 | VRAM: GLiNER vs TEI | Medio | Media | 3 |
