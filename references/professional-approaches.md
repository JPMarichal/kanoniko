---
description: Enfoques profesionales y herramientas técnicas para detección y corrección de patrones IA. Enlaces a investigación académica, APIs de detección, y código de referencia.
---

# Enfoques Profesionales Anti-IA

Este documento recoge enfoques técnicos, herramientas profesionales y referencias académicas para la detección y mitigación de patrones de IA.

---

## 1. Enfoques Técnicos de Detección

### 1.1 Perplexity (Perplejidad)

**Qué mide**: Qué tan "predecible" es el texto para un modelo de lenguaje.

- **Texto IA**: Baja perplexity (<30) — usa palabras altamente esperables
- **Texto humano**: Alta perplexity (>85) — hace elecciones léxicas inesperadas

**Cómo aumentar perplexity en escritura**:
- Vocabulario variado, evitar repetición
- Elecciones léxicas inesperadas (no siempre la palabra "obvia")
- Uso ocasional de coloquialismos o regionalismos
- Inclusión de referencias culturales específicas

**Herramientas**:
- Hugging Face transformers: calcular perplexity con modelos locales
- OpenAI API: logprobs para estimar predictibilidad
- GPTZero API: score de perplexity integrado

### 1.2 Burstiness (Ráfaga)

**Qué mide**: Variación en longitud y complejidad de oraciones.

- **Texto IA**: Baja burstiness — frases de longitud uniforme (~15 palabras)
- **Texto humano**: Alta burstiness — mezcla de frases cortas (4-6 palabras) y largas (25-35 palabras)

**Fórmula aproximada**:
```
Burstiness = σ(longitud_oraciones) / μ(longitud_oraciones)
```

**Cómo aumentar burstiness**:
- Alternar frases cortas brutales con desarrollos largos
- Usar oraciones de 1 palabra para énfasis ("Silencio.")
- Fragmentos seguidos de períodos complejos
- Variar estructura: pregunta, imperativo, declarativo

### 1.3 Rank Analysis / Log-Rank

**Qué mide**: Posición en ranking de probabilidad de palabras generadas.

- Texto IA tiende a palabras de rank bajo (más probables)
- Texto humano incluye palabras de rank alto (menos probables)

**Herramientas**:
- Originality.AI: usa rank-based detection
- GPTZero: combina perplexity + burstiness + rank

### 1.4 Perturbation Scoring

**Qué mide**: Cambios en predicción del modelo ante pequeñas modificaciones.

- Texto IA es más sensible a perturbaciones (cambia drásticamente)
- Texto humano es más robusto a cambios menores

---

## 2. APIs y Servicios Profesionales

### 2.1 GPTZero

- **URL**: https://gptzero.me
- **Precisión**: ~85% en textos largos (>500 palabras)
- **Límites**: Menor precisión en textos cortos o muy editados
- **API**: Disponible para integración

### 2.2 Originality.AI

- **URL**: https://originality.ai
- **Características**: Rank-based + clasificador entrenado
- **Casos de uso**: Content marketing, publicaciones web
- **Precio**: Por crédito de análisis

### 2.3 Pangram Labs

- **URL**: https://www.pangram.com
- **Investigación**: Decoder-only classifier entrenado en 28M documentos humanos
- **API**: Enterprise disponible
- **Ventaja**: Enfoque en señales estructurales, no solo léxicas

### 2.4 Turnitin AI Detection

- **URL**: https://www.turnitin.com (producto "Originality")
- **Uso**: Instituciones académicas
- **Cobertura**: Integrado en flujos de revisión de papers

### 2.5 Hugging Face (Self-Hosted)

- **Modelos**: 
  - `roberta-base-openai-detector`
  - `radford-gpt2-detector`
  - `Hello-SimpleAI/chatgpt-detector-roberta`
- **Ventaja**: Gratuito, privado, customizable
- **Requisito**: Infraestructura propia

---

## 3. Código de Referencia Open Source

### 3.1 Conor Bronsdon / avoid-ai-writing

- **Repo**: https://github.com/conorbronsdon/avoid-ai-writing
- **Contenido**: SKILL.md con 109 reemplazos, 36 categorías, sistema de 2 pasadas
- **Adaptación**: Este skill está basado en este trabajo

### 3.2 Brandon Wise / humanizer

- **Repo**: https://github.com/brandonwise/humanizer
- **Sistema**: Tiered vocabulary (3 tiers)
- **Investigación**: Burstiness, sentence length variation, trigram repetition

### 3.3 Blader / humanizer (Claude Code skill)

- **Repo**: https://github.com/blader/humanizer
- **Enfoque**: Reescritura con preservación de significado

### 3.4 OpenClaw

- **URL**: https://github.com/openclaw/openclaw
- **Ecosistema**: Comunidad de skills humanizer
- **Recursos**: Patrones compartidos, vocabulario research

### 3.5 Wikipedia: Signs of AI-Generated Text

- **URL**: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- **Autor**: Editores de Wikipedia
- **Calidad**: Referencia canónica, mantenida activamente

---

## 4. Métricas y Umbrales Recomendados

### 4.1 Métricas Combinadas

Para un sistema robusto, combinar:

```
Score_total = w1*perplexity_score + w2*burstiness_score + w3*rank_score + w4*pattern_matches

Sugerencia de pesos:
- w1 (perplexity): 0.25
- w2 (burstiness): 0.25  
- w3 (rank): 0.20
- w4 (patterns): 0.30
```

### 4.2 Umbrales Prácticos

| Contexto | Umbral de "Sospecha IA" | Umbral de "Probable IA" |
|----------|-------------------------|-------------------------|
| Ensayos académicos | 0.6 | 0.8 |
| Marketing/SEO | 0.7 | 0.85 |
| Ficción creativa | 0.5 | 0.7 |
| Noticias/periodismo | 0.65 | 0.8 |
| Contenido doctrinal (Alejandría) | 0.6 | 0.75 |

### 4.3 Factores de Ajuste

**Aumentan sospecha (+0.1 a +0.2)**:
- Texto generado de una sola vez (no iterado)
- Sin citas verificables
- Sin anécdotas personales o datos específicos
- Estructura excesivamente simétrica

**Reducen sospecha (-0.1 a -0.2)**:
- Múltiples borradores con historial visible
- Citas FCD verificables
- Anécdotas del autor con detalles específicos
- Variación deliberada de estilo

---

## 5. Limitaciones Conocidas

### 5.1 Textos Cortos (<100 palabras)

- Perplexity poco fiable
- Burstiness no calculable
- Recomendación: Usar solo análisis de patrones léxicos

### 5.2 Textos Muy Editados

- Edición extensiva por humanos reduce señales IA
- Pero puede introducir "patchwriting"
- Recomendación: Evaluar historial de edición

### 5.3 Bilingüismo y Español

- La mayoría de detectores entrenados en inglés
- Precisión menor en español (~10-15%)
- Recomendación: Ajustar umbrales, usar más peso en patrones léxicos

### 5.4 Modelos Más Recientes

- GPT-4 produce texto más "humano" que GPT-3.5
- Diferencia de detectabilidad: ~15-20 puntos porcentuales
- Recomendación: Actualizar modelos de detección periódicamente

---

## 6. Enfoque Forense (Investigación de Procedencia)

### 6.1 Metadata del Documento

- Historial de versiones (git, Google Docs history)
- Timestamps de creación/edición
- Autor declarado vs. estilo real

### 6.2 Análisis Estilométrico

- Comparación con corpus del autor
- Métricas: tasa de hapax legomena, diversidad léxica
- Análisis de n-gramas característicos

### 6.3 Validación de Fuentes

- ¿Existen las citas atribuidas?
- ¿Son precisas las transcripciones?
- ¿Hay mezcla de fuentes humanas e IA?

---

## 7. Políticas Éticas y Legales

### 7.1 No Declarar Absolutamente

- Nunca afirmar "esto es 100% IA" o "esto es 100% humano"
- Usar lenguaje probabilístico: "indica señales", "sugiere", "probabilidad de"
- Incluir intervalos de confianza cuando sea posible

### 7.2 Privacidad

- Los textos analizados pueden almacenarse en servicios externos
- Considerar auto-hosting para contenido sensible
- Cumplir GDPR/CCPA si aplica

### 7.3 Sesgos Conocidos

- Falsos positivos: Textos de no nativos, textos técnicos altamente estandarizados
- Falsos negativos: Texto IA muy editado, textos de modelos avanzados
- Recomendación: Validación humana siempre

---

## 8. Integración con Flujos de Trabajo

### 8.1 Pre-publicación (Editorial)

1. Autor escribe borrador
2. Revisión por pares (humana)
3. **Análisis anti-IA automático**
4. Si score > umbral → revisión editorial enfocada
5. Segunda pasada anti-IA
6. Aprobación final

### 8.2 Investigación Forense

1. Recepción de documento sospechoso
2. Análisis técnico (perplexity, burstiness, rank)
3. Análisis forense (metadata, historial)
4. Análisis estilométrico (comparación con corpus)
5. Validación de fuentes
6. Reporte con intervalos de confianza

### 8.3 Mejora Continua de Modelos

1. Recopilar falsos positivos/negativos
2. Reentrenar clasificador
3. Actualizar vocabulario de patrones
4. Ajustar pesos de métricas

---

## 9. Recursos Adicionales

### Papers Académicos

- **"Detecting AI-Generated Text"** (MIT, 2023)
- **"Adversarial Robustness of AI Detectors"** (Stanford, 2024)
- **"The Reliability of AI Text Detectors"** (Meta Research, 2024)

### Blogs y Newsletters

- **Chain of Thought** (newsletter.chainofthought.show)
- **One Useful Thing** (Ethan Mollick)
- **AI Snake Oil** (Arvind Narayanan)

### Comunidades

- Reddit: r/ChatGPT, r/artificial
- Discord: OpenClaw, EleutherAI

---

## 10. Checklist de Implementación Profesional

Para desplegar un sistema anti-IA en producción:

- [ ] Seleccionar métricas apropiadas (perplexity + burstiness mínimo)
- [ ] Definir umbrales según contexto (académico vs. marketing)
- [ ] Implementar logging de decisiones (explicabilidad)
- [ ] Establecer proceso de apelación/validación humana
- [ ] Documentar limitaciones para usuarios
- [ ] Plan de actualización ante nuevos modelos
- [ ] Consideración de privacidad y retención de datos
- [ ] Pruebas con corpus representativo (falsos positivos/negativos)

---

*Documento vivo: Actualizar con nuevas investigaciones y herramientas.*
*Última actualización: Mayo 2026*
