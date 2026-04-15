# Fase 0 — Teaching, No Greater Call (1999)

> Investigación editorial + análisis de contenido y valor KG.
> Fecha: 2026-04-15

---

## Paso 1 — Investigación editorial (web research)

### Historia editorial

- **Título EN:** *Teaching, No Greater Call: A Resource Guide for Gospel Teaching*
- **Título ES:** *La Enseñanza: El llamamiento más importante — Guía de consulta para la enseñanza del evangelio*
- **Autor:** The Church of Jesus Christ of Latter-day Saints (Intellectual Reserve, Inc.)
- **Publicación:** 1999 (copyright Intellectual Reserve)
- **Editor:** Departamento de Currículo de la Iglesia (correlacionado)
- **Formato:** Manual impreso (~200 pp.) + PDF oficial + web completo en sitio oficial
- **ISBN:** No aplica (publicación interna de la Iglesia, no Deseret Book)

### Contexto institucional

TNGC es el **manual oficial de la Iglesia sobre pedagogía del evangelio**. Fue el recurso
estándar para capacitación de maestros durante más de dos décadas (1999–2022), hasta ser
funcionalmente reemplazado por *Teaching in the Savior's Way* (2022).

**Cadena pedagógica histórica:**
```
J. Reuben Clark — The Charted Course of the Church in Education (1938)
  → Boyd K. Packer — Teach Ye Diligently (1975/1991)
    → Teaching, No Greater Call (1999) ← ESTE MATERIAL
      → Teaching in the Savior's Way (2022, ya en corpus)
        → Teacher Development Skills (S&I, ya en corpus)
```

TNGC sintetiza los principios de enseñanza que Packer articuló narrativamente en TYD,
pero en formato de manual oficial correlacionado — sin voz personal, con estructura
sistemática y respaldo institucional pleno.

### Audiencia y alcance

- **Todos los maestros llamados en la Iglesia:** Escuela Dominical, Primaria, Mujeres Jóvenes,
  Hombres Jóvenes, RS, Sacerdocio, maestros orientadores/ministrantes, padres
- **Líderes:** secciones específicas sobre enseñanza en contextos de liderazgo
- **Curso "Teaching the Gospel"** (Parte G): 12 lecciones estructuradas para impartir como clase
- Referenciado en General Handbook y materiales de capacitación de barrio hasta 2022

### Traducción

- **Bilingüe completo** (EN + ES) en el sitio oficial
- ES confirmado: `/study/manual/teaching-no-greater-call-a-resource-guide-for-gospel-teaching/contents?lang=spa`

### Estado actual

Funcionalmente reemplazado por *Teaching in the Savior's Way* (2022) pero **no retirado**
del sitio oficial. Sigue disponible y es referenciado como recurso complementario.
Church News lo describe como "phased out" por TITSW.

---

## Paso 2 — Análisis de contenido y valor para el corpus

### Estructura de contenido

7 partes (A–G), ~90 páginas web totales:

| Parte | Título | Páginas | Contenido |
|-------|--------|---------|-----------|
| **A** | Your Call to Teach | 12 | Importancia, preparación espiritual, mejora personal |
| **B** | Basic Principles of Gospel Teaching | 35 | Amor, Espíritu, doctrina, aprendizaje, métodos, preparación |
| **C** | Teaching Different Age-Groups | 6 | Niños, jóvenes, adultos |
| **D** | Teaching in the Home | 10 | Familia, padres, maestros orientadores |
| **E** | Teaching in Leadership Settings | 4 | Reuniones de liderazgo, entrevistas |
| **F** | Methods of Teaching | 1 (grande) | 48 métodos A–Z en una sola página (~25 pp. impresas) |
| **G** | The Teaching the Gospel Course | 14 | 12 lecciones + guía del instructor + estudio personal |
| | Extras | ~8 | Título, contenido, índice, "how to use" |
| | **Total** | **~90** | |

### URLs verificadas

- **Base:** `/study/manual/teaching-no-greater-call-a-resource-guide-for-gospel-teaching/`
- **API v3:** Funciona. URI = strip `/study` del path.
- **Slugs:** Jerárquicos: `{parte}/{sub-sección}/{N}-{título}`
  - Ejemplo: `/a-your-call-to-teach/prepare-yourself-spiritually/5-seeking-the-spirit`
- **Parte F:** Una sola página: `/f-methods-of-teaching` (contiene los 48 métodos)
- **Bilingüe:** Mismos slugs, cambiar `?lang=spa`

### Modelo de authority

| Eje | Valor | Justificación |
|-----|-------|---------------|
| **authority** | **60** | Manual oficial correlacionado de la Iglesia |
| **rigor** | 70 | Sistematizado, con referencias escriturales y citas de profetas inline |
| **official** | true | Publicado por Intellectual Reserve, correlacionado |
| **doctrinal** | 40 | Pedagógico con base doctrinal — enseña *cómo* enseñar el evangelio |

### Valor KG

**Alto para pedagogía y relaciones cruzadas con otros materiales de enseñanza.**

#### Relaciones KG esperadas

| Relación | from | to | Fuente |
|----------|------|----|--------|
| `SUCCEEDED_BY` | Teaching, No Greater Call | Teaching in the Savior's Way | Church News; curriculum transition 2022 |
| `INFLUENCED_BY` | Teaching, No Greater Call | Teach Ye Diligently (Packer) | Continuidad temática CES |
| `INFLUENCED_BY` | Teaching, No Greater Call | The Charted Course (Clark, 1938) | Filosofía CES fundacional |
| `COMPANION_OF` | Teaching, No Greater Call | Come Follow Me (curso) | TNGC Part G = curso para maestros CFM |
| `REFERENCES` | TNGC | D&C 88:77-80,118 | "Teach ye diligently" — mandato escritural título |
| `REFERENCES` | TNGC | D&C 42:14 | "The Spirit shall be given by the prayer of faith" |
| `REFERENCES` | TNGC | Moroni 7:48 | Charity (Part A, cap. 4) |
| `TEACHES` | TNGC | Teaching by the Spirit (concept) | Part B, sección 2 |
| `TEACHES` | TNGC | Gospel Pedagogy (concept) | Todo el manual |
| `TEACHES` | TNGC | Classroom Discipline (concept) | Part B, caps. 23-24 |
| `TEACHES` | TNGC | Teaching in the Home (concept) | Part D completa |
| `PRODUCED_BY` | TNGC | Church Curriculum Dept | Intellectual Reserve 1999 |
| `DERIVED_FROM` | Teacher Development Skills | TNGC + TITSW | S&I operationalization |

#### Entidades nuevas para gazetteer

- Teaching, No Greater Call (document)
- Teaching the Gospel Course (program — Part G)
- Gospel Pedagogy (concept)

### Deduplicación con material existente

| Material existente | Solapamiento | Valor añadido de TNGC |
|-------------------|-------------|----------------------|
| Teaching in the Savior's Way (2022) | TITSW moderniza los mismos principios | TNGC tiene 48 métodos detallados (Part F) que TITSW condensa. TNGC tiene Part D (hogar) y Part E (liderazgo) que TITSW no cubre |
| Teacher Development Skills | TDS operacionaliza principios | TNGC es la fuente teórica; TDS es la hoja de evaluación |
| Seminary Teacher Manuals | Pedagogía aplicada | TNGC es el marco general; los teacher manuals son aplicación por escritura |

**Conclusión:** El solapamiento con TITSW es parcial — TNGC aporta contenido sustancial
que TITSW no tiene (48 métodos, enseñanza en el hogar, enseñanza en liderazgo, curso
completo de 12 lecciones). No es redundante.

### Riesgos de contenido

- **Terminología datada:** Menciona "home teaching" y "visiting teaching" (pre-2018,
  ahora "ministering"). No es doctrinal pero es anacronismo terminológico.
- **Ningún riesgo doctrinal** — es pedagógico y correlacionado.

### Estimación de volumen

- ~90 páginas web × 2 idiomas = ~180 archivos (.txt + .meta.json)
- Parte F es 1 página grande — puede generar un archivo largo (~5000+ palabras)
- Contenido total estimado: ~80,000–100,000 palabras (EN+ES combinados)

---

## Fuente de descarga

### Sitio oficial de la Iglesia (API v3)

- **Script:** `download_manual.py` — requiere agregar config para TNGC
- **API confirmada:** `GET /study/api/v3/language-pages/type/content?lang={lang}&uri=/manual/teaching-no-greater-call-a-resource-guide-for-gospel-teaching/{slug}`
- **TOC:** `/contents` page lista todos los slugs
- **Bilingüe:** Mismos slugs para EN y ES

### Corpus path propuesto

```
corpus/{lang}/manuals/teaching-no-greater-call/
```

### Meta.json schema

```json
{
  "title": "...",
  "source_url": "https://www.churchofjesuschrist.org/study/manual/teaching-no-greater-call-a-resource-guide-for-gospel-teaching/{slug}?lang={lang}",
  "authority": 60,
  "lang": "eng",
  "manual": "teaching-no-greater-call",
  "part": "A|B|C|D|E|F|G",
  "section": "...",
  "official": true,
  "category": "manuals"
}
```

---

## Decisión

**Prioridad: ALTA**

**Justificación:**
- Manual oficial correlacionado — máxima accesibilidad y calidad de descarga
- Pieza central de la cadena pedagógica (Packer → **TNGC** → TITSW)
- Contenido único que TITSW no reemplaza: 48 m��todos detallados, enseñanza en hogar/liderazgo, curso de 12 lecciones
- Bilingüe completo
- Script existente (`download_manual.py`) — solo agregar config

**Siguiente paso:** Agregar TNGC a `download_manual.py` ManualConfig, dry-run, descargar.

**Estado:** `researched` → listo para `prepared`
