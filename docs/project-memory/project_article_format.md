---
name: Formato estándar de artículos
description: Especificación del producto "artículo" para el blog/sitio de Juan Pablo Marichal. Incluye estructura, estilo, bibliografía, largo y principios editoriales.
type: project
---

## Definición de producto: Artículo

### Estructura obligatoria
- **Título:** Atractivo, orientado a marketing y SEO
- **Abstract:** En la parte superior, claramente diferenciado. Apropiado para WordPress (se usa como excerpt/meta description)
- **Autor:** Juan Pablo Marichal (por default)
- **Fecha:** Incluir siempre
- **Cuerpo:** Texto con citas bibliográficas (FCD — formato de cita directa), pasajes de escrituras, e ilustraciones verificables (anécdotas, reflexiones)
- **Bibliografía y Notas al calce:** Sección al final detallando todas las fuentes usadas

### Principios de contenido
- Basarse en **más de una fuente** — mientras más, mejor
- Incluir **texto** (qué dice la fuente), **contexto** (por qué importa, qué estaba pasando) y **aplicación** (qué significa para el lector hoy)
- Profundidad académica pero **ameno, interesante y digerible** para cualquier nivel de lector
- Dar al lector novel suficiente contexto sin abrumar al experto
- **Principio de responsabilidad simple:** si un tema se extiende más allá del alcance, subdivir en otros artículos o crear series

### Estilo editorial
- Fresco, ameno, accesible
- Romper la cuarta pared en ocasiones (dirigirse al lector, aludir a su experiencia práctica)
- Reflexivo, cercano al lector
- Ilustraciones verificables: anécdotas, reflexiones, ejemplos prácticos que contribuyan a comprensión y amenidad

### Especificaciones técnicas
- **Largo estándar/promedio:** 3,000 palabras (puede abreviarse o extenderse según necesidad)
- **Citas:** Formato FCD (cita directa con referencia a la bibliografía)
- **Escrituras:** Citadas como pasajes dentro del texto
- **Bibliografía:** Sección final con todas las fuentes detalladas

### Proceso de producción (orden obligatorio)

#### Fase 1: Investigación (antes de escribir)
1. **Consultar corpus** (Alejandría) para fuentes doctrinales y eclesiásticas
2. **Complementar con web** para contexto histórico, noticias, artículos de terceros
3. **Verificar citas** antes de incluirlas

#### Fase 2: Columna doctrinal (antes de escribir — series obligatorio, standalone recomendado)
1. **Crear doctrinal-spine.md** en la carpeta de la serie: escrituras ancla + fuentes proféticas mapeadas a cada artículo
2. **Mínimo 3-5 escrituras por artículo**, con equilibrio entre formatos (recomendación, no límite — usar las que el artículo necesite):
   - **Inline**: referencias breves que sostienen un argumento sin interrumpir el flujo
   - **Outline/blockquote** (`>`): pasajes destacados donde el lector debe detenerse. Reservar para escrituras ancla o momentos de peso espiritual
   - También aplica a citas de Autoridades Generales y fuentes: las más poderosas merecen formato outline
   - No limitar la cantidad de ninguno de los dos formatos; el contenido dicta la forma
3. **Mapa de responsabilidad temática** para series: cada tema transversal tiene UN artículo propietario. Los demás artículos: máximo 1-2 oraciones + referencia cruzada explícita ("ver Art N de esta serie")
4. **Diversificar fuentes proféticas** por artículo — no repetir las mismas 3 citas en todos

#### Fase 3: Escritura (aplicar desde el borrador)
1. **Patrón texto-contexto-aplicación** para cada dato o cambio: qué dice la fuente → por qué importa (contexto) → qué significa para el lector (aplicación espiritual/práctica)
2. **Patrones narrativos de conferencia general**: metáfora central sostenida, preguntas retóricas como transiciones, variación de ritmo (párrafos cortos alternados con bloques narrativos), cierre circular
3. **Fuentes seculares abren, escrituras anclan, profetas cierran** — patrón dominante en los mejores discursos
4. **Conectar con la Restauración y la Segunda Venida** cuando el tema lo permita — los cambios administrativos no son mera logística

#### Fase 4: Revisión (antes de entregar)
1. **Checklist anti-IA** (ver `feedback_avoid_ai_patterns.md`):
   - ¿Más de 2 instancias de "no es X, es Y"?
   - ¿Cada párrafo empieza con oración temática?
   - ¿Transiciones todas causales/adversativas?
   - ¿Tono uniforme de principio a fin?
   - ¿Listas repetitivas "De X a Y"?
   - ¿Palabras sobreusadas de la lista léxica?
2. **Verificar conteo de escrituras** (mín. 3-5 por artículo)
3. **Verificar responsabilidad simple** en series (tema X no sangra a otros artículos)
4. **Verificar integridad bibliográfica** (notas numeradas sin huérfanas ni duplicadas)
5. **Checklist SEO cola larga** (ver `reference_seo_longtail_interlinking.md`):
   - ¿Slug = keyword principal en kebab-case (sin prefijo de serie)?
   - ¿Title/H1 contiene la keyword long-tail principal?
   - ¿Abstract < 160 chars con keyword en las primeras palabras?
   - ¿Al menos 2 H2s contienen variantes de keywords de búsqueda?
   - ¿Primer párrafo incluye la keyword naturalmente?
   - ¿Interlinks al pillar (1×) + a 1-2 clusters hermanos?
   - ¿Anchor text descriptivo y variado (nunca genérico)?
   - ¿Propiedad de citas verificada (outline solo en el artículo propietario)?

### Directorio de salida
- **Proyecto:** `C:\own\alejandria` (NO singalong)
- **Raíz de productos:** `prods/`
- **Artículos standalone:** `prods/articulos/stand-alone/keyword-principal-en-kebab-case.md`
- **Series:** `prods/articulos/series/{tema-descriptivo}/NN-titulo-keyword.md`
  - Ej: `series/orden-unida/01-que-es-orden-unida.md`
  - Ej: `series/cambios-en-los-consejos/01-cambios-gobierno-iglesia.md`
  - La carpeta es descriptiva del tema; el prefijo numérico ordena; el nombre del archivo es la keyword principal
  - **NO usar nombre de serie en el archivo** — la serie va en el frontmatter `series`
- **Convención de nombres:** NN-keyword-principal-en-kebab-case

### Frontmatter YAML obligatorio
```yaml
# --- Contenido ---
title       # Display/H1 — keyword de cola larga completa, puede exceder 60 chars
author      # Juan Pablo Marichal (default)
date        # YYYY-MM-DD
abstract    # 150-155 chars — keyword + valor + gancho (fallback de meta_description)
tags        # [keywords secundarias relevantes]
category    # Categoría principal

# --- SEO (Google) ---
slug            # keyword principal en kebab-case (URL en WordPress)
focus_keyword   # keyword de cola larga — ANCLA: todos los meta campos derivan de aquí
meta_title      # 50-60 chars — términos core del focus_keyword al inicio
meta_description # 150-155 chars — ABRE con términos core del focus_keyword

# --- Social (Open Graph) ---
og_title        # Más emocional/directo que meta_title — 1-2 términos core
og_description  # Gancho conversacional — engagement > keywords
og_type         # siempre "article"
og_image        # URL de imagen destacada — se llena al publicar

# --- Serie (solo si aplica) ---
series          # Nombre de la serie
series_part     # Número de orden
```

**Regla de alineación:** `focus_keyword` es el ancla (3-5 palabras, la frase de búsqueda más probable). `meta_title` y `meta_description` abren con sus términos core. `og_*` mantiene coherencia temática pero prioriza engagement. Keywords secundarias, años y variantes van en `tags` y H2s. No abreviaturas (SUD), no años en focus_keyword (caducan), no frases de 7+ palabras (keyword stuffing).

**Why:** El usuario produce artículos para su blog/sitio con estándar editorial definido. Los productos van en `prods/`. Este formato asegura consistencia y calidad.

**How to apply:** Usar esta especificación cada vez que se produzca un artículo. Crear en `prods/articles/`. Verificar contra el checklist antes de entregar.
