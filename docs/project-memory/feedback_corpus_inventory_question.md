# Feedback: "Cuántas obras tenemos" = obras únicas, no archivos

Cuando el usuario pregunta "cuántas obras tenemos en el corpus", quiere **obras únicas** (libros, manuales, colecciones), NO archivos .txt individuales (que son capítulos/páginas/entradas).

## Nivel correcto de conteo por categoría

| Categoría | Unidad = "obra" | NO contar como obra |
|---|---|---|
| Escrituras | Libro (Génesis, Mateo, 1 Nefi…) | Capítulo individual |
| Conferencia general | Sesión semestral (abr 2024) | Discurso individual |
| Manuales | Publicación (CFM 2025, Saints vol. 1, Preach My Gospel) | Capítulo/lección |
| Ayudas de estudio | Obra completa (GEE, TG, BD) | Entrada individual |
| Música | Colección (Himnos, Canciones para niños) | Himno individual |
| Libros | Título (Articles of Faith, Jesus the Christ) | Capítulo |
| Proclamaciones | Documento individual | — |
| Web | Sitio/fuente | Página individual |

## Cifras de referencia (abril 2025, EN solamente)

- ~316 obras únicas EN
- ~530 obras únicas bilingües (EN+ES)
- 29,412 archivos indexados (capítulos/páginas)
- Estas cifras cambian con cada adición al corpus; recalcular cuando se pregunte

## Cómo recalcular

Para categorías con estructura `{lang}/{cat}/{obra}/{cap}.txt`: contar subdirectorios con contenido.
Para categorías anidadas (`{lang}/{cat}/{obra}/{subobra}/{cap}.txt`): contar al nivel de subobra.
Para escrituras (`{lang}/scriptures/{vol}/{book}/{ch}.txt`): contar al nivel de libro.

La pregunta se hará con frecuencia — tener el script listo.
