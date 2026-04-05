# Corpus Expansion — Backlog

Items pendientes de trabajo. Se divide en tres categorías:
1. **Pendientes de descarga** — material aún no en el corpus
2. **Pendientes de indexación** — descargados, esperando ingest pipeline
3. **KG enrichment** — material ingested que necesita relaciones adicionales

Para inventario de lo ya completo → `03-corpus-inventory.md`.
Para catálogos de fuentes → `05-source-registry.md`.
Para análisis detallado por material → `fase0/`.

---

## 1. Pendientes de descarga

### `blocked`

| Material | Script | Problema | Fase 0 |
|----------|--------|----------|--------|
| Música para los jóvenes | `download_music.py --collection youth-music` | API `/study/api/v3/` retorna 404 para `/music/youth-music/` — requiere endpoint alternativo | `fase0/music.md` |

### `backlog` — requieren investigación

| Material | authority | Prioridad | Notas | Fase 0 |
|----------|-----------|-----------|-------|--------|
| Reference Guide to Holy Bible + BoM | 80 | MEDIA | Study aid oficial; requiere adaptar `scrape_study_aids.py` | `fase0/study-aids.md` |
| A Marvelous Work and a Wonder (LeGrand Richards) | 45 | MEDIA | Investigar disponibilidad digital | — |
| Our Search for Happiness (M.R. Ballard) | 45 | MEDIA | Investigar disponibilidad digital | — |
| Teachings of the Prophet Joseph Smith | 45 | MEDIA | Investigar: sitio oficial vs dominio público | — |
| Doctrines of Salvation (JFS, 3 vols) | 45 | MEDIA | No en sitio oficial; investigar BYU/MTP | — |
| Journal of Discourses (26 vols) | 25 | BAJA | Enorme. MTP declinó transcribirlo. Solo PDF/OCR en Archive.org/BYU | — |
| Life Help (mini-manuals) | 60 | BAJA | Hubs sin texto nuevo; valor KG mínimo | — |
| Ensign / Liahona archive | 60 | BAJA | Volumen enorme (~12,000 docs); priorizar por tema | — |

### `researched` — Gutenberg, script pendiente

> Estos libros ya tienen Fase 0 completa y están en el corpus (descargados),
> pero el status `researched` indica que fueron analizados — en realidad ya están
> **descargados e ingested** según la tabla de inventario. Ver nota al final.

| Material | authority | Gutenberg # | Fase 0 |
|----------|-----------|-------------|--------|
| Essentials in Church History | 45 | 45054 | `fase0/gutenberg-church-history.md` |
| History of Prophet Joseph by His Mother | 35 | 45619 | `fase0/gutenberg-church-history.md` |
| Autobiography of Parley P. Pratt | 40 | 44896 | `fase0/gutenberg-biographical.md` |
| Gospel Doctrine (JFS) | 50 | 47109 | `fase0/gutenberg-doctrinal.md` |
| Life of Heber C. Kimball | 40 | 35333 | `fase0/gutenberg-biographical.md` |
| The Government of God | 40 | 44941 | `fase0/gutenberg-doctrinal.md` |
| Leaves from My Journal | 40 | 46028 | `fase0/gutenberg-biographical.md` |
| Wilford Woodruff, Fourth President | 40 | 47703 | `fase0/gutenberg-biographical.md` |
| Heber C. Kimball's Journal | 40 | 47519 | `fase0/gutenberg-biographical.md` |
| William Clayton's Journal | 40 | 45051 | `fase0/gutenberg-biographical.md` |
| Early Scenes in Church History | 35 | 46783 | `fase0/gutenberg-church-history.md` |
| Life of David W. Patten | 35 | 51730 | `fase0/gutenberg-biographical.md` |
| Biography of Lorenzo Snow | 40 | 47708 | `fase0/gutenberg-biographical.md` |
| The Story of the Mormons | 20 | 2443 | `fase0/gutenberg-church-history.md` |

> **Nota de reconciliación:** Varios de estos items figuraban como `researched` en el
> backlog original, pero el inventario del corpus muestra que ya están descargados
> e indexados. Sus análisis Fase 0 se preservan en `fase0/` como referencia histórica.
> Estos items deben verificarse y, si están ingested, eliminarse de esta lista.

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

## Prioridades recomendadas (actualizado 2026-04-05)

> **Lo que ya está completo:** Escrituras, Conferencia General, 60+ manuales oficiales,
> **~70 libros Gutenberg** (19 previos + 34 nuevos + B.H. Roberts), himnos/canciones,
> study aids, HC 1-7, **57 libros RSC BYU**, **28 libros BYU Studies** — TODO descargado.
>
> **Lo que queda:** ~20 RSC PDF-only (sin HTML), 1 RSC parcial (`fulness-gospel` URL bug),
> fuentes secundarias (CCEL, womeninthescriptures.com), ~30 Gutenberg ficción/baja prioridad.
> Church site: solo Youth Music (blocked — API 404) y Ensign/Liahona (sin investigar).
>
> **Regla:** Iglesia > RSC > BYU Studies > MTP > Gutenberg > CCEL > Archive.org.

### Materiales oficiales pendientes (Church site)

| Prioridad | Material | Script | Justificación |
|-----------|----------|--------|---------------|
| 🔴 **blocked** | Música para los jóvenes | `download_music.py` | API 404 — endpoint `/music/` no soportado por Study API |
| ⚫ **P6** | Ensign / Liahona archive | investigar | Volumen enorme; priorizar por tema |

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
| ⚫ **P6** | Journal of Discourses (26 vols) | Pendiente — MTP no lo tiene; enorme; authority baja |

---

## Protocolo de actualización de status

Cuando un material cambia de estado:

1. **backlog → researched:** Escribir análisis Fase 0 en `fase0/{slug}.md`
2. **researched → prepared:** Agregar script/comando en esta tabla
3. **prepared → descargado:** Ejecutar script, commit corpus files
4. **descargado → ingested:** Ejecutar pipeline, verificar en `/corpus/status`
5. **ingested (confirmado):** Mover entrada de aquí → `03-corpus-inventory.md`, eliminar de este archivo
