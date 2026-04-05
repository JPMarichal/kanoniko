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
| 7 | **Archive.org** | Baja — OCR variable, formatos inconsistentes | Caso por caso | **Último recurso.** Solo cuando no hay alternativa. Verificar OCR antes de ingestar. |

**Regla:** Antes de escribir un script nuevo, verificar si el texto existe en una
fuente de mayor prioridad. Workflow: Iglesia → RSC → BYU Studies → MTP → Gutenberg → CCEL → Archive.org.

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

| Slug | Título | Cat | Notas |
|------|--------|-----|-------|
| illuminating-jaredite-records | Illuminating the Jaredite Records | 7 | Multi-autor, ed. Belnap — verificado |
| give-ear-my-words | Give Ear to My Words | 15 | Multi-autor Sperry — verificado |
| opening-isaiah | Opening Isaiah | 1,7,10 | Clave para entender Isaías en el LdM |
| abinadi | Abinadi | 1,7 | Análisis profundo de Mosíah 11-17 |
| samuel-lamanite | Samuel the Lamanite | 7 | Profeta LdM poco estudiado |
| jacob | Jacob | 7 | Análisis del libro de Jacob |
| search-diligently-words-isaiah | Search Diligently the Words of Isaiah | 7,10 | Isaías en contexto SUD |
| introduction-book-abraham | An Introduction to the Book of Abraham | 9,2 | Exégesis PGP clave |
| book-moses-joseph-smith-translation-manuscripts | The Book of Moses and the JST Manuscripts | 9,1 | Exégesis Moisés/PGP |
| pearl-great-price-revelations-god | The Pearl of Great Price: Revelations from God | 9,1 | PGP completo |
| foundations-restoration | Foundations of the Restoration | 8,15 | Multi-autor, D&C — verificado |
| you-shall-have-my-word | You Shall Have My Word | 8,15 | D&C exégesis |
| doctrine-covenants-revelations-context | The D&C: Revelations in Context | 8,1 | Contexto histórico de cada sección |
| genesis | Genesis | 10,2 | Génesis desde perspectiva SUD |
| prophets-prophecies-old-testament | Prophets and Prophecies of the OT | 1,10 | AT desde perspectiva SUD |
| gospel-jesus-christ-old-testament | The Gospel of Jesus Christ in the OT | 1,10,15 | Cristo en el AT |
| thou-art-christ-son-living-god | Thou Art the Christ, the Son of the Living God | 1,10,15 | Cristología NT |
| ministry-peter-chief-apostle | The Ministry of Peter, the Chief Apostle | 1,10,15 | Pedro, primer apóstol |
| sermon-mount-latter-day-scripture | The Sermon on the Mount in Latter-day Scripture | 1,15 | Sermón del Monte vs 3 Nefi |
| new-testament-history-culture-society | NT History, Culture, and Society | 1,10 | Contexto NT |
| joseph-smiths-new-translation-bible | Joseph Smith's New Translation of the Bible | 9,1,10 | JST completa |
| understanding-joseph-smiths-translation-bible | Understanding JS's Translation of the Bible | 10,2 | JST académico |
| king-james-bible-restoration | The King James Bible and the Restoration | 1,10,16 | KJV en contexto SUD |

**🟡 P2 — Doctrina, convenios, templo, cristología:**

| Slug | Título | Cat | Notas |
|------|--------|-----|-------|
| ascending-mountain-lord | Ascending the Mountain of the Lord | 10,15 | Templo en la Biblia |
| household-god | The Household of God | 15 | Convenios y familia |
| covenant-compassion | Covenant of Compassion | 10,15 | Convenios en el AT |
| how-what-you-worship | How and What You Worship | 1,10,15 | Adoración |
| our-rites-worship | By Our Rites of Worship | 1,10,12 | Ordenanzas y adoración |
| he-was-seen | He Was Seen | 14 | Resurrección — Easter Conference |
| power-christs-deliverance | The Power of Christ's Deliverance | 14 | Expiación |
| tragedy-triumph | The Tragedy and the Triumph | 14 | Crucifixión y resurrección |
| his-majesty-mission | His Majesty and Mission | 14,10 | Cristología |
| our-saviors-love | Our Savior's Love | 14,10 | Cristología |
| healing-his-wings | With Healing in His Wings | 1,14 | Expiación |
| my-redeemer-lives | My Redeemer Lives! | 1,14 | Resurrección |
| save-lost | To Save the Lost | 1,14 | Misión de Cristo |
| celebrating-easter | Celebrating Easter | 14 | Conferencia pascual |
| behold-lamb-god | "Behold the Lamb of God" | 14 | Cristología |
| fulness-gospel | The Fulness of the Gospel | 15 | Plenitud del evangelio |
| temple-antiquity | The Temple in Antiquity | 12,16 | Templo en la antigüedad |
| lectures-faith-historical-perspective | Lectures on Faith in Historical Perspective | 1,2 | Lecturas sobre la fe |
| life-beyond-grave | Life Beyond the Grave | 11,12 | Escatología SUD |

**🟢 P3 — Fe, salud mental, vida práctica, apologética:**

| Slug | Título | Cat | Notas |
|------|--------|-----|-------|
| freedom-scrupulosity | Freedom from Scrupulosity | 3 | Salud mental + fe |
| our-savior-self-doubt | Our Savior from Self-Doubt | 3 | Auto-duda y fe |
| finding-christ-covenant-path | Finding Christ in the Covenant Path | 3 | Sendero del convenio |
| reason-faith | A Reason for Faith | 3 | Apologética SUD |
| no-weapon-shall-prosper | No Weapon Shall Prosper | 1,12 | Apologética SUD |
| shield-faith | Shield of Faith | 1,3,12 | Apologética |
| divine-design | By Divine Design | 3,11 | Propósito divino |
| moral-foundations-standing-firm-world-shifting-values | Moral Foundations | 16,3 | Ética y valores |
| let-us-reason-together | Let Us Reason Together | 11 | Diálogo interreligioso |
| converging-paths-truth | Converging Paths to Truth | 1,11,16 | Diálogo ecuménico |
| eye-faith | An Eye of Faith | 12,2 | Fe y razón |
| notes-amateur | Notes from an Amateur | 11 | Reflexiones sobre la fe |
| religion-mental-health-latter-day-saints | Religion, Mental Health, and the LDS | 3 | Salud mental |
| religion-family-connection | The Religion and Family Connection | 3,17 | Fe y familia |
| no-other-success | No Other Success | 3,2 | Éxito y fe |
| commitment-covenant | Commitment to the Covenant | 3 | Convenios |

**🔵 P4 — Historia (selectiva, no exhaustiva):**

| Slug | Título | Cat | Notas |
|------|--------|-----|-------|
| joseph-smith-visionary | Joseph Smith as a Visionary | 2 | JS como visionario |
| council-fifty | The Council of Fifty | 2 | Consejo de los Cincuenta |
| darkness-unto-light | From Darkness unto Light | 2 | Surgimiento del LdM |
| coming-forth-book-mormon | The Coming Forth of the Book of Mormon | 7,2,15 | Surgimiento del LdM |
| joseph-smiths-seer-stones | Joseph Smith's Seer Stones | 1,2 | Piedras videntes |
| joseph-smiths-uncanonized-revelations | Joseph Smith's Uncanonized Revelations | 2 | Revelaciones no canónicas |
| sister-prophet | Sister to the Prophet | 2 | Lucy Mack Smith — mujer clave |
| my-dear-sister | My Dear Sister | 2 | Mujeres de la Restauración |
| brigham-young-journals | The Brigham Young Journals | 2 | Diarios de BY |
| exploring-first-vision | Exploring the First Vision | 1,2,11 | Primera Visión |
| repicturing-restoration | Repicturing the Restoration | 2 | Arte de la Restauración |
| joseph-smith-his-first-vision | Joseph Smith and His First Vision | 2,13 | Primera Visión académico |
| well-sing-well-shout | We'll Sing and We'll Shout | 2 | Música SUD histórica |

**⚪ P5 — Relaciones interreligiosas y mundo:**

| Slug | Título | Cat | Notas |
|------|--------|-----|-------|
| view-hebrews | View of the Hebrews | 17 | Texto histórico relevante para LdM |
| peter-popes | Peter and the Popes | 17 | Pedro y la sucesión apostólica |
| understanding-covenants-communities | Understanding Covenants and Communities | 17 | Convenios interreligioso |
| mormons-muslims | Mormons and Muslims | 17 | Diálogo SUD-Islam |
| global-mormonism-21st-century | Global Mormonism in the 21st Century | 16 | Iglesia global |
| salvation-christ-comparative-christian-views | Salvation in Christ: Comparative Views | 2 | Soteriología comparada |
| alexander-campbell-joseph-smith | Alexander Campbell and Joseph Smith | 2 | Contexto restauracionista |

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

| Slug | Prioridad | Notas |
|------|-----------|-------|
| the-testimony-of-luke | **ALTA** | Comentario académico SUD del NT |
| the-gospel-according-to-mark | **ALTA** | |
| pauls-first-epistle-to-the-corinthians | ALTA | |
| the-revelation-of-john-the-apostle | ALTA | |

**BYU NT Commentary: New Renditions (14 volúmenes):**

| Slug | Prioridad | Notas |
|------|-----------|-------|
| the-gospel-according-to-matthew-a-new-rendition | MEDIA | Traducción moderna del NT |
| the-gospel-according-to-mark-a-new-rendition | MEDIA | |
| the-testimony-of-luke-a-new-rendition | MEDIA | |
| pauls-first-epistle-to-the-corinthians-a-new-rendition | MEDIA | |
| pauls-second-epistle-to-the-corinthians-a-new-rendition | MEDIA | |
| the-epistle-to-the-ephesians-a-new-rendition | MEDIA | |
| pauls-first-epistle-to-the-thessalonians-a-new-rendition | MEDIA | |
| pauls-second-epistle-to-the-thessalonians-a-new-rendition | MEDIA | |
| pauls-first-epistle-to-timothy-a-new-rendition | MEDIA | |
| pauls-second-epistle-to-timothy-a-new-rendition | MEDIA | |
| pauls-epistle-to-titus-a-new-rendition | MEDIA | |
| philemon-a-new-rendition | MEDIA | |
| epistle-to-the-hebrews-a-new-rendition | MEDIA | |
| the-revelation-of-john-the-apostle-a-new-rendition | MEDIA | |

**Charting the Scriptures (2):**

| Slug | Prioridad | Notas |
|------|-----------|-------|
| charting-the-new-testament | MEDIA | Tablas/charts escriturales |
| charting-the-book-of-mormon | MEDIA | |

**Libros individuales (9):**

| Slug | Prioridad | Notas |
|------|-----------|-------|
| doctrine-and-covenants-contexts | **ALTA** | Contexto histórico de cada sección D&C |
| opening-the-heavens | **ALTA** | Manifestaciones divinas 1820-1844, fuentes primarias |
| my-fellow-servants | ALTA | Historia del sacerdocio |
| sustaining-the-law | MEDIA | Encuentros legales de JS |
| the-journals-of-william-e-mclellin | MEDIA | Diario de apóstol temprano (1831-36) |
| the-willie-handcart-company | MEDIA | Historia pionera |
| voyages-of-faith | BAJA | Historia mormona del Pacífico |
| wayward-saints | BAJA | Movimiento Godbeite |
| the-st-louis-luminary | BAJA | Periódico SUD histórico |

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

### P2 — Alta prioridad doctrinal (no en corpus)

| # | Título | Autor | Notas |
|---|--------|-------|-------|
| 56684 | Lectures on Faith | Joseph Smith Jr. | Doctrina fundacional Kirtland, 7 lecturas |
| 6720 | The Wentworth Letter | Joseph Smith Jr. | Artículos de Fe originales |
| 35470 | Key to the Science of Theology | Parley P. Pratt | Teología sistemática temprana |
| 35554 | A Voice of Warning | Parley P. Pratt | Clásico misional, muy citado |
| 36327 | Mediation and Atonement | John Taylor | Cristología profética |
| 35562 | A Rational Theology | John A. Widtsoe | Teología moderna SUD |
| 54309 | Ancient Apostles | David O. McKay | Cristología por profeta |

### P3 — Biografías y memorias valiosas

| # | Título | Autor | Notas |
|---|--------|-------|-------|
| 59970 | Life of Joseph Smith, the Prophet | George Q. Cannon | Biografía por apóstol |
| 54331 | Life of a Pioneer | James S. Brown | Autobiografía, Batallón Mormón |
| 48284 | Jacob Hamblin: A Narrative | Jacob Hamblin | Misión a indios, frontera |
| 46391 | Memoirs of John R. Young | John R. Young | Pionero 1847 |
| 54337 | Reminiscences of Joseph the Prophet | Edward Stevenson | Testimonios personales de JS |
| 45049 | My First Mission | George Q. Cannon | Memorias misionales |

### P3 — Historia y apologética

| # | Título | Autor | Notas |
|---|--------|-------|-------|
| 42152 | The Mormon Battalion | B. H. Roberts | Historia militar |
| 44907 | Interesting Account of Remarkable Visions | Orson Pratt | Relato temprano Primera Visión |
| 54278 | Proclamation of the Twelve Apostles | Council of Q12 | Documento fundacional 1845 |
| 45006 | General Smith's Views | Joseph Smith Jr. | Plataforma presidencial 1844 |
| 49432 | Myth of the Manuscript Found | Various | Refutación tesis Spaulding |

### P4 — Perspectiva femenina

| # | Título | Autor | Notas |
|---|--------|-------|-------|
| 50958 | Representative Women of Deseret | Augusta J. Crocheron | Biografías de mujeres SUD |
| 54335 | The Women of Mormondom | Edward W. Tullidge | Historia colectiva de mujeres |
| 51097 | Heroines of Mormondom | Various | Narrativas de mujeres pioneras |
| 46602 | Lydia Knight's History | Susa Young Gates | Perspectiva femenina pionera |

### P4 — Colecciones y antologías

| # | Título | Autor | Notas |
|---|--------|-------|-------|
| 60056 | Scrap Book of Mormon Literature, Vol. 1 | Ben E. Rich | 38 panfletos (Roberts, Pratt, Snow) |
| 54298 | Scrap Book of Mormon Literature, Vol. 2 | Ben E. Rich | Más panfletos |
| 46734 | Scraps of Biography | Various | Colección biográfica |

### P5 — Doctrina menor y miscelánea

| # | Título | Autor | Notas |
|---|--------|-------|-------|
| 56700 | Mormon Doctrine, Plain and Simple | Charles W. Penrose | Doctrinal |
| 47336 | Cowley's Talks on Doctrine | Matthias F. Cowley | Charlas de apóstol |
| 50536 | Gospel Themes | Orson F. Whitney | Ensayos doctrinales |
| 46617 | The Plan of Salvation | John Morgan | Manual misional |
| 46974 | Rays of Living Light | Charles W. Penrose | Folletos misionales |
| 54292 | What Jesus Taught | Osborne J.P. Widtsoe | Cristología |

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

### Historia de la Iglesia (no en corpus)

| # | Título | Autor | Prioridad |
|---|--------|-------|-----------|
| 59970 | The Life of Joseph Smith, the Prophet | George Q. Cannon | ALTA |
| 56698 | The Latter-Day Prophet (para jóvenes) | George Q. Cannon | MEDIA |
| 16534 | A Young Folks' History of the Church | Nephi Anderson | MEDIA |
| 36486 | The City of the Mormons; Three Days at Nauvoo | Henry Caswall | BAJA |
| 9661 | Mormon Settlement in Arizona | James H. McClintock | BAJA |

### Biografías y memorias (no en corpus)

| # | Título | Autor | Prioridad |
|---|--------|-------|-----------|
| 54331 | Life of a Pioneer | James S. Brown | MEDIA |
| 48284 | Jacob Hamblin | Jacob Hamblin | MEDIA |
| 46391 | Memoirs of John R. Young | John R. Young | MEDIA |
| 46602 | Lydia Knight's History | Susa Young Gates | MEDIA |
| 54337 | Reminiscences of Joseph the Prophet | Edward Stevenson | MEDIA |
| 46521 | Forty Years Among the Indians | Daniel W. Jones | MEDIA |
| 50958 | Representative Women of Deseret | Augusta J. Crocheron | MEDIA |
| 51097 | Heroines of "Mormondom" | Various | MEDIA |
| 46734 | Scraps of Biography | Various | BAJA |
| 49739 | Gems of Reminiscence | Various | BAJA |
| 49401 | Eventful Narratives | R. Aveson / O.B. Huntington | BAJA |

### Teología y doctrina (no en corpus)

| # | Título | Autor | Prioridad |
|---|--------|-------|-----------|
| 56684 | The Lectures on Faith | Joseph Smith Jr. | **ALTA** |
| 36327 | Mediation and Atonement | John Taylor | ALTA |
| 35470 | Key to the Science of Theology | Parley P. Pratt | ALTA |
| 35562 | A Rational Theology | John A. Widtsoe | ALTA |
| 54309 | Ancient Apostles | David O. McKay | ALTA |
| 47336 | Cowley's Talks on Doctrine | Matthias F. Cowley | MEDIA |
| 50535 | Blood Atonement and Plural Marriage | Joseph Fielding Smith | MEDIA |
| 47182 | The Vitality of Mormonism (ensayos) | James E. Talmage | MEDIA |
| 5630 | The Story of "Mormonism" / Philosophy | James E. Talmage | MEDIA |
| 50536 | Gospel Themes | Orson F. Whitney | MEDIA |
| 34362 | Joseph Smith as Scientist | John A. Widtsoe | MEDIA |
| 54292 | What Jesus Taught | Osborne J.P. Widtsoe | MEDIA |
| 56700 | Mormon Doctrine, Plain and Simple | Charles W. Penrose | MEDIA |
| 46099 | The Vitality of "Mormonism" (discurso) | James E. Talmage | BAJA |
| 56691 | Saturday Night Thoughts | Orson F. Whitney | BAJA |
| 49357 | Outlines of Mormon Philosophy | Lycurgus A. Wilson | BAJA |
| 46635 | Gospel Philosophy | J.H. Ward | BAJA |

### Escritos misionales y apologéticos (no en corpus)

| # | Título | Autor | Prioridad |
|---|--------|-------|-----------|
| 35554 | A Voice of Warning | Parley P. Pratt | MEDIA |
| 44907 | Interesting Account of Remarkable Visions | Orson Pratt | MEDIA |
| 45846 | Letters Exhibiting Prominent Doctrines | Orson Spencer | BAJA |
| 46243 | Divine Authority | Orson Pratt | BAJA |
| 45005 | Absurdities of Immaterialism | Orson Pratt | BAJA |
| 46244 | The Kingdom of God, Part 1 | Orson Pratt | BAJA |
| 46974 | Rays of Living Light | Charles W. Penrose | BAJA |
| 46617 | The Plan of Salvation | John Morgan | BAJA |

### Documentos históricos y discursos (no en corpus)

| # | Título | Autor | Prioridad |
|---|--------|-------|-----------|
| 6720 | The Wentworth Letter | Joseph Smith Jr. | **ALTA** |
| 54278 | Proclamation of the Twelve Apostles | Council of Q12 | ALTA |
| 45006 | General Smith's Views | Joseph Smith Jr. | MEDIA |
| 46221 | Items on the Priesthood | John Taylor | MEDIA |

### Perspectiva femenina SUD (no en corpus)

| # | Título | Autor | Prioridad |
|---|--------|-------|-----------|
| 54335 | The Women of Mormondom | Edward W. Tullidge | MEDIA |

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
