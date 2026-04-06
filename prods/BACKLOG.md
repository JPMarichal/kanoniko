# Backlog de productos

Semilla mantenible para nuevas Formas T, artículos y otros productos. Alimentado por el skill `/theme-detection` y por observaciones durante el trabajo.

**Protocolo:** Cada ítem incluye fuente de detección, tipo de producto sugerido y prioridad. Los ítems se marcan `[x]` al completarse, no se borran (sirven como historial).

---

## Gaps en la senda de los convenios

Temas del currículo oficial sin cobertura o con cobertura parcial en Formas T.

### Principios del Evangelio — capítulos sin Forma T

- [ ] **Nuestro Padre Celestial** (cap. 1) → colección: naturaleza de Dios
- [ ] **Nuestra familia celestial** (cap. 2) → colección: plan de salvación
- [ ] **Jesucristo, nuestro Salvador** (cap. 3) → colección: Jesucristo
- [ ] **La libertad de escoger** (cap. 4) → parcial: senda-albedrio-y-convenios
- [ ] **La Creación** (cap. 5) → colección: plan de salvación
- [ ] **La caída de Adán y Eva** (cap. 6) → colección: plan de salvación
- [ ] **La fe en Jesucristo** (cap. 18) → colección: primeros principios
- [ ] **El arrepentimiento** (cap. 19) → colección: primeros principios
- [ ] **El día de reposo** (cap. 24) → forma individual o colección: vida del convenio
- [ ] **El ayuno** (cap. 25) → forma individual
- [ ] **El sacrificio** (cap. 26) → forma individual o colección: vida del convenio
- [ ] **El servicio** (cap. 28) → forma individual
- [ ] **La ley de salud del Señor** (cap. 29) → colección: mandamientos
- [ ] **El diezmo y las ofrendas** (cap. 32) → forma individual o colección: vida del convenio
- [ ] **La obediencia** (cap. 35) → forma individual
- [ ] **La ley de castidad** (cap. 39) → colección: mandamientos
- [ ] **El mundo de los espíritus** (cap. 41) → colección: plan de salvación
- [ ] **La segunda venida** (cap. 44) → colección: últimos días
- [ ] **El Milenio** (cap. 45) → colección: últimos días
- [ ] **El juicio final** (cap. 46) → colección: plan de salvación
- [ ] **La exaltación** (cap. 47) → parcial: senda-la-exaltacion

### FTSOY — secciones sin Forma T directa

- [ ] **Tu cuerpo es sagrado** (sec. 10) → colección: mandamientos (castidad, Palabra de Sabiduría)
- [ ] **La verdad te hará libre** (sec. 11) → forma individual: verdad y discernimiento

---

## Controversias y malentendidos

Preguntas frecuentes que merecen tratamiento en Forma T (enseñanza, no apologética).

### Investidura

- [ ] ¿La investidura es secreta? → sagrado vs. secreto (Temas del Evangelio: Templos)
- [ ] ¿Han cambiado las ordenanzas del templo? → desarrollo legítimo vs. cambio doctrinal (Temas históricos)

### Sellamiento

- [ ] ¿Los fieles solteros pueden alcanzar la exaltación? → MG 38.4.1; promesa profética
- [ ] ¿Por qué se requiere matrimonio para la exaltación? → DyC 131:1-4; contexto doctrinal
- [ ] ¿Qué pasa con las familias parcialmente activas? → misericordia + agencia

### Bautismo

- [ ] ¿Los niños que mueren sin bautismo se pierden? → Moroni 8; DyC 137:10
- [ ] ¿Por qué bautizarse si Cristo no tenía pecado? → 2 Nefi 31:5-9; cumplir toda justicia

### Sacerdocio

- [ ] ¿Pueden las mujeres tener el sacerdocio? → autoridad vs. poder; convenios del templo
- [ ] ¿Por qué la restricción histórica del sacerdocio? → DyO 2; Temas del Evangelio

### Santa Cena

- [ ] ¿Es la Santa Cena solo un símbolo? → ordenanza real con convenio real; diferencia con otras iglesias
- [ ] ¿Por qué agua y no vino? → DyC 27:2-3; contexto histórico

### Espíritu Santo

- [ ] ¿Cuál es la diferencia entre el Espíritu Santo y la Luz de Cristo? → parcial: espiritu-santo-luz-de-cristo
- [ ] ¿Pueden los no miembros sentir el Espíritu? → influencia vs. don

---

## Colecciones potenciales (fuera de la senda actual)

Agrupaciones temáticas sugeridas por el análisis de tags y currículo.

- [ ] **Plan de salvación** — Creación, Caída, Expiación, mundo de espíritus, juicio, reinos de gloria
- [ ] **Primeros principios** — Fe, arrepentimiento (anclan la senda antes del bautismo)
- [ ] **Jesucristo** — vida, ministerio, Expiación, títulos, Segunda Venida
- [ ] **Mandamientos** — castidad, Palabra de Sabiduría, diezmo, día de reposo
- [ ] **Vida del convenio** — ayuno, oración, servicio, obediencia (el "vivir" la senda, no solo recibirla)
- [ ] **Últimos días** — señales, Segunda Venida, Milenio, juicio final
- [ ] **La Apostasía y la Restauración** — tag `restauracion` cruza vidas + bautismo + sacerdocio; merece colección propia
- [ ] **Profetas** — Principios del Evangelio cap. 9; revelación continua; sucesión apostólica

---

## Nuevo tipo de producto: Discursos

Producto diseñado (2026-04-05). Borradores completos de discursos grounded en el corpus, calibrados para traducción simultánea. Template y guía de estilo en `prods/discursos/`.

- Columna vertebral flexible (escrituraria, conceptual, narrativa) en modo singular o progresión
- Default 8 min (~950 palabras con traducción), escalable a 15 min
- Conectado a Formas T (source_forms) y Dossiers (source_dossiers)

---

## Nuevo tipo de producto: Ilustraciones

Producto diseñado (2026-04-06). Biblioteca de ilustraciones retóricas extraídas del corpus, listas para uso en discursos, artículos y dossiers. Doble rol: recurso cross-product + producto extractable.

- Estructura en `prods/ilustraciones/` con metadata (forma, objetivo, autor, fuente, parafraseada)
- Skill `/ilustracion` para extracción del corpus
- Fuentes primarias: conferencia general, revistas de la Iglesia
- Integrado en templates de dossiers (sec. 7), GUIDELINES de discursos (sec. 6), y skill de artículos

---

## Mejoras a colecciones existentes

- [x] Investidura: agregar "Investidos antes de ir" (forma 3) — completado 2026-04-05
- [ ] Tags: auditar que los tags sean puentes entre colecciones, no solo descriptivos
- [ ] `derived_from` / `feeds_into`: poblar en formas que tengan conexiones reales

---

## Historial de detecciones

| Fecha | Método | Hallazgos | Acción |
|-------|--------|-----------|--------|
| 2026-04-05 | Manual (revisión de session) | "Investidos antes de ir" faltante | Creada forma investidura #3 |
| 2026-04-05 | Análisis de tags + currículo | 20+ gaps en Principios del Evangelio, 12 controversias, 8 colecciones potenciales | Backlog inicial creado |
