# Fase 0 — Preach My Gospel 2023

> Análisis de contenido y relaciones KG. Extraído de la reorganización del backlog (2026-04-05).

---

### Preach My Gospel 2023

**Estado corpus:** `ingested` | authority=60 | EN+ES

**KG — qué ya está capturado:**

| Tipo de relación | Mecanismo | Cobertura |
|-----------------|-----------|-----------|
| Entidades doctrinales mencionadas (Faith, Repentance, Baptism, Atonement, Restoration, etc.) | Gazetteer NER ✅ | Alta densidad |
| Co-ocurrencia de entidades en el mismo chunk | `RELATED_TO` / `TEACHES` tipo-inferido ✅ | Todos los chunks |
| Scripture refs en footnotes | meta.json `scripture_refs` ✅ | ~200+ refs estimadas |
| Estructura de capítulos (5 lecciones = 5 nodos de trabajo) | meta.json→KG `work/PART_OF` ✅ | Solo si `title`/`book` están en meta.json — **verificar** |

**KG — qué falta y debe agregarse a `relations.json`:**

La secuencia de primeros principios (Artículo de Fe 4) es la contribución estructural más importante de PME:

```
Faith -[PREREQUISITE_FOR]-> Repentance
Repentance -[PREREQUISITE_FOR]-> Baptism
Baptism -[PREREQUISITE_FOR]-> Holy Ghost (gift)
Holy Ghost (gift) -[PREREQUISITE_FOR]-> Endure to End
```

Estas relaciones NO están en `relations.json`. Se producen co-ocurrencias genéricas (`RELATED_TO`) pero no la secuencia ordenada.

| Relación | from | to | Source ref |
|----------|------|----|------------|
| `PREREQUISITE_FOR` | Faith | Repentance | AoF 4; PME cap 3 |
| `PREREQUISITE_FOR` | Repentance | Baptism | AoF 4; PME cap 3 |
| `PREREQUISITE_FOR` | Baptism | Holy Ghost (gift) | AoF 4; D&C 20:41 |
| `PART_OF` | Faith | Gospel | AoF 4 |
| `PART_OF` | Repentance | Gospel | AoF 4 |
| `PART_OF` | Baptism | Gospel | AoF 4 |
| `PART_OF` | Holy Ghost (gift) | Gospel | AoF 4 |
| `TAUGHT` | Jesus Christ | Plan of Salvation | PME cap 2; 2 Nephi 9 |
| `TAUGHT` | Jesus Christ | Gospel | 3 Nephi 27:13-21 |

**Nota:** PME también estructura la Restauración como narrativa: Joseph Smith → Primera Visión → Restauración → Sacerdocio → Iglesia. Estas relaciones ya existen parcialmente en relations.json vía `RESTORED` (7 entradas) y `CONFERRED_KEYS_TO` (8 entradas).
