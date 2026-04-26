---
name: forma-t
description: Genera o revisa Formas T doctrinales y biográficas en Alejandria. Usar cuando el usuario pida "Forma T", "genera una forma T", "colección de Formas T", "portar una Forma T", o quiera crear/ajustar el skill y el archivo final en prods/formas-t/.
---

# Forma T

Usa este skill para crear o revisar Formas T dentro de Alejandria.

## Lecturas obligatorias iniciales

Antes de proponer o editar una Forma T, leer:

1. `docs/project-memory/feedback_forma_t.md`
2. `docs/project-memory/procedure_forma_t_generation.md`
3. `docs/project-memory/project_covenant_path_architecture.md`

Si la forma pertenece a una colección existente, leer además 1-2 formas vecinas de `prods/formas-t/` para copiar estructura, longitud y tono.

## Cuándo usarlo

- Cuando el usuario pida una Forma T individual.
- Cuando el usuario pida una colección de Formas T.
- Cuando haya que portar una Forma T al formato estándar del repo.
- Cuando haya que revisar una Forma T existente por orden, referencias o relleno.

## Flujo de trabajo

### 1. Determinar alcance

- Si es una sola Forma T, construirla directamente.
- Si es una colección o un tema amplio, primero proponer subdivisión y pedir aprobación antes de crear archivos.

### 2. Investigar primero en el corpus

- Seguir protocolo documentation-first: corpus local antes que web.
- Para temas doctrinales, buscar en este orden: escrituras ancla, ayudas para las escrituras, manuales oficiales, conferencia general, libros doctrinales.
- Para biografías, reunir todas las menciones canónicas y luego complementar con GEE o ayudas si añaden identidad real y no relleno.

### 3. Diseñar la secuencia didáctica

- La columna de conceptos debe enseñar por sí sola.
- Un concepto por fila; usar rangos cuando una sola idea abarque varios versículos.
- Evitar relleno, duplicación y conceptos editoriales.
- Regla general: 5 a 12 filas; biografías pueden necesitar más si la vida tiene varias etapas claras.

### 4. Crear o actualizar archivo

- Guardar cada Forma T en `prods/formas-t/`.
- Usar la nomenclatura `{CCCC}-{slug-coleccion}-{FF}-{slug-forma}.md`.
- Incluir frontmatter completo: `title`, `date`, `status`, `collection`, `collection_id`, `group`, `collection_order`, `tags`, `derived_from`, `feeds_into`.

### 5. Sincronizar arquitectura

- Si agregas una forma a una colección existente, actualiza los conteos o notas arquitectónicas relevantes.

## Checklist duro

- El tema es específico y tiene responsabilidad simple.
- Cada referencia enseña realmente el concepto.
- El orden es didáctico y no arbitrario.
- El concepto cabe aproximadamente en 15 palabras.
- La forma no mezcla doctrina oficial con especulación.
- Si es doctrinal, Biblia primero cuando aplique; si es biográfica, priorizar secuencia de vida.

## Ejemplos locales

- `prods/formas-t/0003-vidas-01-melquisedec.md`
- `prods/formas-t/0003-vidas-06-juan-apostol.md`

## Resultado esperado

Entregar un archivo listo en `prods/formas-t/` y, si aplica, la actualización documental mínima para que la colección siga consistente.