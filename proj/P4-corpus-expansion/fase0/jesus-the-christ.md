# Fase 0 — Jesus the Christ (Talmage)

> Análisis de contenido y relaciones KG. Extraído de la reorganización del backlog (2026-04-05).

---

### Jesus the Christ — James E. Talmage

**Estado corpus:** `ingested` (43 capítulos EN) | Script: `download_jesus_the_christ.py` | authority=45, author="James E. Talmage"

**KG — qué ya está capturado:**

| Tipo de relación | Mecanismo | Cobertura |
|-----------------|-----------|-----------|
| `AUTHORED_BY` James E. Talmage | meta.json → pipeline ✅ | 43 capítulos |
| Tipos AT → Jesucristo (Brazen Serpent, Passover Lamb, Isaac, Manna, Melchizedek, etc.) | `TYPE_OF` en relations.json ✅ | 14 tipos |
| Símbolos → Jesucristo (Vine, Shepherd, Cornerstone, Lamb, etc.) | `SYMBOLIZES` en relations.json ✅ | 17 símbolos |
| Profecías mesiánicas (Isaías, Miqueas, Samuel) | `PROPHECY_OF` / `PROPHESIED_ABOUT` ✅ | 16+9 entradas |
| Menciones de entidades doctrinales (Atonement, Resurrection, Faith, etc.) | Gazetteer NER ✅ | 200+ conceptos |

**KG — qué falta y debe agregarse a `relations.json`:**

| Relación | from | to | Prioridad |
|----------|------|----|-----------|
| `TAUGHT` | Jesus Christ | Resurrection | Alta — JTC caps 35-38 son LA fuente |
| `TAUGHT` | Jesus Christ | Atonement | Alta — JTC cap 2, 34-38 |
| `TAUGHT` | Jesus Christ | Sermon on the Mount | Ya existe en TAUGHT ✅ |
| `TAUGHT` | Jesus Christ | Law of Moses (fulfillment) | Alta — JTC caps 12-14 |
| `QUOTED_BY` | Isaiah | Jesus Christ | Media — JTC cita Isaías extensamente |
| `TYPE_OF` | High Priest (Levitical) | Jesus Christ | Media — JTC cap 3 |

**Nota:** El gazetteer no tiene entrada para "James E. Talmage" como `person`. La relación `AUTHORED_BY` se crea desde meta.json, pero si alguien busca "Talmage" en el KG no encontrará el nodo a menos que NER lo detecte del texto. Se recomienda agregar a gazetteers después de la ingesta.
