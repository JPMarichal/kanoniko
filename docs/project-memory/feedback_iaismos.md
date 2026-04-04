---
name: Evitar iaísmos en narrativa española
description: No abusar del imperfecto (-ía) ni del pluscuamperfecto (había+participio) en artículos; preferir pretérito simple cuando la acción está completa
type: feedback
---

Evitar la acumulación de verbos en imperfecto (-ía, -aba) y pluscuamperfecto (había + participio) en textos narrativos en español. Preferir el pretérito simple cuando la acción está completa.

**Why:** En el Art 05 (Abish), el usuario detectó "muchos iaísmos" — párrafos donde casi todos los verbos terminaban en -ía o usaban "había + participio", lo que vuelve el texto monótono y pesado. Es un patrón que la IA sobreusa porque el imperfecto y el pluscuamperfecto son formas "seguras" para narrar en pasado, pero el español tiene más recursos.

**How to apply:**
- **Al escribir narrativa en pasado**, usar pretérito simple como tiempo base ("corrió", "vio", "decidió") y reservar el imperfecto para fondo/contexto simultáneo ("mientras llovía", "la gente que estaba").
- **Pluscuamperfecto solo cuando es necesario**: anterioridad real respecto a otra acción pasada. "Había esperado años" → "Esperó años" si no hay otra acción pasada que lo exija.
- **Prueba rápida**: leer un párrafo en voz alta. Si más de la mitad de los verbos terminan en -ía/-aba o usan "había", reescribir variando tiempos.
- **Alternativas**: pretérito simple, presente histórico (para dramatizar), infinitivo, construcciones nominales ("sin garantías" en vez de "no tenía garantías").
- **Tres pasadas obligatorias en revisión:**
  1. Grep de verbos en `-ía/-aba` — listar todas las instancias
  2. Grep de `había + participio` — listar pluscuamperfectos
  3. Densidad por párrafo editorial (sin contar citas escriturales/proféticas) — si un párrafo tiene 3+ imperfectos, reescribir
