# Fase 0 — Seminary & Institute Materials

> Análisis de contenido y relaciones KG. Extraído de la reorganización del backlog (2026-04-05).

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
