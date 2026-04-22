# Ingestion backlogs

Cuatro archivos JSON que rastrean el estado de cada pieza del corpus
a través de los 9 pasos del workflow de ingesta
(`docs/ingestion-workflow.md`). Clave compartida: **`slug`**
(lowercase kebab-case).

## Archivos

| Archivo | Tracks | Schema |
|---|---|---|
| `discovery.json` | Material candidato identificado; clasificación + path destino. | `schemas/discovery.schema.json` |
| `research.json` | Producción de reseña (`prods/reseñas/{slug}/reseña.md`). | `schemas/research.schema.json` |
| `downloads.json` | Crudos bajados al cache local. | `schemas/downloads.schema.json` |
| `indexing.json` | Estado de ingestión en Postgres (SHA, stale detection). | `schemas/indexing.schema.json` |

Todos los JSON son arrays en la raíz: `[]` = backlog vacío.

## Reglas de llave

- `slug` es único dentro de cada backlog (el validator lo enforcea).
- `slug` es consistente entre los cuatro: el mismo material aparece
  con el mismo slug en discovery, research, downloads y indexing.
- Patrón: `^[a-z0-9]([a-z0-9-]*[a-z0-9])?$` (lowercase, kebab-case,
  sin espacios ni underscores).

## Validación

El pre-commit hook (`scripts/pre-commit-sync.sh`) corre
`scripts/validate_backlogs.py` en cada commit y bloquea el push si
hay errores de schema o slugs duplicados.

Manual:

```bash
python scripts/validate_backlogs.py            # todos
python scripts/validate_backlogs.py discovery  # uno solo
```

## Reconcile

Para detectar drift entre backlogs ↔ filesystem ↔ Postgres:

```bash
# Dry-run (default): sólo reporta lo que cambiaría
python scripts/reconcile_backlogs.py

# Apply: materializa los updates detectados y guarda los JSONs
python scripts/reconcile_backlogs.py --apply

# Incluir check contra Postgres (requiere SSH tunnel up)
python scripts/reconcile_backlogs.py --with-postgres
```

El reconciler opera con **agresividad media**: actualiza entries
existentes pero **nunca** crea entries nuevas automáticamente. Los
huérfanos (reseña sin slug registrado, archivo corpus sin indexing
entry, etc.) se reportan con `kind="orphan"` para que un humano
decida cómo integrarlos.

## Pendiente de migración

Hay material pre-existente documentado en `proj/00-backlog.md` que
fue el formato manual antes de §Level B. La migración a estos cuatro
JSON backlogs **no se hace automáticamente** — cada entrada requiere
decisión humana (slug, categoría, autoridad, reseña). Traerlo manual
cuando lo trabajes.
