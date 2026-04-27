# Fase 0 — Study Aids

> Análisis de contenido y relaciones KG. Extraído de la reorganización del backlog (2026-04-05).

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

**Estado:** `descargado`

**URLs:** `/study/scriptures/bible-reference` y `/study/scriptures/bofm-reference`
**Autoridad:** 80 | **Bilingüe:** verificar

**Estructura:** Índices temáticos con secciones (Godhead, Gospel Topics, People,
Places, Events) y verse references por tema. El de BoM incluye secciones:
Jesus Christ, Doctrines, People, Events and Places.

**KG valor:** MEDIO — cubren terreno similar al TG/GEE ya ingresados. El valor
incremental es el agrupamiento temático diferente (más condensado). El de BoM
puede capturar relaciones entre personas y eventos del LdM que el TG no agrupa
de la misma forma.

**Descarga ejecutada 2026-04-26:**
- `Reference Guide to the Holy Bible`: 6 archivos EN (`introduction` + 5 secciones)
- `Reference Guide to the Book of Mormon`: 5 archivos EN (`introduction` + 4 secciones)

**Script:** `scrape_study_aids.py` adaptado. La ingestión queda pendiente.

---

### Index to Triple Combination

**Estado:** `descargado`

**URL:** `/study/scriptures/triple-index`
**Autoridad:** 80 | **Bilingüe:** no verificado

**Estructura:** Índice alfabético granular para Triple Combination con cobertura de
Book of Mormon + Doctrine and Covenants + Pearl of Great Price. El índice expone
entradas individuales por slug y se descargó como corpus plano de alta granularidad.

**KG valor:** MEDIO-ALTO — complementa TG con foco más fuerte en D&C y PGP, añade
entidades, temas y eventos con agrupamiento editorial útil para recuperación y posterior
pre-seeding.

**Descarga ejecutada 2026-04-26:** 3,060 entradas EN.

**Script:** `scrape_study_aids.py` adaptado. La ingestión queda pendiente.
