# Ilustraciones

Biblioteca de ilustraciones retóricas extraídas del corpus de Alejandría, listas para uso en discursos, artículos y dossiers.

---

## Qué es una ilustración

Una instancia concreta — narrativa, comparativa o descriptiva — que hace visible, sentida y memorable una verdad abstracta. No es decoración sino **iluminación**: la ventana en el muro del discurso (Spurgeon).

### Posición estructural

```
Concepto → Evidencia (escritura/cita) → ILUSTRACIÓN → Aplicación
```

La ilustración es el puente emocional entre la evidencia y la aplicación.

---

## Taxonomía

### Por forma

| Tipo | Mecanismo |
|------|-----------|
| Anécdota | Narrativa breve verídica |
| Parábola | Narrativa ficticia con significado analógico |
| Analogía | Comparación estructural entre dos dominios |
| Metáfora/Símil | Comparación comprimida (imagen única) |
| Escenario hipotético | Situación inventada ("imaginen que...") |
| Incidente histórico | Evento real del pasado |
| Cita | Palabras de una autoridad o testigo |
| Pintura verbal | Descripción vívida que crea imagen mental |
| Contraste | Yuxtaposición de dos estados |
| Lección objetiva | Objeto físico como ancla didáctica |
| Testimonio | Vivencia espiritual del orador (SUD-específico) |

### Por función (objetivo)

| Código | Función | Descripción |
|--------|---------|-------------|
| `clarify` | Clarificar | Hacer comprensible lo abstracto |
| `prove` | Probar | Mostrar con instancia concreta |
| `apply` | Aplicar | Mostrar cómo opera en la vida real |
| `attention` | Captar atención | Recapturar al oyente |
| `resonate` | Crear resonancia | Mover del asentimiento a la convicción |

### Por fuente (prioridad de extracción)

1. Conferencia general (fuente primaria)
2. Revistas de la Iglesia (Liahona/Ensign)
3. Manuales (Ven Sígueme, Principios del Evangelio)
4. Libros del corpus (biografías, historia)

---

## Criterios de calidad

Una buena ilustración es:

1. **Pertinente** — sirve al punto exacto
2. **Proporcional** — su extensión no excede la importancia del punto
3. **Auténtica** — suena verdadera
4. **Emocionalmente precisa** — evoca la emoción correcta a la intensidad correcta
5. **Fresca** — sorprende por reconocimiento, no por familiaridad
6. **Culturalmente accesible** — inteligible para la audiencia
7. **Autoefacente** — el orador no es el héroe

---

## Estructura de archivos

```
prods/ilustraciones/
  README.md               # este archivo
  BACKLOG.md              # pendientes de extracción
  {tema}/                 # agrupación temática
    {slug}.md             # una ilustración por archivo
```

### Formato de cada ilustración

```markdown
---
title: "Título breve"
author: "Nombre completo"
source: "Fuente FCD completa"
year: NNNN
form: anecdota | parabola | analogia | metafora | historica | cita | pintura | contraste | leccion | testimonio | hipotetica
objective: clarify | prove | apply | attention | resonate
emotional_tone: esperanza | urgencia | ternura | solemnidad | humor | asombro | gratitud | arrepentimiento | gozo | reverencia
paraphrased: true | false
characters: []
scripture_refs: []
topics: []
context: "Breve nota editorial: función de esta ilustración dentro del discurso original."
---

[Texto de la ilustración — completo, citable, listo para copiar y pegar.]
```

### Campos de metadata

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `title` | string | Título breve descriptivo |
| `author` | string | Nombre completo del orador/autor |
| `source` | string | Referencia FCD completa |
| `year` | int | Año de la fuente |
| `form` | enum | Tipo de ilustración (ver taxonomía) |
| `objective` | enum | Función retórica primaria |
| `emotional_tone` | enum | Emoción primaria que evoca — emparejar con el tono del punto |
| `paraphrased` | bool | Si el texto fue parafraseado respecto a la fuente |
| `characters` | list | Personas/personajes mencionados — enlazables en KG |
| `scripture_refs` | list | Escrituras asociadas — cross-reference escriturario |
| `topics` | list | Tags temáticos — cross-product, asociación KG |
| `context` | string | Nota editorial: función de esta ilustración dentro del discurso original (no va en el cuerpo) |

### 4 partes obligatorias

Cada ilustración debe contener estas 4 partes o no tiene sentido extraerla:

1. **Contexto de apertura** — quién cuenta, cuándo, por qué (frase introductoria con título honroso y contexto temporal)
2. **Texto narrativo completo** — setup → desarrollo → consecuencia. NUNCA elipsis "[...]" ni saltos. Parafraseada si es larga, pero completa
3. **Aplicación/enseñanza** — qué se aprende, emergente de la narrativa (no moraleja genérica pegada al final)
4. **FCD embebido** — citación completa entre paréntesis al cierre, para autonomía total (redes, clase, correo)

### Reglas de calidad

- **Lista para usar:** un orador debe poder copiar y pegar el texto en un discurso, clase o red social. Si no puede, la ilustración está mal escrita
- **Prosa narrativa:** ~100-200 palabras en prosa fluida, nunca bullet points ni frases telegráficas. Incluir el arco emocional
- **Parafrasear ≠ comprimir ni sugerir:** renarrar con brevedad pero con vida, contando la historia completa
- **La enseñanza emerge de la historia** — no pegar moralejas genéricas que podrían aplicarse a cualquier historia
- **Una por archivo:** facilita búsqueda, reutilización y metadata
- **Temas como carpetas:** fe, arrepentimiento, servicio, familia, etc. — alineados con tags de Formas T
- **No duplicar:** si la misma ilustración sirve a varios temas, ponerla en el tema primario y usar `topics` para cross-reference
