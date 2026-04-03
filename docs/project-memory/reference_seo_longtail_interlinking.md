---
name: SEO cola larga e interlinking para WordPress
description: Mejores prácticas de long-tail SEO, modelo pillar-cluster, interlinking contextual y anchor text para series de artículos en WordPress.
type: reference
---

## Long-Tail SEO + Interlinking para WordPress (Series de Artículos)

### Modelo Pillar-Cluster

La estructura ideal para una serie de artículos en WordPress es el **modelo pillar-cluster**:

- **Pillar page (artículo panorámico):** Cubre el tema amplio, enlaza a cada cluster
- **Cluster pages (artículos específicos):** Cada uno profundiza un subtema, enlaza al pillar y a otros clusters relacionados
- **Bidireccional:** Pillar → clusters Y clusters → pillar. También cluster ↔ cluster cuando hay relación contextual

### Dónde van los long-tail keywords

| Elemento | Regla | Ejemplo |
|----------|-------|---------|
| **H1** | Keyword principal completa, natural | "Mujeres en los Consejos de la Iglesia: De Invitadas a Esenciales" |
| **Title tag (YAML `title`)** | Puede coincidir con H1 o ser variante corta | Mismo o ligeramente diferente |
| **URL slug** | Solo la keyword principal, sin prefijo de serie ni números | `mujeres-consejos-iglesia-jesucristo` (NO `04-revolucion-silenciosa-mujeres`) |
| **Abstract/meta description** | Keyword + gancho emocional, <160 caracteres ideales | Incluir la keyword en las primeras palabras |
| **H2s** | Al menos 1-2 deben contener variantes de la keyword | "Cómo el élder Ballard transformó el consejo de barrio" |
| **Primer párrafo** | Keyword principal en las primeras 100 palabras | Natural, no forzado |

### Reglas de slugs para WordPress

- **No usar prefijo numérico** (01-, 02-) en el slug — el orden va en `series_part`
- **No usar nombre de serie en el slug** — va en el campo `series` del frontmatter y en la categoría/taxonomy de WordPress
- **El slug es la keyword principal en kebab-case**, lo más corto posible
- **WordPress genera la URL:** `sitio.com/serie/slug` — la jerarquía la da la taxonomía, no el nombre del archivo

### Interlinking contextual (aplica a series y standalones)

- **Links embebidos en el párrafo**, nunca en listas de "artículos relacionados" al final
- **Anchor text descriptivo y keyword-rich:** "la [transformación del consejo de barrio](...)" — NO "el [segundo artículo](...)" ni "[haz clic aquí](...)"
- **Variar el anchor text:** No usar el mismo texto para todos los enlaces al mismo artículo
- Links en el **primer 30% del artículo pesan más** para Google
- **Regla de propiedad de citas** (series): Cada cita recurrente tiene UN artículo propietario. Los demás hacen mención breve + enlace.

### Interlinking de series (pillar-cluster)

- Cada cluster enlaza al pillar (1×) + a 1-2 clusters hermanos
- El pillar enlaza a todos los clusters
- Bidireccional siempre

### Interlinking de standalones (red temática)

- **3-5 links contextuales** por artículo de ~3,000 palabras
- Al publicar un nuevo standalone: identificar 2-3 artículos existentes con tags compartidos, añadir links salientes y **actualizar los existentes** con link de vuelta (cross-pollination)
- **Anti-huérfanos:** todo artículo tiene mín. 2 enlaces entrantes contextuales
- **Hub emergente:** un standalone sobre tema amplio puede funcionar como mini-pillar informal
- **Cross-serie:** standalones pueden enlazar a artículos de series y viceversa

### Regla de alineación focus_keyword → meta campos

El `focus_keyword` es el ancla. Todos los meta campos deben derivar de él:

| Campo | Relación con focus_keyword | Prioridad |
|-------|---------------------------|-----------|
| `slug` | Términos core en kebab-case | SEO (URL) |
| `meta_title` | Términos core al inicio, 50-60 chars | SEO (SERP title) |
| `meta_description` | **Abre** con términos core, 150-155 chars | SEO (SERP snippet) |
| `title` / H1 | Keyword de cola larga completa, puede exceder 60 chars | SEO + lectura |
| `abstract` | Keyword + valor + gancho, 150-155 chars | Fallback / excerpt WP |
| `og_title` | 1-2 términos core, tono emocional/directo | Social (engagement) |
| `og_description` | Coherencia temática, prioriza gancho sobre keyword | Social (engagement) |
| H2s (al menos 2) | Variantes/sinónimos del focus_keyword | SEO (structure) |
| Primer párrafo | Keyword natural en primeras 100 palabras | SEO (content) |

**Principio:** `meta_*` optimiza para Google (keyword-first, longitudes exactas). `og_*` optimiza para redes sociales (gancho emocional, tono personal). `title`/H1 puede ser más largo y expresivo. `abstract` sirve de fallback si WordPress no tiene meta_description configurado.

**Longitud del focus_keyword:** 3-5 palabras (sweet spot para long-tail). Keywords secundarias (variantes, sinónimos, año) van en `tags` y se cubren en H2s y contenido — no en el focus_keyword.

**Anti-patrón 1:** Focus keywords de 7+ palabras — fuerzan repeticiones artificiales y no coinciden con búsquedas reales.

**Anti-patrón 2:** Usar abreviaturas (SUD, IJSUD) en meta campos cuando el focus_keyword usa el nombre completo. Las abreviaturas no coinciden con las búsquedas reales del público objetivo.

**Anti-patrón 3:** Incluir años en el focus_keyword — caduca rápido. El año va en `meta_title` o `meta_description` donde se puede actualizar sin cambiar la keyword ancla.

### Checklist pre-publicación SEO para series

1. [ ] **Slug** = keyword principal en kebab-case (sin prefijo numérico ni nombre de serie)
2. [ ] **Title/H1** contiene la keyword long-tail principal
3. [ ] **Abstract** < 160 chars con keyword en las primeras palabras
4. [ ] **Al menos 2 H2s** contienen variantes de keywords
5. [ ] **Primer párrafo** incluye la keyword naturalmente
6. [ ] **Series:** interlinks al pillar (1×) + a 1-2 clusters hermanos
7. [ ] **Standalone:** 3-5 links contextuales a artículos relacionados (por tags compartidos)
8. [ ] **Standalone:** artículos existentes actualizados con link de vuelta (cross-pollination)
9. [ ] **Anchor text** descriptivo y variado (nunca genérico)
10. [ ] **Anti-huérfanos:** todo artículo tiene mín. 2 enlaces entrantes contextuales
11. [ ] **Citas propiedad** verificadas: outline solo en el artículo propietario (si aplica)
12. [ ] **Tags YAML** incluyen keywords secundarias relevantes

### Keywords de la serie "Revolución Silenciosa"

| focus_keyword (3-5 palabras) | Artículo | Keywords secundarias (en tags/H2s) |
|------------------------------|----------|-----------------------------------|
| cambios gobierno iglesia jesucristo | Art 01 (pillar) | santos últimos días, transformación, revelación continua |
| consejo de barrio iglesia jesucristo | Art 02 | comité ejecutivo sacerdocio, élder Ballard, simplificación |
| manual general iglesia transparencia | Art 03 | manuales confidenciales, acceso público, globalización |
| mujeres consejos iglesia jesucristo | Art 04 | escuela dominical mujeres 2026, autoridad sacerdocio |
| iglesia centrada en el hogar | Art 05 | horario dominical 2026, ven sígueme, FSY, currículo hogar |

**Why:** El usuario produce artículos para WordPress en un nicho religioso hispanohablante. El long-tail SEO y el interlinking son críticos para posicionamiento en un espacio donde los keywords cortos están dominados por sitios oficiales de la Iglesia.

**How to apply:** Usar este checklist en la Fase 4 (Revisión) del proceso de producción de artículos. Los slugs deben decidirse antes de publicar en WordPress — los nombres de archivo locales pueden diferir.
