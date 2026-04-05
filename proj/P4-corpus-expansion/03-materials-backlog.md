# Corpus Materials Backlog

Materiales candidatos para ingesta. Cada ítem incluye investigación previa,
relaciones KG esperadas, consideraciones especiales y estado del script.

## Estados

| Estado | Significado |
|--------|-------------|
| `ingested` | En el corpus, indexado |
| `prepared` | Investigado + script listo para ejecutar |
| `researched` | Investigado, script pendiente |
| `backlog` | Identificado, requiere investigación |

---

## Corpus actual (referencia)

> Actualizado 2026-04-05 contra contenido real en disco.

### Escrituras y ayudas de estudio

| Material | Estado | Notas |
|----------|--------|-------|
| Escrituras EN (todos los standard works) | `ingested` | |
| Escrituras ES (Book of Mormon) | `ingested` | AT/NT/D&C/PGP ES pendientes |
| Conferencia General 1971–2025 EN | `ingested` | ~6,900 charlas — **completo** |
| Conferencia General ES (~1990–2025) | `ingested` | Completo para lo disponible digitalmente — **completo** |
| Bible Dictionary | `ingested` | EN (1,275 entradas) |
| Guide to the Scriptures (GEE) | `ingested` | EN (813) + ES (810) — consolida TG+BD en ES |
| Topical Guide | `ingested` | EN (3,513 entradas) — en GEE ES |
| JST Appendix | `ingested` | EN+ES (94 caps) |
| Chapter headings / superscriptions | `ingested` | EN+ES — en `.meta.json` de cada capítulo |
| Volume introductions (BoM, D&C, PGP, OT, NT) | `ingested` | EN+ES — 29 archivos vía `scrape_introductions.py` |
| Harmony of the Gospels | `ingested` | 8 partes + intro — EN+ES |
| Bible Chronology (AT + NT) | `ingested` | intro + OT + NT — EN+ES |
| Abbreviations | `ingested` | EN+ES |
| Reference Guide to Holy Bible + BoM | `backlog` | Tier 0a — MEDIUM |

### Manuales y materiales oficiales

| Material | Estado | Notas |
|----------|--------|-------|
| General Handbook | `ingested` | EN+ES |
| Missionary Standards + Supplement | `ingested` | EN+ES |
| Proclamations (Family, Living Christ) | `ingested` | EN+ES |
| Preach My Gospel 2023 | `ingested` | EN+ES |
| Gospel Principles | `ingested` | 51 archivos EN+ES |
| True to the Faith | `ingested` | ~180 entradas EN+ES |
| Come Follow Me (2019–2026, 8 años) | `ingested` | Ciclo completo: NT, LdM, D&C, AT × 2 ciclos |
| Teachings of Presidents (17 volúmenes) | `ingested` | Todos: JS a Nelson, ~560 capítulos EN+ES |
| For the Strength of Youth (2022) | `ingested` | EN+ES |
| Gospel Topics Essays | `ingested` | 15 ensayos EN+ES |
| First Vision Accounts | `ingested` | 9 documentos EN+ES |
| Our Heritage | `ingested` | 11 capítulos EN+ES |
| Saints vols 1–4 | `ingested` | 214 capítulos EN+ES |
| Institute Manuals (CES) | `ingested` | 8 cursos (LdM, D&C, PGP, NT, Familia Eterna, Restauración, etc.) |
| Doctrines of the Gospel | `ingested` | Manual de seminario/instituto |
| Revelations in Context | `ingested` | D&C contexto histórico |
| At the Pulpit | `ingested` | 68 capítulos — mujeres de la Iglesia |
| Daughters in My Kingdom | `ingested` | 17 capítulos — historia de la Sociedad de Socorro |
| Christmas Study Plan (2024) | `ingested` | 9 archivos — 2025 no existe en el sitio |
| Easter / Holy Week Study Plan | `ingested` | 18 archivos (NT + BoM pistas paralelas) |
| Seminary Teacher Manuals (OT, NT, BOM, D&C) | `ingested` | OT 278, NT 312, BOM 312, D&C 280 archivos EN+ES cada uno |
| Seminary Student Manuals (OT, NT, BOM) | `ingested` | OT 218, NT 255-256, BOM 257 archivos EN+ES |
| Doctrinal Mastery (Seminary) | `ingested` | 4 archivos EN+ES |
| Marriage and Family Relations | `ingested` | 18 archivos EN+ES (bajo family-resources/) |
| Strengthening Marriage (Instructor + Couples) | `ingested` | 17 EN+ES (instructor bilingüe, couples EN-only) |
| Strengthening Family (Instructor + Parents) | `ingested` | 19 EN+ES (instructor bilingüe, parents EN-only) |
| Self-Reliance: Leaders Guide | `ingested` | 4 archivos EN+ES |
| Self-Reliance: My Path | `ingested` | 3 archivos EN+ES |
| Self-Reliance: Perpetual Education Fund | `ingested` | 1 archivo EN+ES |
| Self-Reliance: Facilitating Groups | `ingested` | 3 archivos EN+ES |
| Self-Reliance: Plan + Bishop's Guide | `ingested` | 1 archivo EN+ES |
| Institute Student Readings | `ingested` | 39 archivos EN-only (ES 404) |
| Institute Elevate Learning Experience | `ingested` | 10 EN + 11 ES |
| Teacher Development Skills | `ingested` | 27 archivos EN+ES (bajo seminaries-and-institutes/) |
| Principles of Christlike Teaching | `ingested` | 1 archivo EN-only |

### Música

| Material | Estado | Notas |
|----------|--------|-------|
| Himnos (Himnario clásico) | `ingested` | 341 archivos EN+ES |
| Himnos para el hogar y la Iglesia | `ingested` | 73 archivos EN+ES |
| Canciones para los niños | `ingested` | 268 archivos EN+ES |
| Ayudas para los Himnos | `ingested` | 90 archivos (About the Hymns 72 + Using 18) |
| Música para los jóvenes | `blocked` | API `/study/api/v3/` retorna 404 para `/music/youth-music/` — requiere investigación de endpoint alternativo |

### Libros (Gutenberg + BYU Studies + Church site)

| Material | Estado | Notas |
|----------|--------|-------|
| Jesus the Christ (Talmage) | `ingested` | 43 capítulos EN |
| Articles of Faith (Talmage) | `ingested` | 24 capítulos EN (Gutenberg) |
| Great Apostasy (Talmage) | `ingested` | 10 capítulos EN (Gutenberg) |
| House of the Lord (Talmage) | `ingested` | 11 capítulos EN (Gutenberg) |
| Discourses of Brigham Young | `ingested` | 42 capítulos EN (Gutenberg) |
| History of the Church vols 1–7 | `ingested` | 266 capítulos EN (HC7 BYU Studies, HC1-6 Gutenberg) |
| Autobiography of Parley P. Pratt | `ingested` | 54 capítulos EN |
| Gospel Doctrine (Joseph F. Smith) | `ingested` | 25 capítulos EN |
| + 30 libros adicionales de Gutenberg | `ingested` | Ver `corpus/en/books/` — ~40 dirs total |

---

## Tier 0 — Planes de Estudio Estacionales (authority=60)

### Christmas Study Plan (anual)

**Estado:** `ingested` — Script: `download_christmas_study_plan.py` — 2024 descargado (9 archivos). 2025 confirmado inexistente en el sitio oficial.

**Estructura:** 9 páginas — intro + "Light the World" overview + 7 lecturas
diarias (19–25 dic). Slug **año-sufijado** (`christmas-study-plan-2024`):
se renueva cada año. Requiere `--year` al ejecutar.

**URL:** `/study/manual/christmas-study-plan-{año}` | Bilingüe: sí

**Contenido por página:** devoción en prosa, pasajes escriturales con
preguntas de reflexión, enlace a video, actividad para niños, ideas de servicio.

**KG — relaciones esperadas:**
- 7 eventos del nacimiento (natividad) → secuencia temporal con relación
  `narrates_event` por día
- Profecías AT (Isaías, Miqueas, Alma 7) → intertextualidad con NT/LdM
- 3 Nefi 1 (noche sin oscuridad) vinculada al 23 dic → paralelo único LdM↔NT
- "Light the World" como concepto doctrinal con relaciones de servicio

**Consideración especial:** El slug cambia cada año → el corpus crecerá
con un directorio nuevo por edición. Priorizar la más reciente.

---

### Easter / Holy Week Study Plan

**Estado:** `ingested` — Script: `download_easter_study_plan.py` — 18 archivos en corpus

**Estructura:** 18 páginas en **dos pistas paralelas** que recorren
simultáneamente la misma semana:
- **Pista NT** (9 páginas): Palm Sunday → Easter Monday, cronología evangélica
- **Pista BoM** (8 páginas): mismos días, narrativa paralela en 3 Nefi

El slug es **permanente** (`easter-plan`) — se actualiza in-place cada año.

**URL:** `/study/manual/easter-plan` | Bilingüe: sí

**KG — valor estructural único:**
- Cada par de páginas (NT + BoM mismo día) crea relaciones `parallel_to`
  entre pasajes del NT y 3 Nefi — el corpus mismo establece esta intertextualidad
- `day_key` en meta.json (e.g., `"good-friday"`) es la clave de unión entre
  pistas → permite consultas como "¿qué paralelos hay entre Juan 19 y 3 Nefi?"
- 8 días × 2 pistas = 16 pares de intertextualidad doctrinal curada
- Expiación, Resurrección, Sacramento como conceptos con múltiples entradas
- Jueves Santo: Última Cena (NT) + institución del Sacramento en las Américas (BoM)

**Preguntas habilitadas:**
- "¿Qué paralelos hay entre la crucifixión y 3 Nefi?"
- "¿Cómo ven los SUD el Viernes Santo en relación al Libro de Mormón?"
- "¿Qué ocurrió en las Américas durante la semana de la Expiación?"

---

## KG: Materiales ya ingresados — análisis pendiente

### Jesus the Christ — James E. Talmage

**Estado corpus:** `ingested` (43 capítulos EN) | Script: `download_jesus_the_christ.py` | authority=45, author="James E. Talmage"

**KG — qué ya está capturado:**

| Tipo de relación | Mecanismo | Cobertura |
|-----------------|-----------|-----------|
| `AUTHORED_BY` James E. Talmage | meta.json → pipeline ✅ | 43 capítulos |
| Tipos AT → Jesucristo (Brazen Serpent, Passover Lamb, Isaac, Manna, Melchizedek, etc.) | `TYPE_OF` en relations.json ✅ | 14 tipos |
| Símbolos → Jesucristo (Vine, Shepherd, Cornerstone, Lamb, etc.) | `SYMBOLIZES` en relations.json ✅ | 17 símbolos |
| Profecías mesiánicas (Isaías, Miqueas, Samuel) | `PROPHECY_OF` / `PROPHESIED_ABOUT` ✅ | 16+9 entradas |
| Menciones de entidades doctrinales (Atonement, Resurrection, Faith, etc.) | Gazetteer NER ✅ | 200+ conceptos |

**KG — qué falta y debe agregarse a `relations.json`:**

| Relación | from | to | Prioridad |
|----------|------|----|-----------|
| `TAUGHT` | Jesus Christ | Resurrection | Alta — JTC caps 35-38 son LA fuente |
| `TAUGHT` | Jesus Christ | Atonement | Alta — JTC cap 2, 34-38 |
| `TAUGHT` | Jesus Christ | Sermon on the Mount | Ya existe en TAUGHT ✅ |
| `TAUGHT` | Jesus Christ | Law of Moses (fulfillment) | Alta — JTC caps 12-14 |
| `QUOTED_BY` | Isaiah | Jesus Christ | Media — JTC cita Isaías extensamente |
| `TYPE_OF` | High Priest (Levitical) | Jesus Christ | Media — JTC cap 3 |

**Nota:** El gazetteer no tiene entrada para "James E. Talmage" como `person`. La relación `AUTHORED_BY` se crea desde meta.json, pero si alguien busca "Talmage" en el KG no encontrará el nodo a menos que NER lo detecte del texto. Se recomienda agregar a gazetteers después de la ingesta.

---

### Preach My Gospel 2023

**Estado corpus:** `ingested` | authority=60 | EN+ES

**KG — qué ya está capturado:**

| Tipo de relación | Mecanismo | Cobertura |
|-----------------|-----------|-----------|
| Entidades doctrinales mencionadas (Faith, Repentance, Baptism, Atonement, Restoration, etc.) | Gazetteer NER ✅ | Alta densidad |
| Co-ocurrencia de entidades en el mismo chunk | `RELATED_TO` / `TEACHES` tipo-inferido ✅ | Todos los chunks |
| Scripture refs en footnotes | meta.json `scripture_refs` ✅ | ~200+ refs estimadas |
| Estructura de capítulos (5 lecciones = 5 nodos de trabajo) | meta.json→KG `work/PART_OF` ✅ | Solo si `title`/`book` están en meta.json — **verificar** |

**KG — qué falta y debe agregarse a `relations.json`:**

La secuencia de primeros principios (Artículo de Fe 4) es la contribución estructural más importante de PME:

```
Faith -[PREREQUISITE_FOR]-> Repentance
Repentance -[PREREQUISITE_FOR]-> Baptism
Baptism -[PREREQUISITE_FOR]-> Holy Ghost (gift)
Holy Ghost (gift) -[PREREQUISITE_FOR]-> Endure to End
```

Estas relaciones NO están en `relations.json`. Se producen co-ocurrencias genéricas (`RELATED_TO`) pero no la secuencia ordenada.

| Relación | from | to | Source ref |
|----------|------|----|------------|
| `PREREQUISITE_FOR` | Faith | Repentance | AoF 4; PME cap 3 |
| `PREREQUISITE_FOR` | Repentance | Baptism | AoF 4; PME cap 3 |
| `PREREQUISITE_FOR` | Baptism | Holy Ghost (gift) | AoF 4; D&C 20:41 |
| `PART_OF` | Faith | Gospel | AoF 4 |
| `PART_OF` | Repentance | Gospel | AoF 4 |
| `PART_OF` | Baptism | Gospel | AoF 4 |
| `PART_OF` | Holy Ghost (gift) | Gospel | AoF 4 |
| `TAUGHT` | Jesus Christ | Plan of Salvation | PME cap 2; 2 Nephi 9 |
| `TAUGHT` | Jesus Christ | Gospel | 3 Nephi 27:13-21 |

**Nota:** PME también estructura la Restauración como narrativa: Joseph Smith → Primera Visión → Restauración → Sacerdocio → Iglesia. Estas relaciones ya existen parcialmente en relations.json vía `RESTORED` (7 entradas) y `CONFERRED_KEYS_TO` (8 entradas).

---

## Tier 0a — Study Aids pendientes (authority=80)

> Las ayudas de estudio de las Escrituras tienen la misma authority que los
> standard works — son parte del canonizado Quad/Triple y están aprobadas
> por la Primera Presidencia.

### Harmony of the Gospels

**Estado:** `ingested` — Script: `scrape_harmony.py` — 8 partes + intro en corpus

**URL:** `/study/scriptures/harmony` — 8 partes + introducción | **Bilingüe:** verificar
**Autoridad:** 80 (parte del Quad oficial)

**Estructura:** Tabla de 6 columnas por evento:
`Evento | Lugar | Mateo | Marcos | Lucas | Juan + Revelación moderna`

La columna "Revelación moderna" incluye referencias del Libro de Mormón,
D&C y PGP — es la única harmonía que existe con paralelos LDS integrados.
~150 eventos en orden cronológico desde la premortalidad hasta la Resurrección.

**KG valor crítico:**
- Crea relaciones `PARALLEL_ACCOUNT_OF` explícitas entre pasajes de los
  cuatro evangelios — intertextualidad que NER no puede inferir
- Conecta NT con BoM y D&C en el mismo evento (e.g., nacimiento de Cristo
  → Lucas 2:6-7 ↔ 1 Nefi 11:18-20 ↔ Alma 7:10 ↔ 3 Nefi 1:4-22)
- Secuencia cronológica del ministerio → relaciones `PRECEDED_BY` entre eventos
- Cada evento = nodo tipo `event` con `location` y refs a múltiples volúmenes

**Script:** `scrape_study_aids.py` adaptado. ~10 archivos (1 por parte).

---

### Bible Chronology

**Estado:** `ingested` — Script: `scrape_bible_chronology.py` — intro + OT + NT en corpus

**URL:** `/study/scriptures/bible-chron` — intro + AT + NT | **Bilingüe:** verificar
**Autoridad:** 80

**Estructura:** Tablas con columnas: `Fecha B.C./A.D. | Evento | Historia judía | Sincronismos externos`.
- AT: desde la caída de Adán hasta 6 a.C. (~3,000 años)
- NT: A.D. 1–96 (~50-55 eventos), incluye historia cristiana, judía y romana en paralelo

**KG valor:**
- Crea nodos `period` con fechas absolutas para el KG → permite anclar
  entidades a tiempos concretos ("Abraham: ~2000 a.C.", "Crucifixión: A.D. 33")
- Sincronismos con historia secular (Babilonia, Persia, Roma) → relaciones
  `CONTEMPORARY_WITH` entre entidades bíblicas y figuras externas
- Habilita queries como "¿Qué profetas vivieron durante el cautiverio babilónico?"

**Script:** `scrape_study_aids.py` adaptado. ~3 archivos.

---

### Abbreviations

**Estado:** `ingested` — Script: `scrape_abbreviations.py` — EN+ES en corpus

**URL:** `/study/scriptures/quad` | **Bilingüe:** sí (mismas abreviaturas, distintos nombres)
**Autoridad:** 80

**Estructura:** Tabla de abreviaturas → nombre completo para los 4 volúmenes
del Quad: AT (39 libros), NT (27 libros), LdM (15 libros), D&C+PGP.
Incluye también: JST, TG, BD, GEE, A of F.

**Valor directo para el sistema:**
- Alimenta el normalizador de scripture refs en el parser: "1 Ne." → "1 Nephi",
  "A of F" → "Articles of Faith", "DyC" → "Doctrine and Covenants"
- Previene errores de NER que no reconoce formas abreviadas
- La versión ES confirma abreviaturas oficiales en español ("DyC", "Moro.")

**Script:** Una sola página, parseable directamente. ~2 archivos (EN+ES).

---

### Reference Guide to the Holy Bible + Reference Guide to the Book of Mormon

**Estado:** `backlog`

**URLs:** `/study/scriptures/bible-reference` y `/study/scriptures/bofm-reference`
**Autoridad:** 80 | **Bilingüe:** verificar

**Estructura:** Índices temáticos con secciones (Godhead, Gospel Topics, People,
Places, Events) y verse references por tema. El de BoM incluye secciones:
Jesus Christ, Doctrines, People, Events and Places.

**KG valor:** MEDIO — cubren terreno similar al TG/GEE ya ingresados. El valor
incremental es el agrupamiento temático diferente (más condensado). El de BoM
puede capturar relaciones entre personas y eventos del LdM que el TG no agrupa
de la misma forma.

**Script:** `scrape_study_aids.py` adaptado. ~10-20 archivos c/u.

---

## Tier 0b — Música Oficial (authority=65)

> Script único: `download_music.py --collection {nombre}`
> Meta capturada por himno: letra, `author`, `composer`, `tune`, `occasion`, `first_line`, `audio_urls`, `scripture_refs`, `footnotes`.

### Himnos (Himnario clásico, 1985)

**Estado:** `ingested` — `download_music.py --collection hymns` — 341 archivos EN+ES en corpus

**Estructura:** 333 himnos numerados. Aprobados por la Primera Presidencia.
Algunos usados en ordenanzas (por ej. "Oh Dios, Nuestro Padre Eterno" —
Sacramento; "En la Cruz del Calvario" — bautismo).

**URL:** `/manual/hymns/` | Bilingüe: sí — mismos slugs en EN y ES

**KG — relaciones esperadas:**
- Cada himno → `authored_by` → Person (compositor de letra) + `composed_by` → Person (compositor de música)
- ~40 himnos llevan `occasion` (Sacramento, Apertura/Cierre, Bautismo) → `associated_with` → Ordinance/Occasion
- ~60 himnos tienen `scripture_refs` directos → `references` → Verse
- Compositores recurrentes: William W. Phelps, Eliza R. Snow, Parley P. Pratt → perfiles de personas con múltiples `authored` edges
- Traducciones de himnos protestantes → `adapted_from` → Person (autor original, e.g., Charles Wesley, Isaac Watts)
- Himnos de ordinanzas → `required_for` → Ordinance

**Consideración especial:** Los autores de letra y música son frecuentemente
figuras históricas de la Iglesia temprana → enriquecen profiles de personas
(Eliza R. Snow, W.W. Phelps, etc.). Los compositores externos (Wesley, Watts,
Handel) son nuevos nodos de personas que el corpus actual no tiene.

**Audio:** La API devuelve enlaces a archivos `.mp3`/`.aiff` — `audio_urls`
en meta.json habilita futura búsqueda por tune o audio embedding.

---

### Himnos para el Hogar y la Iglesia (nuevo himnario, 2024–)

**Estado:** `ingested` — `download_music.py --collection hymns-home-church` — 73 archivos EN+ES en corpus

**Estructura:** 72 himnos en el primer lanzamiento; el colección irá creciendo.
Diseñado para uso tanto en el hogar como en reuniones. Formato más flexible
que el himnario clásico.

**URL:** `/music/hymns-for-home-and-church/` | Bilingüe: sí
Algunos slugs tienen sufijo `-release-3` (el script los normaliza).

**KG valor:** Complementa al himnario clásico. Algunos himnos son nuevos
(futuros nodos), otros son reediciones o arreglos alternativos de himnos
clásicos → relación `arrangement_of` → himno original.

---

### Canciones para los Niños (Children's Songbook)

**Estado:** `ingested` — `download_music.py --collection childrens-songbook` — 268 archivos EN+ES en corpus

**Estructura:** 148 canciones. Usadas en Primaria (niños 3–11 años).
Incluyen canciones doctrinales simples, canciones de acción, y canciones
de feriados.

**URL:** `/manual/childrens-songbook/` | Bilingüe: sí

**KG valor:**
- Canciones doctrinales en vocabulario simple → buenas para definir conceptos
  con lenguaje accesible (útil para respuestas a niños/familias)
- "I Am a Child of God" como nodo central — una de las canciones más conocidas
  → `teaches_concept` → divine_nature, identity_in_christ
- Canciones para cada artículo de fe → relación directa con doctrina

---

### Música para los Jóvenes (Youth Music)

**Estado:** `blocked` — API `/study/api/v3/` retorna 404 para todas las rutas `/music/youth-music/*`. Los álbumes existen en el sitio web pero no están expuestos vía la Study API. Requiere investigación de endpoint alternativo o scraping HTML directo.

**Estructura:** ~6 álbumes (2022–2026), ~12 canciones c/u. Publicados por
la Iglesia para apoyar al Programa de Jóvenes (Young Men/Young Women).
El hub (`/music/youth-music/`) está activo; la API descubre los álbumes
desde el HTML del hub.

**URL:** Hub `/music/youth-music/` → álbumes individuales | Bilingüe: sí

**KG valor:** Cada álbum está ligado a un tema del año para jóvenes (e.g.,
"Gather Israel 2026" → `theme_for` → año/programa). Artistas son miembros
contemporáneos → nuevos nodos de personas.

---

### Ayudas para los Himnos (Hymn Helps)

**Estado:** `ingested` — `download_music.py --collection hymn-helps` — 90 archivos EN (About the Hymns 72 + Using Hymnbook 11 + Using Songbook 7)

**Sub-recursos:**

| Sub-colección | URI | Idioma | Páginas |
|---------------|-----|--------|---------|
| About the Hymns | `/manual/sacred-music-gospel-study-resource-pilot` | **EN only** | ~72 |
| Using the Hymnbook | `/manual/using-the-hymnbook` | EN+ES | ~7 |
| Using the Songbook | `/manual/using-the-songbook` | EN+ES | ~6 |
| Using Hymns for Home and Church | `/music/using-hymns-for-home-and-church` | EN+ES | ~8 |

**"About the Hymns" — el más valioso:**
Por cada himno del nuevo himnario, incluye:
- Historia del texto y la música (fecha, contexto de composición)
- Doctrina relacionada con la letra
- 4–6 referencias escriturales por himno
- Preguntas de reflexión

**KG valor crítico:** Este recurso es la fuente más rica para relaciones
estructuradas de los himnos: cada página crea relaciones `hymn` → `teaches` →
concepto, `hymn` → `references` → versículo, con contexto histórico preciso.
Es esencialmente el comentario exegético oficial del nuevo himnario.

---

## Tier 1 — Clásicos de Autoridades Generales (authority=45)

### 1. The Articles of Faith — James E. Talmage

**Estado:** `ingested` — 24 capítulos EN en `corpus/en/books/articles-of-faith/` (descargado de Gutenberg)

**Estructura:** 13 capítulos, uno por artículo de fe. El libro expande cada
artículo con historia, doctrina comparada con otras tradiciones cristianas,
y referencias bíblicas exhaustivas.

**URL pattern probable:**
- TOC: `/study/manual/the-articles-of-faith`
- Capítulos: `/study/manual/the-articles-of-faith/chapter-{N}` (13 caps + prefacio)
- Bilingüe: probable — verificar

**Autoridad:** 45 — también comisionado por la Iglesia; los Artículos de Fe son
doctrina oficial, y el libro es su expansión canónica.

**KG — entidades y relaciones esperadas:**
- 13 artículos de fe como nodos doctrinales con relación `expands_on` → AoF 1–13
- Comparaciones con credos nicenos, credos apostólicos → `contrasts_with`
- Referencias a Reforma Protestante, patrística → `historical_context`
- Profecías OT citadas como cumplidas en NT → intertextualidad masiva
- Sacerdocio de Aarón y Melquisedec → relaciones institucionales
- Organización de la Iglesia primitiva vs restaurada

**Preguntas que habilita:**
- "¿En qué difiere la doctrina SUD sobre la Deidad de la Trinidad nicena?"
- "¿Cómo explica la Iglesia la apostasía y restauración del sacerdocio?"
- "¿Cuál es la base escritural de cada artículo de fe?"

**Script:** Adaptar `download_jesus_the_christ.py` — estructura idéntica, cambiar
`MANUAL_URI`, `SLUG_TO_FILENAME`, y meta fields. ~20 archivos por idioma.

---

### 2. The Great Apostasy — James E. Talmage

**Estado:** `ingested` — 10 capítulos EN en `corpus/en/books/great-apostasy/` (descargado de Gutenberg)

**Estructura:** 8 capítulos. Argumento histórico-doctrinal de que la apostasía
era prevista, ocurrió, y requería una restauración. Usa fuentes patrísticas
(Orígenes, Tertuliano, Agustín) y documentos históricos.

**URL pattern:**
- TOC: `/study/manual/the-great-apostasy`
- Capítulos: `/study/manual/the-great-apostasy/chapter-{N}`
- Bilingüe: sí

**Autoridad:** 45

**KG — valor especial:**
- Único material en el corpus que nombra y cita patrísticos → nodos nuevos
  (personas: Orígenes, Tertuliano, Constantino; períodos: Concilio de Nicea)
- Relación `caused_by` entre apostasía y corrupción doctrinal
- Relación `leads_to` entre apostasía → Restauración → Primera Visión
- Puente directo con *Jesus the Christ* cap. 40 y JS-H en PGP

**Preguntas:**
- "¿Qué evidencias históricas cita la Iglesia para la Gran Apostasía?"
- "¿Cuándo y cómo se perdieron las llaves del sacerdocio?"

**Script:** Mismo patrón que *Articles of Faith*. ~15 archivos por idioma.

---

### 3. A Marvelous Work and a Wonder — LeGrand Richards

**Estado:** `backlog`

**Descripción:** Manual apologético sobre la Restauración, estructurado para
investigadores. Extensamente usado por misioneros. Puede no estar en el sitio
oficial en formato de manual — requiere investigación de URL.

**Investigar:** ¿Está en `/study/manual/a-marvelous-work-and-a-wonder`?
¿O solo en Gospel Library app? ¿Dominio público (1950)?

---

### 4. Our Search for Happiness — M. Russell Ballard

**Estado:** `backlog`

**Descripción:** Libro apologético para no miembros, en biblioteca misionera
oficial. Requiere investigar disponibilidad digital en el sitio.

---

## Tier 2 — Manuales Oficiales de la Iglesia (authority=60)

### 5. Gospel Principles

**Estado:** `ingested` — 51 archivos EN+ES en corpus | Script: `download_manual.py --manual gospel-principles`
**Seed file:** `data/kg-seeds/gospel-principles.json` ✅

#### Fase 0 — Análisis de contenido

**Estructura:** 47 capítulos en arco secuencial: Deidad (1–3) → Existencia Preterrenal (4–6) → Espíritu Santo (7) → Ordenanzas (8–26) → Virtudes y familia (27–40) → Escatología (41–47). No alfabético — sigue la progresión doctrinal que se enseña a investigadores. ~600 palabras por capítulo + bloque de "Additional Scriptures" (8–12 refs) al final de cada uno.

**Tipo de contenido:** Prosa doctrinal narrativa con preguntas de estudio integradas (2–3 por capítulo). Mezcla definición, principio, y aplicación. Citas directas de escrituras y profetas históricos en contexto.

**Citas de escrituras:** ~6–10 inline por capítulo (todas las obras estándar, con énfasis en D&C y PGP) + bloque Additional Scriptures. Formato parentético en HTML.

**Valor KG único — cadenas causales que NER no puede inferir:**

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `IS_SAME_AS` | Jesus Christ | Jehovah | GP ch. 3; Ether 3:14 |
| `IS_SAME_AS` | Lucifer | Satan | GP ch. 3; Moses 4:3-4 |
| `FOREORDAINED_AS` | Jesus Christ | Savior | 1 Peter 1:19-20; Moses 4:2 |
| `PRECEDED_BY` | War in Heaven | Council in Heaven | GP ch. 3 (secuencia causal) |
| `PREREQUISITE_FOR` | Baptism | Exaltation | GP ch. 47 (secuencia ordenada) |
| `PREREQUISITE_FOR` | Temple Endowment | Exaltation | GP ch. 47 |
| `PREREQUISITE_FOR` | Eternal Marriage | Exaltation | GP ch. 47; D&C 131:1-4 |
| `PART_OF` | Exaltation | Celestial Kingdom (highest degree) | D&C 131:1-4 |
| `PART_OF` | Celestial/Terrestrial/Telestial | Degrees of Glory | D&C 76 |

**Entidades nuevas para gazetteer:** Council in Heaven, War in Heaven, Premortal Existence, Exaltation, Degrees of Glory, Celestial Kingdom, Terrestrial Kingdom, Telestial Kingdom, Spirit Children, Foreordination

**Estructura:** 47 capítulos organizados en 5 partes: La Deidad, El Plan de
Salvación, Los Principios del Evangelio, Los Mandamientos, Vivir el Evangelio.
Manual de clase para nuevos conversos y preparación para el templo. ~300 páginas.

**URL pattern:**
- TOC: `/study/manual/gospel-principles`
- Capítulos: `/study/manual/gospel-principles/{slug}` — slugs descriptivos,
  no numerados (e.g., `god-our-eternal-father`, `our-heavenly-family`)
- API: confirmado funciona igual que PMG
- Bilingüe: sí — "Principios del Evangelio"

**Autoridad:** 60 — manual de clase oficial, revisado más recientemente en 2009.

**KG — valor:**
- Cubre **todo** el plan de salvación en capítulos dedicados → nodos doctrinales
  completos (prexistencia, mortalidad, kingdoms of glory, temple ordinances)
- Alta densidad de citas de todos los standard works → intertextualidad
- Vocabulario doctrinal canónico en ES — fuente de términos para gazetteers
- 47 capítulos = ~47 clusters temáticos bien delimitados

**Preguntas:**
- "¿Qué enseña la Iglesia sobre los tres grados de gloria?"
- "¿Cuál es la doctrina sobre la fe, el arrepentimiento y el bautismo?"
- "¿Qué son las ordenanzas del templo según la doctrina oficial?"

**Consideración especial:** Los slugs deben mapearse manualmente desde el TOC
(no son `chapter-N`). Script necesita `fetch_toc()` robusto.

**Script:** Adaptar `download_pme.py`. ~100 archivos por idioma.

---

### 6. True to the Faith: A Gospel Reference

**Estado:** `ingested` — ~180 entradas EN+ES en corpus | Script: `download_manual.py --manual true-to-the-faith`
**Seed file:** `data/kg-seeds/true-to-the-faith.json` ✅

#### Fase 0 — Análisis de contenido

**Estructura:** 171 entradas alfabéticas (Aaronic Priesthood → Zion). Diccionario de referencia, no currículum secuencial. Cada entrada = definición inmediata + 2–4 subsecciones + bloque "See Also" con 4–6 referencias cruzadas a otras entradas. Las entradas de temas de comportamiento (Abortion, Coffee, Gambling, Tattooing) son únicas — no tienen análogos en GP.

**Tipo de contenido:** Referencia doctrinal pura, sin preguntas. Mayor densidad de citas que GP (~10–20 refs por entrada sustancial). La red See-Also crea ~850 aristas `RELATED_TO` curadas entre conceptos.

**Valor KG único vs. Gospel Principles:**
- **TTF aporta definiciones explícitas:** "Priesthood IS the eternal power and authority of God." — triples `HAS_DEFINITION` con alta confianza que NER no puede generar
- **Red See-Also:** 171 × ~5 refs = ~850 relaciones semánticas curadas entre conceptos doctrinales
- **Distinción Paradise/Spirit Prison:** TTF los trata como sub-regiones distintas del Spirit World — NER los fusionaría
- **Autoridad-clave cadena:** Jesus Christ HOLDS all keys → President of Church AUTHORIZED to use them → delegates down. Árbol formal de delegación.
- **Doctrina de compensación:** Atonement COMPENSATES_FOR all suffering and injustice (not just sin) — declaración única en TTF

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `AUTHORIZED` | Jesus Christ | All Priesthood Keys | TTF: Priesthood |
| `PART_OF` | Paradise | Spirit World | TTF: Plan of Salvation |
| `PART_OF` | Spirit Prison | Spirit World | TTF: Spirit Prison |
| `IS_SAME_AS` | Light of Christ | Conscience | TTF: Light of Christ |
| `RESTORED` | John the Baptist | Aaronic Priesthood | TTF: Aaronic Priesthood |
| `DESCRIBED_BY` | Lucifer | Agency (intento de destruir) | TTF: Plan of Salvation |

**Entidades nuevas para gazetteer:** Light of Christ, Foreordination, Paradise (spirit world), Spirit Prison, Patriarchal Blessing, Family Home Evening, Deacon/Teacher/Priest/Elder (oficios del sacerdocio)

**Estructura:** ~180 entradas alfabéticas (A–Z), como glosario doctrinal
compacto. Cada entrada = 1 página promedio con definición + referencias.
Diseñado para uso rápido, especialmente misioneros y jóvenes.

**URL pattern:**
- TOC: `/study/manual/true-to-the-faith`
- Entradas: `/study/manual/true-to-the-faith/{slug}` — slugs alfabéticos
  (e.g., `accountability`, `atonement-of-jesus-christ`, `tithing`)
- Bilingüe: sí — "Fiel a la Fe"

**Autoridad:** 60

**KG — valor:**
- Vocabulario doctrinal **oficial y conciso** → gazetteer source excelente
- Cada entrada es un concepto bien definido → nodos doctrinales limpios
- Relaciones entre conceptos (e.g., "fe" → "arrepentimiento" → "bautismo")
- Buena cobertura de términos especializados SUD: "calling", "endowment",
  "ward", "stake", "sealing" — términos que causan confusión en NER

**Consideración especial:** Entradas muy cortas (~300 palabras c/u) →
chunks pequeños, buena precisión semántica.

**Script:** Adaptar `scrape_study_aids.py` (índice → entradas individuales).
~360 archivos por idioma (EN+ES).

---

### 7. Come Follow Me (manuales anuales 2019–2026)

**Estado:** `ingested` — 8 años completos (2019–2026) EN+ES en corpus | Script: `download_manual.py --manual come-follow-me --cfm-year YYYY`
**Seed file:** `data/kg-seeds/cfm.json`

#### Fase 0 — Investigación del material

**Estructura del sitio:**
- Existen 5 versiones por año (Individuals & Families, Primary, Youth, Sunday School, Home Teaching). Se descarga solo "para el hogar y la iglesia" / "for individuals and families" — la versión principal usada por adultos.
- Cada manual cubre un ciclo del año: ~52 lecciones semanales + ~8 páginas interstitiales "Thoughts" (pensamientos adicionales al inicio, fin y puntos del año).
- Estructura: TOC → una página por unidad semanal → dentro: contexto histórico, pasajes clave, preguntas de estudio, aplicaciones.

**URL patterns — dos esquemas según año:**

| Años | Patrón de slug |
|------|---------------|
| 2019–2022 | `come-follow-me-for-individuals-and-families-{volume}-{year}` |
| 2023–2026 | `come-follow-me-for-home-and-church-{volume}-{year}` |

Volúmenes: `new-testament`, `book-of-mormon`, `doctrine-and-covenants`, `old-testament`

Ciclo completo (8 años):
- 2019 NT / 2020 LdM / 2021 D&C / 2022 AT
- 2023 NT / 2024 LdM / 2025 D&C / 2026 AT

**Autoridad:** 60

**Extracción de referencias escriturales:**
Las páginas CFM NO usan el sistema de notas al pie de la API (`footnotes: {}`). Las referencias a escrituras están embebidas directamente en el HTML como `<a class="scripture-ref">`. Requiere `extract_scripture_refs_from_html()` además de `extract_footnotes_api()`. **Implementado en `download_manual.py`.**

**KG — entidades clave:**

| Entidad | Tipo | Notas |
|---------|------|-------|
| Come, Follow Me | program | El programa de estudio como unidad |
| Come, Follow Me {año}: {volume} | work | 8 instancias (2019–2026) |
| Abrahamic Covenant | concept | Cadena del convenio, recurrente en OT/D&C |

**KG — relaciones únicas:**

| Relación | Descripción |
|----------|-------------|
| `PART_OF` (CFM year → programa) | 8 relaciones |
| `COVERS` (CFM year → standard work) | 8 relaciones |
| `PARALLEL_ACCOUNT_OF` (OT → NT, OT → LdM) | Tipología cristológica del AT explícita |
| `IS_SAME_AS` (Jesus Christ ↔ Jehovah) | CFM 2026 lección 01, confirmado por Pres. Oaks |
| `RESTORED` (Abrahamic Covenant ← Joseph Smith) | "The Covenant" (Thoughts 2026) |

**Páginas "Thoughts" — alta densidad doctrinal:**
- ~8 por año = ~64 páginas totales (ciclo completo)
- Densidad doctrinal 3–5× mayor que las lecciones semanales
- Contienen: análisis tipológicos explícitos (OT↔NT↔LdM), cadenas del Convenio Abrahámico, citas de GAs con fuente, relaciones de Armonía por año
- Ejemplos de 2026: "The Covenant", "The Passover and the Lamb", "Prophets and Prophecy"

**Consideraciones especiales:**
- 8 años × ~60 docs × 2 idiomas = ~960 archivos en total
- El ciclo 2023–2026 es el actualmente en uso — priorizar descargas en ese orden
- La branding cambió en 2023 (nuevos slugs) pero el contenido es equivalente
- No descargar variantes (Primary, Youth) a menos que se decida ampliar cobertura

---

### 8. Teachings of Presidents of the Church (serie)

**Estado:** `ingested` — 17 volúmenes completos (~560 capítulos) EN+ES en corpus | Script: `download_manual.py --manual teachings-{nombre}` o `--all-prophets`
**Seed file:** `data/kg-seeds/teachings-of-presidents.json` ✅

#### Fase 0 — Investigación del material

**17 volúmenes** (1997–2025), usados como curriculum de quórumes de Élderes y Sociedad de Socorro. Cada manual: citas directas del profeta organizadas temáticamente.

**Tabla de volúmenes y slugs confirmados:**

| # | Profeta | Capítulos | Slug |
|---|---------|-----------|------|
| 1 | Brigham Young | 48 | `teachings-brigham-young` |
| 2 | Joseph F. Smith | 48 | `teachings-joseph-f-smith` |
| 3 | Harold B. Lee | 24 | `teachings-harold-b-lee` |
| 4 | John Taylor | 24 | `teachings-john-taylor` |
| 5 | Heber J. Grant | 24 | `teachings-heber-j-grant` |
| 6 | David O. McKay | 24 | `teachings-david-o-mckay` |
| 7 | Wilford Woodruff | 24 | `teachings-wilford-woodruff` |
| 8 | Spencer W. Kimball | 24 | `teachings-spencer-w-kimball` |
| 9 | Joseph Smith | 47 | `teachings-joseph-smith` |
| 10 | George Albert Smith | 24 | `teachings-george-albert-smith` |
| 11 | Lorenzo Snow | 24 | `teachings-of-presidents-of-the-church-lorenzo-snow` |
| 12 | Joseph Fielding Smith | 26 | `teachings-of-presidents-of-the-church-joseph-fielding-smith` |
| 13 | Ezra Taft Benson | 24 | `teachings-of-presidents-of-the-church-ezra-taft-benson` |
| 14 | Howard W. Hunter | 24 | `teachings-of-presidents-of-the-church-howard-w-hunter` |
| 15 | Gordon B. Hinckley | 25 | `teachings-of-presidents-of-the-church-gordon-b-hinckley` |
| 16 | Thomas S. Monson | 24 | `teachings-of-presidents-of-the-church-thomas-s-monson` |
| 17 | Russell M. Nelson | ~24 | `teachings-of-presidents-of-the-church-russell-m-nelson` |

**Patrón de slugs:** Los primeros 10 volúmenes (1997–2007) usan `teachings-{nombre}`; los 7 posteriores (2011–2025) usan `teachings-of-presidents-of-the-church-{nombre}`. Todos ya están mapeados en `download_manual.py`.

**Total estimado:** ~430 capítulos × 2 idiomas = ~860 archivos.

**Estructura interna de cada capítulo:**
1. Enunciado temático breve
2. "From the Life of [Profeta]" — viñeta biográfica (narrativa editorial)
3. "Teachings of [Profeta]" — citas directas organizadas bajo sub-temas
4. "Suggestions for Study and Teaching" — preguntas + "Related Scriptures" (lista curada)

**Extracción de referencias:** Las referencias escriturales aparecen como `<a class="scripture-ref">` inline (mismo patrón que CFM) + sección "Related Scriptures" al final de cada capítulo. Ambas fuentes deben extraerse. El script ya tiene la extracción inline implementada.

**Autoridad:** 60 (manuales oficiales) — las citas del profeta mismo son de mayor credibilidad que el texto editorial.

**⚠️ Consideración de confianza — Joseph Smith:**
El apéndice del volumen de Joseph Smith documenta que algunas citas: (a) fueron convertidas de tercera a primera persona, (b) combinan múltiples fuentes parciales, (c) tienen ortografía corregida. Nivel de confianza para el KG: `metadata`, no `curated`.

**KG — valor único de la serie:**

| Relación | Descripción | Densidad |
|----------|-------------|----------|
| `TAUGHT` (profeta → doctrina) | ~430 capítulos temáticos con atribución directa | Muy alta |
| `TESTIFIED_OF` (profeta → Joseph Smith) | Cada volumen tiene 1 capítulo explícito sobre JS | 16 relaciones curadas |
| `SUCCEEDED` (BY → JS → JT → ...) | Cadena de sucesión completa | 16 relaciones |
| `WITNESSED` (Taylor → Martyrdom) | John Taylor fue herido en Carthage Jail | Curado |
| `ISSUED_MANIFESTO` (Woodruff → OD1) | Cap. 19 "Following the Living Prophet" | Curado |
| `RECORDED_ON` | Woodruff: entradas de diario con fechas exactas | Alta para Woodruff |
| `INTERPRETS` (teaching → scripture) | "Related Scriptures" por capítulo — puente curado | ~430 listas |

**Temas recurrentes entre profetas (cross-temporal):**
Fe, expiación, familia, templos, misiones — aparecen en los 17 volúmenes → habilita `TAUGHT_BY_MULTIPLE_PROPHETS` como relación de agregación.

**Prioridad de seed files:**
1. Joseph Smith — mayor densidad de entidades de la Restauración
2. Wilford Woodruff — `ISSUED_MANIFESTO` + fechas de diario
3. John Taylor — `WITNESSED` (martyrdom) + `SUCCEEDED`

---

### 9. Institute Manuals (CES)

**Estado:** `ingested` — 8 cursos con ~340 archivos EN+ES en corpus | Script: `download_manual.py --manual {key}`

**Serie:** Old Testament, New Testament, Book of Mormon, Doctrine & Covenants,
Church History — cada uno ~40 lecciones densas. Son la base del estudio
académico del evangelio en el instituto de religión.

**Investigar:** URL patterns en el sitio (probablemente `/study/manual/book-of-mormon-seminary`
o similar). Los de Instituto son distintos a los de Seminario.

**KG valor:** Muy alto — son comentarios académicos con referencias cruzadas
extensas entre todos los standard works.

---

### 10. Our Heritage: A Brief History of The Church

**Estado:** `ingested` — 11 capítulos EN+ES en corpus | Script: `download_manual.py --manual our-heritage`
**Seed file:** `data/kg-seeds/our-heritage.json` ✅

#### Fase 0 — Análisis de contenido

**Estructura:** 11 capítulos + Introduction + Conclusion. Cronológico: ch. 1 = Primera Visión (1820) → ch. 11 = Iglesia actual. ~50–80 párrafos por capítulo. Publicado 1996. URL confirmado: `/manual/our-heritage` (no "our-heritage-a-brief-history").

**Tipo de contenido:** Prosa histórica narrativa. Cita diarios, cartas y discursos. Lectura accesible. Menciona figuras históricas con contexto de evento y lugar. Densidad de citas escriturales: baja (2–5 por capítulo) — usado para establecer autoridad doctrinal, no como comentario bíblico.

**Personas clave:** Joseph Smith, Lucy Mack Smith, Brigham Young, Heber C. Kimball, Eliza R. Snow, Oliver Cowdery, Martin Harris, Newel K. Whitney, Orson Pratt, Orson Hyde, todos los profetas sucesores hasta Gordon B. Hinckley, Governor Lilburn Boggs.

**Lugares históricos:** Liberty Jail, Carthage Jail, Winter Quarters, Haun's Mill, Kirtland (templo), Nauvoo (templo), Salt Lake City.

**Valor KG único — espina dorsal institucional:**
- **Sucesión profética:** Joseph Smith → Brigham Young → … → Gordon B. Hinckley — cadena `SUCCESSOR_OF` explícita
- **Templos fundacionales:** cuándo y dónde se construyó cada uno → `dedicated_by` + `year`
- **Eventos fechados:** Martyrdom (1844), Pioneer Entry (1847), OD1 (1890), Dedication of Salt Lake Temple (1893)
- **Fundación de organizaciones:** Joseph Smith founded Relief Society, Sunday School, YLMIA, Priesthood quorums

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `MARTYRED_AT` | Joseph Smith | Carthage Jail | Our Heritage ch. 5 |
| `SUCCESSOR_OF` | Brigham Young | Joseph Smith | Our Heritage ch. 6 |
| `LED` | Brigham Young | Pioneer Trek | Our Heritage ch. 6 |
| `FOUNDED` | Joseph Smith | Relief Society | Our Heritage ch. 5 (1842) |
| `AUTHORIZED` | Wilford Woodruff | Official Declaration 1 | Our Heritage ch. 8 |

**Entidades nuevas:** Lucy Mack Smith, Martin Harris, Heber C. Kimball, Eliza R. Snow, Newel K. Whitney, Orson Pratt, Orson Hyde, Lilburn Boggs, Liberty Jail, Carthage Jail, Winter Quarters, Haun's Mill, Pioneer Trek (event), Extermination Order (event), Nauvoo Period (period), Pioneer Period (period)

**Estructura:** ~10 capítulos de historia de la Iglesia desde 1820 hasta el
siglo XX. Narrativa oficial, concisa. Usado en clases de historia de la Iglesia.

**URL:** `/study/manual/our-heritage-a-brief-history-of-the-church`
**Bilingüe:** sí — "Nuestra herencia"
**Autoridad:** 60

**KG valor:** Crea línea de tiempo de personas, lugares y períodos históricos —
útil para el eje temporal del grafo.

**Script:** `download_pme.py` adaptado. ~15 archivos por idioma.

---

### 11. Saints: The Story of the Church — Volumes 1–4

**Estado:** `ingested` — 214 capítulos EN+ES (v1: 59, v2: 55, v3: 50, v4: 50) | Script: `download_manual.py --manual saints-v{1-4}`

**Descripción:** Historia narrativa oficial de la Iglesia (2018–2024),
~400 páginas por volumen. Altamente citada en conferencia reciente.
Es la historia institucional más moderna y completa.

**URL pattern:** `/study/history/saints-v{1-4}` (uri_prefix=/history, no /manual) — confirmado en download_manual.py.

---

### 12. For the Strength of Youth

**Estado:** `ingested` — EN+ES en corpus | Script: `download_manual.py --manual for-the-strength-of-youth`
**Seed file:** — (cubierto por `_enrich_kg_from_meta`; NER captura las entidades doctrinales)

#### Fase 0 — Análisis de contenido

**Estructura:** 14 páginas (12 capítulos doctrinales + Apéndice + Índice). Edición 2022–2026. Cada capítulo = "Eternal Truths" (2–4 principios) + "Invitations" (conducta) + "Promised Blessings" + Q&A + pregunta de entrevista para el templo.

**Tipo de contenido:** Doctrinal-pastoral dirigido a jóvenes (12–18 años). Sin citas de profetas por nombre — prosa directa de la Iglesia. Las preguntas Q&A abordan temas sensibles: atracción del mismo sexo, abuso, normas de vestimenta.

**Personas mencionadas:** Heavenly Father, Jesus Christ, Holy Ghost — ninguna figura histórica por nombre.

**Mecánica de citas:** Inline en HTML, formato parentético. Moderada densidad (5–10 por capítulo). Escrituras de todos los standard works.

**Valor KG único:**
- `Body → IS_TEMPLE_OF → Holy Ghost` (1 Cor 6:18-20) — relación Body-Spirit explícita
- `Body and Spirit → CONSTITUTE → Soul` (D&C 88:15) — definición de alma
- `Covenant Path → LEADS_TO → Eternal Life` — nombre oficial del camino
- `Law of Chastity → PERMITS_SEXUAL_EXPRESSION_WITHIN → Eternal Marriage` — límite doctrinal
- Q&A sobre same-sex attraction crea relación `same-sex attraction → IS_NOT → Sin` (declaración oficial 2022)

**Entidades nuevas:** Covenant Path, Law of Chastity, Temple Recommend, Plan of Happiness (alias de Plan of Salvation), Word of Wisdom (si no está ya)

**Descripción:** Estándares para jóvenes. La edición 2022 es un cambio
importante de enfoque — menos reglas, más principios. Relativamente corto.

**URL:** `/study/manual/for-the-strength-of-youth`
**Bilingüe:** sí
**Autoridad:** 60

**KG valor:** Bajo para KG, pero captura vocabulario normativo de la Iglesia
y principios morales. Útil para preguntas sobre estándares.

**Script:** `download_pme.py`. ~10 archivos.

---

## Tier 3 — Fuentes Históricas (authority=30–40)

### 13. Discourses of Brigham Young

**Estado:** `ingested` — 42 capítulos EN en `corpus/en/books/discourses-brigham-young/` (Gutenberg)

**Descripción:** Compilación de ~600 páginas de discursos de Brigham Young
organizados temáticamente (por John A. Widtsoe, 1925). Dominio público.
Muy citado en materiales de la Iglesia.

**Fuente:** No en el sitio oficial — disponible en Project Gutenberg y
archive.org. Requiere script distinto (no API de la Iglesia).

**Autoridad:** 35 — discursos de profeta (alta autoridad), compilación
editada de fuentes históricas (reduce rigor).

**KG valor:**
- Brigham Young es el 2do profeta más influyente → enriquece su perfil
- Temas: colonización del Oeste, economía del reino, relaciones familiares,
  teología cosmológica (adam-god theory — importante manejar con cuidado)

**Consideración especial:** Algunas enseñanzas de BY son controvertidas y
han sido matizadas/retractadas por líderes posteriores. El `authority_model`
debe reflejar esto (alta autoridad histórica, rigor doctrinal medio-bajo).

**Script:** Requiere nuevo script para Project Gutenberg / archive.org.

---

### 14. Teachings of the Prophet Joseph Smith

**Estado:** `backlog`

**Descripción:** Compilación de Joseph Fielding Smith de enseñanzas de JS.
Parte en dominio público. Alta densidad de doctrina profunda (King Follett,
Nauvoo Discourses). Posiblemente en el sitio oficial.

**Investigar:** URL en sitio oficial vs dominio público.

---

### 15. Doctrines of Salvation — Joseph Fielding Smith (3 vols)

**Estado:** `backlog`

**Descripción:** Compilación teológica sistemática de JFS, uno de los
teólogos más influyentes del siglo XX de la Iglesia. Muy citado en
conferencia de esa era. Dominio público (1954–1956).

**Investigar:** Disponibilidad digital. No parece estar en el sitio oficial.

---

### 16. Journal of Discourses (26 volúmenes)

**Estado:** `backlog`

**Descripción:** 26 volúmenes de discursos de profetas y apóstoles 1854–1886.
Dominio público. Fuente histórica primaria. La Iglesia ha aclarado que no
son doctrina oficial — pero son amplamente citados.

**Consideración especial:** Alta complejidad de ingestión (26 vols, miles
de discursos). Requiere procesamiento cuidadoso de autoridad y notas de
contexto histórico.

**Script:** Requiere investigación de fuentes (archive.org, BYU collections).

---

## Tier 2b — Descubiertos en survey del sitio (2026-04)

> Materiales confirmados en el sitio oficial durante el inventario completo.
> No estaban en el backlog previo.

### Gospel Topics Essays

**Estado:** `ingested` — 15 ensayos EN+ES en corpus | Script: `download_manual.py --manual gospel-topics-essays`
**Seed file:** `data/kg-seeds/gospel-topics-essays.json` ✅

**URL:** `/study/manual/gospel-topics-essays` | **Bilingüe:** sí
**Autoridad:** 70 — essays aprobados por la Primera Presidencia; los únicos
documentos donde la Iglesia aborda temas histórico-doctrinales sensibles de forma oficial.

#### Fase 0 — Análisis de contenido

**Estructura:** 15 ensayos sobre temas histórico-doctrinales específicos: poligamia (4 sub-ensayos), raza y sacerdocio, traducción del LdM, Primera Visión, ADN y Lamanitas, Libro de Abraham, sacerdocio y mujeres, Masones y el templo, Becoming Like God, Heavenly Mother, Mountain Meadows Massacre. Cada ensayo tiene 800–3,500 palabras con 25+ citas a fuentes primarias y académicas en footnotes numerados — el material más densamente citado del corpus.

**Tipo de contenido:** Ensayos histórico-explicativos. Mezclan narrativa histórica, argumentación doctrinal, y contexto académico. Cada uno responde preguntas que miembros enfrentan en Internet. La Iglesia disavows explícitamente teorías raciales (Curse of Cain) y acknowledges incertidumbres históricas.

**Mecánica de citas:** Refs inline en HTML + footnotes numerados en JSON. Los footnotes citan Joseph Smith Papers, Diarios de apóstoles, artículos académicos (BYU Studies, Journal of Mormon History), documentos legales históricos.

**Personas clave:**

| Persona | Rol en los ensayos |
|---------|-------------------|
| Joseph Smith | Autor/receptor de revelación sobre matrimonio plural y restricción racial (ausente en su era) |
| Brigham Young | Anunció públicamente la restricción sacerdotal en 1852 |
| Wilford Woodruff | Emitió el Manifiesto 1890 (OD1) — fin de la práctica de matrimonio plural |
| Spencer W. Kimball | Recibió la revelación de 1978 (OD2) — fin de la restricción sacerdotal |
| Emma Smith | Opositora conocida al matrimonio plural; primera presidenta de RS |
| Elijah Abel | Hombre negro ordenado bajo Joseph Smith — excepción a la restricción posterior |
| Jane Manning James | Pionera negra; acceso limitado al templo |
| Bruce R. McConkie | Apóstol que revisó públicamente su teología racial post-1978 |
| Reed Smoot | Senador/apóstol cuyas audiencias precipitaron reformas al matrimonio plural (1904) |

**Valor KG único — relaciones que NER no puede inferir:**

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `AUTHORIZED` | Joseph Smith | Plural Marriage | D&C 132; GTE Plural Marriage |
| `REVOKED` | Wilford Woodruff | Plural Marriage (práctica) | Official Declaration 1 |
| `REVOKED` | Spencer W. Kimball | Priesthood Restriction | Official Declaration 2 |
| `AUTHORIZED` | Brigham Young | Priesthood Restriction | 1852 public announcement |
| `DISAVOWED` | Curse of Cain | The Church (organización) | Race and the Priesthood essay |
| `DISAVOWED` | Curse of Ham | The Church (organización) | Race and the Priesthood essay |
| `ADDRESSED_BY` | Official Declaration 2 | Priesthood Restriction | Race essay |
| `PRECEDED_BY` | Official Declaration 2 | Official Declaration 1 | Canon D&C |
| `ADDRESSED_BY` | D&C 132 | Plural Marriage | GTE Plural Marriage essay |

**Entidades nuevas para gazetteer:** Plural Marriage, Priesthood Restriction, Curse of Cain, Elijah Abel, Jane Manning James, Q. Walker Lewis, Reed Smoot, Bruce R. McConkie, Official Declaration 1, Official Declaration 2, São Paulo Temple

---

### First Vision Accounts

**Estado:** `ingested` — 9 documentos EN+ES en corpus | Script: `download_manual.py --manual first-vision-accounts`
**Seed file:** `data/kg-seeds/first-vision-accounts.json` ✅

**URL:** `/study/manual/first-vision-accounts` | **Bilingüe:** sí
**Autoridad:** 75 — documentos primarios del evento fundacional más importante de la Restauración.

#### Fase 0 — Análisis de contenido

**Estructura:** 9 documentos totales: 4 relatos de primera mano de Joseph Smith (1832, 1835, 1838, 1842) + 5 relatos de contemporáneos que escucharon a JS hablar del evento. El relato de 1838 está canonizado como JS-H 1:5-20 en PGP — ya en el corpus. Los relatos 1832, 1835 y 1842, y los 5 contemporáneos, **NO están** en el corpus sin este material.

**Tipo de contenido:** Documentos primarios transcritos + análisis histórico de contexto (año, audiencia, propósito del relato). No es exégesis — son los textos originales anotados.

**Diferencias clave entre relatos:**

| Detalle | 1832 | 1835 | 1838 (oficial) | 1842 |
|---------|------|------|----------------|------|
| Personajes vistos | El Señor (1) | 2 personajes + ángeles | Padre + Hijo (2) | 2 personajes idénticos |
| Tema central | Perdón de pecados | Perdón + curiosidad teológica | "No te unas a ninguna iglesia" | Misma orden |
| Audiencia | Papeles privados | Diario personal | Historia oficial de la Iglesia | Carta pública (periódico) |
| Escritura que motivó | Sal 14:1 (aludido) | Santiago 1:5 | Santiago 1:5 | Santiago 1:5 |

La diferencia 1 vs 2 personajes es teológicamente significativa y KG-expresable como tensión entre relatos.

**Personas clave:** Joseph Smith (autor de los 4 relatos), Heavenly Father, Jesus Christ (como personajes de la visión)

**Valor KG único — relaciones que NER no puede inferir:**

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `PARALLEL_ACCOUNT_OF` | 1832 account | First Vision (event) | FVA manual |
| `PARALLEL_ACCOUNT_OF` | 1835 account | First Vision (event) | FVA manual |
| `PARALLEL_ACCOUNT_OF` | 1838 account | First Vision (event) | JS-H 1:5-20 |
| `PARALLEL_ACCOUNT_OF` | 1842 account | First Vision (event) | Wentworth Letter |
| `CANONIZED_AS` | 1838 First Vision Account | Joseph Smith—History 1:5-20 | Pearl of Great Price |
| `EARLIER_VERSION_OF` | 1832 account | 1838 account | FVA manual |
| `PART_OF` | 1842 account | Wentworth Letter | Times and Seasons, 1842 |
| `DESCRIBED_IN` | First Vision | Sacred Grove | JS-H 1:14 |
| `DESCRIBED_BY` | First Vision | James 1:5 | JS-H 1:11 — la escritura que motivó la oración |

**Consideración especial:** La divergencia 1 vs. 2 personajes es uno de los temas más consultados en apologética mormona. El KG debe poder responder "¿Cuántas personajes vio Joseph Smith?" con el contexto de que los relatos varían — **esto NO se puede inferir de NER, requiere el seed file y los metadatos del manual**.

**Entidades nuevas para gazetteer:** 1832/1835/1838/1842 First Vision Account (documentos), Wentworth Letter, Spring of 1820 (período)

---

### Seminary Student Manuals (ciclo actual)

**Estado:** `ingested` — 5 manuales con ~1,014 archivos EN en corpus | Script: `download_manual.py --manual {key}`

**Serie disponible:**
| Manual | Slug | Año | Tamaño estimado |
|--------|------|-----|----------------|
| OT Seminary Student Manual | `old-testament-seminary-student-manual-2026` | 2026 | ~140 lecciones |
| BoM Seminary Student Manual | `book-of-mormon-seminary-student-manual-2024` | 2024 | ~160 lecciones |
| NT Seminary Student Manual | `new-testament-seminary-student-manual-2023` | 2023 | ~180 lecciones |
| D&C Seminary Teacher Manual | `doctrine-and-covenants-seminary-teacher-manual-2025` | 2025 | ~160 lecciones |
| Doctrinal Mastery Core Document | `doctrinal-mastery-core-document-2023` | 2023 | ~20 páginas |

**ℹ️ D&C Seminary student manual 2025 es PDF-only** — nunca se publicó como web manual. Solo existe el manual del maestro en web (`doctrine-and-covenants-seminary-teacher-manual-2025`). Los PDFs del estudiante están en: `content-preview.churchofjesuschrist.org/si/bc/si/seminary/pdf/Seminary-Student-Manual-2025/`. Se usa el teacher manual como fallback web; los PDFs requieren descarga manual separada.

**Autoridad:** 60 | **Bilingüe:** sí

**Formato:** Los manuales de seminario son orientados a actividades (A/B options), con secciones "Doctrinal Mastery" marcadas y puntos "Assess Your Learning" cada ~50 lecciones. Audiencia: secundaria (14–18 años). Diferente al formato de Instituto (reflexión universitaria).

#### Fase 0 — OT Seminary Student Manual (2026)

**Estructura:** ~140 lecciones, orden canónico AT + PGP intercalado (Moses 1-7 y Abraham 1-5 woven in en posición Genesis). Incluye 5 lecciones Doctrinal Mastery Practice + 4 Assess Your Learning.

**Valor KG único:**
- `Jehovah → IS_SAME_AS → Jesus Christ`: el manual más sistemático en afirmar esta identidad en cada lección AT donde aparece "LORD"
- PGP-Genesis parallel structure: `Moses 4 → PARALLEL_TO → Genesis 3`; `Abraham 3 → expands → Genesis 1 (premortal)`
- Tipología cristológica densa: Passover Lamb, Isaac, Brazen Serpent, Tabernacle — todos como tipos de Cristo
- Sistema Doctrinal Mastery OT: ~25 pasajes AT designados como alta prioridad → `DESIGNATED_AS high-priority` en KG
- `Enoch → built → City of Zion → translated_to → Heaven` (Moses 7) — nodo único

**KG — relaciones clave:**

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `IS_SAME_AS` | Jehovah | Jesus Christ | OT Sem L1 (Oaks confirmado) |
| `PARALLEL_ACCOUNT_OF` | Moses 4 | Genesis 3 | OT Sem (PGP restoration) |
| `TYPIFIES` | Passover Lamb | Jesus Christ | OT Sem Exodus lessons |
| `TYPIFIES` | Isaac | Jesus Christ | OT Sem Genesis 22 |
| `TYPIFIES` | Brazen Serpent | Jesus Christ | OT Sem Numbers 21 |
| `TYPIFIES` | Tabernacle of Moses | Temple | OT Sem Exodus lessons |
| `DESIGNATED_AS` | Abraham 3:22-23 | Doctrinal Mastery | OT Sem DM passages |

**Entidades nuevas para gazetteer:** Tabernacle of Moses, City of Zion (Enoch's), Brazen Serpent, Deborah (judge), Ruth (person), Rahab, Michael T. Ringwood

#### Fase 0 — NT Seminary Student Manual (2023)

**Estructura:** ~180 lecciones, orden canónico NT. Joseph Smith—Matthew 1 tratado como texto NT. Incluye 3 mini-series "Acquiring Spiritual Knowledge" (partes dispersas). ~25 pasajes Doctrinal Mastery NT.

**Valor KG único:**
- **Genealogía de Mateo 1**: análisis de las 5 mujeres nombradas (Tamar, Rahab, Ruth, Bathsheba, María) → relaciones de genealogía raramente en KG
- **Discurso de Despedida** (Juan 13-17): 3+ lecciones separadas — `Holy Ghost → IS_CALLED → Comforter`; vid y pámpanos como doctrina nombrada
- **Matrimonio (Mateo 19)**: cruza con Proclamación de la Familia y D&C 131:1-4 → bridge NT↔D&C
- Doctrinal Mastery NT: Mt 5:14-16; 11:28-30; 16:15-19; 22:36-39; Jn 3:5; 3:16; 7:17; 14:15; Lc 2:10-12; 22:19-20 — nodos de alta confianza

**KG — relaciones clave:**

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `IS` | Jesus Christ | Promised Messiah | NT Sem Mt 1; Is 7:14; 53 |
| `RECEIVED` | Peter | Keys of the Kingdom | NT Sem Mt 16:18-19 (DM) |
| `TITLED` | Holy Ghost | Comforter | NT Sem Jn 14:16-17 |
| `INSTITUTED_BY` | Sacrament | Jesus Christ | NT Sem Mt 26:26-30 (DM) |
| `IS_TITLED` | JST Matthew 24 | Joseph Smith—Matthew 1 | NT Sem PGP text |

**Entidades nuevas:** Tamar (OT), Bathsheba, Lazarus, Keys of the Kingdom (concept), Farewell Discourse (text unit), Comforter (Holy Ghost title)

---

### Institute Scripture Course Manuals

**Estado:** `ingested` — 8 cursos EN+ES en corpus (ver tabla de Cornerstone abajo también) | Script: `download_manual.py --manual {key}`

**Serie disponible:**
| Manual | Slug |
|--------|------|
| OT Institute Teacher Manual | `old-testament-institute-teacher-manual-2026` |
| NT Institute Teacher Manual | `new-testament-institute-teacher-manual-2024` |
| Book of Mormon Teacher Manual | `book-of-mormon-teacher-manual` |
| Book of Mormon Student Manual | `book-of-mormon-student-manual` |
| D&C Teacher Manual | `doctrine-and-covenants-teacher-manual-2017` |
| D&C Student Manual | `doctrine-and-covenants-student-manual-2017` |
| PGP Teacher Manual | `the-pearl-of-great-price-teacher-manual-2018` |
| PGP Student Manual | `the-pearl-of-great-price-student-manual-2018` |

**Autoridad:** 60 | **Bilingüe:** sí

**KG valor:** Comentario académico de nivel universitario sobre cada volumen.
Los student manuals son especialmente densos en referencias cruzadas y
citas de profetas. Priorizar BoM y D&C por complementar el corpus existente.

---

### Institute Cornerstone Courses

**Estado:** `ingested` — 4 cursos EN+ES en corpus | Script: `download_manual.py --manual {key}`

**Serie:**
| Manual | Slug | Lecciones |
|--------|------|-----------|
| Eternal Family | `the-eternal-family-class-prep-material-2022` | 28 |
| Foundations of the Restoration | `foundations-of-the-restoration-class-preparation-material-2019` | ~30 |
| Jesus Christ and His Everlasting Gospel | `jesus-christ-and-his-everlasting-gospel-class-prep-material-2023` | ~30 |
| Teachings and Doctrine of the BoM | `teachings-and-doctrine-of-the-book-of-mormon-class-prep-material-2021` | 28 |

**Autoridad:** 60 | **Bilingüe:** sí | **Formato:** Class Preparation Material (CPM) — ensayo reflexivo, citas de AA, sin actividades A/B. Audiencia universitaria.

#### Fase 0 — The Eternal Family (Religion 200, 2022)

**Estructura:** 28 lecciones, sin unidades formales. Tres bloques naturales: doctrina fundamental (L1-5), matrimonio eterno (L6-17), crianza y desafíos (L18-28).

**Valor KG único — mayor que cualquier otro manual para doctrina de matrimonio:**
- `Eternal Marriage → REQUIRED_FOR → Exaltation in Celestial Kingdom` (D&C 131:1-4) — afirmación más directa en el corpus
- `Elijah → RESTORED → Sealing Authority` → `Sealing Authority → BINDS → Eternal Family Unit` (D&C 110:13-16) — dos relaciones como tesis de lección completa
- `Gender → IS → Eternal Characteristic` (pre-mortal, mortal, post-mortal) — nodo doctrinal único
- **Heavenly Mother**: mencionada explícitamente (L3 "Mother in Heaven") — uno de pocos manuales oficiales con referencia directa
- `Triangle Model (Bednar)`: Cristo en el ápex del triángulo matrimonial — doctrina pedagógica nombrada
- Cadena de 3 convenios: `Malachi 4:5-6 → Elijah → D&C 110 → Temple Sealing → Abraham 2:6-11 → Eternal Posterity`

**KG — relaciones clave:**

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `REQUIRED_FOR` | Eternal Marriage | Exaltation | Eternal Family L6; D&C 131:1-4 |
| `RESTORED` | Elijah | Sealing Authority | Eternal Family L12; D&C 110:13-16 |
| `RECEIVED_KEYS_FROM` | Joseph Smith | Elijah | Eternal Family — Kirtland Temple 1836 |
| `BINDS` | Sealing Authority | Eternal Family Unit | Eternal Family L12 |
| `IS` | Gender | Eternal Characteristic | Eternal Family L3; Family Proclamation |
| `PROMISES` | Abrahamic Covenant | Eternal Posterity | Eternal Family L15; Abraham 2:6-11 |

**Entidades nuevas:** Heavenly Mother (person/deity), New and Everlasting Covenant of Marriage (concept), Holy Spirit of Promise (concept), Family Proclamation 1995 (document), Sealing Authority (concept distinct from general priesthood), Spirit of Elijah (concept — genealogical impulse doctrine, Elder Bednar), Jean B. Bingham, Julie B. Beck

#### Fase 0 — Teachings and Doctrine of the Book of Mormon (Religion 275, 2021)

**Estructura:** 28 lecciones en 8 unidades temáticas (no sigue orden canónico del LdM):
1. Power of the Word (L1-4) · 2. Plan of Redemption (L5-8) · 3. Doctrine of Christ (L9-12) · 4. Gathering of Israel (L13-14) · 5. Ministry of Christ (L15-18) · 6. Spiritual Dangers (L19-22) · 7. Trust in God (L23-24) · 8. Come unto Christ (L25-28)

**Valor KG único:**
- `Jacob 5 Olive Tree Allegory → REPRESENTS → Scattering and Gathering of Israel` — relación central de la Unidad 4; la más explícita del corpus
- `Doctrine of Christ → CONSISTS_OF → Faith, Repentance, Baptism, Holy Ghost, Endure to End` — 5 partes como relación ordenada (2 Nephi 31; 3 Nephi 11)
- `Book of Mormon → RESTORES → Plain and Precious Truths` (1 Nephi 13:29-33) — tesis organizadora de la Unidad 1
- Ciclo de orgullo Nefita: `Prosperidad → Pride → Destrucción → Humildad → Prosperidad` — patrón temporal nombrado
- Cadena de autoría: `Lehi → taught → Jacob → taught (via 2 Nephi 2) → Doctrine of the Fall`

**KG — relaciones clave:**

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `IS` | Book of Mormon | Keystone of Our Religion | T&D BoM L1; Joseph Smith |
| `TAUGHT` | Lehi | Doctrine of the Fall | T&D BoM L5; 2 Nephi 2 |
| `REPRESENTS` | Jacob 5 Olive Tree | Scattering and Gathering of Israel | T&D BoM L13 |
| `RESTORES` | Book of Mormon | Plain and Precious Truths | T&D BoM L1; 1 Ne 13:29-33 |
| `CONSISTS_OF` | Doctrine of Christ | Faith/Repentance/Baptism/HG/Endure | T&D BoM L9; 2 Ne 31 |
| `EXEMPLIFIED_IN` | Nephite Pride Cycle | 3 Nephi 6-7; Helaman 12 | T&D BoM L19 |

**Entidades nuevas:** Doctrine of Christ (concept), Nephite Pride Cycle (concept — named pattern), Plain and Precious Truths (concept), Jacob 5 Olive Tree Allegory (text/concept), Bruce C. Hafen (person — Elder Emeritus), Peter M. Johnson (Elder)

---

### Saints: Story of the Church (Vols. 1–4)

**Estado:** `ingested` — 214 capítulos EN+ES (v1: 59, v2: 55, v3: 50, v4: 50) | Script: `download_manual.py --manual saints-v{1-4}`
**Seed file:** `data/kg-seeds/saints.json` ✅

#### Fase 0 — Investigación del material

**4 volúmenes** (2018–2024), historia narrativa oficial con 500+ fuentes primarias por volumen. Nivel literario "novela narrativa" pero 100% documentado.

| Vol. | Título | Período | Partes | Capítulos | Páginas |
|------|--------|---------|--------|-----------|---------|
| 1 | The Standard of Truth | 1815–1846 | 4 | 46 | ~699 |
| 2 | No Unhallowed Hand | 1846–1893 | 4 | 44 | ~833 |
| 3 | Boldly, Nobly, and Independent | 1893–1955 | 4 | 39 | ~757 |
| 4 | Sounded in Every Ear | 1955–2020 | 4 | 39 | ~831 |

**Total estimado:** 167 capítulos × 2 idiomas = ~334 archivos.

**Autoridad:** 65 | **Bilingüe:** sí (14 idiomas disponibles)

**Tipo de contenido:** Narrativa con ~20-30 notas al pie por capítulo. Citas de diarios y cartas word-for-word. Aborda temas difíciles (poligamia, raza, Mountain Meadows) — diferencia clave vs. Our Heritage.

**⚠️ URL patterns — Vol. 1 distinto al resto:**

| Volumen | Patrón |
|---------|--------|
| Vol. 1 | `/history/saints-v1/{NN}-{slug}` (sin parte) |
| Vols. 2-4 | `/history/saints-v{N}/part-{P}/{NN}-{slug}` (con parte) |

El `download_manual.py` ya usa `uri_prefix="/history"` y sigue los links del TOC, por lo que maneja ambos patrones automáticamente si el TOC incluye las URLs completas. Verificar en dry-run antes de descarga completa.

**KG — relaciones únicas con precisión temporal:**

| Relación | Ejemplo | Fuente |
|----------|---------|--------|
| `SUCCEEDED` | Brigham Young → Joseph Smith (1844) | Vol. 1 |
| `EXPELLED_FROM` | Saints → Missouri (1838, Extermination Order) | Vol. 1 |
| `DEDICATED_BY` | Kirtland Temple → Joseph Smith (Mar 27 1836) | Vol. 1 |
| `DEDICATED_BY` | Salt Lake Temple → Wilford Woodruff (Apr 6 1893) | Vol. 2 |
| `ISSUED_ON` | Missouri Extermination Order → Oct 27 1838 | Vol. 1 |
| `MARTYRED_AT` | Joseph Smith → Carthage Jail (Jun 27 1844) | Vol. 1 |
| `ISSUED_MANIFESTO` | Wilford Woodruff → OD1 (Sep 25 1890) | Vol. 2 |
| `RECEIVED_REVELATION` | Spencer W. Kimball → OD2 (Jun 1978) | Vol. 4 |
| `MIGRATED_FROM` | Saints → Nauvoo → Salt Lake Valley (1846-47) | Vol. 2 |

**Ventaja vs. Our Heritage:** 23× más largo, con fechas exactas en todas las relaciones, cobertura de mujeres e internacionales (Emmeline Wells, Jane Manning James, Jonathan Napela), y fuente primaria citada en cada evento.

**Entities nuevas para Vol. 1-2:**
- Personas: Emma Hale Smith, William W. Phelps, Parley P. Pratt, David Whitmer, Zina D. Young, Jonathan Napela, B. H. Roberts, George Q. Cannon
- Eventos: Mountain Meadows Massacre, Utah War (1857-58), Pioneer Exodus
- Lugares: Palmyra NY, Hill Cumorah, Harmony PA, Fayette NY, Far West MO, Salt Lake Valley, Deseret Territory

---

### Doctrines of the Gospel (Student + Teacher Manual)

**Estado:** `ingested` — 43 archivos EN+ES en corpus | Script: `download_manual.py --manual doctrines-of-the-gospel`
**Seed file:** `data/kg-seeds/doctrines-of-the-gospel.json` ✅

#### Fase 0 — Análisis de contenido

**Estructura:** 37 capítulos temáticos + Introduction + 4 índices (autores, escrituras, temas, bibliografía). Nivel instituto. Cada capítulo = **outline doctrinal jerárquico** (A/B/C/D sub-puntos, cada uno con 2–5 pruebas escriturales) + **antología de citas de profetas** (Supporting Statements). El capítulo de la Expiación (ch. 9) solo tiene 60+ citas de escrituras y cita a Marion G. Romney, Bruce R. McConkie, John Taylor, J. Reuben Clark Jr., y otros. El índice de autores mapea cada GA citado a los capítulos relevantes — un activo KG en sí mismo.

**Tipo de contenido:** Referencia teológica académica. Es la fuente de mayor densidad doctrinal del corpus: cada sub-punto está anclado a escritura + profeta con fuente completa. No es narrativo; es sistemático.

**Densidad de citas:** ~33+ escrituras por capítulo (ch. 1), ~60+ en ch. 9. La más alta de todos los manuales investigados.

**Personas clave citadas:** Marion G. Romney, Bruce R. McConkie, John Taylor, J. Reuben Clark Jr., Neal A. Maxwell, Boyd K. Packer, Spencer W. Kimball, David O. McKay, Harold B. Lee, Joseph Fielding Smith, LeGrand Richards, Mark E. Petersen.

**Valor KG único:**
- Mayor fuente de `prophet→doctrine` con confianza curada — cada cita es atribuible a persona + fuente + año
- Índice de escrituras → mapa bidirecional `scripture ↔ doctrine` (todos los capítulos donde cada versículo aparece)
- Índice de autores → mapa `prophet → conceptos enseñados` lista
- Relaciones únicas: `Atonement SATISFIES Justice`, `Fall MADE_NECESSARY Atonement`, `Christ QUALIFIED_FOR Atonement BY sinlessness`

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `TAUGHT` | D&C 93:24 | Truth (definition) | DOTG ch. 1 |
| `IS_SAME_AS` | Jesus Christ | Truth | John 14:6; D&C 93:11 |
| `DESCRIBED_BY` | Atonement | Justice (satisfies) | Alma 42:13-14 |
| `PREREQUISITE_FOR` | Fall of Adam | Atonement | 2 Nephi 2:13 |
| `DESCRIBED_IN` | Jesus Christ (suffering) | Gethsemane | Matt. 26:36-46; D&C 19:15-20 |
| `AUTHORED` | John Taylor | The Mediation and Atonement | DOTG ch. 9 bibliography |

**Entidades nuevas para gazetteer:** Marion G. Romney, J. Reuben Clark Jr., Neal A. Maxwell, Boyd K. Packer, Mark E. Petersen, LeGrand Richards, Outer Darkness, Sons of Perdition

**URLs:** `/study/manual/doctrines-of-the-gospel` y `/study/manual/doctrines-of-the-gospel-student-manual`
**Autoridad:** 60 | **Bilingüe:** sí

**Descripción:** Manual de instituto dedicado a doctrinas fundamentales.
El student manual es una referencia teológica sistemática. Equivalente
académico de Gospel Principles pero más profundo.

**KG valor:** Cada capítulo = concepto doctrinal con citas extensas de
profetas y escrituras → fuente ideal para relaciones `teaches_doctrine`.

---

### Gospel Topics (Topics and Questions)

**Estado:** `ingested` — 299 archivos EN+ES en corpus | Script: `download_manual.py --manual gospel-topics`

**URL:** `/study/manual/gospel-topics` | **Bilingüe:** sí
**Autoridad:** 65

**Descripción:** Enciclopedia de temas doctrinales del sitio oficial (~400 entradas).
Similar a True to the Faith pero con entradas más extensas y referencias más ricas.
Complementa (y en parte superpone) el Bible Dictionary y la Guía de las Escrituras.

**KG valor:** Alta densidad de conceptos bien definidos → fuente excelente
para gazetteer terms. Cada entrada puede convertirse en un nodo `concept` con
aliases y relaciones.

**Consideración:** Alto volumen. Priorizar después de True to the Faith.

---

### Missionary Preparation Teacher Manual 2025

**Estado:** `ingested` — 26 archivos EN+ES en corpus | Script: `download_manual.py --manual missionary-preparation`

**URL:** `/study/manual/missionary-preparation-teacher-manual-2025`
**Autoridad:** 60 | **Bilingüe:** sí

**Descripción:** Manual actualizado (2025) para preparar misioneros. Complementa
PME con énfasis en el proceso de preparación personal. Bilingüe.

---

## Tier 2c — Inventario Books & Lessons + Gospel Topics + Life Help (2026-04-04)

> Materiales descubiertos al auditar tres secciones del sitio oficial:
> `/study/books-and-lessons/`, `/study/manual/gospel-topics`, `/study/life-help/`.
> Investigación paso 2 completada antes de config/autoridad.

### Seminary Teacher Manuals (generación actual CFM-aligned)

**Estado:** `ingested` — Descargados 2026-04-05. OT 278, NT 312, BOM 312 archivos EN+ES (D&C 280 ya existía)

**Fuente:** Seminaries and Institutes of Religion (S&I). Autoría institucional,
sin autores individuales. Dirección curricular: Chad H Webb (administrador S&I)
y élder Clark G. Gilbert (comisionado de educación, Setenta). Formato "Seminary 2.0"
inaugurado 2023, con aval de élder D. Todd Christofferson y presidente M. Russell Ballard
(para Doctrinal Mastery, 2016).

**Tipo de contenido:** Manuales pedagógicos para maestros de seminario. Cuatro tipos
de lección: (1) Scripture Course (alineadas a CFM semanal), (2) Life Preparation
(resiliencia emocional, preparación misional/templo, autosuficiencia), (3) Doctrinal
Mastery Practice, (4) Assess Your Learning. Cada semana tiene un overview + 5 lecciones
diarias. ~160-200 lecciones por manual. Diseñados para maestros sin experiencia previa.

**Audiencia:** Maestros de seminario — tanto voluntarios llamados (mayoría mundial) como
empleados CES. S&I superó 1 millón de alumnos en 2026.

**Autoridad:** 60 — currículo oficial S&I aprobado por la Iglesia; pedagógico, no doctrinal.
No son declaraciones de AG sino herramientas de enseñanza institucionales.

**Bilingüe:** Sí — los tres manuales actuales y el curriculum training existen en ES.

#### A) Old Testament Seminary Teacher Manual 2026

**Key:** `ot-seminary-teacher` | **Slug:** `old-testament-seminary-manual-2026`
**Publicación:** Dic 2025 (Church Newsroom). Año curricular 2026.
**Relaciones:** Alineado con CFM 2026 (AT). Companion: OT Student Manual 2026 (ya en corpus).
Supersede: OT Seminary Teacher Manual 2018. Companion meta-training: Seminary Curriculum
Training 2026 (item E).

#### B) Book of Mormon Seminary Teacher Manual 2024

**Key:** `bom-seminary-teacher` | **Slug:** `book-of-mormon-seminary-teacher-manual-2024`
**Publicación:** 2024. Segunda generación del formato actual.
**Relaciones:** Alineado con CFM 2024 (LdM). Companion: BofM Student Manual 2024 (ya en corpus).
Supersede: BofM Seminary Teacher Manual 2020. Incluye 32 lecciones home-study.
Requisito: 75% en learning assessments para crédito.

#### C) New Testament Seminary Teacher Manual 2023

**Key:** `nt-seminary-teacher` | **Slug:** `new-testament-seminary-teacher-manual-2023`
**Publicación:** 2023. Manual inaugural de la generación actual.
**Relaciones:** Alineado con CFM 2023 (NT). Companion: NT Student Manual 2023 (ya en corpus).
Supersede: NT Seminary Teacher Manual 2019. Primer manual con la arquitectura de lección actual.

#### D) D&C Home-Study Seminary Guide 2014

**Key:** `dc-seminary-home-study` | **Slug:** `doctrine-and-covenants-and-church-history-study-guide-for-home-study-seminary-students-2014`
**Publicación:** Junio 2014. Generación anterior (pre-CFM, pre-Doctrinal Mastery).
**Tipo:** Guía de estudio para alumnos (no manual de maestro). Para estudiantes sin
acceso a seminario diario. 32 unidades × 4 lecciones = 128 lecciones.
**Estado actual:** No retirado del sitio pero funcionalmente supersedido por los materiales
D&C 2025. Formato legacy — pre-CFM, pre-Life Preparation.
**Decisión:** Prioridad baja. El D&C Seminary Teacher Manual 2025 (ya en corpus) es más
actual y relevante. Descargar solo si se busca completitud histórica del currículo.
**Autoridad:** 55 — legacy, no current.

#### E) Seminary Curriculum Training 2026

**Key:** pendiente | **Slug:** `seminary-curriculum-training-2026`
**Publicación:** 2026, acompaña al manual OT.
**Tipo:** Meta-documento de capacitación, NO manual de lecciones. Enseña a los maestros
*cómo usar* los manuales. Secciones: Quick Start Guide, Life Preparation Training,
Doctrinal Mastery Training, Assessment Training, Adopting/Adapting Curriculum.
**Referenciado en:** S&I Annual Training Broadcast enero 2026 (élder Gilbert, hno. Webb).
**Relaciones:** Companion de todos los teacher manuals actuales (OT 2026, BofM 2024, NT 2023, D&C 2025).
**Decisión:** Valor moderado para el corpus. Es pedagógico-administrativo, no doctrinal ni
escriturístico. Contiene principios de enseñanza que podrían complementar "Teaching in the
Savior's Way". Prioridad media-baja.
**Autoridad:** 50 — herramienta administrativa interna S&I.

**Valor KG — relaciones esperadas (teacher manuals):**

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `COMPANION_OF` | OT Teacher Manual 2026 | OT Student Manual 2026 | S&I curriculum |
| `COMPANION_OF` | BofM Teacher Manual 2024 | BofM Student Manual 2024 | S&I curriculum |
| `COMPANION_OF` | NT Teacher Manual 2023 | NT Student Manual 2023 | S&I curriculum |
| `ALIGNED_WITH` | OT Teacher Manual 2026 | Come Follow Me 2026 | CFM alignment |
| `ALIGNED_WITH` | BofM Teacher Manual 2024 | Come Follow Me 2024 | CFM alignment |
| `ALIGNED_WITH` | NT Teacher Manual 2023 | Come Follow Me 2023 | CFM alignment |
| `SUPERSEDES` | OT Teacher Manual 2026 | OT Teacher Manual 2018 | S&I curriculum cycle |
| `SUPERSEDES` | BofM Teacher Manual 2024 | BofM Teacher Manual 2020 | S&I curriculum cycle |
| `SUPERSEDES` | NT Teacher Manual 2023 | NT Teacher Manual 2019 | S&I curriculum cycle |
| `PART_OF` | Doctrinal Mastery | Seminary curriculum | Launched 2016 by pres. M. Russell Ballard |

**Entidades nuevas para gazetteer:** Seminary Curriculum Training, Life Preparation Lessons,
Doctrinal Mastery, Assess Your Learning, S&I Annual Training Broadcast

---

### Family Strengthening Manuals (Family Services + Curriculum Dept)

**Estado:** `ingested` — Descargados 2026-04-05. Marriage 18 EN+ES, Str.Marriage 17 (couples EN-only), Str.Family 19 (parents EN-only)

**Contexto institucional:** Dos productores distintos, dos contextos de uso:
- **Marriage and Family Relations** (2000): Departamento de Currículo de la Iglesia.
  Para reuniones dominicales (Escuela Dominical, RS, Sacerdocio). Enfoque doctrinal/escriturístico.
  Anunciado por el presidente Boyd K. Packer, presidente interino del Q12.
- **Strengthening Marriage/Family** (2006): LDS Family Services (ahora "Family Services").
  Para cursos entre semana fuera de reuniones dominicales. Integra metodología
  terapéutica profesional + doctrina. Grupos de ≤20 personas.

Ambas líneas coexisten — ninguna reemplaza a la otra. Todavía activas en 2023+ según
Church News y listadas en la página de family resources del sitio oficial.

**Tipo de contenido:** Manuales de curso con lecciones estructuradas. Los de Family Services
incluyen role-playing, ejercicios interactivos y perspectivas de consejeros profesionales.
Los de Curriculum Dept son más escriturísticos con referencias a la Proclamación de la Familia.

**Audiencia:** Marriage & Family Relations → miembros generales en reuniones dominicales.
Strengthening Marriage/Family → parejas/padres en cursos dedicados, impartidos por
instructores voluntarios o profesionales de Family Services.

**Autoridad:** 55 — manuales oficiales de la Iglesia pero orientados a enriquecimiento
práctico, no a doctrina canónica. El respaldo de Family Services les da peso profesional.

#### A) Marriage and Family Relations Instructor's Manual (2000)

**Key:** `marriage-family-instructor` | **Slug:** `marriage-and-family-relations-instructors-manual`
**Estructura:** 16 lecciones en 2 partes: Parte A "Strengthening Marriages" (8 lecciones:
matrimonio eterno, unidad, amor, desafíos, comunicación, fe/oración, perdón, finanzas) +
Parte B "Parents' Responsibilities" (8 lecciones: deberes parentales, ejemplo, instrucción
del evangelio, guía de hijos). Basado en escrituras, enseñanzas proféticas y la Proclamación.
**Companion:** Marriage and Family Relations Participant's Study Guide (ya en corpus como
`family-resources/`).
**Bilingüe:** Sí.

#### B) Strengthening Marriage: Instructor's Guide (2006)

**Key:** `strengthening-marriage-instructor` | **Slug:** `strengthening-marriage-instructors-guide`
**Estructura:** 6 sesiones de ~90 min: (1) Applying Gospel Principles, (2) Communicating
with Love, (3) Fostering Equality and Unity, (4) Overcoming Anger, (5) Resolving Conflict,
(6) Enriching Marriage. Sesión 1 obligatoria como opener.
**Bilingüe:** Sí ("Cómo fortalecer el matrimonio: Guía para el instructor").

#### C) Strengthening Marriage: Resource Guide for Couples (2006)

**Key:** `strengthening-marriage-couples` | **Slug:** `strengthening-marriage-resource-guide-for-couples`
**Estructura:** Mismas 6 sesiones. Lecturas, ejercicios y actividades para parejas.
Sirve para uso en grupo y estudio individual.
**Bilingüe:** **No** — 404 en ES. Solo EN.

#### D) Strengthening the Family: Instructor's Guide (2006)

**Key:** `strengthening-family-instructor` | **Slug:** `strengthening-the-family-instructors-guide`
**Estructura:** 9 sesiones: (1) Parenting Principles, (2) Child Development, (3) Communicating
with Love, (4) Nurturing Children, (5) Fostering Confidence, (6) Overcoming Anger,
(7) Resolving Conflict, (8) Teaching Responsible Behavior, (9) Applying Consequences.
**Bilingüe:** Sí ("Cómo fortalecer a la familia: Guía para el instructor").

#### E) Strengthening the Family: Resource Guide for Parents (2006)

**Key:** `strengthening-family-parents` | **Slug:** `strengthening-the-family-resource-guide-for-parents`
**Estructura:** Mismas 9 sesiones. Lecturas y ejercicios para padres.
**Bilingüe:** **No** — 404 en ES. Solo EN.

#### F) Families and Temples (pamphlet misionero)

**Key:** `families-and-temples` | **Slug:** `families-and-temples`
**Tipo:** Panfleto misionero (NO manual de curso). 14 secciones: familia, retorno a Dios,
sacerdocio, propósitos del templo, bautismo por los muertos, historia familiar, investidura,
sellamiento, Q&A doctrinal, texto completo de la Proclamación de la Familia.
**Producido por:** Departamento Misional. Corresponde a lección 5, capítulo 3 de PME.
**Bilingüe:** Sí ("Las familias y los templos").
**Nota:** Género completamente diferente a los manuales A-E. Es material misionero.
**Autoridad:** 60 — pamphlet misionero oficial, mismo nivel que los otros teaching pamphlets.

**Mapa de relaciones entre recursos de familia:**

```
Marriage & Family Relations (2000, Curriculum Dept) — dominical, doctrinal, 16 lecciones
  Parte A: Matrimonio (8) ←comparable→ Strengthening Marriage (2006, Family Services)
  Parte B: Crianza (8)   ←comparable→ Strengthening the Family (2006, Family Services)

Strengthening Marriage (2006) — entre semana, terapéutico+doctrinal, 6 sesiones
  = Instructor's Guide (B) + Resource Guide for Couples (C)

Strengthening the Family (2006) — entre semana, terapéutico+doctrinal, 9 sesiones
  = Instructor's Guide (D) + Resource Guide for Parents (E)

Families and Temples — pamphlet misionero, género diferente
  = Parte del set PME teaching pamphlets
```

**Valor KG — relaciones esperadas:**

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `COMPANION_OF` | Marriage & Family Instructor | Marriage & Family Participant | Curso 2000 |
| `COMPANION_OF` | Strengthening Marriage Instructor | Strengthening Marriage Couples | Curso 2006 |
| `COMPANION_OF` | Strengthening Family Instructor | Strengthening Family Parents | Curso 2006 |
| `COMPLEMENTS` | Strengthening Marriage | Marriage & Family Relations | Ensign Mar 2009 |
| `COMPLEMENTS` | Strengthening the Family | Marriage & Family Relations | Ensign Mar 2009 |
| `PRODUCED_BY` | Strengthening Marriage/Family (4) | LDS Family Services | Inst. authorship |
| `PRODUCED_BY` | Marriage & Family Relations | Church Curriculum Dept | Announced by pres. Packer |
| `REFERENCES` | Marriage & Family Relations | The Family: A Proclamation | "Special emphasis" |
| `PART_OF` | Families and Temples | Preach My Gospel pamphlet set | PME ch3 lesson 5 |

---

### Self-Reliance — manuales secundarios (Self-Reliance Services / Obispado Presidente)

**Estado:** `ingested` — Descargados 2026-04-05. Leaders 4, My Path 3, PEF 1, Facilitating 3, Plan 1 archivos EN+ES

**Contexto institucional:** Todos producidos por Self-Reliance Services (antes Welfare and
Self-Reliance Services), bajo el Obispado Presidente. Forman un ecosistema integrado:

```
Leader's Guide (E) — documento maestro que define la estructura organizacional
  ↓
My Path (C) — punto de entrada del miembro, canaliza a 5 cursos
  ↓
Facilitating Groups (D) — entrena a los facilitadores de los cursos
  ↓
[5 cursos de 12 semanas: Personal Finances, Find a Better Job, Education,
 Starting a Business, Emotional Resilience] ← ya en corpus
  ↓
PEF Lesson (B) — post-curso para solicitantes de préstamo educativo
  ↑
Self-Reliance Plan + Bishop's Guide (A) — formularios operacionales de bienestar
```

**Tipo de contenido:** Variado — formularios operacionales (A), lección única (B), cuadernillo
de evaluación (C), manual de capacitación (D), guía administrativa (E). Ninguno es un manual
de estudio doctrinal extenso.

**Audiencia:** Obispos y líderes (A, E), miembros en asistencia de bienestar (A), solicitantes
PEF (B), todos los miembros (C), facilitadores voluntarios (D).

**Autoridad:** 50-55 — material operacional/administrativo de la Iglesia. Respaldado por el
Obispado Presidente pero orientado a implementación práctica, no a doctrina.

**Bilingüe:** Todos existen en ES (el programa opera fuertemente en Latinoamérica).

#### A) Self-Reliance Plan and Bishop's Guide

**Key:** `sr-self-reliance-plan` | **Slug:** `self-reliance-plan-and-bishops-guide-explanation`
**Publicación:** ~2012, rev. 2024. Formulario operacional — los miembros evalúan necesidades,
ingresos, gastos, recursos disponibles y desarrollan un plan. El Bishop's Guide acompaña
para seguimiento. Referenciado en General Handbook sección 22.
**Decisión:** Valor moderado-bajo para RAG/KG. Es un formulario, no prosa doctrinal.
Útil como referencia de cómo funciona el programa de bienestar. Prioridad baja.

#### B) Perpetual Education Fund for Self-Reliance

**Key:** `sr-perpetual-education` | **Slug:** `perpetual-education-fund-for-self-reliance`
**Publicación:** 2017. Lección única (~60 min) administrada después del curso "Education for
Better Work". Explica cómo funcionan los préstamos PEF, el convenio de pago, y la naturaleza
perpetua del fondo. PEF anunciado por el presidente Hinckley en CG abril 2001; 110K+ beneficiarios.
**Decisión:** Valor bajo para RAG doctrinal. Es operacional. Podría tener valor histórico
como conexión al discurso de Hinckley 2001. Prioridad baja.

#### C) My Path for Self-Reliance

**Key:** `sr-my-path` | **Slug:** `my-path-for-self-reliance`
**Publicación:** 2016. Cuadernillo de ~20 páginas usado en una reunión grupal de 2 horas.
Doctrina de autosuficiencia + autoevaluación + selección de curso.
Punto de entrada obligatorio al programa. "Mi camino a la autosuficiencia" en ES.
**Decisión:** Valor moderado — contiene enseñanza doctrinal sobre autosuficiencia que
conecta con escrituras y principios del evangelio. Prioridad media.

#### D) Facilitating Groups for Self-Reliance (2018)

**Key:** `sr-facilitating-groups` | **Slug:** `facilitating-groups-for-self-reliance-2018`
**Publicación:** 2018 (edición revisada). Manual de capacitación que replica el formato
de las reuniones de grupo. Facilitadores NO son maestros — siguen el material al pie de
la letra, no deben hablar más que cualquier otro miembro del grupo.
**Decisión:** Valor bajo para corpus. Pedagógico-administrativo. Prioridad baja.

#### E) Leader's Guide for the Self-Reliance Initiative

**Key:** `sr-leaders-guide` | **Slug:** `leaders-guide-for-the-self-reliance-initiative`
**Publicación:** 2017. Guía maestra para líderes del sacerdocio. Cubre doctrina/principios,
marco de liderazgo, comité de estaca, llamamientos de especialista en autosuficiencia,
metodología de grupos. Referenciado en General Handbook.
**Decisión:** Valor moderado — contiene sección doctrinal sobre autosuficiencia como
principio del evangelio. Prioridad media.

---

### Institute — materiales nuevos (S&I)

**Estado:** `ingested` — Descargados 2026-04-05. Student Readings 39 EN-only, Elevate 10 EN + 11 ES

**Contexto institucional:** Seminaries and Institutes of Religion (S&I), bajo CES y la
Junta de Educación de la Iglesia. Instituto atiende adultos 18-30+ (abierto a todos).

#### F) Institute Student Readings

**Key:** `institute-student-readings` | **Slug:** `institute-student-readings`
**Publicación:** ~2024 (copyright del plan curricular S&I).
**Tipo:** Compilación de lecturas asignadas para ~35 cursos: 4 Cornerstone (fundacionales),
9 Scripture (escrituras), 22+ otros (historia, liderazgo, temas especializados). Completar
lecturas es requisito de graduación (100% en cursos de escrituras, 75% en los demás).
Se necesitan 14 créditos (4 Cornerstone + 3 electivos) para graduarse.
**Bilingüe:** **No** — 404 en ES. Solo EN.
**Decisión:** Valor alto como meta-recurso que organiza el currículo de instituto. Pero su
contenido son lecturas de otras fuentes (escrituras, manuales, discursos) que probablemente
ya tenemos. Necesita evaluación de cuánto contenido original vs. pointers. Prioridad media.

#### G) Institute Elevate Learning Experience (ELE)

**Key:** `institute-elevate` | **Slug:** `institute-elevate-learning-experience`
**Publicación:** 2016 (NO es un piloto 2024 como asumí — lleva una década en uso).
**Tipo:** Framework de evaluación/enriquecimiento. Tres opciones por curso: (1) Elevate
Learning Questions (preguntas de estudio específicas para Cornerstone), (2) Course Study
Journal, (3) Personal Learning Project aprobado por maestro. Completar una opción ELE es
obligatorio para crédito.
**Bilingüe:** Sí — "Experiencia de Elevar el aprendizaje en Instituto".
**Decisión:** Valor moderado — las preguntas de estudio revelan qué considera S&I como
los conceptos clave de cada curso. Prioridad media-baja.
**Corrección necesaria:** Eliminar nota "2024 pilot" del ManualConfig — es 2016, no pilot.

---

### Teaching — materiales complementarios

**Estado:** `ingested` — Teacher Development Skills 27 archivos EN+ES (ya existían), Christlike Teaching 1 EN-only (ya existía)

**Contexto:** Ambos derivan de "Teaching in the Savior's Way" (2022, ya en corpus) pero
para audiencias diferentes.

#### H) Teacher Development Skills

**Key:** `teacher-development-skills` | **Slug:** `teacher-development-skills`
**Publicación:** ~2022+. Producido por S&I.
**Tipo:** Framework de competencias con 5 categorías y ~27 habilidades individuales:
(1) Focus on Jesus Christ, (2) Love Those You Teach, (3) Teach By the Spirit,
(4) Teach the Doctrine, (5) Invite Diligent Learning. Incluye herramienta de
autoevaluación personal ("Improving as a Christlike Teacher").
**Audiencia:** Maestros de S&I (seminario/instituto) — tanto empleados CES como voluntarios.
Versión profesional de los principios de "Teaching in the Savior's Way".
**Bilingüe:** Sí — "Habilidades para el desarrollo del maestro".
**Autoridad:** 55 — herramienta pedagógica S&I, no doctrinal.
**Decisión:** Valor moderado para corpus. Complementa Teaching in the Savior's Way con
operacionalización específica. Prioridad media-baja.

#### I) Principles of Christlike Teaching

**Key:** `principles-of-christlike-teaching` | **Slug:** `principles-of-christlike-teaching`
**Publicación:** Enero 2025. Producido por Escuela Dominical / Departamento de Currículo.
**Tipo:** Recurso visual/diagrama conciso (primariamente single-page con PDF descargable)
que sintetiza los principios de enseñanza de "Teaching in the Savior's Way" en un framework
visual interconectado. NO es un manual completo.
**Audiencia:** Maestros de barrio/rama. Catalogado bajo "Ward or Branch Callings > Sunday
School > Teaching and Learning". Referenciado en General Handbook capítulo 17.
**Bilingüe:** **No** — 404 en ES. Posiblemente pendiente de traducción (muy reciente).
**Autoridad:** 55 — recurso visual complementario.
**Decisión:** Valor bajo — es un diagrama, no prosa sustantiva. Ya tenemos "Teaching in the
Savior's Way" que contiene todo el contenido fuente. Prioridad baja.

**Valor KG — relaciones esperadas (self-reliance + institute + teaching):**

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `PART_OF` | My Path | Self-Reliance Initiative | Entry point |
| `PART_OF` | Facilitating Groups | Self-Reliance Initiative | Trainer guide |
| `PART_OF` | Leader's Guide | Self-Reliance Initiative | Master admin doc |
| `PREREQUISITE_FOR` | Education for Better Work | PEF Lesson | PEF manual |
| `ANNOUNCED_BY` | Perpetual Education Fund | Gordon B. Hinckley | CG abril 2001 |
| `COMPANION_OF` | Institute Student Readings | Institute Elevate | S&I curriculum |
| `DERIVED_FROM` | Teacher Development Skills | Teaching in the Savior's Way | S&I operationalization |
| `DERIVED_FROM` | Principles of Christlike Teaching | Teaching in the Savior's Way | Visual summary |
| `PRODUCED_BY` | Self-Reliance materials (A-E) | Presiding Bishopric | Self-Reliance Services |
| `PRODUCED_BY` | Institute materials (F-G) | Seminaries and Institutes | S&I/CES |

---

### Gospel Topics — gap ES (RESUELTO 2026-04-05)

**Estado:** `ingested` — 279 ES / 299 EN

**Resultado de verificación (2026-04-05):** De los 24 tópicos faltantes en ES:
- **3 existían y fueron descargados:** patriarchal-blessings, restoration-of-the-church-study-guide, tithing
- **21 NO existen en ES** — la API devuelve la página índice ("Temas y preguntas") en vez de contenido individual. No están traducidos al español.

**Tópicos sin traducción al español (21):**
church-financial-administration, debt, divorce, high-council, joseph-smiths-character,
journal-of-discourses, mormon-church, mormonism, mormons, movies-and-television,
plural-marriage, prison-ministry,
race-and-the-church-of-jesus-christ-of-latter-day-saints, religion-and-science,
religion-vs-violence, sacrament-meeting, single-parent-families,
temples-of-the-church-of-jesus-christ-of-latter-day-saints, transgression,
transparency-about-church-history-questions, womens-service-and-leadership-in-the-church.

**No hay acción posible** — el contenido simplemente no existe en ES en el sitio oficial.
Diferencia final: 299 EN vs 279 ES = 20 tópicos sin traducir (normal para el sitio).

---

### Life Help — análisis de contenido

**Estado:** `backlog` (evaluación pendiente de valor)

**Hallazgo:** Las páginas `/study/life-help/{topic}` son **hubs de navegación** sin contenido
propio — curan enlaces a charlas de conferencia, escrituras y videos que ya están en el corpus.
Las páginas `/study/manual/{topic}` bajo Life Help son **mini-manuales** de 1-4 párrafos cada uno.

**Contenido ya cubierto:** `counseling-resources/` (23 temas, EN+ES) cubre la perspectiva
del líder con más profundidad que los mini-manuales.

**Decisión:** Prioridad muy baja. Los hubs no aportan texto nuevo. Los mini-manuales
(adoption, child-nutrition, death, divorce, grief) son tan cortos que su valor para RAG
es marginal. Podríamos indexarlos eventualmente por completitud pero no son prioritarios.

**ES disponibilidad:** 10 de 13 existen en ES. Faltan: hope, adoption, death.

---



### 17. Ensign / Liahona archive

**Estado:** `backlog`

**Descripción:** Revista oficial mensual desde 1971 (Ensign) y 2001
(Liahona, fusión de publicaciones internacionales). Artículos de miembros,
líderes y académicos.

**URL pattern probable:** `/study/ensign/{year}/{month}` o similar.
**Autoridad:** 55 — publicación oficial pero autores variados.

**Consideración especial:** Volumen muy grande (~600 números × ~20 artículos
= ~12,000 documentos). Priorizar por relevancia temática o rango de autor.

---

## B.H. Roberts — Obras completas (authority=40, books)

> B.H. Roberts (1857–1933): presidente del Primer Quórum de los Setenta,
> historiador asistente de la Iglesia, "the foremost Latter-day Saint
> historian of the first century of the Church's existence." 20 libros
> en corpus, 624 capítulos. Source: Project Gutenberg (dominio público).

### Corianton: A Nephite Story (1889/1902)

**Estado:** `ingested` (corpus, pendiente indexación) | 13 capítulos

**Fase 0:**
- **¿Qué es?** Novela corta basada en la historia de Coriantón (Alma 39-42).
  Publicada en serie en The Contributor (1889), reimpresa como libro (1902).
  Ficción narrativa, no historia ni teología.
- **¿Quién?** B.H. Roberts (como autor de ficción, no como historiador).
- **¿Para quién?** Público general SUD. Inspiró una obra de teatro (1902),
  una película (1931), y es hito de la literatura mormona temprana.
- **¿Cómo referenciado?** Significativo en historia cultural SUD. No citado
  doctrinalmente. Wikipedia lo documenta como fenómeno cultural.
- **Limitaciones:** Ficción — no es fuente doctrinal ni histórica. Authority
  más bajo que las obras de no-ficción de Roberts.

**Authority override:** authority=25 (ficción basada en escritura, no doctrinal)

---

### The Missouri Persecutions (1900)

**Estado:** `ingested` (corpus, pendiente indexación) | 49 capítulos

**Fase 0:**
- **¿Qué es?** Historia detallada de las persecuciones SUD en Missouri
  (1830-1838). Cubre la Orden de Exterminio de Boggs, la Guerra de Missouri,
  expulsión de los santos. Companion volume de Rise and Fall of Nauvoo.
- **¿Quién?** B.H. Roberts, publicado por George Q. Cannon & Sons (1900).
- **¿Para quién?** Juventud SUD — Roberts explícitamente: "placing in the
  hands of the youth...a full statement of the persecutions."
- **¿Cómo referenciado?** Fuente primaria para historia SUD en Missouri.
  Citado en manuales de historia de la Iglesia (Lesson 16 del Church
  History Teacher Manual referencia el periodo).
- **Relaciones KG:** Alta densidad — Joseph Smith, Sidney Rigdon, Lilburn
  Boggs, Far West, Independence, Adam-ondi-Ahman, Haun's Mill.

---

### A New Witness for God (3 vols, 1895/1909)

**Estado:** `ingested` (corpus, pendiente indexación) | 77 capítulos (30+29+18)

**Fase 0:**
- **¿Qué es?** Obra apologética en 3 volúmenes. Vol 1 (1895): defensa de
  José Smith como profeta. Vols 2-3 (1909, "New Witnesses"): defensa del
  Libro de Mormón — evidencias internas, externas, tradiciones americanas.
  Es el tratamiento más extenso de Roberts sobre el Libro de Mormón.
- **¿Quién?** B.H. Roberts como apologista oficial. "Defender of the faith."
- **¿Para quién?** Audiencia SUD educada + público externo.
- **¿Cómo referenciado?** Piedra angular de la apologética SUD temprana.
  Precursor intelectual de FARMS/Interpreter. Contexto: Roberts luego
  escribió "Studies of the Book of Mormon" (póstumo, 1985) con preguntas
  más difíciles — ambos lados del mismo pensador.
- **Relaciones KG:** Libro de Mormón como entidad central, José Smith,
  evidencias arqueológicas, tradiciones nativas americanas, testimonios
  de los testigos.

---

### Outlines of Ecclesiastical History (1893)

**Estado:** `ingested` (corpus, pendiente indexación) | 22 capítulos

**Fase 0:**
- **¿Qué es?** Manual/textbook de historia eclesiástica desde la iglesia
  primitiva hasta la Restauración. Cubre apostasía, concilios, Reforma,
  y restauración. Notas y preguntas de repaso al final de cada capítulo.
- **¿Quién?** B.H. Roberts, publicado como libro de texto (1893).
- **¿Para quién?** Estudiantes — formato de manual con ejercicios.
- **¿Cómo referenciado?** Usado en educación SUD temprana. Precursor
  temático de The Great Apostasy (Talmage, 1909).
- **Relaciones KG:** Gran Apostasía, Concilios (Nicea, Calcedonia),
  Reforma (Lutero, Calvino, Wesley), Restauración.

---

### Seventy's Course in Theology (5 vols, 1907-1912)

**Estado:** `ingested` (corpus, pendiente indexación) | 170 capítulos (43+44+37+23+23)

**Fase 0:**
- **¿Qué es?** Manuales de estudio teológico para los quórums de los Setenta.
  5 años de currículo: (1) Historia de los Setenta + escrituras, (2) Historia
  de las dispensaciones, (3) Doctrina de Dios, (4) Expiación, (5) Espíritu
  Santo e inmanencia divina. Formato: lecciones con outline, referencias,
  notas extensas, citas de otros comentaristas.
- **¿Quién?** B.H. Roberts, por encargo oficial para 146 quórums de Setenta.
- **¿Para quién?** Setentas (líderes del sacerdocio). Nivel avanzado.
- **¿Cómo referenciado?** "One of the most important works of Mormon theology
  in the 20th Century" (Mormon Texts Project). Roberts como "leading LDS
  philosophical and theological thinker."
- **⚠️ Nota:** Vol 3 contiene una lección sobre "Negro Race Problem" con
  contenido racista pseudocientífico. Contexto histórico necesario si
  alguna vez se expone al usuario.
- **Relaciones KG:** Expiación, Trinidad/Deidad, Espíritu Santo, Sacerdocio,
  dispensaciones (Adán→Noé→Abraham→Moisés→Cristo→José Smith).

---

### History of the Church (6 vols, 1902-1912)

**Estado:** `ingested` (corpus, pendiente indexación) | 224 capítulos

**Fase 0:**
- **¿Qué es?** La historia oficial más importante de la Iglesia temprana.
  6 volúmenes que cubren la vida de José Smith (1805-1844). Basada en el
  manuscrito de la "History of Joseph Smith" compilada por escribientes del
  Profeta (1838-1857). Roberts editó, corrigió errores, añadió notas
  explicativas y material corroborativo. Vol 7 (no en corpus) cubre 1844-1848.
- **¿Quién?** Joseph Smith (fuente original) + B.H. Roberts (editor/compilador).
  Comisionada por la Primera Presidencia.
- **¿Para quién?** Miembros, académicos, líderes.
- **¿Cómo referenciado?** "The most-cited source in two official histories"
  (Our Heritage, Church History in the Fulness of Times). No tiene estatus
  de "historia oficial" pero es la fuente más citada sobre José Smith.
  Ampliamente usada en sermones de Autoridades Generales.
- **Limitaciones:** Escrita en primera persona como si fuera diario de José
  Smith, pero gran parte fue compilada por escribientes y editada por Roberts.
  Ver Joseph Smith Papers para fuentes primarias originales.
- **Relaciones KG:** MÁXIMA densidad — prácticamente toda persona, lugar y
  evento de la historia temprana de la Iglesia aparece aquí. Joseph Smith,
  Primera Visión, Kirtland, Nauvoo, Carthage, todos los apóstoles originales,
  revelaciones de D&C en contexto histórico.

**Authority override sugerido:** authority=55 (comisionado por Primera
Presidencia, fuente más citada de historia SUD, mayor que books default=40)

---

### The Life of John Taylor (1892)

**Estado:** `ingested` (corpus, pendiente indexación) | 49 capítulos

**Fase 0:**
- **¿Qué es?** Biografía del tercer presidente de la Iglesia. Cubre desde
  su nacimiento en Inglaterra hasta su muerte (1887). Incluye su conversión,
  misiones, el martirio de Cartago (donde Taylor fue herido), su presidencia
  durante la persecución por poligamia.
- **¿Quién?** B.H. Roberts. El manuscrito fue revisado por un comité
  designado por la Primera Presidencia (John Jaques y L. John Nuttall)
  para "doctrinal and historical correctness."
- **¿Para quién?** Miembros, estudiantes de historia.
- **¿Cómo referenciado?** Biografía estándar de John Taylor. Roberts fue
  "the foremost Latter-day Saint historian."
- **Relaciones KG:** John Taylor, Cartago, martirio, poligamia/Manifiesto,
  Brigham Young (sucesión), Inglaterra (misión).

---

### The Mormon Doctrine of Deity (1903)

**Estado:** `ingested` (corpus, pendiente indexación) | 8 capítulos

**Fase 0:**
- **¿Qué es?** El debate Roberts-Van Der Donckt sobre la doctrina SUD de
  Dios. Roberts defiende la corporeidad de Dios y la pluralidad de dioses
  contra la doctrina católica de la Trinidad inmaterial. Incluye un discurso
  adicional: "Jesus Christ: The Revelation of God."
- **¿Quién?** B.H. Roberts vs Rev. Cyril Van Der Donckt (sacerdote católico
  de Pocatello, Idaho). Publicado en Improvement Era (1902).
- **¿Para quién?** Miembros educados, apologistas.
- **¿Cómo referenciado?** "The classic treatises on the Mormon implications
  of Deity" (Mormon Texts Project). "A major stepping stone in Mormon
  Theology." Debate fundacional sobre la Deidad SUD.
- **Relaciones KG:** Deidad (Godhead), corporeidad de Dios, Trinidad,
  Gran Apostasía (helenización de la doctrina cristiana).

---

### The Rise and Fall of Nauvoo (1900)

**Estado:** `ingested` (corpus, pendiente indexación) | 41 capítulos

**Fase 0:**
- **¿Qué es?** Historia del periodo de Nauvoo (1840-1846). Companion volume
  de Missouri Persecutions — continúa la secuencia histórica. Cubre la
  transformación de Commerce en Nauvoo, la intriga de John C. Bennett,
  la introducción del matrimonio plural, el martirio, la sucesión y el éxodo.
- **¿Quién?** B.H. Roberts, Deseret News (1900).
- **¿Para quién?** Juventud SUD (mismo propósito que Missouri Persecutions).
- **¿Cómo referenciado?** "One of the most complete historical accounts
  of the Nauvoo Period." Complemento esencial de Missouri Persecutions.
- **Relaciones KG:** Nauvoo, Joseph Smith, John C. Bennett, matrimonio
  plural, martirio, Brigham Young, Templo de Nauvoo, éxodo al oeste.

---

### Análisis conjunto — B.H. Roberts como autor

| Obra | Caps | Tipo | Authority | Valor KG |
|------|------|------|-----------|----------|
| History of the Church (6v) | 224 | Historia primaria | 55* | MÁXIMO |
| Seventy's Course (5v) | 170 | Teología/manual | 40 | Alto (doctrina) |
| New Witness for God (3v) | 77 | Apologética | 40 | Alto (BoM) |
| Missouri Persecutions | 49 | Historia | 40 | Alto (personas/lugares) |
| Life of John Taylor | 49 | Biografía | 40 | Alto (personas) |
| Rise and Fall of Nauvoo | 41 | Historia | 40 | Alto (personas/lugares) |
| Outlines Eccl. History | 22 | Manual/textbook | 40 | Medio (apostasía) |
| Mormon Doctrine of Deity | 8 | Teología/debate | 40 | Medio (doctrina) |
| Corianton | 13 | Ficción | 25* | Bajo |
| **Total** | **673** | | | |

*Overrides necesarios: HC=55 (comisionado por FP), Corianton=25 (ficción).

### KG — Paso 4: Pre-seed

**No se requiere pre-seed Cypher manual.** Razones:
1. Las personas/lugares mencionados ya existen masivamente en gazetteers
   (Joseph Smith, Brigham Young, Nauvoo, Kirtland, etc.)
2. El NER pipeline detectará automáticamente entidades en el texto
3. La HC es tan densa en entidades que el pipeline generará miles de
   `MENTIONS` edges por volumen

**Relaciones que el pipeline NO capturará (futuro enriquecimiento manual):**
- `AUTHORED_BY` B.H. Roberts → las 20 obras (meta.json ya lo incluye)
- `EDITED_BY` B.H. Roberts → History of the Church (vs authored by JS)
- `COMMISSIONED_BY` First Presidency → History of the Church
- `SEQUEL_OF` Rise and Fall of Nauvoo → Missouri Persecutions
- `REVIEWED_BY` John Jaques + L. John Nuttall → Life of John Taylor

Estas relaciones son pocas y específicas — se pueden agregar manualmente
post-indexación sin bloquear el proceso.

---

## Jerarquía de fuentes externas por calidad

> Las fuentes no oficiales se priorizan por **calidad textual**, **confiabilidad
> de la digitalización** y **riqueza de metadata**. Archive.org es último
> recurso por OCR inconsistente y formatos variables.

| Prioridad | Fuente | Calidad | Script | Notas |
|-----------|--------|---------|--------|-------|
| 🥇 1 | **Sitio oficial de la Iglesia** (churchofjesuschrist.org) | Excelente — HTML limpio, API oficial, bilingüe | `download_manual.py`, `download_scriptures.py`, etc. | Fuente canónica. Siempre preferir sobre cualquier otra. |
| 🥈 2 | **RSC BYU** (rsc.byu.edu) | Muy buena — Drupal HTML limpio, footnotes, metadata estructurada | `download_rsc.py` | ~215 libros online. Contenido académico SUD de alta calidad. |
| 🥉 3 | **BYU Studies** (byustudies.byu.edu) | Buena — Next.js RSC, HTML en payload, footnotes | `download_byustudies.py` | History of the Church y otros textos históricos. |
| 4 | **Mormon Texts Project** (mormontextsproject.org) | Buena — texto corregido manualmente, dominio público | Pendiente | Transcripciones revisadas de Journal of Discourses y otros. ⚠️ Bloqueado por proxy Solera. |
| 5 | **Project Gutenberg** (gutenberg.org) | Variable — texto plano limpio, sin footnotes, sin metadata rica | `download_gutenberg.py` | Bookshelf LDS: ~120 títulos. Buena calidad textual pero splitting manual. |
| 6 | **CCEL** (ccel.org) | Buena — ThML/XML estructurado | Script ad-hoc por obra | Diccionarios bíblicos clásicos (Easton ya ingested). |
| 7 | **Archive.org** | Baja — OCR variable, formatos inconsistentes | Caso por caso | **Último recurso.** Solo cuando no hay alternativa. Verificar OCR antes de ingestar. |

**Regla:** Antes de escribir un script nuevo, verificar si el texto existe en una
fuente de mayor prioridad. Workflow: Iglesia → RSC → BYU Studies → MTP → Gutenberg → CCEL → Archive.org.

---

## RSC BYU — Inventario y backlog (authority=25–35)

> Fuente: [rsc.byu.edu/books/online](https://rsc.byu.edu/books/online)
> Script: `download_rsc.py` — soporta libros de autor único y multi-autor
> (conferencias, symposia). Per-chapter author, subtitles, sections, footnotes.
> ~215 libros disponibles online (inventario 2026-04).
>
> **Nota:** Muchos libros RSC recientes son de pago ("not been released for
> online reading"). Solo se pueden descargar los libros libres.

### Categorías RSC y priorización (inventario completo 2026-04-05)

> 214 libros únicos disponibles online. Muchos libros aparecen en múltiples
> categorías (e.g., `opening-isaiah` en cat 1, 7 y 10). Los conteos son por
> categoría, no únicos.

| Cat ID | Categoría | Libros | Prioridad corpus | Justificación |
|--------|-----------|--------|------------------|---------------|
| 7 | Book of Mormon | 37 | **ALTA** | Exégesis académica SUD del LdM |
| 8 | Doctrine and Covenants | 5 | **ALTA** | Exégesis D&C, contexto histórico |
| 9 | Pearl of Great Price | 4 | **ALTA** | Exégesis PGP, Abrahám, Moisés |
| 10 | Bible Studies | 41 | **ALTA** | Perspectiva SUD sobre la Biblia |
| 1 | Scripture Study | 53 | ALTA | Estudio de escrituras general |
| 14 | Easter Conference | 10 | ALTA | Conferencias cristológicas |
| 15 | Sidney B. Sperry Symposium | 26 | ALTA | Conferencias escriturales multi-autor |
| 309 | Book of Mormon Symposium | 9 | ALTA | Conferencias LdM por libro |
| 12 | Gospel Questions | 21 | MEDIA | Preguntas doctrinales |
| 3 | Self-Help | 15 | MEDIA | Auto-ayuda con perspectiva SUD, salud mental |
| 13 | Church History Symposium | 12 | MEDIA | Conferencias académicas multi-autor |
| 11 | Teaching | 33 | MEDIA | Pedagogía religiosa |
| 2 | Church History | 152 | MEDIA | Historia académica SUD (mayoritariamente regional/biográfica) |
| 16 | Other Conferences | 14 | BAJA | Conferencias varias |
| 17 | World Religions & Traditions | 14 | BAJA | Religiones comparadas |

### Libros RSC prioritarios — por tipo de contenido

> **Criterios:** (1) relevancia doctrinal/escritural, (2) diversidad temática
> (no solo historia), (3) enriquecimiento del KG, (4) autores reconocidos.
> Inventario verificado 2026-04-05 vía `download_rsc.py --list-books --category N`.

**🔴 P1 — Exégesis escritural (Book of Mormon, D&C, PGP, Bible):**

| Slug | Título | Cat | Notas |
|------|--------|-----|-------|
| illuminating-jaredite-records | Illuminating the Jaredite Records | 7 | Multi-autor, ed. Belnap — verificado |
| give-ear-my-words | Give Ear to My Words | 15 | Multi-autor Sperry — verificado |
| opening-isaiah | Opening Isaiah | 1,7,10 | Clave para entender Isaías en el LdM |
| abinadi | Abinadi | 1,7 | Análisis profundo de Mosíah 11-17 |
| samuel-lamanite | Samuel the Lamanite | 7 | Profeta LdM poco estudiado |
| jacob | Jacob | 7 | Análisis del libro de Jacob |
| search-diligently-words-isaiah | Search Diligently the Words of Isaiah | 7,10 | Isaías en contexto SUD |
| introduction-book-abraham | An Introduction to the Book of Abraham | 9,2 | Exégesis PGP clave |
| book-moses-joseph-smith-translation-manuscripts | The Book of Moses and the JST Manuscripts | 9,1 | Exégesis Moisés/PGP |
| pearl-great-price-revelations-god | The Pearl of Great Price: Revelations from God | 9,1 | PGP completo |
| foundations-restoration | Foundations of the Restoration | 8,15 | Multi-autor, D&C — verificado |
| you-shall-have-my-word | You Shall Have My Word | 8,15 | D&C exégesis |
| doctrine-covenants-revelations-context | The D&C: Revelations in Context | 8,1 | Contexto histórico de cada sección |
| genesis | Genesis | 10,2 | Génesis desde perspectiva SUD |
| prophets-prophecies-old-testament | Prophets and Prophecies of the OT | 1,10 | AT desde perspectiva SUD |
| gospel-jesus-christ-old-testament | The Gospel of Jesus Christ in the OT | 1,10,15 | Cristo en el AT |
| thou-art-christ-son-living-god | Thou Art the Christ, the Son of the Living God | 1,10,15 | Cristología NT |
| ministry-peter-chief-apostle | The Ministry of Peter, the Chief Apostle | 1,10,15 | Pedro, primer apóstol |
| sermon-mount-latter-day-scripture | The Sermon on the Mount in Latter-day Scripture | 1,15 | Sermón del Monte vs 3 Nefi |
| new-testament-history-culture-society | NT History, Culture, and Society | 1,10 | Contexto NT |
| joseph-smiths-new-translation-bible | Joseph Smith's New Translation of the Bible | 9,1,10 | JST completa |
| understanding-joseph-smiths-translation-bible | Understanding JS's Translation of the Bible | 10,2 | JST académico |
| king-james-bible-restoration | The King James Bible and the Restoration | 1,10,16 | KJV en contexto SUD |

**🟡 P2 — Doctrina, convenios, templo, cristología:**

| Slug | Título | Cat | Notas |
|------|--------|-----|-------|
| ascending-mountain-lord | Ascending the Mountain of the Lord | 10,15 | Templo en la Biblia |
| household-god | The Household of God | 15 | Convenios y familia |
| covenant-compassion | Covenant of Compassion | 10,15 | Convenios en el AT |
| how-what-you-worship | How and What You Worship | 1,10,15 | Adoración |
| our-rites-worship | By Our Rites of Worship | 1,10,12 | Ordenanzas y adoración |
| he-was-seen | He Was Seen | 14 | Resurrección — Easter Conference |
| power-christs-deliverance | The Power of Christ's Deliverance | 14 | Expiación |
| tragedy-triumph | The Tragedy and the Triumph | 14 | Crucifixión y resurrección |
| his-majesty-mission | His Majesty and Mission | 14,10 | Cristología |
| our-saviors-love | Our Savior's Love | 14,10 | Cristología |
| healing-his-wings | With Healing in His Wings | 1,14 | Expiación |
| my-redeemer-lives | My Redeemer Lives! | 1,14 | Resurrección |
| save-lost | To Save the Lost | 1,14 | Misión de Cristo |
| celebrating-easter | Celebrating Easter | 14 | Conferencia pascual |
| behold-lamb-god | "Behold the Lamb of God" | 14 | Cristología |
| fulness-gospel | The Fulness of the Gospel | 15 | Plenitud del evangelio |
| temple-antiquity | The Temple in Antiquity | 12,16 | Templo en la antigüedad |
| lectures-faith-historical-perspective | Lectures on Faith in Historical Perspective | 1,2 | Lecturas sobre la fe |
| life-beyond-grave | Life Beyond the Grave | 11,12 | Escatología SUD |

**🟢 P3 — Fe, salud mental, vida práctica, apologética:**

| Slug | Título | Cat | Notas |
|------|--------|-----|-------|
| freedom-scrupulosity | Freedom from Scrupulosity | 3 | Salud mental + fe |
| our-savior-self-doubt | Our Savior from Self-Doubt | 3 | Auto-duda y fe |
| finding-christ-covenant-path | Finding Christ in the Covenant Path | 3 | Sendero del convenio |
| reason-faith | A Reason for Faith | 3 | Apologética SUD |
| no-weapon-shall-prosper | No Weapon Shall Prosper | 1,12 | Apologética SUD |
| shield-faith | Shield of Faith | 1,3,12 | Apologética |
| divine-design | By Divine Design | 3,11 | Propósito divino |
| moral-foundations-standing-firm-world-shifting-values | Moral Foundations | 16,3 | Ética y valores |
| let-us-reason-together | Let Us Reason Together | 11 | Diálogo interreligioso |
| converging-paths-truth | Converging Paths to Truth | 1,11,16 | Diálogo ecuménico |
| eye-faith | An Eye of Faith | 12,2 | Fe y razón |
| notes-amateur | Notes from an Amateur | 11 | Reflexiones sobre la fe |
| religion-mental-health-latter-day-saints | Religion, Mental Health, and the LDS | 3 | Salud mental |
| religion-family-connection | The Religion and Family Connection | 3,17 | Fe y familia |
| no-other-success | No Other Success | 3,2 | Éxito y fe |
| commitment-covenant | Commitment to the Covenant | 3 | Convenios |

**🔵 P4 — Historia (selectiva, no exhaustiva):**

| Slug | Título | Cat | Notas |
|------|--------|-----|-------|
| joseph-smith-visionary | Joseph Smith as a Visionary | 2 | JS como visionario |
| council-fifty | The Council of Fifty | 2 | Consejo de los Cincuenta |
| darkness-unto-light | From Darkness unto Light | 2 | Surgimiento del LdM |
| coming-forth-book-mormon | The Coming Forth of the Book of Mormon | 7,2,15 | Surgimiento del LdM |
| joseph-smiths-seer-stones | Joseph Smith's Seer Stones | 1,2 | Piedras videntes |
| joseph-smiths-uncanonized-revelations | Joseph Smith's Uncanonized Revelations | 2 | Revelaciones no canónicas |
| sister-prophet | Sister to the Prophet | 2 | Lucy Mack Smith — mujer clave |
| my-dear-sister | My Dear Sister | 2 | Mujeres de la Restauración |
| brigham-young-journals | The Brigham Young Journals | 2 | Diarios de BY |
| exploring-first-vision | Exploring the First Vision | 1,2,11 | Primera Visión |
| repicturing-restoration | Repicturing the Restoration | 2 | Arte de la Restauración |
| joseph-smith-his-first-vision | Joseph Smith and His First Vision | 2,13 | Primera Visión académico |
| well-sing-well-shout | We'll Sing and We'll Shout | 2 | Música SUD histórica |

**⚪ P5 — Relaciones interreligiosas y mundo:**

| Slug | Título | Cat | Notas |
|------|--------|-----|-------|
| view-hebrews | View of the Hebrews | 17 | Texto histórico relevante para LdM |
| peter-popes | Peter and the Popes | 17 | Pedro y la sucesión apostólica |
| understanding-covenants-communities | Understanding Covenants and Communities | 17 | Convenios interreligioso |
| mormons-muslims | Mormons and Muslims | 17 | Diálogo SUD-Islam |
| global-mormonism-21st-century | Global Mormonism in the 21st Century | 16 | Iglesia global |
| salvation-christ-comparative-christian-views | Salvation in Christ: Comparative Views | 2 | Soteriología comparada |
| alexander-campbell-joseph-smith | Alexander Campbell and Joseph Smith | 2 | Contexto restauracionista |

---

## BYU Studies — Inventario y backlog (authority=30–40)

> Fuente: [byustudies.byu.edu](https://byustudies.byu.edu)
> Script: `download_byustudies.py` — usa RSC payload (Next.js streaming).
> Contiene textos históricos que no están disponibles en otras fuentes digitales.

### Ya ingested

| Slug | Título | Caps | Estado | Fuente |
|------|--------|------|--------|--------|
| history-of-the-church-vol7 | History of the Church, Vol. 7 | 42 | `ingested` | BYU Studies |
| history-of-the-church-vol1 | History of the Church, Vol. 1 | 33 | `ingested` | Gutenberg |
| history-of-the-church-vol2 | History of the Church, Vol. 2 | 71 | `ingested` | Gutenberg |
| history-of-the-church-vol3 | History of the Church, Vol. 3 | 28 | `ingested` | Gutenberg |
| history-of-the-church-vol4 | History of the Church, Vol. 4 | 30 | `ingested` | Gutenberg |
| history-of-the-church-vol5 | History of the Church, Vol. 5 | 28 | `ingested` | Gutenberg |
| history-of-the-church-vol6 | History of the Church, Vol. 6 | 34 | `ingested` | Gutenberg |

> Nota: HC vols 1-6 descargados de Gutenberg (plain text). Si se quiere mejorar
> la calidad, re-descargar de BYU Studies (HTML limpio con footnotes).
> Decisión: mantener Gutenberg por ahora; upgrade opcional.

### Backlog

### Catálogo completo BYU Studies online (38 libros — verificado 2026-04-05)

> Inventario: 2026-04-05 via `download_byustudies.py --list-books`
> **38 títulos reales** — la estimación anterior de 65 era incorrecta.

**History of the Church (7 volúmenes):** ✅ Todos `ingested` (ver tabla arriba)

**BYU NT Commentary (4 volúmenes):**

| Slug | Prioridad | Notas |
|------|-----------|-------|
| the-testimony-of-luke | **ALTA** | Comentario académico SUD del NT |
| the-gospel-according-to-mark | **ALTA** | |
| pauls-first-epistle-to-the-corinthians | ALTA | |
| the-revelation-of-john-the-apostle | ALTA | |

**BYU NT Commentary: New Renditions (14 volúmenes):**

| Slug | Prioridad | Notas |
|------|-----------|-------|
| the-gospel-according-to-matthew-a-new-rendition | MEDIA | Traducción moderna del NT |
| the-gospel-according-to-mark-a-new-rendition | MEDIA | |
| the-testimony-of-luke-a-new-rendition | MEDIA | |
| pauls-first-epistle-to-the-corinthians-a-new-rendition | MEDIA | |
| pauls-second-epistle-to-the-corinthians-a-new-rendition | MEDIA | |
| the-epistle-to-the-ephesians-a-new-rendition | MEDIA | |
| pauls-first-epistle-to-the-thessalonians-a-new-rendition | MEDIA | |
| pauls-second-epistle-to-the-thessalonians-a-new-rendition | MEDIA | |
| pauls-first-epistle-to-timothy-a-new-rendition | MEDIA | |
| pauls-second-epistle-to-timothy-a-new-rendition | MEDIA | |
| pauls-epistle-to-titus-a-new-rendition | MEDIA | |
| philemon-a-new-rendition | MEDIA | |
| epistle-to-the-hebrews-a-new-rendition | MEDIA | |
| the-revelation-of-john-the-apostle-a-new-rendition | MEDIA | |

**Charting the Scriptures (2):**

| Slug | Prioridad | Notas |
|------|-----------|-------|
| charting-the-new-testament | MEDIA | Tablas/charts escriturales |
| charting-the-book-of-mormon | MEDIA | |

**Libros individuales (9):**

| Slug | Prioridad | Notas |
|------|-----------|-------|
| doctrine-and-covenants-contexts | **ALTA** | Contexto histórico de cada sección D&C |
| opening-the-heavens | **ALTA** | Manifestaciones divinas 1820-1844, fuentes primarias |
| my-fellow-servants | ALTA | Historia del sacerdocio |
| sustaining-the-law | MEDIA | Encuentros legales de JS |
| the-journals-of-william-e-mclellin | MEDIA | Diario de apóstol temprano (1831-36) |
| the-willie-handcart-company | MEDIA | Historia pionera |
| voyages-of-faith | BAJA | Historia mormona del Pacífico |
| wayward-saints | BAJA | Movimiento Godbeite |
| the-st-louis-luminary | BAJA | Periódico SUD histórico |

**Newsletters (ignorar):** 2 newsletters de BYU Religious Publications — no relevantes.

---

## MTP / Gutenberg — Textos pendientes priorizados (authority=25–40)

> Fuente: Mormon Texts Project → Project Gutenberg
> Los ~94 ebooks MTP son el upstream de casi todos los textos SUD en Gutenberg.
> Calidad: texto proofread 2x, sin OCR artifacts.
> Script: `download_gutenberg.py`
>
> **Journal of Discourses:** MTP explícitamente declinó transcribirlo.
> Solo disponible como PDF/OCR en Archive.org y BYU. NO hay texto limpio.
> El libro "Discourses of Brigham Young" (#74447) ya está en el corpus
> como antología temática compilada por Widtsoe.

### P2 — Alta prioridad doctrinal (no en corpus)

| # | Título | Autor | Notas |
|---|--------|-------|-------|
| 56684 | Lectures on Faith | Joseph Smith Jr. | Doctrina fundacional Kirtland, 7 lecturas |
| 6720 | The Wentworth Letter | Joseph Smith Jr. | Artículos de Fe originales |
| 35470 | Key to the Science of Theology | Parley P. Pratt | Teología sistemática temprana |
| 35554 | A Voice of Warning | Parley P. Pratt | Clásico misional, muy citado |
| 36327 | Mediation and Atonement | John Taylor | Cristología profética |
| 35562 | A Rational Theology | John A. Widtsoe | Teología moderna SUD |
| 54309 | Ancient Apostles | David O. McKay | Cristología por profeta |

### P3 — Biografías y memorias valiosas

| # | Título | Autor | Notas |
|---|--------|-------|-------|
| 59970 | Life of Joseph Smith, the Prophet | George Q. Cannon | Biografía por apóstol |
| 54331 | Life of a Pioneer | James S. Brown | Autobiografía, Batallón Mormón |
| 48284 | Jacob Hamblin: A Narrative | Jacob Hamblin | Misión a indios, frontera |
| 46391 | Memoirs of John R. Young | John R. Young | Pionero 1847 |
| 54337 | Reminiscences of Joseph the Prophet | Edward Stevenson | Testimonios personales de JS |
| 45049 | My First Mission | George Q. Cannon | Memorias misionales |

### P3 — Historia y apologética

| # | Título | Autor | Notas |
|---|--------|-------|-------|
| 42152 | The Mormon Battalion | B. H. Roberts | Historia militar |
| 44907 | Interesting Account of Remarkable Visions | Orson Pratt | Relato temprano Primera Visión |
| 54278 | Proclamation of the Twelve Apostles | Council of Q12 | Documento fundacional 1845 |
| 45006 | General Smith's Views | Joseph Smith Jr. | Plataforma presidencial 1844 |
| 49432 | Myth of the Manuscript Found | Various | Refutación tesis Spaulding |

### P4 — Perspectiva femenina

| # | Título | Autor | Notas |
|---|--------|-------|-------|
| 50958 | Representative Women of Deseret | Augusta J. Crocheron | Biografías de mujeres SUD |
| 54335 | The Women of Mormondom | Edward W. Tullidge | Historia colectiva de mujeres |
| 51097 | Heroines of Mormondom | Various | Narrativas de mujeres pioneras |
| 46602 | Lydia Knight's History | Susa Young Gates | Perspectiva femenina pionera |

### P4 — Colecciones y antologías

| # | Título | Autor | Notas |
|---|--------|-------|-------|
| 60056 | Scrap Book of Mormon Literature, Vol. 1 | Ben E. Rich | 38 panfletos (Roberts, Pratt, Snow) |
| 54298 | Scrap Book of Mormon Literature, Vol. 2 | Ben E. Rich | Más panfletos |
| 46734 | Scraps of Biography | Various | Colección biográfica |

### P5 — Doctrina menor y miscelánea

| # | Título | Autor | Notas |
|---|--------|-------|-------|
| 56700 | Mormon Doctrine, Plain and Simple | Charles W. Penrose | Doctrinal |
| 47336 | Cowley's Talks on Doctrine | Matthias F. Cowley | Charlas de apóstol |
| 50536 | Gospel Themes | Orson F. Whitney | Ensayos doctrinales |
| 46617 | The Plan of Salvation | John Morgan | Manual misional |
| 46974 | Rays of Living Light | Charles W. Penrose | Folletos misionales |
| 54292 | What Jesus Taught | Osborne J.P. Widtsoe | Cristología |

### P6 — Ficción, poesía, perspectiva externa

> Ficción y poesía SUD tienen bajo valor para el knowledge engine pero
> pueden ser útiles para contexto cultural. Perspectiva externa solo
> con authority=15-20 y etiqueta `external-perspective`.

| # | Título | Autor | Tipo |
|---|--------|-------|------|
| 17249 | Added Upon | Nephi Anderson | Ficción teológica |
| 37718 | Elias: An Epic of the Ages | Orson F. Whitney | Poema épico |
| 7066 | Under the Prophet in Utah | Frank J. Cannon | Crítica interna |
| 51096 | The Mormons (Discourse) | Thomas L. Kane | Perspectiva simpática |

---

## Gutenberg Bookshelf "Latter Day Saints" — Inventario completo

> Fuente: [gutenberg.org/ebooks/bookshelf/404](https://www.gutenberg.org/ebooks/bookshelf/404)
> Inventario tomado: 2026-04-04
> Excluye obras de B.H. Roberts (sección propia arriba) y Book of Mormon (#17).
> Estado por defecto: `backlog` salvo que se indique otra cosa.

### Ya en corpus o preparados

| # | Título | Autor | Estado |
|---|--------|-------|--------|
| 22542 | Jesus the Christ | James E. Talmage | `prepared` (script listo) |
| 42238 | The Articles of Faith | James E. Talmage | ver Tier 1 |

### Historia de la Iglesia

| # | Título | Autor | Prioridad | Notas |
|---|--------|-------|-----------|-------|
| 45054 | Essentials in Church History | Joseph Fielding Smith | **ALTA** | `ingested` — 54 ch |
| 45619 | History of the Prophet Joseph, by His Mother | Lucy Mack Smith | **ALTA** | `ingested` — 54 ch |
| 59970 | The Life of Joseph Smith, the Prophet | George Q. Cannon | ALTA | Biografía por apóstol/consejero FP |
| 56698 | The Latter-Day Prophet (para jóvenes) | George Q. Cannon | MEDIA | Versión juvenil de la anterior |
| 16534 | A Young Folks' History of the Church | Nephi Anderson | MEDIA | Historia popular simplificada |
| 2443 | The Story of the Mormons (hasta 1901) | William A. Linn | BAJA | `ingested` — 81 ch |
| 36486 | The City of the Mormons; Three Days at Nauvoo, 1842 | Henry Caswall | BAJA | Relato de viajero, perspectiva crítica |
| 46783 | Early Scenes in Church History | Various | MEDIA | `ingested` — 17 ch |
| 9661 | Mormon Settlement in Arizona | James H. McClintock | BAJA | Historia regional |

### Biografías y memorias

| # | Título | Autor | Prioridad | Notas |
|---|--------|-------|-----------|-------|
| 44896 | Autobiography of Parley Parker Pratt | Parley P. Pratt | **ALTA** | `ingested` — 54 ch |
| 47708 | Biography and Family Record of Lorenzo Snow | Eliza R. Snow | **ALTA** | `ingested` — 87 ch (biographies/) |
| 47703 | Wilford Woodruff, Fourth President | Wilford Woodruff | **ALTA** | `ingested` — 56/57 ch (ch19 missing in source) |
| 35333 | Life of Heber C. Kimball | Orson F. Whitney | **ALTA** | `ingested` — 66/68 ch (ch29,64 missing in source) |
| 47519 | President Heber C. Kimball's Journal | Heber C. Kimball | ALTA | `ingested` — 17 ch |
| 45051 | William Clayton's Journal | William Clayton | ALTA | `ingested` — 18 monthly sections |
| 54331 | Life of a Pioneer (autobiografía) | James S. Brown | MEDIA | Pionero, Batallón Mormón |
| 48284 | Jacob Hamblin (fronterizo/misionero) | Jacob Hamblin | MEDIA | Misión a los indios, frontera |
| 46391 | Memoirs of John R. Young, Utah Pioneer, 1847 | John R. Young | MEDIA | Pionero temprano |
| 51730 | Life of David W. Patten, First Apostolic Martyr | Lycurgus A. Wilson | MEDIA | `ingested` — 8 ch |
| 46602 | Lydia Knight's History | Susa Young Gates | MEDIA | Perspectiva femenina pionera |
| 46028 | Leaves from My Journal | Wilford Woodruff | MEDIA | `ingested` — 28 ch |
| 54337 | Reminiscences of Joseph, the Prophet | Edward Stevenson | MEDIA | Testimonios personales de JS |
| 46521 | Forty Years Among the Indians | Daniel W. Jones | MEDIA | Misiones, frontera |
| 50958 | Representative Women of Deseret | Augusta J. Crocheron | MEDIA | Biografías de mujeres SUD |
| 51097 | Heroines of "Mormondom" | Various | MEDIA | Más biografías femeninas |
| 46734 | Scraps of Biography | Various | BAJA | Colección miscelánea |
| 49739 | Gems of Reminiscence | Various | BAJA | Colección miscelánea |
| 49401 | Eventful Narratives | R. Aveson / O.B. Huntington | BAJA | Narrativas pioneras |

### Teología y doctrina (con valor histórico)

| # | Título | Autor | Prioridad | Notas |
|---|--------|-------|-----------|-------|
| 35514 | The Great Apostasy | James E. Talmage | **ALTA** | Ya en backlog Tier 3, patrística |
| 47109 | Gospel Doctrine (sermones) | Joseph F. Smith | **ALTA** | `ingested` — 25/26 ch (ch16 missing in source) |
| 56684 | The Lectures on Faith | Joseph Smith Jr. | **ALTA** | Doctrina fundacional (Kirtland) |
| 44941 | The Government of God | John Taylor | ALTA | `ingested` — 12 ch |
| 36327 | Mediation and Atonement | John Taylor | ALTA | Cristología profética |
| 35470 | Key to the Science of Theology | Parley P. Pratt | ALTA | Teología sistemática temprana |
| 35562 | A Rational Theology | John A. Widtsoe | ALTA | Teología moderna SUD |
| 47336 | Cowley's Talks on Doctrine | Matthias F. Cowley | MEDIA | Charlas doctrinales de apóstol |
| 50535 | Blood Atonement and Plural Marriage | Joseph Fielding Smith | MEDIA | Discusión apologética |
| 47182 | The Vitality of Mormonism (ensayos) | James E. Talmage | MEDIA | Ensayos breves |
| 46099 | The Vitality of "Mormonism" (discurso) | James E. Talmage | BAJA | Discurso individual |
| 5630 | The Story of "Mormonism" / Philosophy of "Mormonism" | James E. Talmage | MEDIA | Ensayos apologéticos |
| 45149 | The House of the Lord | James E. Talmage | MEDIA | Templos, alto interés |
| 50536 | Gospel Themes | Orson F. Whitney | MEDIA | Ensayos doctrinales |
| 56691 | Saturday Night Thoughts | Orson F. Whitney | BAJA | Ensayos misceláneos |
| 46536 | The Gospel: Exposition of First Principles | B.H. Roberts | MEDIA | Ya en corpus como Roberts |
| 54292 | What Jesus Taught | Osborne J.P. Widtsoe | MEDIA | Cristología |
| 54309 | Ancient Apostles | David O. McKay | ALTA | Profeta, cristología |
| 34362 | Joseph Smith as Scientist | John A. Widtsoe | MEDIA | Filosofía mormona |
| 49357 | Outlines of Mormon Philosophy | Lycurgus A. Wilson | BAJA | Filosofía especulativa |
| 46635 | Gospel Philosophy | J.H. Ward | BAJA | Teología popular |

### Escritos misionales y apologéticos

| # | Título | Autor | Prioridad | Notas |
|---|--------|-------|-----------|-------|
| 45846 | Letters Exhibiting Prominent Doctrines | Orson Spencer | BAJA | Apologética epistolar |
| 35554 | A Voice of Warning | Parley P. Pratt | MEDIA | Clásico misional, muy citado |
| 46243 | Divine Authority; Was Joseph Smith Sent of God? | Orson Pratt | BAJA | Apologética |
| 44907 | An Interesting Account of Several Remarkable Visions | Orson Pratt | MEDIA | Temprano relato de la Primera Visión |
| 45005 | Absurdities of Immaterialism | Orson Pratt | BAJA | Filosofía teológica |
| 46244 | The Kingdom of God, Part 1 | Orson Pratt | BAJA | Teología del reino |
| 46974 | Rays of Living Light | Charles W. Penrose | BAJA | Folletos misionales |
| 46617 | The Plan of Salvation | John Morgan | BAJA | Manual misional |

### Documentos históricos y discursos

| # | Título | Autor | Prioridad | Notas |
|---|--------|-------|-----------|-------|
| 45006 | General Smith's Views (Gobierno de EEUU) | Joseph Smith Jr. | MEDIA | Plataforma presidencial 1844 |
| 6720 | The Wentworth Letter | Joseph Smith Jr. | **ALTA** | Contiene Artículos de Fe originales |
| 54278 | Proclamation of the Twelve Apostles | Council of Q12 | ALTA | Documento fundacional 1845 |
| 46221 | Items on the Priesthood | John Taylor | MEDIA | Doctrina del sacerdocio |

### Perspectiva femenina SUD

| # | Título | Autor | Prioridad | Notas |
|---|--------|-------|-----------|-------|
| 54335 | The Women of Mormondom | Edward W. Tullidge | MEDIA | Historia colectiva de mujeres SUD |
| 50958 | Representative Women of Deseret | Augusta J. Crocheron | MEDIA | (también en biografías arriba) |
| 51097 | Heroines of "Mormondom" | Various | MEDIA | (también en biografías arriba) |

### Colecciones y miscelánea

| # | Título | Autor | Prioridad | Notas |
|---|--------|-------|-----------|-------|
| 60056 | Scrap Book of Mormon Literature (Vol. 1) | — | BAJA | Antología |
| 54298 | Scrap Book of Mormon Literature (Vol. 2) | — | BAJA | Antología |
| 51095 | Book of Mormon Stories No. 1 | George Q. Cannon | BAJA | Para niños |
| 49382 | The Life of Nephi, Son of Lehi | George Q. Cannon | MEDIA | Ficción/exégesis |
| 48517 | Mother Stories from the Book of Mormon | William A. Morton | BAJA | Para niños |
| 50029 | The Story of the Book of Mormon | — | BAJA | Resumen narrativo |
| 46601 | Gems for the Young Folks | Various | BAJA | Colección juvenil |
| 46733 | A String of Pearls | Various | BAJA | Colección devocional |
| 49830 | Treasures in Heaven | — | BAJA | Colección devocional |
| 50072 | Fragments of Experience | Various | BAJA | Colección miscelánea |
| 49327 | Labors in the Vineyard | Various | BAJA | Relatos misionales |
| 49362 | Helpful Visions | — | BAJA | Colección devocional |

### Ficción SUD

| # | Título | Autor | Prioridad | Notas |
|---|--------|-------|-----------|-------|
| 13756 | Story of Chester Lawrence | Nephi Anderson | BAJA | Novela SUD |
| 17249 | Added Upon | Nephi Anderson | BAJA | Novela teológica (plan de salvación) |
| 12684 | Dorian | Nephi Anderson | BAJA | Novela |
| 52552 | Venna Hastings: Eastern Mormon Convert | Julia Farr | BAJA | Novela |
| 50955 | The Cities of the Sun | Elizabeth Cannon Porter | BAJA | Ficción |
| 56685 | Mr. Durant of Salt Lake City | Ben. E. Rich | BAJA | Ficción |

### Perspectiva externa / crítica (authority=15-20)

| # | Título | Autor | Prioridad | Notas |
|---|--------|-------|-----------|-------|
| 2443 | The Story of the Mormons | William A. Linn | BAJA | (también en historia arriba) |
| 44414 | The Mormon Prophet and His Harem | C.V. Waite | BAJA | Anti-mormón, valor documental |
| 7066 | Under the Prophet in Utah | Frank J. Cannon | BAJA | Hijo de GQC, crítico; controversial |
| 14661 | Conditions in Utah | Thomas Kearns | BAJA | Informe político senatorial |
| 54079 | Sinners and Saints | Phil Robinson | BAJA | Relato de viajero |
| 36791 | The Mormon Puzzle | R.W. Beers | BAJA | Perspectiva externa |
| 17279 | The Mormon Prophet | L. Dougall | BAJA | Novela sobre JS (ficción externa) |
| 51096 | The Mormons (discurso) | Thomas L. Kane | MEDIA | Amigo de la Iglesia, perspectiva simpática |
| 35565 | The Mormons and the Theatre | John S. Lindsay | BAJA | Historia cultural |
| 23519 | The Mormon Menace (Confessions of J.D. Lee) | A.H. Lewis / J.D. Lee | BAJA | Mountain Meadows, controversial |
| 49432 | The Myth of the "Manuscript Found" | — | MEDIA | Refutación del origen Spaulding |

### Poesía

| # | Título | Autor | Prioridad | Notas |
|---|--------|-------|-----------|-------|
| 60077 | The Millennium, and Other Poems | Parley P. Pratt | BAJA | Poesía teológica |
| 37718 | Elias: An Epic of the Ages | Orson F. Whitney | BAJA | Poema épico, plan de salvación |

---

## Gutenberg Bookshelf — Fase 0 Analyses

### Essentials in Church History (Gutenberg #45054)

**Estado:** `researched` | authority=45 | Corpus path: `corpus/en/books/essentials-in-church-history/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Historia de la Iglesia en un solo volumen, desde la antigüedad
  del Evangelio hasta la administración de Heber J. Grant (~1922). Subtítulo:
  "A History of the Church from the Birth of Joseph Smith to the Present Time
  (1922), with Introductory Chapters on the Antiquity of the Gospel and the
  'Falling Away.'" 6 partes, 54 capítulos, ~675 páginas, 5 apéndices.

| Parte | Título | Capítulos | Cobertura |
|-------|--------|-----------|-----------|
| I | Introductory | 1-3 | Antigüedad del Evangelio, Apostasía, Reforma Protestante |
| II | Opening of the Dispensation | 4-14 | Restauración hasta ~1831 |
| III | Ohio and Missouri Period | 15-26 | Kirtland, Zion's Camp, expulsión de Missouri (~1831-1839) |
| IV | Nauvoo Period | 27-36 | Nauvoo, templo, martirio, sucesión (~1839-1846) |
| V | Settlement in Rocky Mountains | 37-48 | Éxodo, pioneros, Guerra de Utah, colonización (~1846-1877) |
| VI | Recent Development | 49-54 | Administraciones Taylor–Grant (~1877-1922) |

  Apéndices: organizaciones auxiliares, lista completa de AG, estacas de Sión,
  publicaciones de la Iglesia, bibliografía de autoridades. Ilustrado con
  retratos, escenas históricas, mapas (rutas de migración, Batallón Mormón).

- **¿Quién lo produjo?** Joseph Fielding Smith Jr. (1876-1972), apóstol
  (ordenado 1910) y recién nombrado Historiador y Registrador de la Iglesia
  (1921). Luego 10º Presidente de la Iglesia (1970-1972). Nieto de Hyrum
  Smith. Copyright: Heber J. Grant (Trustee-in-Trust). Publisher: Deseret
  News Press, Salt Lake City, 1922.
- **¿Cuándo?** 1ª edición: 1922. Al menos 27 ediciones/reimpresiones hasta
  1974. La edición Gutenberg es la de 1922 (dominio público), digitalizada
  por el Mormon Texts Project (2014). Ediciones posteriores extendieron la
  cobertura a presidentes subsiguientes — NO están en Gutenberg.
- **¿Para quién?** Explícitamente diseñado como volumen de lectura general Y
  como **libro de texto para quórumes del sacerdocio y escuelas de la Iglesia**.
  Fue EL texto estándar de historia de la Iglesia por décadas, usado en
  instrucción del sacerdocio y CES antes de ser reemplazado por "Church
  History in the Fulness of Times" (1989/2003) y luego "Saints" (2018+).
- **¿Cómo referenciado?** Ampliamente citado en historiografía SUD como
  historia semi-oficial. La Joseph Smith Foundation lo distribuye digitalmente.
  Harold B. Lee y otros líderes lo citaron como referencia doctrinal/histórica.
  Superseded en currículo actual pero sigue en bibliografías.
- **Relaciones KG — densidad extraordinaria:**
  - **Personas:** Todos los presidentes hasta Grant, Doce Apóstoles originales,
    familia Smith, Council of Fifty, antagonistas (Boggs, McKean), Batallón
    Mormón, pioneros, Oliver Cowdery, Martin Harris, David Whitmer, Sidney Rigdon
  - **Eventos:** Primera Visión, visitas de Moroni, traducción del LdM,
    restauración del sacerdocio, organización (1830), Campamento de Sión,
    dedicación Kirtland, persecuciones Missouri, Haun's Mill, Orden de
    Exterminio, fundación de Nauvoo, ordenanzas del templo, martirio,
    crisis de sucesión, éxodo, Batallón Mormón, trek pionero, Guerra de
    Utah (1857-58), Mountain Meadows, ferrocarril, legislación antipoligamia,
    Manifiesto
  - **Lugares:** Palmyra, Fayette, Colesville, Kirtland, Hiram, Independence,
    Far West, Adam-ondi-Ahman, Nauvoo, Carthage, Winter Quarters, Council
    Bluffs, Salt Lake Valley, toda la geografía de colonización de Utah
  - **Doctrinas:** Apostasía/Restauración (caps 1-4), sacerdocio, testigos
    del LdM, ordenanzas del templo, sucesión presidencial, recogimiento,
    teología de Sión
- **Consideraciones:**
  - Historiografía de 1922 — apologética, no crítica-moderna. No incorpora
    Joseph Smith Papers ni erudición post-1970.
  - Edición Gutenberg = solo 1922 (hasta administración Grant temprana).
  - Complementa Roberts HC: Smith es más conciso y doctrinal; Roberts más
    detallado y analítico.
  - Solo EN — nunca traducido oficialmente al español.
  - Los apéndices (listas de AG, estacas, publicaciones) son metadatos
    únicos para el KG no disponibles en otra fuente del corpus.

---

### History of the Prophet Joseph, by His Mother (Gutenberg #45619)

**Estado:** `researched` | authority=35 | Corpus path: `corpus/en/books/history-of-prophet-joseph-by-his-mother/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Memorias familiares / biografía de Joseph Smith Jr., dictadas
  por su madre Lucy Mack Smith. Única cuenta de primera persona de la vida
  de la familia Smith desde la perspectiva de un progenitor. 54 capítulos +
  apéndice (diarios y elegías de Don Carlos Smith).
  - Caps I-IX: genealogía Mack/Smith
  - Caps X-XVII: mudanzas y dificultades tempranas
  - Caps XVIII-XXVII: experiencias espirituales de Joseph, manuscrito del LdM
  - Caps XXVIII-XXXIV: Oliver Cowdery, traducción, organización de la Iglesia
  - Caps XXXV-LIV: misiones, persecuciones, martirio
- **¿Quién lo produjo?** Lucy Mack Smith (1775-1856), madre de Joseph Smith.
  Dictó las memorias a Martha Jane Knowlton Coray (amanuense) en Nauvoo,
  invierno 1844-1845. Howard Coray (esposo) compiló notas en dos borradores.
  **Edición Gutenberg (45619) = edición revisada de 1902**, NO la edición
  Orson Pratt de 1853. Título: "History of the Prophet Joseph by His Mother,
  Lucy Smith, as Revised by George A. Smith and Elias Smith." Revisores:
  George A. Smith (Historiador de la Iglesia, primo de JS Sr.) y Elias Smith
  (patriarca). Producida por Mormon Texts Project, mayo 2014.
- **¿Cuándo?** Historia textual compleja:
  - 1844-45: Lucy dicta en Nauvoo tras las muertes de Joseph, Hyrum y Samuel
  - 1853: Orson Pratt publica en Liverpool como *Biographical Sketches* —
    sin autorización de Brigham Young
  - 1865: BY suprime oficialmente la edición de 1853
  - 1856-66: George A. Smith y Elias Smith trabajan correcciones
  - 1901-03: Serializada en Improvement Era
  - **1902: Publicada como libro — esta es la edición Gutenberg**
  - 2001: Lavina Fielding Anderson publica *Lucy's Book* (edición crítica,
    Signature Books) — texto paralelo del manuscrito original de 1845
- **¿Para quién?** Familia y miembros SUD. La edición 1902 fue la versión
  autorizada por la Iglesia para consumo general.
- **¿Cómo referenciado?** Una de las fuentes primarias fundamentales para
  historia SUD temprana. Leonard Arrington: "informative, basically accurate,
  and extremely revealing." Jan Shipps: "of central importance in the Mormon
  historical corpus." 190+ de 200 nombres corroborados por fuentes
  independientes. Citada extensamente en *Saints*, manuales de seminario/
  instituto, *Rough Stone Rolling* (Bushman), y virtualmente todas las
  biografías de Joseph Smith. Joseph Smith Papers la trata como documento
  primario clave.
- **Relaciones KG — altísima densidad:**
  - **Personas:** Joseph Smith Jr., Joseph Smith Sr., Lucy Mack Smith, Hyrum,
    Samuel, Don Carlos, Alvin, William, Sophronia Smith; Solomon Mack
    (abuelo), familia Mack extendida; Emma Hale, Oliver Cowdery, Martin
    Harris, David Whitmer; Martha Jane Coray (amanuense)
  - **Eventos únicos (perspectiva materna):** cirugía de pierna de Joseph
    (infancia), Primera Visión (contexto familiar), visitas de Moroni,
    obtención de las planchas, pérdida de las 116 páginas, organización
    de la Iglesia, Kirtland, Campamento de Sión, Missouri, martirio
  - **Lugares:** Sharon VT, Tunbridge VT, Lebanon NH, Palmyra NY, Manchester
    NY, Harmony PA, Fayette NY, Kirtland OH, Far West MO, Nauvoo IL,
    Carthage IL
- **Consideraciones:**
  - **~14% del contenido original fue eliminado** en la revisión 1902.
    Material que BY consideró "erróneo" fue editado o suprimido — la
    revisión suavizó pasajes que conflictuaban con la narrativa de liderazgo
    de BY. Académicos prefieren *Lucy's Book* (2001) o transcripciones JSP.
  - Para el corpus, la edición 1902 sigue siendo enormemente valiosa —
    fue el texto estándar por más de un siglo y contiene la gran mayoría
    del contenido histórico.
  - Solo EN.

---

### Autobiography of Parley Parker Pratt (Gutenberg #44896)

**Estado:** `researched` | authority=40 | Corpus path: `corpus/en/books/autobiography-of-parley-p-pratt/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Autobiografía póstuma de Parley P. Pratt, uno de los primeros
  apóstoles. Título completo: *...Embracing His Life, Ministry and Travels,
  with Extracts, in Prose and Verse, from His Miscellaneous Writings.*
  54 capítulos + apéndice + genealogía, 502 páginas. Los últimos capítulos
  transicionan de narrativa a entradas de diario y cartas familiares.
  - Caps 1-6: infancia, juventud en Nueva York, conversión (1807-1830)
  - Caps 7-16: primeras misiones, Missouri, Zion's Camp, Kirtland
  - Caps 17-20: misión a Canadá (conversión de John Taylor), muerte de 1ª esposa
  - Caps 21-35: persecuciones Missouri, prisión Richmond/Liberty, escape
  - Caps 36-41: misión a Inglaterra, Millennial Star, emigración
  - Caps 42-45: martirio de JS, éxodo, Winter Quarters, Montañas Rocosas
  - Caps 46-50: Utah, misiones al Pacífico (California, Chile — 1er misionero
    en Sudamérica, 1851)
  - Caps 51-54: última misión, cartas, poema "My Fiftieth Year", respuesta
    de John Taylor
- **¿Quién lo produjo?** Parley Parker Pratt (1807-1857), apóstol original
  (ordenado 1835). Compilado por su hijo Parley P. Pratt Jr. desde "various
  forms of manuscript, some in book form, some in loose leaves, whilst others
  were extracts from the Millennial Star." Publicado por Russell Brothers,
  New York, 1874 (17 años después del asesinato de Pratt).
- **¿Cuándo?** Escrito durante su vida; últimos caps son diario de 1856-57.
  Asesinado 13 mayo 1857 por Hector McLean. Publicado 1874.
- **¿Para quién?** Audiencia SUD general. Sigue siendo uno de los textos SUD
  más leídos en el siglo XXI por su prosa accesible.
- **¿Cómo referenciado?** Descrito como **"possibly the most important [LDS]
  historical work written in the nineteenth century."** "Remains one of the
  most frequently read texts for Latter-day Saints even in the twenty-first
  century." Fuente primaria citada extensamente en manuales, academia y
  conferencia general. Artículo académico dedicado: R.A. Christmas, *Dialogue*
  vol. 1 no. 1 (1966).
- **Relaciones KG �� altísima densidad:**
  - **Personas:** Joseph Smith, Brigham Young, John Taylor (co-editor),
    Hyrum Smith, Sidney Rigdon, Orson Hyde, Orson Pratt (hermano), Hector
    McLean (asesino), Thankful Halsey (1ª esposa), Mary Ann Frost (2ª esposa)
  - **Eventos como testigo presencial:** conversión (1830), Zion's Camp (1834),
    persecuciones Missouri, Orden de Exterminio, Haun's Mill, prisión
    Richmond, escape de la prisión, templo Kirtland, misión a Inglaterra,
    Millennial Star, martirio (1844), éxodo, trek pionero, 1ª misión SUD
    a Sudamérica (Chile 1851)
  - **Lugares:** Burlington NY, Kirtland, Independence, Far West, Richmond MO,
    Nauvoo, Winter Quarters, SLC, San Francisco, Valparaíso Chile, Toronto,
    Preston/Manchester England, Van Buren AR
  - **Misiones:** Indios lamanitas (1830-31), Canadá (1836), Inglaterra
    (1839-42), Pacífico/Chile (1851), última misión al este (1856-57)
- **Consideraciones:**
  - Edición del hijo — no hay certeza de cuánto reorganizó u omitió.
  - Tratamiento evasivo del matrimonio plural — notable dado que su asesinato
    fue causado por su matrimonio con Eleanor McLean.
  - La autobiografía termina antes del asesinato (por razones obvias).
  - Gutenberg = edición original 1874 (sin las 700+ notas de la edición
    Proctor 2000, que es con copyright).

---

### Gospel Doctrine (Gutenberg #47109)

**Estado:** `researched` | authority=50 | Corpus path: `corpus/en/books/gospel-doctrine/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Antología de sermones y escritos de Joseph F. Smith organizada
  temáticamente en 26 capítulos: Truth, Eternal Nature, Revelation, Free
  Agency, God and Man, Mission of the Church, First Principles, Church and
  Man, Priesthood, Spiritual Gifts, Obedience, Prayer, Tithing/Poor/Industry,
  Temperance/Sabbath, Duties, Marriage/Home/Family, Amusements, Love Your
  Enemies, Education, Missionaries, False Teachings, Auxiliary Organizations,
  Political Government, Eternal Life/Salvation, Joseph Smith the Prophet,
  Personal Testimonies. NO es un libro escrito por JFS — es compilación
  de extractos de sermones publicados, agrupados por tema.
- **¿Quién lo produjo?** Joseph F. Smith (1838-1918), 6º presidente (1901-18).
  Compiladores: John A. Widtsoe (líder), Osborne J.P. Widtsoe, Albert E.
  Bowen, F.S. Harris, Joseph Quinney. Patrocinador: Lorenzo N. Stohl.
  Editor: Deseret News, SLC. Copyright: 1919 por Heber J. Grant.
- **¿Cuándo?** 1919 (un año después de la muerte de JFS). Múltiples
  reimpresiones; 12ª edición 1966. Sigue en catálogo de Deseret Book.
  Gutenberg release: oct 2014, producido por Mormon Texts Project.
- **¿Para quién?** Originalmente **libro de texto para quórumes del
  Sacerdocio de Melquisedec**, bajo iniciativa de David O. McKay. Con el
  tiempo se convirtió en referencia doctrinal general.
- **¿Cómo referenciado?** Clásico de la literatura SUD. Harold B. Lee:
  "When I want to seek for a more clear definition of doctrinal subjects,
  I have usually turned to the writings and sermons of President Joseph F.
  Smith." El manual *Teachings of Presidents: Joseph F. Smith* (1998)
  toma extensamente de este libro. 961 descargas/mes en Gutenberg.
- **Doctrinas clave:**
  - **Visión de la Redención de los Muertos** (Cap XXIV) — texto fuente
    pre-canonización de lo que luego fue D&C 138 (canonizado 1976/1979).
    Valor intertextual alto.
  - Preexistencia, inmortalidad, vida después de la muerte (Caps II, XXIV)
  - Sacerdocio: autoridad, organización, llaves (Cap IX)
  - Primeros principios: fe, arrepentimiento, bautismo, EG (Cap VII)
  - Libre albedrío (Cap IV), revelación (Caps III, X)
  - Matrimonio y familia (Cap XVI) — doctrina pre-Proclamación
  - El Profeta Joseph Smith — testimonios de nieto de Hyrum (Cap XXV)
  - Diezmo, Palabra de Sabiduría, día de reposo (Caps XIII, XIV)
  - Gobierno político: relación Iglesia-Estado (Cap XXIII)
- **Relaciones KG:** Alta densidad — JFS conecta con JS Sr., Hyrum,
  BY, John Taylor, Wilford Woodruff, Lorenzo Snow (todos presidentes que
  conoció). También David O. McKay, John A. Widtsoe, Heber J. Grant.
- **Consideraciones:**
  - D&C 138 pre-canonización — el texto de la Visión es la versión
    publicada antes de entrar al canon. Intertextualidad valiosa.
  - No duplica el manual de 1998 (Teachings of Presidents) — Gospel Doctrine
    es la fuente completa y no editada; el manual es selección oficial.
  - Solo EN — el manual Teachings of Presidents sí está en español.

---

### Life of Heber C. Kimball (Gutenberg #35333)

**Estado:** `researched` | authority=40 | Corpus path: `corpus/en/books/life-of-heber-c-kimball/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Biografía completa en 68 capítulos + apéndice, 515 páginas.
  Título: *Life of Heber C. Kimball, an Apostle: The Father and Founder of
  the British Mission.* El autor deja al sujeto "speak for himself" —
  incorpora extensos extractos de diarios y cartas verbatim, haciendo que
  sea simultáneamente biografía y compilación de fuentes primarias.
  - Caps I-X: vida temprana, matrimonio con Vilate Murray, bautismo, Kirtland
  - Caps XI-XX: primera misión de los Doce, Kirtland Temple, British Mission
  - Caps XXI-XXX: 1ª Misión Británica (1837-38), conversiones en Preston
  - Caps XXXI-XL: persecuciones Missouri, Nauvoo, 2ª Misión Británica
  - Caps XLI-L: conferencia de Londres, trabajo apostólico, templo Nauvoo
  - Caps LI-LX: éxodo, trek pionero 1847, colonización
  - Caps LXI-LXVIII: historia familiar, anécdotas, muerte de Vilate, muerte
    de Heber (1868)
- **¿Quién lo produjo?** Orson Ferguson Whitney (1855-1931), **nieto** de
  Kimball (hijo de Helen Mar Kimball Whitney). Whitney luego fue **apóstol**
  (ordenado 1906). También autor de la *History of Utah* (4 vols). Publicado
  por la familia Kimball, impreso en Juvenile Instructor Office, 1888.
  Originado en reunión familiar Kimball (14 jun 1887).
- **¿Cuándo?** 1888. Gutenberg release: feb 2011, Mormon Texts Project.
- **¿Para quién?** Miembros SUD y familia Kimball. Estilo devocional-
  hagiográfico típico del siglo XIX. Goodreads 4.29/5 (194 ratings).
- **¿Cómo referenciado?** Fue LA biografía de Kimball por casi un siglo
  (1888-1981). Superseded como biografía académica definitiva por Stanley
  B. Kimball, *Heber C. Kimball: Mormon Patriarch and Pioneer* (U. of
  Illinois Press, 1981). Sigue citada como fuente primaria por las
  transcripciones verbatim de diarios.
- **Relaciones KG — alta densidad (68 caps, vida completa):**
  - **Personas:** Heber C. Kimball (sujeto), Brigham Young (amigo de toda
    la vida), Joseph Smith, Vilate Murray Kimball, Helen Mar Kimball,
    Orson F. Whitney (autor/nieto), Willard Richards, Orson Hyde, Parley
    P. Pratt, John Taylor
  - **Eventos:** 1ª y 2ª Misión Británica, dedicación Kirtland, persecuciones
    Missouri, Nauvoo y templo, revelación del matrimonio celestial, éxodo,
    trek pionero 1847, colonización
  - **Lugares:** Kirtland, Preston (Inglaterra), Londres, Far West, Nauvoo,
    Winter Quarters, Salt Lake Valley

| Relación | from | to |
|----------|------|----|
| `FIRST_COUNSELOR_TO` | Heber C. Kimball | Brigham Young |
| `FOUNDED` | Heber C. Kimball | British Mission |
| `GRANDSON_OF` | Orson F. Whitney | Heber C. Kimball |
| `MARRIED_TO` | Heber C. Kimball | Vilate Murray |

- **Consideraciones:**
  - 68 capítulos — libro grande, ~150-200 chunks estimados.
  - Prosa victoriana densa — funcionalmente correcta para el chunker pero
    estilísticamente diferente del material moderno.
  - Transcripciones de diario embebidas sin delimitadores claros.
  - **Complementa #47519** (Kimball's Journal) — ingestar juntos maximiza
    cross-references.
  - Sesgo hagiográfico — escrito por nieto devoto para audiencia familiar.

---

### The Government of God (Gutenberg #44941)

**Estado:** `researched` | authority=40 | Corpus path: `corpus/en/books/government-of-god/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Tratado de teología política en 12 capítulos (~200 páginas).
  Contrasta el gobierno de Dios (orden, armonía) con los gobiernos humanos
  (confusión, desigualdad), argumentando que solo el reino literal de Cristo
  resolverá los males del mundo. Estructura progresiva: diagnóstico (caps 1-3)
  → naturaleza del hombre (4-6) → gobierno divino en la historia (7-9) →
  reino literal de Cristo (10-12).

| Cap | Título |
|-----|--------|
| I | The Wisdom, Order, and Harmony of the Government of God |
| II | The Government of Man |
| III | On the Incompetency of the Means Made Use of by Man to Regenerate the World |
| IV | What Is Man? What Is His Destiny and Relationship to God? |
| V | The Object of Man's Existence on the Earth |
| VI | Man's Accountability to God |
| VII | The Lord's Course in the Moral Government of the World |
| VIII | Whose Right Is It to Govern the World? |
| IX | Will Man Always Be Permitted to Usurp Authority Over Men? |
| X | Will God's Kingdom Be a Literal or a Spiritual Kingdom? |
| XI | The Establishment of the Kingdom of God upon the Earth |
| XII | The Effects of the Establishment of Christ's Kingdom |

- **¿Quién lo produjo?** John Taylor (1808-1887), apóstol al momento de
  escribir, luego 3er presidente de la Iglesia (1880-87). Publicado por
  S.W. Richards, Liverpool, agosto 1852. Tiraje: 5,000 copias. Editor:
  James Linforth. Impreso por W. Bowden, Londres.
- **¿Cuándo?** Escrito 1849-1852 durante la misión de Taylor en Francia y
  Alemania. Publicado agosto 1852. Contexto: revoluciones europeas fallidas
  de 1848 + Taylor era miembro del Council of Fifty de Joseph Smith.
  Gutenberg release: feb 2014, Mormon Texts Project.
- **¿Para quién?** Público general europeo + investigadores. Tono accesible,
  no técnico. Propósito parcial: recaudar fondos para la Misión Francesa.
- **¿Cómo referenciado?** B.H. Roberts lo llamó **"Elder Taylor's
  masterpiece"** y "a work which is sufficient at once to establish both his
  literary ability and his power as a moral philosopher" (en *Life of John
  Taylor*, ya en corpus). El manual *Teachings of Presidents: John Taylor*
  (cap 13) extrae ideas de este libro. BYU RSC lo analiza en estudios
  sobre teología política mormona. Es la articulación más sistemática de
  la doctrina del reino de Dios en la literatura SUD del siglo XIX.
- **Doctrinas clave:**
  - **Teocracia / Reino literal de Dios** — no metafórico, gobierno literal
    en la tierra durante el Milenio (Cap X argumenta contra interpretaciones
    espiritualizantes)
  - **Incompetencia de gobiernos humanos** (Caps 2-3) — crítica sistemática
  - **Soberanía divina** (Cap 8) — derecho inherente de Dios a gobernar
  - **Accountability ante Dios** (Cap 6) — gobernantes rinden cuentas
  - **Destino del hombre** (Caps 4-5) — propósito divino, trasciende mortalidad
  - **Efectos del reino milenial** (Cap 12) — paz, justicia, fin de pobreza
- **Relaciones KG:**

| Relación | from | to |
|----------|------|----|
| `AUTHORED` | John Taylor | The Government of God |
| `TEACHES` | The Government of God | Kingdom of God |
| `TEACHES` | The Government of God | Theocracy |
| `TEACHES` | The Government of God | Millennium |
| `MEMBER_OF` | John Taylor | Council of Fifty |
| `PUBLISHED_IN` | The Government of God | Liverpool |

- **Consideraciones:**
  - **Teocracia es doctrina sensible** — Taylor argumenta que todos los
    gobiernos serán destruidos y reemplazados. Matiza con obediencia a leyes
    civiles, pero la tesis central puede malinterpretarse fuera de contexto.
  - **Council of Fifty** — la versión pública y articulada de ideas exploradas
    en ese consejo secreto.
  - No menciona poligamia (a pesar de publicarse el mismo año que el anuncio
    público de 1852).
  - 12 capítulos — obra compacta, buen ratio valor/tamaño.

---

### Leaves from My Journal (Gutenberg #46028)

**Estado:** `researched` | authority=40 | Corpus path: `corpus/en/books/leaves-from-my-journal/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Autobiografía abreviada en 28 capítulos extraída de los
  diarios personales de Wilford Woodruff. 3er libro de la Faith-Promoting
  Series. Cubre desde infancia en Connecticut (~1807) hasta experiencias
  espirituales tardías. Narrativa en primera persona con relatos de misiones,
  milagros, encuentros con Joseph Smith, y experiencias espirituales.
  ~100 páginas originales.
- **¿Quién lo produjo?** Wilford Woodruff (autor). Serie editada por
  George Q. Cannon. Publicado por Juvenile Instructor Office, SLC, 1882.
- **¿Cuándo?** 1882 (2ª edición en Gutenberg; 1ª vendió 4,000+ copias).
- **¿Para quién?** Juventud SUD — Faith-Promoting Series "designed for the
  instruction and encouragement of young Latter-day Saints."
- **¿Cómo referenciado?** Ampliamente citado. Los diarios de Woodruff son
  una de las fuentes primarias más importantes ("his elaborate journal has
  always been one of the principal sources from which the Church history has
  been compiled"). El Wilford Woodruff Papers Project cataloga esta obra
  como documento A-23.
- **Relaciones KG:**
  - **Personas:** Joseph Smith, Brigham Young, Robert Mason (profeta local
    de Connecticut — figura única, casi no aparece en otras fuentes),
    David W. Patten, Warren Parrish, George Q. Cannon
  - **Eventos:** Campamento de Sión (1834), misiones al sur de EE.UU.,
    Fox Islands (Maine), investiduras, bautismos
  - **Lugares:** Connecticut, Kirtland, Missouri, Arkansas, Tennessee,
    Fox Islands, Memphis
- **Consideraciones:**
  - Libro breve (28 caps cortos) — buen ratio valor/tamaño.
  - Títulos de capítulo muy largos y descriptivos — chapter_pattern debe
    usar "CHAPTER [ROMAN]" sin los subtítulos.
  - Devocional, no riguroso históricamente.
  - Complementa #47703 (biografía completa por Cowley) — este aporta la
    voz en primera persona y el episodio único de Robert Mason.

---

### Wilford Woodruff, Fourth President (Gutenberg #47703)

**Estado:** `researched` | authority=40 | Corpus path: `corpus/en/books/wilford-woodruff-fourth-president/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Biografía exhaustiva en 57 capítulos + 4 apéndices. Subtítulo:
  "History of His Life and Labors as Recorded in His Daily Journals." Cubre
  vida completa: nacimiento (1807), genealogía, accidentes juveniles,
  conversión, Campamento de Sión, misiones (sur EE.UU., Fox Islands, Gran
  Bretaña), Nauvoo, martirio, éxodo pionero, vida en Utah, presidencia,
  el Manifiesto (1890), dedicación del Templo de Salt Lake (1893), muerte
  (1898). Apéndices sobre Sidney Rigdon, discurso a santos británicos,
  tormenta en Lake Michigan, racionalidad de la Expiación. Estadísticas:
  172,369 millas viajadas, 7,655 reuniones, 3,526 discursos.
- **¿Quién lo produjo?** Matthias F. Cowley (editor/compilador), apóstol
  ordenado por el propio Woodruff en 1897. Publicado en SLC, 1909. Nota:
  Cowley tuvo sacerdocio suspendido en 1911 (matrimonios plurales post-
  Manifiesto) y restaurado en 1936 — no fue excomulgado; la disciplina
  fue posterior a la publicación.
- **¿Cuándo?** 1909 (11 años tras muerte de Woodruff). Gutenberg: MTP.
- **¿Para quién?** Miembros SUD. Biografía autorizada — LA referencia
  biográfica estándar de Woodruff por más de un siglo. Cowley describió a
  Woodruff como "perhaps, the best chronicler of events in all the history
  of the Church."
- **¿Cómo referenciado?** Obra fundamental. Citada extensamente en obras
  históricas SUD. La Wilford Woodruff Papers Foundation la usa como fuente
  de referencia. Es para Woodruff lo que la HC es para Joseph Smith.
- **Relaciones KG — muy alta densidad (91 años documentados):**
  - **Personas:** Joseph Smith, Hyrum Smith, Brigham Young, John Taylor,
    Sidney Rigdon, Heber C. Kimball, Parley P. Pratt, Orson Pratt, esposas
  - **Eventos:** Campamento de Sión (1834), misión a GB (1840-41, 1844-46),
    martirio (1844), sucesión, partida pioneros (1847), dedicación St.
    George, muerte de BY (1877), Manifiesto (1890), dedicación SLC Temple
    (1893)
  - **Lugares:** Connecticut, Kirtland, Nauvoo, Missouri, Fox Islands, GB,
    Winter Quarters, SLC, Rich County, St. George, Arizona
  - Apéndice A sobre Sidney Rigdon — relaciones únicas sobre crisis de
    sucesión
- **Consideraciones:**
  - 57 capítulos + apéndices — libro extenso, ingesta significativa.
  - Cowley omite y edita material — no es transcripción literal.
  - Apéndice y material suplementario (esposas, hijos) requieren atención
    especial en parsing.
  - **Prioridad sobre #46028:** subsume la mayoría del contenido de *Leaves*
    con mucho más detalle. Idealmente ambos — *Leaves* aporta la voz directa.
  - Ingestar juntos como batch.

---

### President Heber C. Kimball's Journal (Gutenberg #47519)

**Estado:** `researched` | authority=40 | Corpus path: `corpus/en/books/heber-c-kimball-journal/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Seventh Book of the Faith-Promoting Series. Memoir/journal
  covering Heber C. Kimball's mission to England (1837-1838) and subsequent
  events in Missouri and Illinois through 1839. 17 chapters: Ch. I-IX cover
  the first LDS mission to England (June 1837 – April 1838); Ch. X-XIV cover
  Missouri persecutions, Far West siege, and expulsion; Ch. XV-XVII cover
  the second mission departure and supplementary letters. Not a raw diary —
  Ch. I-X were dictated from memory to Robert B. Thompson in Nauvoo (1840)
  and published as a pamphlet; Ch. XI-XVII were compiled posthumously by his
  daughter Helen Mar Whitney from manuscript sources.
- **¿Quién lo produjo?** Heber C. Kimball (1801-1868), original Apostle and
  First Presidency counselor. Edited by George C. Lambert (series editor).
  Published by the Juvenile Instructor Office, Salt Lake City, 1882.
- **¿Cuándo?** Events: 1837-1839. First publication (pamphlet): 1840 (Nauvoo).
  This edition: 1882. Gutenberg release: Dec 3, 2014.
- **¿Para quién?** "Designed for the Instruction and Encouragement of Young
  Latter-day Saints" — the Faith-Promoting Series was Sunday School youth
  curriculum material. Accessible, devotional tone.
- **¿Cómo referenciado?** Widely cited as a primary source for the 1837
  British Mission — in some cases the only contemporary account of events.
  Referenced in Church manuals (Lesson 15 of LDS History 1815-1846 Teacher
  Material). Superseded for scholarly purposes by Stanley Kimball's critical
  edition *On the Potter's Wheel: The Diaries of Heber C. Kimball* (1987),
  and by Orson F. Whitney's *Life of Heber C. Kimball* (Gutenberg #35333)
  which draws heavily on these same sources.
- **Relaciones KG clave:**

| Entidad | Tipo | Relación |
|---------|------|----------|
| Heber C. Kimball | person | `AUTHORED_BY` — author |
| Brigham Young | person | Traveling companion, fellow apostle |
| Orson Hyde | person | Co-missionary to England |
| Joseph Fielding | person | Co-missionary to England |
| Willard Richards | person | Converted in England, baptized by Kimball |
| Joseph Smith | person | Called Kimball to mission; imprisoned at Far West |
| Helen Mar Whitney | person | Daughter, compiled Ch. XI-XVII |
| George C. Lambert | person | Series editor |
| Robert B. Thompson | person | Scribe for original 1840 dictation |
| Preston, England | place | First LDS preaching location in England |
| Liverpool | place | Port of departure/arrival |
| Far West, Missouri | place | Siege and betrayal (Ch. XI) |
| Chatburn / Downham | place | Sites of extraordinary conversion success |
| British Mission (1837) | event | First LDS mission to England |
| Battle of Crooked River | event | Ch. X |
| Missouri Expulsion | event | Ch. XII-XIII |

- **Consideraciones:**
  - **Not a raw diary** — dictated memoir (Ch. I-X) and posthumous compilation
    (Ch. XI-XVII). Lacks the immediacy of a daily journal; memory-based
    accounts may conflate or idealize events.
  - **Faith-Promoting editorial lens** — the series was devotional youth
    literature; tone is inspirational rather than critical-historical.
  - **Complements Gutenberg #35333** — Whitney's *Life of Heber C. Kimball*
    is the full biography that draws on this journal plus other sources.
    Ingesting both creates rich cross-reference opportunities.
  - **Kimball was barely literate** — his diaries have unique spelling and
    grammar; the 1882 edition is editorially polished.
  - **KG density:** High for British Mission events and Missouri persecutions.
    Many entities already in gazetteers from History of the Church volumes.

---

### William Clayton's Journal (Gutenberg #45051)

**Estado:** `researched` | authority=40 | Corpus path: `corpus/en/books/william-clayton-journal/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Daily record of the Mormon pioneer exodus from Nauvoo, Illinois
  to the Salt Lake Valley. Covers February 1846 through October 1847.
  Organized chronologically by daily entries. Documents the Iowa crossing
  (Feb-June 1846), Winter Quarters (1846-47), and the vanguard pioneer
  company trek (April-October 1847). Clayton meticulously recorded distances
  traveled, weather, geography, wildlife, camp organization, and social
  dynamics. This is the 1921 edition — the first published version, covering
  only the pioneer trek journal. Clayton kept other journals (Nauvoo diaries
  1842-1846) that are NOT included in this edition.
- **¿Quién lo produjo?** William Clayton (1814-1879), English convert,
  secretary to Joseph Smith (from Feb 1842), scribe, record-keeper. Edited
  by Lawrence Clayton (grandson, trustee of the Clayton Family Association).
  Introduction by Levi Edgar Young (of the First Council of the Seventy).
  Produced electronically by the Mormon Texts Project.
- **¿Cuándo?** Events: Feb 1846 – Oct 1847. Published: 1921 by the Clayton
  Family Association (Salt Lake City). Gutenberg release: March 2, 2014.
  Editor acknowledged it was a somewhat hasty first edition prepared for
  family distribution on Clayton's birthday (July 17).
- **¿Para quién?** Originally for Clayton Family Association members and those
  interested in pioneer-era Western history. Now a standard primary source
  for LDS historians and general students of the westward migration.
- **¿Cómo referenciado?** One of the most important primary sources for the
  1847 pioneer trek. Cited extensively in LDS scholarship. Clayton's Nauvoo
  journals (NOT in this edition) were used as a source for Joseph Smith's
  History of the Church and for D&C 132 (Clayton was the scribe when Joseph
  Smith dictated the revelation on plural marriage, July 12, 1843). The
  complete journals were published as *An Intimate Chronicle: The Journals
  of William Clayton* (ed. George D. Smith, Signature Books, 1991/1995) —
  that edition covers 1840-1879 and reveals ~50% of the pioneer journal was
  omitted or condensed in the 1921 family edition. A full critical edition
  of the Nauvoo journals is planned by Joseph Smith Papers editors (Yale
  University Press, expected ~2026).
- **Relaciones KG clave:**

| Entidad | Tipo | Relación |
|---------|------|----------|
| William Clayton | person | `AUTHORED_BY` — author |
| Brigham Young | person | Appointed Clayton as company historian |
| Joseph Smith | person | Clayton's employer/prophet (Nauvoo period, pre-journal) |
| Heber C. Kimball | person | Fellow pioneer in vanguard company |
| Levi Edgar Young | person | Wrote introduction |
| Lawrence Clayton | person | Editor (grandson) |
| Nauvoo, Illinois | place | Point of departure |
| Winter Quarters | place | Winter camp 1846-47 |
| Salt Lake Valley | place | Destination, arrival July 1847 |
| Council Bluffs / Kanesville | place | Staging area |
| "Come, Come, Ye Saints" | work | Hymn written by Clayton, April 1846, during Iowa crossing |
| Pioneer Odometer / Roadometer | object | Designed by Clayton, first used May 12, 1847 |
| Latter-Day Saints' Emigrants' Guide | work | Published by Clayton after trek, based on odometer data |
| Council of Fifty | organization | Clayton was secretary (Nauvoo period) |
| Pioneer Trek 1847 | event | Core subject of the journal |
| D&C 132 | scripture | Clayton was scribe (Nauvoo, not in this journal) |

- **Consideraciones:**
  - **1921 family edition is incomplete** — George D. Smith's collation shows
    ~50% of entries were condensed or omitted. The family may have removed
    sensitive content (polygamy references, internal conflicts). For corpus
    purposes, this is still a valuable primary source but users should be
    aware it is not the full text.
  - **Pioneer journal only** — Clayton's more historically explosive Nauvoo
    diaries (1842-1846), which document Joseph Smith's personal life,
    polygamy, the Council of Fifty, and temple ordinances, are NOT in this
    edition. Those are in *An Intimate Chronicle* (copyrighted, not available).
  - **Unique historical contributions:** Clayton invented the pioneer
    odometer (roadometer) and wrote "Come, Come, Ye Saints" — both documented
    in this journal. His distance measurements became the basis for the
    *Emigrants' Guide*.
  - **Clayton as bureaucrat, not leader** — his perspective is that of a
    "faithful follower and veritable workhorse," providing ground-level
    detail that leaders' accounts often lack.
  - **KG density:** Very high for pioneer trek entities (places, distances,
    dates, camp dynamics). Moderate overlap with other pioneer narratives
    already in corpus.

---

### Biography and Family Record of Lorenzo Snow (Gutenberg #47708)

**Estado:** `backlog` — requiere script Gutenberg | authority=40 | Corpus path: `corpus/en/biographies/lorenzo-snow-biography/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Biografía de Lorenzo Snow (1814–1901), quinto presidente de
  la Iglesia, escrita y compilada por su hermana Eliza R. Snow Smith.
  63 capítulos (numerados en romano I–LXIII) + genealogía familiar + 14
  cartas de Lorenzo desde su misión en Palestina. Subtítulo completo: "One
  of the Twelve Apostles of the Church of Jesus Christ of Latter-day Saints."
  Cubre desde el nacimiento y linaje familiar, conversión, misiones
  (Inglaterra, Italia, Hawái, Palestina), apostolado, vida en Utah, y
  registro genealógico extenso de esposas, hijos y nietos. ~200K palabras.
- **¿Quién lo produjo?** Eliza R. Snow Smith (1804–1887). Segunda presidenta
  general de la Sociedad de Socorro (1880–1887), poetisa prolífica (~500
  poemas, incluyendo "Oh mi Padre"/"O My Father"), esposa plural de Joseph
  Smith (sellada en junio de 1842) y luego de Brigham Young. Una de las
  mujeres más influyentes del mormonismo del siglo XIX. Publicado por
  Deseret News Company, Salt Lake City, 1884.
- **¿Cuándo?** 1884, cuando Lorenzo tenía 70 años y era apóstol (aún no
  presidente — asumió en 1898). Eliza murió en 1887, tres años después
  de la publicación.
- **¿Para quién?** Familia Snow y miembros SUD. El prólogo indica que fue
  concebida como "tribute of sisterly affection" y "family Memorial" para
  ser "handed down in lineal descent from generation to generation."
- **¿Cómo referenciado?** Fuente primaria ampliamente citada en estudios
  sobre Lorenzo Snow. Disponible en Archive.org, Wikisource, HathiTrust,
  Joseph Smith Foundation. Es la principal fuente biográfica sobre Lorenzo
  Snow anterior al siglo XX. Menos conocida que la autobiografía de Parley
  P. Pratt pero igualmente valiosa como fuente primaria.
- **Relaciones KG — alta densidad:**
  - **Personas:** Lorenzo Snow, Eliza R. Snow, Oliver Snow (padre),
    Rosetta Snow (madre), Brigham Young, Joseph Smith, David W. Patten,
    Heber C. Kimball, Franklin D. Richards, Warren Parrish (apostasía),
    y toda la familia Snow extendida (cap. LXIII)
  - **Eventos:** Conversión en Kirtland, Gran Apostasía (1837-38, cap. IV —
    "disaffection in every Quorum, pride and speculation, apostates
    claiming the Temple, Warren Parrish as ringleader"), misión a
    Inglaterra, apertura de la misión en Italia, misión a Palestina,
    migración pionera, cooperativa de Brigham City
  - **Lugares:** Mantua (Ohio), Kirtland, Nauvoo, Salt Lake City, Italia
    (Piamonte), Palestina/Tierra Santa, Hawái, Brigham City, Oberlin
    College (educación pre-conversión)
  - **Relaciones familiares:** Cap. LXIII contiene registro genealógico
    extenso — esposas, hijos, nietos, yernos/nueras, hijos de Mary
    Adaline por primer matrimonio — fuente rica para edges `FAMILY_OF`,
    `MARRIED_TO`, `PARENT_OF`

**Valor KG único:**

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `SIBLING_OF` | Eliza R. Snow | Lorenzo Snow | Biográfico — hermana mayor |
| `MARRIED_TO` | Eliza R. Snow | Joseph Smith | Cap. biográfico — sellada 1842 |
| `MARRIED_TO` | Eliza R. Snow | Brigham Young | Post-martirio |
| `MISSION_TO` | Lorenzo Snow | Italy | Primera misión SUD a Italia (Piamonte) |
| `MISSION_TO` | Lorenzo Snow | Palestine | 14 cartas en apéndice |
| `MISSION_TO` | Lorenzo Snow | Hawaii | Misión 1864, ~3 meses |
| `PRESIDED_OVER` | Lorenzo Snow | Brigham City | Comunidad cooperativa modelo |
| `CONVERTED_BY` | Lorenzo Snow | David W. Patten | Cap. I — primer contacto con el evangelio |
| `STUDIED_AT` | Lorenzo Snow | Oberlin College | Cap. I — estudios pre-conversión |
| `AUTHORED` | Eliza R. Snow | "O My Father" | Contexto biográfico de la poetisa |

**Entidades nuevas para gazetteer:** Oliver Snow, Rosetta Snow, Brigham City
(como comunidad cooperativa), Warren Parrish (si no existe)

**Consideraciones:**
- **Perspectiva:** 100% interna/devocional. Escrita por hermana del sujeto,
  líder prominente SUD. Tono hagiográfico — presenta a Lorenzo como modelo
  de virtud y fe. No hay pretensión de objetividad: es un tributo familiar.
- **Authority override:** authority=40 — biografía por figura prominente SUD,
  publicada por Deseret News (imprenta oficial de la Iglesia). No es manual
  ni escritura, pero es fuente primaria de alto valor histórico.
- **Estructura para parser:** 63 capítulos en romano (I–LXIII) + "Brief
  Biography" + "Fourteen Letters" (Palestina). El skill `/gutenberg`
  debería manejar la división por capítulos. Las cartas van como capítulos
  adicionales o como apéndice.
- **Valor diferencial vs. corpus existente:** Única biografía en el corpus
  escrita por una mujer sobre un profeta. Perspectiva femenina SUD del
  siglo XIX. Complementa las conferencias de Lorenzo Snow (ya en corpus
  vía General Conference) con contexto biográfico y familiar.

---

### The Story of the Mormons, from the Date of Their Origin to the Year 1901 (Gutenberg #2443)

**Estado:** `backlog` — requiere script Gutenberg | authority=20 | Corpus path: `corpus/en/books/story-of-the-mormons/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Historia comprensiva del movimiento mormón desde sus orígenes
  hasta 1901. 637 páginas (xxv + 637 p.), organizada en 6 "Books" con
  ~54 capítulos totales:
  - **Book I — The Mormon Origin** (7 caps): familia Smith, money-digging,
    anuncio de la "Golden Bible", diferentes relatos de la revelación,
    traducción y publicación, doctrinas y gobierno eclesiástico
  - **Book II — In Ohio** (6 caps): primeros conversos en Kirtland, dones
    de lenguas y milagros, crecimiento, empresas comerciales de Smith,
    últimos días en Kirtland
  - **Book III — In Missouri** (6 caps): asentamiento en Sión, primera
    visita de Smith a Missouri, expulsión de Jackson County, Ejército de
    Sión, condados de Clay/Caldwell/Daviess, danitas y diezmo
  - **Book IV — In Illinois** (15 caps): recepción, asentamiento de Nauvoo,
    proselitismo extranjero, gobierno municipal, política, candidatura
    presidencial de Smith, condiciones sociales, ruptura con Bennett y
    Higbee, institución de la poligamia, anuncio público de la doctrina,
    supresión del Expositor, levantamiento, arresto y asesinato del profeta
  - **Book V — The Migration to Utah** (~8 caps): preparativos para la
    marcha, del Mississippi al Missouri, Batallón Mormón, campamentos en
    el Missouri, viaje pionero, llegada al Valle de Salt Lake, compañías
    posteriores
  - **Book VI — In Utah** (~12 caps): fundación de SLC, progreso del
    asentamiento, inmigración extranjera, tragedia de los carros de mano,
    historia política temprana, conflictos con el gobierno federal, fin
    de la poligamia, statehood
  Incluye mapas e ilustraciones en la edición original.
- **¿Quién lo produjo?** William Alexander Linn (1846–1917). Periodista
  estadounidense, graduado de Phillips Academy (Andover) y Yale (1868,
  class poet). Staff del New York Tribune, luego managing editor del New
  York Evening Post (1891–1900) — considerado "almost unique in the
  journalism of that time" por la fiabilidad de su trabajo. Se retiró
  del periodismo en 1900 para dedicarse a la escritura. También publicó
  "Horace Greeley, Founder and Editor of the New York Tribune" (1903).
  Admitido al bar de Nueva York en 1883. No era miembro SUD. Publicado
  por Macmillan, New York, 1902.
- **¿Cuándo?** 1902, un año después de la muerte de Lorenzo Snow y el
  inicio de la presidencia de Joseph F. Smith. Cubre hasta el statehood
  de Utah (1896) y el Manifiesto (1890).
- **¿Para quién?** Público general estadounidense educado. Linn buscaba
  presentar una "consecutive history" secular, basada mayormente en fuentes
  mormonas primarias pero filtrada por su perspectiva periodística.
- **¿Cómo referenciado?** Considerada una de las primeras historias serias
  del mormonismo por un no-miembro. La Millennial Star (reseña moderna)
  la describe como "the first attempt to seriously consider the Mormon
  religion and culture" desde fuera. Todavía citada en bibliografías de
  Mormon studies como referencia de época. Sin embargo, la recepción es
  mixta: Linn era consciente de que fuentes anti-mormonas exageran, pero
  no logró mantener distancia crítica consistente — terminó aceptando
  demasiadas fuentes hostiles al pie de la letra. El tono es "clearly
  quite hostile to the church" aunque no es panfletario.
- **Relaciones KG — altísima densidad (historia completa):**
  - **Personas:** Joseph Smith Sr., Joseph Smith Jr., Brigham Young, Sidney
    Rigdon, Oliver Cowdery, Martin Harris, Parley P. Pratt, Orson Pratt,
    John C. Bennett, Lilburn Boggs, Thomas L. Kane, John Taylor, Wilford
    Woodruff, Lorenzo Snow, Joseph F. Smith, Warren Parrish, William Law
  - **Eventos:** Primera Visión (versión crítica), traducción del Libro de
    Mormón, money-digging, organización de la Iglesia, Ejército de Sión,
    expulsión de Missouri, Orden de Exterminio, fundación de Nauvoo,
    candidatura presidencial de Smith 1844, destrucción del Nauvoo
    Expositor, martirio, migración pionera, Batallón Mormón, tragedia
    de los carros de mano, Guerra de Utah (1857), Mountain Meadows,
    Manifiesto de 1890, statehood de Utah 1896
  - **Lugares:** Palmyra, Fayette, Kirtland, Independence, Far West,
    Adam-ondi-Ahman, Haun's Mill, Nauvoo, Council Bluffs, Winter Quarters,
    Salt Lake City, St. George, Camp Floyd
  - **Temas doctrinales (perspectiva externa):** poligamia (extenso),
    gobierno teocrático, diezmo, danitas, bautismo por los muertos,
    endowment, profecía y revelación

**Valor KG único:**

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `NARRATES_EVENT` | Linn (obra) | Expulsion from Jackson County | Book III |
| `NARRATES_EVENT` | Linn (obra) | Zion's Camp (Army of Zion) | Book III |
| `NARRATES_EVENT` | Linn (obra) | Danite organization | Book III — perspectiva externa detallada |
| `NARRATES_EVENT` | Linn (obra) | Smith presidential campaign 1844 | Book IV |
| `NARRATES_EVENT` | Linn (obra) | Nauvoo Expositor suppression | Book IV |
| `NARRATES_EVENT` | Linn (obra) | Martyrdom of Joseph Smith | Book IV |
| `NARRATES_EVENT` | Linn (obra) | Mormon Battalion march | Book V |
| `NARRATES_EVENT` | Linn (obra) | Handcart tragedy | Book VI |
| `NARRATES_EVENT` | Linn (obra) | Utah War 1857 | Book VI |
| `AUTHORED_BY` | Story of the Mormons | William Alexander Linn | Macmillan 1902 |

**Entidades nuevas para gazetteer:** William Alexander Linn (autor externo),
John C. Bennett (si no existe), Nauvoo Expositor (evento/entidad), William
Law (disidente Nauvoo)

**Consideraciones:**
- **Perspectiva:** Externa/secular con sesgo hostil. Linn era consciente de
  que las fuentes anti-mormonas exageran, pero no logró filtrar consistente-
  mente. Presenta la historia como fenómeno sociológico, no como narrativa
  de fe. Trata a Joseph Smith con escepticismo sostenido (lo presenta como
  money-digger, autocrat). Los capítulos sobre poligamia son los más extensos
  del libro (Book IV) y cargan con la moral victoriana de la época.
- **Authority override:** authority=20 — perspectiva externa, sin revisión
  eclesiástica, sesgo documentado. Valor principal: es la narrativa externa
  más completa del mormonismo del siglo XIX, útil para contrastar con fuentes
  internas (B.H. Roberts HC, Lucy Mack Smith, etc.).
- **⚠️ Nota editorial para RAG:** Contiene afirmaciones sobre money-digging,
  danitas, poligamia y carácter de Joseph Smith que reflejan fuentes hostiles
  no verificadas independientemente. El RAG debe contextualizar cualquier
  cita con el nivel de autoridad (20) y la perspectiva del autor. Nunca
  presentar afirmaciones de Linn como dato factual sin contrastar con
  fuentes internas de mayor autoridad.
- **Estructura para parser:** 6 Books con capítulos titulados (títulos
  descriptivos largos, no numeración simple). El skill `/gutenberg`
  necesitará manejo de la jerarquía Book > Chapter — los capítulos podrían
  mapearse como `book-i-ch-01-facility-of-human-belief.txt` o similar.
  ~54 capítulos totales.
- **Valor diferencial vs. corpus existente:** Única historia completa del
  mormonismo desde perspectiva externa secular en el corpus. Contrabalanza
  las fuentes internas (HC de Roberts, Missouri Persecutions, Rise and Fall
  of Nauvoo). Permite al RAG responder preguntas como "¿cómo veían los
  no-mormones a la Iglesia en 1900?" con fuente primaria.

---

### Early Scenes in Church History (Gutenberg #46783)

**Estado:** `researched` | authority=35 | Corpus path: `corpus/en/books/early-scenes-church-history/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Colección de relatos de primera mano sobre experiencias
  milagrosas y fe en la Iglesia temprana. Octavo libro de la Faith-Promoting
  Series (17 volúmenes, 1879-1915). Contiene testimonios personales de
  curaciones, protecciones divinas, don de lenguas, expulsión de espíritus
  malignos, y cumplimiento de profecías. NO es historia analítica — es
  literatura devocional testimonial con relatos autobiográficos organizados
  por autor, cada una con sub-capítulos propios.
- **¿Quién lo produjo?** Autores múltiples: B.F. Johnson, A.O. Smoot,
  Elias Morris, John Parry, John T. Evans, Thomas D. Giles, William J. Smith,
  Martin H. Peck, Philo Dibble, entre otros. Editado por George C. Lambert
  bajo la supervisión de George Q. Cannon (consejero de la Primera Presidencia).
  Publicado por Juvenile Instructor Office, Salt Lake City.
- **¿Cuándo?** 1882. La serie completa abarca 1879-1915.
- **¿Para quién?** "Designed for the Instruction and Encouragement of Young
  Latter-Day Saints." Audiencia juvenil SUD — Cannon quería libros que
  enseñaran fe y principios del evangelio de forma entretenida para jóvenes.
- **¿Cómo referenciado?** No ampliamente citado individualmente, pero la
  Faith-Promoting Series como conjunto es reconocida en historiografía SUD.
  Mormon Texts Project digitalizó los 17 volúmenes completos (2015).
  El relato de Philo Dibble es una fuente primaria citada ocasionalmente
  en obras sobre la Guerra de Missouri y Zion's Camp.
- **Relaciones KG clave:**

| Entidad | Tipo | Relación |
|---------|------|----------|
| George Q. Cannon | person | Series supervisor, First Presidency counselor |
| George C. Lambert | person | Series editor |
| A.O. Smoot | person | Author — 4 chapters covering missionary work, Far West, exile |
| Philo Dibble | person | Author — 4 chapters covering Kirtland, Missouri, Nauvoo |
| David W. Patten | person | Prophetic healing gifts, mentioned across multiple accounts |
| Wilford Woodruff | person | Smoot's missionary companion |
| Joseph Smith | person | Central figure in Dibble's narrative |
| Sidney Rigdon | person | Mentioned in Dibble's Kirtland account |
| Brigham Young | person | Dibble's account of succession |
| Elias Morris | person | Author — British Mission, scaffold fall miracle |
| Abel Evans | person | British Mission — gift of healing |
| Far West, Missouri | place | Siege and imprisonment (Smoot, Dibble) |
| Kirtland, Ohio | place | Early manifestations (Dibble) |
| Nauvoo, Illinois | place | Final chapters of Dibble's narrative |
| Winter Quarters | place | Smoot's account |
| Wales / Cornwall | place | British Mission chapters |
| Missouri War 1838 | event | Covered by both Smoot and Dibble |
| Zion's Camp | event | Dibble's narrative |
| British Mission (1840s) | event | Morris, Evans, Parry chapters |

- **Consideraciones:**
  - **Estructura irregular** — no capítulos numerados secuenciales sino
    secciones por autor, cada una con sub-capítulos propios. El splitter
    debe respetar la jerarquía autor > capítulo.
  - **Contenido anecdótico-testimonial**, no doctrinal ni analítico.
    No genera relaciones causales fuertes pero sí enlaces persona-evento
    y persona-lugar de alta densidad.
  - **Superposición parcial** con History of the Church (HC) y Missouri
    Persecutions (Roberts) para los mismos eventos, pero desde perspectiva
    de participantes individuales (no del historiador).
  - **Complementa directamente** #51730 (Life of David W. Patten) — A.O.
    Smoot relata experiencias con Patten, y Dibble cubre los mismos eventos
    de Missouri desde otra perspectiva.
  - **Parte de la Faith-Promoting Series** junto con Heber C. Kimball's
    Journal (#47519, ya analizado arriba). Comparte editor (Lambert),
    publisher (Juvenile Instructor Office), y audiencia (jóvenes SUD).
  - **Valor KG principal:** testimonios de primera mano de personas menores
    que no tienen otra biografía en el corpus (Dibble, Morris, Evans, Giles).

**Estructura detallada (~15 secciones/capítulos):**
1. "Show Us a Sign" ��� B.F. Johnson (curación milagrosa, escepticismo)
2. "Contest with Evil Spirits" — H.G.B. (posesión demoniaca, Virginia)
3. "Early Experience of A.O. Smoot" — Ch. I-IV (misión con Woodruff,
   Far West, prisión, éxodo, misión a Tennessee, martirio de JS)
4. "Scenes in the British Mission" — Ch. I-IV (Morris scaffold fall,
   Evans healing gifts, Parry Welsh mission, Evans cholera/conversions)
5. "Remarkable Healings" — Martin H. Peck (curaciones múltiples)
6. "Philo Dibble's Narrative" — Ch. I-IV (Kirtland manifestations,
   personal shooting at Haun's Mill, Far West siege/betrayal, Nauvoo
   prophecies of Joseph Smith)
7. Thomas D. Giles (ch. VI) — coal crushing injury, miraculous healing
8. William J. Smith (ch. VII) — prophecy and fulfillment

---

### Life of David W. Patten, the First Apostolic Martyr (Gutenberg #51730)

**Estado:** `researched` | authority=35 | Corpus path: `corpus/en/books/life-of-david-w-patten/`

#### Fase 0 — Análisis de contenido

- **¿Qué es?** Biografía completa de David W. Patten (1799-1838), miembro
  original del Quórum de los Doce Apóstoles y primer apóstol martirizado
  en esta dispensación. 8 capítulos cubriendo su vida completa: juventud,
  conversión metodista, bautismo (1832), misiones, ordenación apostólica
  (1835), liderazgo en Missouri, designación como "Captain Fear Not",
  y muerte en la Batalla de Crooked River (25 oct 1838). Formato
  narrativo-biográfico con testimonios de terceros y citas de fuentes
  primarias. Incluye prefacio de Lorenzo Snow. ~139 KB texto plano.
- **¿Quién lo produjo?** Lycurgus A. Wilson (1856-1940), autor y filósofo
  SUD (también escribió "Outlines of Mormon Philosophy", Gutenberg #49357).
  No fue Autoridad General. Contribuyeron: Thomas Jefferson Patten (sobrino
  del apóstol), Wilford Woodruff, Lorenzo Snow. Prefacio de Lorenzo Snow
  (entonces presidente de la Iglesia), quien relata un viaje a caballo
  de 25 millas con Patten que fue "the turning point" en su vida espiritual.
  Publicado por Deseret News, Salt Lake City.
- **¿Cuándo?** 1900 (prefacio fechado 8 feb 1900; publicación efectiva 1904).
  Producción Gutenberg por Christopher Dunn (Mormon Texts Project Intern),
  release 11 abr 2016.
- **¿Para quién?** Miembros SUD interesados en historia de la Iglesia
  temprana y los primeros apóstoles. Dedicado "to the missionaries of
  the Church of Jesus Christ of Latter-day Saints."
- **¿Cómo referenciado?** Fuente primaria estándar sobre David W. Patten —
  prácticamente la única biografía dedicada a él. Citado en el Religious
  Studies Center de BYU, en Doctrine and Covenants Central, y en artículos
  del Church News y Deseret News sobre Patten. La frase de Joseph Smith
  sobre su muerte ("There lies a man who has done just as he said he would
  — he has laid down his life for his friends") se cita frecuentemente
  en conferencia general y materiales de la Iglesia.
- **Relaciones KG clave:**

| Entidad | Tipo | Relación |
|---------|------|----------|
| David W. Patten | person | `SUBJECT_OF` — biography subject |
| Lycurgus A. Wilson | person | `AUTHORED_BY` — author |
| Lorenzo Snow | person | Wrote preface; personal testimony of Patten's influence |
| Wilford Woodruff | person | Contributed testimony; missionary companion |
| Abraham O. Smoot | person | Missionary companion to Patten |
| Joseph Smith | person | Called Patten to missions; eulogized him at death |
| Thomas B. Marsh | person | Co-president pro tempore in Missouri with Patten |
| Oliver Cowdery | person | Ordained Patten as Apostle (with Whitmer, Harris) |
| David Whitmer | person | Ordained Patten as Apostle |
| Martin Harris | person | Ordained Patten as Apostle |
| Samuel Bogart | person | Ray County militia captain at Crooked River |
| Thomas Jefferson Patten | person | Nephew, contributed source material |
| Theresa, New York | place | Birthplace of Patten |
| Far West, Missouri | place | Headquarters; Patten's base 1836-1838 |
| Adam-ondi-Ahman | place | Ch. VII — Patten's address to Saints |
| Kirtland, Ohio | place | Temple endowments, apostolic ordination |
| Paris, Tennessee | place | Missionary field, prophecy |
| Crooked River, Missouri | place | Battle site, mortal wounding |
| D&C 114 | scripture | Revelation calling Patten to mission (Apr 1838) |
| D&C 124:130 | scripture | Posthumous memorial (Jan 1841) |
| Battle of Crooked River | event | 25 Oct 1838 — Patten's death |
| Apostolic Ordination 1835 | event | Original Quorum of Twelve |
| Missouri War 1838 | event | Context for Patten's martyrdom |
| Extermination Order | event | Precipitated by Crooked River battle |

- **Consideraciones:**
  - **Alta densidad KG para obra corta** (8 capítulos, ~139 KB). Cada
    capítulo conecta múltiples personas y eventos del periodo 1832-1838.
  - **Enlace causal critico para el KG:** la muerte de Patten en Crooked
    River fue el evento que precipitó la Orden de Exterminio de Boggs
    (CAUSED_BY / PRECEDED_BY).
  - **Superposición significativa** con History of the Church vols 2-3 y
    Missouri Persecutions (Roberts) para 1835-1838, pero desde la
    perspectiva específica de Patten.
  - **Prefacio de Lorenzo Snow** valioso por derecho propio: testimonio
    personal de un futuro profeta sobre el impacto espiritual de un apóstol.
  - **Wilson no es historiador de primer nivel** (no es Roberts ni Cannon),
    pero la obra fue avalada por Lorenzo Snow como presidente de la Iglesia.
  - **Complementa directamente** Early Scenes (#46783) — A.O. Smoot relata
    experiencias con Patten en ese libro. Ingestar ambos juntos maximiza
    las conexiones cruzadas.
  - **Wilson también escribió** "Outlines of Mormon Philosophy" (#49357) —
    perfil de autor filosófico-devocional, no historiográfico.
  - **Capítulo 5 contiene** el encuentro de Patten con Caín — relato
    legendario frecuentemente citado en folklore SUD. Requiere nota de
    contexto (no es doctrina oficial).

**Estructura (8 capítulos):**
1. Early life, parentage, Methodism, Gospel discovery, baptism (1832), first mission
2. Healing practices, visit to Prophet Joseph, missionary labors, family baptism, move to Missouri
3. Missouri Saints' conditions, revelation, Tennessee mission, healing testimonies
4. Apostolic ordination (Feb 1835), revelation to the Twelve, Lorenzo Snow impressions
5. Rest, Kirtland temple endowments, second Tennessee mission, Woodruff/Smoot meetings, mob court, Cain encounter
6. Physical appearance, healing incidents, Paris TN prophecy, Far West, Kirtland apostasy visit, Missouri presidency succession
7. Adam-ondi-Ahman, "Captain Fear Not," storm calming, succession to presidency of the Twelve
8. Battle of Crooked River, mortal wounding, death scene, Woodruff's testimony, Joseph Smith's eulogy

---

## Tier EXT — Diccionarios bíblicos clásicos (authority=15-20, external reference)

> Obras de referencia protestantes del siglo XIX, dominio público.
> NO son fuentes doctrinales SUD. Valor principal: contexto histórico/geográfico/
> arqueológico y alimentación del KG con definiciones y etimologías.
> La Iglesia SUD produce sus propias ayudas (Bible Dictionary, GEE, TG) que
> ya están en el corpus con authority=50-55. Estas obras externas complementan
> con profundidad enciclopédica lo que las ayudas oficiales cubren brevemente.

### Easton's Bible Dictionary (1897)

**Estado:** `ingested` (corpus, pendiente indexación)

**Fase 0 — Análisis de contenido:**

- **¿Qué es?** Diccionario bíblico compacto con ~3,964 entradas: definiciones
  cortas tipo diccionario + artículos más largos tipo enciclopedia. Cubre
  personas, lugares, palabras, costumbres, geografía, historia natural.
- **¿Quién lo produjo?** Matthew George Easton (1823–1894), ministro
  presbiteriano escocés. Publicado póstumamente por Thomas Nelson en 1897.
- **¿Cuándo?** 1897 (3ª edición, la más difundida).
- **¿Para quién?** Estudiantes de la Biblia en general; nivel accesible.
- **¿Cómo referenciado?** Ampliamente distribuido en formato digital; incluido
  en casi todo software bíblico (SwordSearcher, e-Sword, Logos, Accordance).
  No es académico de primer nivel pero sí el más popular para uso personal.
- **Relaciones con corpus existente:** Entradas sobre personas/lugares bíblicos
  se cruzan con nuestro Bible Dictionary SUD (1,275 entradas) y TG/GEE.
  Easton es más extenso (3,964 vs 1,275) y cubre temas que el BD SUD omite.
- **Limitaciones:** Teología "decidedly Protestant" (CCEL). Interpretaciones
  del siglo XIX sin arqueología moderna (no conoce Qumrán, Nag Hammadi, etc.).
  No incluye perspectiva de la Restauración. Algunos artículos reflejan
  anti-catolicismo de la época.

**Source:** CCEL — ThML XML parseado a `corpus/en/reference/easton-bible-dictionary/`

---

### Smith's Bible Dictionary (1884)

**Estado:** `ingested` (corpus, pendiente indexación)

**Fase 0 — Análisis de contenido:**

- **¿Qué es?** Diccionario bíblico enciclopédico con ~4,556 entradas.
  Originalmente 3 volúmenes (1857), condensado en 1 volumen (1884).
  Cubre antigüedades, biografías, geografía e historia natural.
- **¿Quién lo produjo?** William Smith (1813–1893), lexicógrafo y clasicista
  inglés. Contribuyeron Harold Browne (obispo de Ely), Charles Ellicott
  (obispo de Gloucester), J.B. Lightfoot (Cambridge). "The fruit of the
  ripest biblical scholarship of England" (reseña original).
- **¿Cuándo?** 1ª ed. 1857, edición popular 1884.
- **¿Para quién?** Público general educado + estudiantes de seminario.
- **¿Cómo referenciado?** Considerado un clásico fundacional; "required
  reference book for any good study library" (Bible History). Más
  académico que Easton pero menos profundo que Hastings.
- **Relaciones:** Similar a Easton pero con artículos más largos para
  temas geográficos y arqueológicos. Complementa bien el BD SUD.
- **Limitaciones:** Mismo sesgo temporal (pre-Qumrán). Perspectiva anglicana
  de la era victoriana. Algunos artículos superados por descubrimientos
  posteriores (geografía de Palestina, cronología de los patriarcas).

**Source:** CCEL — ThML XML parseado a `corpus/en/reference/smith-bible-dictionary/`

---

### Hitchcock's Bible Names Dictionary (1869)

**Estado:** `ingested` (corpus, pendiente indexación)

**Fase 0 — Análisis de contenido:**

- **¿Qué es?** Diccionario etimológico compacto de 2,614 nombres propios
  bíblicos con sus significados en hebreo/griego. Formato: `Nombre, significado`.
  Extraído de "Hitchcock's New and Complete Analysis of the Holy Bible."
- **¿Quién lo produjo?** Roswell Dwight Hitchcock (1817–1887), profesor de
  historia eclesiástica en Union Theological Seminary, Nueva York.
- **¿Cuándo?** 1869.
- **¿Para quién?** Estudiantes de la Biblia, predicadores que necesitan
  etimologías rápidas para sermones/estudios.
- **¿Cómo referenciado?** "Though first published in 1869, Hitchcock's
  scholarship of the Hebrew language still measures up to contemporary
  standards" (CCEL). Incluido en múltiples plataformas bíblicas digitales.
- **Relaciones:** Valor único para el KG — cada entrada es un nombre propio
  con significado etimológico. Se cruza directamente con nuestros gazetteers
  (personas, lugares, pueblos). Puede enriquecer nodos existentes con campo
  `etymology` o `name_meaning`.
- **Limitaciones:** Solo nombres — no hay definiciones ni contexto. Algunas
  etimologías son especulativas o basadas en folk etymology del siglo XIX
  (el hebreo bíblico tiene muchos hapax legomena). No incluye nombres
  del Libro de Mormón ni D&C.

**Source:** CCEL — texto plano parseado a `corpus/en/reference/hitchcock-bible-names/`

---

### International Standard Bible Encyclopedia — ISBE (1915)

**Estado:** `ingested` (corpus, pendiente indexación)

**Fase 0 — Análisis de contenido:**

- **¿Qué es?** Enciclopedia bíblica exhaustiva en 5 volúmenes con ~10,121
  entradas por 200+ académicos. La obra de referencia bíblica protestante
  más completa en dominio público. Artículos firmados, algunos de varias
  páginas, con análisis detallado.
- **¿Quién lo produjo?** Editor general: James Orr (1844–1913), teólogo
  reformado escocés. Editores asociados: John Nuelsen, Edgar Mullins,
  Morris Evans, Melvin Grove Kyle. Contribuyentes notables: B.B. Warfield,
  A.T. Robertson, Archibald Alexander.
- **¿Cuándo?** Publicado 1915 por Howard-Severance Co., Chicago. Completado
  1939. Creado explícitamente para contrarrestar el impacto del higher
  criticism liberal.
- **¿Para quién?** Pastores, profesores de seminario, académicos.
- **¿Cómo referenciado?** Stephen Motyer (1984): "great solid worth...
  seriously commend this encyclopedia." Conservadurismo "broad, main-line
  evangelicalism." Sigue siendo la enciclopedia protestante de referencia
  gratuita más citada. Existe edición revisada (Bromiley, 1979-1995)
  con copyright.
- **Relaciones:** Artículos largos sobre personas, lugares, doctrinas,
  costumbres — alimenta directamente el KG con relaciones curadas en
  prosa. Se cruza con los 3 diccionarios menores + nuestro BD SUD.
  Cubre temas que ninguno de los otros tiene (arqueología, lingüística,
  historia de manuscritos, cronología detallada).
- **Limitaciones:** Perspectiva evangelical conservadora de principios del
  s. XX — anti-higher-criticism explícito (Orr). "Dogmatic use of the
  Bible" (Motyer). Arqueología desactualizada (pre-Dead Sea Scrolls,
  pre-Ebla, pre-Ugarit). Artículos largos pero a veces apologéticos
  más que descriptivos.

**Source:** internationalstandardbible.com — HTML scrapeado a `corpus/en/reference/isbe/`

---

### Hastings' Dictionary of the Bible (1898)

**Estado:** `ingested` (corpus, pendiente indexación — descarga en curso)

**Fase 0 — Análisis de contenido:**

- **¿Qué es?** Enciclopedia bíblica en 5 volúmenes (4 + índice) con 5,915
  entradas firmadas, algunas de varias páginas. Descrito como "better
  described as an encyclopaedia" (Wikipedia). Cubre personas, lugares,
  antigüedades, arqueología, teología bíblica, ética, palabras arcaicas
  de las versiones inglesas.
- **¿Quién lo produjo?** Editor: James Hastings (1852–1922). Asistentes:
  John A. Selbie, A.B. Davidson, S.R. Driver, H.B. Swete — los nombres
  más importantes del biblical scholarship británico de la época.
  194 autores de artículos, principalmente del Reino Unido.
- **¿Cuándo?** Volúmenes publicados 1898–1904.
- **¿Para quién?** Académicos y pastores; nivel más técnico que Easton/Smith.
- **¿Cómo referenciado?** "For nearly a century, lay people and scholars
  alike have valued the authoritative contents" (Logos). Representa la
  mainstream scholarship de su época — acepta higher criticism moderado
  (documentary hypothesis), a diferencia de ISBE que la combate. "Full
  account taken of literary criticism and archaeological discovery."
- **Relaciones:** Complemento ideológico de ISBE — donde ISBE es
  conservador/apologético, Hastings es crítico/académico. Juntos dan
  el espectro completo del scholarship de 1900. Se cruza con los mismos
  temas pero desde perspectiva más analítica.
- **Limitaciones:** 194 autores = variación en calidad. Perspectiva
  protestante británica de la era eduardiana. Higher criticism de la
  época está en parte superado. Encoding issues (caracteres hebreos/
  griegos transliterados de forma inconsistente en la versión digital).

**Source:** bibleportal.com — HTML scrapeado a `corpus/en/reference/hastings-dictionary-of-the-bible/`

---

### Análisis comparativo — las 5 obras como conjunto

| Dimensión | Easton | Smith | Hitchcock | ISBE | Hastings |
|-----------|--------|-------|-----------|------|----------|
| Entradas | 3,964 | 4,556 | 2,614 | 10,121 | 5,915 |
| Profundidad | Media | Media | Mínima (solo nombres) | Alta | Alta |
| Perspectiva teológica | Presbiteriana | Anglicana | N/A | Evangelical conservador | Mainstream crítico |
| Rigor académico | 60 | 65 | 55 | 75 | 80 |
| Arqueología | Básica | Básica | N/A | Detallada (1915) | Detallada (1900) |
| Año | 1897 | 1884 | 1869 | 1915 | 1898 |
| Valor KG | Definiciones, refs | Definiciones, geografía | Etimologías directas | Artículos enciclopédicos | Análisis crítico |

**Valor conjunto para Alejandría:**
Las 5 obras no compiten — se complementan en una pirámide:
1. **Hitchcock** (base) → etimologías de nombres → enriquece nodos KG existentes
2. **Easton + Smith** (nivel medio) → definiciones accesibles → contexto rápido para RAG
3. **ISBE + Hastings** (nivel superior) → artículos enciclopédicos → profundidad para queries complejas

Las 5 juntas suman ~27K entradas con ~80% de solapamiento en lemas pero contenido
complementario. El RAG puede citar múltiples fuentes para un mismo tema.

**Relación con ayudas SUD existentes:**
- Nuestro Bible Dictionary SUD (1,275 entradas, authority=50) es la fuente oficial.
- Estas obras externas NUNCA deben tener mayor authority que las ayudas SUD.
- El RAG debe priorizar: escritura > BD SUD/GEE/TG > Easton/Smith > ISBE/Hastings.
- El valor de las obras externas es profundidad y cobertura, no autoridad.

### KG — Paso 4: Análisis de relaciones y pre-seed

**Patrón diferenciado:** Estas obras son _fuentes de definiciones_, no narrativas.
No se pre-seedean relaciones individuales (serían ~27K). En cambio:

**Relaciones automáticas (pipeline las genera sin pre-seed):**
- `MENTIONS` — NER detecta entidades en definiciones → link chunk↔entity
- `AUTHORED_BY` — meta.json ya incluye autor → pipeline crea arista
- `REFERENCES` — scripRef parseadas en el XML (Easton/Smith) → intertextualidad

**Relaciones estructurales (ya implícitas en `authority.py` + `meta.json`):**
- `category: reference` → el pipeline asigna authority=15, context=external-reference
- Cada letra (A.txt, B.txt...) → un chunk group con ~150-650 entries

**Pre-seed manual recomendado (futuro, no bloqueante):**
No se requiere pre-seed Cypher para estas obras. El valor viene del NER
automático sobre definiciones ricas en entidades. Sin embargo, para
enriquecimiento futuro del KG:

| Enrichment | Source | Target KG field | Método |
|------------|--------|-----------------|--------|
| Etimología de nombres | Hitchcock 2,614 | `name_meaning` en nodos person/place | Script batch post-indexación |
| Cross-refs a escritura | Easton/Smith scripRef | `REFERENCES` edges | Automático vía pipeline |
| Definiciones complementarias | ISBE/Hastings | Ninguno — vive en FTS/semántico | Pipeline estándar |

**Nota:** `data/gazetteers/hitchcocks_bible_names.csv` ya existe con los mismos
2,614 nombres. El corpus en `reference/hitchcock-bible-names/` añade la misma
info como texto searcheable (FTS + embeddings), no duplica el gazetteer.

**Conclusión paso 4:** No se requiere pre-seed Cypher. Las relaciones emergen
del pipeline estándar. El valor KG principal es que las definiciones mencionan
entidades que el NER ya reconoce, generando miles de edges `MENTIONS`
automáticamente.

---

## Prioridades recomendadas (actualizado 2026-04-05)

> **Lo que ya está completo:** Escrituras, Conferencia General, 60+ manuales oficiales
> (incluyendo seminary teachers ×4, family strengthening, self-reliance, institute),
> 40 libros Gutenberg, himnos/canciones, study aids, HC 1-7 — TODO ingested.
> Ver tabla "Corpus actual" arriba para el inventario completo.
>
> **Lo que queda:** RSC BYU (214 libros), BYU Studies (31 libros pendientes),
> MTP/Gutenberg (~89 títulos), fuentes secundarias (CCEL, womeninthescriptures.com).
> Church site: solo Youth Music (blocked — API 404) y Ensign/Liahona (sin investigar).
>
> **Regla:** Iglesia > RSC > BYU Studies > MTP > Gutenberg > CCEL > Archive.org.

### Materiales oficiales pendientes (Church site)

| Prioridad | Material | Script | Justificación |
|-----------|----------|--------|---------------|
| ~~🟡 P1~~ | ~~Gospel Topics ES gap~~ | ~~resuelto~~ | ✅ 3 descargados, 21 no existen en ES |
| ~~🟡 P2~~ | ~~Seminary Teacher Manuals (4 vols)~~ | ~~resuelto~~ | ✅ OT 278, NT 312, BOM 312, D&C 280 — EN+ES |
| ~~🟡 P2~~ | ~~Family Strengthening Manuals~~ | ~~resuelto~~ | ✅ Marriage 18 + Str.Marriage 17 + Str.Family 19 archivos |
| ~~🟢 P3~~ | ~~Self-Reliance admin guides~~ | ~~resuelto~~ | ✅ Leaders 4, My Path 3, PEF 1, Facilitating 3, Plan 1 — EN+ES |
| ~~🟢 P3~~ | ~~Institute Student Readings + Elevate~~ | ~~resuelto~~ | ✅ Readings 39 EN-only, Elevate 10 EN + 11 ES |
| ~~🔵 P4~~ | ~~Teacher Development Skills + Christlike Teaching~~ | ~~resuelto~~ | ✅ Ya existían (27 + 1 archivos) |
| 🔴 **blocked** | Música para los jóvenes | `download_music.py` | API 404 — endpoint `/music/` no soportado por Study API |
| ⚫ **P6** | Ensign / Liahona archive | investigar | Volumen enorme; priorizar por tema |

### RSC BYU — exégesis académica SUD (214 libros, inventario completo arriba)

> Ver sección "Libros RSC prioritarios — por tipo de contenido" para la lista completa con slugs.

| Prioridad | Tipo de contenido | Libros | Notas |
|-----------|-------------------|--------|-------|
| 🔴 **P1** | Exégesis escritural (LdM, D&C, PGP, Bible, Isaías, JST) | 23 | `opening-isaiah`, `abinadi`, `introduction-book-abraham`, etc. |
| 🟡 **P2** | Doctrina, convenios, templo, cristología | 19 | Easter Conference (10), Sperry Symposium, templo |
| 🟢 **P3** | Fe práctica, apologética, salud mental | 16 | `freedom-scrupulosity`, `reason-faith`, etc. |
| 🔵 **P4** | Historia selectiva | 13 | `council-fifty`, `sister-prophet`, `my-dear-sister` |
| ⚪ **P5** | Relaciones interreligiosas | 7 | `view-hebrews`, `mormons-muslims`, etc. |

### BYU Studies — pendientes (31 libros)

| Prioridad | Material | Script | Notas |
|-----------|----------|--------|-------|
| 🟠 **P1** | BYU NT Commentary (4 vols) | `download_byustudies.py` | Comentario académico SUD del NT |
| 🟠 **P1** | Doctrine and Covenants Contexts | `download_byustudies.py` | Contexto histórico D&C |
| 🟠 **P1** | Opening the Heavens | `download_byustudies.py` | Manifestaciones divinas 1820-1844 |
| 🟡 **P2** | NT New Renditions (14 vols) | `download_byustudies.py` | Traducción moderna del NT |
| 🟡 **P2** | My Fellow Servants | `download_byustudies.py` | Historia del sacerdocio |
| 🟢 **P3** | Charting the Scriptures (2 vols) | `download_byustudies.py` | Charts escriturales |
| 🔵 **P4** | Remaining standalone books (5) | `download_byustudies.py` | Sustaining the Law, McLellin, etc. |
| ⚪ Upgrade | HC vols 1-6 de BYU Studies | `download_byustudies.py` | Mejorar calidad vs Gutenberg (opcional) |

### MTP / Gutenberg — textos pendientes (~89 títulos, ver sección MTP arriba)

| Prioridad | Material | Notas |
|-----------|----------|-------|
| 🟡 **P2** | Lectures on Faith, Wentworth Letter | Doctrina fundacional Kirtland |
| 🟢 **P3** | Mediation and Atonement (Taylor), Key to Theology (Pratt) | Teología profética |
| 🔵 **P4** | Representative Women of Deseret, Women of Mormondom | Perspectiva femenina |
| ⚫ **P6** | Journal of Discourses (26 vols) | MTP no lo tiene; enorme; authority baja |
