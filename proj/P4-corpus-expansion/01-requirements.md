# P4 — Corpus Expansion — Requirements

## Estado del corpus al inicio de P4

| Categoría | EN | ES | Gaps |
|-----------|----|----|------|
| Escrituras | ✅ completo | ⚠️ solo BOM | AT/NT/D&C/PGP ES |
| Conferencia General | ✅ 1971–2025 | ✅ ~1990–2025 | — |
| General Handbook | ✅ | ✅ | — |
| Missionary Standards | ✅ | ✅ | — |
| Proclamaciones | ✅ | ✅ | — |
| Bible Dictionary | ✅ | ❌ | ES pendiente |
| Guide to Scriptures | ✅ | ✅ | — |
| Topical Guide | ✅ | ❌ | ES pendiente |
| JST Appendix | ✅ | ✅ | — |
| Preach My Gospel 2023 | ✅ | ✅ | — |
| Jesus the Christ | 🟡 prepared | 🟡 prepared | ejecutar scripts |
| Christmas Study Plan | 🟡 prepared | 🟡 prepared | ejecutar scripts |
| Easter Study Plan | 🟡 prepared | 🟡 prepared | ejecutar scripts |

## Problema

El corpus cubre bien la conferencia y los documentos canónicos, pero carece
de los materiales doctrinales de estudio que los miembros usan cotidianamente:
manuales de clase, libros clásicos de Autoridades Generales, planes de estudio
estacionales, y la serie de enseñanzas de profetas. Esta ausencia limita la
capacidad del sistema para responder preguntas doctrinales prácticas y para
enriquecer los perfiles KG de personas y conceptos.

## Requisitos funcionales

### FR-1: Completar gaps de estudio bíblico
- Bible Dictionary ES
- Topical Guide ES

### FR-2: Completar escrituras ES
- AT, NT, D&C, PGP en español
- Fuente: sitio oficial (scrape_scriptures.py) o dump MySQL disponible

### FR-3: Ejecutar scripts preparados
- Jesus the Christ (EN+ES)
- Christmas Study Plan (EN+ES, --year 2024)
- Easter Study Plan (EN+ES)

### FR-4: Libros clásicos de Autoridades Generales
- The Articles of Faith — Talmage (script a preparar)
- The Great Apostasy — Talmage (script a preparar)
- Discourses of Brigham Young (fuente externa, script nuevo)

### FR-5: Manuales doctrinales esenciales
- Gospel Principles (script a preparar)
- True to the Faith (script a preparar)
- Teachings of Presidents — Joseph Smith (script a preparar)

### FR-6: Come Follow Me — ciclo actual
- Individuals & Families para los 4 libros del ciclo (EN+ES)

### FR-7: Serie Teachings of Presidents (completa)
- ~22 manuales, uno por Presidente de la Iglesia

### FR-8: Instituto y Seminary
- Manuales de Instituto: LdM, NT, AT, D&C, Historia de la Iglesia
- Requiere investigación de URL patterns

## Requisitos no funcionales

- Respetar rate limits del sitio (0.5s entre requests)
- Todo material nuevo: .txt + .meta.json con footnotes capturadas
- Ingesta siempre incremental — nunca reindex completo
- Cada script nuevo usa `scripts/lib/church_scraper.py`

## Fuera de alcance en P4

- Revistas (Ensign/Liahona) — volumen demasiado grande, P5
- Journal of Discourses — complejidad histórica, P5
- Fine-tuning o cambios al pipeline — proyectos separados (P9)
- Contenido de audio/video
