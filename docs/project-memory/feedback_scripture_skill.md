---
name: Usar skill /scripture para citas textuales
description: Siempre usar el skill scripture-lookup para citar pasajes de escritura — nunca de memoria ni de resultados de búsqueda
type: feedback
---

Siempre que se necesite citar textualmente un pasaje de las escrituras, usar el skill `/scripture` (scripture-lookup) para leer el texto directamente del corpus.

**Why:** Las citas de escritura deben ser exactas, tomadas del archivo del corpus. Citar de memoria o de fragmentos de búsqueda introduce errores sutiles. El skill resuelve la referencia al archivo correcto, extrae los versículos y los formatea en FCD.

**How to apply:**
1. Cuando la respuesta incluya una cita textual de escritura (no paráfrasis ni alusión), invocar el skill o seguir su procedimiento: resolver referencia → leer archivo → extraer versículos → formatear en FCD
2. Aplica tanto a respuestas conversacionales como a productos editoriales (artículos, formas T, dossiers, discursos)
3. Si son múltiples referencias, resolverlas todas antes de componer la respuesta
4. No sustituir con resultados de `search_text` o `search_hybrid` — esos devuelven chunks, no versículos exactos
