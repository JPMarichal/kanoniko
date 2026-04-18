# PR — Phase 1: Postgres as alternative backend

> Draft description for the GitHub PR. Delete this file before merge (or keep as history).

## Summary

Introduces **Postgres 16 + pgvector** as a feature-flagged alternative backend. Full data layer (chunks, FTS, embeddings, entities, relations, mentions) replicated to an IONOS VPS. Read-side ports for the 3 most-used KG client methods validated against a Neo4j oracle. Feature flag defaults to `"sqlite"` — **merging does not change runtime behavior**.

## What's included

- **Infra** — Postgres 16 + pgvector on IONOS VPS, TLS, UFW, IONOS Cloud Firewall, `pg_dump` cron daily, SSH tunnel for corporate networks.
- **Data layer** — 9 tables + `entity_document_mentions` (schema v2). Migradores idempotentes SQLite + Neo4j. R0 + R7 cleanup reusables.
- **Read backends** — `postgres_textual`, `postgres_semantic`, `postgres_graph_client` (3 of 30+ methods) + factories wired into DI / CLI / MCP.
- **Prevention filters** — R1/R3 gate in ingestion (`gazetteer_lookup.should_skip_ner_entity`); R2 retention policy at end of KG rebuild.
- **Parity validation** — 3 methods × 11 queries compared Neo4j vs Postgres. 8 OK, 2 documented divergences (one Postgres WIN, one known limitation).

## What's NOT included (follow-up PRs, documented in `docs/postgres-migration-status.md`)

1. `feature/postgres-kg-client-rest` — remaining 13 KG client methods.
2. `feature/postgres-write-path` — ingestion cutover (pipeline + profile_store + registry).
3. `feature/postgres-cutover` — parallel A/B + flip default + 30-day read-only archive.
4. `feature/sunset-sqlite-neo4j` — tear down old stack.

## Test plan

- [ ] `pytest tests/` passes locally (52 tests + 19 new Postgres graph client tests).
- [ ] `ALEJANDRIA_STORAGE_BACKEND=sqlite` (default) behavior unchanged — run existing integration smoke tests.
- [ ] `ALEJANDRIA_STORAGE_BACKEND=postgres` with IONOS Postgres reachable: 3 implemented methods return sensible data (validated with `tests/parity/compare_oracles.py`).
- [ ] Docs build / links valid: `docs/postgres-migration-status.md` is the entry point.

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| `NotImplementedError` stubs in `postgres_graph_client.py` if someone flips the flag | Default stays `sqlite`; flipping before follow-up PR #1 yields clear error with tier reference. |
| Feature flag untested in production | By design — that's PR #3 (cutover). |
| Schema version drift if follow-ups add v3 | `SCHEMA_VERSION` + `schema_version` table tracks migrations explicitly. |

## Metrics

- 52 tests passing.
- Postgres IONOS: 6.6 GB final size — **–18 % vs combined SQLite + Neo4j (8.1 GB)**.
- KG cleanup: –8,807 garbage entities, –33M noise relations, merge of 1,244 canonical duplicates.
- Parity: 8/11 OK vs Neo4j on the implemented method subset.

## Screenshots / references

- `docs/postgres-migration-status.md` — merge-readiness executive summary.
- `docs/postgres-migration.md` — full plan with phase status.
- `docs/ionos-setup.md` — VPS setup guide (reproducible).
- `docs/kg-client-port-audit.md` — audit of all 34 KG client methods + port plan.
- `docs/vector-db-options.md` — Qdrant/Weaviate/Pinecone/Milvus comparison.
- `tests/parity/VALIDATION-TIER2AB.md` — parity report.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
