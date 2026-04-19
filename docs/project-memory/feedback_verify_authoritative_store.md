---
name: Verify authoritative store before any destructive op
description: Antes de purgar/merge/insertar en el KG o data layer, verificar dónde está la fuente de verdad. No confiar en CLAUDE.md si los commits recientes contradicen.
type: feedback
---

Antes de cualquier operación destructiva o correctiva sobre KG/datos, **verificar explícitamente cuál es la fuente de verdad activa hoy**, no la que dice CLAUDE.md o un doc estático.

**Why:** En esta sesión apliqué 4 operaciones costosas (purga, entity resolution, family backfill) sobre Neo4j local creyendo que era la fuente de verdad porque CLAUDE.md así lo decía. Pero la migración Phase 1 a Postgres IONOS había mergeado en `main` (PR #3) y CLAUDE.md no se actualizó. El usuario confirmó que Postgres IONOS es autoridad. Tuve que repetir todo el trabajo. Pérdida: ~1h de operaciones DB y mucha contexto/turn.

**How to apply:**
- Al inicio de toda sesión que toque KG/data: revisar `git log --oneline -10` y memoria (`MEMORY.md` index) buscando "postgres", "migration", "source of truth". Si hay merge reciente que afecte el storage, asumir que cambió.
- Al ver mismatch entre CLAUDE.md y commits recientes / memoria, **prevalece la memoria + git log más recientes**. CLAUDE.md puede estar stale.
- Antes de la primera operación destructiva, hacer una pregunta de verificación al usuario: "Voy a aplicar X sobre Y. ¿Correcto que Y es la fuente de verdad actual?" Si la respuesta es sí, proceder. Si requiere búsqueda, hacerla.
- Si los `mcp__alejandria__*` tools se conectan a un backend local pero la fuente real es remota, los tools sirven solo como **vista**, no como **escritura/oracle**. Para validar verdad, conectar directo al store remoto.
