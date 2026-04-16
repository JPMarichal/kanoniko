# Corpus Expansion — Backlog de indexación

Material ya **descargado al corpus** (archivos en disco) que aún no ha pasado por el
pipeline de indexación (FTS + vectors + KG).

Para backlog de descarga → `04-backlog.md`.
Para inventario de lo ya indexado → `03-corpus-inventory.md`.
Para análisis detallado por material → `fase0/`.

> **Última reconciliación:** 2026-04-16 — verificado contra FTS (54,897 docs indexados
> de 57,956 .txt en disco). Gap confirmado: ~2,600 archivos en 6 materiales.

---

## 1. Pendientes de indexación

### Resumen

| # | Material | Archivos | authority | Fase 0 | Corpus path | Bloqueante |
|---|----------|----------|-----------|--------|-------------|------------|
| 1 | Teaching, No Greater Call (EN+ES) | 182 | 60 | ✅ `fase0/teaching-no-greater-call.md` | `corpus/{lang}/manuals/teaching-no-greater-call/` | — |
| 2 | Interpreter Journal | 888 | 25 | ✅ `fase0/interpreter-journal.md` | `corpus/en/books/interpreter-journal/` | — |
| 3 | Journal of Discourses (26 vols) | 1,425 | 20 | ✅ `fase0/journal-of-discourses.md` | `corpus/en/books/journal-of-discourses/` | — |
| 4 | Teach Ye Diligently | 18 | 45 | ✅ `fase0/teach-ye-diligently.md` | `corpus/en/books/teach-ye-diligently/` | Solo en rama `main` |
| 5 | Missionary Guide 1988 | 18 | 90/60 | ✅ `fase0/missionary-guide-1988.md` | `corpus/en/manuals/missionary-guide-1988/` | — |
| 6 | Doctrines of Salvation (3 vols) | 60 | 45 | — | `corpus/en/books/doctrines-of-salvation/` | Formato .md, sin .txt |

**Total:** ~2,591 archivos pendientes de indexación.

---

### Detalle por material

#### 1. Teaching, No Greater Call (1999) — Bilingüe

> Fase 0: `fase0/teaching-no-greater-call.md`

Manual oficial de enseñanza de la Iglesia. 7 partes (A-G), ~90 páginas web por idioma.
Descargado bilingüe (EN+ES) desde el sitio de la Iglesia vía `download_manual.py`.
Predecesor de *Teaching in the Savior's Way* (2022, ya ingested).

- **Listo para indexar:** Sí — Fase 0 completa, authority definida, .txt + .meta.json
- **Prioridad de indexación:** ALTA — material oficial, bilingüe, complementa TITSW

#### 2. Interpreter Journal (888 artículos)

> Fase 0: `fase0/interpreter-journal.md`

Revista académica peer-reviewed de estudios mormones (2012-2026). 888 artículos, 50 MB.
Solo EN. Descargado con `download_interpreter.py`.

- **Listo para indexar:** Sí — Fase 0 completa, authority definida, .txt + .meta.json
- **Prioridad de indexación:** MEDIA — volumen alto, authority baja (25), académico

#### 3. Journal of Discourses (26 vols, 1,425 discursos)

> Fase 0: `fase0/journal-of-discourses.md`

1,425 discursos de líderes de la Iglesia (1851-1886). ~5M palabras. Solo EN.
Fuente: journalofdiscourses.com. Authority 20 — no oficial, imprecisión documentada.

- **Listo para indexar:** Sí — Fase 0 completa, authority definida, .txt + .meta.json
- **Prioridad de indexación:** BAJA — volumen enorme, authority muy baja, riesgos de contenido
- **Nota:** Indexar incrementalmente puede tomar tiempo significativo (~1,425 archivos)

#### 4. Teach Ye Diligently (Boyd K. Packer)

> Fase 0: `fase0/teach-ye-diligently.md`

Tratado pedagógico de Packer (1975/1991). 16 capítulos + foreword + appendix.
Solo EN. Extraído de EPUB (biblioteca personal Calibre).

- **Listo para indexar:** No — archivos en rama `main`, no en `feature/local-llm-backend`
- **Bloqueante:** Merge de ramas pendiente
- **Prioridad de indexación:** MEDIA-ALTA — pieza fundacional de la cadena pedagógica CES

#### 5. Missionary Guide: Training for Missionaries (1988)

> Fase 0: `fase0/missionary-guide-1988.md`

"El manual rosa" — compañero pedagógico de las charlas misionales 1986,
predecesor directo de *Preach My Gospel* 2004. 17 archivos (front + 16 caps).
Solo EN. Fuente: Archive.org (PDF escaneo + OCR DjVu).

- **Listo para indexar:** Sí — Fase 0 completa, authority definida
- **Prioridad de indexación:** ALTA — authority 90/60, manual oficial histórico

#### 6. Doctrines of Salvation (Joseph Fielding Smith, 3 vols)

> Fase 0: pendiente

60 archivos en formato .md (no .txt). Requiere conversión de formato antes de indexar.
Descargado pero sin Fase 0 — necesita investigación editorial antes de indexar.

- **Listo para indexar:** No
- **Bloqueantes:**
  1. Formato .md → necesita conversión a .txt + .meta.json
  2. Fase 0 pendiente — investigación editorial obligatoria antes de indexar
- **Prioridad de indexación:** MEDIA — authority estimada 45, 3 volúmenes doctrinales

---

## 2. KG enrichment pendiente (material ya ingested)

Material indexado que tiene relaciones KG identificadas pero no pre-seeded.

| Material | Relaciones pendientes | Fase 0 |
|----------|----------------------|--------|
| Jesus the Christ | `TAUGHT` (Resurrection, Atonement, Law of Moses), `QUOTED_BY` (Isaiah→JC), `TYPE_OF` (High Priest) | `fase0/jesus-the-christ.md` |
| Preach My Gospel | `PREREQUISITE_FOR` cadena primeros principios (Faith→Repentance→Baptism→HG→Endure) | `fase0/preach-my-gospel.md` |

### Indexados sin investigación editorial + KG pre-seed (retroactivo)

Materiales ingested en la sesión 2026-04-16 con el pipeline automático (NER + co-ocurrencia),
pero **sin re-verificar la investigación editorial de Fase 0** y **sin KG pre-seeding manual**
de las relaciones tipadas curadas. Requieren una pasada posterior para:

1. Re-verificar o expandir la investigación editorial (web research actualizada)
2. Identificar y pre-seedar relaciones tipadas específicas (TAUGHT, PREREQUISITE_FOR, TYPE_OF, etc.)

| Material | Ingested | Fase 0 original | Notas |
|----------|----------|-----------------|-------|
| Missionary Guide 1988 | 2026-04-16 | `fase0/missionary-guide-1988.md` | Relaciones clave: `PREDECESSOR_OF` (→PMG), `COMPANION_TO` (1986 discussions) |
| Teach Ye Diligently | 2026-04-16 | `fase0/teach-ye-diligently.md` | Relaciones clave: `AUTHORED_BY` (Packer), `CITES` (Charted Course), cadena pedagógica CES |
| Teaching, No Greater Call (EN+ES) | 2026-04-16 | `fase0/teaching-no-greater-call.md` | Relaciones clave: `PREDECESSOR_OF` (→TITSW), `SUCCESSOR_OF` (→Teaching—No Greater Call earlier versions) |

> **Nota para sesiones futuras:** Estos tres materiales deben recibir pasada de web research +
> KG pre-seed antes de considerarse "completamente ingested" según el protocolo de Fase 0.
> Mientras tanto, el FTS y la búsqueda semántica funcionan normalmente; solo las relaciones
> KG tipadas curadas están pendientes.

---

## 3. Prioridad de indexación recomendada

Orden sugerido para la siguiente sesión de indexación:

| Orden | Material | Archivos | Justificación |
|-------|----------|----------|---------------|
| 1 | Teaching, No Greater Call | 182 | Oficial, bilingüe, Fase 0 lista, complementa material ingested |
| 2 | Missionary Guide 1988 | 18 | Authority alta, volumen bajo, Fase 0 lista |
| 3 | Teach Ye Diligently | 18 | Pedagógico, Fase 0 lista (requiere merge de ramas) |
| 4 | Interpreter Journal | 888 | Académico, volumen alto, Fase 0 lista |
| 5 | Doctrines of Salvation | 60 | Requiere conversión + Fase 0 antes de indexar |
| 6 | Journal of Discourses | 1,425 | Volumen enorme, authority baja, riesgos — al final |

**ETA estimada** (GPU Docker, incremental):
- Items 1-3: ~30 min total (~218 archivos, ~2-3 sec/archivo)
- Item 4: ~45 min (~888 archivos)
- Item 5: bloqueado (conversión + Fase 0)
- Item 6: ~1h+ (~1,425 archivos) — considerar sesión dedicada

---

## 4. Protocolo de indexación

### Workflow

```
descargado
  → Fase 0 (gate obligatorio)
      → Paso 1: Investigación editorial (web research)
      → Paso 2: Análisis de contenido + authority + valor KG
  → Pre-seed KG (relaciones identificadas en Fase 0)
  → Ejecutar pipeline incremental
  → Verificar con /corpus/status
  → Mover a 03-corpus-inventory.md
```

### Gate de Fase 0

La Fase 0 es **obligatoria antes de indexar**, aunque la descarga haya ocurrido antes.
Esto garantiza que:
- El modelo de authority está fundamentado en investigación editorial real
- Las relaciones KG están pre-seeded antes de que el pipeline las necesite
- Los riesgos de contenido están documentados
- La deduplicación con material existente está verificada

> **Excepción:** Material oficial de la Iglesia con authority conocida (escrituras,
> conferencia general, manuales correlacionados) puede tener Fase 0 simplificada.

### Estados

| Estado | Significado | Gate |
|--------|-------------|------|
| `descargado` | Archivos en disco, sin indexar | Commit hecho |
| `researched` | Fase 0 completa: authority y KG evaluados | Fase 0 pasos 1-2 aprobados |
| `pre-seeded` | Relaciones KG cargadas al grafo | KG pre-seed ejecutado |
| `ingested` | Pipeline completo (FTS + vectors + KG) | Pipeline ejecutado, `/corpus/status` verificado |
| `blocked` | Impedimento técnico (formato, merge, etc.) | — |

### Transiciones

**1. descargado → researched:** Escribir Fase 0 en `fase0/{slug}.md`:
  - Paso 1: Investigación editorial (web research) — **obligatorio, no sustituible por LLM**
  - Paso 2: Análisis de contenido, authority, valor KG, deduplicación, riesgos

**2. researched → pre-seeded:** Cargar relaciones KG identificadas en Fase 0 al grafo.

**3. pre-seeded → ingested:** Ejecutar pipeline incremental, verificar `/corpus/status`.

**4. ingested (confirmado):** Mover a `03-corpus-inventory.md`, eliminar de este archivo.
