# Corpus Expansion — Backlog de descarga

Material identificado pero **aún no descargado** al corpus. Este archivo cubre exclusivamente
el ciclo de descarga. Para material ya descargado pendiente de indexación → `04b-indexation-backlog.md`.

Para inventario de lo ya completo → `03-corpus-inventory.md`.
Para catálogos de fuentes → `05-source-registry.md`.
Para análisis detallado por material → `fase0/`.

> **Última reconciliación:** 2026-04-16 — auditoría FTS vs disco, separación descarga/indexación.

---

## 1. Pendientes de descarga

### `blocked`

| Material | Script | Problema | Fase 0 |
|----------|--------|----------|--------|
| Música para los jóvenes | `download_music.py --collection youth-music` | API `/study/api/v3/` retorna 404 para `/music/youth-music/` — requiere endpoint alternativo | `fase0/music.md` |

### `backlog` — requieren investigación y/o descarga

| Material | authority | Prioridad | Notas | Fase 0 |
|----------|-----------|-----------|-------|--------|
| Reference Guide to Holy Bible | 80 | MEDIA | Study aid oficial; requiere adaptar `scrape_study_aids.py` | `fase0/study-aids.md` |
| Reference Guide to Book of Mormon | 80 | MEDIA | Study aid oficial; requiere adaptar `scrape_study_aids.py` | `fase0/study-aids.md` |
| Index to Triple Combination | 80 | BAJA | Extends TG coverage to D&C+PGP; large volume | `fase0/study-aids.md` |
| A Marvelous Work and a Wonder (LeGrand Richards) | 45 | MEDIA | Investigar disponibilidad digital | — |
| Our Search for Happiness (M.R. Ballard) | 45 | MEDIA | Investigar disponibilidad digital | — |
| Teachings of the Prophet Joseph Smith | 45 | MEDIA | Investigar: sitio oficial vs dominio público | — |
| Life Help (mini-manuals) | 60 | BAJA | Hubs sin texto nuevo; valor KG mínimo | — |
| Ensign archive (1971-2020) | 60 | BAJA | Volumen enorme; separado de Liahona | — |
| ~20 RSC BYU PDF-only | varies | BAJA | No disponibles para lectura online; requieren scraper de PDF o compra | — |
| Conferencia General ES pre-199004 | 80 | MEDIA | Corpus `general-conference/es/` empieza abril 1990. El lote epub traía Liahona enero 1989 (= Oct 1988 GC en ES) pero la fuente es scrape pirata (`bibliotecasud.blogspot.com`) con columnas intercaladas ilegibles — rechazada 2026-04-22. Re-descargar limpio desde `churchofjesuschrist.org` con scraper GC. | `fase0/gc-198810-liahona-198901.md` (rechazado) |
| Doctrina Mormona (ES) — Bruce R. McConkie | 35 | MEDIA | Traducción ES de *Mormon Doctrine* (1966). El epub del lote tiene 798 spine files pero sin estructura per-entry (solo 25 h1s para las letras A-Z). El EN ya en corpus (`books/gospelink/mormon-doctrine/`) tiene 2007 entradas granuladas; incorporar esta versión ES degradaría el corpus con chunks coarse. Rechazado 2026-04-23. Considerar: scrape directo ES de alguna edición digital mejor estructurada, o post-procesar el epub actual con detección heurística de fronteras de entrada. | — |

> **Nota:** La sección `researched` (Gutenberg) fue eliminada 2026-04-09.
> Todos los libros Gutenberg listados previamente ya están descargados e ingested.
> Liahona también fue eliminada: 19,747 artículos descargados (11,975 EN + 7,772 ES).
> Harmony of the Gospels, Bible Chronology y Abbreviations ya descargados (study-aids).

### Recientemente completados (descarga)

Materiales que pasaron de este backlog a disco. Pendientes de indexación en `04b-indexation-backlog.md`.

| Material | Fecha | Archivos | Destino |
|----------|-------|----------|---------|
| ~~Teaching, No Greater Call~~ | 2026-04-15 | 182 (EN+ES) | `corpus/{lang}/manuals/teaching-no-greater-call/` |
| ~~Teach Ye Diligently~~ | 2026-04-15 | 18 (EN) | `corpus/en/books/teach-ye-diligently/` |
| ~~Interpreter Journal~~ | 2026-04-09 | 888 (EN) | `corpus/en/books/interpreter-journal/` |
| ~~Journal of Discourses~~ | 2026-04-08 | 1,425 (EN) | `corpus/en/books/journal-of-discourses/` |
| ~~Missionary Guide 1988~~ | 2026-04-12 | 18 (EN) | `corpus/en/manuals/missionary-guide-1988/` |
| ~~Doctrines of Salvation~~ | 2026-04-07 | 60 .md (EN) | `corpus/en/books/doctrines-of-salvation/` |

---

## 2. Prioridades recomendadas (actualizado 2026-04-16)

> **Lo que ya está descargado + indexado:** Escrituras, Conferencia General, 60+ manuales oficiales,
> ~70 libros Gutenberg (19 previos + 34 nuevos + B.H. Roberts), himnos/canciones,
> study aids (GEE, TG, BD, JST, Harmony, Chronology, Abbreviations), HC 1-7,
> 57 libros RSC BYU, 28 libros BYU Studies, Liahona EN+ES (19,747 arts),
> 5 diccionarios bíblicos, 543 biografías AG — TODO descargado e indexado.
>
> **Descargado, pendiente de indexación:** → ver `04b-indexation-backlog.md`
>
> **Lo que queda por descargar:** ~20 RSC PDF-only (sin HTML), 1 RSC parcial (`fulness-gospel` URL bug),
> fuentes secundarias (CCEL, womeninthescriptures.com), ~30 Gutenberg ficción/baja prioridad.
> Church site: Youth Music (blocked — API 404) y Ensign archive (sin investigar).
> Libros individuales (Richards, Ballard, TPJS) requieren investigación.
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

| Prioridad | Tipo de contenido | Libros | Descargados | PDF-only |
|-----------|-------------------|--------|-------------|----------|
| 🔴 **P1** | Exégesis escritural (LdM, D&C, PGP, Bible, Isaías, JST) | 23 | 18 | 5 |
| 🟡 **P2** | Doctrina, convenios, templo, cristología | 19 | 14 (+1 partial) | 3 |
| 🟢 **P3** | Fe práctica, apologética, salud mental | 16 | 14 | 2 |
| 🔵 **P4** | Historia selectiva | 13 | 6 | 7 |
| ⚪ **P5** | Relaciones interreligiosas | 7 | 5 | 2 |

### BYU Studies — ✅ completado (catálogo en `05-source-registry.md`)

> **Completado 2026-04-05:** 28 de 29 libros online descargados (excl. HC 1-6 ya en corpus
> vía Gutenberg y `the-st-louis-luminary` no intentado).

| Prioridad | Material | Estado |
|-----------|----------|--------|
| ⚪ Upgrade | HC vols 1-6 de BYU Studies | Pendiente — mejorar calidad vs Gutenberg (opcional) |

### MTP / Gutenberg — ✅ batch completado (catálogo en `05-source-registry.md`)

> **Completado 2026-04-05:** 34 libros descargados (~461 archivos).

---

## 3. Protocolo de descarga

### Workflow actualizado (2026-04-16)

La descarga es **independiente** de Fase 0. Un material puede descargarse oportunistamente
cuando la fuente está disponible, sin esperar investigación editorial. El gate de Fase 0
se aplica a la **indexación**, no a la descarga.

```
identificado → descargado → [Fase 0] → indexado → ingested
     │              │            │           │
     │              │            │           └── Pipeline FTS+vectors+KG
     │              │            └── Investigación editorial + authority + KG pre-seed
     │              └── Archivos en disco, commit hecho
     └── Material identificado como candidato
```

**Descarga oportunista:** Si la fuente está accesible y el material es claramente relevante,
se descarga directamente. No requiere Fase 0 previa. Esto permite:
- Aprovechar ventanas de acceso (APIs que pueden cambiar, préstamos digitales temporales)
- Separar el trabajo mecánico (scripting) del trabajo intelectual (investigación)
- Avanzar en paralelo: descargar mientras se investiga otro material

**El gate de Fase 0 sigue siendo obligatorio**, pero ahora controla la transición
`descargado → indexado`. Antes de indexar, el material DEBE tener:
1. Investigación editorial (web research) — paso 1 de Fase 0
2. Análisis de contenido y valor KG — paso 2 de Fase 0
3. Modelo de authority fundamentado
4. Relaciones KG pre-seeded

> **Razón del cambio:** La experiencia mostró que descargar y investigar son actividades
> con ritmos diferentes. Bloquear la descarga por falta de Fase 0 desperdicia oportunidades.
> Pero indexar sin Fase 0 produce authority sin fundamento y KG sin pre-seeding.

### Estados

| Estado | Significado | Gate de entrada |
|--------|-------------|-----------------|
| `backlog` | Identificado, requiere investigación | — |
| `descargado` | En el corpus (archivos en disco) | Script ejecutado, commit hecho |
| `blocked` | Impedimento técnico que impide descargar | — |

Para estados de indexación (`researched`, `prepared`, `ingested`) → `04b-indexation-backlog.md`.
