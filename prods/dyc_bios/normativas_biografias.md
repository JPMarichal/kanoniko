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

3. **Límite Flexible de 1 a 5 Párrafos:**
   La estructura narrativa debe condensarse en un mínimo de **1 párrafo** y un máximo de **5 párrafos** integrales y bien cohesionados. La extensión debe ajustarse a la densidad real de evidencia disponible para cada personaje; no se debe forzar una longitud mayor cuando eso produzca relleno.

4. **Tono FCD (Formal, Claro y Devocional/Académico):**
   El perfil debe redactarse con rigor enciclopédico e histórico, manteniendo un respeto solemne por la narrativa de la Restauración pero con la exactitud documental de una obra académica.

5. **Formato Citas en Texto y Bibliografía:**
   - La procedencia de los datos debe citarse entre paréntesis directamente en el texto (ej. *Revelaciones en contexto, "El tabaco"*).
   - La cita en texto debe nombrar la obra que realmente sostiene la afirmación publicada. No se debe usar una cita genérica o de apoyo como sustituto de la fuente biográfica o contextual que aportó el dato.
   - El documento debe finalizar con un encabezado `### Bibliografía` que enumere las obras bibliográficas que sostienen materialmente la redacción final, utilizando viñetas (`- *Título*, Autor/Sección.`).
   - La matriz sigue gobernando la consulta previa, pero la bibliografía visible al lector no debe ser un volcado mecánico de toda la fila ni una plantilla fija repetida; debe reflejar de forma proporcionada la huella real de las fuentes en el texto final.
   - Instrumentos internos o de control, como `namelist_with_passages.md`, pueden ser obligatorios en el flujo de trabajo, pero no deben aparecer en la bibliografía final para el lector.

6. **Flujo de Trabajo Técnico Requerido (WSL + PowerShell Heredoc):**
   - Las búsquedas de precisión y verificación térmica de eventos deben realizarse exhaustivamente mediante `grep` a través de **WSL bash** apuntando al directorio `corpus/`.
   - La redacción y volcado final del archivo `.md` debe ejecutarse rigurosamente utilizando **Heredoc en PowerShell** (`Set-Content -Encoding UTF8`) para asegurar la ininterrupción de tokens y la fidelidad del archivo.
