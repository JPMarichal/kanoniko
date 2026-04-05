# Fase 0 — Clásicos de Autoridades Generales

> Análisis de contenido y relaciones KG. Extraído de la reorganización del backlog (2026-04-05).

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
