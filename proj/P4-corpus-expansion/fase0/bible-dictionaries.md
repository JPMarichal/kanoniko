# Fase 0 — Diccionarios Bíblicos Clásicos

> Análisis de contenido y relaciones KG. Extraído de la reorganización del backlog (2026-04-05).

> Obras de referencia protestantes del siglo XIX, dominio público.
> NO son fuentes doctrinales SUD. Valor principal: contexto histórico/geográfico/
> arqueológico y alimentación del KG con definiciones y etimologías.
> La Iglesia SUD produce sus propias ayudas (Bible Dictionary, GEE, TG) que
> ya están en el corpus con authority=50-55. Estas obras externas complementan
> con profundidad enciclopédica lo que las ayudas oficiales cubren brevemente.

## Easton's Bible Dictionary (1897)

**Estado:** `ingested` (corpus, pendiente indexación)

**Fase 0 — Análisis de contenido:**

- **¿Qué es?** Diccionario bíblico compacto con ~3,964 entradas: definiciones
  cortas tipo diccionario + artículos más largos tipo enciclopedia. Cubre
  personas, lugares, palabras, costumbres, geografía, historia natural.
- **¿Quién lo produjo?** Matthew George Easton (1823–1894), ministro
  presbiteriano escocés. Publicado póstumamente por Thomas Nelson en 1897.
- **¿Cuándo?** 1897 (3ª edición, la más difundida).
- **¿Para quién?** Estudiantes de la Biblia en general; nivel accesible.
- **¿Cómo referenciado?** Ampliamente distribuido en formato digital; incluido
  en casi todo software bíblico (SwordSearcher, e-Sword, Logos, Accordance).
  No es académico de primer nivel pero sí el más popular para uso personal.
- **Relaciones con corpus existente:** Entradas sobre personas/lugares bíblicos
  se cruzan con nuestro Bible Dictionary SUD (1,275 entradas) y TG/GEE.
  Easton es más extenso (3,964 vs 1,275) y cubre temas que el BD SUD omite.
- **Limitaciones:** Teología "decidedly Protestant" (CCEL). Interpretaciones
  del siglo XIX sin arqueología moderna (no conoce Qumrán, Nag Hammadi, etc.).
  No incluye perspectiva de la Restauración. Algunos artículos reflejan
  anti-catolicismo de la época.

**Source:** CCEL — ThML XML parseado a `corpus/en/reference/easton-bible-dictionary/`

---

## Smith's Bible Dictionary (1884)

**Estado:** `ingested` (corpus, pendiente indexación)

**Fase 0 — Análisis de contenido:**

- **¿Qué es?** Diccionario bíblico enciclopédico con ~4,556 entradas.
  Originalmente 3 volúmenes (1857), condensado en 1 volumen (1884).
  Cubre antigüedades, biografías, geografía e historia natural.
- **¿Quién lo produjo?** William Smith (1813–1893), lexicógrafo y clasicista
  inglés. Contribuyeron Harold Browne (obispo de Ely), Charles Ellicott
  (obispo de Gloucester), J.B. Lightfoot (Cambridge). "The fruit of the
  ripest biblical scholarship of England" (reseña original).
- **¿Cuándo?** 1ª ed. 1857, edición popular 1884.
- **¿Para quién?** Público general educado + estudiantes de seminario.
- **¿Cómo referenciado?** Considerado un clásico fundacional; "required
  reference book for any good study library" (Bible History). Más
  académico que Easton pero menos profundo que Hastings.
- **Relaciones:** Similar a Easton pero con artículos más largos para
  temas geográficos y arqueológicos. Complementa bien el BD SUD.
- **Limitaciones:** Mismo sesgo temporal (pre-Qumrán). Perspectiva anglicana
  de la era victoriana. Algunos artículos superados por descubrimientos
  posteriores (geografía de Palestina, cronología de los patriarcas).

**Source:** CCEL — ThML XML parseado a `corpus/en/reference/smith-bible-dictionary/`

---

## Hitchcock's Bible Names Dictionary (1869)

**Estado:** `ingested` (corpus, pendiente indexación)

**Fase 0 — Análisis de contenido:**

- **¿Qué es?** Diccionario etimológico compacto de 2,614 nombres propios
  bíblicos con sus significados en hebreo/griego. Formato: `Nombre, significado`.
  Extraído de "Hitchcock's New and Complete Analysis of the Holy Bible."
- **¿Quién lo produjo?** Roswell Dwight Hitchcock (1817–1887), profesor de
  historia eclesiástica en Union Theological Seminary, Nueva York.
- **¿Cuándo?** 1869.
- **¿Para quién?** Estudiantes de la Biblia, predicadores que necesitan
  etimologías rápidas para sermones/estudios.
- **¿Cómo referenciado?** "Though first published in 1869, Hitchcock's
  scholarship of the Hebrew language still measures up to contemporary
  standards" (CCEL). Incluido en múltiples plataformas bíblicas digitales.
- **Relaciones:** Valor único para el KG — cada entrada es un nombre propio
  con significado etimológico. Se cruza directamente con nuestros gazetteers
  (personas, lugares, pueblos). Puede enriquecer nodos existentes con campo
  `etymology` o `name_meaning`.
- **Limitaciones:** Solo nombres — no hay definiciones ni contexto. Algunas
  etimologías son especulativas o basadas en folk etymology del siglo XIX
  (el hebreo bíblico tiene muchos hapax legomena). No incluye nombres
  del Libro de Mormón ni D&C.

**Source:** CCEL — texto plano parseado a `corpus/en/reference/hitchcock-bible-names/`

---

## International Standard Bible Encyclopedia — ISBE (1915)

**Estado:** `ingested` (corpus, pendiente indexación)

**Fase 0 — Análisis de contenido:**

- **¿Qué es?** Enciclopedia bíblica exhaustiva en 5 volúmenes con ~10,121
  entradas por 200+ académicos. La obra de referencia bíblica protestante
  más completa en dominio público. Artículos firmados, algunos de varias
  páginas, con análisis detallado.
- **¿Quién lo produjo?** Editor general: James Orr (1844–1913), teólogo
  reformado escocés. Editores asociados: John Nuelsen, Edgar Mullins,
  Morris Evans, Melvin Grove Kyle. Contribuyentes notables: B.B. Warfield,
  A.T. Robertson, Archibald Alexander.
- **¿Cuándo?** Publicado 1915 por Howard-Severance Co., Chicago. Completado
  1939. Creado explícitamente para contrarrestar el impacto del higher
  criticism liberal.
- **¿Para quién?** Pastores, profesores de seminario, académicos.
- **¿Cómo referenciado?** Stephen Motyer (1984): "great solid worth...
  seriously commend this encyclopedia." Conservadurismo "broad, main-line
  evangelicalism." Sigue siendo la enciclopedia protestante de referencia
  gratuita más citada. Existe edición revisada (Bromiley, 1979-1995)
  con copyright.
- **Relaciones:** Artículos largos sobre personas, lugares, doctrinas,
  costumbres — alimenta directamente el KG con relaciones curadas en
  prosa. Se cruza con los 3 diccionarios menores + nuestro BD SUD.
  Cubre temas que ninguno de los otros tiene (arqueología, lingüística,
  historia de manuscritos, cronología detallada).
- **Limitaciones:** Perspectiva evangelical conservadora de principios del
  s. XX — anti-higher-criticism explícito (Orr). "Dogmatic use of the
  Bible" (Motyer). Arqueología desactualizada (pre-Dead Sea Scrolls,
  pre-Ebla, pre-Ugarit). Artículos largos pero a veces apologéticos
  más que descriptivos.

**Source:** internationalstandardbible.com — HTML scrapeado a `corpus/en/reference/isbe/`

---

## Hastings' Dictionary of the Bible (1898)

**Estado:** `ingested` (corpus, pendiente indexación — descarga en curso)

**Fase 0 — Análisis de contenido:**

- **¿Qué es?** Enciclopedia bíblica en 5 volúmenes (4 + índice) con 5,915
  entradas firmadas, algunas de varias páginas. Descrito como "better
  described as an encyclopaedia" (Wikipedia). Cubre personas, lugares,
  antigüedades, arqueología, teología bíblica, ética, palabras arcaicas
  de las versiones inglesas.
- **¿Quién lo produjo?** Editor: James Hastings (1852–1922). Asistentes:
  John A. Selbie, A.B. Davidson, S.R. Driver, H.B. Swete — los nombres
  más importantes del biblical scholarship británico de la época.
  194 autores de artículos, principalmente del Reino Unido.
- **¿Cuándo?** Volúmenes publicados 1898–1904.
- **¿Para quién?** Académicos y pastores; nivel más técnico que Easton/Smith.
- **¿Cómo referenciado?** "For nearly a century, lay people and scholars
  alike have valued the authoritative contents" (Logos). Representa la
  mainstream scholarship de su época — acepta higher criticism moderado
  (documentary hypothesis), a diferencia de ISBE que la combate. "Full
  account taken of literary criticism and archaeological discovery."
- **Relaciones:** Complemento ideológico de ISBE — donde ISBE es
  conservador/apologético, Hastings es crítico/académico. Juntos dan
  el espectro completo del scholarship de 1900. Se cruza con los mismos
  temas pero desde perspectiva más analítica.
- **Limitaciones:** 194 autores = variación en calidad. Perspectiva
  protestante británica de la era eduardiana. Higher criticism de la
  época está en parte superado. Encoding issues (caracteres hebreos/
  griegos transliterados de forma inconsistente en la versión digital).

**Source:** bibleportal.com — HTML scrapeado a `corpus/en/reference/hastings-dictionary-of-the-bible/`

---

## Análisis comparativo — las 5 obras como conjunto

| Dimensión | Easton | Smith | Hitchcock | ISBE | Hastings |
|-----------|--------|-------|-----------|------|----------|
| Entradas | 3,964 | 4,556 | 2,614 | 10,121 | 5,915 |
| Profundidad | Media | Media | Mínima (solo nombres) | Alta | Alta |
| Perspectiva teológica | Presbiteriana | Anglicana | N/A | Evangelical conservador | Mainstream crítico |
| Rigor académico | 60 | 65 | 55 | 75 | 80 |
| Arqueología | Básica | Básica | N/A | Detallada (1915) | Detallada (1900) |
| Año | 1897 | 1884 | 1869 | 1915 | 1898 |
| Valor KG | Definiciones, refs | Definiciones, geografía | Etimologías directas | Artículos enciclopédicos | Análisis crítico |

**Valor conjunto para Alejandría:**
Las 5 obras no compiten — se complementan en una pirámide:
1. **Hitchcock** (base) → etimologías de nombres → enriquece nodos KG existentes
2. **Easton + Smith** (nivel medio) → definiciones accesibles → contexto rápido para RAG
3. **ISBE + Hastings** (nivel superior) → artículos enciclopédicos → profundidad para queries complejas

Las 5 juntas suman ~27K entradas con ~80% de solapamiento en lemas pero contenido
complementario. El RAG puede citar múltiples fuentes para un mismo tema.

**Relación con ayudas SUD existentes:**
- Nuestro Bible Dictionary SUD (1,275 entradas, authority=50) es la fuente oficial.
- Estas obras externas NUNCA deben tener mayor authority que las ayudas SUD.
- El RAG debe priorizar: escritura > BD SUD/GEE/TG > Easton/Smith > ISBE/Hastings.
- El valor de las obras externas es profundidad y cobertura, no autoridad.

## KG — Paso 4: Análisis de relaciones y pre-seed

**Patrón diferenciado:** Estas obras son _fuentes de definiciones_, no narrativas.
No se pre-seedean relaciones individuales (serían ~27K). En cambio:

**Relaciones automáticas (pipeline las genera sin pre-seed):**
- `MENTIONS` — NER detecta entidades en definiciones → link chunk↔entity
- `AUTHORED_BY` — meta.json ya incluye autor → pipeline crea arista
- `REFERENCES` — scripRef parseadas en el XML (Easton/Smith) → intertextualidad

**Relaciones estructurales (ya implícitas en `authority.py` + `meta.json`):**
- `category: reference` → el pipeline asigna authority=15, context=external-reference
- Cada letra (A.txt, B.txt...) → un chunk group con ~150-650 entries

**Pre-seed manual recomendado (futuro, no bloqueante):**
No se requiere pre-seed Cypher para estas obras. El valor viene del NER
automático sobre definiciones ricas en entidades. Sin embargo, para
enriquecimiento futuro del KG:

| Enrichment | Source | Target KG field | Método |
|------------|--------|-----------------|--------|
| Etimología de nombres | Hitchcock 2,614 | `name_meaning` en nodos person/place | Script batch post-indexación |
| Cross-refs a escritura | Easton/Smith scripRef | `REFERENCES` edges | Automático vía pipeline |
| Definiciones complementarias | ISBE/Hastings | Ninguno — vive en FTS/semántico | Pipeline estándar |

**Nota:** `data/gazetteers/hitchcocks_bible_names.csv` ya existe con los mismos
2,614 nombres. El corpus en `reference/hitchcock-bible-names/` añade la misma
info como texto searcheable (FTS + embeddings), no duplica el gazetteer.

**Conclusión paso 4:** No se requiere pre-seed Cypher. Las relaciones emergen
del pipeline estándar. El valor KG principal es que las definiciones mencionan
entidades que el NER ya reconoce, generando miles de edges `MENTIONS`
automáticamente.
