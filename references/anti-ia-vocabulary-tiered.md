---
description: Tabla de reemplazos léxicos anti-IA en español, organizada por severidad (Tier 1/2/3). Equivalente al sistema de 109 reemplazos de avoid-ai-writing.
---

# Vocabulario Anti-IA por Niveles (3 Tiers)

Este documento define las palabras y frases delatoras organizadas por severidad:

- **Tier 1**: Siempre flaggear y reemplazar
- **Tier 2**: Flaggear cuando aparecen en clusters (2+ instancias cercanas)
- **Tier 3**: Flaggear solo en alta densidad (>3 por párrafo)

---

## Tier 1 - Reemplazar Siempre (24 patrones)

Palabras y frases que delatan IA de inmediato. Eliminar o reemplazar siempre.

| Palabra/Frase | Reemplazo Sugerido | Justificación |
|---------------|-------------------|---------------|
| en este sentido | (eliminar) o usar conector específico | Muletilla conectiva vacía |
| cabe destacar que | directamente | Hedging innecesario |
| es importante señalar/destacar | decir | Eufemismo académico |
| vale la pena mencionar | mencionar | Redundancia hedging |
| sin lugar a dudas | sin duda | Perífrasis grandilocuente |
| en última instancia | finalmente | Circunloquio innecesario |
| por consiguiente | entonces / así | Conector excesivamente formal |
| en el ámbito de | en / dentro de | Calco del inglés "in the landscape of" |
| en este contexto | aquí / en esto | Vaguedad situacional |
| resulta fundamental | es fundamental | Evitación de copulativa simple |
| no cabe duda | no hay duda | Fórmula rebuscada |
| podría decirse que | (eliminar, decir directamente) | Falsa humildad epistémica |
| desde una perspectiva más amplia | en general | Hedging espacial |
| es importante notar | notar | Verbo auxiliar innecesario |
| en términos generales | generalmente | Perífrasis adverbial |
| siendo importante destacar | destacar | Gerundio innecesario |
| analizando los datos | los datos muestran | Gerundio impersonal |
| conteniendo información | que contiene | Gerundio calcado del inglés |
| Certainly! / ¡Ciertamente! | (eliminar apertura) | Apertura chatbot |
| Feel free to reach out | (eliminar cierre) | Cierre chatbot |
| Here's a comprehensive overview | (eliminar) | Apertura genérica IA |
| In conclusion / En conclusión | (eliminar o integrar) | Cierre forzado |
| Moreover / Además (inicial) | (reubicar o eliminar) | Conector inicial rígido |
| Only time will tell | (eliminar) | Conclusión genérica evasiva |

---

## Tier 2 - Flaggear en Clusters (42 patrones)

Reemplazar cuando aparecen 2+ veces en un mismo párrafo o sección.

| Palabra/Frase | Contexto Delator | Alternativas |
|---------------|-----------------|--------------|
| profundizar | "Vamos a profundizar en..." | "Veamos" / "Examinemos" / (reestructurar) |
| explorar | "Exploremos el tema de..." | eliminar / "Veamos qué dice..." |
| dinamizar | uso administrativo vacío | impulsar / mover / activar |
| fomentar | uso institucional genérico | promover / ayudar / crear |
| facilitar | uso reiterado | hacer posible / permitir / ayudar |
| maximizar | lenguaje corporativo | aprovechar / obtener el máximo |
| alinear | metáfora corporativa | poner de acuerdo / coordinar |
| subrayar | uso retórico excesivo | destacar / señalar / notar |
| robusto/a | descripción técnica cliché | sólido / resistente / concreto / fuerte |
| innovador/a | adjetivo promocional vacío | nuevo / original / diferente |
| crucial / esencial | intensificación excesiva | importante / necesario / clave |
| sinérgico/a | buzzword corporativo | coordinado / conjunto / combinado |
| vibrante | lenguaje promocional | activo / lleno de vida / (eliminar) |
| vital | hiperbólico común | esencial / necesario / importante |
| transformador/a | elevación excesiva | que cambia / que transforma |
| encomiable | adjetivo valorativo genérico | digno de elogio / (eliminar) |
| ejemplar | descripción idealizada | modelo / ejemplo / buen |
| invaluable | intensificación abstracta | de gran valor / importante / (eliminar) |
| en constante evolución | frase hecha IA | que cambia / que crece |
| paisaje (metafórico) | calco de "landscape" | campo / área / terreno / panorama |
| reino (metafórico) | calco de "realm" | ámbito / esfera / campo |
| tapestria/tapiz | metáfora literaria vacía | tela / conjunto / (usar concretamente) |
| beacon/faro (metafórico) | cliché inspiracional | guía / ejemplo / luz |
| cornerstone/piedra angular | metáfora arquitectónica vacía | base / fundamento / elemento clave |
| paradigm/paradigma | término académico sobreusado | modelo / ejemplo / forma |
| underpinnings/base | calco académico | base / fundamento / soporte |
| holistic/holístico | buzzword wellness/corporativo | total / completo / integral |
| multifaceted/multifacético | descripción académica genérica | con muchas facetas / complejo |
| nuanced/nuanced | calco del inglés | matizado / con matices / sutil |
| tapestry/tapiz (metafórico) | metáfora literaria IA | tejido / conjunto / (concreto) |
| navigate/navegar (figurativo) | verbo corporativo vacío | manejar / atravesar / enfrentar |
| spearhead/encabezar | verbo heroico genérico | liderar / encabezar / dirigir |
| groundbreaking/innovador | adjetivo histriónico | nuevo / revolucionario / pionero |
| cutting-edge/de vanguardia | cliché tecnológico | nuevo / avanzado / último |
| seamless/perfecto | adjetivo promocional | sin problemas / fluido / fácil |
| empower/potenciar | verbo corporativo vacío | fortalecer / capacitar / dar poder |
| foster/fomentar | verbo institucional | promover / cultivar / crear |
| elevate/elevar | verbo abstracto | mejorar / subir / levantar |
| illuminate/iluminar | verbo retórico | aclarar / explicar / mostrar |
| facilitate/facilitar | verbo corporativo | hacer más fácil / ayudar |
| bolster/fortalecer | verbo académico | fortalecer / reforzar / apoyar |
| leverage/aprovechar | calco corporativo | aprovechar / usar / utilizar |

---

## Tier 3 - Flaggear en Alta Densidad (30 patrones)

Problema solo cuando hay 3+ instancias en un párrafo o equivalentes implícitos.

| Patrón | Ejemplo Problema | Acción |
|--------|-----------------|--------|
| Ciclo de sinónimos cíclicos | desarrolladores/practicantes/constructores/ingenieros | Elegir 1-2 términos, mantener consistencia |
| "No es X, es Y" múltiple | Más de 1 construcción contrastiva por sección | Reducir a máximo 1, variar estructura |
| Secuencia explícita numerada | "En primer lugar/En segundo lugar/Finalmente" | Usar transiciones orgánicas |
| Transiciones causales excesivas | cada párrafo con "por lo tanto", "de este modo", "así" | Permitir saltos, yuxtaposiciones |
| Frases participiales iniciales | "Reconociendo..., procedió..." (2+ por párrafo) | Variar inicios: pregunta, dato, cita |
| Gerundios acumulados | "analizando..., viendo..., comprendiendo..." | Alternar con participios, relativas |
| Dicotomías filosóficas | "no es X sino Y" + "el problema no es A sino B" | Matizar, reducir a 1 por texto |
| Listas con emoji | "- 🚀 Performance: ... - 💡 Scale: ..." | Eliminar emojis en contenido formal |
| Headers inline con viñetas | viñetas que funcionan como subtítulos | Usar estructura de párrafos real |
| Citas genéricas | "Expertos creen..." / "Estudios demuestran..." | Nombre específico, cita verificable |
| Hedging acumulativo | "podría argumentarse..." + "no es descabellado..." | Eliminar o decir directamente |
| Uniformidad de longitud | todas las frases ~15 palabras | Mezclar frases de 5 y 30 palabras |
| Tono uniformemente elevado | sin variación de registro | Alternar formal e informal |
| Resumen por sección | cada sección cierra con recapitulación | Eliminar, confiar en el lector |
| Conclusión genérica | "el futuro es brillante" / "solo el tiempo dirá" | Conclusión específica o eliminar |
| "Serves as" / "sirve como" | evitación de copulativa simple | Usar "es" directamente |
| "Featuring/presenting/boasting" | lenguaje promocional evitativo | Describir sin verbos de exhibición |
| Watershed moment/momento decisivo | hiperbólico histórico | Reducir a "importante" o específico |
| Notability name-dropping | listar 3+ nombres de prestigio seguidos | Mencionar solo los relevantes |
| False range | "de los usuarios a los CEOs" | Especificar rangos reales |
| Superficial -ing analysis | "simbolizando... reflejando... destacando..." | Análisis concreto, no listado de gerundios |
| Formulaic challenges | "A pesar de los retos, prospera" | Especificar el reto y la respuesta |
| Negative parallelism | "No es solo X, es Y" | "Es Y" directamente |
| Significance inflation | "marcó un momento decisivo para..." | Reducir intensidad o especificar |
| Copula avoidance | "se desempeña como", "funciona como" | Usar "es" |
| "In order to" / "con el fin de" | perífrasis innecesaria | "para" directamente |
| "Underscoring/destacando" | verbos metalingüísticos excesivos | Integrar en la oración principal |
| "At large" / "en general" muletilla | "...la Iglesia en general" | Especificar ámbito o eliminar |
| "Continues to" / "sigue" muletilla | "sigue prosperando" | "prospera" directamente |
| "Reflecting broader trends" | conclusión genérica evasiva | Especificar la tendencia |

---

## Sistema de Scoring

Cada instancia suma puntos según su tier:

- **Tier 1**: 3 puntos (siempre)
- **Tier 2**: 2 puntos (si está en cluster de 2+)
- **Tier 3**: 1 punto (si hay 3+ en el párrafo)

**Umbral de reescritura**: 15+ puntos en un texto → reescribir completamente.
**Umbral de patch**: 8-14 puntos → corregir por secciones.
**Umbral de limpio**: <8 puntos → revisión menor.

---

## Referencias

- Adaptado de: https://github.com/conorbronsdon/avoid-ai-writing
- Sistema de 3 tiers basado en: brandonwise/humanizer
- Investigación de patrones: Pangram Labs, Wikipedia "Signs of AI-generated text"
