# Ingestion Workflow

Proceso canónico para incorporar material nuevo al corpus de Alejandría.

> **Estado:** propuesta aprobada, implementación en curso. Ingestión **congelada** hasta completar la secuencia de migración (§3).
>
> **Progreso §3.1 (rama `feature/postgres-write-path`):**
> - ✅ ADR 0001 v2 aprobado — 3 Protocols cohesivos (ChunkWriter, KGWriter, KGReader) + Registry + ProfileStore, factory por flag.
> - ✅ `DocumentRegistry` + `ProfileStore` portados.
> - ✅ `ChunkWriter`, `KGWriter`, `KGReader` — Protocols definidos, Legacy adapters y Postgres impls entregados.
> - ✅ `CuratedSeedLoader` extraído como servicio (orquestación ≠ persistencia).
> - ✅ Pipeline refactorizado: 100+ call sites migrados a los 3 Protocols. Cero acceso a `_driver` raw. Los 5 helpers externos de Neo4j fueron absorbidos como métodos del KGWriter.
> - ✅ Imagen `docker-api` reconstruida con `psycopg3`.
> - ✅ Smoke tests verdes: Protocol-level + E2E `ingest_paths` contra Postgres IONOS (1 doc sintético → document_registry + chunks + embeddings + tsvector).
> - ✅ Golden queries: 16/31 ok en Postgres, 10/11 ok en Neo4j, **cero regresiones** del refactor.
> - ✅ **Default flipeado a `postgres`** (`config.py` + las 8 factorías). El flag sigue para pruebas pero las rutas de producción pasan a Postgres.
> - ⏳ §3.2 port completo de lectura KG (15 `NotImplementedError` pendientes en `PostgresGraphClient`).
> - ⏳ §3.3 retiro de Neo4j + `Legacy*` + contenedor `alejandria-neo4j`.
> - ⏳ §3.4 retiro de SQLite + `Sqlite*` + `TextualSearch`/`SemanticSearch` SQLite paths + flag.

## 1. Propósito y principios

Este documento define el workflow único para agregar material al corpus. Reemplaza el procedimiento previo que mezclaba descarga, formateo e indexado en pasos acoplados.

**Principios rectores:**

- **SRP (Single Responsibility):** cada paso hace una cosa y produce un artefacto verificable.
- **Idempotencia:** cada paso verifica si ya está hecho y es re-ejecutable sin efectos colaterales.
- **KISS:** un solo store de verdad (Postgres IONOS), backlogs en JSON plano, sin infra redundante.
- **Backlogs independientes:** cada operación (descubrir, investigar, descargar, indexar) tiene su propio backlog actualizable fuera del workflow principal.
- **Gates mínimos:** solo dos dependencias duras — reseña antes de autoridad/KG/formato, commit+sync antes de indexar. Todo lo demás es orden recomendado, no cadena.

## 2. Estado de congelación

**Ninguna ingestión nueva hasta completar §3.** Los recursos descubiertos o descargados durante la congelación se acumulan en `discovery.json` / `downloads.json` sin avanzar a indexado.

**Criterios de salida de la congelación:**

- Write-path único a Postgres IONOS funcionando end-to-end.
- Lectura KG completa desde Postgres (todos los métodos del cliente portados y validados).
- Neo4j local retirado.
- SQLite local retirado.
- Endpoints de backup/restore redibujados o marcados como retirados.

## 3. Secuencia de migración (prerequisito)

Las cuatro fases se ejecutan en orden. No se pueden paralelizar porque cada una cambia la superficie de la siguiente.

### 3.1 Cutover de escritura a Postgres

- Ingest escribe solo a Postgres IONOS.
- SQLite y Neo4j locales dejan de recibir writes.
- Flag `ALEJANDRIA_STORAGE_BACKEND` pasa a constante `"postgres"`.

### 3.2 Port completo de lectura KG a Postgres

- Completar métodos del cliente KG que hoy levantan `NotImplementedError` (ver `docs/kg-client-port-audit.md`).
- Validar cada método contra Neo4j como oráculo antes de retirarlo.
- Redirigir las herramientas MCP `mcp__alejandria__kg_*` a leer vía Postgres.

### 3.3 Retirar Neo4j local

- Quitar contenedor del `docker-compose`.
- Retirar endpoints `/backup/neo4j*` o reescribirlos sobre Postgres.
- Limpiar referencias en código, docs y scripts.

### 3.4 Retirar SQLite local

- Quitar `data/sqlite/` del runtime.
- Retirar endpoints `/backup/sqlite*`, `/index/rebuild-vectors` o reescribirlos sobre Postgres.
- Limpiar referencias en código, docs y scripts.

## 4. Los 9 pasos del workflow

Cada paso tiene una responsabilidad, un artefacto verificable y actualiza un backlog específico. El orden es recomendado; los gates marcados **BLOQUEANTE** son obligatorios.

| # | Paso | Responsabilidad | Artefacto verificable | Backlog que actualiza | Gate |
|---|------|-----------------|----------------------|----------------------|------|
| 1 | Descubrir | Identificar material candidato | Entrada en `discovery.json` | discovery | — |
| 2 | Descargar | Obtener el crudo de la fuente | Archivo en caché local + SHA | downloads | — |
| 3 | Clasificar y ubicar | Decidir categoría y path destino | Campos `category` y `target_path` en `discovery.json` | discovery | — |
| 4 | Investigar (reseña) | Producir reseña como producto | `prods/reseñas/{slug}/reseña.md` completo | research | **BLOQUEANTE** para 5, 6, 7 |
| 5 | Autoridad | Asignar authority/rigor/official | Entrada en `authority.py` `_SOURCE_DEFAULTS` o confirmación de default | — | — |
| 6 | KG pre-seed | Insertar relaciones curadas | Nodes/rels con `source="curated_seed"` en Postgres | — | **BLOQUEANTE** para 9 |
| 7 | Formatear | Convertir crudo a `.txt` + `.meta.json` | Archivos en `corpus/{lang}/{category}/...` | — | — |
| 8 | Commit + sync | Publicar archivos en el repo operativo | HEAD del repo Ubuntu-20.04 WSL contiene los archivos | — | **BLOQUEANTE** para 9 |
| 9 | Indexar | Persistir en Postgres (chunks, FTS, vectores, KG) | Entrada `status: "indexado"` en `indexing.json` + registros en Postgres | indexing | — |

**Notas operativas:**

- Paso 2 puede ejecutarse meses antes de los demás, o durante el paso 7 si no se hizo. El reconcile detecta el crudo y actualiza el backlog.
- Paso 7 reusa el crudo del paso 2 si existe; si no, baja al vuelo.
- Paso 9 escribe **solo a Postgres IONOS**. No hay write dual.

## 5. Backlogs

### 5.1 Ubicación

```
backlogs/
├── discovery.json
├── research.json
├── downloads.json
├── indexing.json
├── schemas/
│   ├── discovery.schema.json
│   ├── research.schema.json
│   ├── downloads.schema.json
│   └── indexing.schema.json
└── README.md
```

Todos los backlogs usan `slug` como clave primaria compartida, para que el reconcile pueda joinar por slug.

### 5.2 Esquemas (esbozo)

**discovery.json** — un recurso por entrada:
- `slug`, `title`, `source`, `language`, `category` (tentativa), `target_path`, `status` (`propuesto` | `clasificado` | `descartado`), `notes`.

**research.json**:
- `slug`, `review_path` (ruta a `prods/reseñas/{slug}/reseña.md`), `status` (`pendiente` | `en_progreso` | `completa`), `completed_at`.

**downloads.json**:
- `slug`, `source_url`, `skill` (skill usado: gospelink, byu-studies, etc.), `raw_path`, `sha256`, `status` (`pendiente` | `descargado` | `fallido`), `error`.

**indexing.json**:
- `slug`, `paths` (lista de paths relativos al corpus), `last_sha` (SHA del contenido indexado), `indexed_at`, `status` (`pendiente` | `indexado` | `stale`).

Los schemas JSON Schema formales viven en `backlogs/schemas/` y son la fuente de verdad del contrato.

### 5.3 Validación (pre-commit hook)

Un pre-commit hook valida los cuatro backlogs contra sus schemas antes de aceptar el commit. Si falla, el commit se rechaza.

- Extensión del hook existente (`scripts/pre-commit-sync.sh`) o hook nuevo dedicado — a decidir en implementación.
- Dependencia: `jsonschema` (Python). Documentar instalación en `backlogs/README.md`.

### 5.4 Reconcile

`scripts/reconcile-backlogs.py` — comando idempotente que:

1. Escanea el estado real del sistema de archivos y de Postgres.
2. Actualiza entradas de backlog según lo encontrado:
   - Crudo presente en caché → `downloads.status = descargado`.
   - `prods/reseñas/{slug}/reseña.md` completa → `research.status = completa`.
   - Archivos en `corpus/` con SHA nuevo → `indexing.status = stale`.
   - Registros en Postgres coinciden con SHA actual → `indexing.status = indexado`.
3. Reporta inconsistencias que no puede resolver automáticamente.

Se corre al inicio de cada sesión de trabajo con el corpus, o después de cualquier operación ejecutada fuera del workflow (descarga manual, formateo ad-hoc).

## 6. Reseña como producto

La reseña vive en `prods/reseñas/{slug}/reseña.md` y sirve dos audiencias: lectura humana (catálogo publicable) y consumo interno del workflow.

### 6.1 Estructura

Orden fijo: humano primero, bloque IA al final claramente delimitado.

```markdown
# {Título}

## Ficha bibliográfica
Título, autor(es), editor, año, edición, idioma original.

## De qué trata
Síntesis accesible (1-2 párrafos).

## Contexto histórico y propósito
Cuándo y para qué se escribió.

## Relevancia para el lector SUD
Peso eclesial, uso en currículo, por qué leerlo.

## Estructura de la obra
Secciones o capítulos principales.

## Valoración
Fortalezas, limitaciones, a quién recomendarlo.

## Fuentes citadas
Bibliografía en FCD.

<!-- ===== METADATA IA — NO PUBLICAR ===== -->

## Metadata de ingestión

### Clasificación
- Categoría corpus: ...
- Paths destino: ...

### Autoridad propuesta
- authority: ...
- rigor: ...
- official: ...
- Justificación: ...

### KG pre-seed
- Entidades: ...
- Relaciones curadas: ...

### Fuente de descarga
- URL: ...
- Skill: ...
- SHA del crudo: ...

<!-- ===== FIN METADATA IA ===== -->
```

Los marcadores HTML-comment permiten que un script de publicación elimine el bloque IA con una regex simple antes de exportar el catálogo.

### 6.2 Reseña como gate

El paso 4 no se da por cerrado hasta que la reseña esté **completa** (todas las secciones humanas + bloque IA). El gate lo verifica el reconcile: una reseña con secciones vacías o faltantes queda `en_progreso`.

## 7. Gates bloqueantes

Solo dos:

1. **Reseña completa** antes de autoridad (§4.5), KG pre-seed (§4.6) y formato (§4.7).
2. **Commit + sync** antes de indexar (§4.9).

Todo lo demás es orden recomendado. La descarga (§4.2) es especialmente flexible: puede ocurrir antes, durante o incluso después del descubrimiento si el crudo llegó por otro canal.

## 8. Ganancias esperadas

### 8.1 Espacio en disco (medido 2026-04-20, Ubuntu-20.04 WSL)

| Componente | Tamaño | Se libera al |
|---|---|---|
| `alejandria.db` (SQLite activa) | 3.5 GB | retirar SQLite (§3.4) |
| `alejandria.db.gz` (backup comprimida) | 1.4 GB | retirar SQLite (§3.4) |
| Carpetas `sqlite/backups/` y `sqlite/neo4j_backups/` (backups rotativos) | ~6.1 GB | retirar ambos (§3.3 + §3.4) |
| Volumen Docker `docker_alejandria-neo4j` | 5.2 GB | retirar Neo4j (§3.3) |
| **Total recuperable** | **~16.2 GB** | fin de §3 |

Notas:

- El volumen Docker de Neo4j queda huérfano al quitar el servicio del compose; se libera con `docker volume rm docker_alejandria-neo4j`. Revisar también volúmenes auxiliares (logs, import, plugins) si existen.
- Lado Windows: `C:/own/alejandria/data/sqlite/` está vacío — la limpieza ocurre en la partición de Ubuntu-20.04 WSL.
- Los backups rotativos dejan de tener sentido al existir un único source of truth con `pg_dump` diario sobre IONOS.

### 8.2 Runtime

- Un contenedor menos (`neo4j`) — libera RAM (heap JVM típico 1-2 GB) y CPU ociosa.
- Un volumen Docker menos.
- Un modelo de datos menos que mantener y documentar.

## 9. Retiro de endpoints y referencias obsoletas

Tras completar §3, retirar o reescribir:

- `POST /backup/sqlite`, `GET /backup/sqlite`, `POST /backup/sqlite/restore`
- `POST /backup/neo4j`, `GET /backup/neo4j`, `POST /backup/neo4j/restore`
- `POST /index/rebuild-vectors` (sentido si se reescribe sobre Postgres; evaluar)
- Bind-mounts de `data/sqlite/` y volúmenes de Neo4j en `docker-compose`
- Sección "Backup & Disaster Recovery" de `CLAUDE.md` — reescribir sobre Postgres
- Flag `ALEJANDRIA_STORAGE_BACKEND` — eliminar tras cutover

## 10. Actualización de memorias y skills

**Memorias a reemplazar o retirar:**

- `procedure_corpus_addition.md` — reemplazar por puntero a este documento.
- Memorias relacionadas con SQLite/Neo4j como source of truth — revisar y ajustar.
- `project_postgres_source_of_truth.md` — actualizar al estado post-migración.

**Skills a revisar:**

- `gospelink`, `byu-studies`, `rsc-byu`, `gutenberg`, `book-discovery` — adaptar para escribir en el backlog correspondiente en lugar de ejecutar el workflow completo.
- `deploy`, `status` — verificar que no asuman SQLite/Neo4j.

**Nuevos artefactos a crear:**

- `scripts/reconcile-backlogs.py`
- `backlogs/schemas/*.schema.json`
- `backlogs/README.md`
- Hook de pre-commit para validación de schemas.

---

## Apéndice A: Decisiones tomadas durante el diseño

- **Descarga como paso propio** — antes estaba implícita dentro de "formato".
- **Reseña en `prods/reseñas/{slug}/`** — dos propósitos (catálogo humano + metadata ingestión), separados por marcadores HTML-comment.
- **JSON sobre YAML o SQLite** para backlogs — diffeable, sin dependencias, tipos inequívocos.
- **Validación en pre-commit** — no en reconcile.
- **Postgres como único store** — retiro completo de SQLite y Neo4j, no coexistencia.
- **Secuencia de migración ordenada** — cutover write → port read KG → retirar Neo4j → retirar SQLite. No paralelizable.
- **Congelación de ingestión** — durante toda §3, sin excepciones.
