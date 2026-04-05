# Fase 0 — Música Oficial

> Análisis de contenido y relaciones KG. Extraído de la reorganización del backlog (2026-04-05).

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
- Himnos de ordenanzas → `required_for` → Ordinance

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
