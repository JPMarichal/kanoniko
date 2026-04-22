# Fase 0 — *The Sweet Singer of Israel: David Hyrum Smith* (Paul Edwards)

> Fecha: 2026-04-22. Epub en `epub/!Ready/Let us shake off the coals from our garments_br_As break off the yoke of our bond - Boyd K. Packer.epub` (**nota: archivo mislabeled, ver §1**).

---

## 1. Caso del archivo mislabeled

El epub tiene metadata OPF incorrecta:
- **OPF `<dc:title>`**: `"Let us shake off the coals from our garments_br_And arise in the strength of our Lord_br_Let us break off the yoke of our bond"` (una cita de Packer, no un título de obra)
- **OPF `<dc:creator>`**: `"Boyd K. Packer"`
- **CONTENIDO REAL**: un artículo de Paul Edwards titulado *"The Sweet Singer of Israel: David Hyrum Smith"*

Probablemente el epub se ensambló uniendo metadata de un documento con el cuerpo de otro por error de OCR/scraper. El contenido es íntegro (28 KB de texto, con bibliografía numerada al final y cierre limpio); no falta material.

**Decisión**: incorporar bajo el título y autor correctos (Paul Edwards), no bajo Packer. Slug: `the-sweet-singer-of-israel`. En el extract se override con `--slug` y `--author`. Procedencia documentada aquí.

## 2. Qué es

Ensayo histórico-biográfico sobre **David Hyrum Smith** (1844–1904), el quinto hijo vivo del profeta José Smith Jr. y hermano menor de Joseph Smith III. Examina a David Hyrum como poeta, misionero RLDS, figura triste atrapada entre el legado de su padre y su propia búsqueda espiritual. Incluye extractos de su poesía ("Let me be happy too...") y correspondencia.

- **Autor**: Paul Edwards — historiador RLDS, presidente de Park College, director del Temple School Graduate Institute. Miembro de la Community of Christ (antes RLDS), no de la Iglesia SUD.
- **Publicación original**: probablemente BYU Studies o Dialogue (requiere verificación). El texto cita "RLDS History", cartas de Joseph Smith III, Autumn Leaves, Saints' Herald — fuentes primarias RLDS. No hay fecha explícita en el cuerpo; la bibliografía termina con referencia a "Anderson, Mary Audentia" (1952) y un marcador "2014" al final (posiblemente fecha de digitalización).

## 3. Quién es el sujeto

**David Hyrum Smith** (1844–1904):
- Nacido póstumamente 5 meses después del martirio de su padre.
- Poeta, artista, misionero de la Reorganized Church of Jesus Christ of Latter Day Saints (ahora Community of Christ).
- Figura trágica: sus últimos ~25 años los pasó en asilos mentales tras colapso psicológico a mediados de los 1870s.
- Figura periférica pero importante para estudios de la historia SUD porque representa la línea RLDS-Brighamita dividida tras la muerte del profeta.

## 4. Relaciones con el corpus existente

- **KG entities a crear/verificar**:
  - `David Hyrum Smith` (posible nuevo nodo)
  - `Paul Edwards` (autor — nuevo)
  - `Community of Christ` / `RLDS` (contexto denominacional)
- **KG entities existentes conectadas**:
  - José Smith Jr. (padre)
  - Joseph Smith III (hermano mayor, líder RLDS)
  - Emma Smith (madre)
- **Continuidad temática**: complementa material sobre la familia Smith y la bifurcación post-martirio. No hay obras RLDS significativas en el corpus actualmente.

## 5. Evaluación (→ sidecar)

| eje | valor | justificación |
|---|---|---|
| category | **biographies** | biografía de persona histórica |
| authority | 20 | scholarship académico, pero Edwards es RLDS (no SUD) y la obra no es endosada oficialmente; autoridad doctrinal baja |
| rigor | 70 | ensayo académico con bibliografía extensa, fuentes primarias citadas |
| importance | complementario | figura periférica; útil para estudios genealógicos y comparativos |
| official | false | |
| current | true | |
| context | scholarly | ensayo académico |
| audience | scholarly | lectores con interés histórico-teológico |
| tags | `["biography", "david-hyrum-smith", "joseph-smith-family", "rlds", "community-of-christ", "church-history", "poetry"]` | |

## 6. Acción operacional

1. Extract con overrides: `--slug the-sweet-singer-of-israel --author "Paul Edwards" --category biographies`
2. El archivo EPUB source con nombre mislabeled queda registrado en `source_file` del meta.json (trazabilidad del error).
3. Tras incorporar, mover el epub source a `epub/!Done/` — renombrarlo NO (preservar evidencia del mislabel).

## Nota

Vale la pena, en un futuro, buscar la fuente original limpia. Si es BYU Studies, el skill `/byu-studies` podría conseguir una versión con metadata correcta. Por ahora el texto existente es suficiente y completo.
