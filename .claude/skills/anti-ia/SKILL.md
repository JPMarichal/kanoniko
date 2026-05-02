---
name: anti-ia
description: Revisa, endurece o diseña contenido y workflows para evitar patrones reconocibles de texto generado por IA. Usar cuando el usuario pida "anti-ia", "humaniza este texto", "suena a IA", "evita patrones de IA", "haz una pasada anti-AI", o cuando quiera diseñar una herramienta profesional contra texto IA o IA-humanizada.
---

# Skill: Anti-IA

Este skill define el protocolo anti-IA editorial del repo.

Usa este skill para dos clases de trabajo:

1. **Revisión editorial anti-IA**: detectar y corregir patrones léxicos, estructurales y rítmicos que delatan texto generado con IA.
2. **Diseño de herramienta/proceso profesional**: cuando el usuario quiera crear un sistema más serio que un simple checklist estilístico.

## Carácter mandatorio

La pasada anti-IA es **obligatoria para todo producto editorial en `prods/`**.

Eso incluye, como mínimo:

1. artículos
2. dossiers
3. Formas T
4. cualquier otro producto narrativo, doctrinal, biográfico o pedagógico que exponga voz editorial

Ningún producto debe darse por terminado solo porque esté doctrinalmente correcto o bien citado. También debe pasar revisión anti-IA.

## Lecturas iniciales obligatorias

1. Leer `docs/project-memory/feedback_avoid_ai_patterns.md`.
2. Leer `references/anti-ia-vocabulary-tiered.md` (tabla de 96 reemplazos por 3 tiers).
3. Leer `references/anti-ia-patterns-catalog.md` (36 categorías con ejemplos).
4. Si el texto es un artículo, leer también `.claude/skills/articulo/SKILL.md`.
5. Si el texto es un dossier, leer también `.claude/skills/dossier/SKILL.md`.
6. Si el texto es una Forma T, leer también `.claude/skills/forma-t/SKILL.md`.

## Principio central

Una solución anti-IA profesional **no** se basa en un solo detector ni en una sola heurística.

Debe combinar tres capas:

1. **Señales editoriales**: muletillas, contrastes artificiales, rigidez de párrafos, tono plano, burstiness baja.
2. **Señales estadísticas/model-based**: perplexity, burstiness, rank/log-rank, perturbation scoring, clasificadores supervisados.
3. **Señales de procedencia**: historial de escritura, borradores, patrones del autor, validación de fuentes, mezcla humano+IA.

En la práctica, este skill debe operar como un **auditor multicapa y explicable**, no como un detector oracular.

## Dos Modos de Operación

Este skill opera en dos modos distintos según el pedido del usuario.

### Modo Detect (Auditoría sin reescritura)

Activar cuando el usuario dice: "detecta", "audita", "flag only", "audit only", "just flag", "scan", "revisa sin cambiar", "qué problemas hay"

**Proceso:**
1. Escaneo de Tier 1: listar todas las instancias con línea/cita exacta
2. Escaneo de Tier 2: marcar clusters (2+ instancias en mismo párrafo/sección)
3. Escaneo de Tier 3: calcular densidad por párrafo (3+ instancias)
4. Aplicar las 36 categorías de patrones
5. Métricas estructurales: burstiness proxy, uniformidad de frases

**Entregable obligatorio (2 secciones):**
1. **Issues found** — tabla con: categoría, texto citado, tier (1/2/3), severidad (P0/P1/P2)
2. **Assessment** — qué flags son problemas claros vs. intencionales/contextualmente efectivos

### Modo Rewrite (Reescritura completa con dos pasadas)

Activar cuando el usuario dice: "humaniza", "reescribe", "corrige", "limpia", "clean up", "remove AI-isms", "make this sound human", "endurece"

**Proceso de dos pasadas:**

**Primera pasada:**
1. Aplicar reemplazos Tier 1 (24 patrones) — siempre reemplazar
2. Aplicar reemplazos Tier 2 (42 patrones) — si hay clusters
3. Aplicar correcciones Tier 3 (30 patrones) — si densidad >3
4. Corregir las 36 categorías de patrones
5. Variar ritmo: mezclar frases cortas (4-6 palabras) con largas (25+)
6. Eliminar hedging sistemático
7. Anclar abstractos con datos concretos

**Segunda pasada (rechequeo):**
1. Releer el rewrite completo
2. Detectar patrones que sobrevivieron ("supervivientes")
3. Buscar nuevos problemas introducidos
4. Verificar que el texto sigue sonando al autor
5. Validar precisión doctrinal y citas FCD intactas

**Entregable obligatorio (4 secciones):**
1. **Issues found** — cada patrón identificado en primera pasada, con texto citado
2. **Rewritten version** — texto limpio con todos los patrones corregidos
3. **What changed** — resumen de cambios principales por categoría/tier
4. **Second-pass audit** — hallazgos de la segunda pasada (supervivientes + nuevos problemas)

## Caso B: Diseño de herramienta/proceso profesional

Diseñar como pipeline, no como detector único.

Entregables mínimos:

1. **Objetivo**: detección, reducción de huella IA, auditoría editorial, o investigación.
2. **Entrada**: texto suelto, markdown, lote de artículos, comparación entre versiones, historial de edición.
3. **Capas del sistema**:
   - reglas estilísticas
   - métricas estadísticas
   - comparación con muestras del autor
   - procedencia y validación documental
4. **Salida explicable**:
   - score por dimensión
   - hallazgos concretos
   - pasajes sospechosos
   - acciones sugeridas
   - tramos por oración o párrafo cuando sea posible
5. **Política de uso**:
   - nunca declarar “IA” como hecho absoluto
   - tratar resultados como evidencia probabilística
   - exigir revisión humana

## Caso C: Productos editoriales en `prods/` (mandatorio)

Aplicar este skill aunque el usuario no diga explícitamente “anti-IA”, cuando la tarea implique:

1. crear
2. revisar
3. ampliar
4. endurecer
5. preparar para publicación

de cualquier producto con voz editorial.

En esos casos, la revisión anti-IA no es opcional ni “nice to have”; forma parte de la Definition of Done.

## Sistema de Tres Tiers de Vocabulario

Basado en `references/anti-ia-vocabulary-tiered.md`:

### Tier 1 — Reemplazar Siempre (24 patrones)
Muletillas conectivas, aperturas chatbot, cierres genéricos:
- "en este sentido", "cabe destacar que", "es importante señalar"
- "sin lugar a dudas", "en última instancia", "podría decirse que"
- "Ciertamente!", "Feel free to reach out", "In conclusion"

### Tier 2 — Flaggear en Clusters (42 patrones)
Cuando aparecen 2+ veces en mismo párrafo:
- Verbos corporativos: profundizar, dinamizar, facilitar, maximizar
- Adjetivos promocionales: robusto, innovador, vibrante, transformador
- Sustantivos abstractos: sinergia, paradigma, optimización
- Calcos del inglés: paisaje (landscape), reino (realm)

### Tier 3 — Flaggear en Alta Densidad (30 patrones)
Problema cuando hay 3+ instancias por párrafo:
- Ciclo de sinónimos cíclicos
- Construcciones "No es X, es Y" múltiples
- Secuencias explícitas numeradas
- Transiciones causales excesivas
- Gerundios acumulados

## Las 36 Categorías de Patrones

Basado en `references/anti-ia-patterns-catalog.md`. Cada categoría tiene severidad P0/P1/P2:

| # | Categoría | Sev | Ejemplo delator |
|---|-----------|-----|-----------------|
| 1 | Aperturas Chatbot | P0 | "Ciertamente!", "Por supuesto" |
| 2 | Lenguaje Promocional | P1 | "vibrante", "próspero" sin datos |
| 3 | Inflación de Significado | P1 | "momento decisivo" |
| 4 | Evitación de Copulativas | P1 | "sirve como" → "es" |
| 5 | Emojis en Listas Formales | P0 | 🚀 💡 ✅ en contenido formal |
| 6 | Atribuciones Vagas | P1 | "Los expertos creen..." |
| 7 | Listas con Headers Inline | P1 | Viñetas con "palabra: desc" |
| 8 | Transiciones Recicladas | P2 | "Además... Por lo tanto..." |
| 9 | Filler Phrases | P1 | "Es importante señalar que..." |
| 10 | Construcción "No es X, es Y" | P1 | Dicotomías artificiales |
| 11 | Uniformidad de Longitud | P2 | Todas las frases ~15 palabras |
| 12 | Burstiness Baja | P2 | Ritmo monótono |
| 13 | Hedging Sistemático | P1 | "Podría argumentarse que..." |
| 14 | Conclusión Genérica | P1 | "el futuro es brillante" |
| 15 | Párrafo Rígido | P2 | Tema → evidencia → resumen |
| 16 | Gerundios Excesivos | P2 | "Analizando..., viendo..." |
| 17 | Sinónimos Cíclicos | P2 | 3+ sinónimos para mismo concepto |
| 18 | Falsa Humildad Epistémica | P1 | "No es descabellado pensar..." |
| 19 | Abstractos sin Anclaje | P1 | "innovación" sin dato concreto |
| 20 | Tono Uniformemente Elevado | P2 | Sin variación formal/informal |
| 21 | Exceso de Adjetivos Valorativos | P1 | "extraordinario, profundo..." |
| 22 | Resumen por Sección | P2 | Cierre recapitulativo forzado |
| 23 | Secuencia Explícita | P2 | "En primer lugar..." |
| 24 | Name-Dropping de Prestigio | P2 | 3+ nombres de autoridad |
| 25 | "Con el fin de" | P1 | → "para" directamente |
| 26 | "Además" Inicial | P2 | Conector rígido inicial |
| 27 | Construcción "De X a Y" | P2 | Muletilla estructural |
| 28 | Frases Temáticas Iniciales | P2 | Todos los párrafos igual |
| 29 | "Sigue prosperando" | P2 | → "prospera" |
| 30 | "En general" | P2 | Vaguedad de alcance |
| 31 | Desafíos Genéricos | P1 | "A pesar de los retos..." |
| 32 | Análisis Superficial con -ing | P1 | Lista de gerundios |
| 33 | Rango Falso | P1 | "desde X hasta Y" sin datos |
| 34 | "Estudios demuestran" | P0 | Sin cita específica |
| 35 | "Refleja tendencias" | P1 | Conclusión genérica evasiva |
| 36 | "No dude en contactar" | P0 | Cierre de servicio al cliente |

## Sistema de Scoring

Cada instancia suma puntos según su tier:

| Tier | Puntos | Condición |
|------|--------|-----------|
| 1 | 3 | Siempre |
| 2 | 2 | En cluster de 2+ |
| 3 | 1 | 3+ por párrafo |

**Umbrales de acción:**
- **15+ puntos** → Reescribir completamente (modo Rewrite obligatorio)
- **8-14 puntos** → Corregir por secciones (patch selectivo)
- **<8 puntos** → Revisión menor (detección de residuos)

## Sistema de Severidad (P0/P1/P2)

- **P0 (Crítico)**: Requiere corrección inmediata. Afecta credibilidad directamente.
  - Ejemplos: aperturas chatbot, atribuciones vagas sin cita, emojis en contenido formal
  
- **P1 (Alto)**: Debe corregirse en reescritura. Afecta calidad perceptible.
  - Ejemplos: filler phrases, hedging sistemático, lenguaje promocional vacío
  
- **P2 (Medio)**: Corregir si se acumula (>3 por párrafo) o en revisión final.
  - Ejemplos: transiciones recicladas, uniformidad de longitud, sinónimos cíclicos

## Estándar de calidad

Una revisión anti-IA buena:

1. No solo “rompe patrones”; preserva claridad, rigor y voz.
2. No reemplaza una monotonía por caos arbitrario.
3. No sacrifica precisión doctrinal, bibliográfica o técnica.
4. No usa detectores como autoridad final.
5. Deja rastro explicable: qué se detectó, qué se cambió, qué riesgo sigue vivo.

## Anti-patrones

Evitar estos errores al ayudar al usuario:

1. Reescribir solo para “burlar detectores”.
2. Subir artificialmente la rareza léxica hasta volver el texto afectado.
3. Confundir “más raro” con “más humano”.
4. Dar un veredicto absoluto basado en una sola métrica.
5. Destruir citas, estructura o tono del proyecto por perseguir burstiness.
6. Dar por buena una pasada solo porque desapareció la fórmula literal “no es X, es Y”.
7. Limitarse a detectar patrones superficiales y no sus equivalentes implícitos.
8. Revisar artículos y olvidar dossiers, Formas T u otros productos editoriales.

## Criterios profesionales mínimos

Toda versión madura del protocolo anti-IA en Alejandría debe contemplar, como mínimo:

1. evaluación por documento y por tramo
2. mezcla de señales editoriales y técnicas
3. tratamiento explícito de documentos mixtos humano+IA
4. cautela con textos cortos, reescritos o muy editados
5. cautela con español y bilingüismo
6. separación entre detección de origen y calidad editorial
7. distinción entre detección IA y plagio
8. revisión humana final obligatoria

## Política de severidad

Si el usuario pide una pasada “rápida”, puede hacerse una auditoría editorial corta.

Si el usuario pide una solución “profesional”, “exhaustiva”, “de nivel real”, “mandatoria” o “para todos los productos”, entonces debes elevar el estándar y asumir:

1. revisión exhaustiva de equivalentes implícitos
2. uso de la referencia `professional-approaches.md`
3. salida explicable y multicapa
4. propuesta de integración del protocolo en skills o workflows hermanos cuando falte

## Recursos

- Patrones editoriales base: `docs/project-memory/feedback_avoid_ai_patterns.md`
- Vocabulario por 3 tiers (96 reemplazos): `references/anti-ia-vocabulary-tiered.md`
- Catálogo de 36 categorías: `references/anti-ia-patterns-catalog.md`
- Enfoques profesionales: `references/professional-approaches.md`
- Skill para GitHub Copilot: `.github/prompts/anti-ia.md`

## Referencias Externas

- Adaptado de: https://github.com/conorbronsdon/avoid-ai-writing
- Sistema de 3 tiers: brandonwise/humanizer
- Investigación de patrones: Pangram Labs, Wikipedia "Signs of AI-generated text"
- Comunidad: OpenClaw humanizer skill ecosystem
