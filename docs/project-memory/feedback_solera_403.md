---
name: Avoid fetching mormontextsproject.org directly
description: WebFetch to mormontextsproject.org triggers Solera corporate proxy alert (403). Use web search instead.
type: feedback
---

No hacer WebFetch directo a mormontextsproject.org — el proxy corporativo de Solera lo bloquea con 403.

**Why:** Sucedió dos veces en la sesión de Roberts books. El usuario tuvo que intervenir manualmente para descartar la alerta.

**How to apply:** Para consultar el catálogo MTP, usar WebSearch en vez de WebFetch. Alternativamente, buscar en el bookshelf de Gutenberg (`gutenberg.org/ebooks/bookshelf/404`) que tiene el mismo contenido sin restricción de proxy.
