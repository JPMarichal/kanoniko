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

| Material | Estado | Notas |
|----------|--------|-------|
| Escrituras EN (todos los standard works) | `ingested` | |
| Escrituras ES (Book of Mormon) | `ingested` | AT/NT/D&C/PGP ES pendientes |
| Conferencia General 1971–2025 EN | `ingested` | ~6,900 charlas — **completo** |
| Conferencia General ES (~1990–2025) | `ingested` | Completo para lo disponible digitalmente — **completo** |
| General Handbook | `ingested` | EN+ES |
| Missionary Standards + Supplement | `ingested` | EN+ES |
| Proclamations (Family, Living Christ) | `ingested` | EN+ES |
| Bible Dictionary | `ingested` | EN (1,275 entradas) |
| Guide to the Scriptures (GEE) | `ingested` | EN (813) + ES (810) — consolida TG+BD en ES |
| Topical Guide | `ingested` | EN (3,513 entradas) — en GEE ES |
| JST Appendix | `ingested` | EN+ES (94 caps) |
| Chapter headings / superscriptions | `ingested` | EN+ES — en `.meta.json` de cada capítulo |
| Volume introductions (BoM, D&C, PGP, OT, NT) | `ingested` | EN+ES — 29 archivos vía `scrape_introductions.py` |
| Harmony of the Gospels | `prepared` | Tier 0a — P0 — Script: `scrape_harmony.py` |
| Bible Chronology (AT + NT) | `prepared` | Tier 0a — P0 — Script: `scrape_bible_chronology.py` |
| Abbreviations | `prepared` | Tier 0a — P0 — Script: `scrape_abbreviations.py` |
| Reference Guide to Holy Bible + BoM | `backlog` | Tier 0a — MEDIUM |
| Preach My Gospel 2023 | `ingested` | EN+ES — KG analysis: ver sección abajo |
| **Jesus the Christ** (Talmage) | `prepared` | Script: `download_jesus_the_christ.py` — KG analysis: ver sección abajo |
| **Christmas Study Plan** (anual) | `prepared` | Script: `download_christmas_study_plan.py` — `--year YYYY` |
| **Easter / Holy Week Study Plan** | `prepared` | Script: `download_easter_study_plan.py` — slug permanente |
| **Himnos** (Himnario clásico) | `prepared` | Script: `download_music.py --collection hymns` |
| **Himnos para el hogar y la Iglesia** (nuevo himnario) | `prepared` | Script: `download_music.py --collection hymns-home-church` |
| **Canciones para los niños** | `prepared` | Script: `download_music.py --collection childrens-songbook` |
| **Música para los jóvenes** | `prepared` | Script: `download_music.py --collection youth-music` |
| **Ayudas para los Himnos** | `prepared` | Script: `download_music.py --collection hymn-helps` |

---

## Tier 0 — Planes de Estudio Estacionales (authority=60)

### Christmas Study Plan (anual)

**Estado:** `prepared` — Script: `download_christmas_study_plan.py`

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

**Estado:** `prepared` — Script: `download_easter_study_plan.py`

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

**Estado corpus:** `prepared` | Script: `download_jesus_the_christ.py` | authority=45, author="James E. Talmage"

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

**Estado:** `prepared` — Script: `scrape_harmony.py`

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

**Estado:** `prepared` — Script: `scrape_bible_chronology.py`

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

**Estado:** `prepared` — Script: `scrape_abbreviations.py`

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

**Estado:** `prepared` — `download_music.py --collection hymns`

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

**Estado:** `prepared` — `download_music.py --collection hymns-home-church`

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

**Estado:** `prepared` — `download_music.py --collection childrens-songbook`

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

**Estado:** `prepared` — `download_music.py --collection youth-music`

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

**Estado:** `prepared` — `download_music.py --collection hymn-helps`

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

**Estado:** `backlog`

> ⚠️ **Disponibilidad incierta:** Solo *Jesus the Christ* ha sido confirmado
> en el sitio oficial de Talmage. Requiere verificar si este título está en
> `/study/manual/the-articles-of-faith` o solo en Gospel Library / dominio público.

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

**Estado:** `backlog`

> ❌ **No disponible en el sitio oficial** (confirmado 2026-04-02). Requiere fuente externa
> (Project Gutenberg / archive.org, dominio público 1909).

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

**Estado:** `prepared` — Script: `download_manual.py --manual gospel-principles`
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

**Estado:** `prepared` — Script: `download_manual.py --manual true-to-the-faith`
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

**Estado:** `prepared` — Script: `download_manual.py --manual come-follow-me --cfm-year YYYY`
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

**Estado:** `prepared` — Script: `download_manual.py --manual teachings-{nombre}` o `--all-prophets`
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

**Estado:** `prepared` — Script: `download_manual.py --manual {key}` (bom-institute-student, dc-institute-student, pgp-institute-student, nt-institute-teacher)

**Serie:** Old Testament, New Testament, Book of Mormon, Doctrine & Covenants,
Church History — cada uno ~40 lecciones densas. Son la base del estudio
académico del evangelio en el instituto de religión.

**Investigar:** URL patterns en el sitio (probablemente `/study/manual/book-of-mormon-seminary`
o similar). Los de Instituto son distintos a los de Seminario.

**KG valor:** Muy alto — son comentarios académicos con referencias cruzadas
extensas entre todos los standard works.

---

### 10. Our Heritage: A Brief History of The Church

**Estado:** `prepared` — Script: `download_manual.py --manual our-heritage`
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

**Estado:** `prepared` — Script: `download_manual.py --manual saints-v{1-4}`

**Descripción:** Historia narrativa oficial de la Iglesia (2018–2024),
~400 páginas por volumen. Altamente citada en conferencia reciente.
Es la historia institucional más moderna y completa.

**URL pattern:** `/study/history/saints-v{1-4}` (uri_prefix=/history, no /manual) — confirmado en download_manual.py.

---

### 12. For the Strength of Youth

**Estado:** `prepared` — Script: `download_manual.py --manual for-the-strength-of-youth`
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

**Estado:** `backlog` — Fuera del sitio oficial; diferir

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

**Estado:** `prepared` — Script: `download_manual.py --manual gospel-topics-essays`
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

**Estado:** `prepared` — Script: `download_manual.py --manual first-vision-accounts`
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

**Estado:** `prepared` — Script: `download_manual.py --manual {key}` (bom-seminary-student, nt-seminary-student, ot-seminary-student, doctrinal-mastery)

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

**Estado:** `prepared` — Script: `download_manual.py --manual {key}` (ver tabla abajo)

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

**Estado:** `prepared` — Script: `download_manual.py --manual {key}` (eternal-family, foundations-restoration, jesus-christ-everlasting-gospel, teachings-doctrine-bom)

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

**Estado:** `prepared` — Script: `download_manual.py --manual saints-v{1-4}`
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

**Estado:** `prepared` — Script: `download_manual.py --manual doctrines-of-the-gospel`
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

**Estado:** `prepared` — Script: `download_manual.py --manual gospel-topics`

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

**Estado:** `prepared` — Script: `download_manual.py --manual missionary-preparation`

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

**Estado:** `prepared` — Script: `download_manual.py --manual {key}`

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

**Estado:** `prepared` — Script: `download_manual.py --manual {key}`

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

**Estado:** `prepared` — Script: `download_manual.py --manual {key}`

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

**Estado:** `prepared` — Script: `download_manual.py --manual {key}`

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

**Estado:** `prepared` — Script: `download_manual.py --manual {key}`

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

### Gospel Topics — gap ES (24 tópicos)

**Estado:** `prepared` — Script: `download_manual.py --manual gospel-topics --lang spa`

Los 24 tópicos faltantes en ES **existen** en el sitio (verificado 2026-04-04). Son:
church-financial-administration, debt, divorce, high-council, joseph-smiths-character,
journal-of-discourses, mormon-church, mormonism, mormons, movies-and-television,
patriarchal-blessings, plural-marriage, prison-ministry,
race-and-the-church-of-jesus-christ-of-latter-day-saints, religion-and-science,
religion-vs-violence, restoration-of-the-church-study-guide, sacrament-meeting,
single-parent-families, temples-of-the-church-of-jesus-christ-of-latter-day-saints,
tithing, transgression, transparency-about-church-history-questions,
womens-service-and-leadership-in-the-church.

**Causa del gap:** Probablemente el scraper original no recogió nuevas adiciones al índice ES,
o el TOC ES tenía menos enlaces al momento de la descarga.

**Acción:** Re-ejecutar descarga gospel-topics solo para ES, o ejecutar incremental con
`--lang spa`. El script ya existe y los slugs son los mismos.

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

## Prioridades recomendadas

> **Conferencias Generales (EN 1971–2025 + ES ~1990–2025):** ya ingresadas. No hay pendiente.

| Prioridad | Material | Justificación |
|-----------|----------|---------------|
| 🔴 **P0** | Jesus the Christ | Script listo (`prepared`) |
| 🔴 **P0** | Himnos + Himnario nuevo + Canciones niños | Scripts listos; 553 himnos/canciones con metadata rica |
| 🔴 **P0** | Ayudas para los Himnos | "About the Hymns" = comentario exegético oficial (EN only) |
| 🔴 **P0** | Harmony of the Gospels | PARALLEL_ACCOUNT_OF MT/MC/LC/JN ↔ BoM/D&C; intertextualidad imposible de inferir vía NER |
| 🔴 **P0** | Bible Chronology | Eje temporal del KG; ancla entidades a fechas absolutas |
| 🔴 **P0** | Abbreviations | Alimenta normalizador de scripture refs; 2 archivos, esfuerzo mínimo |
| 🟠 **P1** | Gospel Topics Essays | Único lugar donde la Iglesia aborda temas sensibles oficialmente; authority=70 |
| 🟠 **P1** | First Vision Accounts | Relatos primarios no incluidos en PGP; authority=75 |
| 🟠 **P1** | Christmas + Easter Study Plans | Scripts listos; alta densidad de intertextualidad |
| 🟠 **P1** | Gospel Principles | `prepared` — `download_manual.py --manual gospel-principles` |
| 🟡 **P2** | True to the Faith | `prepared` — `download_manual.py --manual true-to-the-faith` |
| 🟡 **P2** | Doctrines of the Gospel | `prepared` — `download_manual.py --manual doctrines-of-the-gospel` |
| 🟡 **P2** | Música para los jóvenes | `prepared` — `download_music.py --collection youth-music` |
| 🟢 **P3** | Teachings of Presidents (Joseph Smith primero) | `prepared` — `download_manual.py --manual teachings-joseph-smith` |
| 🟢 **P3** | Come Follow Me 2019–2026 (8 años) | `prepared` — `download_manual.py --manual come-follow-me --cfm-year YYYY` |
| 🟢 **P3** | Our Heritage + For the Strength of Youth | `prepared` — `download_manual.py --manual our-heritage` etc. |
| 🟢 **P3** | Seminary Student Manuals (BoM + D&C) | `prepared` — `download_manual.py --manual bom-seminary-student` etc. |
| 🔵 **P4** | Teachings of Presidents (serie completa) | `prepared` — `download_manual.py --all-prophets` |
| 🔵 **P4** | Institute Scripture Course Manuals (BoM + D&C) | `prepared` — `download_manual.py --manual bom-institute-student` etc. |
| 🔵 **P4** | Saints Vols 1–4 | `prepared` — `download_manual.py --manual saints-v1` etc. |
| 🔵 **P4** | Institute Cornerstone Courses | `prepared` — `download_manual.py --manual eternal-family` etc. |
| 🔵 **P4** | Gospel Topics (enciclopedia general) | `prepared` — `download_manual.py --manual gospel-topics` |
| ⚪ **P5** | Missionary Preparation | `prepared` — `download_manual.py --manual missionary-preparation` |
| ⚪ **P5** | Discourses of Brigham Young | `backlog` — fuente externa (Project Gutenberg), requiere script nuevo |
| ⚫ **P6** | Articles of Faith + Great Apostasy (Talmage) | `backlog` — ❌ No en sitio oficial; requiere fuente externa |
| ⚫ **P6** | Institute manuals OT/NT | `prepared` — `download_manual.py --manual nt-institute-teacher` etc. |
| ⚫ **P6** | Ensign / Liahona archive | `backlog` — volumen enorme; priorización temática necesaria |
| ⚫ **P6** | Journal of Discourses | `backlog` — histórico, requiere manejo cuidadoso de autoridad |
