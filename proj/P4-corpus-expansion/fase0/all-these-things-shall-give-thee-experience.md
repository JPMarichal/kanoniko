# Fase 0 — *All These Things Shall Give Thee Experience* (Neal A. Maxwell)

> Fecha: 2026-04-23. Epub en `epub/!Ready/All These Things Shall Give Thee Experience - Neal A. Maxwell.epub`.

---

## 1. Qué es

Tratado doctrinal-pastoral de Maxwell sobre la adversidad y el propósito divino en el sufrimiento humano. El título proviene de **DyC 122:7** ("todas estas cosas te servirán de experiencia, y serán para tu bien"), la revelación dada al profeta José Smith en la cárcel de Liberty.

10 capítulos: prefacio + Hard Doctrines and God's Love + The Omniscience of an Omnipotent and Omniloving God + The Fellowship of His Sufferings + Service and the Second Great Commandment + Growth Through Counsel, Correction, and Commendation + Prayer and Growth + Follow the Brethren + Our Moment in Time.

- **Publicado:** 1979 por **Bookcraft**.
- **Idioma original:** inglés.
- **Extensión:** ~230 KB de texto. Calibre reflow con **spine duplicado** (cada capítulo listado dos veces en la misma manifest; el extractor tras esta incorporación lleva dedup automático por signature de contenido).

## 2. Quién lo produjo

Neal A. Maxwell (1926-2004), al momento de la publicación (1979) era **Asistente a los Doce** (llamado julio 1974) y pronto sería llamado al Quórum de los Doce Apóstoles (julio 1981). Este libro pertenece a su prolífica producción doctrinal pre-apostolado pleno. Escrito en capacidad personal, Bookcraft como editorial — no hay comisión formal del FP ni imprimatur institucional.

GA private author — not FP-commissioned (authority 40 en `docs/authority-model.md`).

## 3. Cuándo y cómo se ha usado

- Referencia clásica sobre teodicea SUD: cómo reconciliar la bondad de Dios con el sufrimiento.
- Ampliamente citado en discursos de conferencia posteriores del mismo Maxwell y otros GAs.
- Tratamiento denso, literario, alusivo — característico del estilo Maxwell. Cita abundantemente las escrituras y la poesía.

## 4. Relaciones con el corpus existente

- **KG entities:**
  - Neal A. Maxwell (ya presente como autor de ~50 charlas de conferencia en `en/general-conference/`).
  - Conceptos centrales: Teodicea, Adversity, Omniscience, Fellowship of His Sufferings (cristología paulina), Providence, Prayer.
  - DyC 122:7 como ancla escritural del libro completo.
- **Continuidad temática:** línea de teodicea Maxwell (junto con *If Thou Endure It Well*, *But for a Small Moment* del mismo lote).
- **Primer libro de Maxwell en corpus:** el corpus tenía 0 libros de Maxwell antes de este batch.

## 5. Evaluación (→ sidecar)

| eje | valor | justificación |
|---|---|---|
| authority | 40 | GA privado (Asistente a los Doce al publicar), Bookcraft sin comisión formal |
| rigor | 70 | Maxwell es literario-denso, usa griego del NT, cita poesía, tratamiento cuidadoso |
| importance | importante | obra de referencia en teodicea SUD; inicio del arco doctrinal adversity de Maxwell |
| official | false | Bookcraft privado |
| current | true | citada vigentemente |
| context | book-private | |
| audience | adult | lectura densa, requiere madurez espiritual |
| tags | `["theodicy", "adversity", "apostle-authored", "bookcraft", "divine-purpose", "suffering", "dc-122"]` | |

## 6. Procedencia

- Publicado 1979 por Bookcraft Publishers, Salt Lake City.
- Epub: reflow Calibre con duplicación de spine (Calibre a veces exporta el árbol HTML dos veces). El extractor hace dedup automática.
- Sin `source_url` público.

## Nota del proceso

Este es el primer epub procesado que exhibe duplicación de spine. Se agregó dedup por signature de contenido (primeros 500 chars del texto concatenado por archivo) al extractor en el mismo commit. Futuros Calibre con el mismo defecto se procesarán limpiamente.
