# Fase 0 — Church Site Materials (Discovered 2026-04)

> Análisis de contenido y relaciones KG. Extraído de la reorganización del backlog (2026-04-05).

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
