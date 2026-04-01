---
name: Corpus query strategy - knowledge first, corpus to verify
description: When answering theological/corpus questions, use own knowledge + KG first, corpus only to verify and cite. Never delegate exhaustive search to subagent.
type: feedback
---

Para preguntas sobre contenido del corpus (teología, escrituras, doctrina): el corpus descubre, el LLM sintetiza. No al revés.

**Why:** (1) Un subagente genérico hizo 48 tool calls en 4.5 minutos — demasiado exhaustivo. (2) Después, el LLM respondió desde su conocimiento sin buscar en el corpus — ignorando el valor diferencial de Alejandría (conferencias, manuales, fuentes no canónicas). Ninguno de los dos extremos es correcto.

**How to apply:** Seguir el procedimiento en CLAUDE.md § "Answering Corpus Questions": KG primero para estructura y conexiones, hybrid search para descubrir (especialmente fuentes no canónicas), luego sintetizar con conocimiento propio. Nunca lanzar subagente exhaustivo, pero tampoco responder solo desde conocimiento base.
