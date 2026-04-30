# Normativas y Estándares para la Generación de Biografías

Este documento establece las reglas fundamentales que rigen y regulan la creación de todas las biografías correspondientes al proyecto de Doctrina y Convenios.

## Base de Partida
Toda generación e investigación biográfica debe tomar como fundamento estricto y punto de partida indiscutible los siguientes documentos:
1. `matriz_de_fuentes.md`: Define el corpus histórico autorizado, la jerarquía de las fuentes y el alcance documental.
2. `namelist_with_passages.md`: Proporciona la lista de personajes, las referencias cruzadas iniciales y las secciones específicas de Doctrina y Convenios asociadas a cada individuo.

---

## Las 6 Reglas de Oro

1. **100% Basado en el Corpus Local (Cero Alucinaciones):**
   Absolutamente toda afirmación, fecha, evento, anécdota o relación debe tener su origen demostrable en los textos del corpus local (manuales del SEI, *Santos*, *Revelaciones en contexto*, *LDS Biographical Encyclopedia*, etc.). Está prohibido rellenar vacíos utilizando conocimiento general del LLM.

2. **Exhaustividad Escritural e Histórica:**
   La biografía debe abordar y conectar obligatoriamente al personaje con las secciones específicas de Doctrina y Convenios en las que participó, fue mencionado o tuvo influencia directa (ej. la influencia en el trasfondo histórico).

3. **Límite Estricto de 5 Párrafos:**
   La estructura narrativa debe condensarse en un máximo (y preferiblemente exacto) de **5 párrafos** integrales y bien cohesionados. No se permite exceder esta restricción bajo ninguna circunstancia.

4. **Tono FCD (Formal, Claro y Devocional/Académico):**
   El perfil debe redactarse con rigor enciclopédico e histórico, manteniendo un respeto solemne por la narrativa de la Restauración pero con la exactitud documental de una obra académica.

5. **Formato Citas en Texto y Bibliografía:**
   - La procedencia de los datos debe citarse entre paréntesis directamente en el texto (ej. *Revelaciones en contexto, "El tabaco"*).
   - El documento debe finalizar con un encabezado `### Bibliografía` que enumere las obras consultadas utilizando viñetas (`- *Título*, Autor/Sección.`).

6. **Flujo de Trabajo Técnico Requerido (WSL + PowerShell Heredoc):**
   - Las búsquedas de precisión y verificación térmica de eventos deben realizarse exhaustivamente mediante `grep` a través de **WSL bash** apuntando al directorio `corpus/`.
   - La redacción y volcado final del archivo `.md` debe ejecutarse rigurosamente utilizando **Heredoc en PowerShell** (`Set-Content -Encoding UTF8`) para asegurar la ininterrupción de tokens y la fidelidad del archivo.
