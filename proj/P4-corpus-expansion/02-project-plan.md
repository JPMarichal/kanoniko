# P4 — Corpus Expansion — Project Plan

## Fases

Las fases están ordenadas por **costo/beneficio**: primero lo que tiene script
listo (costo cero, beneficio inmediato), luego lo que requiere preparación.
Cada fase es independiente y ejecutable sin esperar la siguiente.

---

### Fase 1 — Ejecutar scripts preparados

**Costo:** bajo — los scripts ya existen, solo ejecutar.
**Beneficio:** inmediato — ~220 documentos nuevos, JTC enriquece KG masivamente.

| Material | Script | Comando |
|----------|--------|---------|
| Jesus the Christ (EN+ES) | `download_jesus_the_christ.py` | `python scripts/download_jesus_the_christ.py` |
| Christmas Study Plan 2024 (EN+ES) | `download_christmas_study_plan.py` | `python scripts/download_christmas_study_plan.py --year 2024` |
| Easter Study Plan (EN+ES) | `download_easter_study_plan.py` | `python scripts/download_easter_study_plan.py` |

Todos se ejecutan con `REQUESTS_CA_BUNDLE=docker/ca-certificates.crt` prefijado.
Después de cada descarga: `POST /index/ingest` (incremental).

---

### Fase 2 — Cerrar gaps de ayudas de estudio ES

**Costo:** muy bajo — scripts ya existen (`scrape_study_aids.py`).
**Beneficio:** paridad EN/ES en el conjunto de referencia.

| Material | Comando |
|----------|---------|
| Bible Dictionary ES | `python scripts/scrape_study_aids.py --aid bd --lang spa` |
| Topical Guide ES | `python scripts/scrape_study_aids.py --aid tg --lang spa` |

---

### Fase 3 — Escrituras ES completas

**Costo:** medio — script existe (`scrape_scriptures.py`) pero es lento (~3h).
**Beneficio:** alto — cierra la mayor asimetría del corpus.

Opción A (recomendada): usar el dump MySQL disponible (42,699 versículos ES
ya validados del sitio oficial). Ver memoria `mysql_dump_versiculos.md`.

Opción B: ejecutar `scrape_scriptures.py --lang spa` contra el sitio.

Libros pendientes en ES: AT, NT, D&C, PGP.

---

### Fase 4 — Libros clásicos Talmage

**Costo:** bajo — preparar 2 scripts (patrón idéntico a JTC).
**Beneficio:** alto — completa la trilogía Talmage + enriquece KG doctrinal.

| Material | Pasos |
|----------|-------|
| The Articles of Faith | Investigar slugs → adaptar `download_jesus_the_christ.py` |
| The Great Apostasy | Ídem — ~8 capítulos |

Ambos son manuales en `/study/manual/*` con API v3 confirmado.

---

### Fase 5 — Manuales doctrinales esenciales

**Costo:** medio — preparar 3 scripts (patrón PMG, slugs descriptivos).
**Beneficio:** muy alto — cubren plan de salvación, vocabulario doctrinal oficial.

| Material | Notas |
|----------|-------|
| Gospel Principles | 47 capítulos, slugs descriptivos — necesita `fetch_toc()` robusto |
| True to the Faith | ~180 entradas alfa — adaptar `scrape_study_aids.py` |
| Teachings of Presidents — Joseph Smith | ~20 capítulos, slug: `teachings-joseph-smith` |

---

### Fase 6 — Come Follow Me (ciclo actual)

**Costo:** medio-alto — URL patterns por año/versión, ~800 docs total.
**Beneficio:** muy alto — exégesis oficial de todos los standard works.

Prioridad dentro de CFM:
1. Individuals & Families — LdM 2024 (año más reciente disponible)
2. Individuals & Families — NT 2023
3. Individuals & Families — D&C 2021
4. Individuals & Families — AT 2022

---

### Fase 7 — Serie Teachings of Presidents (completa)

**Costo:** alto — ~22 manuales × mapeo de slugs.
**Beneficio:** alto — voz directa de cada profeta por tema.

Estrategia: preparar un script genérico `download_teachings_president.py`
con `--prophet <slug>` y una lista de todos los slugs conocidos.
Ejecutar prophet por prophet para validar antes de batch completo.

---

### Fase 8 — Discourses of Brigham Young

**Costo:** medio — fuente externa (Project Gutenberg / archive.org).
**Beneficio:** medio-alto — enriquece perfil KG de BY, fuente histórica primaria.

Requiere nuevo script de descarga (no API de la Iglesia).
Autoridad: 35 — incluir nota de contexto histórico en meta.json.

---

## Milestones

| Milestone | Fases | Documentos nuevos |
|-----------|-------|-------------------|
| M1 — Scripts ejecutados | 1 | ~220 |
| M2 — Paridad ES study-aids | 2 | ~900 |
| M3 — Escrituras ES completas | 3 | ~4,500 versículos |
| M4 — Trilogía Talmage | 1+4 | ~280 |
| M5 — Manuales esenciales | 5 | ~500 |
| M6 — CFM ciclo actual | 6 | ~800 |
| M7 — Teachings completo | 7 | ~880 |
| M8 — BY histórico | 8 | ~200 |

**Total estimado al cierre de P4:** +8,000–9,000 documentos nuevos.

---

## Riesgos

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Slugs de CFM varían por año | Medio | Verificar TOC con `--dry-run` antes de descargar |
| Teachings of Presidents: slugs inconsistentes | Medio | Mapeo manual desde el sitio antes de scripting |
| Escrituras ES: sitio cambia HTML | Bajo | Fallback al dump MySQL |
| Reindexado KG tarda 3h por batch grande | Alto | Ingesta incremental por fase; no batch único |
| JTC genera muchas entidades nuevas en KG | Medio | Revisar gazetteers antes de ingestar |

---

## Criterios de éxito

1. Corpus crece de ~10k a ~18k documentos
2. Jesus the Christ + trilogía Talmage indexados y aparecen en búsquedas
3. Escrituras ES completas — paridad con EN en standard works
4. Gospel Principles disponible para preguntas sobre plan de salvación
5. Come Follow Me actual = exégesis semanal searchable
6. Perfiles KG de profetas enriquecidos con Teachings series
