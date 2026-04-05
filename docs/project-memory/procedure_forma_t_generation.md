---
name: procedure_forma_t_generation
description: Complete procedure for generating Formas T — audience design, corpus search, didactic ordering, sequence review, length check
type: feedback
---

Procedimiento completo para generar colecciones de Formas T.

---

## Fase A — Propuesta y aprobación

### A1. Tema genérico
- El usuario presenta un tema amplio (ej: "bautismo", "Espíritu Santo").

### A2. Investigación exploratoria
- Buscar en **todo el corpus** (escrituras, manuales, conferencia, libros), no solo en escrituras.
- Usar MCP tools (`search_hybrid`, `kg_find`) con 3-7 llamadas quirúrgicas.
- Identificar los subtemas naturales que el corpus revela.

### A3. Plan y subdivisión
- Proponer Formas T individuales: título, objetivo breve y subtema enfocado.
- Cada Forma T = un subtema con responsabilidad simple. Si bifurca, subdividir.
- Los subtemas surgen del corpus y de las preguntas que el tema genera.
- Evaluar si algún subtema pertenece mejor a otra colección futura.

### A4. Presentación y aprobación
- Presentar la propuesta completa al usuario (lista numerada de Formas T con títulos y objetivos).
- El usuario revisa, ajusta, reordena, agrega o elimina antes de aprobar.
- **No generar archivos hasta obtener aprobación explícita.**

---

## Fase B — Generación

### B1. Audiencias
- Diseñar para: no-miembros, conversos nuevos, miembros reactivándose, líderes nuevos.
- Los conceptos deben enseñar sin requerir conocimiento previo SUD.
- Algunas Formas T pueden ser específicamente apologéticas cuando el tema lo requiere.

### B2. Orden didáctico (de lo conocido a lo avanzado)
- **Biblia primero** (ancla más accesible para todas las audiencias) → Libro de Mormón → DyC/Restauración.
- Dentro de cada bloque, de lo general al detalle.

### B3. Secuencia lógica/cronológica
- Si algo ocurre antes en la práctica, aparece antes en la tabla.
- Revisar cada forma como guión: ¿un lector que sigue las filas en orden entiende una progresión coherente?
- Causas antes de consecuencias. Habilitadores antes de lo que habilitan (ej: llaves de Elías antes de la obra del templo).

### B4. Generación de archivos
- Producir cada Forma T como archivo .md en `prods/formas-t/`.

---

## Fase C — Revisión con checklist de calidad

Revisar cada Forma T generada contra este checklist:

- [ ] **Longitud:** cada concepto ≤ ~15 palabras.
- [ ] **Claridad:** cada concepto es autoexplicativo (no depende de jerga o contexto previo). Si usa un término fuerte ("obra muerta"), explicar en la misma fila.
- [ ] **Orden didáctico:** Biblia primero → Libro de Mormón → DyC. General antes que detalle.
- [ ] **Secuencia:** causas antes de consecuencias; habilitadores antes de lo habilitado; pasos prácticos en orden real.
- [ ] **Responsabilidad simple:** la forma no bifurca en dos subtemas distintos.
- [ ] **Formato:** título corto SEO long-tail (3-5 palabras), sin dos puntos, capitalización hispana. Frontmatter completo (title, date, status, collection, collection_order, tags, derived_from, feeds_into). Nota/abreviaturas solo si se usan fuentes no escriturarias.

Iterar hasta que todas las formas pasen el checklist.

---

**Why:** Las sesiones de bautismo y Espíritu Santo revelaron que: (1) sin plan previo aprobado, se genera material que luego se descarta o reubica; (2) sin checklist de revisión, los conceptos quedan largos, el orden mezcla niveles de familiaridad y la secuencia no sigue la lógica real.

**How to apply:** Seguir las tres fases (A→B→C) cada vez que se genere una colección de Formas T. No saltar de A1 a B4.
