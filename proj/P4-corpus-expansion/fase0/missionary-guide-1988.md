# Fase 0 — Missionary Guide: Training for Missionaries (1988)

> Investigación editorial + análisis de contenido y valor KG.
> Fecha: 2026-04-15

---

## Paso 1 — Investigación editorial (web research)

### Historia editorial

- **Título EN:** *Missionary Guide: Training for Missionaries*
- **Título ES:** *Guía Misional: Capacitación para Misioneros*
- **Autor:** The Church of Jesus Christ of Latter-day Saints
- **Publicación:** 1988
- **Editor:** Departamento Misional de la Iglesia
- **Formato:** Manual impreso + escaneo PDF disponible en Archive.org
- **Fuente digital:** https://archive.org/details/MissionaryGuide (PDF 3.8 MB)
- **Texto completo:** https://archive.org/stream/MissionaryGuide/MissionaryGuide1988_djvu.txt

### Contexto institucional

El *Missionary Guide* fue el compañero pedagógico de las charlas misionales de 1986
(*Uniform System for Teaching the Gospel*). Mientras las seis charlas contenían el mensaje
doctrinal, este manual enseñaba las **habilidades** para transmitirlo. Su estructura se
basa en el **commitment pattern** (patrón de compromiso), que fue el marco pedagógico
misional desde 1986 hasta la adopción de *Preach My Gospel* en 2004.

**Cadena pedagógica misional:**
```
A Uniform System for Teaching the Gospel — 6 charlas (1986)
  → Missionary Guide: Training for Missionaries (1988) ← ESTE MATERIAL
    → Preach My Gospel (2004, revisado 2023)
```

Conocido coloquialmente como "el manual rosa" o "el rosa" por el color de su portada.

### Recepción y legado

- El RSC de BYU documentó que el comité de PMG concluyó que "no había evidencia" de que
  el aumento en habilidades misionales (como las del Missionary Guide) se correlacionara
  con bautismos. Esto motivó el cambio de filosofía: de skills a conversión.
- Sin embargo, el principio de preguntar sobrevivió: el cap. 7 ("Find Out") migró
  conceptualmente a "Haga preguntas inspiradas" en PMG cap. 10.
- Generaciones de misioneros (1988–2004) se capacitaron con este manual.

## Paso 2 — Clasificación

- **Categoría:** `manuals`
- **Ruta corpus:** `corpus/en/manuals/missionary-guide-1988/`
- **Idioma disponible:** EN (solo inglés en Archive.org; la versión ES podría existir)
- **Autoridad doctrinal:** 90 (manual oficial correlacionado de la Iglesia)
- **Autoridad de rigor:** 60 (manual de habilidades, no de doctrina)
- **Oficial:** sí

## Paso 3 — Valor KG

### Entidades esperadas
- Commitment pattern (concepto pedagógico)
- Find Out (habilidad misional = preguntar)
- Relaciones con: Preach My Gospel, TNGC, charlas misionales 1986

### Relaciones KG
- `Missionary Guide` → `PRECEDED_BY` → `Uniform System 1986`
- `Missionary Guide` → `SUCCEEDED_BY` → `Preach My Gospel 2004`
- `Missionary Guide` → `TEACHES_CONCEPT` → `Commitment Pattern`
- `Missionary Guide.ch7` → `TEACHES_CONCEPT` → `Pedagogical Questions`

## Paso 4 — Estructura del contenido

15 capítulos:

| Cap | Título | Relevancia dossier 0009 |
|-----|--------|------------------------|
| 1 | The Purpose of Missionary Work | baja |
| 2 | Christlike Attributes | baja |
| 3 | The Commitment Pattern | media (marco general) |
| 4 | Build Relationships of Trust | baja |
| 5 | Help Others Feel and Recognize the Spirit | baja |
| 6 | Present the Message | baja |
| 7 | **Find Out** | **ALTA** — preguntas como habilidad |
| 8 | Resolve Concerns | media (responder preguntas) |
| 9 | Invite | media (invitación a actuar) |
| 10 | Follow Up | baja |
| 11 | Plan | baja |
| 12 | Find People to Teach | baja |
| 13 | Teach | media |
| 14 | Baptize and Fellowship | baja |
| 15 | Leadership | baja |

## Paso 5 — Descarga y extracción ✅

- **Fuente:** Archive.org PDF + DjVu OCR text
- **PDF descargado:** `corpus/en/manuals/missionary-guide-1988/MissionaryGuide1988.pdf` (3.9 MB)
- **Método real:** PyMuPDF falló (PDF es escaneo de imagen sin capa de texto). Se descargó el texto OCR de Archive.org (`MissionaryGuide1988_djvu.txt`), se extrajo del wrapper HTML, y se dividió en 17 archivos de capítulo.
- **Formato salida:** 17 archivos .txt (front-matter + 16 capítulos) + raw-ocr-clean.txt
- **Notas de calidad:** OCR de calidad aceptable; legible y estructurado. Algunos artefactos menores (números sueltos, caracteres basura como `�`).
- **Estado:** descargado — pendiente de indexación al corpus
