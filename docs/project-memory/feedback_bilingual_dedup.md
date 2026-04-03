---
name: Bilingual dedup in counts
description: When counting corpus items that exist in both EN and ES, report the unique count, not the sum of both languages
type: feedback
---

When the KG or corpus has the same item in both idiomas (EN y ES), reportar la cantidad única, no la suma. 50 registros EN+ES de un mismo discurso = 25 discursos, no 50.

**Why:** Reportar la suma infla artificialmente los números y confunde. El usuario piensa en discursos únicos, no en registros de base de datos.
**How to apply:** Siempre que se cuenten entidades bilingües (discursos, escrituras, perfiles), dividir entre idiomas o deduplicar antes de reportar.
