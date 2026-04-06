---
name: procedure_dossier_generation
description: Complete procedure for generating dossiers doctrinales — territory mapping, fresh research, writing, and quality review
type: feedback
---

Procedimiento completo para generar dossiers doctrinales.

---

## Fase A — Territorio

### A1. Tema amplio
- El usuario presenta un territorio doctrinal (ej: "la vida preterrenal", "la Expiación").

### A2. Pregunta de responsabilidad simple
- ¿El territorio cabe en UN dossier con UNA pregunta central?
- Si el territorio tiene subtemas con profundidad propia, dividir ANTES de investigar.
- **Regla:** si un subtema puede generar su propia sección de Escrituras clave con 5+ pasajes exclusivos, merece su propio dossier.

### A3. Panorámico primero (dp00)
- Crear el dossier panorámico (`dp00`) ANTES de los específicos.
- El panorámico define:
  - La estructura del territorio (tabla de dossiers con pregunta central de cada uno)
  - La secuencia narrativa entre dossiers (diagrama Mermaid)
  - El mapeo a Formas T existentes
  - Los dossiers contiguos (qué viene antes, después, en paralelo)
- El panorámico NO contiene escrituras, citas ni voces — solo orientación y conexiones.
- **Why:** Sin panorámico, los dossiers específicos se solapan o dejan huecos. El panorámico es el mapa antes de la expedición.

### A4. Aprobación
- Presentar el panorámico al usuario: ¿las divisiones son correctas? ¿las preguntas centrales capturan lo esencial? ¿falta algún subtema?
- No generar dossiers específicos hasta aprobación.

---

## Fase B — Investigación

### B1. Investigación fresca por dossier
- Cada dossier específico requiere su propia investigación exhaustiva.
- **No redistribuir** material de un dossier anterior o monolítico. Buscar de nuevo para cada territorio.
- **Why:** Redistribuir produce dossiers desbalanceados — el material original fue recopilado con otra lente. La investigación fresca descubre pasajes y voces que la lente original no buscó.

### B2. Definición oficial primero
- Si el tema involucra un concepto que la Iglesia ya ha definido formalmente, **empezar por las ayudas para el estudio** (GEE, TG, BD). Estas no son complemento — son el ancla definitoria.
- **Why:** Para «inteligencia e inteligencias», la Guía para el Estudio tenía la definición tripartita más clara y autorizada. Sin ella, el dossier habría partido de fuentes académicas que especulan más allá de lo revelado.

### B3. Orden de búsqueda
Seguir la jerarquía de fuentes (igual que Formas T):
1. **Ayudas para las escrituras** (GEE, TG, BD, JST) — ancla definitoria
2. **Escrituras ancla** — Biblia primero, luego Restauración
3. **Manuales oficiales vigentes**
4. **Conferencias generales** relevantes al tema
5. **Libros doctrinales** (Talmage, Roberts, etc.)
6. **Obras de referencia externas**

### B4. Nivel de fuente importa: instituto > seminario
- Los manuales de seminario simplifican deliberadamente para jóvenes. Los de instituto preservan la complejidad doctrinal.
- Para dossiers, **preferir siempre fuentes de nivel instituto o superior**. Las de seminario pueden citarse como referencia pedagógica, pero no como fuente doctrinal definitiva.
- **Why:** El manual de seminario de Abraham 3 dijo «inteligencias = espíritus preterrenales» (simplificación que colapsa la distinción). El de instituto preservó la complejidad con citas de Joseph Fielding Smith y Romney.

### B5. Herramientas de búsqueda
- `mcp__alejandria__kg_profile` y `kg_relations` para el nodo semilla
- `mcp__alejandria__search_hybrid` con 2-3 consultas por subtema
- Lectura directa de archivos del corpus para texto exacto de escrituras
- **Total:** 3-7 llamadas MCP por dossier, no 40+.

### B6. Certezas sobre especulaciones
- Clasificar cada hallazgo:
  - **Certeza:** respaldado por escrituras canónicas + voces proféticas consistentes → secciones 2-3 del dossier
  - **Posición académica:** interpretación razonada con base textual → sección 4
  - **Especulación / pregunta abierta:** sin respaldo claro o con debate no resuelto → sección 7 (Lagunas)
- **Nunca mezclar** especulaciones con doctrina establecida en las mismas secciones.

---

## Fase C — Redacción

### C1. Estructura
Seguir la plantilla (`prods/dossiers/_template.md`):
1. Panorama (párrafo orientador)
2. Escrituras clave (subsecciones temáticas — ver C1b)
3. Voces proféticas
4. Voces académicas y otros autores
5. Diagrama(s) Mermaid
6. Conexiones (tabla)
7. Lagunas y preguntas abiertas
8. Fuentes citadas (bibliografía completa)

### C1b. Subsecciones temáticas, no canónicas
- Las Formas T siguen orden canónico: Biblia → LdM → DyC (didáctico, de lo conocido a lo avanzado).
- Los dossiers organizan la sección de Escrituras clave por **concepto**, no por canon: "atributo eterno", "seres organizados", "gradación", "secuencia".
- La lógica del dossier es analítica; la de la Forma T es pedagógica. Son productos distintos con criterios de orden distintos.
- **Why:** dp05 (inteligencia e inteligencias) organiza por los tres significados del término, no por libro canónico. Un orden Biblia→DyC habría fragmentado la distinción conceptual que es el punto del dossier.

### C2. Patrón de lectura: intro→cita
- Cada blockquote DEBE estar precedido por un párrafo introductorio que oriente al lector.
- El párrafo dice qué va a encontrar y por qué importa; la cita lo demuestra.
- **Nunca** cita seguida de explicación. El lector necesita contexto antes de leer el pasaje.

### C3. Idioma y traducción
- El dossier se escribe en el idioma del usuario.
- Las fuentes se buscan en cualquier idioma del corpus.
- Las citas en idioma distinto al del dossier se traducen (norma FCD).

### C4. Texto completo de escrituras
- Los pasajes escriturarios se citan completos, no resumidos.
- Esto es lo que distingue al dossier de la Forma T: el dossier tiene el texto; la Forma T tiene la referencia.

### C5. Diagramas Mermaid
- **Fondos pastel + texto oscuro** (`color:#1a1a1a`). Nunca fondos saturados con texto blanco.
- **Nodos breves:** concepto + referencia abreviada. Sin citas textuales ni fragmentos largos dentro de los nodos.
- **Paleta estándar:** azul `#d0e4f7`, verde `#d4edda`, rojo `#f5d0d0`, dorado `#f5ecd0`, púrpura `#e0d4f7`.
- Tipos según el contenido: `graph` para flujos doctrinales, `timeline` para secuencias, `mindmap` para dimensiones de un concepto.
- **Why:** Diagramas con fondos saturados y texto largo son ilegibles. El diagrama es un mapa visual, no un documento.

### C6. Frontmatter
```yaml
---
title: "[Territorio doctrinal]"
date: YYYY-MM-DD
status: draft
type: doctrina | narrativa | contraste | simbolo
seed_entity: ""
related_forms:
  - ""
tags: []
---
```

### C7. Nomenclatura
```
{CCCC}-dp{NN}-{slug}.md
```
- `CCCC` = ID de colección (4 dígitos, mismo que las Formas T de esa colección)
- `dp00` = panorámico; `dp01`-`dp99` = específicos
- Slug en minúsculas, sin acentos, separado por guiones

---

## Fase D — Revisión

### D1. Checklist de calidad

- [ ] **Pregunta central clara:** el dossier responde UNA pregunta doctrinal, enunciada en el Panorama
- [ ] **Responsabilidad simple:** no bifurca en dos territorios distintos. Si lo hace, dividir.
- [ ] **Certezas vs. especulaciones:** las secciones 2-3 contienen solo doctrina respaldada; las especulaciones están en sección 7
- [ ] **Intro→cita:** cada blockquote está precedido por párrafo introductorio
- [ ] **Texto completo:** las escrituras se citan completas, no resumidas
- [ ] **Traducciones:** todas las citas en idioma distinto al del dossier están traducidas
- [ ] **Diagramas legibles:** fondos pastel, texto oscuro, nodos breves
- [ ] **Conexiones completas:** tabla con links al panorámico, a otros dossiers del territorio, a Formas T, y a dossiers futuros
- [ ] **Lagunas honestas:** lo que no se sabe se declara, no se oculta ni se rellena con especulación
- [ ] **Bibliografía completa:** cada fuente citada en el cuerpo aparece en la lista final
- [ ] **No es producto final:** el tono es de recopilación analítica, no de discurso o artículo terminado

### D2. Actualizar el panorámico
- **Cada dossier nuevo dentro de un territorio debe reflejarse en su panorámico (dp00).**
- Actualizar: tabla de dossiers, diagrama Mermaid de secuencia, tabla de Formas T, tabla de dossiers contiguos.
- Si un candidato a dossier futuro se materializa, reemplazar la mención «(pendiente)» por un link al archivo.
- **Why:** dp05 (inteligencia e inteligencias) obligó a actualizar dp00 — tabla, diagrama, conexiones. Sin esta regla, el panorámico se desactualiza silenciosamente.

### D3. Revisión cruzada
- Al completar todos los dossiers de un territorio, verificar:
  - ¿Hay solapamiento entre dossiers? → mover material al dossier correcto
  - ¿Hay huecos que ningún dossier cubre? → crear nuevo dossier o anotar en Lagunas del panorámico
  - ¿El panorámico sigue siendo preciso? → actualizar si la investigación reveló algo nuevo

---

**Why:** El primer dossier (vida preterrenal) se escribió como monolítico y luego hubo que dividirlo en 4 porque violaba responsabilidad simple. La división requirió investigación fresca porque redistribuir producía dossiers desbalanceados. Los diagramas iniciales eran ilegibles (fondos saturados, texto largo). Las citas se colocaban sin introducción. El quinto dossier (inteligencia e inteligencias) añadió que: (1) las ayudas para el estudio son el primer recurso definitorio, no un complemento; (2) los manuales de seminario simplifican — preferir instituto; (3) las subsecciones son temáticas, no canónicas; (4) el panorámico debe actualizarse al añadir cada dossier nuevo.

**How to apply:** Seguir las fases (A→B→C→D) cada vez que se genere un territorio de dossiers. No saltar de A1 a C1. A3 (panorámico primero) no es opcional. B1 (investigación fresca) no es opcional. B2 (definición oficial primero) antes de escrituras. D1 (checklist) se aplica a cada dossier antes de darlo por terminado. D2 (actualizar panorámico) cada vez que se añade un dossier.
