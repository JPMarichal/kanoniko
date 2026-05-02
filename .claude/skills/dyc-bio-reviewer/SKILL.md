---
name: dyc-bio-reviewer
description: Revisar y enderezar biografías del "quién es quién" en DyC ubicadas en prods/dyc_bios/bios. Asegura redacción natural, precisión académica, tono espiritual, eliminación de anglicismos, profundidad en menciones a DyC, estructura narrativa apropiada, completitud end-to-end (trayectoria completa del personaje), y aplica revisión anti-IA obligatoria.
triggers:
  - "revisa biografía"
  - "revisa esta biografía"
  - "revisar biografía DyC"
  - "revisar bio"
  - "auditar biografía"
  - "enderezar biografía"
  - "revisar quién es quién"
  - "revisar Sidney Rigdon"
  - "revisar personaje DyC"
---

# Skill: Revisor de Biografías DyC

Revisa biografías del directorio `prods/dyc_bios/bios/` para garantizar calidad editorial, precisión doctrinal y voz humana natural.

## Alcance

Aplica a archivos `.md` de biografías de personajes mencionados en Doctrina y Convenios.

## Criterios de Revisión Obligatorios

### 1. Redacción Natural y Gramática

- **Fluidez**: oraciones que suenen naturales al leer en voz alta
- **Gramática**: concordancia, tiempos verbales, sintaxis correcta
- **Acentuación**: tildes correctas (é, á, í, ó, ú, ü, ñ)
- **Puntuación**: comas, puntos, punto y coma, dos puntos usados correctamente
- **Evitar oraciones excesivamente largas** (>40 palabras) sin necesidad
- **Variación de ritmo**: mezclar frases cortas (5-8 palabras) con medias (15-20) y largas ocasionales (25-30)

### 2. Precisión Académica con Lenguaje Natural

- **Tono espiritual**: respetuoso, reverente, apropiado para contexto SUD
- **Evitar jerga académica innecesaria**: preferir "explicó" sobre "postuló", "mostró" sobre "evidenció"
- **Precisión histórica**: fechas, lugares, eventos verificables
- **Sin sensacionalismo**: evitar "impactante", "asombroso", "increíble"
- **Sin minimización**: no restar importancia a revelaciones o llamamientos

### 3. Eliminación de Anglicismos

**MANDATORIO**: Revisar palabras embebidas en inglés.

Detectar y traducir:
- **Nombres de posesiones**: "Smith's house" → "la casa de Smith"
- **Citas en inglés**: traducir al español con referencia
- **Términos técnicos**: buscar equivalente español o explicar
- **Expresiones idiomaticas**: "by the way", "indeed", "however" → eliminar o adaptar
- **Falsos amigos**: "actual" → "actual" (no "current"), "eventualmente" → "finalmente" (no "eventually")
- **Calcos estructurales**: "es importante notar que" → "cabe destacar" o simplemente eliminar

### 4. Profundidad en Menciones a DyC

**CRÍTICO**: Las referencias a Doctrina y Convenios deben ser sustanciales, no someras.

**Anti-patrón a eliminar**:
```
❌ "DyC lo muestra como un predicador."
❌ "Aparece en DyC 35 como escribiente."
```

**Estándar requerido**:
```
✓ "En DyC 35:20, el Señor lo llama como escribiente de José Smith, 
   encargado de registrar las revelaciones recibidas durante la 
   traducción de la Biblia en 1831."
```

Cada mención a DyC debe responder:
- **¿Qué sección(es)?** (referencia precisa: DyC 35:20, no solo DyC 35)
- **¿En qué parte de la sección?** (texto de revelación, encabezado, pie de página)
- **¿Qué función o rol se describe?**
- **¿En qué contexto histórico?**
- **¿Cuál fue su trayectoria en ese rol?**
- **¿Por qué es significativa esa mención para su biografía?**

**Nota especial para encabezados**: Si el personaje aparece en el encabezado de una sección DyC (no en el texto de la revelación), esto debe mencionarse explícitamente. Ejemplo: "aparece en DyC 99 a través del encabezado de la sección, que explica el contexto..."

### 5. Estructura Narrativa (Elástica según datos, máximo 5 párrafos)

**LÍMITE ABSOLUTO: Máximo 5 párrafos. Mínimo 1 párrafo.**

El número de párrafos es **completamente elástico** dentro del rango 1-5 según la cantidad y calidad de datos disponibles. No hay números fijos predefinidos, pero **nunca puede exceder 5 párrafos**.

**Rango flexible (1-5)**:
- **1 párrafo**: personajes menores, datos escasos, mención breve en DyC, **solo una fuente disponible**, **información limitada a un solo contexto DyC**
- **2-4 párrafos**: personajes con información moderada, múltiples contextos DyC o fuentes biográficas
- **5 párrafos**: figuras centrales con trayectoria compleja y abundancia de datos (MÁXIMO)

**Criterio de decisión**: ¿Qué se necesita para contar la historia completa del personaje de forma natural, sin forzar contenido ni omitir lo relevante?

**Regla para condensar a 1 párrafo**: Cuando el personaje tenga **solo una mención en DyC** y **solo una fuente disponible**, condensar todo en 1 párrafo fluido que combine: contexto DyC + significado histórico.

**Regla para mantener 2+ párrafos**: Cuando haya múltiples contextos DyC, datos biográficos adicionales (matrimonio, muerte, trayectoria) o más de una fuente disponible.

**Principios estructurales**:
- **MÁXIMO 5 párrafos** — límite estricto
- Cada párrafo debe tener densidad informativa, no relleno
- Priorizar completitud end-to-end dentro del límite de 5 párrafos
- Si faltan datos, usar menos párrafos; si hay abundancia, usar exactamente 5
- Orden lógico: cronológico o temático con transiciones naturales

### 6. Eliminación de Referencias al Corpus

**Reemplazar fórmulas meta**:

| ❌ Eliminar | ✅ Usar en su lugar |
|-------------|---------------------|
| "del corpus" | "de las fuentes históricas" |
| "fuentes abiertas del corpus" | "la documentación disponible" |
| "según el corpus" | "según las fuentes biográficas" |
| "el corpus indica" | "la evidencia histórica indica" |
| "en las fuentes del corpus" | "en los registros históricos" |
| "la narrativa del corpus" | "el relato biográfico" |

### 7. Citas Precisas de Escritura

Cuando se cite un pasaje:
- **Referencia completa**: Libro Capítulo:Versículo (ej: DyC 35:20)
- **Contexto**: explicar cómo ese versículo ilumina la biografía
- **Traducción propia** si el pasaje está en inglés en la fuente
- **No citar de memoria**: verificar que el versículo existe y dice lo atribuido

### 8. Revisión Anti-IA Obligatoria (APLICAR AL FINAL)

**Este paso es MANDATORIO, NO NEGOCIABLE y debe ejecutarse DESPUÉS de todas las correcciones de contenido.**

El anti-IA debe aplicarse al texto final para cubrir TODO el trabajo revisado.

1. Invocar el skill `anti-ia` con modo Rewrite (después de completar Pasos 1-3)
2. Aplicar las 36 categorías de patrones
3. Verificar especialmente:
   - Filler phrases religiosos: "Es importante destacar que..."
   - Lenguaje promocional excesivo
   - Estructuras rígidas de párrafo
   - Uniformidad de longitud de oraciones
   - Transiciones recicladas: "Además", "Por lo tanto", "Sin embargo"
4. Preservar precisión doctrinal durante la reescritura

### 9. Completitud End-to-End (NUEVO CRITERIO MANDATORIO)

**CRÍTICO**: La biografía debe cubrir la trayectoria completa del personaje, no solo fragmentos.

**Principio**: End-to-end hasta donde las fuentes lo permitan. No es aceptable mencionar la excomunión sin el contexto previo y posterior.

**Dimensiones de completitud a verificar**:

| Dimensión | Elementos a incluir | Ejemplo (Sidney Rigdon) |
|-----------|---------------------|-------------------------|
| **Primer período** | Origen, conversión, primeros llamamientos | Predicador bautista/campbelita, conversión 1830 |
| **Colaboración con JS** | Funciones específicas, revelaciones recibidas juntos | Escribiente, traducción de la Biblia, visión DyC 76 |
| **Liderazgo institucional** | Cargos formales, responsabilidades | Consejero, portavoz, mayordomo de revelaciones |
| **Advertencias/Pruebas** | Reprensiones, condicionamientos | DyC 63, 90, 100 - exaltación, deudas, humildad |
| **Crisis** | Excomunión, apostasía, conflictos | Excomunión 1844, ruptura con JS |
| **Trayectoria posterior** | Qué hizo después de dejar/ser removido | Candidato a portavoz 1844, iglesias propias (Rigdonitas, Bickertonitas) |
| **Muerte/Legado** | Fecha de defunción, herencia histórica | Fallecimiento 1876, grupos descendientes |

**Anti-patrón de incompletitud** (ejemplo real):
```
❌ "Rigdon fue excomulgado en 1844."
   - No menciona su candidatura como portavoz de la Iglesia
   - No menciona sus iglesias posteriores (Rigdonitas)
   - No menciona la iglesia Bickertonita que aún existe
   - No explica el contexto de la ruptura
```

**Estándar de completitud**:
```
✓ "Tras la muerte de José Smith, Rigdon postuló su candidatura como 
   portavoz protector de la Iglesia en agosto de 1844, argumentando 
   su posición como consejero en la Primera Presidencia. La conferencia 
   general lo rechazó por 127 votos contra 1. Posteriormente se apartó 
   completamente, organizó su propio grupo (conocido como Rigdonitas) 
   en Pittsburgh, y más tarde algunos de sus seguidores se unieron a 
   William Bickerton para formar la Iglesia de Jesucristo (Bickertonita), 
   que persiste hasta hoy. Rigdon falleció en 1876 sin reunirse con 
   los santos de Utah."
```

**Proceso cuando faltan datos**:

1. **Identificar lagunas**: marcar qué aspectos de la vida del personaje no están cubiertos
2. **Consultar fuentes**: volver a las fuentes biográficas disponibles:
   - `LDS Biographical Encyclopedia`
   - `History of the Church`
   - Fuentes del propio `prods/dyc_bios/`
   - Índice de la Triple Combinación
   - `Guide to the Scriptures`
   - `Encyclopedia of Mormonism`
   - `BYU Studies` y `RSC`
3. **Expandir la narrativa**: incorporar los hallazgos manteniendo el tono
4. **Documentar limitaciones**: si ciertos datos no están disponibles, indicarlo brevemente ("la documentación es escasa sobre sus primeros años")

**Regla de oro**: Si una biografía menciona que alguien "apostató" o "fue excomulgado", debe incluir qué hizo después y cómo terminó su vida. La historia no termina en el conflicto.

## Modo de Operación: Ininterrumpido

**Este skill opera en modo ininterrumpido.** Esto significa:

1. **NO se solicita confirmación** del usuario para ejecutar pasos
2. **NO se preguntan** "¿desea que proceda?" ni variantes
3. **SI hay marcadores ❌**, se ejecutan las correcciones automáticamente siguiendo el flujo establecido
4. **TODOS los pasos** se completan secuencialmente hasta el producto final
5. **La revisión anti-IA es SIEMPRE lo último**, aplicada sobre el texto completamente revisado

**Secuencia fija**: Paso 1 → Paso 2 → Paso 3 → Paso 3.5 (si aplica) → Paso 4 (anti-IA obligatoria al final) → Paso 5 → Entregable final

## Modo de Procesamiento por Lotes

Cuando se procesan múltiples biografías en secuencia (lotes de 10+ bios):

**Reglas de lote**:
1. **Procesar sin pausa** entre bios del mismo lote
2. **NO preguntar** "¿procedo con la siguiente?" entre bios
3. **Investigación automática**: Si una bio requiere investigación end-to-end, realizarla inmediatamente sin consultar
4. **Bibliografía automática**: Actualizar fuentes cuando se agregue información nueva
5. **Resumen por lote**: Al finalizar las 10 bios, entregar resumen breve de hallazgos y actualizar LOTE-PROGRESO.md
6. **Continuar inmediatamente** al siguiente lote sin esperar confirmación

**Optimizaciones de lote**:
- Identificar patrones comunes entre bios relacionadas (ej: varios miembros de Nauvoo House)
- Reutilizar consultas de corpus para bios del mismo período/contexto
- Priorizar bios "fáciles" primero para mantener momentum

## Flujo de Trabajo

### Paso 1: Lectura Inicial
1. Leer el archivo de biografía completo
2. Identificar el tipo de personaje (breve, importante, central)
3. Contar menciones explícitas a DyC y verificar profundidad
4. **Evaluar completitud**: ¿cubre desde origen hasta muerte/legado? ¿hay narrativa truncada en conflicto?
5. **Nota**: La revisión anti-IA se aplicará en el Paso 4, después de todas las correcciones de contenido

### Paso 2: Análisis por Categorías
Marcar cada criterio como ✅ (cumple) o ❌ (requiere corrección):

```
REPORTE DE REVISIÓN: [Nombre del personaje]

1. REDACCIÓN NATURAL Y GRAMÁTICA
   - [ ] Fluidez natural
   - [ ] Gramática correcta
   - [ ] Acentuación correcta
   - [ ] Puntuación apropiada
   - [ ] Variación de ritmo

2. LENGUAJE ACADÉMICO NATURAL
   - [ ] Tono espiritual apropiado
   - [ ] Sin jerga innecesaria
   - [ ] Precisión histórica

3. ANGLICISMOS
   - [ ] Sin palabras embebidas en inglés
   - [ ] Citas traducidas al español
   - [ ] Sin falsos amigos

4. PROFUNDIDAD DyC
   - [ ] Referencias precisas (capítulo:versículo)
   - [ ] Contexto histórico incluido
   - [ ] Función/rol explicado
   - [ ] Significado para la biografía

5. ESTRUCTURA NARRATIVA
   - [ ] Número de párrafos: 1-5 (máximo 5 estricto)
   - [ ] Densidad informativa, sin relleno
   - [ ] Orden lógico de párrafos
   - [ ] Transiciones naturales

6. REFERENCIAS META
   - [ ] Sin "del corpus"
   - [ ] Referencias naturales a fuentes

7. CITAS DE ESCRITURA
   - [ ] Referencias precisas
   - [ ] Traducciones propias si aplica

8. ANTI-IA (aplicar en Paso 4)
   - [ ] Pasada anti-IA completada después de correcciones de contenido
   - [ ] Sin patrones detectables en texto final

9. COMPLETITUD END-TO-END
   - [ ] Trayectoria completa cubierta (origen a muerte)
   - [ ] Post-excomunión/apostasía documentada si aplica
   - [ ] Fuentes consultadas para llenar lagunas
   - [ ] Sin narrativas truncadas en el conflicto

10. BIBLIOGRAFÍA
   - [ ] Fuentes presentes y pertinentes
   - [ ] Bibliografía cubre la información presentada (si se menciona carrera política, debe haber fuente biográfica)
   - [ ] Sin padding bibliográfico (fuentes no consultadas)
   - [ ] LDS Biographical Encyclopedia preferido para datos biográficos
```

### Paso 3: Corrección (si aplica)

Si hay marcadores ❌:
1. Corregir problemas de gramática y redacción
2. Eliminar anglicismos
3. Expandir menciones someras a DyC con profundidad
4. Reestructurar párrafos si es necesario
5. Reemplazar referencias meta del corpus
6. **Verificar bibliografía**: si se agregó información nueva (carrera política, llamamientos, etc.), asegurar que exista fuente biográfica apropiada (ej: *LDS Biographical Encyclopedia*)

#### Paso 3.5: Investigación de Completitud (si aplica)

Si el marcador de completitud está ❌:
1. **Listar lagunas identificadas**: qué períodos o eventos faltan
2. **Consultar fuentes biográficas**:
   - Revisar `LDS Biographical Encyclopedia` vol. 1-4
   - Buscar en `prods/dyc_bios/bios/` archivos relacionados
   - Consultar `Guide to the Scriptures`
   - Revisar Índice de la Triple Combinación
   - Si disponible: `History of the Church`, `BYU Studies`, `RSC`
3. **Expandir la narrativa**: incorporar hallazgos con precisión
4. **Verificar**: ¿la biografía ahora cubre end-to-end?

### Paso 4: Revisión Anti-IA Final (MANDATORIO - SIEMPRE AL FINAL)

**⚠️ REGLA ABSOLUTA: Este paso se ejecuta ÚNICAMENTE después de completar TODAS las correcciones de contenido.**

**Secuencia correcta**: (1) Leer → (2) Analizar → (3) Corregir contenido → (3.5) Investigar completitud → **(4) Anti-IA aquí al final** → (5) Revisión final

**Objetivo**: La revisión anti-IA debe abarcar TODO el trabajo revisado, incluyendo material investigado y expandido en los pasos anteriores.

**NO negociable**: Nunca aplicar anti-IA antes de completar las correcciones de contenido.

1. **Invocar skill `anti-ia`** en modo Rewrite sobre el texto completo ya corregido
2. **Aplicar las 36 categorías de patrones**
3. **Verificar residuos específicos**:
   - Filler phrases religiosos introducidos en correcciones
   - Lenguaje promocional en nuevas secciones de completitud
   - Uniformidad de longitud en texto expandido
   - Transiciones recicladas en material investigado
4. **Preservar**: precisión doctrinal, citas FCD, estructura narrativa

### Paso 5: Revisión Final

1. Releer el texto completo en voz alta (mentalmente)
2. Verificar que fluya naturalmente
3. Confirmar que todas las menciones a DyC tienen profundidad
4. Validar que la pasada anti-IA del Paso 4 está completa y no quedan patrones detectables
5. Verificar que no haya referencias al corpus
6. **Confirmar completitud end-to-end**: desde origen hasta muerte/legado, sin truncar en conflictos

## Entregable

Para cada biografía revisada, entregar:

```markdown
## Resumen de Revisión: [Nombre del personaje]

**Estado**: [Aprobada / Correcciones aplicadas / Requiere reescritura]

**Hallazgos principales**:
- [Lista de problemas encontrados]

**Cambios realizados**:
- [Lista de correcciones aplicadas]

**Verificaciones completadas**:
- ✅ Revisión anti-IA
- ✅ Profundidad en menciones DyC
- ✅ Redacción natural
- ✅ Sin referencias al corpus
- ✅ Completitud end-to-end

---

[TEXTO CORREGIDO si aplica, o confirmación de que cumple estándar]
```

## Ejemplos de Corrección

### Ejemplo 1: Mención somera a DyC

**Antes**:
```
Sidney Rigdon aparece en DyC 35 como escribiente.
```

**Después**:
```
Sidney Rigdon aparece a lo largo de DyC 35, 37, 40, 44, 49, 52, 58, 61, 63, 
70, 71, 73, 76, 90, 93, 100, 111, 115 y 124 como una de las figuras más 
visibles del primer período de la Restauración. Las primeras revelaciones 
lo presentan como un converso recién llegado al que el Señor había preparado 
para una obra importante, llamado a servir como escribiente de José Smith 
en la traducción de la Biblia (DyC 35:20), a ayudar a probar por las 
Escrituras las revelaciones del Profeta y a participar en la convocatoria 
de los santos a reunirse en Ohio.
```

### Ejemplo 2: Referencia al corpus

**Antes**:
```
Según las fuentes del corpus, Rigdon había sido predicador bautista.
```

**Después**:
```
Las fuentes biográficas confirman que Rigdon había sido un predicador 
influyente entre bautistas y campbelitas antes de unirse a la Iglesia.
```

### Ejemplo 3: Anglicismo en cita

**Antes**:
```
Como dijo: "I am a true follower of Christ."
```

**Después**:
```
Como expresó: "Soy un verdadero seguidor de Cristo" (traducción propia).
```

### Ejemplo 4: Completitud end-to-end

**Antes** (narrativa truncada):
```
Sidney Rigdon fue excomulgado en 1844 tras el fallecimiento de José Smith.
```

**Después** (trayectoria completa):
```
Tras el martirio de José Smith, Rigdon regresó de Pittsburgh pretendiendo 
el liderazgo de la Iglesia como "portavoz protector". En la conferencia 
de agosto de 1844, la membresía lo rechazó por abrumadora mayoría 
(127 contra 1). No aceptó la autoridad de los Doce y fue excomulgado 
en septiembre de 1844.

Posteriormente organizó su propia iglesia en Pittsburgh (los Rigdonitas), 
que pronto se dispersó. Un grupo de sus seguidores se unió a William 
Bickerton para formar la Iglesia de Jesucristo, conocida como Bickertonita, 
que persiste hasta hoy con miles de miembros. Rigdon vivió sus últimos 
años en deslinde de cualquier organización religiosa organizada, 
falleciendo en 1876 sin reunirse con los santos de Utah.
```

## Anti-patrones a Evitar

1. **Menciones de DyC sin contexto**: "Aparece en DyC 35, 37, 40..." sin explicar qué pasa en cada una
2. **Listados sin narrativa**: simplemente enumerar secciones sin tejer una historia
3. **Vaguedades en lugar de especificidad**: "el núcleo dirigente", "las autoridades" en lugar de "miembro de la Primera Presidencia", "apóstol", "obispo". Especificar el llamamiento exacto.
4. **Falta de end-to-end**: biografías que mencionan un evento crucial (como firma de revelación) sin contexto de nacimiento, trayectoria previa ni muerte/legado final
5. **Reiteraciones innecesarias**: repetir la misma idea con diferentes palabras en el mismo o en párrafos consecutivos ("aprobó y firmó", "testigo institucional", "participación directa" refiriéndose al mismo hecho)
6. **Obscurecimiento**: usar frases complejas cuando una simple basta ("su vinculación con Doctrina y Convenios lo muestra como testigo institucional" → "firmó la revelación como miembro de la Primera Presidencia")
7. **Conclusiones genéricas**: "Fue un hombre de fe" sin sustento específico del texto
8. **Forzamiento de párrafos**: exceder el máximo de 5 párrafos, expandir artificialmente a más párrafos de los que los datos justifican, o condensar en uno solo información que merece más desarrollo
9. **Orden confuso**: mezclar cronología sin transiciones claras
10. **Olvidar el anti-IA**: entregar sin la pasada obligatoria
11. **Biografías truncadas**: terminar en la excomunión/apostasía sin contar el resto de la trayectoria
12. **Falta de investigación**: no consultar fuentes cuando hay lagunas evidentes
13. **Narrativa de conflicto incompleta**: mencionar que "se apartó" sin explicar qué hizo después
14. **Bibliografía inapropiada**: fuentes que no cubren la información presentada (ejemplo: mencionar carrera política detallada pero solo citar fuentes sobre DyC)

## Recursos Relacionados

- Skill anti-ia: `.claude/skills/anti-ia/SKILL.md`
- Referencias anti-IA: `.claude/skills/anti-ia/references/`
- Biografías existentes: `prods/dyc_bios/bios/`
- Contexto general: `prods/dyc_bios/batch1_context.txt` y `batch2_context.txt`
