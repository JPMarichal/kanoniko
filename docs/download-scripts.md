# Download Scripts — Church Site Content

How we download content from `churchofjesuschrist.org` into the corpus.

## Architecture

All scripts live in `scripts/` and share common infrastructure from `scripts/lib/church_scraper.py`.

### Two access strategies

| Strategy | Best for | Conversion | Footnotes from |
|----------|----------|-----------|----------------|
| **API v3** (`/study/api/v3/...`) | Prose: manuals, books, talks | pandoc `html→plain` | `content.footnotes` (structured JSON) |
| **HTML direct** | Structured: verses, numbered sections | BeautifulSoup manual | `<li id="note{N}_{letter}">` in footer |

**Decision rule:** If the content is paragraph prose → API + pandoc. If it has verse numbers or deeply structured sections → direct HTML + BS4.

### URL patterns

| Content type | Page URL | API `uri` parameter |
|---|---|---|
| Scriptures | `/study/scriptures/{vol}/{book}/{ch}` | *(use HTML, not API)* |
| Manuals/books | `/study/manual/{slug}/{chapter}` | `/manual/{slug}/{chapter}` |
| Conference | `/study/general-conference/{YYYY}/{MM}/{talk}` | `/general-conference/{YYYY}/{MM}/{talk}` |
| Study aids | `/study/scriptures/{gs\|tg\|bd}/{entry}` | `/scriptures/{gs\|tg\|bd}/{entry}` |

**Key rule:** The API `uri` = page URL path minus the `/study` prefix.

## Scripts inventory

| Script | Content | Strategy | Bilingual | ~Files |
|--------|---------|----------|-----------|--------|
| `download_scriptures.py` | Standard works | External DBs | EN full, ES BOM | ~6,600 |
| `scrape_scriptures.py` | Standard works | HTML | Yes | ~6,600 |
| `scrape_introductions.py` | Scripture front matter | HTML | Yes | ~30 |
| `scrape_study_aids.py` | GEE, TG, BD, JST | HTML+API fallback | Yes | ~3,000 |
| `scrape_jst.py` | JST Appendix | HTML | Yes | ~60 |
| `scrape_handbook.py` | General Handbook | HTML | Yes | ~80 |
| `download_pme.py` | Preach My Gospel 2023 | API | Yes | ~42 |
| `download_conference.py` | Conference talks | API | Yes | varies |
| `download_jesus_the_christ.py` | Jesus the Christ (Talmage) | API | Yes | ~86 |
| `download_christmas_study_plan.py` | Christmas Study Plan (annual) | API | Yes | ~18/year |
| `download_easter_study_plan.py` | Easter / Holy Week Study Plan | API | Yes | ~36 |
| `download_music.py` | Hymns, children's songs, youth, hymn helps | API | Yes (hymn-helps: EN only) | ~1,100 |

## Shared module: `scripts/lib/church_scraper.py`

### Classes

| Class | Purpose |
|-------|---------|
| `ChurchSession` | Rate-limited HTTP session with CA bundle support |
| `ApiPage` | Dataclass holding parsed API response (title, HTML body, footnotes, meta) |
| `TocEntry` | Dataclass for a discovered TOC link (uri, slug, title) |
| `Footnote` | Dataclass for a single footnote (id, marker, text, references) |
| `Checkpoint` | File-based resume checkpoint for large scrapes |
| `DownloadStats` | Simple counter for progress tracking |

### Key functions

| Function | What it does |
|----------|-------------|
| `fetch_api_page(session, uri, lang)` | Fetch one page from API v3 → `ApiPage` |
| `discover_toc_api(session, parent_uri, lang, ...)` | Parse TOC page to find all chapter links |
| `discover_toc_html(session, url, ...)` | Same but via direct HTML fetch |
| `html_to_structured_text(html)` | HTML → plain text via pandoc with heading markers |
| `extract_verses(soup)` | HTML → list of (verse_num, text) |
| `extract_prose(soup)` | HTML → paragraph text (non-verse pages) |
| `extract_footnotes_api(raw)` | API footnotes dict → list[Footnote] |
| `extract_footnotes_html(soup)` | HTML footnotes → list[Footnote] |
| `format_footnotes_text(footnotes)` | Footnotes → endnotes section string |
| `footnotes_to_meta(footnotes)` | Footnotes → meta.json fields (count, refs, full notes) |
| `extract_scripture_refs_from_html(soup)` | Find scripture links in HTML |
| `write_corpus_file(dir, name, text, meta)` | Write .txt + .meta.json pair |
| `add_common_args(parser)` | Add standard --lang, --dry-run, --delay args |

## Footnotes: why they are essential

Footnotes are **not optional metadata** — they are content that must always be downloaded and preserved. They carry:

1. **Scripture cross-references** — the primary source of intertextuality relations in the KG. A footnote saying "See also Isaiah 53:3-5" creates a typed `cross_references` edge.
2. **Historical/linguistic commentary** — context that enriches RAG responses. "The Greek word *agape* used here..." adds doctrinal depth.
3. **See-also links** — connections to related topics, study aids, or other manual chapters.
4. **Variant readings and translation notes** — important for bilingual corpus alignment.

### Where footnotes go

| In `.txt` file | In `.meta.json` |
|----------------|-----------------|
| Appended as endnotes section (separator `---`, header "Notas") | `note_count`, `footnotes` array, `scripture_refs` list |

### Extraction by strategy

- **API route:** `content.footnotes` is a structured dict with `marker`, `text`, `referenceUris` per note. Use `extract_footnotes_api()`.
- **HTML route:** `<li id="note{N}_{letter}">` elements in the page footer. EN uses `note1_a`, ES uses `note1a` (no underscore). Use `extract_footnotes_html()`.

## Bilingual handling

- **Manuals, books, conference:** Same slugs for both `?lang=eng` and `?lang=spa`. Only the lang param changes.
- **Scriptures:** ES uses Spanish book directory slugs (exodus→exodo, psalms→salmos, etc.). Requires `EN_TO_ES_SLUG` mapping.
- **Corpus dirs:** Always `en`/`es` (not `eng`/`spa`). Use `LANG_MAP = {"eng": "en", "spa": "es"}`.

## CLI conventions

All scripts support:

| Flag | Always | Large scrapers only |
|------|--------|---------------------|
| `--lang {eng\|spa}` | Yes (default: both) | |
| `--dry-run` | Yes | |
| `--delay N` | Yes (default: 0.5s) | |
| `--resume` | | Yes |
| `--limit N` | | Yes |
| `--list-only` | | Yes |

## meta.json → KG: structured metadata fields

The ingestion pipeline reads specific meta.json fields and creates typed KG relations automatically (confidence: `metadata`). Populate these fields in every download script where the information is available:

| meta.json field | Type | KG effect |
|-----------------|------|-----------|
| `title` | string | Creates a `work` entity (required for all relations below) |
| `author` | string | `work -[AUTHORED_BY]-> person` — strip year if present ("William W. Phelps, 1844" works) |
| `composer` | string | `work -[COMPOSED_BY]-> person` |
| `tune` | string | `work -[HAS_TUNE]-> concept` |
| `occasion` | string | `work -[ASSOCIATED_WITH]-> concept` |
| `book` | string | `work (chapter) -[PART_OF]-> work (book)` — connects chapters to their parent book |

**Which backlog materials must set `author`:**

| Material | `author` value | KG value |
|----------|----------------|----------|
| Jesus the Christ ✅ already | `"James E. Talmage"` | All 43 chapters linked to Talmage |
| Articles of Faith (Talmage) | `"James E. Talmage"` | High |
| The Great Apostasy (Talmage) | `"James E. Talmage"` | High |
| Teachings of Presidents (series) | `"{President Name}"` e.g., `"Joseph Smith"` | Critical — 22 volumes × prophet |
| Discourses of Brigham Young | `"Brigham Young"` | High |
| Music (hymns/songs) ✅ already | Extracted from page HTML | Per-hymn attribution |

**Materials where `author` should NOT be set** (institutional/committee authorship):
Gospel Principles, Come Follow Me, True to the Faith, General Handbook, Institute Manuals — these have no individual author attribution.

## Checklist de preparación de materiales

**La preparación no está completa hasta que el KG sepa exactamente qué hacer
en la primera indexación.** Cada paso debe completarse antes de correr el script.

---

### Fase 0 — Investigación del material

Antes de tocar código, entender el material en profundidad. **No saltar esta fase.**

0a. **Leer el material** — Acceder al sitio oficial y hojear varios capítulos/entradas
    representativos. No es suficiente leer el TOC.

0b. **Documentar en el backlog** bajo el nombre del material:
    - **Estructura**: cuántas páginas, cómo están organizadas, tipos de secciones
    - **Contenido típico**: ¿Es prosa doctrinal? ¿Comentario bíblico? ¿Narrativa? ¿Preguntas?
    - **Entidades clave**: personas, lugares, conceptos, periodos que aparecen recurrentemente
    - **Relaciones únicas**: ¿Qué puede aportar que NER no infiere? (tipologías, cronologías,
      autoría, secuencias doctrinales, paralelos intertextuales)
    - **Valor teológico**: ¿Por qué es importante para el corpus? ¿Qué preguntas habilita?
    - **Consideraciones especiales**: manejo de autoridad, temas sensibles, caveats

0c. **Identificar entidades nuevas** no cubiertas por el gazetteer actual.

0d. **Identificar relaciones** que el pipeline estándar no puede crear
    (más allá de AUTHORED_BY, PART_OF, CITES, ASSOCIATED_WITH).

> El backlog es el registro de esta investigación. Si no está documentado, no se hizo.

---

### Fase 1 — Download script

1. **Identificar URL** — TOC en `churchofjesuschrist.org/study/manual/{slug}`
2. **Elegir estrategia** — prosa → API v3, versos → HTML directo
3. **Probar API** — `curl ".../study/api/v3/language-pages/type/content?lang=eng&uri=/manual/{slug}/chapter-1"` — confirmar `content.body` sustancial y `content.footnotes`
4. **Verificar bilingüe** — mismo curl con `?lang=spa`
5. **Verificar dónde están las scripture refs** — ¿en `content.footnotes`? ¿inline en body HTML como `<a class="scripture-ref">`? Usar `extract_footnotes_api()` o `extract_scripture_refs_from_html()` según el caso.
6. **Copiar script más cercano** — adaptar slug map, output dir, authority, meta fields
7. **Probar** — `--dry-run --lang eng`, luego `--lang spa`, luego ambos

---

### Fase 2 — KG meta.json fields

8. **Configurar campos KG estándar** — de la tabla de abajo; `_enrich_kg_from_meta` los procesa automáticamente en cada indexación.

9. **Campos estructurados especiales** — si el material produce datos tabulares únicos (e.g., tablas de paralelos, cronologías, listas de eventos):
   - ¿Ya existe soporte en `_enrich_kg_from_meta`? Ver tabla de campos soportados abajo.
   - Si no existe: **añadir el handler en `_enrich_kg_from_meta`** ANTES de indexar.
   - Si es un campo nuevo, añadir también el tipo de relación a `relations.json`.

---

### Fase 3 — KG seed file

*Derivado directamente de la Fase 0 — no se puede escribir sin haber investigado.*

10. **Crear seed file** en `data/kg-seeds/{slug}.json` — ver esquema abajo. Incluye entidades
    y relaciones que el KG debe afirmar ANTES de la extracción NER.
11. **Agregar entidades al gazetteer** — toda persona/concepto nuevo en `entities.json`
    para que NER los detecte en el texto.
12. **Verificar tipos de relación** — si se usa un `predicate` nuevo, añadirlo a `relations.json`.
13. **Actualizar backlog** — añadir sección "KG — relaciones esperadas" bajo el material.

---

### Fase 4 — Validar y marcar `prepared`

14. **Authority** — definir según `docs/authority-model.md`
15. **Cambiar estado a `prepared`** en `03-materials-backlog.md`

> Solo después de completar las fases 0–3 el material está **ready to ingest**.
> La primera indexación debe dejar el KG completo sin intervención manual posterior.
> Marcar `prepared` sin la Fase 0 es incorrecto aunque el script funcione.

---

## Campos KG soportados en `_enrich_kg_from_meta`

| Campo meta.json | Tipo | Relación creada | Quién la usa |
|-----------------|------|-----------------|--------------|
| `title` | string | nodo `work` | todos los materiales |
| `author` | string | `work -[AUTHORED_BY]-> person` | libros, himnos |
| `composer` | string | `work -[COMPOSED_BY]-> person` | himnos |
| `tune` | string | `work -[HAS_TUNE]-> concept` | himnos |
| `occasion` | string | `work -[ASSOCIATED_WITH]-> concept` | himnos |
| `book` | string | `work -[PART_OF]-> work` | capítulos de manuales |
| `scripture_refs` | list[str] | `work -[CITES]-> scripture_reference` | PME, estudio, etc. |
| `parallel_events` | list[dict] | `event -[DESCRIBED_IN]-> scripture_reference` + `scripture_ref -[PARALLEL_ACCOUNT_OF]-> scripture_ref` | Armonía de los Evangelios |
| `events` | list[dict] | `event -[OCCURRED_DURING]-> period` + `event -[PRECEDED_BY]-> event` | Cronología Bíblica |

Si tu material produce un campo estructurado distinto a los de esta tabla,
**debes añadir su handler en `_enrich_kg_from_meta`** en `src/alejandria/ingestion/pipeline.py`.

---

## KG seed file — esquema y workflow

KG seed files (`data/kg-seeds/*.json`) codifican conocimiento de fase de investigación —
entidades y relaciones que el KG debe afirmar **antes** de la extracción NER.
Se aplican al inicio de cada `run()` (incremental) y cada `rebuild_kg()`.

**Cuándo escribir un seed file:**
- Relaciones que NER no puede inferir por co-ocurrencia (tipologías, secuencias doctrinales, autoría)
- Entidades que aparecen pocas veces en texto pero son estructuralmente importantes
- Relaciones inter-volumen conocidas (JTC cap. X → Hebreos Y)

**Esquema:**
```json
{
  "name": "Human-readable name",
  "corpus_pattern": "*/manuals/preach-my-gospel/*",
  "confidence": "curated",
  "entities": [
    { "name": "Canonical Name", "type": "person|place|concept|object|period|work|event", "aliases": ["..."] }
  ],
  "relations": [
    {
      "subject": "entity name", "subject_type": "work",
      "predicate": "AUTHORED_BY",
      "object": "entity name", "object_type": "person",
      "source_ref": "Scripture/source note"
    }
  ]
}
```

Seeds son idempotentes (Neo4j MERGE). Ver `data/kg-seeds/README.md` para esquema completo.

## Volume slug mapping (site ≠ corpus)

| Site slug | Corpus slug |
|-----------|-------------|
| `bofm` | `bom` |
| `dc-testament` | `dc` |
| `ot` | `ot` |
| `nt` | `nt` |
| `pgp` | `pgp` |
