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
> 40+ libros Gutenberg, himnos/canciones, study aids, HC 1-7 — TODO ingested.
>
> **Lo que queda:** RSC BYU (214 libros), BYU Studies (31 pendientes),
> MTP/Gutenberg (~89 títulos), fuentes secundarias (CCEL, womeninthescriptures.com).
> Church site: solo Youth Music (blocked — API 404) y Ensign/Liahona (sin investigar).
>
> **Regla:** Iglesia > RSC > BYU Studies > MTP > Gutenberg > CCEL > Archive.org.

### Materiales oficiales pendientes (Church site)

| Prioridad | Material | Script | Justificación |
|-----------|----------|--------|---------------|
| 🔴 **blocked** | Música para los jóvenes | `download_music.py` | API 404 — endpoint `/music/` no soportado por Study API |
| ⚫ **P6** | Ensign / Liahona archive | investigar | Volumen enorme; priorizar por tema |

### RSC BYU — 214 libros (catálogo completo en `05-source-registry.md`)

| Prioridad | Tipo de contenido | Libros | Notas |
|-----------|-------------------|--------|-------|
| 🔴 **P1** | Exégesis escritural (LdM, D&C, PGP, Bible, Isaías, JST) | 23 | `opening-isaiah`, `abinadi`, `introduction-book-abraham`, etc. |
| 🟡 **P2** | Doctrina, convenios, templo, cristología | 19 | Easter Conference (10), Sperry Symposium, templo |
| 🟢 **P3** | Fe práctica, apologética, salud mental | 16 | `freedom-scrupulosity`, `reason-faith`, etc. |
| 🔵 **P4** | Historia selectiva | 13 | `council-fifty`, `sister-prophet`, `my-dear-sister` |
| ⚪ **P5** | Relaciones interreligiosas | 7 | `view-hebrews`, `mormons-muslims`, etc. |

### BYU Studies — pendientes (31 libros, catálogo en `05-source-registry.md`)

| Prioridad | Material | Notas |
|-----------|----------|-------|
| 🟠 **P1** | BYU NT Commentary (4 vols) | Comentario académico SUD del NT |
| 🟠 **P1** | Doctrine and Covenants Contexts | Contexto histórico D&C |
| 🟠 **P1** | Opening the Heavens | Manifestaciones divinas 1820-1844 |
| 🟡 **P2** | NT New Renditions (14 vols) | Traducción moderna del NT |
| 🟡 **P2** | My Fellow Servants | Historia del sacerdocio |
| 🟢 **P3** | Charting the Scriptures (2 vols) | Charts escriturales |
| 🔵 **P4** | Remaining standalone books (5) | Sustaining the Law, McLellin, etc. |
| ⚪ Upgrade | HC vols 1-6 de BYU Studies | Mejorar calidad vs Gutenberg (opcional) |

### MTP / Gutenberg — textos pendientes (catálogo en `05-source-registry.md`)

| Prioridad | Material | Notas |
|-----------|----------|-------|
| 🟡 **P2** | Lectures on Faith, Wentworth Letter | Doctrina fundacional Kirtland |
| 🟢 **P3** | Mediation and Atonement (Taylor), Key to Theology (Pratt) | Teología profética |
| 🔵 **P4** | Representative Women of Deseret, Women of Mormondom | Perspectiva femenina |
| ⚫ **P6** | Journal of Discourses (26 vols) | MTP no lo tiene; enorme; authority baja |

---

## Protocolo de actualización de status

Cuando un material cambia de estado:

1. **backlog → researched:** Escribir análisis Fase 0 en `fase0/{slug}.md`
2. **researched → prepared:** Agregar script/comando en esta tabla
3. **prepared → descargado:** Ejecutar script, commit corpus files
4. **descargado → ingested:** Ejecutar pipeline, verificar en `/corpus/status`
5. **ingested (confirmado):** Mover entrada de aquí → `03-corpus-inventory.md`, eliminar de este archivo
