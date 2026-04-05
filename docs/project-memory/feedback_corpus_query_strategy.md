---
name: Corpus query strategy - thorough tool coverage
description: When answering corpus questions, exhaust KG tools (find+neighbors, not just profile), always search in books/, and verify sources before dismissing them.
type: feedback
---

Para preguntas sobre contenido del corpus (teología, escrituras, historia, doctrina): el corpus descubre, el LLM sintetiza. No al revés.

**Regla 1 — KG: no abandonar tras un solo intento.**
Si `kg_profile` falla, seguir con `kg_find` (buscar variantes del nombre) y `kg_neighbors` (ver relaciones). Solo descartar el KG después de agotar las tres herramientas.

**Regla 2 — Siempre buscar en `books/`.**
Para preguntas históricas o doctrinales, incluir al menos una búsqueda con `source_filter: "en/books"` (o `es/books`). Los libros (Roberts, Talmage, Taylor, BY) aportan narrativa de primera mano que manuales y conferencias no tienen.

**Regla 3 — No descartar fuentes sin leerlas.**
Si una búsqueda dice "1 resultado en archivo X", leer ese resultado antes de declarar que no aporta. Un solo dato factual puede ser el que falta.

**Regla 4 — Nunca subagente exhaustivo, pero sí cobertura quirúrgica.**
Total de tool calls para una pregunta de corpus: 3–7 llamadas, cubriendo KG (1–2), hybrid general (1–2), hybrid filtrado por books (1), y lectura directa si se necesita precisión.

**Why:** En la cronología de Winter Quarters: (1) abandoné el KG tras un solo `kg_profile` fallido, cuando `kg_find` sí encontraba el nodo; (2) no busqué en `en/books/` donde *Life of John Taylor* tenía 10 menciones valiosas; (3) descarté *Outlines of Ecclesiastical History* sin leer su única mención, que confirmaba la fecha de reorganización de la Primera Presidencia.

**How to apply:** Al planificar las llamadas para una pregunta de corpus, asegurar cobertura de: KG (find → profile/neighbors), búsqueda general, búsqueda en books, y verificación de fuentes mencionadas.
