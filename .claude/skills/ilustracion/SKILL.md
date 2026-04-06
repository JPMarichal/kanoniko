---
name: ilustracion
description: Extract rhetorical illustrations from corpus materials (conference talks, magazines, manuals) into the illustration library at prods/ilustraciones/.
trigger: /ilustracion
---

# Skill: Extracción de ilustraciones

Extrae ilustraciones retóricas de materiales del corpus y las deposita en `prods/ilustraciones/` con metadata estructurada.

## Uso

```
/ilustracion <fuente>          # extraer de una fuente específica
/ilustracion --tema <tema>     # extraer ilustraciones sobre un tema
/ilustracion --inventario      # mostrar estado del backlog
```

## Proceso de extracción

### 1. Identificar fuente
- Si se da una fuente específica (ej. "Holland abril 2024"), leer ese archivo del corpus
- Si se da un tema (ej. "fe"), buscar con `search_hybrid` materiales ricos en narrativa sobre ese tema
- Si `--inventario`, leer `prods/ilustraciones/BACKLOG.md` y reportar estado

### 2. Detectar ilustraciones en el texto
Buscar patrones narrativos:
- Historias personales del orador ("cuando era joven...", "recuerdo que...")
- Anécdotas de terceros ("una hermana en [lugar] me dijo...")
- Analogías desarrolladas ("es como cuando...")
- Incidentes históricos narrados con detalle
- Escenarios hipotéticos ("imaginen que...")
- Pinturas verbales (descripciones vívidas de escenas escriturarias)

### 3. Extraer y formatear
Para cada ilustración detectada:

1. **Determinar forma:** anecdota | parabola | analogia | metafora | historica | cita | pintura | contraste | leccion | testimonio | hipotetica
2. **Determinar objetivo:** clarify | prove | apply | attention | resonate
3. **Redactar como mini-narrativa autocontenida:**
   - El texto debe ser una historia narrada en prosa fluida (~100-200 palabras)
   - Estructura: setup (quién, dónde, cuándo) → desarrollo (qué pasó) → punto (por qué importa)
   - **Abrir con frase introductoria que nombre al orador con título honroso:** "El élder [Nombre] relató:", "La hermana [Nombre] explicó:", "El presidente [Nombre] compartió:"
   - **FCD embebido al final del texto:** cerrar con citación completa entre paréntesis. Así la ilustración es autónoma — usable en redes sociales, clase, correo, sin necesitar la biblioteca
   - Autocontenida: el lector NO necesita haber leído el discurso original
   - Un orador debe poder copiar y pegar el texto directamente en su discurso o red social
   - Parafrasear ≠ comprimir a telegrama; significa renarrar con brevedad pero con vida
4. **Marcar si parafraseada:** `paraphrased: true/false`
5. **Generar metadata completa:**
   - `title`: título breve descriptivo
   - `author`: nombre completo del orador/autor
   - `source`: referencia FCD completa
   - `year`: año de la fuente
   - `form`: tipo de ilustración
   - `objective`: función retórica
   - `emotional_tone`: emoción primaria (esperanza, urgencia, ternura, solemnidad, humor, asombro, gratitud, arrepentimiento, gozo, reverencia)
   - `paraphrased`: bool
   - `characters`: personas/personajes mencionados (enlazables en KG)
   - `scripture_refs`: escrituras asociadas
   - `topics`: tags temáticos (cross-product, asociación KG)

### 4. Guardar
- Determinar carpeta temática (crear si no existe)
- Guardar en `prods/ilustraciones/{tema}/{slug}.md`
- Actualizar `prods/ilustraciones/BACKLOG.md` marcando la fuente como procesada

### 5. Reportar
- Listar ilustraciones extraídas con título, forma, objetivo y ubicación
- Sugerir productos que podrían beneficiarse de estas ilustraciones

## Estructura de cada ilustración

El cuerpo de cada ilustración tiene 3 partes obligatorias (el contexto va en metadata):

1. **Texto narrativo completo** — abre con frase introductoria (quién, cuándo, título honroso). Setup → desarrollo → consecuencia. SIN elipsis ni saltos
2. **Aplicación/enseñanza** — qué se aprende, emergente de la narrativa (no moraleja genérica pegada)
3. **FCD embebido** — citación completa entre paréntesis al cierre

El campo `context` en el frontmatter es metadata editorial (función de la ilustración dentro del discurso original). NO va en el cuerpo — el texto debe ser 100% copiable sin recortar nada.

Sin estas 3 partes, la ilustración no tiene sentido extraerla.

## Ejemplo de salida

```markdown
---
title: "Doscientas cuarenta personas en una casa alquilada"
author: "Carlos A. Godoy"
source: "Élder Carlos A. Godoy, «Rostros sonrientes y corazones agradecidos» (conferencia general, octubre 2025)"
year: 2025
form: anecdota
objective: resonate
emotional_tone: gozo
paraphrased: true
characters: [Carlos A. Godoy]
scripture_refs: []
topics: [crecimiento, gozo, bautismo, africa, sacrificio]
context: "Ilustró que el crecimiento de la Iglesia nace de la conversión genuina, no de la comodidad."
---

En la conferencia general de octubre de 2025, el élder Carlos A. Godoy relató una experiencia durante una visita a África. Asistió a los servicios dominicales de una rama que se reunía en una pequeña casa alquilada. En dos salas diminutas se apretaban doscientas cuarenta personas; las que no cabían se sentaban afuera y seguían la reunión asomándose por las puertas y ventanas.

En ese marco de estrechez, el obispo se puso de pie y presentó con alegría a diez nuevos miembros bautizados esa semana. Nadie se quejaba de la incomodidad ni pedía un edificio más grande. Solo había rostros sonrientes y corazones agradecidos.

La experiencia muestra que el gozo del Evangelio no depende de las condiciones materiales: a veces se manifiesta con más fuerza precisamente donde estas son más escasas. (Élder Carlos A. Godoy, «Rostros sonrientes y corazones agradecidos», conferencia general, octubre 2025)
```

## Reglas

- **No inventar ilustraciones** — solo extraer del corpus existente
- **Historia completa** — NUNCA usar "[...]" ni elipsis; contar setup, desarrollo, consecuencia y aplicación
- **Parafrasear ≠ comprimir** — renarrar con brevedad pero con vida; no reducir a telegrama ni sugerir sin contar
- **FCD siempre embebido** — citación completa al final del texto entre paréntesis
- **Frase introductoria** — abrir con contexto temporal + nombre y título honroso del orador
- **Honoríficos siempre** — nunca referirse a un líder solo por apellido ("Godoy"); siempre "el élder Godoy", "el presidente Oaks", "la hermana Dennis". Primera mención: nombre completo con título; siguientes: título + apellido
- **La enseñanza emerge de la historia** — no pegar moralejas genéricas al final
- **Un archivo por ilustración** — facilita reutilización
- **~100-200 palabras** el texto principal
- **Verificar antes de guardar** que no exista una ilustración duplicada en la biblioteca
