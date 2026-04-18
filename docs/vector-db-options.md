# Vector DB options for Alejandría — comparativa y decisión

> **Estado:** referencia. No es plan activo. Documenta el análisis hecho el 2026-04-18 tras preguntar "y si migramos a Pinecone / Weaviate".
>
> **Conclusión operativa:** mantener **pgvector sobre Postgres en IONOS** (stack actual). Este doc existe para tener un registro fechado de por qué, y para disparar reconsideración cuando alguno de los triggers del §6 se cumpla.

---

## 1. Por qué existe este doc

Pinecone, Weaviate, Qdrant y Milvus son las 4 alternativas de vector DB que se evalúan cada vez que un proyecto hace RAG a escala. Cada 6-12 meses vale la pena re-auditar la elección de stack contra los precios y features que evolucionan.

Para Alejandría, la elección hoy es:
- Storage unificado (chunks + embeddings + KG + FTS en Postgres)
- pgvector como capa de similaridad
- IONOS VPS como host (costo cero incremental)

Este doc compara esa elección contra las 4 alternativas y deja explícitos los **triggers** que nos harían reconsiderar.

---

## 2. Perfil de uso actual (2026-04-18)

| Dimensión | Valor |
|---|---:|
| Vectores | 217,370 |
| Dimensiones | 384 (paraphrase-multilingual-MiniLM-L12-v2) |
| Storage vectores + HNSW | ~750 MB |
| Queries semánticas/día (estimado) | 10-10,000 según intensidad de uso |
| Writes/mes en estado estable | ~1k-10k nuevos vectores |
| Latencia p95 observada (bench) | 2.4 ms |
| Latencia p95 observada (IONOS via SSH tunnel) | pendiente medir; estimada <50ms |
| Costo incremental actual | **$0** (VPS ya pagado) |
| Ops burden | VACUUM ocasional, HNSW rebuild en cleanups grandes; típicamente 0 |

Esto es **escala muy pequeña**. Cualquier vector DB del mercado la soporta sin despeinarse. La elección no es de capacidad sino de:
- Costo y complejidad operativa
- Ajuste arquitectónico al resto del stack
- Vendor lock-in / soberanía de datos
- Features que necesitamos vs las que pagaríamos sin usar

---

## 3. Matriz comparativa

Precios al 2026-04-18, verificados en las fuentes al pie.

| | **pgvector** (actual) | **Qdrant** | **Weaviate** | **Milvus/Zilliz** | **Pinecone** |
|---|---|---|---|---|---|
| **Naturaleza** | Extensión Postgres | DB vectorial dedicada | DB vectorial dedicada | DB vectorial dedicada | Servicio SaaS propietario |
| **Open source** | ✅ PostgreSQL License | ✅ Apache 2.0 | ✅ BSD-3 | ✅ Apache 2.0 | ❌ Closed source |
| **Self-hostable** | ✅ | ✅ Rust binary o Docker | ✅ Docker/k8s | ✅ Docker/k8s | ❌ |
| **Free tier managed** | n/a | 1 GB RAM + 4 GB disk **indefinido** | 14-day sandbox | 5 GB storage + 2.5M vCU/mes | 2 GB storage + 1M RU/mes |
| **Managed pago (mínimo)** | n/a | Pay-as-you-go (~$150-200/mo a 8 GB RAM / 2 vCPU) | Flex $45/mo PAYG | Zilliz Dedicated desde $99/mo | Standard $50/mo |
| **Lock-in** | Bajo | Bajo | Bajo | Bajo-medio (Zilliz si managed) | Alto |
| **Hybrid search BM25+vector** | Manual (RRF ya implementado) | Sparse vectors nativos | ✅ built-in | ✅ built-in | Paid feature |
| **Metadata filtering** | SQL WHERE nativo | ✅ | ✅ | ✅ | ✅ |
| **Query language** | SQL | REST/gRPC | GraphQL + REST | REST/gRPC SDK | REST/gRPC SDK |
| **JOIN con datos no-vector** | ✅ SQL trivial | ❌ | ❌ | ❌ | ❌ |
| **Escalabilidad probada** | Cientos de millones | Billions | Billions | **Billions** (fuerte en este terreno) | Billions |
| **Costo para Alejandría hoy** | **$0** | $0 (self-host) o free tier | $0 self-host o 14d sandbox | $0 free tier | $0 starter |
| **Barrera de migración** | n/a | Media (nueva API) | Media-alta (GraphQL) | Media | Media + lock-in |

---

## 4. Análisis por opción

### 4.1 Qdrant

**Qué es:** vector DB escrita en Rust, open source (Apache 2.0), con SDK Python maduro. Diseñada desde cero para vector search con índice HNSW.

**Pricing 2026:**
- Self-host: $0 (Apache 2.0)
- Cloud free tier: 1 GB RAM + 4 GB disk **indefinidamente** — única free tier real entre las 4 opciones que no expira.
- Cloud PAYG: ~$150-200/mo a 8 GB RAM / 2 vCPU (mid-range).

**Cuándo pagaría para Alejandría:**
- Si pgvector empieza a mostrar tensión de RAM en un VPS con más datos. Qdrant usa memoria eficientemente y puede persistir índices en disco con hot-load on demand.
- Si la API de REST/gRPC encaja mejor con un frontend JS que mezclar SQL en el backend.

**Por qué no hoy:**
- Splits storage (chunks/KG/FTS en Postgres, vectores en Qdrant) → dos network hops para hybrid search.
- Zero features que pgvector no ofrezca a escala 217k vectores.
- Sería mi **primera opción** si pgvector algún día no alcanza — ecosystem Python limpio y Apache 2.0.

**Relación histórica con el proyecto:** según `CLAUDE.md`, Qdrant fue la opción original de Fase 2 antes de consolidar todo en SQLite/Postgres. Volver a Qdrant sería un "regreso informado" si alguna vez el monolito Postgres se vuelve incómodo.

### 4.2 Weaviate

**Qué es:** vector DB open source (BSD-3) en Go. Fuertemente orientada a semantic search con módulos nativos para embeddings + hybrid search (BM25+vector) built-in. GraphQL como lenguaje de queries principal.

**Pricing 2026 (post-reestructuración Oct 2025):**
- Self-host: $0 (BSD-3).
- Sandbox: 14 días gratis (solo demo).
- Cloud Flex: **$45/mo mínimo**, PAYG.
- Cloud Plus: $280/mo (dedicated + SLA 99.9%).
- Cloud Premium: custom (BYOC data residency).

**Cuándo pagaría para Alejandría:**
- Si decidiéramos hacer Alejandría SaaS multi-tenant: Weaviate tiene multi-tenancy first-class, mejor que Qdrant o pgvector.
- Si quisiéramos hybrid BM25+vector **sin implementar RRF**. Pero `search/hybrid.py` ya resuelve esto con ~90 líneas de código.

**Por qué no hoy:**
- Mismo problema de split architecture que Qdrant.
- RAM baseline 2-4 GB cómodos; en el VPS actual con MariaDB comiendo ~3 GB, requeriría upgrade a VPS L.
- GraphQL añade curva de aprendizaje sin beneficio para un stack SQL-céntrico.

### 4.3 Milvus / Zilliz

**Qué es:** Milvus es una vector DB open source (Apache 2.0) diseñada para billion-scale. Zilliz es la empresa que la mantiene y ofrece Zilliz Cloud como versión gestionada.

**Pricing 2026:**
- Self-host Milvus: $0 (Apache 2.0).
- Zilliz Cloud free tier: 5 GB storage + 2.5M vCU/mes + 30 días de Serverless/Dedicated gratis + $100 de créditos iniciales.
- Zilliz Cloud Dedicated: desde $99/mo.
- Storage standardizado a $0.04/GB/mes en todas las clouds desde enero 2026.

**Cuándo pagaría para Alejandría:**
- Solo si llegáramos a **billions** de vectores. Milvus es el que más alto escala del grupo.
- Si requiriéramos índices avanzados (GPU-accelerated, DiskANN, específicos para embeddings muy grandes).

**Por qué no hoy:**
- Overkill masivo. Milvus pesa en ops — Kubernetes nativo, componentes distribuidos (rootcoord, querynode, datanode, indexnode, proxy). No hay forma amable de self-hostear en un VPS de 4 GB RAM.
- Same split architecture problem.
- La escala donde Milvus brilla (>100M vectores, miles de QPS) está a 50-100x de distancia de la realidad actual.

### 4.4 Pinecone

**Qué es:** servicio SaaS de vector DB propietario. Pionero en el espacio, primera DB vectorial realmente "managed-first". Sin opción self-host.

**Pricing 2026:**
- Starter (gratis): 2 GB storage + 1M RU/mes + 2M WU/mes. **Alejandría cabe en Starter.**
- Serverless PAYG: $0.33/GB/mes storage + $16/M RU + $4/M WU. ~$5-10/mo para escala Alejandría.
- Standard: $50/mo mínimo (multi-cloud, mejor SLA).
- Enterprise: $500/mo (SLA 99.95%, private networking).

**Cuándo pagaría para Alejandría:**
- Si quisiéramos externalizar **completamente** las ops de vector search y no nos importara el vendor lock-in.
- Si llegáramos a multi-región con usuarios globales y necesitáramos latencia baja worldwide.

**Por qué no hoy:**
- **Closed source** + SDK propietario + API propietaria = alto lock-in.
- Split architecture: embeddings en Pinecone, texto/metadata/KG en Postgres → 2 round trips por hybrid query.
- El free tier "cubre" pero está pensado para hook comercial — sin garantía de mantener esos límites.
- Data residency: embeddings del corpus de escrituras viviendo en servers de Pinecone (US-East por default).
- No hay ningún feature que Pinecone ofrezca y que necesites.

---

## 5. ¿Y si algún día el monolito Postgres no alcanza?

Orden de reconsideración, del más probable al menos:

1. **Upgrade de VPS** (IONOS VPS L con 8 GB RAM) — €10-15/mo, resuelve el 99% de los problemas de RAM con pgvector + HNSW. **Primer paso siempre.**
2. **Qdrant self-hosted** en el mismo VPS (si RAM alcanza) o VPS aparte — mantiene OSS, mantiene control. Mejor fit para "salir de pgvector sin rediseñar arquitectura".
3. **Weaviate self-hosted** — si además queremos multi-tenancy o hybrid BM25+vector nativo sin mantener nuestro propio RRF.
4. **Qdrant Cloud / Weaviate Cloud** — si queremos reducir ops sin perder OSS underlying.
5. **Zilliz Cloud (Milvus managed)** — solo si hay billion-scale + equipo de ops pequeño.
6. **Pinecone** — última opción, solo si vendor lock-in es aceptable a cambio de ops-zero y features específicas no disponibles OSS.

---

## 6. Triggers concretos para reconsiderar pgvector

Criterios cuantitativos — si alguno se cumple, re-abrir este doc:

| # | Trigger | Acción |
|---|---|---|
| T1 | p95 de `search_semantic` >500 ms sostenido 1 semana | Upgrade VPS L (más RAM) |
| T2 | HNSW index build >1h (actualmente 40s por 217k vectores) | Investigar halfvec / IVFFlat / upgrade VPS |
| T3 | Tabla `chunk_embeddings` >5 GB (actualmente 750 MB) | Re-evaluar: ¿upgrade VPS o mover a Qdrant? |
| T4 | >5M vectores totales | Benchmark Qdrant vs pgvector escalado |
| T5 | Multi-tenancy real (Alejandría como SaaS) | Weaviate con multi-tenancy first-class |
| T6 | Multi-región necesaria (usuarios en 2+ continentes con latencia <100 ms) | Pinecone o Weaviate Cloud regional |
| T7 | Ingesta lenta dominada por write de vectores (actualmente lo domina spaCy/LLM, no DB) | Qdrant tiene writes batched agresivos |

Ninguno de estos triggers se cumple hoy. T4 podría tardar años (el corpus agrega ~1-10k chunks/mes).

---

## 7. Decisión vigente

**Mantener pgvector sobre Postgres en IONOS.** Razones:

1. **Costo incremental $0.** Cualquier alternativa añade al menos $45/mo (Weaviate Flex) o complejidad de self-host + VPS L.
2. **JOINs relacionales** entre `chunks`, `chunk_embeddings`, `entities`, `relations` — imposibles con storage dedicado. `search/postgres_semantic.py` hace un JOIN single-query que en cualquier otra DB serían 2 round trips.
3. **Stack unificado** — un motor, un `pg_dump`, un backup cron. Cualquier split añade una segunda DB que respaldar, monitorear, upgradar.
4. **No hay dolor actual** que cualquier alternativa resolvería. Los problemas observables (RAM 512 MB para shared_buffers, latencia de SSH tunnel) son de infraestructura, no de motor de vectores.

La elección se revisita si algún trigger del §6 se cumple, **no antes**.

---

## 8. Cross-references

- [postgres-migration.md](postgres-migration.md) — plan general que resultó en pgvector.
- [benchmarks/postgres-migration/RESULTS.md](../benchmarks/postgres-migration/RESULTS.md) — números que respaldan "pgvector alcanza para Alejandría".
- [CLAUDE.md](../CLAUDE.md) — nota histórica: Fase 2 original usó Qdrant antes de consolidar en pgvector.
- [ionos-setup.md](ionos-setup.md) — infra actual donde corre pgvector.

---

## 9. Fuentes verificadas 2026-04-18

- [pgvector GitHub](https://github.com/pgvector/pgvector) — extensión y licencia.
- Qdrant: [pricing page](https://qdrant.tech/pricing/) + [cloud docs](https://qdrant.tech/cloud/).
- Weaviate: [pricing 2026](https://weaviate.io/pricing) + [cloud pricing update Oct 2025](https://weaviate.io/blog/weaviate-cloud-pricing-update).
- Milvus/Zilliz: [Zilliz pricing](https://zilliz.com/pricing) + [Oct 2025 update](https://zilliz.com/blog/zilliz-cloud-oct-2025-update).
- Pinecone: [pricing page](https://www.pinecone.io/pricing/estimate/) + [understanding cost](https://docs.pinecone.io/guides/manage-cost/understanding-cost).
