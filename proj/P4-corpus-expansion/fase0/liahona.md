# Fase 0 — Liahona (Revista de la Iglesia)

> Investigacion inicial. Fecha: 2026-04-05.

---

## 1. Historia y cambios editoriales

### Antes de 2021 (formato antiguo)

La Iglesia publicaba **4 revistas**:

| Revista | Audiencia | Idioma | Periodo |
|---------|-----------|--------|---------|
| **Ensign** | Adultos | Solo ingles | 1971-2020 |
| **New Era** | Jovenes 12-18 | Solo ingles | 1971-2020 |
| **Friend** | Ninos | Solo ingles | 1971-presente |
| **Liahona** (antigua) | Todas las edades | Internacional (decenas de idiomas) | 1977-2020 (como "Tambuli" hasta 1995) |

La antigua Liahona era una revista **omnibus internacional** — combinaba contenido para todas las edades, mayormente traducido de Ensign, New Era y Friend.

### Desde enero 2021 (formato actual)

Anunciado agosto 2020 por la Primera Presidencia. Las 4 revistas se consolidaron en **3 revistas globales**:

| Revista | Audiencia | Frecuencia | Idiomas |
|---------|-----------|------------|---------|
| **Liahona** (nueva) | Adultos + adultos jovenes (digital) | Mensual | 47+ print, ~40 digital |
| **For the Strength of Youth** | Jovenes 12-18 | Mensual/bimestral | Mismos tiers |
| **Friend** | Ninos 3-11 | Mensual/bimestral | Mismos tiers |

**Agosto 2023:** Todas las revistas pasan a ser **gratuitas** worldwide (print y digital).

La nueva Liahona **reemplaza al Ensign** para angloparlantes y a la seccion adulta de la antigua Liahona para el resto del mundo. Ya no es una traduccion — tiene contenido original global.

---

## 2. Archivo disponible en churchofjesuschrist.org

### Cobertura temporal

| Idioma | Rango | Meses/ano tipico | Issues estimados |
|--------|-------|-------------------|-----------------|
| **EN** | 1977-2026 | 7 (1977) → 12 (2000+) | ~550 |
| **ES** | 2000-2026 | 12 | ~310 |

### Patron URL

```
TOC de un numero:  /study/liahona/{YYYY}/{MM}?lang={eng|spa}
Articulo individual: /study/liahona/{YYYY}/{MM}/{slug}?lang={eng|spa}
Indice por ano:     /study/magazines/liahona/{YYYY}?lang={eng|spa}
Indice general:     /study/magazines/liahona?lang={eng|spa}
```

### API v3

Funciona correctamente:
```
GET /study/api/v3/language-pages/type/content?lang=eng&uri=/liahona/{YYYY}/{MM}
```

Retorna TOC con: `href`, `primaryMeta` (autor), `title`, `description`, thumbnails.
Para articulo individual, retorna body HTML, footnotes, meta (igual que manuales/conferencia).

**Conclusion:** Se puede reutilizar `church_scraper.py` con adaptaciones menores.

---

## 3. Estructura de contenido por numero

### Numero regular (no-conferencia)

Ejemplo: octubre 2024, enero 2025 — **40-45 articulos** cada uno.

| Seccion | Articulos tipicos | Valor corpus |
|---------|-------------------|--------------|
| **Featured Articles** | 6-9 | ALTO — mensajes de lideres, doctrina |
| **Gospel Solutions** | 2-3 | ALTO — aplicacion doctrinal a problemas reales |
| **Latter-day Saint Voices** | 4-5 | MEDIO — testimonios personales |
| **Come, Follow Me** | 4-6 | ALTO — exegesis escritural alineada al curriculum |
| **Young Adults** | 8-10 | MEDIO — temas contemp. (salud mental, fe, dudas) |
| **Ongoing Series** | 2-3 | MEDIO — "The Church Is Here", columnas |
| **Local Pages** | 6-8 regiones | BAJO — noticias regionales, efimero |

### Numeros de conferencia — patron validado

Los numeros de conferencia **cambiaron de mes** a lo largo de la historia:

| Periodo | Conf. abril (Annual) | Conf. octubre (Semiannual) |
|---------|---------------------|---------------------------|
| **1977-1999** | No hay CG en Liahona EN (sitio tiene 404 pre-1995; mayo 1995 = regular) |  |
| **2000-2002** | **Julio** (ej. jul 2000, jul 2001) | **Enero** del ano siguiente (ej. ene 2001, ene 2002) |
| **2003-2020** | **Mayo** (ej. may 2003, may 2005) | **Noviembre** (ej. nov 2003, nov 2004) |
| **2021-presente** | **Mayo** (ej. may 2021, may 2025) | **Noviembre** (ej. nov 2024) |

> Validado caso a caso: may 1995 = regular; jul 2000, jan 2001, jul 2001 = conf;
> jul 2002 = regular; ene 2003 = regular; may 2003, nov 2003 = conf;
> may 2004, nov 2004 = conf; may 2021-2025, nov 2024 = conf.
> ES sigue el mismo patron (verificado may 2005 y may 2024).

Cada numero de conferencia contiene **30-40+ discursos completos** + informe estadistico, nuevos llamamientos, Church News.

**Deduplicacion critica:** Ya tenemos 110 sesiones de conferencia (1971-2025 EN, 1990-2025 ES) con ~34 discursos por sesion. Los discursos de la Liahona son **el mismo texto**.

---

## 4. Estimacion de volumen

### Calculo conservador

| Periodo | Issues | Conf. issues | Non-conf. issues | Arts/issue | Total arts |
|---------|--------|-------------|------------------|------------|-----------|
| EN 1977-1994 | ~150 | 0 (no conf en Liahona) | ~150 | ~12 | ~1,800 |
| EN 1995-1999 | ~55 | 0 (mayo 1995=regular; sitio parcial) | ~55 | ~15 | ~825 |
| EN 2000-2002 | ~36 | ~6 (jul+ene patron) | ~30 | ~20 | ~600 |
| EN 2003-2020 | ~216 | ~36 | ~180 | ~25 | ~4,500 |
| EN 2021-2026 | ~66 | ~10 | ~56 | ~40 | ~2,240 |
| ES 2000-2002 | ~36 | ~6 | ~30 | ~20 | ~600 |
| ES 2003-2020 | ~216 | ~36 | ~180 | ~25 | ~4,500 |
| ES 2021-2026 | ~66 | ~10 | ~56 | ~40 | ~2,240 |
| **Total** | **~841** | **~104** | **~737** | — | **~17,305** |

> **Nota:** Pre-1995 EN tiene cobertura limitada en el sitio (muchos 404). Pre-2000 ES no esta disponible.
> Muchos issues pre-1995 podrian no tener contenido descargable via API.

Descontando conferencias: **~17,300 articulos unicos** de contenido original.

**Estimacion de archivos:** ~17,300 .txt + ~17,300 .meta.json = **~34,600 archivos**.

Para referencia: el corpus actual tiene ~29,000 archivos. Esto **mas que duplica** el corpus.

### Tiempo estimado de descarga

A 1 segundo/articulo (API): ~17,000 seg = ~4.7 horas.
Indexacion (GPU): ~17,000 chunks × ~0.3 seg = ~1.4 horas vectors + ~3 horas KG.

---

## 5. Deduplicacion con conferencia general

### Regla

Los numeros de conferencia (mes variable segun epoca — ver seccion 3) contienen los discursos **que ya estan en el corpus**.

**Meses de conferencia por epoca:**
- 2000-2002: julio (abril conf) y enero del ano siguiente (octubre conf)
- 2003+: mayo (abril conf) y noviembre (octubre conf)
- Pre-2000: no se detectaron numeros de conferencia en Liahona EN

**Estrategia de deteccion** — al procesar un TOC, detectar si un articulo es un discurso de conferencia:
- **Patron slug:** Los discursos tienen slugs como `11oaks`, `35uchtdorf`, `57nelson` (2 digitos + apellido).
- **Patron seccion:** Agrupados bajo "Saturday Morning Session", "Sunday Afternoon Session", etc.
- **Patron titulo TOC:** Buscar "Report of the Nth Annual/Semiannual General Conference" en el encabezado del numero.
- **Validacion cruzada:** Comparar titulo+autor contra el indice de `corpus/{lang}/general-conference/{YYYYMM}/`.

**Articulos NO-conferencia en numeros de conferencia** (mantener):
- Informe estadistico anual
- Nuevos llamamientos (biografias)
- Church News / Noticias de la Iglesia
- Informes de auditoria

### Contenido parcialmente duplicado

Algunos articulos regulares citan o resumen discursos de conferencia. Esto **no es duplicacion** — es contenido derivado con valor propio (comentario, aplicacion, contexto).

---

## 6. Propuesta de estructura en corpus

```
corpus/{lang}/magazines/liahona/{YYYY}/{MM}/
    {slug}.txt
    {slug}.meta.json
```

### meta.json propuesto

```json
{
  "title": "A Pattern for Unity in Jesus Christ",
  "author": "Russell M. Nelson",
  "author_role": "President of the Church",
  "source": "Liahona",
  "source_url": "https://www.churchofjesuschrist.org/study/liahona/2024/10/03-a-pattern-for-unity-in-jesus-christ",
  "year": 2024,
  "month": 10,
  "section": "Featured Articles",
  "content_type": "leader_message",
  "language": "en",
  "authority": 60,
  "footnotes": ["D&C 38:27", "John 17:21", "..."]
}
```

### Clasificacion de content_type

| Tipo | Descripcion | Ejemplo |
|------|-------------|---------|
| `leader_message` | Mensaje de AG (Primera Presidencia, Apostoles, AG) | "Grateful to Gather" (Nelson) |
| `doctrinal_article` | Articulo doctrinal por autor no-AG | "Accessing God's Power through Covenants" |
| `member_story` | Testimonio / experiencia personal | "Latter-day Saint Voices" |
| `study_guide` | Material de estudio Come Follow Me | "Come, Follow Me" section |
| `historical` | Articulo historico | "The Blessings of 1836..." (Grow) |
| `young_adult` | Contenido para adultos jovenes | "Young Adults" section |
| `news` | Noticias de la Iglesia, llamamientos | "News of the Church" |
| `local_pages` | Paginas regionales | "Africa West", "Caribbean" |

---

## 7. Authority model

| Contenido | Authority | Justificacion |
|-----------|-----------|---------------|
| Mensajes de la Primera Presidencia | 70 | Publicacion oficial, autoria FP |
| Articulos de Apostoles/AG | 65 | Publicacion oficial, autoria AG |
| Articulos doctrinales (otros autores) | 55 | Aprobados por correlacion |
| Come, Follow Me (estudio) | 60 | Material curricular oficial |
| Historicos | 50 | Investigacion aprobada |
| Testimonios de miembros | 40 | Experiencias personales |
| Noticias / llamamientos | 45 | Informativo, no doctrinal |
| Local pages | 30 | Efimero, regional |

**Authority por defecto del contenedor:** 60 (publicacion oficial de la Iglesia).
Authority por articulo se asigna segun `content_type` y `author_role`.

---

## 8. Valor KG

### Entidades nuevas esperadas

- **Autores:** Cientos de autores no-AG que no aparecen en conferencia.
- **Temas contemporaneos:** Salud mental, dudas de fe, redes sociales, roles de genero — temas que la conferencia aborda brevemente pero las revistas desarrollan.
- **Lugares:** "The Church Is Here" serie = descripciones de estacas/misiones especificas.
- **Programas:** CES, FSY, seminario, instituto — mencionados en contexto de aplicacion.

### Relaciones KG unicas

| Relacion | Ejemplo |
|----------|---------|
| `AUTHORED_BY` | Articulo → Autor (no-AG con perfil en meta.json) |
| `COMMENTS_ON` | Articulo Come Follow Me → Pasaje escritural |
| `APPLIES_TO` | Articulo Gospel Solutions → Tema pastoral |
| `PUBLISHED_IN` | Articulo → Liahona {YYYY}/{MM} |

---

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigacion |
|--------|---------|------------|
| Volumen duplica el corpus | Storage, indexacion lenta | Descarga por fases (decadas) |
| Conferencia duplicada | Redundancia, confunde RAG | Filtro de dedup por slug+titulo+autor |
| Rate limiting API | Descargas interrumpidas | Throttle 1 req/seg, retry con backoff |
| Contenido efimero (noticias) | Ruido en busquedas | Excluir `local_pages` y `news` en fase inicial |
| Articulos sin autor claro | meta.json incompleto | Fallback a "Liahona Staff" |
| Cambio formato old vs new | Parsing inconsistente | Dos estrategias de parsing (pre/post 2021) |

---

## 10. Propuesta de fases de descarga

Dado el volumen (~17,000 articulos), se propone descarga **incremental por decadas**:

| Fase | Periodo | Issues est. | Arts est. | Justificacion |
|------|---------|-------------|-----------|---------------|
| **D1** | 2021-2026 (nueva Liahona) | ~66 EN + ~66 ES | ~4,480 | Formato uniforme, mas relevante, prueba de concepto |
| **D2** | 2010-2020 | ~130 EN + ~130 ES | ~6,500 | Liahona moderna, buen overlap con conferencia actual |
| **D3** | 2000-2009 | ~120 EN + ~120 ES | ~4,800 | Era digital temprana |
| **D4** | 1977-1999 (solo EN) | ~200 | ~3,000 | Archivo historico, ES no disponible |

**Recomendacion:** Comenzar con D1 como prueba de concepto. Si el pipeline funciona, D2-D4 son ejecucion mecanica.

---

## 11. Contenido a excluir (no descargar)

| Tipo | Razon |
|------|-------|
| Discursos de conferencia general | Ya en `corpus/{lang}/general-conference/` |
| Informes de auditoria | Sin valor doctrinal |
| Informes estadisticos | Datos numericos sin texto significativo |
| Local pages (fase inicial) | Efimero, bajo valor KG — reconsiderar despues |

---

## 12. Prerequisitos para descarga

- [x] Script `download_liahona.py` basado en `church_scraper.py` — **LISTO**
- [x] Logica de deduplicacion conferencia (slug pattern + session keywords + month detection)
- [x] Clasificador de `content_type` por seccion del TOC (h2.label → content_type mapping)
- [x] Extractor de `author_role` (detecta AG, boost authority a 65)
- [x] Campos meta.json especificos para revistas (section, content_type, year, month)
- [x] Test con 1 numero completo (oct 2024 EN) — 41 articulos descargados, 2 skipped (art/intro)
- [x] Dos estrategias de parsing: h2.label+ul.doc-map (2003+) y fallback nav links (pre-2003)

### Comandos de descarga por fase

```bash
# D1: Nueva Liahona (2021-2026) — prueba de concepto
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_liahona.py --year-from 2021 --year-to 2026 --resume

# D2: 2010-2020
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_liahona.py --year-from 2010 --year-to 2020 --resume

# D3: 2000-2009
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_liahona.py --year-from 2000 --year-to 2009 --resume

# D4: 1977-1999 (solo EN)
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_liahona.py --year-from 1977 --year-to 1999 --lang eng --resume
```

---

## Status: `prepared` — script listo, pendiente ejecucion D1
