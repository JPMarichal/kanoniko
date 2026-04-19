# Plan de remoción de Neo4j local + SQLite local

> **Estado:** plan, no ejecutado. La remoción real requiere coordinación
> porque el pipeline de escritura aún apunta a SQLite + Neo4j locales.

## Contexto

Phase 1 de `postgres-migration` mergeó (PR #3, 2026-04-18). **Postgres
IONOS es la fuente de verdad** para chunks, FTS, embeddings, entities,
relations, mentions. Neo4j local + SQLite local quedaron como mirrors
transitorios — eventualmente se eliminan.

## Qué se elimina

| Componente | Ubicación | Tamaño aprox |
|---|---|---:|
| Neo4j container | `alejandria-neo4j` (Docker, WSL) | ~6 GB DB + 1 GB image |
| Neo4j volume | `alejandria-neo4j` (Docker volume) | ~6 GB |
| SQLite WSL | `/home/jpmarichal/alejandria-data/sqlite/alejandria.db` | ~1.4 GB |
| SQLite Windows | `C:/own/alejandria/data/sqlite/alejandria.db` | variable, gitignored |
| Backup directories locales | `data/sqlite/backups/`, `data/sqlite/neo4j_backups/` | hasta GBs |

## Bloqueadores actuales

1. **Pipeline de escritura sigue escribiendo a SQLite + Neo4j**
   (`src/alejandria/ingestion/pipeline.py`). Cualquier ingesta nueva los
   re-popula. Hay que cortar primero.
2. **`PostgresGraphClient` solo tiene 3 métodos portados** (de ~15+).
   Ver `docs/kg-client-port-audit.md`. Las APIs de KG que no están
   portadas (chat, profile, disambiguation, etc.) hoy responden vía
   Neo4j; al eliminar Neo4j romperían sin un fallback completo en
   Postgres.
3. **`ALEJANDRIA_STORAGE_BACKEND` default sigue siendo `"sqlite"`**.
   Para que la API funcione contra Postgres por default hay que cambiarlo,
   y para que ese cambio sea seguro hay que completar el port.

## Pasos del plan (en orden)

1. **Completar `PostgresGraphClient`** — implementar los métodos
   `NotImplementedError` listados en `docs/kg-client-port-audit.md`.
   Cubrir con tests de paridad contra Neo4j antes de borrar este último.
2. **Cortar el write path local** — modificar
   `src/alejandria/ingestion/pipeline.py` para que las escrituras vayan a
   Postgres (entities, relations, chunks, mentions) cuando
   `ALEJANDRIA_STORAGE_BACKEND="postgres"`.
3. **Cambiar el default a `"postgres"`** en `src/alejandria/config.py`
   y `.env.example`. Actualizar tests.
4. **Validar el ciclo completo** — ingesta nueva debe poblar IONOS sin
   tocar Neo4j/SQLite locales. Búsquedas (textual, semantic, KG, chat)
   deben funcionar end-to-end contra Postgres.
5. **Sincronizar el último delta SQLite→Postgres** si hubo escrituras
   locales después del merge inicial (verificar con `migrate_sqlite.py`).
6. **Detener y remover Neo4j**:
   ```bash
   docker stop alejandria-neo4j
   docker rm alejandria-neo4j
   docker volume rm alejandria_alejandria-neo4j  # name puede variar
   docker rmi neo4j:5-community  # opcional, libera ~1 GB
   ```
   Eliminar el servicio `neo4j:` y dependencias en
   `docker/docker-compose.yml` y `docker/docker-compose.gpu.yml`.
7. **Eliminar SQLite WSL**:
   ```bash
   rm -f /home/jpmarichal/alejandria-data/sqlite/alejandria.db*
   rm -rf /home/jpmarichal/alejandria-data/sqlite/backups
   rm -rf /home/jpmarichal/alejandria-data/sqlite/neo4j_backups
   ```
   Quitar el bind-mount `/home/jpmarichal/alejandria-data/sqlite ->
   /app/data/sqlite` del compose.
8. **Eliminar SQLite Windows** (si existe; está gitignored):
   ```powershell
   Remove-Item C:/own/alejandria/data/sqlite -Recurse -Force
   ```
9. **Limpiar código legacy** — quitar `src/alejandria/storage/` rutas
   SQLite, `src/alejandria/knowledge/neo4j_client.py`, hooks de backup
   local. Marcar como deprecated antes de borrar para una versión.
10. **Actualizar docs** — `CLAUDE.md` (sacar feature flag dual,
    sacar sección "Local SQLite + Neo4j son transitionales"),
    `docs/architecture.md`, README.

## Validaciones antes de cada paso destructivo

- `pg_dump` reciente de IONOS verificado y restaurable.
- Búsqueda hybrid + chat funcionando en Postgres.
- Tests de integración pasando con `ALEJANDRIA_STORAGE_BACKEND=postgres`.

## Tiempo estimado

Pasos 1-4: el bulk del trabajo (días-semanas, requiere portar y testear).
Pasos 5-10: una sesión enfocada (~2-4 h) una vez que 1-4 estén listos.
