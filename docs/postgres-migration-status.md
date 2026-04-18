# postgres-migration — estado de merge (2026-04-18)

> **Veredicto:** rama en punto natural de merge como **Phase 1**. Infra completa,
> feature-flagged como opcional, read path parcial pero validado contra oracle
> de Neo4j. Los follow-ups son extensiones seguras sobre esta base.
>
> **Feature flag:** `ALEJANDRIA_STORAGE_BACKEND` default `"sqlite"` → mergear no cambia comportamiento en producción.

## Qué entrega esta rama (must-have para mergear)

### Infra y datos

- ✅ Postgres 16 + pgvector 0.8.2 + pg_trgm + unaccent en IONOS VPS M
  (`212.227.243.210`), TLS self-signed, UFW, IONOS Cloud Firewall.
- ✅ SSH key auth para scripting. SSH tunnel laptop→VPS documentado.
- ✅ `pg_dump` cron diario a 03:15 UTC con rotación 14 días (primer backup 656 MB).
- ✅ DB `alejandria` con `SCHEMA_VERSION=2`, 9 tablas + `entity_document_mentions`.
- ✅ 811,954 entities + 21.2M relations + 3.5M mentions migradas desde SQLite + Neo4j.
- ✅ Cleanup R0 (garbage + merges canonical) + R7 (kill CO_OCCURS_WITH + ASSOCIATED_WITH llm_low) aplicados.

### Código portable (feature-flagged, default off)

- ✅ `src/alejandria/storage/postgres/` módulo completo:
  - `connection.py`, `schema.py` (v2), `ddl.sql` canónico.
  - `migrate_sqlite.py` + `migrate_neo4j.py` idempotentes (streaming + COPY).
  - `kg_cleanup.py` (R0) + `kg_r7_kill_noise.py` reusables.
- ✅ Filtros R1/R3 en ingesta: `knowledge/gazetteer_lookup.py` centralizado;
  `extractor.py` y `ner_candidates.py` usan gate unificado.
- ✅ R2 retention policy al final de cada KG rebuild (`prune_low_value`).
- ✅ `search/postgres_textual.py` + `search/postgres_semantic.py` con factories.
- ✅ `knowledge/postgres_graph_client.py` con 3 métodos implementados (`close`,
  `graph_summary`, `find_node`, `get_neighbors`). Otros 30 raise
  `NotImplementedError` con puntero al tier de implementación pendiente.
- ✅ DI wiring: `api/dependencies.py`, `cli.py`, `mcp_server.py` consumen
  `make_*` factories en vez de constructores directos.

### Tests

- 🟢 52 tests (schema, extractor filters, postgres_textual, postgres_semantic,
  postgres_graph_client, gazetteer_lookup) passing.
- 🟢 Validación de paridad Neo4j vs Postgres: 8/11 OK + 2 divergencias
  documentadas (una es Postgres WIN por cleanup; otra es limitación conocida
  del recursive CTE).

### Documentación

- ✅ `docs/postgres-migration.md` — plan maestro con estado real por fase.
- ✅ `docs/ionos-setup.md` — guía operativa reproducible del VPS.
- ✅ `docs/kg-client-port-audit.md` — auditoría pre-port de los 34 métodos.
- ✅ `docs/kg-ingestion-refactor.md` — backlog R0-R10 de hygiene del KG.
- ✅ `docs/vector-db-options.md` — análisis comparativo con triggers para reconsiderar.
- ✅ `benchmarks/postgres-migration/` — RESULTS (Fase 1), VALIDATION
  (SQLite migration), VALIDATION-KG (Neo4j migration), VALIDATION-CLEANUP
  (R0), VALIDATION-R7.
- ✅ `tests/parity/VALIDATION-TIER2AB.md` — reporte de paridad que certifica
  el approach REWRITE.
- ✅ 2 feedback memories nuevas (`feedback_docs_sync.md`).

## Delegado a follow-up PRs (nice-to-have, no bloquea merge)

### PR #1: `feature/postgres-kg-client-rest` (3-4 días)

Completar el port del KG client:

- [ ] **Tier 2c** (8 métodos): `get_typed_relations`, `get_typed_relations_batch`,
      `get_documents_for_entity`, `get_documents_for_entities_batch`,
      `get_all_entity_mentions`, `get_disambiguated_counts`, `find_nodes_batch`,
      `get_parallel_passages`. Todos con `ORDER BY confidence` — ver lección
      cross-cutting en `kg-client-port-audit.md §6.5ter`.
- [ ] **Tier 2d** (2 métodos): `get_genealogy_tree`, `get_genealogy_path`
      con recursive CTE + LIMIT intermedio + confidence ordering en SELECT final
      (arreglando la divergencia observada en q14).
- [ ] **Tier 2e**: expandir `capture_oracle` para los 31 queries del golden set;
      validación completa de paridad.

### PR #2: `feature/postgres-write-path` (3-5 días)

Portar el write path de ingesta a Postgres:

- [ ] `ingestion/registry.py` refactor a driver abstracto (SQLite + Postgres).
- [ ] `knowledge/profile_store.py` refactor. Resolver `_staging_profiles` que
      dejó el migrador SQLite.
- [ ] `ingestion/pipeline.py`: write path unificado con `COPY` por batch en
      lugar de Neo4j UNWIND. Entity profiles staging + resolve a `entity_id`.
- [ ] Tests de ingesta contra Postgres.

### PR #3: `feature/postgres-cutover` (1-2 semanas wait-heavy)

Corte en frío del stack antiguo:

- [ ] Correr ingesta completa con `ALEJANDRIA_STORAGE_BACKEND=postgres` en
      un subset del corpus.
- [ ] Validar 31 golden queries con overlap ≥ 80 % en el día-1 de paralelo.
- [ ] Flip del default a `postgres` en `config.py`.
- [ ] 30 días de Neo4j + SQLite read-only como fallback.
- [ ] Monitoreo de latencia / errores.

### PR #4: `feature/sunset-sqlite-neo4j` (1 día)

Tear down del stack antiguo post-cutover exitoso:

- [ ] Eliminar `neo4j_client.py`, `textual.py` (SQLite), `semantic.py` (sqlite-vec paths).
- [ ] Eliminar endpoints deprecados (`migrate_untyped_relations` etc.).
- [ ] Actualizar `docs/architecture.md`, `docs/ingestion.md`, `docs/stack.md`.
- [ ] Actualizar `CLAUDE.md` para hacer Postgres canónico.
- [ ] Remover dependencias opcionales `semantic` + `graph` si ya no se usan.
- [ ] Decommissionar contenedor Neo4j en el GPU Docker stack.

## Otras mejoras opcionales (backlog, no asignadas)

Ninguna bloquea la migración. Se ejecutan cuando haya ventana y
justifique ROI:

- **R5** — cross-language honorific merge (Señor Jesucristo, Su Hijo Jesucristo).
  Requiere extender `gazetteer_lookup.normalize` con strip de honoríficos.
- **R6** — decidir destino del mecanismo `ner_candidates.promote/dismiss`
  (0 promotions históricas). Opciones (a) usar activamente, (b) auto-promover,
  (c) eliminar mecanismo.
- **R8** — profile generation lazy (top-K por `mention_count` en ingesta).
- **R10** — type correctness pass sobre 800k entities (scripture refs como
  `period`, lugares europeos como `person`, etc.). Ver `kg-ingestion-refactor.md §R10`.
- **Upgrade VPS L** (8 GB RAM) si el corpus crece 5x+ y `shared_buffers` aprieta.
- **Backup `.env` cifrado** a GitHub Release encrypted, como disaster recovery
  de credenciales Postgres.

## Criterio de aceptación para mergear

- [x] Tests pasan (52 + validación de paridad)
- [x] Feature flag default sqlite (sin impacto runtime)
- [x] Docs reflejan estado real (no promesas)
- [x] Follow-up PRs con scope claro
- [x] CLAUDE.md actualizado para mencionar opción Postgres

## Qué NO hacer en futuros follow-ups

- No re-abrir Fase 0-2 (infra + migración + cleanup). Ya están cerradas.
- No añadir features no esenciales al port del KG client. Tiers 2c/2d son
  **ports mecánicos**, no rediseños. Divergencias semánticas complejas
  (disambiguation, profile enrichment) van a sus propios PRs.
- No mezclar R5/R6/R8/R10 con el port. Son hygiene independientes.
