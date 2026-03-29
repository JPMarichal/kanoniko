# P1 — Scripture Structure: Long Chain — Risks

## R1: MySQL file path mapping errors (Fase 1)

**Descripción:** Las referencias en el dump MySQL son textuales ("Génesis 1", "Doctrina y Convenios 20") y deben mapearse a file paths del corpus (`es/scriptures/ot/genesis/1.txt`, `en/scriptures/dc/20.txt`). Errores en este mapeo dejan chunks sin estructura.

**Impacto:** Alto — chunks huérfanos no tendrían cadena larga; errores silenciosos difíciles de detectar en producción.

**Probabilidad:** Media — la mayoría de los libros son directos, pero hay casos irregulares: abreviaturas, acentos (Éxodo vs exodo), libros con números (1 Nefi → 1-nephi), guiones (José Smith-Mateo → js-matthew).

**Mitigación:**
1. Crear tabla explícita de mapeo `{mysql_book_name → corpus_slug}` para los 88 libros — no inferir, declarar
2. Validar en Fase 1: cada capítulo del JSON debe corresponder a un archivo existente en el corpus
3. Generar reporte de cobertura: capítulos en el dump sin match en corpus y viceversa
4. Ejecutar validación contra ambos idiomas (EN y ES)

**Criterio de aceptación:** 0 capítulos sin match en corpus; 0 archivos de corpus sin match en estructura.

---

## R2: Gaps y overlaps en cobertura de perícopas (Fase 1)

**Descripción:** El dump MySQL tiene 4,904 perícopas pero no garantiza cobertura total. El análisis preliminar de DyC 20 ya mostró que no todos los versículos están cubiertos.

**Impacto:** Alto — el requerimiento exige que todo versículo pertenezca a exactamente una perícopa.

**Probabilidad:** Alta — el dump fue construido con foco en perícopas significativas, no en cobertura exhaustiva.

**Mitigación:**
1. Script de validación que, por cada capítulo, liste los rangos de versículos cubiertos y los gaps
2. Generar reporte cuantitativo: total de gaps por volumen, capítulos más afectados
3. Gap-fill automatizado: crear perícopas para rangos descubiertos con nombres generados por LLM a partir del contenido textual
4. Validación de overlaps: detectar perícopas con rangos que se solapan y resolver (mantener la más específica)
5. Constraint de integridad: `verse_start[n+1] = verse_end[n] + 1` para perícopas contiguas dentro de cada capítulo

**Criterio de aceptación:** Reporte de cobertura al 100% sin gaps ni overlaps tras gap-fill.

---

## R3: Reestructuración de D&C (Fase 1)

**Descripción:** El dump tiene 2 divisiones y 2 libros para D&C (espejo 1:1). El modelo adoptado colapsa a 1 División ("Revelaciones de los últimos días") con 2 Libros ("Secciones" + "Declaraciones Oficiales") y renombra partes geográficas a "Periodo de...". Esta transformación es manual y propensa a errores de mapeo.

**Impacto:** Medio — una sección asignada al periodo geográfico incorrecto genera desinformación para el estudiante.

**Probabilidad:** Baja — el dump ya tiene la asignación; solo se renombra y reorganiza.

**Mitigación:**
1. Tabla de mapeo explícita: `{mysql_division_id, mysql_book_id} → {new_division, new_book, new_part_name}`
2. Verificar las 138 secciones + 2 ODs contra la asignación geográfica del dump
3. Cross-check con la información histórica conocida (ej. DyC 20 → Fayette, NY → "Periodo de Nueva York")
4. Las ODs no tienen versículos — modelarlas como capítulos con `verse_count: null` y sin perícopas (o una sola perícopa que cubre todo el documento como prosa)

**Criterio de aceptación:** Las 140 entradas (138 secciones + 2 ODs) resuelven correctamente su cadena larga completa.

---

## R4: Calidad de traducción EN para ~5,300 nombres (Fase 2)

**Descripción:** 19 divisiones, 412+ partes y 4,904+ perícopas necesitan nombres en inglés. La traducción masiva por LLM puede generar inconsistencias terminológicas, traducciones literales torpes, o nombres que no corresponden a la tradición anglófona.

**Impacto:** Medio — nombres incorrectos degradan la experiencia de búsqueda y confunden al estudiante.

**Probabilidad:** Media — los nombres de divisiones y partes son relativamente estándar, pero las perícopas son descriptivas y variadas.

**Mitigación:**
1. Divisiones (19): traducción manual — nombres académicos bien establecidos
2. Partes (412+): LLM batch con contexto de dominio (terminología escritural), revisión manual para LdM y D&C
3. Perícopas (4,904+): LLM batch agrupado por volumen para consistencia
4. Spot-check obligatorio de perícopas conocidas: "Sermon on the Mount" (no "Sermon of the Mountain"), "Lehi's Dream" (no "Lehi's Vision"), "The First Vision" (no "The First Apparition")
5. Para gap-fills: el LLM genera el nombre ES y EN simultáneamente a partir del texto, evitando traducción en cadena
6. Glosario de términos fijos: covenant = convenio, priesthood = sacerdocio, atonement = expiación — compartido como contexto en cada batch

**Criterio de aceptación:** 100% de entradas con nombre EN; spot-check de 50 perícopas conocidas con 0 errores.

---

## R5: Declaraciones Oficiales sin versículos (Fase 1, 3)

**Descripción:** OD-1 y OD-2 son documentos en prosa sin numeración de versículos. Rompen el modelo perícopa→versículo.

**Impacto:** Bajo — solo 2 documentos, pero si no se manejan, causan errores en `resolve_long_chain()`.

**Probabilidad:** Cierta — es un caso conocido.

**Mitigación:**
1. Modelar como capítulos con `chapter_type: "prose"` y `verse_count: null`
2. Una sola perícopa por OD que cubre "todo el documento" con `verse_start: null, verse_end: null`
3. `resolve_long_chain()` retorna la perícopa sin rango de versículos para estos casos
4. Búsquedas por perícopa los incluyen; búsquedas por versículo los excluyen gracefully

**Criterio de aceptación:** `resolve_long_chain("dc/od-1.txt", null, null)` retorna cadena completa sin error.

---

## R6: Facsímiles como placeholders sin corpus (Fase 1)

**Descripción:** Los 3 facsímiles se modelan como capítulos tipo facsimile bajo una nueva Parte, pero no hay archivos de corpus ni contenido textual todavía.

**Impacto:** Bajo — son placeholders; no afectan funcionalidad existente.

**Probabilidad:** Cierta — es diseño intencional.

**Mitigación:**
1. `chapter_type: "facsimile"` con `corpus_file: null` señala explícitamente que no hay contenido
2. `resolve_long_chain()` retorna la estructura pero sin perícopa/versículo para facsímiles
3. El endpoint `/scriptures/structure` los muestra en la jerarquía con indicador de "pendiente"
4. Documentar en el JSON el número de figuras esperadas por facsímile (12, 22, 6) para trabajo futuro

**Criterio de aceptación:** Los facsímiles aparecen en la estructura pero no generan errores en búsqueda ni indexación.

---

## R7: Impacto en rendimiento de KG con ~5,300 nodos estructurales nuevos (Fase 3)

**Descripción:** Agregar ~19 divisiones + ~412 partes + ~4,900 perícopas como nodos en Neo4j, más sus relaciones (`PART_OF`, `CONTAINS`), incrementa significativamente el tamaño del grafo.

**Impacto:** Bajo-Medio — más nodos en traversals, posible degradación en queries de vecinos.

**Probabilidad:** Baja — Neo4j maneja bien este volumen, pero depende de cómo se integran con queries existentes.

**Mitigación:**
1. Nodos estructurales con tipo específico (`division`, `part`, `pericope`) — no mezclados con entidades genéricas
2. Índices Neo4j por tipo para estos nodos
3. Queries de RAG no traversan nodos estructurales por defecto — solo cuando el usuario pregunta explícitamente sobre estructura
4. Benchmark antes/después de la inserción con las queries más frecuentes

**Criterio de aceptación:** Queries existentes de RAG no degradan más de 10% en latencia tras la inserción.

---

## Matriz resumen

| ID | Riesgo | Impacto | Probabilidad | Fase |
|----|--------|---------|-------------|------|
| R1 | Mapeo file path | Alto | Media | 1 |
| R2 | Gaps en perícopas | Alto | Alta | 1 |
| R3 | Reestructuración D&C | Medio | Baja | 1 |
| R4 | Calidad traducción EN | Medio | Media | 2 |
| R5 | ODs sin versículos | Bajo | Cierta | 1, 3 |
| R6 | Facsímiles sin corpus | Bajo | Cierta | 1 |
| R7 | Rendimiento KG | Bajo-Medio | Baja | 3 |
