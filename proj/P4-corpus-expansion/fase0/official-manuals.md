# Fase 0 — Manuales Oficiales de la Iglesia

> Análisis de contenido y relaciones KG. Extraído de la reorganización del backlog (2026-04-05).

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

## Descubiertos en survey del sitio (Tier 2b, 2026-04)

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
