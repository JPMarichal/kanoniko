# Migración SQLite → Postgres — validación con datos reales

> **Fecha:** 2026-04-17 · **Rama:** `feature/postgres-migration`

Primer paso de Fase 2: ejercer el migrador (`alejandria.storage.postgres.migrate_sqlite`) contra la SQLite live (`/home/jpmarichal/alejandria-data/sqlite/alejandria.db`, 3.5 GB) y cargar su contenido en el Postgres 16 + pgvector del benchmark aislado.

---

## 1. Resultados de la carga

| Tabla | Origen (SQLite) | Destino (Postgres) | Tiempo | Throughput |
|---|---:|---:|---:|---:|
| `document_registry` | 56,073 | **56,073 ✓** | 0.3 s | ~187k rows/s |
| `chunks` | 309,089 | **309,089 ✓** | 142.4 s | 2,170 rows/s |
| `chunk_embeddings` | 325,050 (vec0) | **217,370 ✓** | 24.2 s | 8,984 rows/s |
| `entity_profiles` | 0 | 0 ✓ | 0.0 s | — |
| `ner_candidates` | 623,283 | **623,283 ✓** | 6.0 s | 104,209 rows/s |
| **Subtotal copia** | | | **~173 s** | |
| **Build HNSW** (217k × 384-dim) | — | — | **40.7 s** | — |
| **Total migración** | | | **~214 s (3.5 min)** | |

### Notas
- **107,680 vectores huérfanos** descartados (33% del total en `chunk_vectors`). Son residuo de chunks recreados durante la ingesta incremental sin limpieza de vectores. El migrador los salta vía `valid_ids` set en memoria.
- `chunks` es la fase más lenta porque el trigger de tsvector GENERATED STORED se dispara por fila; no hay forma de bulk-skipearlo (el índice GIN debe llenarse). A esta velocidad, ingesta incremental de 1-2k chunks nuevos toma ~1s.
- `ner_candidates` es súper rápido (104k rows/s) porque es texto plano sin índices pesados ni generated columns.

---

## 2. Tamaño resultante — el dato incómodo

| | SQLite actual | Postgres migrado | Delta |
|---|---:|---:|---:|
| DB size | 3.5 GB | **2.7 GB** | **–23 %** |
| chunks + FTS índices | — | 1.72 GB | — |
| chunk_embeddings + HNSW | — | 346 MB | — |
| ner_candidates | — | 207 MB | — |
| document_registry | — | 18 MB | — |
| otros (entities, profiles, aliases) | — | <1 MB (aún vacías) | — |

Proyección al completar Fase 2 (Neo4j → entities/aliases/relations, probable +300-500 MB):
- **Postgres final estimado: ~3.0-3.2 GB**
- **Ahorro neto: ~10-15 %** sobre SQLite actual.

### ⚠️ Discrepancia respecto al benchmark de Fase 1
El benchmark predijo ~31 % del tamaño de SQLite (1 GB). El tamaño real termina en ~90 %. Causas:

1. **Texto real ≠ texto sintético.** El corpus tiene unicode (acentos, cirílico ocasional, bilingüe) y longitudes variables mayores; los chunks reales promedian ~5.5 KB vs ~2 KB del benchmark.
2. **FTS GIN sobre texto multilingüe real** crece más que sobre palabras sintéticas repetidas.
3. **623k `ner_candidates`** no estaban en el benchmark; añaden 207 MB.
4. **WAL y metadata de Postgres** añaden overhead que SQLite comprime.

**Implicación para el plan:** el beneficio de "reducir tamaño" es modesto (~15 %), no dramático. Los demás beneficios del doc de diseño **siguen vigentes**:

- Multi-máquina ✓ (DB remota vs archivo de 3.5 GB)
- Respaldo a GitHub resuelto ✓ (`pg_dump` al VPS, no a Release assets)
- Ingesta fase DB-write ✓ (115x más rápido que Neo4j batched)
- Stack unificado ✓ (un motor en vez de tres)

---

## 3. Verificación funcional

### FTS Query de ejemplo
```sql
SELECT id, reference, substr(text, 1, 80), ts_rank_cd(tsv, q)
FROM chunks, websearch_to_tsquery('spanish', 'Expiación Jesucristo') q
WHERE tsv @@ q ORDER BY 4 DESC LIMIT 3;
```

Resultados reales devueltos:
1. `Guía para el estudio del Evangelio # Expiación de Jesucristo — El sacrificio de nu…` (score 0.322)
2. `# Juan 3:14–17 "Porque de tal manera amó Dios al mundo"…` (score 0.318)
3. `"ese monstruo, muerte e infierno" y el "escape" que Dios ha preparado…` (score 0.310)

El FTS está funcionando end-to-end: stem spanish, ranking por `ts_rank_cd`, matcheo case-insensitive (gracias a `immutable_unaccent`).

### Embeddings / HNSW
- 217,370 vectores cargados sin errores.
- Índice HNSW construido en 40.7 s (ligeramente más rápido que lo extrapolado del benchmark: 7.66 s × 7.2x = 55 s esperado).
- Queries de similaridad no se probaron aún porque faltan entities para unir — se cierra en Fase 2.3.

### Nulos / corrupción
- 1 issue encontrado: **texto con NUL bytes (`\x00`)** en algunos chunks del corpus. Probable residuo de extracción de PDF. Se sanitiza en `_strip_nuls()` antes de `COPY`. Cero filas perdidas, solo bytes 0x00 eliminados.

---

## 4. Acciones pendientes antes de cerrar Fase 2

- [ ] Fase 2.2: migrador Neo4j → Postgres (`entities`, `entity_aliases`, `relations`).
- [ ] Fase 2.3: resolver `_staging_profiles` (JOIN a entities tras migrar Neo4j).
- [ ] Tests unitarios del migrador (helpers + mini SQLite sintético).
- [ ] Script de validación end-to-end (checksums por file_path, overlap de resultados FTS con stack actual).

---

## 5. Reproducir esta validación

```bash
# Reset del Postgres del benchmark
wsl -d Ubuntu-20.04 bash -c "docker exec alejandria-pg-bench psql -U bench -d alejandria_bench \
  -c 'TRUNCATE schema_version, document_registry, chunks, chunk_embeddings, entities, \
       entity_aliases, relations, entity_profiles, ner_candidates RESTART IDENTITY CASCADE; \
       DROP INDEX IF EXISTS chunk_embeddings_hnsw'"

# Correr el migrador (container Python 3.12 en la misma red compose)
wsl -d Ubuntu-20.04 bash -c "docker run --rm \
  --network postgres-migration_default \
  -v /mnt/c/own/alejandria:/app \
  -v /home/jpmarichal/alejandria-data/sqlite:/sqlite_data:ro \
  -w /app -e PYTHONPATH=/app/src \
  -e ALEJANDRIA_POSTGRES_HOST=postgres \
  -e ALEJANDRIA_POSTGRES_USER=bench -e ALEJANDRIA_POSTGRES_PASSWORD=bench \
  -e ALEJANDRIA_POSTGRES_DB=alejandria_bench -e ALEJANDRIA_POSTGRES_SSLMODE=disable \
  -e ALEJANDRIA_POSTGRES_STATEMENT_TIMEOUT_MS=300000 \
  python:3.12-slim bash -c 'pip install -q \"psycopg[binary]>=3.1\" sqlite-vec pydantic-settings \
    && python -m alejandria.storage.postgres.migrate_sqlite \
       --sqlite /sqlite_data/alejandria.db --reset'"

# HNSW aparte (post bulk load)
# python -c "from alejandria.storage.postgres.schema import ensure_hnsw_index; ensure_hnsw_index()"
```
