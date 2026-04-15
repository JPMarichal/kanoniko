# Fase 0 — Interpreter: A Journal of Latter-day Saint Faith and Scholarship

> Análisis de contenido, authority y valor KG. Investigación web: 2026-04-15.

---

## Paso 1 — Investigación editorial

### Historia editorial

- **Nombre completo:** *Interpreter: A Journal of Latter-day Saint Faith and Scholarship*
  (hasta Vol. 29/2018: *Interpreter: A Journal of Mormon Scripture*)
- **Fundación:** 2012 por **Daniel C. Peterson** (BYU, estudios islámicos y árabes).
  Peterson había sido despedido como editor del FARMS Review en 2012; fundó Interpreter
  como vehículo independiente para continuar la tradición de scholarship apologético.
- **Modelo:** Journal académico peer-reviewed, acceso abierto (Open Access), sin costo
  para autores ni lectores. Publicación continua (rolling) — artículos salen individualmente
  cada viernes, se agrupan en volúmenes al completarse.
- **Volúmenes:** 68 al momento de la investigación (Vol. 68, 2026, aún en compilación).
  Volúmenes 1-3 corresponden a 2012; múltiples volúmenes por año.
- **Artículos estimados:** ~580+ artículos por ~208 autores primarios (dato de 2024).
  Con el ritmo actual (~8-12 artículos/volumen), el total 2026 supera los 600.
- **Formato:** HTML completo en el sitio + descarga en PDF, ePub, Kindle. Volúmenes
  completos disponibles en paperback (Amazon, MagCloud) y PDF compilado.
- **CDN de PDFs:** `cdn.interpreterfoundation.org/jnlpdf/Interpreter-Volume-{N}-PDF.pdf`
  (volúmenes completos) y PDFs individuales con patrón
  `{author}-v{vol}-{year}-pp{pages}-PDF.pdf`.

### Contexto institucional

- **NO es publicación oficial de la Iglesia.** Es una fundación independiente 501(c)(3).
- **NO está afiliada a BYU** (a diferencia de RSC o BYU Studies), aunque muchos autores
  son profesores de BYU.
- **Posición:** Se ubica en el espectro apologético-académico. Más riguroso que FAIR,
  más apologético que BYU Studies. Comparable a la antigua FARMS Review.
- **Recepción:** Bien citado en círculos SUD académicos. Algunos artículos son citados
  en publicaciones de RSC BYU y BYU Studies. No citado por publicaciones oficiales de
  la Iglesia.
- **Política editorial:** Peer-reviewed (doble ciego según su descripción). Aceptan
  submissions externas. El comité editorial incluye nombres conocidos del scholarship SUD.

### Audiencia y alcance

- **Audiencia:** Miembros académicamente orientados, apologistas, estudiantes de
  religión, investigadores. Tono accesible pero con aparato académico completo.
- **Alcance temático:** Exégesis escritural (énfasis Libro de Mormón), estudios
  lingüísticos, historicidad, evidencias del Libro de Mormón, templo, Libro de Abraham,
  profecía, tipología, intertextualidad, respuestas a críticos.
- **Idioma:** Solo inglés.

### Autores destacados (con volumen de contribución)

| Autor | Artículos | Especialidad |
|-------|-----------|-------------|
| Matthew L. Bowen | ~59 | Onomástica hebrea, Libro de Mormón |
| Jeff Lindsay | ~24 | Apologética, Libro de Mormón |
| Brant A. Gardner | ~24 | Mesoamérica, traducción del LdM |
| Daniel C. Peterson | ~20+ | Estudios islámicos, apologética general |
| Stanford Carmack | ~15+ | Lingüística del inglés moderno temprano en el LdM |
| John Gee | ~10+ | Egiptología, Libro de Abraham |
| William J. Hamblin | ~10+ | Historia militar antigua, templo |
| Stephen D. Ricks | ~10+ | Estudios del Cercano Oriente, ley bíblica |

---

## Paso 2 — Análisis de contenido y valor para el corpus

### Estructura del contenido

El journal publica cuatro categorías de contenido:

| Categoría | Descripción | Valor corpus | Incluir |
|-----------|-------------|-------------|---------|
| **Article** | Artículo académico peer-reviewed completo (5,000-20,000 palabras) | ALTO | **Sí** |
| **Essay** | Ensayo más breve, menos formal (2,000-5,000 palabras) | ALTO | **Sí** |
| **Book Review** | Reseña de libro ajeno (1,000-5,000 palabras) | BAJO — opinión sobre obra de terceros | **No** |
| **Review Essay** | Reseña extendida / ensayo crítico sobre un libro (3,000-10,000 palabras) | MEDIO-BAJO — similar a book review | **No** |

**Filtro:** Articles + Essays. Excluir Book Reviews y Review Essays.

### Índices disponibles para scraping

El sitio ofrece 6 índices, todos bajo `/journal/indexes/`:

| Índice | URL | Utilidad para scraping |
|--------|-----|----------------------|
| Volume Index | `journal-volume-index` | **Principal** — lista artículos por volumen |
| Title Index | `journal-title-index` | Alfabético, filtro A-Z dinámico (React) |
| Author Index | `journal-author-index` | Por autor |
| Topic Index | `journal-topic-index` | Por tema |
| Scripture Index | `journal-scriptural-references` | Por referencia escrituraria |
| Chronological | `journal-cron-index` | Por fecha |

**Nota técnica:** Los índices usan React (Next.js) con carga dinámica. Las páginas de
volumen individual (`/journal/volume/volume-{N}-{year}`) sí listan artículos con
títulos, autores, páginas y categoría. Son el mejor punto de entrada para enumerar
artículos.

### Estructura de un artículo (análisis de scraping)

Basado en inspección de artículos reales:

- **URL patrón:** `interpreterfoundation.org/journal/{slug}` (redirecciones desde
  `journal.interpreterfoundation.org/{slug}`)
- **Título:** Heading principal `<h1>`
- **Autor:** Sección de perfil con link `/all/author/{author-slug}`
- **Abstract:** Párrafo(s) en itálica antes del cuerpo principal
- **Cuerpo:** HTML semántico con secciones, subheadings, blockquotes
- **Notas al pie:** Inline con anclas `[sdfootnote{N}sym]` → `[sdfootnote{N}anc]`
- **Metadata visible:** Volumen, páginas, categoría, formatos disponibles
- **PDF individual:** `cdn.interpreterfoundation.org/jnlpdf/{author}-v{vol}-{year}-pp{pages}-PDF.pdf`

### Authority model

**authority = 25**

Justificación:
- (+) Peer-reviewed, aparato académico completo, autores con credenciales
- (+) Acceso abierto, citado en literatura académica SUD
- (−) No es publicación oficial de la Iglesia
- (−) No afiliado a BYU institucionalmente
- (−) Orientación apologética explícita — no neutral académicamente
- (−) Algunos artículos son más especulativos que otros (varianza alta)
- Comparable a RSC BYU (25-35) en el extremo inferior, por el sesgo apologético

> Para comparación: RSC BYU = 25-35, BYU Studies = 25-35, FAIR = 15-20,
> Gutenberg/MTP = 40-50 (obras clásicas de profetas), Journal of Discourses = 20.

### Valor KG

**ALTO.** Los artículos de Interpreter son densos en:

- **Intertextualidad:** conexiones entre pasajes del Libro de Mormón, Biblia, PGP
  (es probablemente la fuente más rica en relaciones `ALLUDES_TO` e `INTERPRETS`)
- **Onomástica:** Bowen (59 artículos) analiza nombres hebreos del LdM — entidades
  de personas con etimología y significado doctrinal
- **Tipología:** relaciones `TYPE_OF` entre figuras del AT y Cristo, entre
  narrativas del LdM y la Biblia
- **Geografía del LdM:** artículos sobre ubicaciones propuestas
- **Autoría:** cada artículo genera relación `AUTHORED` + `PUBLISHED_IN` (volumen)
- **Relaciones doctrinales:** artículos temáticos cubren convenios, templo,
  sacerdocio, expiación, desde perspectiva escritural

### Deduplicación con corpus existente

- **No duplica contenido existente.** El journal es material original — análisis
  académico, no reproducción de textos.
- **Complementa:** Los artículos citan extensamente las escrituras (ya en corpus),
  conferencia general, y libros que ya tenemos (Jesus the Christ, Talmage, Roberts).
  El valor está en el análisis, no en el texto citado.
- **Posible solapamiento mínimo:** Algunos artículos de conferencias Interpreter
  pueden duplicar proceedings ya publicados en RSC, pero serían versiones distintas.

### Riesgos de contenido

1. **Hipótesis especulativas:** Algunos artículos proponen teorías no mainstream
   (geografía del LdM, lingüística del inglés moderno temprano). El authority=25
   refleja esto.
2. **Tono apologético:** Algunos artículos son respuestas directas a críticos. Útil
   como fuente, pero el sistema no debe presentarlos como doctrina oficial.
3. **Varianza de calidad:** Al ser 600+ artículos por 200+ autores, la calidad varía.
   El peer review mitiga pero no elimina esto.

### Estimación de volumen

| Métrica | Estimación |
|---------|-----------|
| Artículos totales (Articles + Essays) | ~500 (excluyendo reviews) |
| Palabras promedio por artículo | ~8,000-10,000 |
| Palabras totales estimadas | ~4-5 millones |
| Archivos resultantes | ~500 .txt + ~500 .meta.json |
| Chunks estimados (a 512 tokens) | ~12,000-15,000 |
| Tiempo de indexación estimado (GPU) | ~2-3 horas |

### Ruta corpus propuesta

```
corpus/en/books/interpreter-journal/{slug}.txt
corpus/en/books/interpreter-journal/{slug}.meta.json
```

Donde `{slug}` es el slug del artículo en la URL (ej.
`the-book-of-mormon-witnesses-and-their-challenge-to-secularism`).

**Alternativa considerada y descartada:** `vol-{NN}/{slug}.txt` — añade una capa
de directorio innecesaria; el volumen se captura en el meta.json.

### meta.json schema propuesto

```json
{
  "title": "The Book of Mormon Witnesses and Their Challenge to Secularism",
  "author": "Daniel C. Peterson",
  "author_slug": "dan",
  "volume": 27,
  "year": 2017,
  "pages": "vii-xxviii",
  "category": "article",
  "source_url": "https://interpreterfoundation.org/journal/the-book-of-mormon-witnesses-and-their-challenge-to-secularism",
  "pdf_url": "https://cdn.interpreterfoundation.org/jnlpdf/peterson-v27-2017-ppvii-xxviii-PDF.pdf",
  "abstract": "...",
  "authority": 25
}
```

---

## Estrategia de descarga

### Paso 1 — Enumerar artículos

Recorrer las páginas de volumen `/journal/volume/volume-{N}-{year}` para
N = 1..68. Extraer de cada volumen: título, autor, slug (URL), páginas,
categoría.

**Problema:** Las páginas de volumen son React (Next.js) con rendering dinámico.
Opciones:
- (a) **Playwright/Selenium** para renderizar JS — fiable pero más lento
- (b) **API interna de Next.js** — inspeccionar las llamadas XHR del sitio para
  encontrar el endpoint JSON subyacente
- (c) **Sitemap XML** — verificar si existe `/sitemap.xml` con URLs de artículos

**Recomendación:** Investigar (b) primero — los sitios Next.js suelen tener un
`_next/data/` endpoint. Si no, (a) con Playwright.

### Paso 2 — Filtrar

Excluir artículos con `category` = "Book Review" o "Review Essay".

### Paso 3 — Descargar artículos

Para cada artículo:
1. Fetch HTML de la URL del artículo
2. Extraer: título, autor, abstract, cuerpo, notas al pie, metadata
3. Convertir a texto plano limpio (markdown o texto con notas al pie al final)
4. Generar `.meta.json`
5. Guardar en `corpus/en/books/interpreter-journal/`

### Paso 4 — Verificación

- Contar archivos vs artículos esperados
- Spot-check de 5 artículos: verificar que el texto completo está presente
- Verificar que footnotes se preservaron
- Verificar que no se incluyeron book reviews

---

## Próximos pasos

1. ~~Fase 0~~ (este documento)
2. **Exploración técnica:** Inspeccionar la API del sitio (XHR, sitemap, _next/data)
   para determinar la mejor estrategia de enumeración
3. **Script:** `scripts/download_interpreter.py`
4. **Descarga + commit**
5. **Indexación** (pipeline estándar)
