# Catálogo — Obras de Juan Pablo Marichal Catalán (JPM)

Relación de obras propias del usuario incorporadas al corpus, para uso futuro en búsquedas, citaciones y análisis cruzados. Todas en español, `authority=25`, `context=book-private`, autor independiente SUD.

**Mantener siempre actualizado.** Añadir aquí cualquier obra nueva de JPM al momento de incorporarla.

## Incorporadas al corpus (18)

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
| `lucas-biografo-maria-jpm` | Lucas como el biógrafo de María | Análisis estadístico de menciones marianas en el NT; Lucas dedica más versículos que los demás evangelistas. |
| `patronimicos-jpm` | Patronímicos | Nota sobre la genealogía del sacerdocio (DyC 107): orden de Melquisedec → Enoc → Hijo Unigénito. |
| `pendon-a-las-naciones-jpm` | Pendón a las naciones | Símbolo isaiánico (bandera/estandarte); significado en profecías de recogimiento. |
| `significado-ultimas-palabras-jesus-jpm` | El significado de las últimas palabras de Jesús | Carta a los élderes Espino. Compilación de citas y pasajes sobre la crucifixión. |

### Discursos (`corpus/es/discourses/`)

| Slug | Título | Contexto |
|------|--------|----------|
| `articulo-fe-10-jpm` | El Artículo de Fe número 10 | Discurso. Complejidad del décimo AF. |
| `honradez-sentido-congruencia-jpm` | La honradez y el sentido interior de congruencia | Discurso de estaca. Honestidad, verdad, responsabilidad, convenios. |
| `nuestra-ofrenda-sacramental-jpm` | Nuestra ofrenda en la reunión sacramental | Discurso, Barrio Plateros, 18 de junio de 2017. |

### Biografías (`corpus/es/biographies/`)

| Slug | Título | Sujeto |
|------|--------|--------|
| `datos-biograficos-amasa-lyman-jpm` | Datos biográficos de Amasa M. Lyman | Q12 1842-1870; ficha compilada de *Church Chronology* (Jenson 1914). |

### Ayudas de estudio (`corpus/es/study-aids/`)

| Slug | Título | Contenido |
|------|--------|-----------|
| `capitulos-versiculos-clave-jpm` | Capítulos y versículos clave | Tabla pan-bíblica (palabra clave, capítulos clave, versículos clave por libro). |
| `resena-general-jpm` | Reseña General | Índice pan-bíblico por libro: autor y fecha, propósito editorial, temas y estructura literaria, estructura, curiosidades, comentarios, citas, referencias. 90 capítulos. |

## Pendientes de procesamiento posterior (OCR/fuente)

Todas en `epub/_imagen_pendientes/`. Son epubs solo-imagen (`cover + JPG` sin capa de texto). Requieren OCR o recuperación de la fuente markdown/docx original.

### Formas T solo-imagen (7)

Cuando se obtengan fuentes, ejecutar skill `/forma-t` y portar a `prods/formas-t/` (fuera del corpus).

- Forma T Ley Civil y Constitución
- Forma T Libros perdidos
- Forma T Pasajes bíblicos contradictorios
- Forma T, La Iglesia premosaica
- Forma T, Secretarios de la Iglesia
- Forma T, conocer a Dios
- Forma T, varios temas

### Biblicomentarios (1)

- Biblicomentarios, temas propuestos — colección de **artículos** que deben evaluarse **uno por uno por contenido**, nunca por título (directiva explícita del usuario).

## Excluidas (skip)

| Obra | Razón |
|------|-------|
| Biblia Reina Valera SUD | Republicación del texto canónico; ya en `corpus/es/scriptures/`. |
| Doctrina y Convenios | Republicación del texto canónico; ya en `corpus/es/scriptures/`. |
| Libro de Mormón, El | Republicación del texto canónico; ya en `corpus/es/scriptures/`. |
| Libro de Mormón (versión anotada), El | Variante anotada de la republicación canónica. |
| Triple combinación | Republicación de BoM+DyC+PGP canónicos. |
| Apuntes para la instrucción de Reunión de Quórum | Notas de uso personal; sin valor de corpus general. |
| Los miembros de la Iglesia | Fragmento citado de una declaración de la Primera Presidencia (1992) sobre participación cívica; no es obra original. |
| Ya lo leí BOM | Herramienta de seguimiento de lectura (checklist); no contenido textual. |
| Writing a blog post | Tutorial genérico en inglés sobre redacción para blog; sin contenido SUD. |

## Uso futuro

- **Búsqueda en corpus**: filtrar por `author: "Juan Pablo Marichal Catalán"` o `tag: jpm`.
- **Protocolo de actualización**: cuando se incorpore, excluya o posponga cualquier obra nueva de JPM, **añadirla a este catálogo en el mismo commit**.
- **Formas T**: cuando el usuario provea las fuentes originales, ejecutar skill `/forma-t` y portar a `prods/formas-t/` (fuera del corpus).
- **Biblicomentarios**: una vez OCR'd o recuperada fuente, evaluar **cada artículo individualmente por tema** (NO generalizar, directiva del usuario).
- **Ampliaciones**: obras futuras del usuario seguirán la misma convención (`authority=25`, `tag: jpm` + tags temáticos, `context=book-private`, `lds-independent-author`).

## Metadata común

Todas las obras de JPM incorporadas comparten:

```
author: "Juan Pablo Marichal Catalán"
authority: 25
rigor: 60-70 (según grado de análisis/investigación)
importance: opcional (salvo Reseña General = importante por amplitud)
official: false
current: true
context: book-private
audience: adult
tags: ["jpm", "lds-independent-author", ...temáticos específicos]
```

---

Última actualización: 2026-04-24, tras la segunda ronda de P4-corpus-expansion (adición de 6 artículos + actualización de excluidas con 3 republicaciones canónicas adicionales).
