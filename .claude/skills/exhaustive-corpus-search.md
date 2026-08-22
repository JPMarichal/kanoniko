---
description: Búsqueda exhaustiva y no limitativa en el corpus Alejandría para cualquier tema. Usa la API REST para acceder a múltiples fuentes sin conformarse con resultados limitados.
---

# Skill: Búsqueda Exhaustiva en Corpus

## Propósito
Realizar búsquedas exhaustivas y no limitativas en el corpus Alejandría para CUALQUIER tema (doctrinal, histórico, biográfico, etc.), usando la API REST para acceder a múltiples fuentes sin conformarse con resultados limitados.

## Cuándo usar
- Para CUALQUIER búsqueda de información en el corpus Alejandría
- Cuando el usuario exija exhaustividad y no conformarse con una sola fuente
- Para investigar temas doctrinales, históricos, biográficos, etc.
- Cuando se necesite perspectiva completa desde múltiples fuentes

## Protocolo de Búsqueda Exhaustiva

### Fase 1: Estrategia de Múltiples Fuentes del Corpus (OBLIGATORIO)

**Nunca conformarse con una sola fuente del corpus.** Debes buscar sistemáticamente en TODAS las categorías del corpus:

1. **Escrituras** (`corpus/{lang}/scriptures/`)
   - Pasajes relevantes al tema
   - Referencias cruzadas
   - Contexto doctrinal

2. **Conferencias Generales** (`corpus/{lang}/general-conference/`)
   - Discursos que mencionen el tema directamente
   - Discursos con ejemplos o aplicaciones del tema
   - Discursos de Autoridades Generales relacionadas

3. **Revistas (Liahona/Ensign)** (`corpus/{lang}/magazines/`)
   - Artículos específicos sobre el tema
   - Entrevistas y perfiles
   - Artículos de aplicación práctica

4. **Biografías** (`corpus/{lang}/biographies/`)
   - Biografías de líderes relacionados
   - Biografías de figuras históricas
   - Memorias y autobiografías

5. **Manuales de la Iglesia** (`corpus/{lang}/manuals/`)
   - Manuales de Institutos
   - Teachings of Presidents
   - Manuales de Seminario
   - Saints (historia de la Iglesia)

6. **Ayudas de Estudio** (`corpus/{lang}/study-aids/`)
   - Guías de estudio
   - Topical guides
   - Materiales de referencia

7. **Libros** (`corpus/{lang}/books/`)
   - Libros históricos
   - Libros doctrinales
   - Obras académicas

8. **Contenido Web** (`corpus/{lang}/web/`)
   - Artículos de Church News
   - Otros recursos web integrados

### Fase 2: Uso de API REST (OBLIGATORIO)

**SIEMPRE usar la API REST** para búsquedas en el corpus para evitar problemas con caracteres especiales en nombres de archivo:

```bash
# Búsqueda híbrida en todo el corpus
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "TÉRMINO DE BÚSQUEDA",
  "limit": 15
}'

# Búsqueda específica por término
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "TÉRMINO ALTERNATIVO",
  "limit": 15
}'
```

**Prohibido:** Intentar leer directamente archivos del sistema de archivos si tienen caracteres especiales en el nombre (comillas, paréntesis, etc.). Usar siempre la API REST para estos casos.

### Fase 3: Iteración de Búsqueda con Múltiples Términos

Para cada búsqueda exhaustiva, usar **5-10 términos diferentes** para maximizar cobertura:

1. Término principal + contexto general
2. Término principal + categoría específica (ej. "scripture", "conference", "magazine")
3. Término principal + aspecto doctrinal
4. Término principal + aspecto histórico
5. Término principal + aplicación práctica
6. Sinónimos o términos relacionados
7. Términos en inglés y español (búsqueda bilingüe)
8. Nombres propios relacionados
9. Citas o referencias bíblicas asociadas
10. Términos específicos del contexto histórico o geográfico

### Fase 4: Verificación de Cobertura del Corpus

Antes de pasar a complementación online, verificar que has agotado recursos del corpus:

- [ ] Escrituras consultadas
- [ ] Conferencias generales consultadas
- [ ] Revistas consultadas
- [ ] Biografías consultadas
- [ ] Manuales consultados
- [ ] Ayudas de estudio consultadas
- [ ] Libros consultados
- [ ] Contenido web consultado
- [ ] Mínimo 5-10 términos de búsqueda diferentes usados
- [ ] Mínimo 3 categorías del corpus consultadas

### Fase 5: Complementación Online (SOLO después de agotar corpus)

**Solo después de agotar TODOS los recursos del corpus**, complementar con búsqueda online:

1. **Documentación-first**: Corpus → KBA → Web
2. **Búsqueda web** solo cuando:
   - El corpus no tiene información sobre el tema
   - El corpus tiene información incompleta
   - Se necesita contexto actualizado
   - Se requiere información externa específica

3. **Prioridad siempre**: Corpus primero, web después

## Ejemplo de Flujo Completo

### Ejemplo Genérico: Búsqueda sobre "Expansión del Sacerdocio"

**Búsqueda 1:** Término principal general
```bash
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "priesthood expansion",
  "limit": 15
}'
```

**Búsqueda 2:** Término + categoría específica
```bash
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "priesthood expansion conference",
  "limit": 15
}'
```

**Búsqueda 3:** Término + aspecto doctrinal
```bash
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "priesthood authority revelation",
  "limit": 15
}'
```

**Búsqueda 4:** Término + aspecto histórico
```bash
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "priesthood history 1978",
  "limit": 15
}'
```

**Búsqueda 5:** Término + aplicación práctica
```bash
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "priesthood blessings youth",
  "limit": 15
}'
```

**Búsqueda 6:** Sinónimos en inglés/español
```bash
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "sacerdocio extensión",
  "limit": 15
}'
```

**Búsqueda 7:** En revistas
```bash
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "priesthood Ensign Liahona article",
  "limit": 15
}'
```

**Búsqueda 8:** En manuales
```bash
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "priesthood manual handbook",
  "limit": 15
}'
```

**Búsqueda 9:** En biografías de líderes relacionados
```bash
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "Kimball priesthood expansion",
  "limit": 15
}'
```

**Búsqueda 10:** En escrituras
```bash
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "priesthood Doctrine and Covenants",
  "limit": 15
}'
```

## Reglas de Calidad

### Exhaustividad
- **Mínimo 3 categorías del corpus** consultadas antes de sintetizar
- **Mínimo 5-10 llamadas a API** con términos variados
- **Verificar duplicados** - no contar la misma fuente dos veces
- **Agotar recursos del corpus** antes de buscar online

### Precisión
- **Usar FCD** para todas las citas del corpus
- **Distinguir fuentes** - identificar claramente qué información viene de dónde
- **No mezclar** - no fusionar información sin atribución clara
- **Atribuir fuentes externas** si se complementa con búsqueda web

### No Limitación
- **Buscar activamente** en todas las categorías del corpus
- **No detenerse** en la primera fuente encontrada
- **Explorar** rutas alternativas (revistas, conferencias, manuales, libros, web)
- **Usar múltiples términos** para maximizar cobertura

### Prioridad
- **Corpus primero** - siempre consultar el corpus antes de buscar web
- **Documentación-first** - corpus → KBA → web
- **No saltar al web** sin exhaustivamente buscar en el corpus

## Output Esperado

Una síntesis que incluya:
1. **Información completa** del tema desde múltiples perspectivas del corpus
2. **Detalles específicos**: fechas, lugares, circunstancias, aplicaciones prácticas
3. **Múltiples perspectivas**: de escrituras, conferencias, revistas, manuales, libros, etc.
4. **Citas FCD** para cada hecho importante del corpus
5. **Atribución de fuentes externas** si se complementa con búsqueda web
6. **Fuentes consultadas**: lista completa del corpus y web (si aplica)
7. **Gaps identificados**: información no encontrada en el corpus para complementación futura

## Comandos de Diagnóstico

Si no se encuentra información adicional en el corpus:
```bash
# Búsqueda más amplia con términos relacionados
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "TÉRMINO RELACIONADO",
  "limit": 20
}'

# Búsqueda en español e inglés
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "TÉRMINO EN INGLÉS",
  "limit": 15
}'

# Búsqueda con contexto específico
curl -s "http://localhost:4300/search/hybrid" -X POST -H "Content-Type: application/json" -d '{
  "query": "TÉRMINO CONTEXTO HISTÓRICO",
  "limit": 15
}'
```
