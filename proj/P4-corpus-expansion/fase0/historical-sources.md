# Fase 0 — Fuentes Históricas

> Análisis de contenido y relaciones KG. Extraído de la reorganización del backlog (2026-04-05).

---

## Tier 3 — Fuentes Históricas (authority=30–40)

### 13. Discourses of Brigham Young

**Estado:** `ingested` — 42 capítulos EN en `corpus/en/books/discourses-brigham-young/` (Gutenberg)

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
