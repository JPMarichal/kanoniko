# Enfoques Profesionales Anti-IA

## Idea clave

Una solución profesional anti-IA no debe prometer certeza absoluta. Debe trabajar con **señales múltiples**, **explicabilidad** y **revisión humana**.

## Qué mostró la investigación

### 1. Detectores comerciales serios no usan una sola métrica

La explicación pública de GPTZero describe un sistema multicapa que empezó con:

- **Perplexity**: predictibilidad del texto.
- **Burstiness**: variación del ritmo y longitud de frases.
- **Semantic coherence / embeddings / classifiers**: coherencia semántica y clasificación aprendida.
- **Sentence-level classification**: análisis por oración, no solo por documento.
- **Context + human review**: el propio proveedor insiste en no usar el detector como juez único.

Implicación: una herramienta profesional en Alejandría no debe producir solo un score global. Debe producir explicaciones por dimensión y por tramo.

### 1.1. También importan los límites operativos declarados por detectores serios

La investigación pública sobre detectores comerciales y su uso responsable deja varios límites prácticos que deben volverse reglas internas:

- **documentos cortos**: menos contexto, menos señal útil
- **documentos mezclados**: texto parcialmente humano y parcialmente IA
- **documentos editados o humanizados**: la señal superficial puede degradarse sin desaparecer
- **sesgo por idioma**: muchos detectores nacieron en inglés; el español y los textos bilingües requieren más cautela
- **falsos positivos y falsos negativos**: inevitables; no usar un solo veredicto como prueba final

Implicación: el sistema de Alejandría debe marcar incertidumbre, no esconderla.

### 1.2. Distinguir detección IA, plagio y procedencia

Otra lección importante de la investigación: detectar origen probable de IA no equivale a detectar plagio ni a probar autoría.

- **Detección IA**: cómo suena o cómo puntúa el texto
- **Plagio**: de dónde salió el texto
- **Procedencia**: cómo se produjo el documento, con qué historial y qué mezcla de intervención humana tuvo

Implicación: una herramienta profesional debe separar esas tres preguntas y no mezclarlas en una sola etiqueta.

### 2. Hay código open source útil

#### DetectGPT

Fuente revisada:

- Paper: `https://arxiv.org/abs/2301.11305`
- Repo: `https://github.com/eric-mitchell/detect-gpt`

Qué aporta:

- Método **zero-shot**.
- No depende de entrenar un clasificador nuevo para cada caso.
- Usa **log-probabilities** del modelo y **perturbaciones** del texto generadas con otro modelo (por ejemplo T5).
- Señal principal: los textos generados por un LLM tienden a caer en regiones de **curvatura negativa** de la función de probabilidad del modelo.

Piezas reutilizables observadas en el repo:

- perturbación por enmascarado y relleno
- scoring por log-likelihood
- comparación original vs perturbado
- baselines de rank, log-rank, entropy
- evaluación supervisada opcional

Cuándo usar su idea:

- para investigación y scoring experimental
- para comparar variantes de un mismo texto
- para una segunda capa técnica detrás del checklist editorial

Limitaciones:

- costoso en cómputo
- sensible al modelo usado para puntuar
- no sustituye evaluación humana
- menos apropiado como primer filtro universal que como segunda capa profunda

#### GLTR

Fuente revisada:

- Repo: `https://github.com/HendrikStrobelt/detecting-fake-text`
- Paper: `https://arxiv.org/abs/1906.04043`

Qué aporta:

- enfoque **interpretativo/visual**
- muestra cuán probables eran los tokens elegidos bajo un modelo dado
- útil para detectar texto “demasiado probable” o con elecciones muy conservadoras
- tiene backend extensible y frontend ya armado

Cuándo usar su idea:

- para inspección humana asistida
- para resaltar tramos sospechosos en vez de solo dar un score
- para una UI editorial donde el revisor vea por qué un pasaje suena a IA

Limitaciones:

- es una ayuda de inspección, no una solución completa
- su base histórica está centrada en modelos más antiguos
- necesita reinterpretación moderna si se adapta a modelos y flujos actuales

### 3. Qué hacer con watermarks y soluciones “mágicas”

La investigación también muestra que los watermarks son una idea útil, pero no una base suficiente hoy:

- pueden perderse con edición, traducción o parafraseo
- no son estándar interoperable entre proveedores
- no resuelven documentos ya existentes ni corpus heterogéneos

Implicación: en Alejandría no se debe diseñar la estrategia anti-IA alrededor de watermarking.

## Arquitectura recomendada para una herramienta anti-IA de nivel profesional

### Capa 1. Reglas editoriales explicables

Entrada: markdown o texto.

Señales:

- muletillas
- conectores demasiado regulares
- contraste “no es X, es Y”
- longitud media y desviación de oraciones
- densidad de verbos imperfectos / hedging
- cierres-resumen por sección

Salida:

- hallazgos concretos por línea/párrafo
- sugerencia de reescritura

### Capa 2. Métricas estadísticas

Señales mínimas:

- perplexity aproximada
- burstiness
- rank/log-rank de tokens
- repetición léxica y n-gramas
- distribución irregular o demasiado uniforme por oración

Salida:

- score por documento
- score por párrafo
- heatmap o ranking de pasajes más sospechosos
- incertidumbre declarada cuando el texto sea corto, mixto o muy editado

### Capa 3. Scoring por perturbación

Inspiración: DetectGPT.

Flujo:

1. enmascarar spans
2. regenerar perturbaciones
3. medir log-likelihood del original y los perturbados
4. comparar estabilidad/curvatura

Uso ideal:

- textos largos
- revisión previa a publicación
- auditoría técnica, no uso casual en cada párrafo

### Capa 4. Procedencia y autoría operativa

Más valiosa que cualquier detector aislado.

Señales:

- historial de versiones
- velocidad y patrón de edición
- consistencia con textos previos del autor
- presencia de citas válidas y fuentes reales
- mezcla humano+IA

Esto reduce falsos positivos y hace el sistema útil en el mundo real.

### Capa 5. Gobernanza de uso

Una herramienta profesional también necesita reglas de uso:

1. no emitir veredicto absoluto con una sola fuente
2. permitir contradicción entre señales
3. mostrar incertidumbre explícita
4. exigir revisión humana antes de una conclusión editorial fuerte
5. registrar por qué un texto fue marcado y qué evidencia concreta lo sostiene

## Recomendación para Alejandría

La mejor herramienta para este repo no es un “detector universal de IA”.

Debe ser un **auditor editorial anti-IA** con dos modos:

1. **Modo rápido**
   - reglas editoriales
   - burstiness básica
   - reporte explicable

2. **Modo profundo**
   - análisis por perturbación tipo DetectGPT
   - revisión de procedencia
   - comparación contra muestras del autor
   - evaluación por tramo y no solo por documento

Además, el protocolo debe ser **mandatorio sobre todo producto editorial de `prods/`** y no limitarse a artículos.

Aplicación mínima:

1. artículos
2. dossiers
3. Formas T
4. cualquier pieza narrativa, doctrinal o pedagógica con voz autoral

## Qué no prometer

No prometer:

- detección perfecta
- certeza forense absoluta
- inmunidad frente a paraphrasing/humanizers

Sí prometer:

- reducción de huella IA visible
- mejor explicabilidad editorial
- priorización de pasajes a revisar
- integración con juicio humano
- protocolo reutilizable y obligatorio sobre productos editoriales

## Código existente que conviene estudiar primero

1. `eric-mitchell/detect-gpt`
2. `HendrikStrobelt/detecting-fake-text` (GLTR)

## Conclusión operativa

Una herramienta verdaderamente profesional anti-IA combina:

- heurísticas editoriales del dominio
- métricas estadísticas
- perturbation scoring
- procedencia del documento
- revisión humana final

Y, en el caso de Alejandría, añade una exigencia más:

- uso obligatorio en todo producto editorial antes de darlo por terminado

Sin esa combinación, lo que se obtiene no es una herramienta profesional sino un detector frágil o un simple estilizador.
