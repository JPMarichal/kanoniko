# Fuentes para bios de personajes de DyC

Este archivo documenta las fuentes ya localizadas en el corpus que pueden servir para construir un "quién es quién" de Doctrina y Convenios. La idea es distinguir entre:

- fuentes biográficas directas
- fuentes tipo diccionario / enciclopedia
- fuentes auxiliares para validación y cruce
- fuentes citadas pero no incorporadas todavía como obra autónoma

## 0. Clasificación funcional de fuentes

| grupo | familias principales en el corpus | estatus recomendado | uso principal |
|---|---|---|---|
| oficiales | `saints/vol-1..4`, `revelaciones-en-contexto-mcbride-goldberg-es`, `doctrina-y-convenios-manual-del-alumno`, `seminary/doctrine-and-covenants-teacher`, `church-history-topics`, `guide-to-scriptures` | prioritario | contexto por sección, cronología, normalización doctrinal y lectura correlacionada |
| académicas_lds | `lds-biographical-encyclopedia-vol-1..4`, `church-history-and-modern-revelation-vol-1..4`, `joseph-smith-the-prophet-the-man-tate`, `joseph-smiths-kirtland-anderson`, `hyrum-smith-patriarch-corbett`, `autobiography-parley-p-pratt`, artículos de `encyclopedia-of-mormonism` | prioritario con cruce | síntesis biográfica, profundidad histórica y perfiles por persona |
| auxiliares | `general-authorities/` (GAPages), `history-of-the-church-*`, `history-joseph-smith-his-mother`, `they-knew-the-prophet-andrus`, `book-of-john-whitmer`, `reynolds-cahoon-stalwart-sons` | apoyo y validación | arranque rápido, color histórico, cronología y contraste de datos |
| citadas_no_autonomas | referencias dispersas a `Mormon Doctrine` y otras obras aún no incorporadas como corpus dedicado | secundaria | terminología, contraste doctrinal y pistas para futuras incorporaciones |

Lectura sugerida:

- empezar por `oficiales` cuando el anclaje principal sea una sección concreta de DyC
- pasar a `académicas_lds` cuando ya se tenga identificado el personaje y haga falta profundidad
- usar `auxiliares` para resolver huecos rápidos, cronologías o validaciones cruzadas

## 1. Fuentes biográficas directas ya incorporadas

### 1.1 Obras sobre José Smith y su círculo inmediato

- `corpus/en/biographies/history-joseph-smith-his-mother/`
  - Obra: *History of Joseph Smith by His Mother*
  - Evidencia: `01-introduction.meta.json`
  - Valor: fuente fundacional para José Smith, su familia, Palmyra, primeras visiones, traducción, persecución y entorno temprano de la Restauración.
  - Observación: muy útil para personas de DyC de la etapa 1820-1844.

- `corpus/en/biographies/joseph-smith-prophet-of-restoration-hartshorn/`
  - Obra: *Joseph Smith, Prophet of the Restoration*
  - Evidencia: `01-preface.meta.json`
  - Valor: biografía moderna sintética de José Smith.

- `corpus/es/biographies/jose-smith-profeta-y-vidente/`
  - Obra: *José Smith, el profeta y vidente*
  - Evidencia: `01-jose-smith.meta.json`
  - Valor: fuente ya en español para perfilar a José Smith y su entorno.

- `corpus/en/biographies/they-knew-the-prophet-andrus/`
  - Obra: *They Knew the Prophet*
  - Evidencia: `01-preface.meta.json`
  - Valor: testimonios y recuerdos sobre José Smith por personas que lo conocieron.
  - Uso recomendado: complemento narrativo y de color histórico, no fuente única para datos duros.

- `corpus/en/biographies/joseph-smiths-kirtland-anderson/`
  - Obra: *Joseph Smith's Kirtland, Eyewitness Accounts*
  - Evidencia: `01-preface.meta.json`
  - Valor: fuerte para personajes vinculados al período Kirtland de DyC.

### 1.2 Obras sobre familiares y figuras centrales de DyC

- `corpus/en/biographies/father-of-the-prophet-joseph-smith-sr/`
  - Obra: *Father of the Prophet, Stories and Insights from the Life of Joseph Smith, Sr.*
  - Evidencia: `01-preface.meta.json`
  - Valor: José Smith Sr., familia Smith, patriarcado temprano.

- `corpus/en/biographies/hyrum-smith-patriarch-corbett/`
  - Obra: *Hyrum Smith, Patriarch*
  - Evidencia: `01-introduction.meta.json`
  - Valor: una de las fuentes más directas para Hyrum Smith.

- `corpus/en/biographies/autobiography-parley-p-pratt/`
  - Obra: *The Autobiography of Parley Parker Pratt*
  - Evidencia: `02-the-autobiography-of-parley-parker-pratt.meta.json`
  - Valor: fuente primaria mayor para Parley P. Pratt y el primer apostolado restaurado.

- `corpus/en/biographies/book-of-john-whitmer/`
  - Obra: *Book of John Whitmer*
  - Evidencia: `01-chapter-1.meta.json`
  - Valor: registro histórico temprano de gran utilidad para validar contexto y cronología de personajes del primer período.

- `corpus/en/biographies/reynolds-cahoon-stalwart-sons/`
  - Obra: *Reynolds Cahoon and His Stalwart Sons*
  - Evidencia: `reynolds-cahoon-stalwart-sons.meta.json`
  - Valor: útil para perfiles de figuras secundarias del tejido de DyC.

### 1.3 Fuentes directas sobre DyC e historia de la Iglesia

#### Santos / Saints

- `corpus/es/manuals/saints/vol-1/`
- `corpus/es/manuals/saints/vol-2/`
- `corpus/es/manuals/saints/vol-3/`
- `corpus/es/manuals/saints/vol-4/`

Evidencia:

- `corpus/es/manuals/saints/vol-4/title-page.meta.json`

Valor:

- Sí, `Santos` sirve y está ya incorporado en el corpus.
- Es historia narrativa oficial de la Iglesia, muy útil para contexto, cronología, redes de personas y secuencias de acontecimientos.
- No sustituye una entrada biográfica tipo diccionario, pero sí ayuda mucho a construir perfiles narrativos de los personajes que aparecen en DyC.

Uso recomendado:

- Usarlo para reconstruir contexto histórico y relaciones entre personajes.
- Cruzarlo con el pasaje de DyC, luego con una fuente más puntual cuando se necesiten datos biográficos compactos.

#### Revelaciones en contexto

- `corpus/es/books/revelaciones-en-contexto-mcbride-goldberg-es/`

Evidencia:

- `corpus/es/books/revelaciones-en-contexto-mcbride-goldberg-es/92-d-y-c-1.meta.json`

Valor:

- Es una de las fuentes más directamente útiles para este proyecto.
- Está organizada precisamente alrededor de las secciones de DyC y sus historias de trasfondo.
- Sirve para identificar quiénes estaban involucrados, qué problema motivó la revelación y qué relaciones personales o institucionales rodean cada sección.

Uso recomendado:

- Consultar primero la entrada asociada a la sección de DyC.
- Extraer nombres, roles, conflicto o circunstancia revelatoria.
- Después pasar a biografías o enciclopedias para consolidar el perfil personal.

#### Doctrina y Convenios - Manual del alumno

- `corpus/es/manuals/doctrina-y-convenios-manual-del-alumno/`

Evidencia:

- `corpus/es/manuals/doctrina-y-convenios-manual-del-alumno/117-introduccion-y-cronologia.meta.json`

Valor:

- Sí hay una fuente directa sobre DyC de tipo manual de estudio.
- Tiene cronología, antecedentes históricos adicionales y comentarios por bloques y secciones.
- Es especialmente útil para una primera capa correlacionada y ordenada por sección.

Observación:

- Esto resuelve en buena medida la necesidad de “manual de instituto” para DyC, aunque el corpus también contiene manuales modernos de seminario y materiales relacionados.

#### Manual de seminario de Doctrina y Convenios

- `corpus/es/manuals/seminary/doctrine-and-covenants-teacher/`

Evidencia:

- `corpus/es/manuals/seminary/doctrine-and-covenants-teacher/430-doctrine-and-covenants-124-overview.meta.json`

Valor:

- Añade una capa moderna, web-hosted y oficial con reseñas, objetivos y encuadre pedagógico por sección.
- Puede complementar al manual del alumno cuando convenga una lectura más reciente o resumida.

#### Church History and Modern Revelation

- `corpus/en/history/church-history-and-modern-revelation-vol-1/`
- `corpus/en/history/church-history-and-modern-revelation-vol-2/`
- `corpus/en/history/church-history-and-modern-revelation-vol-3/`
- `corpus/en/history/church-history-and-modern-revelation-vol-4/`

Evidencia:

- `corpus/en/history/church-history-and-modern-revelation-vol-4/14-the-nauvoo-templethe-nauvoo-housethe-calling-of-hyrum-smith.meta.json`

Valor:

- Es otra familia muy directamente relevante para DyC.
- Combina historia de la Iglesia y revelación moderna, con capítulos ligados a acontecimientos, doctrinas y personajes del período restauracionista.
- Puede ser especialmente útil para enlazar personas con eventos y desarrollos doctrinales alrededor de una revelación.

#### History of the Church

- `corpus/en/manuals/history-of-the-church-of-jesus-christ-of-latter-day-saints-volume-1-jr-jose/`
- `corpus/en/manuals/history-of-the-church-of-jesus-christ-of-latter-day-saints-volume-6-b-h-rob/`
- `corpus/en/reference/history-of-the-church-of-jesus-christ-of-latter-day-saints/`

Evidencia:

- `corpus/en/manuals/history-of-the-church-of-jesus-christ-of-latter-day-saints-volume-1-jr-jose/02-history-of-the-church-of-jesus-christ-of-latter-day-saints.meta.json`
- `corpus/en/reference/history-of-the-church-of-jesus-christ-of-latter-day-saints/history-of-the-church-of-jesus-christ-of-latter-day-saints.meta.json`

Valor:

- Aporta historia narrativa extensa, citas y marco documental para el período de José Smith.
- Es útil para profundizar después de una primera identificación del personaje.
- Conviene usarlo con más cuidado que las fuentes más modernas y mejor delimitadas, porque en el corpus aparece en variantes de atribución y empaquetado editorial.

#### Church History Topics

- `corpus/en/manuals/church-history-topics/`
- `corpus/es/manuals/church-history-topics/`

Evidencia:

- `corpus/en/manuals/church-history-topics/daily-life-of-first-generation-latter-day-saints.meta.json`

Valor:

- No es una biografía por persona, pero sí una capa oficial temática muy valiosa.
- Sirve para contextualizar oficios, prácticas, instituciones, condiciones de vida y problemas históricos del mundo de DyC.
- Útil cuando una biografía necesita explicar el entorno, no sólo los datos del individuo.

## 2. Fuentes tipo diccionario / enciclopedia

### 2.1 LDS Biographical Encyclopedia

- `corpus/en/biographies/lds-biographical-encyclopedia-vol-1/`
- `corpus/en/biographies/lds-biographical-encyclopedia-vol-2/`
- `corpus/en/biographies/lds-biographical-encyclopedia-vol-3/`
- `corpus/en/biographies/lds-biographical-encyclopedia-vol-4/`

Evidencia:

- `corpus/en/biographies/lds-biographical-encyclopedia-vol-1/01-preface.meta.json`

Valor:

- Es la fuente más cercana en el corpus a un verdadero "who's who" o diccionario biográfico.
- Tiene entradas por persona.
- Es especialmente útil para líderes y figuras del siglo XIX ligadas al universo de DyC.

Uso recomendado:

- Primera consulta rápida por nombre.
- Luego validación con biografías más amplias o fuentes primarias.

### 2.2 GAPages / Grandpa Bill's General Authority Pages

Ubicación:

- `corpus/en/biographies/general-authorities/`

Evidencia:

- múltiples `.meta.json` con `source = "Grandpa Bill's General Authority Pages"`
- ejemplo: `corpus/en/biographies/general-authorities/amasa-m-lyman.meta.json`
- ejemplo: `corpus/en/biographies/general-authorities/david-w-patten.meta.json`

Valor:

- Muy útil para lookup rápido de datos vitales, llamamientos y cronologías resumidas.
- En varios casos cubre nombres de DyC de forma inmediata, sin tener que recorrer libros completos.

Limitación:

- Los propios metadatos advierten que es una compilación comunitaria recuperada de Wayback.
- Debe cruzarse con fuentes de mayor rigor.

Conclusión:

- Sí, GAPages puede servir.
- Debe tratarse como fuente auxiliar de arranque, no como autoridad final.

### 2.3 Encyclopedia of Mormonism

Ubicación observada en el corpus:

- `corpus/en/reference/abraham-encyclopedia-of-mormonism/`
- `corpus/en/reference/abrahamic-covenant-the-encyclopedia-of-mormonism/`
- `corpus/en/reference/amulek-the-encyclopedia-of-mormonism/`
- `corpus/en/reference/book-of-remembrance-the-encyclopedia-of-mormonism/`
- `corpus/en/reference/covenant-israel-latter-day-the-encyclopedia-of-mormonism/`
- `corpus/en/reference/ephraim-the-encyclopedia-of-mormonism/`
- `corpus/en/reference/evangelists-the-encyclopedia-of-mormonism/`
- `corpus/en/reference/freemasonry-and-the-temple-the-encyclopedia-of-mormonism/`
- `corpus/en/reference/gathering-the-encyclopedia-of-mormonism/`
- `corpus/en/reference/gospel-of-abraham-the-encyclopedia-of-mormonism/`
- `corpus/en/reference/ishmael-the-encyclopedia-of-mormonism/`

Evidencia:

- `corpus/en/reference/abraham-encyclopedia-of-mormonism/abraham-encyclopedia-of-mormonism.meta.json`

Valor:

- Sí tenemos fuentes tipo diccionario / enciclopedia.
- En el estado actual del corpus, la *Encyclopedia of Mormonism* aparece como artículos individuales, no como una obra navegable unificada.
- Aun así, esos artículos pueden ser muy útiles cuando existan entradas por persona o concepto conectado con DyC.

Uso recomendado:

- Buscar por nombre exacto del personaje.
- Si existe artículo dedicado, usarlo como resumen de referencia.
- Si no existe, usar artículos temáticos relacionados para contexto doctrinal e histórico.

## 3. Fuentes auxiliares de cruce y validación

### 3.1 Guía para el Estudio de las Escrituras / Guide to the Scriptures

Ubicación:

- `corpus/en/study-aids/guide-to-scriptures/`
- `corpus/es/study-aids/guide-to-scriptures/`

Evidencia:

- `corpus/en/study-aids/guide-to-scriptures/doctrine-and-covenants.meta.json`
- `corpus/es/study-aids/guide-to-scriptures/doctrine-and-covenants.meta.json`

Valor:

- La GEE no es biográfica en sentido estricto, pero sí sirve para:
  - confirmar nombres normalizados
  - detectar alias y variantes
  - enlazar personas con conceptos, lugares, oficios y pasajes
  - cruzar temas doctrinales asociados a un personaje

Uso recomendado:

- Cruzar cada personaje con su entrada GEE, si existe.
- Usar GEE para normalizar nombres en español e inglés.
- Usar GEE como puente entre biografía y pasajes canónicos.

### 3.2 Metadatos y notas de las escrituras

Ubicación principal:

- `corpus/en/scriptures/dc/sections/`
- `corpus/en/scriptures/dc/official-declarations/`

Valor:

- Encabezados, resúmenes y notas editoriales ayudan a identificar personas asociadas a cada sección.
- Útiles para enlazar una bio con las secciones DyC donde un personaje aparece o actúa.

## 4. Sobre Mormon Doctrine

Estado actual en el corpus:

- No encontré una incorporación autónoma de *Mormon Doctrine* como libro completo en el corpus.
- Sí aparece citado muchas veces en otros libros, manuales, discursos y referencias.

Evidencia representativa:

- `corpus/es/reference/relatos-de-doctrina-y-convenios/02-fuentes-de-informacion.txt`
- múltiples citas dispersas en `corpus/en/books/**`, `corpus/es/books/**`, `corpus/en/manuals/**`, `corpus/es/manuals/**`

Evaluación:

- Puede aportar definiciones, clasificaciones doctrinales y a veces notas interpretativas sobre personajes o cargos.
- No debe considerarse, al menos con la evidencia actual del corpus, una fuente biográfica principal.
- Su rol más natural aquí es doctrinal / terminológico, no de diccionario de personajes.

Conclusión:

- Tratar *Mormon Doctrine* como fuente secundaria citada.
- Si en el futuro se incorpora la obra completa, reevaluar si conviene usarla para mini-perfiles o glosario doctrinal asociado a personajes.

## 5. Priorización sugerida para el proyecto DyC

Orden sugerido de uso por personaje:

1. `lds-biographical-encyclopedia-vol-1..4`
2. `general-authorities/` (GAPages), solo como arranque rápido
3. `revelaciones-en-contexto-mcbride-goldberg-es`
4. `doctrina-y-convenios-manual-del-alumno`
5. `saints/vol-1..4`
6. biografía monográfica específica si existe
7. `history-joseph-smith-his-mother`, `they-knew-the-prophet`, `joseph-smiths-kirtland`, `book-of-john-whitmer` para contexto primario
8. `church-history-and-modern-revelation-vol-1..4` y `history-of-the-church-*` para profundización histórica
9. `guide-to-scriptures/` para alias, normalización y cruces temáticos
10. pasajes y encabezados de DyC para aterrizar la bio en el texto canónico

## 6. Estrategia de cruce propuesta

Para cada nombre de `prods/dyc_bios/namelist.md`:

1. Buscar entrada exacta o aproximada en `lds-biographical-encyclopedia-vol-*`.
2. Buscar ficha en `corpus/en/biographies/general-authorities/`.
3. Buscar biografía monográfica dedicada en `corpus/en/biographies/` o `corpus/es/biographies/`.
4. Cruzar con GEE / Guide to the Scriptures.
5. Confirmar secciones y pasajes en `namelist_with_passages.md`.
6. Marcar nivel de confianza de la bio final:
   - alto: biografía dedicada o fuente primaria fuerte
   - medio: entrada enciclopédica + GEE + pasajes
   - bajo: GAPages + pasajes + validación mínima

## 7. Conclusión operativa

Sí, el corpus ya contiene material suficiente para arrancar una base seria de bios de personajes de DyC.

Las piezas más importantes son:

- `lds-biographical-encyclopedia-vol-1..4`
- `general-authorities/` (GAPages)
- `saints/vol-1..4`
- `revelaciones-en-contexto-mcbride-goldberg-es`
- `doctrina-y-convenios-manual-del-alumno`
- biografías monográficas de José, Hyrum, Joseph Smith Sr. y otros actores cercanos
- `church-history-and-modern-revelation-vol-1..4`
- `guide-to-scriptures/` como capa de normalización y cruce
- artículos sueltos de *Encyclopedia of Mormonism* como apoyo de referencia

El punto débil actual no es la ausencia total de fuentes, sino la dispersión: están repartidas entre biografías, referencias, ayudas de estudio y fuentes citadas. Este archivo busca precisamente concentrar ese mapa.