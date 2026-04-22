# Fase 0 — *Boyd K. Packer: Una selección de discursos*

> Fecha: 2026-04-22. Epub en `epub/!Ready/Boyd K. Packer_ Una selección de discursos - Boyd K. Packer.epub`.

---

## 1. Qué es

Antología de discursos de Packer publicada por los centros de distribución de la Iglesia como parte de una **serie** titulada "Una selección de discursos" que abarca múltiples apóstoles:

- Boyd K. Packer (esta obra)
- Bruce R. McConkie
- Ezra Taft Benson
- Gordon B. Hinckley
- Jeffrey R. Holland
- Joseph B. Wirthlin

En el lote `epub/!Ready/` están los 6 volúmenes. Este Fase 0 cubre solo el de Packer.

El volumen contiene 36 discursos seleccionados cubriendo décadas de ministerio (desde CES addresses antiguos hasta discursos tardíos como "Acting President of the Q12").

## 2. Quién lo produjo

Compilación editorial de la Iglesia (Departamento de Traducción / Centros de Distribución) para distribución en idioma español. Los textos individuales son discursos de Packer en diversos contextos (General Conference, CES, regional conferences, BYU addresses). La selección es editorial.

## 3. Relaciones con el corpus existente

- **Overlap esperado con `corpus/en/general-conference/`**: muchos de los 36 discursos tienen contraparte en General Conference sessions. No se deduplica en esta ingesta; se documenta y se hace auditoría post-ingesta.
- **Overlap con `corpus/en/discourses/let-not-your-heart-be-troubled/`**: pieces como "El don de saber escuchar" / "Feed My Sheep" pueden solaparse.
- **Continuidad de serie Packer**: junto con *Holy Temple*, *Eternal Love*, *Let Not Your Heart Be Troubled*, *Enseñad Diligentemente* completa (con el "Let us shake off" pendiente de validar) el cluster Packer del lote.

## 4. Calidad del source — IMPORTANTE

El epub es una **reconversión PDF → EPUB de un folleto** impreso en columnas. El reflow resultó en **interleaving de líneas entre columnas**: texto de la columna izquierda y derecha aparece mezclado línea por línea en vez de leerse columna por columna.

Ejemplo (discurso 05, "Autosuficiencia emocional"):
> "Nuestros obispos notan un aumento en la personas ven seguridad material."

Se lee: "Nuestros obispos notan un aumento en la [salto-columna-derecha] personas ven seguridad material." — dos líneas de columnas distintas intercaladas.

**Implicación:** las búsquedas semánticas y textuales funcionarán parcialmente porque los tokens están presentes, pero la lectura humana del texto quedará confusa y el KG tendrá relaciones de bajo-señal. La deduplicación con el corpus de conferencia (que sí tiene texto limpio) resolverá este problema cuando se haga el audit.

**Decisión:** incorporar de todos modos — cubre discursos no presentes en `general-conference/` por ser CES/regional/pre-TV. Marcar `rigor` bajo (45) y `note` con la caveat explícita. El par EN puede sobrescribir cuando aparezca.

## 5. Qué se filtró manualmente antes del promote

- **Capítulo 1 "indice"** (TOC fragmentado, ~100 chars de líneas sueltas como "Pag. SABER. PRECIOSAS.") — eliminado antes del promote por ser basura documental sin valor.

## 6. Duplicado interno observado

Dos discursos con el título "El obispo y sus consejeros" (capítulos 23 y 29 tras extract). Son piezas distintas de Packer sobre el mismo tema (uno firmado "Presidente Packer, Presidente en Funciones del Q12" = post-2008; otro con encabezado más antiguo). Se mantienen ambos; los slugs difieren por prefijo numérico.

## 7. Evaluación (→ sidecar)

| eje | valor | justificación |
|---|---|---|
| category | **discourses** | override — antología de discursos |
| authority | 55 | compilación ES oficial distribuida por la Iglesia; los discursos individuales son de Packer como Q12/acting-president. Más alto que *Let Not Your Heart Be Troubled* (40) porque esta es publicación oficial de la Iglesia, no Bookcraft privado. |
| rigor | 45 | rebajado del natural por el interleaving de columnas en el source |
| importance | importante | recoge discursos no presentes en `general-conference/` |
| official | true | publicada oficialmente por centros de distribución SUD |
| current | true | distribuida hasta al menos 2010 |
| context | book-private | no revelatorio institucional, pero publicación oficial |
| audience | general | |
| tags | `["discourses", "apostle-authored", "spanish-translation", "church-publication", "anthology", "packer-series"]` | |

## 8. Procedencia

- Publicado por Centros de Distribución de La Iglesia de Jesucristo de los Santos de los Últimos Días, en la serie "Una selección de discursos".
- Fecha OPF: 2008-05-29 (fecha de digitalización/ingesta del epub, no de publicación original).
- Sin `source_url` público.

## Notas del proceso

**Bug del extractor descubierto y corregido durante esta incorporación**: 14 archivos de 39 tenían h2 real, 25 tenían solo first_bold como título de discurso. Mi `any_heading` binario global hacía que los 25 files-sin-heading no recibieran chapter boundary. Fix: decisión per-archivo (`file_has_real_heading[i]`) que usa h1/h2 cuando existe, fallback a first_bold cuando no.
