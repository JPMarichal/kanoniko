---
name: No system jargon in user-facing responses
description: Never reference system internals (corpus, KG, FTS, Qdrant) in user-facing commentary — the system is a black box to the end user
type: feedback
---

En respuestas dirigidas al usuario final (comentarios bíblicos, análisis temáticos, etc.), nunca referirse a los componentes internos del sistema: "el corpus", "el KG", "la base de datos", "FTS", "Qdrant", "Neo4j", "los embeddings", etc.

En su lugar, usar lenguaje natural que el lector común entienda:
- ❌ "Lo que el corpus revela sobre Rut"
- ✅ "Lo que las Autoridades Generales han dicho sobre Rut"
- ❌ "El KG muestra 25 discursos"
- ✅ "Se han pronunciado 25 discursos sobre este tema"
- ❌ "La búsqueda semántica encontró..."
- ✅ "En los discursos de conferencia general se enseña que..."

**Why:** La aplicación final es para un lector común de las escrituras. El sistema es una caja negra — el usuario no sabe ni le importa qué tecnología hay detrás. Referirse a "el corpus" o "el KG" rompe la ilusión y confunde.
**How to apply:** Esta regla aplica SOLO a respuestas de contenido (comentarios, análisis, búsquedas doctrinales). NO aplica cuando se está hablando del sistema mismo (desarrollo, debugging, arquitectura).
