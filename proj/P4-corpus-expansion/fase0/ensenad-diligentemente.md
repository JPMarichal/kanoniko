# Fase 0 — *Enseñad Diligentemente* (Boyd K. Packer) — edición en español

> Fecha: 2026-04-22. Epub en `epub/!Ready/Enseñad Diligentemente - Boyd K. Packer.epub`. **Par de traducción** del libro *Teach Ye Diligently* ya presente en `corpus/en/books/teach-ye-diligently/`.

---

## 1. Qué es

Traducción oficial al español de *Teach Ye Diligently* (Bookcraft, 1975) — tratado de Packer sobre los principios de la enseñanza del evangelio. Audiencia: maestros de Iglesia, padres, instructores de CES. Organizada en 28 capítulos + prefacio, aproximadamente 700 KB de texto.

El epub es un reflow PDF producido por un miembro ("MARIO LABRAÑA" aparece como digitalizador en la portada) a partir de la edición en español distribuida por los centros de distribución de la Iglesia. La portada indica "Publicado por La Iglesia de Jesucristo de los Santos de los Últimos Días".

## 2. Quién lo produjo

Autor: Boyd K. Packer, miembro del Q12 (sostenido abril de 1970) al momento de escribir la obra original en inglés (1975). Publicada originalmente por Bookcraft como tratado pedagógico personal, sin comisión explícita del FP+Q12.

La traducción al español fue coordinada por el Departamento de Traducción de la Iglesia para distribución oficial. La edición española que alimenta el epub es, por tanto, **traducción oficial** — aunque el texto fuente es obra privada del autor.

## 3. Relaciones con el corpus existente

- **Par bilingüe con:** `corpus/en/books/teach-ye-diligently/` (authority=45 ya asignado).
- **KG entities:** Boyd K. Packer, conceptos pedagógicos (teaching, pedagogy, gospel-teaching).
- **Continuidad temática:** junto con *Holy Temple* y *Eternal Love*, completa la serie Packer EN/ES que estamos incorporando.
- **Bug del inventario descubierto:** la versión ES apareció como `nuevo` en `epub/_inventory.csv` porque el fuzzy matcher filtra por idioma; no cruzó contra `teach-ye-diligently` EN. Arreglo del matcher ya agendado como tarea separada.

## 4. Evaluación (→ sidecar)

Para mantener consistencia con el par EN, uso authority=45 y los mismos tags base, añadiendo `spanish-translation`.

| eje | valor | justificación |
|---|---|---|
| authority | 45 | igual que par EN ya en corpus; tratamiento tipo-manual con autor individual AG |
| rigor | 60 | cuidadoso, con anécdotas y citas de escritura, no académico |
| importance | importante | ampliamente usado en CES y enseñanza local |
| official | false | original de autor privado, aunque traducción oficial |
| current | true | distribuido por los centros de distribución |
| context | book-private | |
| audience | general | maestros, padres, miembros en llamamientos de enseñanza |
| tags | `["teaching", "pedagogy", "CES", "gospel-teaching", "apostle-authored", "spanish-translation"]` | |

## 5. Procedencia

- Digitalizador declarado en portada: "MARIO LABRAÑA" (miembro que reflowed el PDF original).
- Sin `source_url` público; marcado `null` en sidecar.

## Notas del proceso

- El epub no tiene headings `<h1>` pero sí `<h2>` con el título de cada capítulo.
- **Bug detectado y corregido durante esta incorporación**: el parser contaba `<h2>` vacíos (page-breaks Calibre con solo whitespace) como "hay heading", bloqueando el fallback a `first_bold`. El frontmatter pre-primer-heading se quedaba sin título ("Untitled"). Arreglo: contar solo bloques-heading emitidos con texto, y mantener un `pending_first_bold` como fallback para la portada.
