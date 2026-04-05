# Corpus Inventory

Inventario actualizado del material ya ingresado en el corpus de Alejandría.
Para ver qué queda pendiente → `04-backlog.md`.
Para catálogos de fuentes externas → `05-source-registry.md`.
Para análisis detallados por material → `fase0/`.

> Actualizado 2026-04-05 contra contenido real en disco.

## Estados

| Estado | Significado |
|--------|-------------|
| `ingested` | En el corpus, indexado |
| `prepared` | Investigado + script listo para ejecutar |
| `researched` | Investigado, script pendiente |
| `backlog` | Identificado, requiere investigación |
| `blocked` | No se puede proceder por impedimento técnico |

---

## Escrituras y ayudas de estudio

| Material | Notas |
|----------|-------|
| Escrituras EN (todos los standard works) | |
| Escrituras ES (Book of Mormon) | AT/NT/D&C/PGP ES pendientes |
| Conferencia General 1971–2025 EN | ~6,900 charlas — **completo** |
| Conferencia General ES (~1990–2025) | Completo para lo disponible digitalmente — **completo** |
| Bible Dictionary | EN (1,275 entradas) |
| Guide to the Scriptures (GEE) | EN (813) + ES (810) — consolida TG+BD en ES |
| Topical Guide | EN (3,513 entradas) — en GEE ES |
| JST Appendix | EN+ES (94 caps) |
| Chapter headings / superscriptions | EN+ES — en `.meta.json` de cada capítulo |
| Volume introductions (BoM, D&C, PGP, OT, NT) | EN+ES — 29 archivos vía `scrape_introductions.py` |
| Harmony of the Gospels | 8 partes + intro — EN+ES |
| Bible Chronology (AT + NT) | intro + OT + NT — EN+ES |
| Abbreviations | EN+ES |

## Manuales y materiales oficiales

| Material | Notas |
|----------|-------|
| General Handbook | EN+ES |
| Missionary Standards + Supplement | EN+ES |
| Proclamations (Family, Living Christ) | EN+ES |
| Preach My Gospel 2023 | EN+ES |
| Gospel Principles | 51 archivos EN+ES |
| True to the Faith | ~180 entradas EN+ES |
| Come Follow Me (2019–2026, 8 años) | Ciclo completo: NT, LdM, D&C, AT × 2 ciclos |
| Teachings of Presidents (17 volúmenes) | Todos: JS a Nelson, ~560 capítulos EN+ES |
| For the Strength of Youth (2022) | EN+ES |
| Gospel Topics Essays | 15 ensayos EN+ES |
| First Vision Accounts | 9 documentos EN+ES |
| Our Heritage | 11 capítulos EN+ES |
| Saints vols 1–4 | 214 capítulos EN+ES |
| Institute Manuals (CES) | 8 cursos (LdM, D&C, PGP, NT, Familia Eterna, Restauración, etc.) |
| Doctrines of the Gospel | Manual de seminario/instituto |
| Revelations in Context | D&C contexto histórico |
| At the Pulpit | 68 capítulos — mujeres de la Iglesia |
| Daughters in My Kingdom | 17 capítulos — historia de la Sociedad de Socorro |
| Christmas Study Plan (2024) | 9 archivos — 2025 no existe en el sitio |
| Easter / Holy Week Study Plan | 18 archivos (NT + BoM pistas paralelas) |
| Seminary Teacher Manuals (OT, NT, BOM, D&C) | OT 278, NT 312, BOM 312, D&C 280 archivos EN+ES cada uno |
| Seminary Student Manuals (OT, NT, BOM) | OT 218, NT 255-256, BOM 257 archivos EN+ES |
| Doctrinal Mastery (Seminary) | 4 archivos EN+ES |
| Marriage and Family Relations | 18 archivos EN+ES (bajo family-resources/) |
| Strengthening Marriage (Instructor + Couples) | 17 EN+ES (instructor bilingüe, couples EN-only) |
| Strengthening Family (Instructor + Parents) | 19 EN+ES (instructor bilingüe, parents EN-only) |
| Self-Reliance: Leaders Guide | 4 archivos EN+ES |
| Self-Reliance: My Path | 3 archivos EN+ES |
| Self-Reliance: Perpetual Education Fund | 1 archivo EN+ES |
| Self-Reliance: Facilitating Groups | 3 archivos EN+ES |
| Self-Reliance: Plan + Bishop's Guide | 1 archivo EN+ES |
| Institute Student Readings | 39 archivos EN-only (ES 404) |
| Institute Elevate Learning Experience | 10 EN + 11 ES |
| Teacher Development Skills | 27 archivos EN+ES (bajo seminaries-and-institutes/) |
| Principles of Christlike Teaching | 1 archivo EN-only |

## Música

| Material | Notas |
|----------|-------|
| Himnos (Himnario clásico) | 341 archivos EN+ES |
| Himnos para el hogar y la Iglesia | 73 archivos EN+ES |
| Canciones para los niños | 268 archivos EN+ES |
| Ayudas para los Himnos | 90 archivos (About the Hymns 72 + Using 18) |

## Libros (Gutenberg + BYU Studies + Church site)

| Material | Notas |
|----------|-------|
| Jesus the Christ (Talmage) | 43 capítulos EN |
| Articles of Faith (Talmage) | 24 capítulos EN (Gutenberg) |
| Great Apostasy (Talmage) | 10 capítulos EN (Gutenberg) |
| House of the Lord (Talmage) | 11 capítulos EN (Gutenberg) |
| Discourses of Brigham Young | 42 capítulos EN (Gutenberg) |
| History of the Church vols 1–7 | 266 capítulos EN (HC7 BYU Studies, HC1-6 Gutenberg) |
| Autobiography of Parley P. Pratt | 54 capítulos EN |
| Gospel Doctrine (Joseph F. Smith) | 25 capítulos EN |
| Essentials in Church History (JFS Jr.) | 54 capítulos EN |
| History of Prophet Joseph by His Mother | 54 capítulos EN |
| Life of Heber C. Kimball | 66 capítulos EN |
| Wilford Woodruff, Fourth President | 56 capítulos EN |
| Heber C. Kimball's Journal | 17 capítulos EN |
| William Clayton's Journal | 18 secciones mensuales EN |
| Life of David W. Patten | 8 capítulos EN |
| Early Scenes in Church History | 17 capítulos EN |
| The Government of God (John Taylor) | 12 capítulos EN |
| Leaves from My Journal (W. Woodruff) | 28 capítulos EN |
| Biography of Lorenzo Snow | 87 capítulos EN |
| The Story of the Mormons (Linn) | 81 capítulos EN (external perspective, auth=20) |
| + ~20 libros adicionales de Gutenberg/B.H. Roberts | Ver `corpus/en/books/` — ~50 dirs total |

## Referencia externa (pendiente indexación)

| Material | Notas |
|----------|-------|
| Easton's Bible Dictionary | ~3,964 entradas EN (CCEL) |
| Smith's Bible Dictionary | ~4,556 entradas EN (CCEL) |
| Hitchcock's Bible Names | 2,614 nombres EN (CCEL) |
| ISBE (International Standard Bible Enc.) | ~10,121 entradas EN (scrapeado) |
| Hastings' Dictionary of the Bible | ~5,915 entradas EN (scrapeado) |

## B.H. Roberts — Obras completas (pendiente indexación)

| Material | Caps | Notas |
|----------|------|-------|
| Corianton | 11 | Drama/ficción histórica |
| Missouri Persecutions | 20 | Historia |
| New Witness for God (3 vols) | 70 | Apologética |
| Outlines of Ecclesiastical History | 50 | Historia eclesiástica |
| Seventy's Course in Theology (5 vols) | 84 | Teología sistemática |
| Life of John Taylor | 40 | Biografía presidencial |
| Mormon Doctrine of Deity | 13 | Teología |
| Rise and Fall of Nauvoo | 32 | Historia |
