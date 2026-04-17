# Migración a Postgres + pgvector (Alejandría)

> **Rama:** `feature/postgres-migration` · **Estado:** diseño (pre-implementación)

Este documento define la arquitectura objetivo, el plan de fases, criterios de éxito y plan de rollback para migrar Alejandría desde el stack actual **SQLite (FTS5 + sqlite-vec) + Neo4j** hacia **Postgres 16 + pgvector** alojado en IONOS VPS M.

---

## 1. Motivación

Tres dolores observados hoy:

1. **Tamaño del archivo SQLite (3.4 GB)** — excede cómodamente el límite práctico de GitHub Releases (2 GB) y crece linealmente con el corpus.
2. **Ingesta lenta** — reindexación completa ~7h; la fase de escritura a Neo4j es el cuello de botella después de embeddings.
3. **Multi-máquina sin dolor** — handoff secuencial entre laptop laboral y máquina personal requiere sincronizar 3.4 GB o re-indexar.

El cambio de motor por sí solo no resuelve los tres, pero **externalizar la DB a IONOS** más **unificar FTS/vectores/KG en Postgres** los ataca todos:

| Dolor | Mecanismo de solución |
|---|---|
| Tamaño local | La DB vive en VPS; máquinas locales solo tienen corpus + código |
| Respaldo a GitHub | Obsoleto: `pg_dump` en el VPS reemplaza el Release asset de SQLite |
| Ingesta | `COPY FROM STDIN` es 3-6x más rápido que Neo4j UNWIND; unificación elimina escritura dual |
| Multi-máquina | DB remota única, ambas máquinas son clientes |

---

## 2. Arquitectura objetivo

### 2.1 Topología

```
┌──────────────────────────────┐         ┌──────────────────────────────┐
│  Máquina local (GPU)         │         │  IONOS VPS M                 │
│                              │         │                              │
│  ┌────────────────────────┐  │         │  ┌────────────────────────┐  │
│  │ corpus/ (bind-mount)   │  │         │  │  Postgres 16           │  │
│  │ embeddings model (GPU) │  │         │  │  + pgvector            │  │
│  │ ingestion pipeline     │──┼─TLS────►│  │  + tsvector (FTS)      │  │
│  │ FastAPI (solo dev)     │  │  COPY   │  │  + relations table     │  │
│  └────────────────────────┘  │         │  │  (KG unificado)        │  │
│                              │         │  │                        │  │
│                              │◄──────►─┼──┤  FastAPI (prod)        │  │
│                              │ queries │  │  pg_dump cron          │  │
└──────────────────────────────┘         │  └────────────────────────┘  │
                                         └──────────────────────────────┘
```

- **GPU local** retiene la generación de embeddings (único lugar que la justifica).
- **VPS** hospeda Postgres y opcionalmente la API pública. El cliente FastAPI puede correr en ambos lados según conveniencia.
- **Comunicación** sobre TLS; credenciales vía variables de entorno encriptadas.

### 2.2 Esquema lógico

Postgres reemplaza seis elementos del stack actual:

| Origen (hoy) | Destino (Postgres) |
|---|---|
| SQLite `chunks` | `chunks` (tabla relacional) |
| SQLite `chunks_fts` (FTS5 virtual) | Columna `tsvector` en `chunks` + índice GIN |
| SQLite `chunk_vectors` (vec0) | `chunk_embeddings` con `vector(384)` + índice HNSW |
| SQLite `document_registry` | `document_registry` (tabla relacional) |
| SQLite `entity_profiles` | `entity_profiles` (tabla relacional) |
| SQLite `ner_candidates` | `ner_candidates` (tabla relacional) |
| Neo4j `(e:Entity)` nodes | `entities` + `entity_aliases` |
| Neo4j `(d:Document)`, `(c:Chapter)`, `(n:Narrative)` | `graph_nodes` (poliformo) o tablas dedicadas |
| Neo4j relations (67 tipos) | `relations` (tabla normalizada con enum + JSONB props) |

DDL canónico (orientativo, se refinará en implementación):

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- === Index Layer ===

CREATE TABLE document_registry (
  file_path     TEXT PRIMARY KEY,
  sha256        TEXT NOT NULL,
  file_size     BIGINT NOT NULL,
  chunk_count   INTEGER NOT NULL DEFAULT 0,
  last_indexed  TIMESTAMPTZ NOT NULL DEFAULT now(),
  status        TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE chunks (
  id            BIGSERIAL PRIMARY KEY,
  file_path     TEXT NOT NULL REFERENCES document_registry(file_path) ON DELETE CASCADE,
  chunk_index   INTEGER NOT NULL,
  text          TEXT NOT NULL,
  reference     TEXT,
  start_char    INTEGER,
  end_char      INTEGER,
  metadata      JSONB NOT NULL DEFAULT '{}',
  language      CHAR(2),                          -- 'es' | 'en'
  tsv           tsvector GENERATED ALWAYS AS (
                  to_tsvector(
                    CASE language WHEN 'es' THEN 'spanish' ELSE 'english' END,
                    unaccent(text)
                  )
                ) STORED
);
CREATE INDEX chunks_tsv_gin ON chunks USING GIN (tsv);
CREATE INDEX chunks_file_idx ON chunks(file_path);
CREATE INDEX chunks_metadata_gin ON chunks USING GIN (metadata);

CREATE TABLE chunk_embeddings (
  chunk_id      BIGINT PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
  embedding     vector(384) NOT NULL,
  model_version TEXT NOT NULL DEFAULT 'paraphrase-multilingual-MiniLM-L12-v2'
);
CREATE INDEX chunk_embeddings_hnsw ON chunk_embeddings
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- === Knowledge Layer ===

CREATE TABLE entities (
  id            BIGSERIAL PRIMARY KEY,
  name          TEXT NOT NULL,
  entity_type   TEXT NOT NULL,          -- person, place, concept, etc.
  disambiguator TEXT,
  metadata      JSONB NOT NULL DEFAULT '{}',
  UNIQUE (name, entity_type, disambiguator)
);
CREATE INDEX entities_name_trgm ON entities USING GIN (name gin_trgm_ops);
CREATE INDEX entities_type_idx ON entities(entity_type);

CREATE TABLE entity_aliases (
  entity_id     BIGINT REFERENCES entities(id) ON DELETE CASCADE,
  alias         TEXT NOT NULL,
  language      CHAR(2),
  PRIMARY KEY (entity_id, alias)
);
CREATE INDEX entity_aliases_alias_trgm ON entity_aliases USING GIN (alias gin_trgm_ops);

CREATE TABLE relations (
  id            BIGSERIAL PRIMARY KEY,
  src_id        BIGINT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  dst_id        BIGINT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  rel_type      TEXT NOT NULL,          -- authored, parent_of, prophesied, etc.
  category      TEXT,                    -- family, governance, prophetic...
  confidence    TEXT NOT NULL DEFAULT 'llm_low',  -- curated|metadata|llm_high|llm_low|ner
  source_ref    TEXT,                    -- scripture reference
  source        TEXT,                    -- curated_seed|metadata_extraction|llm|co_occurrence
  verified      BOOLEAN NOT NULL DEFAULT false,
  role          TEXT,                    -- for AUTHORED: author|compiler|editor...
  properties    JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX relations_src_type_idx ON relations(src_id, rel_type);
CREATE INDEX relations_dst_type_idx ON relations(dst_id, rel_type);
CREATE INDEX relations_type_idx ON relations(rel_type);
CREATE INDEX relations_category_idx ON relations(category);

CREATE TABLE entity_profiles (
  entity_id     BIGINT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
  mention_count INTEGER NOT NULL DEFAULT 0,
  document_count INTEGER NOT NULL DEFAULT 0,
  books         JSONB NOT NULL DEFAULT '[]',
  key_passages  JSONB NOT NULL DEFAULT '[]',
  summary_en    TEXT,
  summary_es    TEXT,
  profile_version INTEGER NOT NULL DEFAULT 0,
  status        TEXT NOT NULL DEFAULT 'metadata',
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ner_candidates (
  id            BIGSERIAL PRIMARY KEY,
  name          TEXT NOT NULL,
  entity_type   TEXT NOT NULL,
  frequency     INTEGER NOT NULL DEFAULT 1,
  status        TEXT NOT NULL DEFAULT 'candidate',  -- candidate|promoted|rejected
  first_seen    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (name, entity_type)
);
CREATE INDEX ner_freq_idx ON ner_candidates(frequency DESC);
CREATE INDEX ner_status_idx ON ner_candidates(status);
```

### 2.3 Queries equivalentes a tools MCP actuales

| Tool MCP | Patrón Postgres |
|---|---|
| `kg_find` | `SELECT … FROM entities WHERE name ILIKE %q% OR id IN (SELECT entity_id FROM entity_aliases WHERE alias ILIKE %q%)` con `pg_trgm` |
| `kg_neighbors` | `SELECT … FROM relations r JOIN entities e ON (e.id = r.dst_id) WHERE r.src_id = $1` (+ inverso) |
| `kg_relations` | `WHERE src_id = $1 AND category = $2` |
| `kg_profile` | Join entities + entity_profiles + agregación sobre relations |
| `kg_genealogy_path` | Recursive CTE limitado a `rel_type IN ('parent_of','son_of','daughter_of')` con profundidad máxima |
| `kg_genealogy_tree` | Recursive CTE hacia abajo |
| `search_text` | `WHERE tsv @@ websearch_to_tsquery(lang, query)` ordenado por `ts_rank_cd` |
| `search_semantic` | `ORDER BY embedding <=> $query_vec LIMIT k` |
| `search_hybrid` | RRF fusion de ambas (misma lógica de `search/hybrid.py` actual, queries distintos) |
| `kg_docs` | Relations a Document entity + join a documents |
| `kg_summary` | Conteos agregados sobre entities + relations |

**Decisión pendiente:** si AGE aporta legibilidad suficiente para genealogías como para justificar la extensión, o si recursive CTEs bastan. Se define en fase 2 con benchmark.

---

## 3. Plan de fases

### Fase 0 — Preparación (1-2 días)
- Provisionar Postgres 16 en IONOS VPS (systemd, TLS con Let's Encrypt, pgbouncer opcional).
- Configurar `postgresql.conf` para 4 GB RAM: `shared_buffers = 1GB`, `effective_cache_size = 2.5GB`, `work_mem = 32MB`, `maintenance_work_mem = 512MB`.
- Instalar extensiones: `pgvector`, `pg_trgm`, `unaccent`.
- Configurar backups: `pg_dump` diario cifrado a un segundo volumen.
- Crear usuario `alejandria_rw` y `alejandria_ro`; capturar secretos en `.env.vps` (cifrado).
- Abrir firewall solo para IPs específicas + puerto 5432 sobre TLS.

### Fase 1 — Benchmark validatorio (2-3h)
- Subset: 10k chunks + 100k relaciones.
- Medir:
  - Ingesta vía `COPY` vs ingesta SQLite-equivalente hoy.
  - Latencia p50/p95/p99 de 3 queries típicas (FTS, semántica, `kg_profile`, `kg_genealogy_path` a 5 hops).
  - Network RTT desde GPU local al VPS.
- **Go / no-go:** si ingesta ≥3x Neo4j y queries KG < 500ms p95, continuar.

### Fase 2 — Schema + migrador (3-5 días)
- Crear módulo `src/alejandria/storage/postgres/` con conexión, DDL, migraciones Alembic.
- Script `scripts/migrate_sqlite_to_postgres.py`: exporta chunks/registry/profiles/ner a CSV/TSV, `COPY` al VPS.
- Script `scripts/migrate_neo4j_to_postgres.py`: dump nodes+edges → tablas `entities`, `entity_aliases`, `relations`.
- Validación: conteos por tabla, checksums por file_path, spot-check de queries típicas.

### Fase 3 — Adaptación de módulos (1-2 semanas)
Orden sugerido, de menor a mayor acoplamiento:
1. `search/textual.py` → `search/postgres_textual.py` (tsvector + ts_rank).
2. `search/semantic.py` → `search/postgres_semantic.py` (pgvector HNSW).
3. `search/hybrid.py` — reutiliza, solo cambia las fuentes.
4. `ingestion/registry.py` → cambio de driver.
5. `knowledge/neo4j_client.py` → `knowledge/postgres_graph_client.py` (CTEs recursivos).
6. `knowledge/profile_store.py` → cambio de driver.
7. `ingestion/pipeline.py` → write path unificado con `COPY` por batch.

**Feature flag:** `ALEJANDRIA_BACKEND=sqlite|postgres` en `config.py`. Permite correr ambos stacks en paralelo durante transición.

### Fase 4 — Paralelo y cutover (3-5 días)
- Correr ambos backends en paralelo una semana; comparar resultados de `mcp__alejandria__chat_ask` con queries de referencia.
- Diff automatizado de top-10 resultados por search mode.
- Cutover: flip del flag en producción, API lee de Postgres.
- Neo4j y SQLite quedan como read-only archive 30 días.

### Fase 5 — Limpieza (1 día)
- Eliminar código SQLite/Neo4j path si benchmark de producción se sostiene 2 semanas.
- Actualizar `docs/architecture.md`, `docs/ingestion.md`, `docs/stack.md`.
- Actualizar `CLAUDE.md` sección Backup & DR.

---

## 4. Criterios de éxito

| Métrica | Umbral |
|---|---|
| Ingesta completa (reindex) | ≤ 2h (vs ~7h actual) |
| Ingesta incremental por archivo | ≤ 1s promedio |
| `search_hybrid` p95 | ≤ 400ms (incluye RTT VPS) |
| `kg_profile` p95 | ≤ 300ms |
| `kg_genealogy_path` p95 (5 hops) | ≤ 500ms |
| Tamaño DB sin vectores | ≤ 40% del SQLite actual |
| Tamaño DB con vectores | ≤ 70% del SQLite actual |
| Paridad de resultados top-10 vs stack actual | ≥ 90% overlap |
| RAM uso en VPS sin carga | ≤ 2 GB (deja headroom) |

---

## 5. Plan de rollback

### Nivel 1 — Feature flag (segundos)
`ALEJANDRIA_BACKEND=sqlite` revierte API a stack original. Requiere que Neo4j y SQLite sigan running.

### Nivel 2 — Restore SQLite (minutos)
`scripts/backup-pull.sh db` + `gunzip` restaura el SQLite comprimido del último GitHub Release. Postgres permanece intacto.

### Nivel 3 — Limpieza total (si migración falla definitivamente)
- Borrar tablas Postgres, liberar VPS para otro uso.
- Merge de rama revertido con `git revert`.
- `docs/postgres-migration.md` marcado como "abandoned — ver postmortem".

---

## 6. Decisiones abiertas (a resolver durante implementación)

1. **AGE vs recursive CTE** para genealogías profundas — decidir tras benchmark fase 1.
2. **pgbouncer** delante de Postgres — solo si observamos >50 conexiones concurrentes (improbable con 1-2 máquinas).
3. **Model version tracking en embeddings** — hoy implícito; la columna `model_version` habilita migraciones de modelo sin re-indexar todo.
4. **Particionamiento por `file_path`** — no necesario hoy; considerar si corpus > 500 GB.
5. **Replicación a segundo VPS** — fuera de scope inicial; `pg_dump` cifrado + sync a GitHub (< 2 GB comprimido) cubre el caso de DR.

---

## 7. Riesgos identificados

| Riesgo | Mitigación |
|---|---|
| Latencia VPS mata UX de búsqueda interactiva | Benchmark fase 1 — si p95 > 500ms con RTT, evaluar CDN de queries o mover la API al VPS |
| RAM 4 GB insuficiente al crecer corpus 5x | Plan de upgrade a IONOS VPS L (8 GB); disparador: RAM >3 GB sostenida 1 semana |
| `pg_dump` de DB grande satura red en horario pico | Programar en ventana nocturna; usar `pg_basebackup` incremental si crece mucho |
| Paridad de resultados con Neo4j en queries complejos | Golden dataset de 50 queries con respuestas esperadas, validación automatizada |
| Pérdida de features Neo4j específicos (shortest-path optimizado) | Benchmark real de queries actuales antes de comprometerse; AGE como plan B |

---

## 8. Trabajo fuera de scope

- Migrar el backend LLM local (rama `feature/local-llm-backend`) — independiente.
- Refactor del pipeline de embeddings para soportar modelos distintos — tema aparte.
- Dashboard de observabilidad del VPS — posterior a cutover.
- Autenticación multi-tenant — no es necesario mientras sea proyecto de un solo usuario.

---

## 9. Referencias internas

- `docs/architecture.md` — stack actual.
- `docs/ingestion.md` — pipeline actual a reemplazar.
- `docs/performance.md` — benchmarks históricos.
- `docs/project-memory/feedback_batch_neo4j.md` — lección sobre batching que informa el diseño de `COPY`.
- `docs/project-memory/reference_indexing_benchmarks.md` — baseline actual 779 archivos / 1632 chunks en ~8min GPU.
