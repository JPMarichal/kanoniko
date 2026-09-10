# P0 — Documentation Sync & Cleanup — Risks

> Rescoped after A0. The migration is done & validated on `main`; this is a docs + cleanup task, so
> the risk surface is small.

## R1: Over-editing — erasing useful history

**Descripción:** Al sincronizar 7 docs es fácil borrar el registro de por qué existió Neo4j/Qdrant,
perdiendo contexto que `vector-db-options.md` y futuros lectores necesitan.

**Impacto:** Bajo.

**Probabilidad:** Media.

**Mitigación:**
1. Regla: cambiar tiempo verbal ("uses Neo4j" → "used Neo4j in Phase 3; consolidated to pgvector"),
   no eliminar el hecho histórico.
2. Mantener y enlazar `vector-db-options.md`, `postgres-migration.md` como el registro fechado.
3. Diff review: el cambio debe ser casi todo reemplazo de párrafos de arquitectura, no borrado neto.

**Criterio de aceptación:** `git log`/`vector-db-options.md` siguen explicando la evolución del stack.

## R2: Cleanup (FR-3) borra algo vivo

**Descripción:** El `packages/` sin trackear en `main` o la rama `workspace-migration` podrían
contener trabajo que el usuario quiera rescatar (aunque dijo que no es vigente).

**Impacto:** Medio (si hay algo irrecuperable).

**Probabilidad:** Baja.

**Mitigación:**
1. FR-3 es **opcional** y requiere confirmación explícita del usuario antes de `branch -D` / `stash drop`.
2. El WIP quedó en `git stash` (reversible) y la rama sigue en el repo local hasta que el usuario diga.
3. `git ls-files packages/` = 0 confirma que el `packages/` de `main` no aporta nada trackeado.
4. Antes de borrar la rama: `git log --stat main..workspace-migration` para inventariar qué se pierde.

**Criterio de aceptación:** nada se borra sin `git log`/inventario previo y OK del usuario.

## Matriz resumen

| ID | Riesgo | Impacto | Probabilidad |
|----|--------|---------|--------------|
| R1 | Over-editing borra historia | Bajo | Media |
| R2 | Cleanup borra algo vivo | Medio | Baja |
