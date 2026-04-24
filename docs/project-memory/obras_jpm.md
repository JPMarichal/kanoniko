# Catálogo — Obras de Juan Pablo Marichal Catalán (JPM)

Relación de obras propias del usuario incorporadas al corpus, para uso futuro en búsquedas, citaciones y análisis cruzados. Todas en español, `authority=25`, `context=book-private`, autor independiente SUD.

## Incorporadas al corpus (12)

### Artículos doctrinales / análisis (`corpus/es/books/`)

| Slug | Título | Tema / nota |
|------|--------|-------------|
| `antecedentes-vida-moises-jpm` | Antecedentes de la vida de Moisés | Infancia y adopción egipcia de Moisés. |
| `apuntes-convenio-abraham-jpm` | Apuntes sobre el Convenio de Abraham (Forma T pequeña) | "Parte de Dios / Parte del hombre", Génesis 17, Kimball. |
| `autobiografia-lucas-hechos-jpm` | La autobiografía de Lucas en el Libro de Hechos | Análisis de los "we-passages" del NT. |
| `creacion-no-ex-nihilo-jpm` | La creación de la tierra no fue a partir de la nada | Análisis del verbo hebreo `bará` en Gén 1:1. |
| `escrituras-perdidas-jpm` | Escrituras perdidas | Libros mencionados en la Biblia ausentes del canon. |
| `esquema-metodo-tematico-ensenanza-jpm` | Esquema del método temático de enseñanza | Principio de prerrequisitos (Boyd K. Packer, *Teach Ye Diligently*). |
| `identidad-lamanitas-jpm` | Identidad de los lamanitas | Carta al Hno. Barrera sobre miembros latinoamericanos y el linaje lamanita. |
| `levirato-jpm` | La ley del levirato | Nota. Orígenes del levirato en el Cercano Oriente. |

### Discursos (`corpus/es/discourses/`)

| Slug | Título | Contexto |
|------|--------|----------|
| `articulo-fe-10-jpm` | El Artículo de Fe número 10 | Discurso. Complejidad del décimo AF. |
| `honradez-sentido-congruencia-jpm` | La honradez y el sentido interior de congruencia | Discurso de estaca. Honestidad, verdad, responsabilidad, convenios. |

### Biografías (`corpus/es/biographies/`)

| Slug | Título | Sujeto |
|------|--------|--------|
| `datos-biograficos-amasa-lyman-jpm` | Datos biográficos de Amasa M. Lyman | Q12 1842-1870; ficha compilada de *Church Chronology* (Jenson 1914). |

### Ayudas de estudio (`corpus/es/study-aids/`)

| Slug | Título | Contenido |
|------|--------|-----------|
| `capitulos-versiculos-clave-jpm` | Capítulos y versículos clave | Tabla pan-bíblica (palabra clave, capítulos clave, versículos clave por libro). |

## Pendientes de procesamiento posterior

### Formas T en formato solo-imagen (7) — `epub/_imagen_pendientes/`

Epubs solo-imagen (cover + JPG sin capa de texto). Requieren OCR o fuente markdown/docx original para procesarse con el skill Forma T (`/forma-t`) y portarse a `prods/formas-t/`.

- Forma T Ley Civil y Constitución
- Forma T Libros perdidos
- Forma T Pasajes bíblicos contradictorios
- Forma T, La Iglesia premosaica
- Forma T, Secretarios de la Iglesia
- Forma T, conocer a Dios
- Forma T, varios temas

### Biblicomentarios (1) — `epub/_imagen_pendientes/`

- Biblicomentarios, temas propuestos — epub solo-imagen. Pendiente OCR o fuente original. Según descripción del usuario: son **artículos** que deben evaluarse por contenido, no por título.

## Excluidas (skip)

| Obra | Razón |
|------|-------|
| Biblia Reina Valera SUD | Republicación del texto canónico; ya en `corpus/es/scriptures/`. |
| Doctrina y Convenios | Republicación del texto canónico; ya en `corpus/es/scriptures/`. |
| Apuntes para la instrucción de Reunión de Quórum | Notas de uso personal; sin valor de corpus general. |

## Uso futuro

- **Búsqueda**: filtrar por `author: "Juan Pablo Marichal Catalán"` o `tag: jpm`.
- **Formas T**: cuando el usuario provea las fuentes originales, ejecutar skill `/forma-t` y portar a `prods/formas-t/` (fuera del corpus).
- **Biblicomentarios**: una vez OCR'd o recuperada fuente, evaluar cada artículo individualmente por tema (NO generalizar).
- **Ampliaciones**: obras futuras del usuario seguirán la misma convención (`authority=25`, `tag: jpm`, `context=book-private`).

---

Actualización: 2026-04-24. Processed en P4-corpus-expansion batch final junto con Ernesto Pelé (alias de Ernest C. Pyle).
