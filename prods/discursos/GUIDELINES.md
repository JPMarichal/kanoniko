# Guía de estilo — Discursos

Reglas de producción para el producto "discursos" de Alejandría, basadas en el análisis de ~4,200 discursos de conferencia general (1971-2025) y en los criterios editoriales del proyecto.

---

## 1. Anatomía del discurso

### Apertura (~10%)
- **Saludo** — "Hermanos y hermanas" (universal, breve)
- **Gancho** — historia personal, pregunta, escena, o dato que conecte emocionalmente
- **Tesis** — declarar el mensaje central en los primeros 30 segundos

### Cuerpo (~75%)
- **1-4 bloques** según duración (ver tabla de calibración)
- Cada bloque desarrolla un punto de la columna vertebral
- Micro-estructura interna: concepto → evidencia (escritura/cita) → ilustración → aplicación
- Progresión didáctica: de lo conocido a lo nuevo, de lo simple a lo profundo

### Cierre (~15%)
- Recapitulación de la tesis (1-2 oraciones, no repetir el discurso)
- Invitación concreta y específica
- Testimonio personal vinculado al tema
- "En el nombre de Jesucristo. Amén."

---

## 2. Columna vertebral

Cada discurso tiene UN eje dominante. Los otros elementos aparecen como apoyo.

### Tipos de columna

| Tipo | Descripción |
|------|-------------|
| **Escrituraria** | Pasajes clave como eje de la enseñanza |
| **Conceptual** | Ideas doctrinales como eje |
| **Narrativa** | Historias o ilustraciones como eje |

### Modos

| Modo | Descripción | Ejemplo |
|------|-------------|---------|
| **Singular** | Un solo elemento central desmenuzado desde múltiples ángulos | Una parábola, una escritura, una experiencia misionera |
| **Progresión** | Varios elementos que escalan o convergen hacia la tesis | Tres escrituras que construyen un argumento; dos historias que enseñan la misma verdad |

### Combinaciones frecuentes en conferencia general

- **Escrituraria singular:** élder Holland desmenuzando Mateo 11:28-30 por 12 minutos
- **Escrituraria progresión:** élder Bednar hilando D&C 88:119 verso a verso
- **Conceptual singular:** presidente Nelson desarrollando "el poder del convenio" desde múltiples ángulos
- **Conceptual progresión:** élder Christofferson con "tres razones por las que necesitamos la Iglesia"
- **Narrativa singular:** presidente Monson con una historia de servicio que ancla toda la doctrina
- **Narrativa progresión:** hermana Beck con tres ejemplos de "madre heart" que convergen en un principio

---

## 3. Calibración (con traducción simultánea)

Ritmo: ~120 palabras/min (vs. ~150 sin traducción). El overhead de traducción es ~20%.

| Duración | Palabras | Bloques | Escrituras | Ilustraciones |
|----------|----------|---------|------------|---------------|
| **8 min (default)** | **~950** | **1-2** | **2-3** | **1-2** |
| 10 min | ~1,200 | 2 | 3-5 | 2 |
| 12 min | ~1,450 | 2-3 | 5-7 | 2-3 |
| 15 min | ~1,800 | 3 | 7-10 | 3 |

Sin traducción simultánea: multiplicar palabras por 1.25.

---

## 4. Redacción para traducción simultánea

- Frases de **15-20 palabras máximo**
- Evitar subordinadas largas y paréntesis anidados
- Pausas naturales cada 2-3 oraciones (punto y aparte frecuente)
- Vocabulario claro — evitar modismos difíciles de traducir
- Repetir el sujeto si hay ambigüedad (el traductor no puede detenerse a preguntar)

---

## 5. Tono y estilo

- **Ameno siempre** — variar ritmo: pregunta → pausa → historia → doctrina → invitación
- **Humor reverente y sutil** — cuarta pared ocasional; nunca humor forzado ni sarcasmo
- **Sin iaísmos** — preferir pretérito simple ("dijo") sobre imperfecto ("decía") y pluscuamperfecto ("había dicho")
- **Sin patrones IA** — revisar contra checklist de patrones detectables (ver feedback_avoid_ai_patterns.md)
- **Honoríficos** para Autoridades Generales: élder, presidente, hermana — siempre
- **Tres capas doctrinales:** doctrina oficial ≠ enseñanza profética ≠ creencia cultural — nunca mezclar
- **Certezas sobre especulaciones** — lo especulativo marcado aparte, nunca presentado como doctrina

---

## 6. Ilustraciones

Cada discurso debe ser **ricamente ilustrado**. La ilustración es el puente emocional entre la evidencia y la aplicación.

### Definición
Una instancia concreta — narrativa, comparativa o descriptiva — que hace visible, sentida y memorable una verdad abstracta. No decoración sino iluminación.

### Posición estructural
Micro-estructura: concepto → evidencia (escritura/cita) → **ilustración** → aplicación

### Tipos más frecuentes en discursos
- **Anécdota** — historia breve verídica (propia o ajena)
- **Incidente histórico** — evento real que ancla doctrina
- **Analogía** — comparación estructural ("la fe es como...")
- **Escenario hipotético** — "imaginen que..." (conecta con experiencia del oyente)
- **Testimonio** — vivencia espiritual del orador (la más poderosa; invita al Espíritu)
- **Pintura verbal** — descripción vívida que crea imagen mental

### Cada ilustración tiene un objetivo
| Objetivo | Cuándo usarlo |
|----------|--------------|
| Clarificar | Concepto abstracto que necesita hacerse visible |
| Probar | Afirmación que requiere instancia concreta |
| Aplicar | Verdad que necesita aterrizarse en la vida diaria |
| Captar atención | Audiencia distraída o cambio de bloque |
| Crear resonancia | Mover del asentimiento intelectual a la convicción |

### Criterios de calidad
1. **Pertinente** — sirve al punto exacto, sin desvíos
2. **Proporcional** — extensión ≤ importancia del punto (Chapell: "una ilustración más larga que el punto que sirve, se ha convertido en el punto")
3. **Auténtica** — suena verdadera
4. **Emocionalmente precisa** — emoción correcta, intensidad correcta
5. **Fresca** — evitar clichés reciclados ("huellas en la arena")
6. **Culturalmente accesible** — inteligible para la audiencia real (sin analogías de béisbol en Latinoamérica)
7. **Autoefacente** — el orador no es el héroe de su historia

### FCD y paráfrasis
- Si se inserta verbatim: FCD completo inline obligatorio
- Si se parafrasea por brevedad: citar fuente en bibliografía
- `[HISTORIA PERSONAL]` sigue siendo marcador para experiencias del orador

### Fuente de ilustraciones
Usar la biblioteca en `prods/ilustraciones/` cuando existan ilustraciones relevantes. El skill `/ilustracion` extrae nuevas del corpus.

---

## 7. Fuentes y citas

- **Escrituras como columna vertebral** — agotar raíces bíblicas antes de fuentes de la Restauración
- **FCD inline obligatorio** — nombre+título en la oración, referencia completa en paréntesis
  - Correcto: *Como enseñó el élder Jeffrey R. Holland, del Cuórum de los Doce Apóstoles: «...» ("Broken Things to Mend", conferencia general, abril 2006).*
  - Incorrecto: *Holland dijo: «...» [3].*
- **Texto completo de la escritura** — no solo la referencia; el oyente necesita escuchar las palabras
- **Historias concretas** — con nombres, lugares, fechas; no anécdotas genéricas
- **Marcadores de personalización:** `[HISTORIA PERSONAL: sugerencia de tipo de historia]` donde el orador debe insertar experiencia propia. El borrador sugiere el tipo pero no inventa la historia.

---

## 8. Checklist de revisión

Antes de marcar un discurso como `status: final`:

- [ ] Tesis identificable en los primeros 30 segundos
- [ ] Columna vertebral clara y consistente (tipo + modo)
- [ ] Longitud dentro del rango de la tabla de calibración
- [ ] Frases ≤ 20 palabras (si `translation: true`)
- [ ] Escrituras con texto completo, no solo referencia
- [ ] Citas en FCD inline con nombre+título+fuente
- [ ] Honoríficos para toda AG mencionada
- [ ] Sin iaísmos ni patrones IA detectables
- [ ] Doctrina vs. opinión claramente diferenciadas
- [ ] Cierre con invitación concreta + testimonio + "En el nombre de Jesucristo. Amén."
- [ ] `source_forms` y `source_dossiers` poblados si existen fuentes
