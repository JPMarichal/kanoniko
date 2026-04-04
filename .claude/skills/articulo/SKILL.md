---
name: articulo
description: Crear o revisar un artículo (standalone o serie) para el blog de Juan Pablo Marichal. Invoca protocolo DF, aplica FCD, 4 fases de producción, SEO cola larga, interlinking y checklist anti-IA.
---

# Skill: Creación de Artículos

Producto editorial para el blog/sitio de Juan Pablo Marichal. Cada artículo es una pieza amena, rigurosa y bien documentada.

---

## Fase 1: Investigación (antes de escribir)

Seguir el skill `documentation-first` (DF):
1. **Consultar Alejandría** (corpus, KG, búsqueda híbrida) para fuentes doctrinales y eclesiásticas
2. **Evaluar cobertura** — solo complementar con web para lo que el corpus no cubra
3. **Verificar citas** antes de incluirlas — nunca presentar conjeturas como hechos

## Fase 2: Columna doctrinal (antes de escribir)

**Series: obligatorio. Standalone: recomendado.**

1. **Crear `doctrinal-spine.md`** en la carpeta de la serie: escrituras ancla + fuentes proféticas mapeadas a cada artículo
2. **Escrituras**: mínimo 3-5 por artículo (recomendación, no límite), con equilibrio entre formatos:
   - **Inline**: referencias breves que sostienen un argumento sin interrumpir el flujo
   - **Outline/blockquote** (`>`): pasajes destacados donde el lector debe detenerse
   - También para citas de Autoridades Generales: las más poderosas merecen outline
   - **El contenido dicta la forma** — no limitar la cantidad de ningún formato
3. **Mapa de responsabilidad temática** (series): cada tema transversal tiene UN artículo propietario. Los demás: máximo 1-2 oraciones + referencia cruzada explícita
4. **Diversificar fuentes proféticas** — no repetir las mismas citas en todos los artículos
5. **Mapa de propiedad de citas** (series): cada cita recurrente asignada a UN artículo (outline completo); los demás hacen mención breve + interlink

## Fase 3: Escritura (aplicar desde el borrador)

1. **Patrón texto-contexto-aplicación**: qué dice la fuente → por qué importa → qué significa para el lector
2. **Patrones narrativos de conferencia general**: metáfora central sostenida, preguntas retóricas como transiciones, variación de ritmo, cierre circular
3. **Fuentes seculares abren, escrituras anclan, profetas cierran** — patrón dominante en los mejores discursos
4. **Conectar con la Restauración y la Segunda Venida** cuando el tema lo permita

## Fase 4: Revisión (antes de entregar)

Aplicar los tres checklists en orden:

### 4a. Checklist anti-IA

(Ver `feedback_avoid_ai_patterns.md` para la lista completa)

- [ ] No más de 2 instancias de "no es X, es Y"
- [ ] No todos los párrafos empiezan con oración temática
- [ ] Transiciones variadas (no todas causales/adversativas)
- [ ] Tono no uniforme de principio a fin (variación de ritmo)
- [ ] Sin listas repetitivas "De X a Y"
- [ ] Sin palabras sobreusadas de la lista léxica

### 4b. Checklist editorial

- [ ] Conteo de escrituras verificado (mín. 3-5 por artículo)
- [ ] Responsabilidad simple verificada en series
- [ ] Integridad bibliográfica (notas numeradas sin huérfanas ni duplicadas)
- [ ] Terminología correcta (llamamientos, no puestos; títulos honrosos para AG)
- [ ] Tuteo al lector (tú, no usted)
- [ ] ~3,000 palabras (flexible)
- [ ] Texto + contexto + aplicación presentes

### 4c. Checklist SEO cola larga

(Ver `reference_seo_longtail_interlinking.md` para la guía completa)

- [ ] Title tag (`title`): 50-60 chars, keyword al inicio
- [ ] Abstract: 150-155 chars, keyword en primeras palabras
- [ ] Slug = keyword principal en kebab-case (sin prefijo de serie)
- [ ] H1 contiene keyword de cola larga completa
- [ ] Al menos 2 H2s contienen variantes de keywords de búsqueda
- [ ] Primer párrafo incluye la keyword naturalmente
- [ ] **Alineación keyword↔meta** (ver reglas abajo):
  - [ ] `focus_keyword` define los términos ancla — todos los demás campos deben contenerlos
  - [ ] `meta_title`: contiene términos core del focus_keyword (50-60 chars)
  - [ ] `meta_description`: abre con términos core del focus_keyword (150-155 chars)
  - [ ] `og_title`: contiene al menos 1-2 términos core (puede ser más emocional)
  - [ ] `og_description`: prioriza engagement sobre keywords, pero mantiene coherencia temática
- [ ] **Series:** interlinks al pillar (1x) + a 1-2 clusters hermanos
- [ ] **Standalone:** 3-5 links contextuales a artículos relacionados (tags compartidos)
- [ ] **Standalone:** artículos existentes actualizados con link de vuelta (cross-pollination)
- [ ] Anchor text descriptivo y variado (nunca genérico)
- [ ] Sin artículos huérfanos (mín. 2 enlaces entrantes contextuales)
- [ ] Propiedad de citas verificada (outline solo en el artículo propietario, si aplica)

---

## Template del archivo

```markdown
---
title: "Título display/H1 — keyword de cola larga completa, puede exceder 60 chars"
author: Juan Pablo Marichal
date: YYYY-MM-DD
abstract: "150-155 chars. Keyword + valor + gancho. Puede servir como fallback de meta_description."
tags: [tag1, tag2, tag3]
category: "Categoría principal"
slug: keyword-principal-en-kebab-case
focus_keyword: "3-5 palabras — frase de búsqueda más probable. ANCLA: todos los meta campos derivan de aquí"
meta_title: "50-60 chars. Términos core del focus_keyword al inicio. Para <title> tag y SERP."
meta_description: "150-155 chars. ABRE con términos core del focus_keyword. Snippet de Google — gancho + valor."
og_title: "Más emocional/directo que meta_title. Contiene 1-2 términos core. Para Facebook/LinkedIn/WhatsApp."
og_description: "Gancho conversacional para redes. Prioriza engagement sobre keywords. 2-3 líneas."
og_type: article
og_image: ""                          # URL de imagen destacada — se llena al publicar
series: "Nombre de la serie"        # solo si aplica
series_part: N                       # solo si aplica
---

# Título H1 (puede ser más largo que el title tag, keyword de cola larga completa)

[Cuerpo del artículo con citas FCD e interlinks contextuales]

---

## Bibliografía y notas

[1] Apellido, Nombre. "Título." Fuente, fecha.
```

## Formato de citas (FCD)

**Cita directa de AG o fuente:**
```
Como enseñó el presidente Nelson: "Necesitamos un ajuste a ese patrón" [1].
```

**Cita outline (blockquote) para momentos de peso:**
```
> "La gloria de Dios es la inteligencia, o en otras palabras, luz y verdad" (DyC 93:36).
```

**Escritura inline:**
```
El Señor declaró: "Esta es mi obra y mi gloria" (Moisés 1:39).
```

**Interlink contextual (series):**
```
La [transformación del consejo de barrio](02-consejo-de-barrio.md) cuenta esa historia en detalle.
```
Anchor text = keyword descriptiva del artículo destino, nunca genérico ("haz clic aquí", "este artículo").

---

## Convenciones de archivos

### Standalone
```
prods/articulos/stand-alone/keyword-principal-en-kebab-case.md
```

### Series
```
prods/articulos/series/{tema-descriptivo}/
  00-indice.md                    # índice con tabla de artículos, slugs, mapa de interlinks
  doctrinal-spine.md              # columna doctrinal (fase 2)
  NN-keyword-principal.md         # artículos numerados
```

- La carpeta es descriptiva del tema general
- El prefijo numérico (NN-) ordena; el nombre del archivo es la keyword principal
- **NO usar nombre de serie en el archivo** — la serie va solo en el frontmatter `series`
- El `slug` en el frontmatter es la URL que se usará en WordPress

### Modelo pillar-cluster (series)

- **Art 01** = pillar page (panorámica, enlaza a todos los clusters)
- **Arts 02+** = cluster pages (profundizan un subtema, enlazan al pillar y entre sí)
- Bidireccional: pillar → clusters Y clusters → pillar
- Cluster ↔ cluster cuando hay relación contextual

### Interlinking de standalones (red temática)

Los standalones no tienen estructura formal de serie, pero forman una **red temática implícita** a través de tags compartidos y enlaces contextuales.

**Protocolo al publicar un standalone nuevo:**

1. **Identificar 2-3 artículos existentes** (standalones o de series) que comparten tema, tags o audiencia
2. **Añadir enlaces salientes** al nuevo artículo hacia esos artículos (en el cuerpo, con anchor text keyword-rich)
3. **Actualizar los artículos existentes** con un enlace de vuelta al nuevo artículo (cross-pollination bidireccional)
4. **Verificar anti-huérfanos:** todo artículo debe tener mínimo 2 enlaces entrantes contextuales

**Modelos de conexión entre standalones:**

- **Por tags compartidos:** Artículos con 2+ tags en común deben enlazarse entre sí
- **Hub emergente:** Un standalone sobre un tema amplio puede convertirse en hub informal al que otros más específicos enlazan (mini-pillar sin serie formal)
- **Cross-serie:** Standalones pueden enlazar a artículos de series y viceversa cuando hay relevancia temática

**Cuántos links por artículo:**

- **3-5 links contextuales** por artículo de ~3,000 palabras (1 link cada ~600-1000 palabras)
- Links en el **primer 30%** del artículo pesan más para Google
- Nunca forzar links — solo donde hay relevancia temática real
- Anchor text descriptivo y variado (nunca genérico)

---

## Template: Índice de serie (`00-indice.md`)

```markdown
# Serie: {Nombre de la serie}

{Descripción de 1-2 oraciones: qué cubre la serie y por qué importa.}

**Autor:** Juan Pablo Marichal
**Estado:** {En producción | Publicada | En revisión}

## Artículos de la serie

| # | Archivo | Slug WordPress | Título | Enfoque | Estado |
|:--|:--------|:--------------|:-------|:---------|:-------|
| 01 | `01-keyword.md` | `slug-wordpress` | Título completo | Enfoque (PILLAR) | estado |
| 02 | `02-keyword.md` | `slug-wordpress` | Título completo | Enfoque | estado |

## Distribución temática por artículo

- **01 (pillar):** Todos los temas, a nivel introductorio
- **02 (cluster):** Temas A, B, C
{mapeo de responsabilidad simple}

## Mapa de interlinking

**Pillar:** Art 01
**Clusters:** Arts 02+

| Artículo | Enlaza a → | Recibe enlaces de ← |
|----------|-----------|---------------------|
| 01 (PILLAR) | 02, 03... | 02, 03... |

## Propiedad de citas recurrentes

| Cita | Propietario (outline) | Otros → tratamiento |
|------|----------------------|---------------------|
| Autor "frase clave" | Art NN | Art NN → breve + link |

## Notas de producción

{Noticias integradas, decisiones editoriales, cronología de cambios}
```

---

## Template: Columna doctrinal (`doctrinal-spine.md`)

```markdown
# Columna Doctrinal — Serie "{Nombre}"

{Descripción: escrituras, fuentes doctrinales y patrones narrativos que anclan cada artículo.}

---

## {TEMA 1} — {Subtítulo descriptivo}

### Escrituras clave

| Referencia | Texto relevante | Aplicación en la serie |
|------------|----------------|------------------------|
| **Ref 1** | "Texto..." | Cómo se usa, en qué artículo |

### Fuentes proféticas

| Fuente | Cita/concepto | Artículo destino |
|--------|--------------|------------------|
| **AG, Nombre** (Fuente, fecha) | "Cita o concepto..." | Art NN |

---

## {TEMA 2} — {Subtítulo descriptivo}

{Repetir estructura: escrituras clave + fuentes proféticas}

---

## Redistribución de temas transversales

{Solo si un tema sangra entre artículos — definir propietario y tratamiento}

| Tema | Propietario | Otros artículos |
|------|------------|-----------------|
| Tema X | Art NN (tratamiento completo) | Art NN → 1-2 oraciones + link |
```

---

## Tipos de artículo

El tipo actual es el **artículo editorial estándar** (~3,000 palabras, ameno+académico, FCD). Otros tipos se definirán según necesidad — el proceso de 4 fases y los checklists aplican a todos; lo que varía es la estructura del cuerpo, el largo y el tono.

---

## Estilo editorial

- Fresco, ameno, accesible, reflexivo
- **Tutear** al lector: "imagina", "considera", "si fuiste"
- Romper la cuarta pared en ocasiones
- Ilustraciones verificables: anécdotas, reflexiones, ejemplos prácticos
- **Llamamientos** o **asignaciones**, nunca "puestos" ni "cargos"
- AG siempre con título honroso: "el élder Ballard", "el presidente Nelson"
- No "secretismo" — preferir "acceso a la información", "transparencia"
- No jerga de sistema (corpus, KG, FTS) en el texto del artículo
