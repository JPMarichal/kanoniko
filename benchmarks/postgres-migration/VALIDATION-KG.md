# Migración Neo4j → Postgres — validación con datos reales

> **Fecha:** 2026-04-17 · **Rama:** `feature/postgres-migration`

Segunda mitad de Fase 2: ejercer el migrador `alejandria.storage.postgres.migrate_neo4j` contra el Neo4j live (`alejandria-neo4j:5-community`, 4.6 GB de data/) y cargar entidades + relaciones al Postgres 16 + pgvector del benchmark aislado.

---

## 1. Resultados de la carga

| Tabla | Origen (Neo4j) | Destino (Postgres) | Tiempo | Throughput |
|---|---:|---:|---:|---:|
| `entities` | 820,761 `:Entity` nodes | **820,761 ✓** | 17.6 s | ~46k rows/s |
| `entity_aliases` | 102 (aliases no vacíos) | **102 ✓** | <0.1 s | — |
| `relations` | 57,030,709 Entity→Entity | **57,030,709 ✓** | **47.8 min** | ~20k rows/s |
| | 3,984,835 Entity→Document | **skipped** (diseño) | — | — |
| **Total** | | | **~48 min** | |

### Notas clave
- Todas las 820,761 entidades del Neo4j están migradas — sin pérdida.
- Solo 102 entidades tenían aliases no vacíos en Neo4j (!); la mayoría del grafo tiene `aliases: []`. El gazetteer canónico con sus aliases ricos es externo a los nodos — vive en `knowledge/gazetteers/entities.json`. Esta observación importa para R5 del backlog KG (cross-language merge necesita el gazetteer, no los aliases de Neo4j).
- Las 3.98M relaciones Entity→Document (`MENTIONED_IN`, `REFERENCED_IN`) se saltan a propósito: el schema actual no las modela. Se pueden reconstruir desde Postgres chunks si resultan necesarias.
- Throughput de lectura Neo4j (~20k rows/s) es el cuello de botella, no la escritura Postgres. Esto es esperable: Neo4j bolt + filter en Python + COPY es serial. Paralelizando lectura (particionar por `rel_type`) se puede bajar a ~15-20 min.

### Bug resuelto durante el run
Primer run chocó con `statement_timeout` a los ~30 min con 57M rows enviados pero no commiteados. Fix: `SET statement_timeout = 0` dentro de la sesión de COPY (el resto del sistema sigue con timeout de seguridad). Ver `migrate_neo4j.py:206-209`.

---

## 2. Tamaño resultante — comparación fair con el stack actual

| | SQLite actual | Neo4j actual | Total stack actual | Postgres migrado | Delta |
|---|---:|---:|---:|---:|---:|
| Chunks + FTS + vectores | 3.5 GB | — | | 2.7 GB | |
| KG (entities + relations) | — | 4.6 GB | | 8.3 GB | |
| **Total** | **3.5 GB** | **4.6 GB** | **8.1 GB** | **11 GB** | **+36 %** |

**Postgres es 36 % más grande que el stack combinado actual**, no más pequeño. Razones:

1. **Índices B-tree sobre relations:** 4 índices (src+type, dst+type, type, category) sobre 57M filas añaden ~4.5 GB de sólo índices. Neo4j representa adyacencia nativa sin duplicación.
2. **Overhead de FK + MVCC:** cada fila en Postgres carga visibility metadata + xmin/xmax; Neo4j es más compacto en bytes/relación.
3. **Sin compresión nativa:** `pg_total_relation_size` no incluye TOAST/compresión automática; Neo4j comprime estructura.

### El punto rescatable — ruido medible

Los **29M `CO_OCCURS_WITH`** son ~50 % de `relations` (~4 GB de los 8 GB de esa tabla). Esa es exactamente la clase de edge que el backlog KG (R7) planea eliminar, porque:
- Confidence `llm_low` sistemática
- Ruido: dos entidades en el mismo chunk no implica relación real
- Reemplazables por similaridad semántica on-demand (pgvector sobre embeddings de profile summaries)

**Si R7 se ejecuta:** relations baja a ~28M filas → ~3-4 GB → total Postgres **~7 GB** (mejora neta sobre los 8.1 GB del stack actual).

### Reclasificación de prioridades

| Argumento a favor de migrar | ¿Sigue válido? |
|---|---|
| Multi-máquina | ✅ Sí, más fuerte ahora |
| Backup a GitHub resuelto | ✅ Sí (`pg_dump` al VPS) |
| Velocidad de escritura durante ingesta | ✅ Sí, 3-6x más rápido |
| Stack unificado (1 motor vs 3) | ✅ Sí, aún más valioso (simplifica ops) |
| Storage menor | ❌ Invalidado — +36 % hasta aplicar R7 |

**Conclusión estratégica:** la migración sigue valiendo la pena por **todos los demás motivos**, pero el argumento de "DB más pequeña" queda fuera hasta ejecutar R7. **R7 sube de prioridad LOW a HIGH** — necesario para que el stack nuevo no sea peor en storage.

---

## 3. Verificación funcional

### kg_find (partial name + trgm)
```sql
SELECT id, name, entity_type FROM entities
WHERE name ILIKE '%Nefi%' ORDER BY name LIMIT 5;
```

Resultados: las primeras filas son "work" type (cabeceras de estudio semanal tipo `"10 – 16 febrero. 2 Nefi 6–10…"`), no personas. Muestra contaminación previa del KG que R0 debe limpiar.

### kg_neighbors (1 hop BELONGS_TO desde "Nefi" person)
```sql
WITH target AS (SELECT id FROM entities WHERE name = 'Nefi' AND entity_type = 'person' LIMIT 1)
SELECT e2.name, r.rel_type, r.confidence FROM relations r
JOIN target t ON r.src_id = t.id JOIN entities e2 ON e2.id = r.dst_id
WHERE r.rel_type NOT IN ('CO_OCCURS_WITH', 'ASSOCIATED_WITH') LIMIT 10;
```

Resultados incluyen: `Iglesia`, `La Iglesia de Jesucristo de los Santos de los Últimos Días`, `Autoridades Generales`, `Él`, `Su Iglesia`, `Sociedad de Socorro`, `Espíritu Santo`, `Escuela Dominical`. Todas marcadas BELONGS_TO.

**Interpretación:** un profeta del Libro de Mormón "pertenece a" la Iglesia moderna y a la Sociedad de Socorro. Son errores de extracción LLM `llm_low` preservados del Neo4j. **Esto es exactamente el sesgo que el usuario flagueó** y que R0 cleanup debe resolver.

El motor (queries, índices, JOINs) está funcional; el **dato** es el que arrastra ruido.

---

## 4. Estado consolidado de Fase 2

| Sub-entregable | Estado |
|---|---|
| Módulo `storage/postgres/` (connection + schema + DDL + tests) | ✅ Commit `21ea4a5ef` |
| Migrador SQLite → Postgres | ✅ Commit `c5a276e47` |
| Migrador Neo4j → Postgres | ✅ este commit |
| Tests unitarios de ambos migradores | ⏳ pendiente |
| Fase 3: Adaptación de módulos (`search_*.py`, `postgres_graph_client.py`) | ⏳ pendiente |

### Datos migrados — snapshot final del Postgres bench
| Tabla | Rows | Size (con índices) |
|---|---:|---:|
| `document_registry` | 56,073 | 18 MB |
| `chunks` | 309,089 | 1.72 GB |
| `chunk_embeddings` | 217,370 | 750 MB |
| `entities` | 820,761 | 177 MB |
| `entity_aliases` | 102 | 112 KB |
| `relations` | 57,030,709 | 7.9 GB |
| `ner_candidates` | 623,283 | 207 MB |
| `entity_profiles` | 0 | 16 KB |
| **Total DB** | | **11 GB** |

---

## 5. Reproducir esta validación

```bash
# Reset KG tables en el bench Postgres
wsl -d Ubuntu-20.04 bash -c "docker exec alejandria-pg-bench psql -U bench -d alejandria_bench \
  -c 'TRUNCATE entities, entity_aliases, relations RESTART IDENTITY CASCADE'"

# Container bi-red (docker_default para Neo4j, postgres-migration_default para Postgres bench)
wsl -d Ubuntu-20.04 bash -c '
docker run -d --name=bench-migrator --network docker_default \
  -v /mnt/c/own/alejandria:/app -w /app -e PYTHONPATH=/app/src \
  -e ALEJANDRIA_POSTGRES_HOST=postgres -e ALEJANDRIA_POSTGRES_USER=bench \
  -e ALEJANDRIA_POSTGRES_PASSWORD=bench -e ALEJANDRIA_POSTGRES_DB=alejandria_bench \
  -e ALEJANDRIA_POSTGRES_SSLMODE=disable \
  -e ALEJANDRIA_NEO4J_URI=bolt://neo4j:7687 -e ALEJANDRIA_NEO4J_USER=neo4j \
  -e ALEJANDRIA_NEO4J_PASSWORD=alejandria \
  python:3.12-slim sleep 7200
docker network connect postgres-migration_default bench-migrator
docker exec bench-migrator bash -c "pip install -q psycopg[binary] neo4j pydantic-settings"
docker exec bench-migrator python -m alejandria.storage.postgres.migrate_neo4j --reset --no-schema
'
```
