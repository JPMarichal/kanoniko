# Source Registry — External Sources for Corpus Expansion

Catálogo de fuentes externas disponibles para expandir el corpus.
Para backlog activo → `04-backlog.md`.
Para inventario de lo ya ingresado → `03-corpus-inventory.md`.

---

## Jerarquía de fuentes por calidad

> Las fuentes no oficiales se priorizan por **calidad textual**, **confiabilidad
> de la digitalización** y **riqueza de metadata**. Archive.org es último
> recurso por OCR inconsistente y formatos variables.

| Prioridad | Fuente | Calidad | Script | Notas |
|-----------|--------|---------|--------|-------|
| 🥇 1 | **Sitio oficial de la Iglesia** (churchofjesuschrist.org) | Excelente — HTML limpio, API oficial, bilingüe | `download_manual.py`, `download_scriptures.py`, etc. | Fuente canónica. Siempre preferir sobre cualquier otra. |
| 🥈 2 | **RSC BYU** (rsc.byu.edu) | Muy buena — Drupal HTML limpio, footnotes, metadata estructurada | `download_rsc.py` | ~215 libros online. Contenido académico SUD de alta calidad. |
| 🥉 3 | **BYU Studies** (byustudies.byu.edu) | Buena — Next.js RSC, HTML en payload, footnotes | `download_byustudies.py` | History of the Church y otros textos históricos. |
| 4 | **Mormon Texts Project** (mormontextsproject.org) | Buena — texto corregido manualmente, dominio público | Pendiente | Transcripciones revisadas de Journal of Discourses y otros. ⚠️ Bloqueado por proxy Solera. |
| 5 | **Project Gutenberg** (gutenberg.org) | Variable — texto plano limpio, sin footnotes, sin metadata rica | `download_gutenberg.py` | Bookshelf LDS: ~120 títulos. Buena calidad textual pero splitting manual. |
| 6 | **CCEL** (ccel.org) | Buena — ThML/XML estructurado | Script ad-hoc por obra | Diccionarios bíblicos clásicos (Easton ya ingested). |
| 7 | **Interpreter Foundation** (interpreterfoundation.org) | Buena — HTML completo, footnotes, abstract, Next.js (React SSR) | `download_interpreter.py` | Journal peer-reviewed, ~600 artículos, acceso abierto. Apologético-académico. |
| 8 | **Archive.org** | Baja — OCR variable, formatos inconsistentes | Caso por caso | **Último recurso.** Solo cuando no hay alternativa. Verificar OCR antes de ingestar. |

**Regla:** Antes de escribir un script nuevo, verificar si el texto existe en una
fuente de mayor prioridad. Workflow: Iglesia → RSC → BYU Studies → MTP → Gutenberg → Interpreter → CCEL → Archive.org.

---

## RSC BYU — Inventario completo (authority=25–35)

> Fuente: [rsc.byu.edu/books/online](https://rsc.byu.edu/books/online)
> Script: `download_rsc.py` — soporta libros de autor único y multi-autor
> (conferencias, symposia). Per-chapter author, subtitles, sections, footnotes.
> ~215 libros disponibles online (inventario 2026-04).
>
> **Nota:** Muchos libros RSC recientes son de pago ("not been released for
> online reading"). Solo se pueden descargar los libros libres.

### Categorías RSC y priorización (inventario completo 2026-04-05)

> 214 libros únicos disponibles online. Muchos libros aparecen en múltiples
> categorías (e.g., `opening-isaiah` en cat 1, 7 y 10). Los conteos son por
> categoría, no únicos.

| Cat ID | Categoría | Libros | Prioridad corpus | Justificación |
|--------|-----------|--------|------------------|---------------|
| 7 | Book of Mormon | 37 | **ALTA** | Exégesis académica SUD del LdM |
| 8 | Doctrine and Covenants | 5 | **ALTA** | Exégesis D&C, contexto histórico |
| 9 | Pearl of Great Price | 4 | **ALTA** | Exégesis PGP, Abrahám, Moisés |
| 10 | Bible Studies | 41 | **ALTA** | Perspectiva SUD sobre la Biblia |
| 1 | Scripture Study | 53 | ALTA | Estudio de escrituras general |
| 14 | Easter Conference | 10 | ALTA | Conferencias cristológicas |
| 15 | Sidney B. Sperry Symposium | 26 | ALTA | Conferencias escriturales multi-autor |
| 309 | Book of Mormon Symposium | 9 | ALTA | Conferencias LdM por libro |
| 12 | Gospel Questions | 21 | MEDIA | Preguntas doctrinales |
| 3 | Self-Help | 15 | MEDIA | Auto-ayuda con perspectiva SUD, salud mental |
| 13 | Church History Symposium | 12 | MEDIA | Conferencias académicas multi-autor |
| 11 | Teaching | 33 | MEDIA | Pedagogía religiosa |
| 2 | Church History | 152 | MEDIA | Historia académica SUD (mayoritariamente regional/biográfica) |
| 16 | Other Conferences | 14 | BAJA | Conferencias varias |
| 17 | World Religions & Traditions | 14 | BAJA | Religiones comparadas |

### Libros RSC prioritarios — por tipo de contenido

> **Criterios:** (1) relevancia doctrinal/escritural, (2) diversidad temática
> (no solo historia), (3) enriquecimiento del KG, (4) autores reconocidos.
> Inventario verificado 2026-04-05 vía `download_rsc.py --list-books --category N`.

**🔴 P1 — Exégesis escritural (Book of Mormon, D&C, PGP, Bible):**

| Slug | Título | Cat | Estado | Notas |
|------|--------|-----|--------|-------|
| illuminating-jaredite-records | Illuminating the Jaredite Records | 7 | ✅ ingested | Multi-autor, ed. Belnap — 12 files |
| give-ear-my-words | Give Ear to My Words | 15 | ✅ ingested | Multi-autor Sperry — 23 files |
| opening-isaiah | Opening Isaiah | 1,7,10 | ❌ PDF-only | No disponible para lectura online |
| abinadi | Abinadi | 1,7 | ✅ ingested | 13 files |
| samuel-lamanite | Samuel the Lamanite | 7 | ✅ ingested | 14 files |
| jacob | Jacob | 7 | ❌ PDF-only | No disponible para lectura online |
| search-diligently-words-isaiah | Search Diligently the Words of Isaiah | 7,10 | ❌ PDF-only | No disponible para lectura online |
| introduction-book-abraham | An Introduction to the Book of Abraham | 9,2 | ✅ ingested | 18 files |
| book-moses-joseph-smith-translation-manuscripts | The Book of Moses and the JST Manuscripts | 9,1 | ✅ ingested | 14 files |
| pearl-great-price-revelations-god | The Pearl of Great Price: Revelations from God | 9,1 | ✅ ingested | 14 files |
| foundations-restoration | Foundations of the Restoration | 8,15 | ✅ ingested | 17 files |
| you-shall-have-my-word | You Shall Have My Word | 8,15 | ✅ ingested | 17 files |
| doctrine-covenants-revelations-context | The D&C: Revelations in Context | 8,1 | ✅ ingested | 11 files |
| genesis | Genesis | 10,2 | ❌ PDF-only | No disponible para lectura online |
| prophets-prophecies-old-testament | Prophets and Prophecies of the OT | 1,10 | ✅ ingested | 12 files |
| gospel-jesus-christ-old-testament | The Gospel of Jesus Christ in the OT | 1,10,15 | ✅ ingested | 17 files |
| thou-art-christ-son-living-god | Thou Art the Christ, the Son of the Living God | 1,10,15 | ✅ ingested | 21 files |
| ministry-peter-chief-apostle | The Ministry of Peter, the Chief Apostle | 1,10,15 | ✅ ingested | 21 files |
| sermon-mount-latter-day-scripture | The Sermon on the Mount in Latter-day Scripture | 1,15 | ✅ ingested | 20 files |
| new-testament-history-culture-society | NT History, Culture, and Society | 1,10 | ✅ ingested | 46 files |
| joseph-smiths-new-translation-bible | Joseph Smith's New Translation of the Bible | 9,1,10 | ✅ ingested | 16 files |
| understanding-joseph-smiths-translation-bible | Understanding JS's Translation of the Bible | 10,2 | ❌ PDF-only | No disponible para lectura online |
| king-james-bible-restoration | The King James Bible and the Restoration | 1,10,16 | ✅ ingested | 16 files |

**🟡 P2 — Doctrina, convenios, templo, cristología:**

| Slug | Título | Cat | Estado | Notas |
|------|--------|-----|--------|-------|
| ascending-mountain-lord | Ascending the Mountain of the Lord | 10,15 | ✅ ingested | 23 files — templo en la Biblia |
| household-god | The Household of God | 15 | ❌ PDF-only | No disponible para lectura online |
| covenant-compassion | Covenant of Compassion | 10,15 | ✅ ingested | 20 files |
| how-what-you-worship | How and What You Worship | 1,10,15 | ✅ ingested | 13 files |
| our-rites-worship | By Our Rites of Worship | 1,10,12 | ✅ ingested | 17 files |
| he-was-seen | He Was Seen | 14 | ❌ PDF-only | No disponible para lectura online |
| power-christs-deliverance | The Power of Christ's Deliverance | 14 | ❌ PDF-only | No disponible para lectura online |
| tragedy-triumph | The Tragedy and the Triumph | 14 | ✅ ingested | 7 files |
| his-majesty-mission | His Majesty and Mission | 14,10 | ✅ ingested | 7 files |
| our-saviors-love | Our Savior's Love | 14,10 | ✅ ingested | 9 files |
| healing-his-wings | With Healing in His Wings | 1,14 | ✅ ingested | 7 files |
| my-redeemer-lives | My Redeemer Lives! | 1,14 | ✅ ingested | 7 files |
| save-lost | To Save the Lost | 1,14 | ✅ ingested | 8 files |
| celebrating-easter | Celebrating Easter | 14 | ✅ ingested | 13 files |
| behold-lamb-god | "Behold the Lamb of God" | 14 | ✅ ingested | 13 files |
| fulness-gospel | The Fulness of the Gospel | 15 | ⚠️ partial | 1/20 files — URL bug en PDFs |
| temple-antiquity | The Temple in Antiquity | 12,16 | ✅ ingested | 13 files |
| lectures-faith-historical-perspective | Lectures on Faith in Historical Perspective | 1,2 | ✅ ingested | 20 files |
| life-beyond-grave | Life Beyond the Grave | 11,12 | ✅ ingested | 14 files |

**🟢 P3 — Fe, salud mental, vida práctica, apologética:**

| Slug | Título | Cat | Estado | Notas |
|------|--------|-----|--------|-------|
| freedom-scrupulosity | Freedom from Scrupulosity | 3 | ❌ PDF-only | Salud mental + fe |
| our-savior-self-doubt | Our Savior from Self-Doubt | 3 | ❌ PDF-only | Auto-duda y fe |
| finding-christ-covenant-path | Finding Christ in the Covenant Path | 3 | ✅ ingested | 18 files |
| reason-faith | A Reason for Faith | 3 | ✅ ingested | 19 files |
| no-weapon-shall-prosper | No Weapon Shall Prosper | 1,12 | ✅ ingested | 20 files |
| shield-faith | Shield of Faith | 1,3,12 | ✅ ingested | 14 files |
| divine-design | By Divine Design | 3,11 | ✅ ingested | 12 files |
| moral-foundations-standing-firm-world-shifting-values | Moral Foundations | 16,3 | ✅ ingested | 16 files |
| let-us-reason-together | Let Us Reason Together | 11 | ✅ ingested | 22 files |
| converging-paths-truth | Converging Paths to Truth | 1,11,16 | ✅ ingested | 9 files |
| eye-faith | An Eye of Faith | 12,2 | ✅ ingested | 21 files |
| notes-amateur | Notes from an Amateur | 11 | ✅ ingested | 44 files |
| religion-mental-health-latter-day-saints | Religion, Mental Health, and the LDS | 3 | ✅ ingested | 14 files |
| religion-family-connection | The Religion and Family Connection | 3,17 | ✅ ingested | 20 files |
| no-other-success | No Other Success | 3,2 | ✅ ingested | 12 files |
| commitment-covenant | Commitment to the Covenant | 3 | ✅ ingested | 14 files |

**🔵 P4 — Historia (selectiva, no exhaustiva):**

| Slug | Título | Cat | Estado | Notas |
|------|--------|-----|--------|-------|
| joseph-smith-visionary | Joseph Smith as a Visionary | 2 | ❌ PDF-only | JS como visionario |
| council-fifty | The Council of Fifty | 2 | ✅ ingested | 18 files |
| darkness-unto-light | From Darkness unto Light | 2 | ❌ PDF-only | Surgimiento del LdM |
| coming-forth-book-mormon | The Coming Forth of the Book of Mormon | 7,2,15 | ✅ ingested | 16 files |
| joseph-smiths-seer-stones | Joseph Smith's Seer Stones | 1,2 | ❌ PDF-only | Piedras videntes |
| joseph-smiths-uncanonized-revelations | Joseph Smith's Uncanonized Revelations | 2 | ❌ PDF-only | Revelaciones no canónicas |
| sister-prophet | Sister to the Prophet | 2 | ❌ PDF-only | Lucy Mack Smith — mujer clave |
| brigham-young-journals | The Brigham Young Journals | 2 | ❌ PDF-only | Diarios de BY |
| my-dear-sister | My Dear Sister | 2 | ✅ ingested | 27 files |
| exploring-first-vision | Exploring the First Vision | 1,2,11 | ✅ ingested | 11 files |
| repicturing-restoration | Repicturing the Restoration | 2 | ❌ PDF-only | Arte de la Restauración |
| joseph-smith-his-first-vision | Joseph Smith and His First Vision | 2,13 | ✅ ingested | 15 files |
| well-sing-well-shout | We'll Sing and We'll Shout | 2 | ✅ ingested | 38 files |

**⚪ P5 — Relaciones interreligiosas y mundo:**

| Slug | Título | Cat | Estado | Notas |
|------|--------|-----|--------|-------|
| view-hebrews | View of the Hebrews | 17 | ✅ ingested | 8 files |
| peter-popes | Peter and the Popes | 17 | ✅ ingested | 16 files |
| understanding-covenants-communities | Understanding Covenants and Communities | 17 | ❌ PDF-only | Convenios interreligioso |
| mormons-muslims | Mormons and Muslims | 17 | ✅ ingested | 18 files |
| global-mormonism-21st-century | Global Mormonism in the 21st Century | 16 | ✅ ingested | 22 files |
| salvation-christ-comparative-christian-views | Salvation in Christ: Comparative Views | 2 | ✅ ingested | 17 files |
| alexander-campbell-joseph-smith | Alexander Campbell and Joseph Smith | 2 | ❌ PDF-only | Contexto restauracionista |

---

## BYU Studies — Inventario completo (authority=30–40)

> Fuente: [byustudies.byu.edu](https://byustudies.byu.edu)
> Script: `download_byustudies.py` — usa RSC payload (Next.js streaming).
> Contiene textos históricos que no están disponibles en otras fuentes digitales.

### Ya ingested

| Slug | Título | Caps | Fuente |
|------|--------|------|--------|
| history-of-the-church-vol7 | History of the Church, Vol. 7 | 42 | BYU Studies |
| history-of-the-church-vol1 | History of the Church, Vol. 1 | 33 | Gutenberg |
| history-of-the-church-vol2 | History of the Church, Vol. 2 | 71 | Gutenberg |
| history-of-the-church-vol3 | History of the Church, Vol. 3 | 28 | Gutenberg |
| history-of-the-church-vol4 | History of the Church, Vol. 4 | 30 | Gutenberg |
| history-of-the-church-vol5 | History of the Church, Vol. 5 | 28 | Gutenberg |
| history-of-the-church-vol6 | History of the Church, Vol. 6 | 34 | Gutenberg |

> Nota: HC vols 1-6 descargados de Gutenberg (plain text). Si se quiere mejorar
> la calidad, re-descargar de BYU Studies (HTML limpio con footnotes).

### Catálogo completo BYU Studies online (38 libros — verificado 2026-04-05)

> Inventario: 2026-04-05 via `download_byustudies.py --list-books`
> **38 títulos reales** — la estimación anterior de 65 era incorrecta.

**History of the Church (7 volúmenes):** ✅ Todos `ingested`

**BYU NT Commentary (4 volúmenes):**

| Slug | Prioridad | Estado | Notas |
|------|-----------|--------|-------|
| the-testimony-of-luke | **ALTA** | ✅ ingested | 29 files |
| the-gospel-according-to-mark | **ALTA** | ✅ ingested | 30 files |
| pauls-first-epistle-to-the-corinthians | ALTA | ✅ ingested | 21 files |
| the-revelation-of-john-the-apostle | ALTA | ✅ ingested | 27 files |

**BYU NT Commentary: New Renditions (14 volúmenes):**

| Slug | Prioridad | Estado | Notas |
|------|-----------|--------|-------|
| the-gospel-according-to-matthew-a-new-rendition | MEDIA | ✅ ingested | 28 files |
| the-gospel-according-to-mark-a-new-rendition | MEDIA | ✅ ingested | 16 files |
| the-testimony-of-luke-a-new-rendition | MEDIA | ✅ ingested | 24 files |
| pauls-first-epistle-to-the-corinthians-a-new-rendition | MEDIA | ✅ ingested | 16 files |
| pauls-second-epistle-to-the-corinthians-a-new-rendition | MEDIA | ✅ ingested | 13 files |
| the-epistle-to-the-ephesians-a-new-rendition | MEDIA | ✅ ingested | 6 files |
| pauls-first-epistle-to-the-thessalonians-a-new-rendition | MEDIA | ✅ ingested | 5 files |
| pauls-second-epistle-to-the-thessalonians-a-new-rendition | MEDIA | ✅ ingested | 3 files |
| pauls-first-epistle-to-timothy-a-new-rendition | MEDIA | ✅ ingested | 6 files |
| pauls-second-epistle-to-timothy-a-new-rendition | MEDIA | ✅ ingested | 4 files |
| pauls-epistle-to-titus-a-new-rendition | MEDIA | ✅ ingested | 3 files |
| philemon-a-new-rendition | MEDIA | ✅ ingested | 1 file |
| epistle-to-the-hebrews-a-new-rendition | MEDIA | ✅ ingested | 13 files |
| the-revelation-of-john-the-apostle-a-new-rendition | MEDIA | ✅ ingested | 22 files |

**Charting the Scriptures (2):**

| Slug | Prioridad | Estado | Notas |
|------|-----------|--------|-------|
| charting-the-new-testament | MEDIA | ✅ ingested | 226 files |
| charting-the-book-of-mormon | MEDIA | ✅ ingested | 194 files |

**Libros individuales (9):**

| Slug | Prioridad | Estado | Notas |
|------|-----------|--------|-------|
| doctrine-and-covenants-contexts | **ALTA** | ✅ ingested | 136 files |
| opening-the-heavens | **ALTA** | ✅ ingested | 13 files |
| my-fellow-servants | ALTA | ✅ ingested | 27 files |
| sustaining-the-law | MEDIA | ✅ ingested | 25 files |
| the-journals-of-william-e-mclellin | MEDIA | ✅ ingested | 28 files |
| the-willie-handcart-company | MEDIA | ✅ ingested | 11 files |
| voyages-of-faith | BAJA | ✅ ingested | 30 files |
| wayward-saints | BAJA | ✅ ingested | 25 files |
| the-st-louis-luminary | BAJA | ❌ not attempted | Periódico SUD histórico |

**Newsletters (ignorar):** 2 newsletters de BYU Religious Publications — no relevantes.

---

## MTP / Gutenberg — Textos priorizados (authority=25–40)

> Fuente: Mormon Texts Project → Project Gutenberg
> Los ~94 ebooks MTP son el upstream de casi todos los textos SUD en Gutenberg.
> Calidad: texto proofread 2x, sin OCR artifacts.
> Script: `download_gutenberg.py`
>
> **Journal of Discourses:** MTP explícitamente declinó transcribirlo.
> Solo disponible como PDF/OCR en Archive.org y BYU. NO hay texto limpio.
> El libro "Discourses of Brigham Young" (#74447) ya está en el corpus
> como antología temática compilada por Widtsoe.

### P2 — Alta prioridad doctrinal ✅

| # | Título | Autor | Estado | Notas |
|---|--------|-------|--------|-------|
| 56684 | Lectures on Faith | Joseph Smith Jr. | ✅ 6 files | Doctrina fundacional Kirtland, 7 lecturas |
| 6720 | The Wentworth Letter | Joseph Smith Jr. | ✅ 1 file | Artículos de Fe originales |
| 35470 | Key to the Science of Theology | Parley P. Pratt | ✅ 17 files | Teología sistemática temprana |
| 35554 | A Voice of Warning | Parley P. Pratt | ✅ 7 files | Clásico misional, muy citado |
| 36327 | Mediation and Atonement | John Taylor | ✅ 24 files | Cristología profética |
| 35562 | A Rational Theology | John A. Widtsoe | ✅ 36 files | Teología moderna SUD |
| 54309 | Ancient Apostles | David O. McKay | ✅ 4 files | Cristología por profeta |

### P3 — Biografías y memorias valiosas ✅

| # | Título | Autor | Estado | Notas |
|---|--------|-------|--------|-------|
| 59970 | Life of Joseph Smith, the Prophet | George Q. Cannon | ✅ 65 files | Biografía por apóstol |
| 54331 | Life of a Pioneer | James S. Brown | ✅ 67 files | Autobiografía, Batallón Mormón |
| 48284 | Jacob Hamblin: A Narrative | Jacob Hamblin | ✅ 24 files | Misión a indios, frontera |
| 46391 | Memoirs of John R. Young | John R. Young | ✅ 1 file | Pionero 1847 (single doc) |
| 54337 | Reminiscences of Joseph the Prophet | Edward Stevenson | ✅ 3 files | Testimonios personales de JS |
| 45049 | My First Mission | George Q. Cannon | ✅ 17 files | Memorias misionales |

### P3 — Historia y apologética ✅

| # | Título | Autor | Estado | Notas |
|---|--------|-------|--------|-------|
| 42152 | The Mormon Battalion | B. H. Roberts | ✅ 1 file | Historia militar (single doc) |
| 44907 | Interesting Account of Remarkable Visions | Orson Pratt | ✅ 1 file | Relato temprano Primera Visión |
| 54278 | Proclamation of the Twelve Apostles | Council of Q12 | ✅ 1 file | Documento fundacional 1845 |
| 45006 | General Smith's Views | Joseph Smith Jr. | ✅ 1 file | Plataforma presidencial 1844 |
| 49432 | Myth of the Manuscript Found | Various | ✅ 1 file | Refutación tesis Spaulding |

### P4 — Perspectiva femenina ✅

| # | Título | Autor | Estado | Notas |
|---|--------|-------|--------|-------|
| 50958 | Representative Women of Deseret | Augusta J. Crocheron | ✅ 1 file | Biografías de mujeres SUD (single doc) |
| 54335 | The Women of Mormondom | Edward W. Tullidge | ✅ 119 files | Historia colectiva de mujeres |
| 51097 | Heroines of Mormondom | Various | ✅ 6 files | Narrativas de mujeres pioneras |
| 46602 | Lydia Knight's History | Susa Young Gates | ✅ 12 files | Perspectiva femenina pionera |

### P4 — Colecciones y antologías (parcial)

| # | Título | Autor | Estado | Notas |
|---|--------|-------|--------|-------|
| 60056 | Scrap Book of Mormon Literature, Vol. 1 | Ben E. Rich | ❌ pendiente | 38 panfletos — necesita config para splitting |
| 54298 | Scrap Book of Mormon Literature, Vol. 2 | Ben E. Rich | ✅ 4 files | Más panfletos |
| 46734 | Scraps of Biography | Various | ✅ 36 files | Colección biográfica |

### P5 — Doctrina menor y miscelánea ✅

| # | Título | Autor | Estado | Notas |
|---|--------|-------|--------|-------|
| 56700 | Mormon Doctrine, Plain and Simple | Charles W. Penrose | ✅ 1 file | Doctrinal (single doc) |
| 47336 | Cowley's Talks on Doctrine | Matthias F. Cowley | ✅ 1 file | Charlas de apóstol |
| 50536 | Gospel Themes | Orson F. Whitney | ✅ 1 file | Ensayos doctrinales |
| 46617 | The Plan of Salvation | John Morgan | ✅ 1 file | Manual misional |
| 46974 | Rays of Living Light | Charles W. Penrose | ✅ 1 file | Folletos misionales |
| 54292 | What Jesus Taught | Osborne J.P. Widtsoe | ✅ 1 file | Cristología |

### P6 — Ficción, poesía, perspectiva externa

> Ficción y poesía SUD tienen bajo valor para el knowledge engine pero
> pueden ser útiles para contexto cultural. Perspectiva externa solo
> con authority=15-20 y etiqueta `external-perspective`.

| # | Título | Autor | Tipo |
|---|--------|-------|------|
| 17249 | Added Upon | Nephi Anderson | Ficción teológica |
| 37718 | Elias: An Epic of the Ages | Orson F. Whitney | Poema épico |
| 7066 | Under the Prophet in Utah | Frank J. Cannon | Crítica interna |
| 51096 | The Mormons (Discourse) | Thomas L. Kane | Perspectiva simpática |

---

## Gutenberg Bookshelf "Latter Day Saints" — Inventario completo

> Fuente: [gutenberg.org/ebooks/bookshelf/404](https://www.gutenberg.org/ebooks/bookshelf/404)
> Inventario tomado: 2026-04-04
> Excluye obras de B.H. Roberts (sección propia en fase0/) y Book of Mormon (#17).
> Estado por defecto: candidato sin Fase 0.

### Ya en corpus

| # | Título | Autor | Estado |
|---|--------|-------|--------|
| 22542 | Jesus the Christ | James E. Talmage | `ingested` |
| 42238 | The Articles of Faith | James E. Talmage | `ingested` |
| 35514 | The Great Apostasy | James E. Talmage | `ingested` |
| 45149 | The House of the Lord | James E. Talmage | `ingested` |
| 74447 | Discourses of Brigham Young | Brigham Young/Widtsoe | `ingested` |
| 45054 | Essentials in Church History | Joseph Fielding Smith | `ingested` |
| 45619 | History of Prophet Joseph by Mother | Lucy Mack Smith | `ingested` |
| 44896 | Autobiography of PPP | Parley P. Pratt | `ingested` |
| 47109 | Gospel Doctrine | Joseph F. Smith | `ingested` |
| 35333 | Life of Heber C. Kimball | Orson F. Whitney | `ingested` |
| 47703 | Wilford Woodruff, Fourth President | Wilford Woodruff | `ingested` |
| 47519 | Heber C. Kimball's Journal | Heber C. Kimball | `ingested` |
| 45051 | William Clayton's Journal | William Clayton | `ingested` |
| 46783 | Early Scenes in Church History | Various | `ingested` |
| 51730 | Life of David W. Patten | Lycurgus A. Wilson | `ingested` |
| 44941 | The Government of God | John Taylor | `ingested` |
| 46028 | Leaves from My Journal | Wilford Woodruff | `ingested` |
| 47708 | Biography of Lorenzo Snow | Eliza R. Snow | `ingested` |
| 2443 | The Story of the Mormons | William A. Linn | `ingested` |

### Historia de la Iglesia

| # | Título | Autor | Estado | Prioridad |
|---|--------|-------|--------|-----------|
| 59970 | The Life of Joseph Smith, the Prophet | George Q. Cannon | ✅ 65 files | ALTA |
| 56698 | The Latter-Day Prophet (para jóvenes) | George Q. Cannon | ✅ 1 file | MEDIA |
| 16534 | A Young Folks' History of the Church | Nephi Anderson | ❌ pendiente | MEDIA |
| 36486 | The City of the Mormons; Three Days at Nauvoo | Henry Caswall | ❌ pendiente | BAJA |
| 9661 | Mormon Settlement in Arizona | James H. McClintock | ❌ pendiente | BAJA |

### Biografías y memorias

| # | Título | Autor | Estado | Prioridad |
|---|--------|-------|--------|-----------|
| 54331 | Life of a Pioneer | James S. Brown | ✅ 67 files | MEDIA |
| 48284 | Jacob Hamblin | Jacob Hamblin | ✅ 24 files | MEDIA |
| 46391 | Memoirs of John R. Young | John R. Young | ✅ 1 file | MEDIA |
| 46602 | Lydia Knight's History | Susa Young Gates | ✅ 12 files | MEDIA |
| 54337 | Reminiscences of Joseph the Prophet | Edward Stevenson | ✅ 3 files | MEDIA |
| 46521 | Forty Years Among the Indians | Daniel W. Jones | ❌ pendiente | MEDIA |
| 50958 | Representative Women of Deseret | Augusta J. Crocheron | ✅ 1 file | MEDIA |
| 51097 | Heroines of "Mormondom" | Various | ✅ 6 files | MEDIA |
| 46734 | Scraps of Biography | Various | ✅ 36 files | BAJA |
| 49739 | Gems of Reminiscence | Various | ❌ pendiente | BAJA |
| 49401 | Eventful Narratives | R. Aveson / O.B. Huntington | ❌ pendiente | BAJA |

### Teología y doctrina

| # | Título | Autor | Estado | Prioridad |
|---|--------|-------|--------|-----------|
| 56684 | The Lectures on Faith | Joseph Smith Jr. | ✅ 6 files | **ALTA** |
| 36327 | Mediation and Atonement | John Taylor | ✅ 24 files | ALTA |
| 35470 | Key to the Science of Theology | Parley P. Pratt | ✅ 17 files | ALTA |
| 35562 | A Rational Theology | John A. Widtsoe | ✅ 36 files | ALTA |
| 54309 | Ancient Apostles | David O. McKay | ✅ 4 files | ALTA |
| 47336 | Cowley's Talks on Doctrine | Matthias F. Cowley | ✅ 1 file | MEDIA |
| 50535 | Blood Atonement and Plural Marriage | Joseph Fielding Smith | ✅ 1 file | MEDIA |
| 47182 | The Vitality of Mormonism (ensayos) | James E. Talmage | ✅ ingested | MEDIA |
| 5630 | The Story of "Mormonism" / Philosophy | James E. Talmage | ✅ 1 file | MEDIA |
| 50536 | Gospel Themes | Orson F. Whitney | ✅ 1 file | MEDIA |
| 34362 | Joseph Smith as Scientist | John A. Widtsoe | ✅ 1 file | MEDIA |
| 54292 | What Jesus Taught | Osborne J.P. Widtsoe | ✅ 1 file | MEDIA |
| 56700 | Mormon Doctrine, Plain and Simple | Charles W. Penrose | ✅ 1 file | MEDIA |
| 46099 | The Vitality of "Mormonism" (discurso) | James E. Talmage | ❌ pendiente | BAJA |
| 56691 | Saturday Night Thoughts | Orson F. Whitney | ❌ pendiente | BAJA |
| 49357 | Outlines of Mormon Philosophy | Lycurgus A. Wilson | ❌ pendiente | BAJA |
| 46635 | Gospel Philosophy | J.H. Ward | ❌ pendiente | BAJA |

### Escritos misionales y apologéticos

| # | Título | Autor | Estado | Prioridad |
|---|--------|-------|--------|-----------|
| 35554 | A Voice of Warning | Parley P. Pratt | ✅ 7 files | MEDIA |
| 44907 | Interesting Account of Remarkable Visions | Orson Pratt | ✅ 1 file | MEDIA |
| 45846 | Letters Exhibiting Prominent Doctrines | Orson Spencer | ❌ pendiente | BAJA |
| 46243 | Divine Authority | Orson Pratt | ❌ pendiente | BAJA |
| 45005 | Absurdities of Immaterialism | Orson Pratt | ❌ pendiente | BAJA |
| 46244 | The Kingdom of God, Part 1 | Orson Pratt | ❌ pendiente | BAJA |
| 46974 | Rays of Living Light | Charles W. Penrose | ✅ 1 file | BAJA |
| 46617 | The Plan of Salvation | John Morgan | ✅ 1 file | BAJA |

### Documentos históricos y discursos

| # | Título | Autor | Estado | Prioridad |
|---|--------|-------|--------|-----------|
| 6720 | The Wentworth Letter | Joseph Smith Jr. | ✅ 1 file | **ALTA** |
| 54278 | Proclamation of the Twelve Apostles | Council of Q12 | ✅ 1 file | ALTA |
| 45006 | General Smith's Views | Joseph Smith Jr. | ✅ 1 file | MEDIA |
| 46221 | Items on the Priesthood | John Taylor | ❌ pendiente | MEDIA |

### Perspectiva femenina SUD

| # | Título | Autor | Estado | Prioridad |
|---|--------|-------|--------|-----------|
| 54335 | The Women of Mormondom | Edward W. Tullidge | ✅ 119 files | MEDIA |

### Colecciones, ficción, perspectiva externa

> Ver sección MTP/Gutenberg arriba para listado priorizado.
> Ficción y perspectiva externa: prioridad P6 (baja).

| # | Título | Autor | Tipo | Prioridad |
|---|--------|-------|------|-----------|
| 60056 | Scrap Book of Mormon Lit. Vol. 1 | Ben E. Rich | Antología | BAJA |
| 54298 | Scrap Book of Mormon Lit. Vol. 2 | Ben E. Rich | Antología | BAJA |
| 51095 | Book of Mormon Stories No. 1 | George Q. Cannon | Infantil | BAJA |
| 49382 | The Life of Nephi | George Q. Cannon | Ficción/exégesis | MEDIA |
| 48517 | Mother Stories from the BoM | William A. Morton | Infantil | BAJA |
| 50029 | The Story of the Book of Mormon | — | Resumen | BAJA |
| 46601 | Gems for the Young Folks | Various | Juvenil | BAJA |
| 46733 | A String of Pearls | Various | Devocional | BAJA |
| 49830 | Treasures in Heaven | — | Devocional | BAJA |
| 50072 | Fragments of Experience | Various | Miscelánea | BAJA |
| 49327 | Labors in the Vineyard | Various | Misional | BAJA |
| 49362 | Helpful Visions | — | Devocional | BAJA |
| 13756 | Story of Chester Lawrence | Nephi Anderson | Ficción | BAJA |
| 17249 | Added Upon | Nephi Anderson | Ficción teológica | BAJA |
| 12684 | Dorian | Nephi Anderson | Ficción | BAJA |
| 52552 | Venna Hastings | Julia Farr | Ficción | BAJA |
| 50955 | The Cities of the Sun | Elizabeth Cannon Porter | Ficción | BAJA |
| 56685 | Mr. Durant of Salt Lake City | Ben. E. Rich | Ficción | BAJA |
| 44414 | The Mormon Prophet and His Harem | C.V. Waite | Anti-mormón | BAJA |
| 7066 | Under the Prophet in Utah | Frank J. Cannon | Crítica interna | BAJA |
| 14661 | Conditions in Utah | Thomas Kearns | Político | BAJA |
| 54079 | Sinners and Saints | Phil Robinson | Viajero | BAJA |
| 36791 | The Mormon Puzzle | R.W. Beers | Externa | BAJA |
| 17279 | The Mormon Prophet | L. Dougall | Ficción externa | BAJA |
| 37718 | Elias: An Epic of the Ages | Orson F. Whitney | Poesía | BAJA |
| 51096 | The Mormons (Discourse) | Thomas L. Kane | Simpática | BAJA |
| 42152 | The Mormon Battalion | B.H. Roberts | Historia militar | MEDIA |
| 49432 | Myth of Manuscript Found | Various | Apologética | MEDIA |
| 45049 | My First Mission | George Q. Cannon | Memorias | MEDIA |
