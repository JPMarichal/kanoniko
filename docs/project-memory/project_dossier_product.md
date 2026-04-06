---
name: project_dossier_product
description: Dossier doctrinal product type — exhaustive reference docs in prods/dossiers/ with template, naming, and design rules
type: project
---

**Dossier doctrinal** is a product type in `prods/dossiers/`. It's an **intermediate analysis and compilation layer** — NOT a finished discourse or article. It collects full scripture passages, prophetic quotes, academic citations, Mermaid diagrams, and connection maps. Designed as the skeleton from which any other material (Formas T, articles, classes, talks) can be built. The dossier itself is never the end product; it's the research base that feeds everything else.

**Why:** Formas T are compact teaching tools (table of concepts+references). Dossiers are the deep, exhaustive research layer that feeds them and any other product. They are independent products with overlapping territory, not hierarchical.

**How to apply:**

- **Template:** `prods/dossiers/_template.md` — sections: Panorama, Escrituras clave, Voces proféticas, Voces académicas, Diagrama, Conexiones, Lagunas, Fuentes citadas
- **Reading pattern:** intro→cita (introductory paragraph BEFORE each blockquote, never after)
- **FCD translation norm:** English quotes must be translated to Spanish when the dossier is in Spanish
- **Single responsibility / KISS:** Each dossier covers ONE doctrinal territory; if a subtopic has enough depth, it gets its own dossier
- **Naming:** `{collection_id}-dp{NN}-{slug}.md` — e.g., `0001-dp01-hijos-espirituales.md`; dp00 is the panoramic/index dossier
- **Exhaustive approach:** Multiple scripture passages with full text, multiple prophetic + academic voices, Mermaid diagrams (graph, timeline, mindmap as appropriate)
- **Mermaid diagram rules:** (1) Fondos pastel + texto oscuro (`color:#1a1a1a`), nunca fondos saturados con texto blanco — legibilidad ante todo. (2) Nodos con texto corto (concepto + referencia abreviada), sin citas textuales ni fragmentos largos. (3) Paleta: azul `#d0e4f7`, verde `#d4edda`, rojo `#f5d0d0`, dorado `#f5ecd0`, púrpura `#e0d4f7`
- **Language-agnostic sourcing:** Sources are searched in any corpus language; presentation language is independent
- **Semi-automatic generation:** KG proposes neighborhood, human curates, corpus provides references, agent writes with corpus verification
- **Relationship to Formas T:** Organic, not hierarchical. A dossier may map to multiple Formas T; a Forma T may draw from multiple dossiers
