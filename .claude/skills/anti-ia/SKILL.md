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
2. Leer `references/professional-approaches.md`.
3. Si el texto es un artículo, leer también `.claude/skills/articulo/SKILL.md`.
4. Si el texto es un dossier, leer también `.claude/skills/dossier/SKILL.md`.
5. Si el texto es una Forma T, leer también `.claude/skills/forma-t/SKILL.md`.

## Principio central

Una solución anti-IA profesional **no** se basa en un solo detector ni en una sola heurística.

Debe combinar tres capas:

1. **Señales editoriales**: muletillas, contrastes artificiales, rigidez de párrafos, tono plano, burstiness baja.
2. **Señales estadísticas/model-based**: perplexity, burstiness, rank/log-rank, perturbation scoring, clasificadores supervisados.
3. **Señales de procedencia**: historial de escritura, borradores, patrones del autor, validación de fuentes, mezcla humano+IA.

En la práctica, este skill debe operar como un **auditor multicapa y explicable**, no como un detector oracular.

## Qué hacer según el pedido

### A. Si el usuario pide revisar un texto

1. Detectar patrones visibles usando `feedback_avoid_ai_patterns.md`.
2. Identificar dónde el texto pierde voz humana:
   - apertura demasiado predecible
   - transiciones demasiado lógicas
   - uniformidad de longitud de frases
   - cierre-resumen repetitivo
   - abstractos vacíos sin anclaje factual
3. Revisar también señales profesionales mínimas:
   - uniformidad por oración o por párrafo
   - pasajes con predictibilidad excesiva
   - tramos que suenan a reformulación “anti-detector” y no a voz humana real
   - posible mezcla de segmentos humanos y segmentos más mecanizados
4. Corregir sin dañar:
   - precisión doctrinal o factual
   - citas FCD
   - estructura argumental válida
5. Validar al final:
   - no quedaron muletillas obvias
   - no quedaron equivalentes implícitos de patrones delatores
   - aumentó la variación rítmica
   - el texto sigue sonando al autor y no a una parodia “humanizada”
   - el resultado puede explicarse con hallazgos concretos, no con intuición vaga

### Entregable mínimo en revisión editorial

Cuando la tarea sea revisar o endurecer un texto, el trabajo debe cubrir cuatro salidas, aunque sea de forma breve:

1. **Hallazgos visibles**: qué patrones delatan IA.
2. **Intervención**: qué se reescribió.
3. **Criterio**: por qué el nuevo texto mejora.
4. **Validación**: qué se comprobó después.

### B. Si el usuario pide crear una herramienta anti-IA

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

### C. Si el usuario está trabajando en un producto de `prods/`

Aplicar este skill aunque el usuario no diga explícitamente “anti-IA”, cuando la tarea implique:

1. crear
2. revisar
3. ampliar
4. endurecer
5. preparar para publicación

de cualquier producto con voz editorial.

En esos casos, la revisión anti-IA no es opcional ni “nice to have”; forma parte de la Definition of Done.

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

- Reglas editoriales base: `docs/project-memory/feedback_avoid_ai_patterns.md`
- Enfoques profesionales y código existente: `references/professional-approaches.md`
