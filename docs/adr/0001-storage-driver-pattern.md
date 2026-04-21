# ADR 0001 — Storage driver pattern for the ingestion write-path

**Estado:** aprobado (v2) · **Fecha:** 2026-04-21 · **Contexto:** §3.1 de `docs/ingestion-workflow.md`

> **v2 (2026-04-21):** enmendado tras mapear el pipeline. El componente
> "WritePath" monolítico se reemplaza por **tres Protocols cohesivos**
> (ChunkWriter, KnowledgeGraphWriter, KnowledgeGraphReader) aplicando ISP
> de forma estricta. Los helpers KG externos con acceso a driver raw se
> refactoran en el mismo PR para tomar el Protocol, eliminando la fuga de
> abstracción (Law of Demeter).

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

**Protocol + driver concreto + factory + DI**, con una aplicación estricta
de **ISP (Interface Segregation Principle)**: cinco Protocols cohesivos en
lugar de uno monolítico.

### Patrón estándar (se aplica a cada componente)

Cada componente expone:

1. **Un `Protocol`** (PEP 544) que declara solo los métodos realmente
   consumidos, agrupados por responsabilidad (SRP).
2. **Dos implementaciones concretas** durante la migración:
   - `Legacy*` o `Sqlite*` — adapter sobre la implementación actual,
     behavior-preserving, retirado al terminar §3.
   - `Postgres*` — implementación nueva sobre Postgres IONOS.
3. **Una factory `make_*()`** que lee `ALEJANDRIA_STORAGE_BACKEND` y devuelve
   la implementación apropiada. Firma mínima.
4. **Inyección por DI** en los consumidores. Nunca instanciación directa
   del driver concreto.

### Catálogo de Protocols

| Dominio | Protocol | Impl transicional | Impl Postgres | Factory |
|---|---|---|---|---|
| Registro de documentos | `DocumentRegistry` | `SqliteDocumentRegistry` | `PostgresDocumentRegistry` | `make_document_registry()` |
| Perfiles de entidades | `ProfileStore` | `SqliteProfileStore` | `PostgresProfileStore` | `make_profile_store()` |
| Escritura de chunks (texto + vectores) | `ChunkWriter` | `LegacyChunkWriter` | `PostgresChunkWriter` | `make_chunk_writer()` |
| Escritura de grafo de conocimiento | `KnowledgeGraphWriter` | `LegacyKGWriter` (Neo4j) | `PostgresKGWriter` | `make_kg_writer()` |
| Lectura de grafo durante ingestión | `KnowledgeGraphReader` | `LegacyKGReader` (Neo4j) | `PostgresKGReader` | `make_kg_reader()` |

**Por qué tres Protocols para el pipeline y no uno.** El pipeline consume
~15 operaciones heterogéneas de almacenamiento. Agruparlas en un
`WritePath` único fusionaría responsabilidades de persistencia de texto
con persistencia de grafo, y obligaría a cualquier consumidor (test fake,
backend alternativo) a implementar toda la superficie. ISP dice lo
contrario: tres interfaces pequeñas — indexado de chunks, escritura de
grafo, lectura de grafo — permiten evolución independiente, tests más
simples y la sustitución futura de un subsistema sin tocar los otros
(ej. cambiar embeddings de pgvector a Qdrant no toca `KGWriter`).

### Helpers externos con acceso a driver raw

Cinco helpers hoy reciben el `_driver` raw de Neo4j:
`ensure_indexes`, `load_hierarchy`, `load_parallels`,
`extract_metadata_relations`, `load_cross_refs`. Esto es una violación de
Law of Demeter. Todos se refactoran **en el mismo PR** para aceptar un
`KnowledgeGraphWriter`. Si tras el refactor algún helper solo llama a una
operación ya presente en el Protocol, se inlinea; no quedan wrappers
inútiles.

### Cohesión del catálogo

- `DocumentRegistry` y `ProfileStore` son independientes — viven en
  módulos separados porque representan dominios distintos (tracking de
  archivos vs. metadata de entidades).
- `ChunkWriter` **consolida** la escritura textual (FTS) y semántica
  (vectores) porque ambas se aplican por chunk y siempre se invocan
  juntas en el pipeline. Separarlas crearía sincronización implícita
  innecesaria.
- `KnowledgeGraphWriter` y `KnowledgeGraphReader` van separados porque
  responden a fases distintas del pipeline (Fase 3: escribir entidades y
  relaciones; Fase 4: leer menciones para consolidar perfiles) y a
  presiones de evolución distintas (la lectura puede rutearse a réplicas).

### Factory y flag

- `ALEJANDRIA_STORAGE_BACKEND` sigue gobernando durante §3.1 mientras los
  `Legacy*` / `Sqlite*` coexisten con los `Postgres*`.
- Al flipear el default a `"postgres"`, las impls transicionales y el
  flag se eliminan en el **mismo PR**. No queda código muerto tras §3.1.

### Política anti-basura (enmienda v2)

Parte explícita del contrato del PR: cada paso del refactor borra su
propio andamiaje al terminar. En concreto:

- Una vez Pipeline depende de los Protocols, no quedan imports directos
  de `Neo4jClient`, `TextualSearch`, `SemanticSearch` ni `sqlite3` en
  `pipeline.py`.
- Una vez los helpers externos aceptan `KnowledgeGraphWriter`, no queda
  código que lea `client._driver`.
- Al retirar `Legacy*` se eliminan también los módulos que quedaron sin
  consumidores (`neo4j_client.py`, `sqlite_registry.py`,
  `sqlite_profile_store.py`, y los caminos SQLite de `textual.py` y
  `semantic.py`).
- No se aceptan comentarios "TODO retirar esto" como sustituto del
  borrado: si se puede borrar, se borra.

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

## Checklist de aplicación (para cada Protocol)

- [ ] Definir Protocol con solo los métodos realmente consumidos (no copiar
      toda la API actual — aprovechar para podar).
- [ ] Implementar Legacy/Sqlite impl como adapter sobre el código actual
      (archivo nuevo, prefijo `legacy_*` / `sqlite_*`), sin cambios de
      comportamiento.
- [ ] Implementar Postgres impl en archivo separado.
- [ ] Factory `make_xxx()` con flag.
- [ ] Actualizar consumidores para importar de la factory, no del concreto.
- [ ] Refactor del pipeline (para los 3 Protocols nuevos) en un commit
      mecánico: cambiar call sites, cero cambio semántico. Tests existentes
      deben seguir pasando.
- [ ] Refactor de helpers externos que lean driver raw → aceptar el Protocol.
- [ ] Tests unitarios por impl + un test de paridad (mismo input, ambos
      backends, outputs equivalentes).
- [ ] Borrado de adapters transicionales y módulos huérfanos al flipear el
      default.
