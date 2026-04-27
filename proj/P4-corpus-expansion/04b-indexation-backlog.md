# Corpus Expansion — Backlog de indexación

Material ya descargado al corpus (archivos en disco) que aún no ha pasado por el
pipeline de indexación (FTS + vectors + KG).

Para backlog de descarga → `04-backlog.md`.
Para inventario de lo ya indexado → `03-corpus-inventory.md`.
Para análisis detallado por material → `fase0/`.

> **Última reconciliación:** 2026-04-26 — cierre de ingesta incremental validado en sesión.
> Backlog de indexación descargado→ingestado: **0 pendientes**.

---

## 1. Pendientes de indexación

No hay materiales descargados pendientes de indexación al 2026-04-26.

### Cerrados en el closeout de ingesta

| Material | Archivos | Estado al 2026-04-26 |
|----------|----------|-----------------------|
| Teaching, No Greater Call (EN+ES) | 182 | Ingested |
| Interpreter Journal | 888 | Ingested |
| Journal of Discourses | 1,425 | Ingested |
| Teach Ye Diligently | 18 | Ingested |
| Missionary Guide 1988 | 18 | Ingested |
| Doctrines of Salvation | 60 | Ingested |

**Total pendiente:** 0 archivos.

### Closeout complementario

La sesión de cierre también dejó completados los perfiles de metadata:

| Métrica | Valor |
|--------|-------|
| `entity_profiles` | 24,133 |
| `metadata` | 24,133 |
| `profiled` | 0 |
| `stale` | 0 |

---

## 2. KG enrichment pendiente (material ya ingested)

Material indexado que tiene relaciones KG identificadas pero no pre-seeded.

| Material | Relaciones pendientes | Fase 0 |
|----------|----------------------|--------|
| Jesus the Christ | `TAUGHT` (Resurrection, Atonement, Law of Moses), `QUOTED_BY` (Isaiah→JC), `TYPE_OF` (High Priest) | `fase0/jesus-the-christ.md` |
| Preach My Gospel | `PREREQUISITE_FOR` cadena primeros principios (Faith→Repentance→Baptism→HG→Endure) | `fase0/preach-my-gospel.md` |

### Indexados sin pasada retroactiva de curación KG

Materiales ingested cuyo FTS y búsqueda semántica ya están operativos, pero que aún
merecen una pasada posterior de web research revisada + KG curado tipado:

| Material | Ingested | Fase 0 original | Notas |
|----------|----------|-----------------|-------|
| Missionary Guide 1988 | 2026-04-16 | `fase0/missionary-guide-1988.md` | Relaciones clave: `PREDECESSOR_OF` (→PMG), `COMPANION_TO` (1986 discussions) |
| Teach Ye Diligently | 2026-04-16 | `fase0/teach-ye-diligently.md` | Relaciones clave: `AUTHORED_BY` (Packer), `CITES` (Charted Course), cadena pedagógica CES |
| Teaching, No Greater Call (EN+ES) | 2026-04-16 | `fase0/teaching-no-greater-call.md` | Relaciones clave: `PREDECESSOR_OF` (→TITSW), continuidad CES |

> **Nota:** Esto ya no bloquea indexación. Es trabajo de curación posterior.

---

## 3. Trabajo pendiente no bloqueante

Ya no existe una cola de indexación descargado→ingestado. El trabajo pendiente pasó a
enriquecimiento, consolidación editorial o curación KG.

| Orden | Material | Seguimiento |
|-------|----------|-------------|
| 1 | Jesus the Christ | KG curado pendiente |
| 2 | Preach My Gospel | KG curado pendiente |
| 3 | Missionary Guide 1988 | pasada retroactiva de web research + KG pre-seed |
| 4 | Teach Ye Diligently | pasada retroactiva de web research + KG pre-seed |
| 5 | Teaching, No Greater Call | pasada retroactiva de web research + KG pre-seed |

---

## 4. Protocolo de indexación

### Workflow

```
descargado
  → Fase 0 (gate obligatorio)
      → Paso 1: Investigación editorial (web research)
      → Paso 2: Análisis de contenido + authority + valor KG
  → Pre-seed KG (relaciones identificadas en Fase 0)
  → Ejecutar pipeline incremental
  → Verificar con /corpus/status
  → Mover a 03-corpus-inventory.md
```

### Gate de Fase 0

La Fase 0 es obligatoria antes de indexar. Esto garantiza que:
- El modelo de authority está fundamentado en investigación editorial real
- Las relaciones KG están pre-seeded antes de que el pipeline las necesite
- Los riesgos de contenido están documentados
- La deduplicación con material existente está verificada

> **Excepción:** Material oficial de la Iglesia con authority conocida (escrituras,
> conferencia general, manuales correlacionados) puede tener Fase 0 simplificada.

### Estados

| Estado | Significado | Gate |
|--------|-------------|------|
| `descargado` | Archivos en disco, sin indexar | Commit hecho |
| `researched` | Fase 0 completa: authority y KG evaluados | Fase 0 pasos 1-2 aprobados |
| `pre-seeded` | Relaciones KG cargadas al grafo | KG pre-seed ejecutado |
| `ingested` | Pipeline completo (FTS + vectors + KG) | Pipeline ejecutado, `/corpus/status` verificado |
| `blocked` | Impedimento técnico (formato, merge, etc.) | — |