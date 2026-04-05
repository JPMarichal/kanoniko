---
name: theme-detection
description: Detect theme gaps, controversies, and expansion opportunities across Formas T and other products. Outputs to prods/BACKLOG.md.
user_invocable: true
---

# Theme Detection

Analiza el estado actual de productos (Formas T, artículos) y detecta oportunidades de expansión. El resultado se escribe en `prods/BACKLOG.md`.

---

## Paso 1 — Inventario de tags transversales

Extraer todos los tags de `prods/formas-t/*.md` y cruzarlos:

```bash
for f in prods/formas-t/*.md; do
  [[ "$(basename "$f")" == "_template.md" ]] && continue
  collection=$(grep '^collection:' "$f" | head -1 | sed 's/collection: *//')
  tags=$(grep '^tags:' "$f" | sed 's/tags: *\[//;s/\]//;s/, */\n/g')
  while IFS= read -r tag; do
    [[ -n "$tag" ]] && echo "$collection|$tag"
  done <<< "$tags"
done | sort > /tmp/all_tags.txt
```

Producir:
- **Frecuencia**: tags en 2+ formas, ordenados por frecuencia
- **Cruce**: tags que aparecen en 2+ colecciones distintas (estos son los temas transversales)

## Paso 2 — Cruce con currículo oficial

Comparar los temas cubiertos en Formas T contra estos índices del corpus:

| Fuente | Ruta en corpus | Qué buscar |
|--------|---------------|------------|
| Principios del Evangelio | `corpus/es/manuals/gospel-principles/` | 47 capítulos = 47 temas doctrinales |
| Folletos didácticos | `corpus/es/manuals/teaching-pamphlets/` | 82 folletos = temas para investigadores |
| FTSOY | `corpus/es/manuals/for-the-strength-of-youth/` | 12 secciones = temas para jóvenes |
| Temas del Evangelio | `corpus/es/manuals/gospel-topics/` | Índice completo de doctrina oficial |
| Manual General | `corpus/es/manuals/general-handbook/` | Secciones 18, 27, 28 = ordenanzas |

Para cada tema del currículo, verificar si existe una Forma T que lo cubra. Marcar como:
- **Cubierto** — existe una forma o colección que lo aborda
- **Parcial** — se toca tangencialmente pero no es el foco
- **Gap** — no hay cobertura

## Paso 3 — Detección de controversias, malentendidos e inquietudes

Para cada colección existente, identificar:

1. **Controversias**: preguntas polémicas que miembros o investigadores enfrentan
   - Fuentes: Temas del Evangelio (ensayos), folletos, conferencia general
   - Patrón: "¿Por qué...?", "¿Es verdad que...?"

2. **Malentendidos comunes**: creencias populares que no son doctrina
   - Patrón: "Muchos creen que... pero la doctrina dice..."
   - Ejemplo: "La investidura es secreta" vs. "Es sagrada"

3. **Inquietudes frecuentes**: dudas legítimas que merecen respuesta clara
   - Patrón: "¿Qué pasa con los que...?"
   - Ejemplo: "¿Fieles solteros pueden alcanzar la exaltación?"

## Paso 4 — Auditoría de colecciones existentes

Para cada colección, verificar:
- ¿Hay huecos revelados por fuentes oficiales que no se leyeron al crearla?
- ¿Nuevas colecciones revelan temas que la colección existente debería cubrir?
- ¿Los campos `derived_from` y `feeds_into` están poblados donde hay conexiones reales?
- ¿Los tags son puentes efectivos entre colecciones o son solo descriptivos?

## Paso 5 — Escribir al backlog

Agregar los hallazgos a `prods/BACKLOG.md` en el formato establecido:

```markdown
### [Fecha] — Detección de temas

**Gaps identificados:**
- [ ] Tema X (fuente: Principios del Evangelio cap. N) → colección sugerida / forma sugerida
- [ ] ...

**Controversias/malentendidos:**
- [ ] Pregunta (fuente: Temas del Evangelio) → forma sugerida

**Mejoras a colecciones existentes:**
- [ ] Colección: forma faltante (razón)

**Conexiones entre colecciones:**
- [ ] Tag X conecta colección A con colección B → verificar `feeds_into`
```

## Paso 6 — Priorizar

Criterios de priorización del backlog:
1. **Raíz bíblica fuerte** — temas con ancla bíblica directa tienen prioridad
2. **Demanda del currículo** ��� si Principios del Evangelio o FTSOY lo enseñan, es esencial
3. **Controversia activa** — malentendidos que causan daño real merecen respuesta
4. **Conexión con colecciones existentes** — formas que llenan huecos en colecciones ya creadas
5. **Disponibilidad de fuentes** — temas con buen soporte en el corpus son más viables

---

## Notas

- Este skill no genera formas T directamente. Alimenta el backlog.
- La generaci��n de formas sigue el procedimiento de 3 fases (A→B→C) documentado en `procedure_forma_t_generation.md`.
- El backlog es un documento vivo. Cada ejecución del skill agrega, no reemplaza.
- El skill puede ejecutarse sobre una colección específica o sobre todo el inventario.
