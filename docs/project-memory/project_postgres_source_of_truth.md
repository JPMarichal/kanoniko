---
name: Postgres IONOS = source of truth
description: Phase 1 of postgres-migration landed (PR #3, merged 2026-04-18). Postgres en IONOS VPS es la fuente de verdad del KG. Neo4j local y SQLite local son legacy/oracle.
type: project
---

**Fact:** La migración Phase 1 a Postgres + pgvector remoto (IONOS VPS 212.227.243.210) se completó y mergeó en `main` (PR #3, commit 426fafeb1, 2026-04-18). Toda corrección, escritura, lectura y verificación del KG, chunks y embeddings debe hacerse contra esa instancia.

**Conexión:** SSH tunnel `localhost:15432 → IONOS:5432`, ya activo en WSL (`pgrep ssh.*15432`). Credenciales en `.env` (`ALEJANDRIA_POSTGRES_*`).

**Tablas relevantes:** `entities`, `relations`, `chunks`, `entity_aliases`, `entity_document_mentions`, `ner_candidates`. Schema en `src/alejandria/storage/postgres/ddl.sql`.

**Why:** El usuario hizo merge formal del trabajo y considera Postgres IONOS como autoridad. Neo4j local + SQLite local quedan como artefactos transicionales — están programados para remoción una vez que el pipeline de escritura termine de portarse.

**How to apply:**
- Antes de cualquier operación destructiva o correctiva sobre el KG, **verificar Postgres IONOS** (no Neo4j local). El estado de Neo4j puede divergir y NO refleja la verdad operativa.
- `CLAUDE.md` puede estar desactualizado en este punto (decía "default sqlite, opt-in postgres") — la realidad post-merge es lo contrario. Confiar en lo que esta memoria y los commits recientes dicen.
- Cuando se vea `mcp__alejandria__kg_*`: esos tools leen vía la API local que apunta a Neo4j. Sirven solo como vista, NO como autoridad. Para verificar verdad, conectar directo a Postgres IONOS.
- Para correr scripts contra IONOS desde el container: `docker run --rm --network host -e ALEJANDRIA_POSTGRES_HOST=127.0.0.1 -e ALEJANDRIA_POSTGRES_PORT=15432 -e ALEJANDRIA_POSTGRES_USER=$ALEJANDRIA_POSTGRES_USER -e ALEJANDRIA_POSTGRES_PASSWORD=$ALEJANDRIA_POSTGRES_PASSWORD -e ALEJANDRIA_POSTGRES_DB=$ALEJANDRIA_POSTGRES_DB ...`. Cargar el `.env` con `set -a; source .env; set +a` desde un heredoc (no `bash -c "set -a; source ..."` porque las quotes interfieren).

**Pendiente operativo:** Completar `PostgresGraphClient` (faltan métodos KG según `docs/kg-client-port-audit.md`), portar pipeline de escritura, y entonces eliminar Neo4j local + SQLite Windows.
