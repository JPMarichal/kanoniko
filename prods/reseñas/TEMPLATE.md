# {Título de la obra}

> **Reseña skeleton.** Duplica este archivo en
> `prods/reseñas/{slug}/reseña.md` y elimina este blockquote. Mantén
> el orden de las secciones y los marcadores HTML-comment del bloque
> de metadata IA al final — el script de publicación usa esos
> marcadores para strippear el bloque antes de exportar el catálogo.

## Ficha bibliográfica

- **Título:** ...
- **Autor(es):** ...
- **Editor / Casa editora:** ...
- **Año (primera edición):** ...
- **Edición consultada:** ...
- **Idioma original:** ...

## De qué trata

Síntesis accesible en 1-2 párrafos. Sin jargon. Tono de reseña para
un lector SUD general (no especialista), estilo catálogo publicable.

## Contexto histórico y propósito

Cuándo y para qué se escribió. Circunstancias de la publicación
original. Problema que atendía o conversación en la que se insertó.

## Relevancia para el lector SUD

Peso eclesial, uso en currículo, menciones en conferencia general,
recepción en comentarios posteriores. Por qué vale la pena hoy.

## Estructura de la obra

Secciones o capítulos principales. Árbol resumido si es colección o
antología. Tamaño (páginas, capítulos, volúmenes).

## Valoración

Fortalezas, limitaciones, a quién recomendarlo (devocional, estudio,
investigación, docencia). Qué NO esperar.

## Fuentes citadas

Bibliografía en FCD — consulta `docs/citation-norms.md`.

<!-- ===== METADATA IA — NO PUBLICAR ===== -->

## Metadata de ingestión

### Clasificación

- **Categoría corpus:** (ej. `books/` | `manuals/` | `biographies/` | `general-conference/`)
- **Paths destino:** (ej. `en/books/{slug}/` + `es/books/{slug}/`)
- **Idioma:** (`en` | `es` | `multi`)

### Autoridad propuesta

Valores para `src/alejandria/authority.py::_SOURCE_DEFAULTS` si la
categoría necesita una fila nueva. Escala en `docs/authority-model.md`.

- **authority:** (0–100)
- **rigor:** (0–100)
- **importance:** (0–100)
- **official:** (true | false)
- **context:** (p.ej. `official-declaration` | `manual` | `biography`)
- **Justificación:** ...

### KG pre-seed

Entidades y relaciones curadas conocidas a priori, a insertarse antes
de que corra el extractor NER sobre el contenido.

```yaml
# Entidades
- name: "..."
  type: "person" | "place" | "concept" | "people" | "object" | "period" | "scripture"
# Relaciones
- from: { name: "...", type: "..." }
  to:   { name: "...", type: "..." }
  rel_type: AUTHORED
  source_ref: "..."
  confidence: curated
```

### Fuente de descarga

- **URL:** ...
- **Skill usado:** (`gospelink` | `byu-studies` | `rsc-byu` | `gutenberg` | `manual`)
- **SHA del crudo:** ...

<!-- ===== FIN METADATA IA ===== -->
