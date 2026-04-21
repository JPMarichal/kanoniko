# ADR 0001 — Storage driver pattern for the ingestion write-path

**Estado:** propuesto · **Fecha:** 2026-04-21 · **Contexto:** §3.1 de `docs/ingestion-workflow.md`

## Contexto

El write-path de ingesta (`ingestion/registry.py`, `knowledge/profile_store.py`,
`ingestion/pipeline.py`) está hoy acoplado a SQLite + sqlite-vec + Neo4j vía
llamadas directas. Necesitamos portar la escritura a Postgres IONOS y
eventualmente retirar los stores antiguos.

El read-path ya introdujo un patrón: factories `make_*` en
`search.textual`, `search.semantic`, `knowledge.postgres_graph_client` que
devuelven instancias según `ALEJANDRIA_STORAGE_BACKEND`. El write-path debe
usar el **mismo patrón** para mantener coherencia.

## Decisión

**Protocol + driver concreto + factory + DI en un único módulo por componente.**

### Patrón estándar (se aplica a los 3 ports)

Cada componente (registry, profile_store, write_path) expone:

1. **Un `Protocol`** (PEP 544) en un módulo neutral (`.../driver.py` o en el
   mismo módulo del Protocol si es chico). Define la interfaz mínima — solo
   los métodos que el resto del código consume.
2. **Dos implementaciones concretas:**
   - `SqliteXxx` — la actual, movida a `.../sqlite_xxx.py` sin cambios de
     comportamiento.
   - `PostgresXxx` — nueva, en `.../postgres_xxx.py`, usando la conexión
     de `storage/postgres/connection.py`.
3. **Una factory `make_xxx()`** que lee `ALEJANDRIA_STORAGE_BACKEND` y devuelve
   la implementación apropiada. Firma mínima, sin parámetros opcionales que no
   sean estrictamente necesarios.
4. **Inyección por DI** en los consumidores (`api/dependencies.py`, `cli.py`,
   `pipeline.py`). Nunca instanciación directa del driver concreto.

### Naming

| Componente | Protocol | SQLite impl | Postgres impl | Factory |
|---|---|---|---|---|
| Registry | `DocumentRegistry` | `SqliteDocumentRegistry` | `PostgresDocumentRegistry` | `make_document_registry()` |
| Profile store | `ProfileStore` | `SqliteProfileStore` | `PostgresProfileStore` | `make_profile_store()` |
| Write path | `WritePath` | `LegacyWritePath` (SQLite + Neo4j) | `PostgresWritePath` | `make_write_path()` |

Notas:
- Mantenemos el nombre sin prefijo (`DocumentRegistry`, `ProfileStore`) para el
  Protocol — es lo que el código consumidor ya importa. Las impls concretas
  llevan prefijo del backend.
- `LegacyWritePath` agrupa SQLite + Neo4j porque se retiran juntos en §3.3-§3.4.
  No tiene sentido separarlos.

### Factory y flag

- `ALEJANDRIA_STORAGE_BACKEND` sigue gobernando durante §3.1.a (dual, flag
  controla).
- En §3.1.b (flip) el default pasa a `"postgres"` en `config.py`.
- En §3.4 (retiro de SQLite) el flag y las impls `Sqlite*` / `Legacy*` se
  eliminan del código.

### Errores y transaccionalidad

- Cada método del Protocol declara su contrato de atomicidad en docstring.
- `PostgresWritePath` usa transacciones por batch (un `COPY` = una
  transacción). Fallo → rollback del batch, no del pipeline completo.
- El registro en `DocumentRegistry` se actualiza **después** de que
  `WritePath` confirma éxito. Orden estricto, no atómico cross-componente
  (KISS — la idempotencia del reconcile cubre inconsistencias raras).

## Consecuencias

### Positivas

- Coherencia con el read-path ya portado.
- Cada componente se puede portar, testear y mergear independientemente.
- El retiro de SQLite/Neo4j es mecánico: eliminar la impl, eliminar el flag,
  simplificar la factory a función identidad.
- Mockeable para tests sin DB real (implementar un `InMemoryXxx` si hace falta).

### Negativas

- Código temporalmente duplicado durante §3.1 (SQLite + Postgres coexisten).
  Mitigación: §3.1.b (flip) ocurre en el mismo PR, no en uno posterior — la
  duplicación dura días, no meses.
- Un Protocol extra por componente. Costo bajo, beneficio alto.

## Alternativas descartadas

- **Subclases con herencia** — más rígido, peor testeable, no alineado con
  el read-path.
- **Feature flag inline en cada método** — dispersa la decisión, imposible
  de limpiar cuando se retire SQLite.
- **Port directo sin Protocol** — viable para `registry.py` (pequeño) pero
  inconsistente con los otros dos. Coherencia gana.

## Checklist de aplicación (para cada uno de los 3 ports)

- [ ] Definir Protocol con solo los métodos realmente consumidos (no copiar
      toda la API actual — aprovechar para podar).
- [ ] Mover impl actual a archivo nuevo con prefijo `sqlite_` / `legacy_`,
      sin cambios de comportamiento.
- [ ] Implementar Postgres impl en archivo separado.
- [ ] Factory `make_xxx()` con flag.
- [ ] Actualizar consumidores para importar de la factory, no del concreto.
- [ ] Tests unitarios por impl + un test de paridad (mismo input, ambos
      backends, outputs equivalentes).
