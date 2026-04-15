# Corpus Expansion — Backlog

Items pendientes de trabajo. Se divide en tres categorías:
1. **Pendientes de descarga** — material aún no en el corpus
2. **Pendientes de indexación** — descargados, esperando ingest pipeline
3. **KG enrichment** — material ingested que necesita relaciones adicionales

Para inventario de lo ya completo → `03-corpus-inventory.md`.
Para catálogos de fuentes → `05-source-registry.md`.
Para análisis detallado por material → `fase0/`.

> **Última reconciliación:** 2026-04-09 — validado contra contenido real en disco.

---

## 1. Pendientes de descarga

### `blocked`

| Material | Script | Problema | Fase 0 |
|----------|--------|----------|--------|
| Música para los jóvenes | `download_music.py --collection youth-music` | API `/study/api/v3/` retorna 404 para `/music/youth-music/` — requiere endpoint alternativo | `fase0/music.md` |

### `backlog` — requieren investigación

| Material | authority | Prioridad | Notas | Fase 0 |
|----------|-----------|-----------|-------|--------|
| Reference Guide to Holy Bible | 80 | MEDIA | Study aid oficial; requiere adaptar `scrape_study_aids.py` | `fase0/study-aids.md` |
| Reference Guide to Book of Mormon | 80 | MEDIA | Study aid oficial; requiere adaptar `scrape_study_aids.py` | `fase0/study-aids.md` |
| Index to Triple Combination | 80 | BAJA | Extends TG coverage to D&C+PGP; large volume | `fase0/study-aids.md` |
| A Marvelous Work and a Wonder (LeGrand Richards) | 45 | MEDIA | Investigar disponibilidad digital | — |
| Our Search for Happiness (M.R. Ballard) | 45 | MEDIA | Investigar disponibilidad digital | — |
| Teachings of the Prophet Joseph Smith | 45 | MEDIA | Investigar: sitio oficial vs dominio público | — |
| Doctrines of Salvation (JFS, 3 vols) | 45 | MEDIA | No en sitio oficial; investigar BYU/MTP | — |
| Teaching, No Greater Call (1999) | 60 | ALTA | Fase 0 completa. Bilingüe. Sitio oficial (`download_manual.py`). Cadena pedagógica CES. | `fase0/teaching-no-greater-call.md` |
| Teach Ye Diligently (Boyd K. Packer) | 45 | BLOCKED | Fase 0 completa. archive.org = DRM/CDL, sin texto extraíble. Solo compra o OCR físico. | `fase0/teach-ye-diligently.md` |
| Journal of Discourses (26 vols) | 20 | BAJA | 1,426 discursos, ~5M palabras. Fase 0 completa. Solo EN. No oficial, imprecisión documentada. | `fase0/journal-of-discourses.md` |
| Life Help (mini-manuals) | 60 | BAJA | Hubs sin texto nuevo; valor KG mínimo | — |
| Ensign archive (1971-2020) | 60 | BAJA | Volumen enorme; separado de Liahona | — |
| ~20 RSC BYU PDF-only | varies | BAJA | No disponibles para lectura online; requieren scraper de PDF o compra | — |

> **Nota:** La sección `researched` (Gutenberg) fue eliminada 2026-04-09.
> Todos los libros Gutenberg listados previamente ya están descargados e ingested.
> Sus análisis Fase 0 se preservan en `fase0/` como referencia histórica.
> Liahona también fue eliminada: 19,747 artículos descargados (11,975 EN + 7,772 ES).
> Harmony of the Gospels, Bible Chronology y Abbreviations ya descargados (study-aids).

---

## 2. Pendientes de indexación

Material ya descargado al corpus pero que no ha pasado por el pipeline de indexación
(FTS + vectors + KG).

### B.H. Roberts — Obras completas

> Análisis detallado: `fase0/bh-roberts.md`

| Material | Caps | authority | Corpus path |
|----------|------|-----------|-------------|
| Corianton | 11 | 25 | `corpus/en/books/corianton/` |
| Missouri Persecutions | 20 | 40 | `corpus/en/books/missouri-persecutions/` |
| New Witness for God (3 vols) | 70 | 40 | `corpus/en/books/new-witness-for-god-*/` |
| Outlines of Ecclesiastical History | 50 | 40 | `corpus/en/books/outlines-ecclesiastical-history/` |
| Seventy's Course in Theology (5 vols) | 84 | 40 | `corpus/en/books/seventys-course-theology-*/` |
| Life of John Taylor | 40 | 40 | `corpus/en/books/life-of-john-taylor/` |
| Mormon Doctrine of Deity | 13 | 40 | `corpus/en/books/mormon-doctrine-of-deity/` |
| Rise and Fall of Nauvoo | 32 | 40 | `corpus/en/books/rise-and-fall-of-nauvoo/` |

### Diccionarios bíblicos clásicos

> Análisis detallado: `fase0/bible-dictionaries.md`

| Material | Entradas | authority | Corpus path |
|----------|----------|-----------|-------------|
| Easton's Bible Dictionary | ~3,964 | 15 | `corpus/en/reference/easton-bible-dictionary/` |
| Smith's Bible Dictionary | ~4,556 | 15 | `corpus/en/reference/smith-bible-dictionary/` |
| Hitchcock's Bible Names | 2,614 | 15 | `corpus/en/reference/hitchcock-bible-names/` |
| ISBE | ~10,121 | 20 | `corpus/en/reference/isbe/` |
| Hastings' Dictionary | ~5,915 | 20 | `corpus/en/reference/hastings-dictionary-of-the-bible/` |

---

## 3. KG enrichment pendiente (material ya ingested)

Material indexado que tiene relaciones KG identificadas pero no pre-seeded.

| Material | Relaciones pendientes | Fase 0 |
|----------|----------------------|--------|
| Jesus the Christ | `TAUGHT` (Resurrection, Atonement, Law of Moses), `QUOTED_BY` (Isaiah→JC), `TYPE_OF` (High Priest) | `fase0/jesus-the-christ.md` |
| Preach My Gospel | `PREREQUISITE_FOR` cadena primeros principios (Faith→Repentance→Baptism→HG→Endure) | `fase0/preach-my-gospel.md` |

---

## Prioridades recomendadas (actualizado 2026-04-09)

> **Lo que ya está completo:** Escrituras, Conferencia General, 60+ manuales oficiales,
> **~70 libros Gutenberg** (19 previos + 34 nuevos + B.H. Roberts), himnos/canciones,
> study aids (GEE, TG, BD, JST, Harmony, Chronology, Abbreviations), HC 1-7,
> **57 libros RSC BYU**, **28 libros BYU Studies**, **Liahona EN+ES (19,747 arts)** — TODO descargado.
>
> **Lo que queda:** ~20 RSC PDF-only (sin HTML), 1 RSC parcial (`fulness-gospel` URL bug),
> fuentes secundarias (CCEL, womeninthescriptures.com), ~30 Gutenberg ficción/baja prioridad.
> Church site: Youth Music (blocked — API 404) y Ensign archive (sin investigar).
> Libros individuales (Richards, Ballard, TPJS, Doctrines of Salvation) requieren investigación.
>
> **Regla:** Iglesia > RSC > BYU Studies > MTP > Gutenberg > CCEL > Archive.org.

### Materiales oficiales pendientes (Church site)

| Prioridad | Material | Script | Justificación |
|-----------|----------|--------|---------------|
| 🔴 **blocked** | Música para los jóvenes | `download_music.py` | API 404 — endpoint `/music/` no soportado por Study API |
| ⚫ **P6** | Ensign archive (1971-2020) | investigar | Volumen enorme; separado de Liahona |
| ✅ ~~Liahona~~ | ~~`download_liahona.py`~~ | **Completado** — 19,747 arts (11,975 EN + 7,772 ES) |

### RSC BYU — 214 libros (catálogo completo en `05-source-registry.md`)

> **Completado 2026-04-05:** 57 libros descargados de ~78 seleccionados.
> ~20 libros son PDF-only ("not available for online reading").
> 1 libro parcial (`fulness-gospel` — URL bug en PDF construction).

| Prioridad | Tipo de contenido | Libros | ✅ Descargados | ❌ PDF-only |
|-----------|-------------------|--------|---------------|------------|
| 🔴 **P1** | Exégesis escritural (LdM, D&C, PGP, Bible, Isaías, JST) | 23 | 18 | 5 |
| 🟡 **P2** | Doctrina, convenios, templo, cristología | 19 | 14 (+1 partial) | 3 |
| 🟢 **P3** | Fe práctica, apologética, salud mental | 16 | 14 | 2 |
| 🔵 **P4** | Historia selectiva | 13 | 6 | 7 |
| ⚪ **P5** | Relaciones interreligiosas | 7 | 5 | 2 |

### BYU Studies — ~~pendientes~~ ✅ completado (catálogo en `05-source-registry.md`)

> **Completado 2026-04-05:** 28 de 29 libros online descargados (excl. HC 1-6 ya en corpus
> vía Gutenberg y `the-st-louis-luminary` no intentado).

| Prioridad | Material | Estado |
|-----------|----------|--------|
| 🟠 **P1** | BYU NT Commentary (4 vols) | ✅ 107 files |
| 🟠 **P1** | Doctrine and Covenants Contexts | ✅ 136 files |
| 🟠 **P1** | Opening the Heavens | ✅ 13 files |
| 🟡 **P2** | NT New Renditions (14 vols) | ✅ 160 files |
| 🟡 **P2** | My Fellow Servants | ✅ 27 files |
| 🟢 **P3** | Charting the Scriptures (2 vols) | ✅ 420 files |
| 🔵 **P4** | Standalone books (5) | ✅ 119 files |
| ⚪ Upgrade | HC vols 1-6 de BYU Studies | Pendiente — mejorar calidad vs Gutenberg (opcional) |

### MTP / Gutenberg — ~~textos pendientes~~ ✅ batch completado (catálogo en `05-source-registry.md`)

> **Completado 2026-04-05:** 34 libros descargados (~461 archivos).
> Incluye P2-P5 + extras. Varios textos cortos como documento único (sin capítulos).

| Prioridad | Material | Estado |
|-----------|----------|--------|
| 🟡 **P2** | Lectures on Faith, Wentworth Letter, Key to Theology, Voice of Warning, Mediation & Atonement, Rational Theology, Ancient Apostles | ✅ 95 files |
| 🟢 **P3** | Life of JS (Cannon), Life of a Pioneer, Jacob Hamblin, My First Mission, Reminiscences, Mormon Battalion, Pratt's Visions, Proclamation, Gen. Smith's Views, Myth of MS Found | ✅ 181 files |
| 🔵 **P4** | Women of Mormondom, Heroines, Lydia Knight, Rep. Women, Scrap Book Vol 2, Scraps of Biography | ✅ 178 files |
| ⚪ **P5** | Mormon Doctrine (Penrose), Cowley's Talks, Gospel Themes, Plan of Salvation, Rays of Living Light, What Jesus Taught | ✅ 6 files |
| ⚪ **Extra** | Blood Atonement, Story of Mormonism, Joseph Smith as Scientist, Latter-day Prophet for Young | ✅ 4 files |
| ⚫ **P6** | Journal of Discourses (26 vols) | `researched` — Fase 0 completa, authority 20, fuente: journalofdiscourses.com |

---

## Protocolo de actualización de status

### Estados

| Estado | Significado | Gate de entrada |
|--------|-------------|-----------------|
| `backlog` | Identificado, requiere investigación | — |
| `researched` | Fase 0 completa: contenido entendido, authority modelada, valor KG evaluado | Fase 0 paso 1-2 aprobados |
| `prepared` | Script listo y probado, estructura corpus definida | Análisis técnico de fuente + script funcional |
| `descargado` | En el corpus (archivos en disco) | Script ejecutado, commit hecho |
| `ingested` | Indexado (FTS + vectors + KG) | Pipeline ejecutado, `/corpus/status` verificado |
| `blocked` | Impedimento técnico que impide avanzar | — |

### Transiciones

**1. backlog → researched:** Escribir Fase 0 en `fase0/{slug}.md` con dos pasos obligatorios:

  **Paso 1 — Investigación editorial (web research).** Esto NO es opcional ni sustituible
  por conocimiento previo del LLM. Requiere búsqueda en internet para establecer:
  - Historia editorial del material (quién lo publicó, cuándo, por qué, cambios a lo largo del tiempo)
  - Contexto institucional (posición oficial de la Iglesia respecto al material, si aplica)
  - Audiencia original y alcance
  - Ediciones, revisiones, traducciones disponibles

  **Paso 2 — Análisis de contenido y valor para el corpus.** Basado en los hallazgos del paso 1:
  - Estructura de contenido (secciones, tipos de texto, qué contiene doctrinalmente)
  - Modelo de authority fundamentado en el contexto editorial (no asumido)
  - Valor KG: entidades nuevas, relaciones únicas que no se pueden inferir de otro material
  - Deduplicación con material existente en el corpus
  - Riesgos de contenido (doctrinas abandonadas, contexto histórico necesario, sesgos)
  - Estimación de volumen

  > **Por qué el paso 1 es un gate obligatorio:** Sin investigación editorial, los niveles de
  > authority y las relaciones KG se asignan sin fundamento. Un material puede parecer
  > doctrinalmente sólido pero tener un contexto editorial que cambie drásticamente su
  > authority (ej. publicado sin correlación, desautorizado posteriormente, etc.).

**2. researched → prepared:** Análisis técnico de la fuente de descarga:
  - Estructura del sitio/API (URL patterns, selectores HTML, endpoints)
  - Prueba de extracción (sample de 2-3 documentos)
  - Diseño del script (flujo, encoding, manejo de errores)
  - Estructura propuesta en corpus (paths, naming, meta.json schema)
  - Comandos de descarga documentados
  - Agregar script/comando en la tabla del backlog

**3. prepared → descargado:** Ejecutar script, commit corpus files

**4. descargado → ingested:** Ejecutar pipeline, verificar en `/corpus/status`

**5. ingested (confirmado):** Mover entrada de aquí → `03-corpus-inventory.md`, eliminar de este archivo
