# Análisis de mejora — Alejandría 2026

> **Tipo:** documento de referencia (el *por qué*). El *qué / cuándo / estado* vive en
> [improvement-program-2026.md](improvement-program-2026.md).
> **Fecha:** 2026-09-09
> **Método:** revisión de `docs/`, `docs/project-memory/`, `proj/` + investigación web del estado
> del arte 2026 (fuentes al pie).

---

## 1. Contexto y alcance

Alejandría es un motor de conocimiento bilingüe (ES/EN) para estudio de escrituras SUD, con tres
modos de búsqueda (FTS, semántica, KG), grafo de conocimiento, perfiles de entidad y Q&A por RAG.
Cinco fases completas. Postgres + pgvector es el store único (Neo4j y SQLite retirados; migración
completa y validada con 31/31 golden queries — A0). Paquete plano `src/alejandria` en `main`; el
split a monorepo de 4 paquetes (`workspace-migration`) fue un intento abandonado.

Desde su creación aparecieron tecnologías y hallazgos que atacan directamente sus limitaciones
conocidas. Este documento hace un SWOT, mapea cada dolor a una tecnología concreta, evalúa el
roadmap vigente y sitúa el spike SophiaLDS y la herramienta Graphify.

Dolores declarados: indexación, mantenimiento, velocidad de ingesta, ruido/calidad del grafo,
calidad de respuestas RAG, ahorro de tokens, aprovechamiento de GPU, contenedores, corpus.

---

## 2. Foto del sistema hoy

| Dimensión | Estado |
|---|---|
| **Corpus** | ~56K docs / ~309K chunks / ~217K vectores. Escrituras bilingües (EN+ES completas tras P2), ~6,900 discursos de conferencia, biografías, manuales, *General Handbook* |
| **Embeddings** | `paraphrase-multilingual-MiniLM-L12-v2` (384 dim, 2019), in-process vía `sentence-transformers` |
| **Búsqueda** | FTS (BM25) + semántica (pgvector) + KG, fusionadas con RRF propio (`search/hybrid.py`) |
| **KG** | ~732K entidades / ~18.5M relaciones tras limpieza R0/R7. Extracción: gazetteer regex (~2,400 términos) + spaCy `sm` + co-ocurrencia |
| **RAG** | 4 llamadas LLM/pregunta: expansión, extracción de entidades, **reranking por LLM**, respuesta. Tiers Gemini Flash / Haiku |
| **Ingesta** | 3 fases batch. GPU RTX PRO 500 Blackwell 6 GB. Fase 2 (embeddings) trivial en GPU (~327 chunks/s); **Fases 1 y 3 dominan** (~408 chunks/min c/u); Fase 3 = spaCy NER por chunk, CPU-bound |
| **Storage** | **Postgres 16 + pgvector en IONOS VPS** — store único autoritativo. Neo4j y SQLite **retirados** (confirmado A0). Write-path portado; `PostgresGraphClient` completo |
| **Infra** | Docker Compose (`api`) + segundo engine Docker nativo en WSL Ubuntu-20.04 para GPU. Máquina 32 GB con presión de RAM. SSH tunnel a IONOS en el camino crítico |
| **Código** | Paquete plano `src/alejandria` en `main` (api, chat, embeddings, ingestion, knowledge, search, storage). `tests/` incl. `tests/parity/`. El branch `workspace-migration` (split a 4 paquetes) está **abandonado** |

---

## 3. SWOT

### Fortalezas

- **Ontología de dominio madura**: 7 tipos de nodo + 67 relaciones tipadas en 12 categorías +
  niveles de confianza (`curated` > `metadata` > `llm_high` > `llm_low` > `ner` > `co_occurrence`).
  Es el activo más difícil de reconstruir.
- **Gazetteers curados bilingües**: 2,175 personas bíblicas con nombres EN/ES
  (Theographic/BibleData/Hitchcock), más lugares/conceptos/objetos. Alta precisión sobre canónicos.
- **Pipeline RAG sofisticado**: clasificación de complejidad heurística sin costo LLM, routing por
  tiers, expansión de query, KG-boosted retrieval (tag `[KG: entity]` para el reranker), passages
  diversos por volumen, perfiles de entidad bilingües con staleness tracking, cross-references de
  footnotes (97,961 pares) integradas al RAG.
- **Higiene de KG ya diagnosticada y parcialmente ejecutada**: R0/R1/R3/R7 aplicados
  (−80K nodos basura, −33M relaciones de co-ocurrencia, DB 11 GB → 5.8 GB), gold standard n=300,
  180 tests de filtros.
- **Store único bien razonado**: `vector-db-options.md` documenta con triggers cuantitativos por
  qué pgvector; los JOINs `chunks`↔`entities`↔`relations` son imposibles en un vector store dedicado.
- **Multi-interfaz** (REST + MCP + CLI) y multi-proveedor LLM con fallback chain.
- **Higiene operativa**: SHA-256 incremental, backup pre-index, `pg_dump` cron, benchmarks
  fechados, memoria de proyecto en git, GPU Blackwell (cu128, sm_120) funcional.

### Debilidades

- **Modelo de embeddings obsoleto**: MiniLM-L12-v2 (384 dim) está ~3 generaciones atrás de
  BGE-M3 / Granite-R2 / E5-large. Techo de recall bajo; 384 dim limita discriminación en un corpus
  con mucha similitud léxica (escrituras).
- **Ruido estructural del KG altísimo**: estimación calibrada del propio diagnóstico ~55–80% por
  tipo (`object` ~81%, `person` ~59%, `period` ~60%). Causas: spaCy `sm` propaga labels mal
  (`_SPACY_LABEL_MAP` traduce ciego `DATE→period`, `ORG→people`), bug de filtro gazetteer
  **por-chunk** (no global), sin validación de tipo. R10 (type-correctness, ~400–500K entidades
  potencialmente mal tipadas) pendiente.
- **Extracción de relaciones débil**: co-ocurrencia ya eliminada (R7) ⇒ el grafo quedó **rico en
  esquema, pobre en aristas reales**. Las 1,966 familiares son todas deterministas/curadas. No hay
  extracción semántica real de los 67 tipos que la ontología define.
- **Fase 3 de ingesta CPU-bound**: spaCy corre en cada chunk; no usa GPU. Full reindex ~7h en CPU.
- **RAG caro en tokens y round-trips**: 4 llamadas LLM secuenciales. El reranking se hace con LLM
  (call #3) en vez de un cross-encoder — más lento, más caro y peor.
- **Deuda de documentación de arquitectura** (confirmado por A0 — ver
  `proj/P0-postgres-cutover/00-state-audit.md`). El código en `main` corre un solo store Postgres y
  la migración está **validada (31/31 golden queries commiteadas)**, pero 7 docs
  (`architecture.md`, `stack.md`, `knowledge-graph.md`, `search-*.md`, `docs/README.md`) +
  algunas descripciones en `api/schemas.py` aún presentan Neo4j / Qdrant / SQLite como el stack
  vigente. `postgres-migration-status.md` lee "en progreso" cuando está cerrado. Es lectura
  engañosa para cualquiera (humano o agente). **P0 quedó reducido a este doc-sync (~1 día).**
- **Rastro del intento abandonado**: el branch `workspace-migration` (split a 4 paquetes
  `uv`/`hatch`) quedó a medias y sin uso; en `main` hay un `packages/` sin trackear como resaca.
  Peso muerto a limpiar (P0·A3), no un problema activo.
- **Superficie de mantenimiento para un solo dev**: 2 engines Docker, VPS IONOS con ops propias,
  stack GPU, bundles de certificados por máquina.
- **SSH tunnel a IONOS en el camino crítico**: latencia añadida y punto de fallo para dev/ingesta.
- **`ner_candidates`**: 623K candidatos, 0 promociones históricas, 207 MB. Mecanismo muerto sin decisión (R6).

### Oportunidades (tecnología/hallazgos posteriores a la creación)

- **Embeddings 2026**: **BGE-M3** (denso + sparse + multi-vector en un modelo, 1024 dim, 8192 ctx,
  MIT), **Granite-Embedding-multilingual-R2**, **EmbeddingGemma-300M**. BGE-M3 da **hybrid nativo**
  y podría retirar el RRF+FTS custom. Re-embeder 217K chunks ≈ 10 min en la GPU actual.
- **Serving de embeddings**: **HF Text-Embeddings-Inference (TEI) v1.9** — servidor Rust con
  dynamic batching, Flash-Attention, soporte Blackwell nativo. Saca el modelo del proceso Python.
- **Rerankers cross-encoder multilingües**: `bge-reranker-v2-m3`, `jina-reranker-v2-base-multilingual`,
  `Qwen3-Reranker`. **+10–25% de precisión** sobre hybrid y **elimina la llamada LLM #3**.
- **IE schema-driven que no existía al empezar**: **GLiNER2 / GLiNER-Relex / GLiREL** — NER +
  relation extraction zero-shot, `<500M` params, se declaran los 67 tipos de relación como
  esquema en inferencia. Corre en GPU en batch. Reemplaza spaCy `sm` y la co-ocurrencia con algo
  que **sí produce relaciones tipadas** sin costo LLM por chunk.
- **Paradigma KG-para-retrieval**: **HippoRAG 2** (2025) usa el KG para *guiar* la recuperación
  (Personalized PageRank sobre grafo de pasajes+entidades), no para expandir el corpus.
  Menos ruido LLM, mejor multi-hop (MuSiQue F1 44.8→51.9; 2Wiki Recall@5 76→90), **~10× menos
  tokens de indexado** que GraphRAG/LightRAG, sin degradar QA simple.
- **Contextual Retrieval (Anthropic) / Late Chunking (Jina)**: prepend de contexto por chunk antes
  de embeder. −49% a −67% en fallos de recuperación top-20. Late chunking no necesita LLM y ayuda
  a cross-references (clave para los tres Layers de paralelismos del `vision_and_roadmap.md`).
- **Ahorro de tokens ya maduro**: prompt caching (−90% en lectura cacheada) + Batch API (−50%) ⇒
  el trabajo offline (perfiles, extracción KG, backfills, contextual retrieval) baja ~95%.
- **Entity resolution 2026**: **EDC (Extract-Define-Canonicalize)** y clustering de embeddings +
  LLM-judge para merge — ataca R10 y duplicados canónicos a escala.
- **pgvector 0.8** (ya instalado): `halfvec` (mitad de storage), iterative index scan — refuerza
  la apuesta de store único aunque se suba a 1024 dim.
- **Corpus**: la content API oficial de churchofjesuschrist.org trae footnotes = miles de
  cross-references que el KG absorbe directo (el `vision_and_roadmap.md` lo identifica como el
  atajo para Layer 3).

### Amenazas

- **Bus factor**: un mantenedor con superficie amplia (2 engines Docker + VPS IONOS + GPU stack +
  intentos de refactor abandonados). Riesgo mayor que cualquier riesgo técnico puntual.
- **Docs que mienten sobre el stack**: mientras `architecture.md`/`stack.md`/etc. describan
  Neo4j/Qdrant/SQLite, cualquier lector (o agente) parte de un modelo mental falso. Barato de
  arreglar (P0), caro de dejar.
- **spaCy `sm` está de facto sin mantenimiento** para dominio arcaico/teológico — techo de calidad
  del KG si no se cambia el extractor.
- **Fragilidad de dependencias externas**: DeepSeek bloqueado por firewall corporativo, certs por
  máquina, free tiers que cambian límites.
- **Churn de frameworks**: atarse a un framework GraphRAG que puede quedar sin mantenimiento.
  Adoptar *modelos y técnicas*, no frameworks.
- **RAM de IONOS VPS M**: si el corpus crece 5×, `shared_buffers` aprieta; el plan es upgrade a
  VPS L (€10–15/mo) — deja de ser "costo cero".
- **Licenciamiento del corpus**: ToS de contenido de la Iglesia para redistribución si el chat
  client se hace público.

---

## 4. Mapeo dolor → causa raíz → tecnología precisa

| Dolor | Causa raíz | Tecnología / método concreto | Impacto esperado |
|---|---|---|---|
| **Velocidad de ingesta / indexación** | Fase 3 (spaCy NER por chunk) CPU-bound; Fase 1 secuencial | Reemplazar spaCy `sm` por **GLiNER2/GLiREL en GPU batch**; paralelizar Fase 1 (parse+FTS) con workers | Fase 3 pasa de CPU a GPU; full reindex ~7h → ~1h |
| **Aprovechamiento de GPU** | GPU solo se usa en Fase 2 (~5 s); NER y rerank no la tocan | **TEI** para embeddings + reranker residentes (~2 GB de 6); **GLiNER** en GPU para extracción. LLM se queda en la nube (6 GB no da para embeddings+reranker+7B) | GPU usada en las 3 fases de ingesta y en query-time rerank |
| **Calidad / ruido del grafo** | spaCy label-map ciego, filtro gazetteer por-chunk, sin validación de tipo, sin extracción de relaciones real | (1) **GLiREL con esquema de los 67 tipos** como extractor primario; (2) gazetteer como pase de precisión; (3) **LLM batch schema-bound + prompt caching** solo para top-K entidades / capítulos ambiguos; (4) **EDC / cluster+LLM-judge** para R10 y merge de duplicados; (5) arreglar el bug de filtro global (R1) | Ruido ~55–80% → objetivo <15%; grafo con aristas tipadas reales |
| **Calidad de respuestas RAG** | Retrieval denso débil (MiniLM 384d), reranking por LLM, KG como fuente de ruido | (1) **BGE-M3** (denso+sparse) sube recall y da hybrid nativo; (2) **cross-encoder reranker** (bge-reranker-v2-m3) reemplaza la llamada LLM; (3) **HippoRAG-2-style PPR** para multi-hop; (4) **Contextual Retrieval** en index-time | +10–25% precisión; +multi-hop; −fallos top-20 hasta −67% |
| **Ahorro de tokens** | 4 llamadas LLM secuenciales/pregunta; trabajo offline sin caching/batch | (1) fusionar expansión+extracción en 1 llamada; (2) reranker cross-encoder elimina otra → **2 llamadas/pregunta**; (3) **prompt caching** en system prompt; (4) **Batch API** para perfiles/extracción/backfills | ~50% menos tokens en query-path; ~95% menos en offline |
| **Contenedores** | 2 engines Docker (Rancher + nativo Ubuntu GPU); compose ya reducido a `api` | (1) unificar en un solo engine Docker; (2) **TEI como servicio** en compose; (3) Postgres local para dev en vez de tunnel siempre; (4) contenedor de reranker | 1 engine, dev sin SSH tunnel |
| **Mantenimiento** | Docs de arquitectura desincronizados, mecanismos muertos (`ner_candidates`), rastro del refactor abandonado | (1) doc-sync (P0·A1); (2) endurecer el hook `pre-commit-sync.sh`; (3) decidir R6; (4) borrar `packages/` sin trackear + rama `workspace-migration` (P0·A3) | Menos superficie, docs confiables |
| **Corpus** | ES ya completo (P2); sin ETL templates activos; Layer 3 sin habilitar | (1) reactivar **P3 ETL templates** (está `Deferred`); (2) **P4 corpus expansion** (revistas, manuales, comentarios); (3) **Church content API** para footnotes → cross-references al KG; (4) **docling/MarkItDown** para PDF | Corpus vivo; Layer 3 de paralelismos habilitado |

---

## 5. Qué rescatar del spike SophiaLDS

SophiaLDS (`D:\myapps\sophialds`) es un spike válido como validación de 3 ideas, **no** como reemplazo:

1. **Retrieval dual-level (low/high-level keywords)** de LightRAG — útil como una estrategia más
   detrás del API; o adoptar directamente HippoRAG 2, mejor en el mismo eje.
2. **Actualización incremental por caché de extracción** — cachear resultados de extracción por
   hash de chunk en la Fase 3 de ingesta.
3. **Podman con GPU passthrough en WSL** — ruta daemonless si se unifican engines.

**Qué NO copiar**: volver a Neo4j+Qdrant (ya retirados con razón), extracción LLM genérica sin
ontología, y la premisa "free tier" (20 req/min, 50–1000 req/día — inviable a 309K chunks).

---

## 6. Graphify

Hay dos herramientas homónimas:

- **Graphify (Graphify-Labs, YC S26)** — convierte un *codebase* + docs + SQL + configs + PDFs en un
  knowledge graph consultable. Parsing AST determinista local (tree-sitter), sin vector store, cada
  arista etiquetada `EXTRACTED / INFERRED / AMBIGUOUS`. Se usa como skill `/graphify` en Claude Code
  / Cursor / etc.
  **Encaje en Alejandría: herramienta de desarrollo/mantenimiento, no de arquitectura ni de corpus.**
  Útil para navegar `src/alejandria`, detectar código muerto (`ner_candidates.promote/dismiss` con
  0 usos, docstrings stale, el `packages/` sin trackear) y ver qué depende de qué antes de tocar el
  extractor (P12) o limpiar la resaca del refactor abandonado. Local y determinista ⇒ compatible
  con la postura de privacidad (hay `.env` y credenciales sensibles en el árbol). **No** es
  componente runtime ni sustituye la extracción de KG del corpus teológico. Uso sugerido: puntual,
  durante **P0** (limpieza) y **Fase C / P12** (mapa de dependencias del pipeline de ingesta).
- **graphify (kbastani) / GraphAware `neo4j-nlp`** — plugins unmanaged de Neo4j 3.x, Stanford/OpenNLP,
  sin mantenimiento y acoplados a Neo4j (que Alejandría retira). **Sin lugar.**

---

## 7. Evaluación del roadmap

### Salud por eje

- **Cadena de corpus P1→P2→P3→P4 (structure → refresh → ETL → expansion): sana.** Respeta
  dependencias, coincide con `vision_and_roadmap.md`. Se mantiene.
- **El roadmap es feature-céntrico, no health-céntrico.** No tiene workstream para: cierre de la
  migración, modernización de retrieval, ni higiene de KG recurrente.

### Incongruencias / desactualización

1. **El roadmap no refleja el cierre de la migración.** La migración a Postgres está **hecha y
   validada** (A0: 31/31 golden queries), pero 7 docs de arquitectura + `postgres-migration-status.md`
   aún la presentan como en curso / describen Neo4j-Qdrant-SQLite. → **Nuevo P0** = doc-sync + limpieza
   de la resaca del intento abandonado `workspace-migration` (~1 día).
2. **P6 "Advanced Relations" dice "move beyond co-occurrence"** pero la co-ocurrencia ya se
   eliminó (R7). El problema real hoy es que el grafo quedó **sin aristas tipadas reales**, y está
   enterrado en prioridad "Medium". → Elevar la extracción de relaciones a proyecto propio
   cercano (**nuevo P11/P12**), reformulado sobre **GLiREL/GLiNER2 + LLM batch schema-bound**.
3. **Retrieval se da por "hecho"** (Fases 1–2 tachadas) pero está datado: MiniLM 384d, reranking
   por LLM, serving in-process. Nada de esto está en el roadmap. → **Nuevo proyecto de
   modernización de retrieval.**
4. **P9 "Fine-Tuning"** mal priorizado para 2026: el lever es mejor modelo base + reranker +
   contextual retrieval, no fine-tunear un MiniLM. → Diferir / reencuadrar dentro de la
   modernización de retrieval.
5. **Colisión de numeración P10**: `docs/roadmap.md` P10 = "Genealogías Escriturales";
   `proj/P10-handbook-kg-model/` = otra cosa. → Renumerar genealogías a **P13**.
6. **Higiene de KG (R10, entity resolution)** se autodescribe como "continua, cada N meses" pero no
   tiene hogar en el roadmap. → Añadir como **Work Item permanente (WI-3)**.
7. **P8 Synthesis / Discursos** es el producto que justifica el trabajo de corpus, pero está
   "Lower". El gating ("backend sólido primero") es correcto; falta nombrar el gate
   (→ modernización de retrieval + KG v2).
8. **HippoRAG-2-style retrieval** no está considerado. → Nota como opción que alimenta P5/P6.

### Prioridades que siguen siendo correctas

La secuencia de corpus, P1 como fundacional, P5 (UI) gated por backend, P7 disambiguation como
multiplicador de precisión.

### Roadmap propuesto

Ver la tabla viva y el plan por fases en
[improvement-program-2026.md](improvement-program-2026.md). Resumen de cambios:

| Cambio | Detalle |
|---|---|
| **+ P0** | Doc-sync de 7 docs de arquitectura + cierre de `postgres-migration-status.md` + limpieza (`packages/` sin trackear, rama abandonada). ~1 día. *(Migración Postgres hecha y validada 31/31 — A0.)* |
| **+ P11** | Retrieval modernization (BGE-M3 + TEI + cross-encoder + contextual/late chunking) |
| **+ P12** | KG extraction v2 (GLiREL/GLiNER2 schema-bound + gazetteer + LLM batch) — absorbe la parte "relaciones" de P6 |
| **+ WI-3** | KG hygiene standing (R10 type-correctness + entity resolution + R5 + decisión R6) |
| **~ P6** | Reenfocado a Layer 2/3 de paralelismos + feedback loop NER→gazetteer; la extracción de relaciones sale a P12 |
| **~ P9** | Deferred / absorbido por P11 |
| **~ P10→P13** | "Genealogías Escriturales" renumerado; `proj/P10` sigue siendo Handbook KG Model |
| **~ P3** | Reactivar (estaba `Deferred`) — habilita P4 y la expansión de corpus |

---

## 8. Shortlist priorizada (cost/benefit)

Detalle y seguimiento en [improvement-program-2026.md](improvement-program-2026.md).

**Ola 1 — desbloquear (alto ROI):**
1. Doc-sync de arquitectura + cierre de status docs + limpieza de la resaca del refactor abandonado — *Fase A / P0, ~1 día*.
2. Cambiar embeddings a BGE-M3 + servir con TEI — *Fase B / P11*.
3. Cross-encoder reranker (bge-reranker-v2-m3) y quitar la llamada LLM de reranking — *Fase B / P11*.

**Ola 2 — calidad del grafo:**
4. GLiREL/GLiNER2 con esquema de 67 relaciones; gazetteer como pase de precisión; fix filtro
   global — *Fase C / P12*.
5. Pase offline de entity resolution + type-correctness (R10) con EDC / cluster+judge en Batch API
   — *Fase D / WI-3*.

**Ola 3 — RAG y tokens:**
6. Contextual Retrieval en index-time (Batch API + prompt caching) — *Fase E*.
7. HippoRAG-2-style PPR para preguntas multi-hop/temáticas — *Fase E (spike)*.
8. Fusionar expansión+extracción → 2 llamadas LLM/pregunta — *Fase E*.

**Ola 4 — corpus e infra:**
9. Reactivar P3 ETL + Church content API; verificar cobertura ES — *Fase G*.
10. Unificar engines Docker; Postgres local para dev — *Fase F*.

---

## 9. Fuentes (investigación 2026)

- [The Best Open-Source Embedding Models in 2026 — BentoML](https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models)
- [8 Embedding Models Compared for Production RAG (2026)](https://tensoria.fr/en/blog/embedding-models-2026-guide)
- [Granite Embedding Multilingual R2 — arXiv](https://arxiv.org/pdf/2605.13521)
- [Top Reranking Models to Boost RAG Accuracy in 2026 — Redis](https://redis.io/blog/top-reranking-models-rag-accuracy/)
- [RAG Is Not Dead: Advanced Retrieval Patterns That Actually Work in 2026](https://dev.to/young_gao/rag-is-not-dead-advanced-retrieval-patterns-that-actually-work-in-2026-2gbo)
- [GLiNER2: Schema-Driven Information Extraction — arXiv](https://arxiv.org/pdf/2507.18546)
- [GLiNER-Relex: Joint NER and Relation Extraction — arXiv](https://arxiv.org/abs/2605.10108)
- [GLiREL: Generalist Zero-Shot Relation Extraction — ACL](https://aclanthology.org/2025.naacl-long.418.pdf)
- [HippoRAG 2 / From RAG to Memory — arXiv](https://arxiv.org/html/2502.14802v2)
- [GraphRAG vs HippoRAG vs PathRAG vs OG-RAG — Graph Praxis](https://medium.com/graph-praxis/graphrag-vs-hipporag-vs-pathrag-vs-og-rag-choosing-the-right-architecture-for-your-knowledge-graph-a4745e8b125f)
- [HKUDS/LightRAG (GitHub)](https://github.com/hkuds/lightrag)
- [Graph RAG in 2026: What Works in Production — paperclipped](https://www.paperclipped.de/en/blog/graph-rag-production/)
- [huggingface/text-embeddings-inference (GitHub)](https://github.com/huggingface/text-embeddings-inference)
- [Text Embeddings Inference Guide 2026](https://tools.zgba.com/tools/text-embeddings-inference)
- [Prompt Caching in 2026: Cut Your LLM API Costs by Up to 90%](https://devtoollab.com/blog/prompt-caching-guide)
- [Claude Cost Optimization 2026: Batch API + Prompt Caching](https://pecollective.com/tools/claude-pricing-guide/)
- [Advanced RAG Chunking Techniques in 2026: Late, Semantic, Parent-Child](https://futureagi.com/blog/advanced-chunking-techniques-for-rag/)
- [Best Chunking Strategies for RAG in 2026 — Firecrawl](https://www.firecrawl.dev/blog/best-chunking-strategies-rag)
- [Entity Resolution at Scale: Deduplication for KG Construction (Jan 2026)](https://medium.com/@shereshevsky/entity-resolution-at-scale-deduplication-strategies-for-knowledge-graph-construction-7499a60a97c3)
- [LLM-empowered knowledge graph construction: A survey — arXiv](https://arxiv.org/html/2510.20345v1)
- [Less is More: Denoising Knowledge Graphs for RAG — arXiv](https://arxiv.org/pdf/2510.14271)
- [Graphify — code knowledge graph for AI coding assistants](https://graphify.com/)
- [Graphify-Labs/graphify (GitHub)](https://github.com/Graphify-Labs/graphify)
