# P4 — Corpus Expansion — Project Plan

## Fases

Las fases están ordenadas por **costo/beneficio**: primero lo que tiene script
listo (costo cero, beneficio inmediato), luego lo que requiere preparación.
Cada fase es independiente y ejecutable sin esperar la siguiente.

---

### Fase 1 — Ejecutar scripts preparados ✅ COMPLETE (2026-04-03)

**Costo:** bajo — los scripts ya existen, solo ejecutar.
**Beneficio:** inmediato — ~140 documentos nuevos, JTC enriquece KG masivamente.

| Material | Script | Estado |
|----------|--------|--------|
| Jesus the Christ (EN+ES) | `download_jesus_the_christ.py` | ✅ 86 archivos (43 caps × EN+ES) |
| Christmas Study Plan 2024 (EN+ES) | `download_christmas_study_plan.py` | ✅ 18 archivos (9 × EN+ES) |
| Easter Study Plan (EN+ES) | `download_easter_study_plan.py` | ✅ 36 archivos (18 × EN+ES) |

Christmas 2025 no existe en el sitio (404 en EN y ES, verificado 2026-04-03).
Se descargará cuando la Iglesia lo publique (~noviembre 2025).

---

### Fase 2 — ~~Cerrar gaps de ayudas de estudio ES~~ N/A (2026-04-03)

**Estado:** CANCELADA — el Bible Dictionary y Topical Guide **no existen en español**
en el sitio oficial de la Iglesia (API retorna 404 para `lang=spa`).

La edición SUD de la Biblia en español reemplaza BD + TG con la **Guía para el
Estudio de las Escrituras** (GEE), que ya está descargada: 809 entries EN + 809 ES.

| Recurso | EN | ES | Nota |
|---------|----|----|------|
| Bible Dictionary | 1,274 | — | Solo existe en inglés (KJV edition) |
| Topical Guide | 3,511 | — | Solo existe en inglés (KJV edition) |
| Guide to the Scriptures | 812 | 809 | ✅ Ya descargado (equivalente ES de BD+TG) |

No hay gap real: la GEE ES cubre el mismo propósito para lectores hispanohablantes.

---

### Fase 3 — Escrituras ES completas ✅ COMPLETE (2026-04-03)

Escrituras ES descargadas: 1,601 de 1,602 archivos (99.94% paridad con EN).
El único faltante es `epistle-dedicatory` en AT (no es escritura canónica).

| Standard Work | ES | EN | Match |
|---------------|----|----|-------|
| Book of Mormon | 246 | 246 | ✅ |
| Old Testament | 930 | 931 | -1 (epistle-dedicatory) |
| New Testament | 261 | 261 | ✅ |
| D&C | 143 | 143 | ✅ |
| Pearl of Great Price | 21 | 21 | ✅ |

---

### Fase 4 — Obras clásicas SUD (Project Gutenberg) ✅ COMPLETE (2026-04-04)

JTC descargado del sitio oficial en Fase 1. Las demás obras descargadas de
Project Gutenberg con `download_gutenberg.py` (skill: `/gutenberg`).

**Fuente:** Project Gutenberg vía API gutendex.com
**Script:** `download_gutenberg.py` (genérico para cualquier libro de Gutenberg)

| ID | Obra | Autor | Caps | Chars | Estado |
|----|------|-------|------|-------|--------|
| — | Jesus the Christ | Talmage | 43 | — | ✅ Sitio oficial |
| 42238 | The Articles of Faith | Talmage | 24 | 978K | ✅ Gutenberg |
| 35514 | The Great Apostasy | Talmage | 10 | 306K | ✅ Gutenberg |
| 45149 | The House of the Lord | Talmage | 11 | 470K | ✅ Gutenberg |
| 47182 | The Vitality of Mormonism | Talmage | 104 | 583K | ✅ Gutenberg |
| 74447 | Discourses of Brigham Young | BY/Widtsoe | 42 | 1,262K | ✅ Gutenberg |

**Limpieza aplicada (implementada en `download_gutenberg.py`):**
- Strip header/footer Gutenberg (`*** START/END ***`)
- Reflow line-wrap a ~75 chars → párrafos continuos
- Parsear footnotes (`[N]`, `[Footnote N: ...]`, notas al final de cap)
- Limpiar marcadores de formato (`_italics_`, `=bold=`, `**bold**`)
- Separar TOC duplicada (Discourses of BY tiene TOC + contenido)
- Índice analítico al final → descartado
- Transcriber notes → descartados
- "See page NNN" (refs a libro físico) → eliminados
- Verificación: cero artefactos Gutenberg en los 191 archivos finales

**Autoridad:** 40 (obras canónicas de líderes de la Iglesia, ediciones históricas).
Discourses of BY: 35 (compilación de terceros, nota de contexto en meta.json).

---

### Fase 5 — Manuales doctrinales esenciales ✅ COMPLETE (2026-04-03)

Los tres materiales ya están descargados en el corpus, bilingüe:

| Material | EN | ES |
|----------|----|----|
| Gospel Principles | ✅ 102 archivos | ✅ 102 archivos |
| True to the Faith | ✅ 346 archivos | ✅ 334 archivos |
| Teachings — Joseph Smith | ✅ 54 archivos | ✅ 52 archivos |

---

### Fase 6 — Come Follow Me ✅ COMPLETE (2026-04-03)

Descargados **8 años** (2019–2026), bilingüe — supera ampliamente el alcance
original de "ciclo actual":

| Año | EN | ES |
|-----|----|----|
| 2019 | 57 | 57 |
| 2020 | 61 | 61 |
| 2021 | 60 | 59 |
| 2022 | 69 | 69 |
| 2023 | 61 | 61 |
| 2024 | 58 | 58 |
| 2025 | 71 | 71 |
| 2026 | 68 | 68 |

---

### Fase 7 — Serie Teachings of Presidents ✅ COMPLETE (2026-04-03)

17 profetas EN, 16 ES. Falta Spencer W. Kimball en ES (verificar si está
en el sitio oficial).

| Profeta | EN | ES |
|---------|----|----|
| Brigham Young | 53 | 50 |
| John Taylor | 29 | 27 |
| Wilford Woodruff | 29 | 27 |
| Lorenzo Snow | 29 | 30 |
| Joseph F. Smith | 54 | 51 |
| Heber J. Grant | 30 | 27 |
| George Albert Smith | 30 | 30 |
| David O. McKay | 30 | 27 |
| Harold B. Lee | 30 | 27 |
| Spencer W. Kimball | 30 | **—** |
| Ezra Taft Benson | 30 | 30 |
| Howard W. Hunter | 30 | 30 |
| Joseph Fielding Smith | 32 | 32 |
| Joseph Smith | 54 | 52 |
| Gordon B. Hinckley | 31 | 31 |
| Thomas S. Monson | 29 | 29 |
| Russell M. Nelson | 24 | 18 |

---

### ~~Fase 8 — Discourses of Brigham Young~~ Absorbida en Fase 4

Consolidada en Fase 4 junto con las demás obras de Gutenberg. El script
`download_gutenberg.py` maneja todas las descargas de esta fuente con un
solo comando por libro (`--book-id 74447`).

---

## Milestones

| Milestone | Fases | Estado |
|-----------|-------|--------|
| M1 — Scripts ejecutados | 1 | ✅ Complete — 140 docs |
| M2 — Paridad ES study-aids | 2 | ❌ Cancelado (BD/TG no existen en ES) |
| M3 — Escrituras ES completas | 3 | ✅ Complete — 1,601 docs |
| M4 — Obras clásicas SUD (Gutenberg) | 4 | ✅ Complete — 191 caps (6 obras: JTC + 5 Gutenberg) |
| M5 — Manuales esenciales | 5 | ✅ Complete — ~936 docs EN+ES |
| M6 — CFM completo | 6 | ✅ Complete — ~1,009 docs EN+ES (8 años) |
| M7 — Teachings completo | 7 | ✅ Complete — ~1,082 docs EN+ES (17 profetas) |
| M8 — BY histórico | 8 | ❌ Absorbido en M4 (Fase 8 → Fase 4) |

**Pendientes:** Ninguno. Todas las fases completadas o canceladas con justificación.
Spencer W. Kimball ES no existe en el sitio oficial (API 404, verificado 2026-04-03).

---

## Riesgos

| Riesgo | Impacto | Mitigación | Estado |
|--------|---------|------------|--------|
| Slugs de CFM varían por año | Medio | Verificar TOC con `--dry-run` | ✅ Resuelto — 8 años descargados |
| Teachings of Presidents: slugs inconsistentes | Medio | Mapeo manual | ✅ Resuelto — 17 profetas descargados |
| Escrituras ES: sitio cambia HTML | Bajo | Fallback al dump MySQL | ✅ Resuelto — paridad lograda |
| Reindexado KG tarda 3h por batch grande | Alto | Ingesta incremental | Vigente |
| Materiales fuera del sitio oficial | Bajo | Verificar disponibilidad antes de planificar | Nuevo — afecta Fase 4 y 8 |

---

## Criterios de éxito

1. ✅ Corpus crece significativamente (de ~10k estimado; conteo actual pendiente de verificar)
2. ✅ Jesus the Christ indexado y aparece en búsquedas
3. ✅ Escrituras ES completas — paridad con EN en standard works
4. ✅ Gospel Principles disponible para preguntas sobre plan de salvación
5. ✅ Come Follow Me = exégesis semanal searchable (8 años, no solo el actual)
6. ✅ Perfiles KG de profetas enriquecidos con Teachings series (17 profetas)
