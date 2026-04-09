# Fase 0 — Journal of Discourses

> Análisis: 2026-04-09 | Fuente: journalofdiscourses.com | Estado: **backlog**
>
> **Fase 0 incompleta.** Solo contiene el análisis técnico de la fuente de descarga
> (selectores HTML, prueba de extracción, diseño del script). Falta la investigación
> editorial (paso 1) y el análisis de contenido/valor (paso 2) del protocolo Fase 0.

---

## PENDIENTE — Paso 1: Investigación editorial

Requiere web research para establecer:
- [ ] Historia editorial (quién compiló los volúmenes, proceso de transcripción de Watt, ediciones)
- [ ] Posición oficial de la Iglesia (declaraciones específicas sobre su estatus)
- [ ] Recepción histórica y uso actual (¿citados en manuales? ¿en conferencia?)
- [ ] Ediciones disponibles (¿hay ediciones críticas modernas?)

## PENDIENTE — Paso 2: Análisis de contenido y valor

Basado en hallazgos del paso 1:
- [ ] Modelo de authority fundamentado (no asumido — el "25" actual es provisional)
- [ ] Valor KG: qué entidades y relaciones únicas aporta que no tenemos
- [ ] Deduplicación con Discourses of Brigham Young (ya en corpus) y otros
- [ ] Riesgos de contenido: doctrinas abandonadas, contexto histórico necesario
- [ ] Estimación de volumen detallada

---

## Descripción provisional

26 volúmenes de discursos de profetas y apóstoles SUD (1854-1886), publicados originalmente
en Liverpool por George D. Watt (estenógrafo de Brigham Young). Dominio público.

**authority:** ? (pendiente investigación editorial — el "25" usado anteriormente era provisional)

## Análisis técnico de fuente: journalofdiscourses.com

### Alternativas evaluadas

| Fuente | Formato | Calidad | Viabilidad |
|--------|---------|---------|------------|
| **journalofdiscourses.com** | HTML limpio | Buena — texto legible, metadata rica | **SELECCIONADA** — scraper simple |
| Wikisource | Wiki markup | Variable — transcripción incompleta en algunos vols | Viable como fallback |
| Archive.org | PDF escaneado / OCR | Baja — requiere post-procesamiento pesado | Último recurso |
| BYU scriptures (scriptures.byu.edu) | PDF | Media — un PDF por volumen | No scrapeable fácilmente |
| BYU OverDrive | eBook | Buena | Requiere cuenta BYU |
| MTP (Mormon Texts Project) | — | N/A — explícitamente declinaron transcribirlo | Descartada |

### Estructura del sitio

- **URL base:** `https://journalofdiscourses.com`
- **Volumen TOC:** `/{volume}` (e.g., `/1`, `/26`)
- **Discurso individual:** `/{volume}/{discourse_number}` (e.g., `/1/1`, `/26/40`)
- **Por orador:** `/{Speaker_Name}` (e.g., `/Brigham_Young`)
- **Sin paginación:** cada volumen muestra todos sus discursos en una sola página
- **Stack:** Bootstrap 3, HTML estático, sin JS dinámico, sin API

### Escala

| Métrica | Valor |
|---------|-------|
| Volúmenes | 26 |
| Discursos totales | **1,426** |
| Rango por volumen | 40-91 |
| Oradores únicos | 52 |
| Orador principal | Brigham Young (388 discursos, 27%) |
| Período | 1851-1886 |
| Palabras estimadas | ~5M (promedio ~3,500 palabras/discurso × 1,426) |

### Oradores principales

| Orador | Discursos |
|--------|-----------|
| Brigham Young | 388 |
| John Taylor | 163 |
| Orson Pratt | 127 |
| Heber C. Kimball | 111 |
| George Q. Cannon | 111 |
| George A. Smith | 80 |
| Wilford Woodruff | 65 |
| Orson Hyde | 49 |
| Daniel H. Wells | 47 |
| Erastus Snow | 37 |
| (+42 oradores más) | 188 |

## Selectores HTML

### Página de volumen (TOC)

```
div.media > div.media-body
  h4.media-heading > a[href="/{vol}/{disc}"]   → título
  p (1º)                                       → descripción con orador, fecha, lugar
  p (2º, font-size:12px)                       → "Volume X, discourse Y, pages A-B"
```

**Ejemplo de descripción:** `"A Discourse by President Brigham Young, Delivered in the Tabernacle, Great Salt Lake City, January 16, 1853"`

Regex para extraer:
- Orador: `by (?:President |Elder |Brother |Bishop )?(.+?),\s+[Dd]eliver`
- Fecha: `(\w+ \d+, \d{4})`
- Lugar: `[Dd]elivered (?:in |at )(.+?),\s+\w+ \d+`

### Página de discurso

```
h1                    → título (text node antes de <small>)
h1 > small            → orador
div.paragraph         → párrafos del texto (múltiples, en orden)
ol.breadcrumb         → navegación (Volume X > Discourse Y)
```

**Nota:** La fecha y lugar NO están en la página del discurso — solo en el TOC del volumen.
El script debe recoger metadata del TOC y luego bajar cada discurso.

## Metadata extraíble

| Campo | Fuente | Disponibilidad |
|-------|--------|----------------|
| `title` | h1 o h4 > a | ✅ Siempre |
| `speaker` | h1 > small o desc | ✅ Siempre |
| `date` | Descripción en TOC | ✅ Mayoría (algunos "undated") |
| `location` | Descripción en TOC | ✅ Mayoría |
| `volume` | URL | ✅ Siempre |
| `discourse_number` | URL | ✅ Siempre |
| `pages` | Meta en TOC | ✅ Siempre |
| `role` | Prefijo en descripción | ⚠️ Variable ("President", "Elder", etc.) |

## Problemas identificados

### Encoding
- El sitio declara `charset=iso-8859-1` pero algunos caracteres em-dash aparecen como `�`
- **Solución:** decodificar como `latin-1` y reemplazar `\x97` → `—` (em-dash) antes de procesar

### OCR artifacts
- Split de palabras ocasional del OCR original: "breth ren", "compre hend"
- Son del texto fuente, no del sitio — presentes en todas las ediciones digitales
- **Decisión:** dejar como están (no intentar corregir automáticamente para no introducir errores)

### Discursos sin fecha
- Algunos discursos no incluyen fecha en la descripción
- **Solución:** campo `date` nullable en .meta.json

## Prueba de extracción (2026-04-09)

| Discurso | Speaker | Párrafos | Palabras | Chars | OCR issues |
|----------|---------|----------|----------|-------|------------|
| 1/1 | Brigham Young | 14 | 3,484 | 18,920 | "breth ren" |
| 13/24 | Brigham Young | 22 | 7,370 | 39,086 | `�` (em-dash) |
| 26/40 | Lorenzo Snow | 34 | 4,108 | 24,903 | `�` (em-dash) |

Extracción exitosa en los 3 casos. Parser simple (stdlib HTMLParser, sin BeautifulSoup).

## Diseño del script

### Flujo propuesto

```
1. Para cada volumen (1-26):
   a. GET /{volume} → parsear TOC → lista de discursos con metadata
   b. Para cada discurso:
      i. GET /{volume}/{discourse} → parsear texto
      ii. Escribir {volume}-{discourse:02d}.txt (texto plano, párrafos separados por \n\n)
      iii. Escribir {volume}-{discourse:02d}.meta.json (title, speaker, date, location, volume, discourse, pages)
   c. Delay entre requests (0.5-1s)
```

### Corpus path propuesto

```
corpus/en/books/journal-of-discourses/
  vol01/
    01-salvation.txt
    01-salvation.meta.json
    02-spiritual-communication.txt
    02-spiritual-communication.meta.json
    ...
  vol02/
    ...
  ...
  vol26/
    ...
```

### Estimaciones

| Métrica | Valor |
|---------|-------|
| Requests totales | 26 (TOC) + 1,426 (discursos) = **1,452** |
| Tiempo estimado (1 req/s) | ~25 min |
| Tamaño estimado | ~25-30 MB texto |
| Archivos | ~2,852 (txt + meta.json) |

## Valor para el corpus

### KG
- 52 oradores → nodos PERSON (mayoría ya existen como entidades del KG)
- Relaciones `DELIVERED_BY` (discurso → orador)
- Relaciones `TAUGHT` (orador → concepto) — extraíbles de títulos y texto
- Relaciones `OCCURRED_DURING` (discurso → período 1851-1886)
- Menciones cruzadas frecuentes con escrituras y otros discursos

### Riesgos
- **Volumen grande:** ~5M palabras = ingest significativo (vectores + KG)
- **Authority baja (25):** no debe dominar resultados de búsqueda
- **Contenido sensible:** algunos discursos contienen doctrinas abandonadas (matrimonio plural, Blood Atonement, etc.) — requiere contexto histórico cuidadoso
- **Solo EN:** no existe traducción oficial al español

## Estado

**`backlog`** — análisis técnico de fuente completo (viable, script diseñable).
Pendiente: Fase 0 pasos 1-2 (investigación editorial + análisis de contenido/valor).
Solo después de completar esos pasos puede pasar a `researched`.
