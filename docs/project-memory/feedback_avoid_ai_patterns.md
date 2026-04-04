---
name: Evitar patrones reconocibles de IA en textos
description: Lista de patrones léxicos, estructurales y estilísticos que delatan texto generado por IA. Aplicar al escribir artículos y contenido editorial.
type: feedback
---

Evitar patrones reconocibles de escritura por IA en todos los artículos y contenido editorial del proyecto.

**Why:** El usuario detectó el patrón contrastivo "no es X, es Y" en los artículos de la serie. Los lectores familiarizados con IA reconocen estos patrones y pierden confianza en el texto.

**How to apply:** Revisar cada artículo antes de entregarlo contra esta lista. Si aparece un patrón, reformular.

## Patrones léxicos (palabras y frases sobreusadas)

### Inglés
delve, pivotal, robust, leverage, harness, tapestry, realm, beacon, underscore, illuminate, facilitate, bolster, seamless, cutting-edge, landscape, synergy, underpinnings, multifaceted, nuanced, holistic, paradigm, foster, elevate, navigate (figurativo), cornerstone, spearhead, groundbreaking, commendable, noteworthy, meticulous

### Español — muletillas y conectores
además, sin embargo, por lo tanto, es importante señalar/destacar, en resumen, cabe destacar, en este sentido, resulta fundamental, no cabe duda, en última instancia, vale la pena señalar que, en el ámbito de, en este contexto, por consiguiente, de hecho, sin duda, ciertamente, en conclusión, podría decirse

### Español — verbos y adjetivos delatores
profundizar, explorar ("vamos a explorar…"), dinamizar, fomentar, abrazar (figurativo), transformar, facilitar, maximizar, alinear, subrayar, utilizar; dinámico/a, robusto/a, innovador/a, crucial, esencial, sinérgico/a, vibrante, vital, transformador/a, encomiable, ejemplar, invaluable, en constante evolución

### Español — sustantivos abstractos vacíos
innovación, transformación, optimización, integración, implementación, eficiencia, paisaje (calco de "landscape"), reino (calco de "realm")

## Patrones estructurales

1. **Contrastivo "no es X, es Y"**: "No dijo 'necesitamos más actividades'. Dijo que el *patrón* necesita invertirse." — Reformular para que el contraste sea implícito o use otra construcción.
2. **Párrafo rígido**: oración temática → evidencia → resumen. Variar la estructura: empezar con anécdota, pregunta, cita, dato.
3. **Secuencia explícita**: "En primer lugar / En segundo lugar / Finalmente". Usar transiciones orgánicas.
4. **Transiciones excesivamente lógicas**: cada párrafo conectado con "sin embargo", "por lo tanto", "de este modo". Permitir saltos, yuxtaposiciones, silencios.
5. **Construcción "De X a Y"**: "De la firma al diezmo", "Del turno al diálogo" — aceptable como título ocasional, no como muletilla.
6. **Frases participiales iniciales**: "Reconociendo la necesidad de cambio, la Iglesia procedió a..." — IA las usa 2-5x más que humanos.
7. **Hedging sistemático**: "es importante notar", "en términos generales", "desde una perspectiva más amplia" — eliminar o ser directo.
8. **Gerundios excesivos** (calcados del inglés): "analizando los datos, se llegó a…", "siendo importante destacar…", "conteniendo información…". Preferir participio, relativa o subordinada.
9. **Dicotomías artificiales exageradas**: sentencias filosóficas tipo "el problema no es X, sino Y" — el mundo es más matizado.
10. **Uniformidad de longitud de frases**: la IA tiende a ~15 palabras por oración. Los humanos varían entre 5 y 30. Mezclar frases cortas secas con oraciones largas.

## Patrones de tono

1. **Tono uniformemente elevado**: sin variación de registro. Los humanos alternan entre formal e informal, serio y ligero.
2. **Exceso de adjetivos valorativos**: "extraordinario", "profundo", "notable", "significativo" en cada párrafo. Dejar que los hechos hablen.
3. **Falsa humildad epistémica**: "podría argumentarse que", "no es descabellado pensar que" — si lo vas a decir, dilo.
4. **Resumen al final de cada sección**: la IA tiende a cerrar cada sección repitiendo lo que acaba de decir. Cortar el resumen; confiar en el lector.

## Métricas de AI detectors (qué miden GPTZero, Originality, etc.)

1. **Perplexity** (perplejidad): mide cuán predecible es el texto para un modelo de lenguaje. Texto IA = baja perplejidad (palabras esperables). Texto humano = alta (>85). Para subir perplejidad: vocabulario variado, elecciones léxicas inesperadas, no usar siempre la palabra "obvia".
2. **Burstiness** (ráfaga): mide la variación en longitud y estilo de frases. IA = frases uniformes (~15 palabras). Humano = mezcla de frases de 4 y de 35 palabras. Para subir burstiness: alternar frases cortas brutales con desarrollos largos.
3. **Consistencia de estilo**: la IA mantiene el mismo registro todo el texto. Los humanos varían — a veces coloquiales, a veces formales.

## Postura de Google sobre contenido IA (SEO)

- **Google no penaliza IA per se**, penaliza contenido inútil. Evaluación por E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness).
- **Sí penaliza**: producción masiva sin revisión, reescritura sin valor añadido, ausencia de perspectiva original, manipulación de rankings.
- **No penaliza**: contenido IA con revisión humana, experiencia real, valor diferencial, perspectiva propia.
- **El 86.5% de páginas top** usan asistencia IA (Ahrefs 2026) — la clave es la calidad, no el método.
- **Para nuestros artículos**: la experiencia real (corpus propio, análisis original de escrituras) + voz editorial reconocible + citas verificadas = E-E-A-T fuerte.

## Prueba rápida (5 puntos + 3 pasadas de iaísmos)

Antes de entregar un artículo, buscar:
- ¿Hay más de 2 instancias de "no es X, es Y"?
- ¿Cada párrafo empieza con oración temática?
- ¿Las transiciones son todas causales/adversativas?
- ¿El tono es uniforme de principio a fin?
- ¿Hay palabras de la lista léxica?

Si la respuesta es sí a 3+, reescribir las secciones afectadas.

### Tres pasadas obligatorias de iaísmos (tiempos verbales)
1. **Grep de verbos en `-ía/-aba`** — listar todas las instancias en texto editorial
2. **Grep de `había + participio`** — listar pluscuamperfectos
3. **Densidad por párrafo** (sin contar citas escriturales/proféticas) — si un párrafo tiene 3+ imperfectos editoriales, reescribir

### Pasada de léxico delator
Grep de las palabras de las listas léxicas españolas (muletillas, verbos delatores, sustantivos abstractos vacíos). Cualquier coincidencia en texto editorial → reformular.

### Pasada de burstiness
Contar palabras por oración en 3-4 párrafos muestra. Si la variación es baja (todas entre 12-18 palabras), reescribir mezclando frases de 4-6 palabras con oraciones de 25+.
