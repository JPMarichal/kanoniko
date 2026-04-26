---
name: dossier
description: Genera o revisa dossiers doctrinales en Alejandria. Usar cuando el usuario pida "dossier", "dossier doctrinal", "panorámico", "dp00", "genera un dossier", "divide este tema en dossiers", o quiera crear/ajustar archivos en prods/dossiers/. Al cerrar, propone automáticamente las Formas T relacionadas que el dossier habilita.
---

# Dossier

Usa este skill para crear o revisar dossiers doctrinales en Alejandria.

## Regla mandatoria

La skill `anti-ia` es obligatoria para todo dossier. No cerrar un dossier sin pasar por esa skill y aplicar su protocolo completo.

## Lecturas obligatorias iniciales

Antes de proponer o editar un dossier, leer:

1. `docs/project-memory/procedure_dossier_generation.md`
2. `docs/project-memory/project_dossier_product.md`
3. `prods/dossiers/_template.md`

Si el dossier pertenece a un territorio existente, leer además:

- el panorámico `dp00` del territorio
- 1 dossier vecino del mismo territorio

Si el dossier ya tiene o podría tener salida pedagógica, leer además 1-2 Formas T relacionadas en `prods/formas-t/` para evitar duplicación y detectar huecos.

## Cuándo usarlo

- Cuando el usuario pida un dossier doctrinal.
- Cuando el usuario pida un dossier panorámico (`dp00`).
- Cuando el usuario pida dividir un tema amplio en varios dossiers.
- Cuando haya que revisar un dossier por alcance, citas, estructura o conexiones.

## Flujo de trabajo

### 1. Determinar si es un territorio o un dossier individual

- Si el tema es amplio, empezar por `dp00` y no por un dossier específico.
- Si el tema ya está bien acotado y cabe en una sola pregunta central, crear el dossier individual.
- Si el territorio ya existe, actualizar primero su mapa mental: panorámico, secuencia y conexiones.

### 2. Investigar primero en el corpus

- Seguir documentation-first: corpus local antes que web.
- Empezar por ayudas para las escrituras cuando el concepto tenga definición oficial.
- Después buscar escrituras ancla, manuales vigentes, conferencia general, libros doctrinales y obras de referencia.
- Para cada dossier específico, hacer investigación fresca; no redistribuir material viejo sin volver a buscar.

### 3. Separar certeza de especulación

- Doctrina respaldada por escrituras y voces proféticas consistentes va en Escrituras clave y Voces proféticas.
- Interpretaciones razonadas van en Voces académicas.
- Preguntas abiertas, tensiones o faltantes van en Lagunas.
- Nunca mezclar especulación con doctrina establecida.

### 4. Redactar con patrón dossier

- Seguir `prods/dossiers/_template.md`.
- El dossier contiene texto completo de pasajes; la Forma T contiene referencias.
- Toda cita larga debe estar precedida por un párrafo orientador.
- Organizar Escrituras clave por subtemas analíticos, no por canon.
- Si el dossier está en español, traducir citas extranjeras según norma FCD.

### 5. Diagramas y conexiones

- Mermaid con fondos pastel y texto oscuro.
- Nodos breves: concepto + referencia corta.
- Completar la tabla de conexiones con dossiers relacionados, Formas T y material futuro.

### 6. Sincronizar panorámico

- Cada dossier nuevo dentro de un territorio debe reflejarse en `dp00`.
- Actualizar tabla de dossiers, diagrama de secuencia, formas relacionadas y contigüidad.

### 7. Proponer Formas T derivadas

- Al terminar el dossier, identificar qué subtemas ya quedaron maduros para una Forma T.
- Proponer siempre una lista corta de Formas T relacionadas, aunque el usuario no las haya pedido explícitamente.
- Cada propuesta debe incluir: título tentativo, objetivo breve y la sección del dossier de la que nace.
- Si ya existe una Forma T cercana, señalar si el dossier la alimenta, la corrige o revela un hueco nuevo.
- No crear automáticamente las Formas T salvo que el usuario lo pida; aquí la salida por defecto es propuesta, no expansión silenciosa.

## Checklist duro

- El dossier responde una sola pregunta central.
- No bifurca en dos territorios doctrinales distintos.
- Cada blockquote tiene introducción previa.
- Las escrituras citadas aparecen completas, no resumidas.
- Las lagunas están declaradas con honestidad.
- La bibliografía final contiene todas las fuentes usadas.
- Si el tema es amplio, existe o se crea `dp00` antes de avanzar.
- El cierre incluye Formas T relacionadas o una nota explícita de que aún no emergen Formas T válidas.
- La pasada anti-IA completa fue ejecutada según `.claude/skills/anti-ia/SKILL.md`.

## Nomenclatura y ubicación

- Guardar en `prods/dossiers/`.
- Usar `{CCCC}-dp{NN}-{slug}.md`.
- `dp00` es panorámico; `dp01+` son dossiers específicos.

## Ejemplos locales

- `prods/dossiers/0001-dp00-vida-preterrenal.md`
- `prods/dossiers/0001-dp05-inteligencia-e-inteligencias.md`

## Resultado esperado

Entregar un dossier listo en `prods/dossiers/` y, si corresponde, dejar actualizado el panorámico del territorio para que la arquitectura no quede desfasada. El cierre debe incluir además una propuesta breve de Formas T relacionadas.