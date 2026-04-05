---
name: project_covenant_path_architecture
description: "Formas T: 3 collections (0001 plan-salvacion 67, 0002 senda 54, 0003 vidas 6) — naming convention, group architecture"
type: project
---

Tres colecciones de Formas T, 127 formas totales:

| ID | Colección | Formas | Grupos |
|----|-----------|--------|--------|
| 0001 | plan-salvacion | 67 | 11 grupos (preexistencia → exaltación) |
| 0002 | senda-de-los-convenios | 54 | 7 grupos (senda → sellamiento) |
| 0003 | vidas | 6 | 1 grupo (biografías) |

**Colección 0002 — grupos y rangos:**
```
Senda (01-08) → Bautismo (09-16) → Espíritu Santo (17-23) → Santa Cena (24-31) → Sacerdocio (32-42) → Investidura (43-49) → Sellamiento (50-54)
  intro           entrada            don/compañía          renovación semanal     autoridad             convenios templo       familia eterna
```

**Naming convention:** `{CCCC}-{slug-coleccion}-{FF}-{slug}.md`
- CCCC: 4-digit collection ID
- FF: 2-digit form number (sequential within collection)
- Frontmatter: `collection`, `collection_id`, `group`, `collection_order`

**Why:** Los 7 grupos de la senda no son colecciones independientes — construyen una progresión doctrinal real que vive un miembro. El plan de salvación (0001) es el marco teológico; la senda (0002) es la experiencia práctica del convenio; vidas (0003) son biografías complementarias.

**How to apply:**
- Dentro de 0002, el `group` del frontmatter identifica el grupo temático (senda, bautismo, espiritu-santo, etc.)
- El `collection_order` es global dentro de la colección (no local al grupo)
- Las vidas son un género diferente: biografías, no parte de la progresión doctrinal
- Nuevas colecciones empiezan en 0004+
