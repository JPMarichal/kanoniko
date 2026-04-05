# Fase 0 — Study Plans (Christmas + Easter)

> Análisis de contenido y relaciones KG. Extraído de la reorganización del backlog (2026-04-05).

---

## Tier 0 — Planes de Estudio Estacionales (authority=60)

### Christmas Study Plan (anual)

**Estado:** `ingested` — Script: `download_christmas_study_plan.py` — 2024 descargado (9 archivos). 2025 confirmado inexistente en el sitio oficial.

**Estructura:** 9 páginas — intro + "Light the World" overview + 7 lecturas
diarias (19–25 dic). Slug **año-sufijado** (`christmas-study-plan-2024`):
se renueva cada año. Requiere `--year` al ejecutar.

**URL:** `/study/manual/christmas-study-plan-{año}` | Bilingüe: sí

**Contenido por página:** devoción en prosa, pasajes escriturales con
preguntas de reflexión, enlace a video, actividad para niños, ideas de servicio.

**KG — relaciones esperadas:**
- 7 eventos del nacimiento (natividad) → secuencia temporal con relación
  `narrates_event` por día
- Profecías AT (Isaías, Miqueas, Alma 7) → intertextualidad con NT/LdM
- 3 Nefi 1 (noche sin oscuridad) vinculada al 23 dic → paralelo único LdM↔NT
- "Light the World" como concepto doctrinal con relaciones de servicio

**Consideración especial:** El slug cambia cada año → el corpus crecerá
con un directorio nuevo por edición. Priorizar la más reciente.

---

### Easter / Holy Week Study Plan

**Estado:** `ingested` — Script: `download_easter_study_plan.py` — 18 archivos en corpus

**Estructura:** 18 páginas en **dos pistas paralelas** que recorren
simultáneamente la misma semana:
- **Pista NT** (9 páginas): Palm Sunday → Easter Monday, cronología evangélica
- **Pista BoM** (8 páginas): mismos días, narrativa paralela en 3 Nefi

El slug es **permanente** (`easter-plan`) — se actualiza in-place cada año.

**URL:** `/study/manual/easter-plan` | Bilingüe: sí

**KG — valor estructural único:**
- Cada par de páginas (NT + BoM mismo día) crea relaciones `parallel_to`
  entre pasajes del NT y 3 Nefi — el corpus mismo establece esta intertextualidad
- `day_key` en meta.json (e.g., `"good-friday"`) es la clave de unión entre
  pistas → permite consultas como "¿qué paralelos hay entre Juan 19 y 3 Nefi?"
- 8 días × 2 pistas = 16 pares de intertextualidad doctrinal curada
- Expiación, Resurrección, Sacramento como conceptos con múltiples entradas
- Jueves Santo: Última Cena (NT) + institución del Sacramento en las Américas (BoM)

**Preguntas habilitadas:**
- "¿Qué paralelos hay entre la crucifixión y 3 Nefi?"
- "¿Cómo ven los SUD el Viernes Santo en relación al Libro de Mormón?"
- "¿Qué ocurrió en las Américas durante la semana de la Expiación?"
