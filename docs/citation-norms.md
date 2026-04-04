# Citation Norms — FCD (Formato de Citas para Dilton)

Standards for citing all corpus materials in Alejandría — for RAG answers, search results, and any output that references corpus content.

## General Principles

1. **Language consistency:** Citations follow the language of the passage being cited. Never mix languages within a single citation.
2. **Literal quotes only:** Quote text exactly as it appears in the corpus. Never paraphrase a quoted passage.
3. **Reference in parentheses:** Always at the end of the quoted text, never on a separate line.
4. **Titles of works** in quotes: "Jesús el Cristo", "Liahona", not in italics.
5. **Titles of autoridades generales:** Usar el título más alto conocido. Presidente para presidentes de la Iglesia (presidente Benson, presidente Nelson), élder para apóstoles (élder Bednar, élder Oaks), presidente para presidencias de quórum (presidente Eyring). Si no se tiene certeza, usar el título más conocido o el vigente al momento de la cita.

---

## FCD Construction Rules

### Citation anatomy

```
"[Work Title]"[, Author][, vol. N][, locator][, (Year)]
```

- **Work Title** — always in quotes; use the official full title as published
- **Author** — include only when it adds value (biographies, doctrinal works by named authors); omit for institutional manuals and plans
- **vol. N** — for multi-volume works (Saints, Teachings of Presidents)
- **locator** — the most specific unit available:

| Work structure | Locator type | Example |
|---------------|-------------|---------|
| Books / biographies | `capítulo N` / `chapter N` | `capítulo 23` |
| Manuals with lessons | `lección N` / `lesson N` | `lección 45` |
| Topic-organized pamphlets | `"Section Name"` | `"Castidad"` |
| Weekly study plans (CFM) | `semana del [date] — [Scripture range]` | `semana del 6 de enero — Génesis 1–2` |
| Seasonal plans (multi-day) | `[Day Name]` or `día N` + track | `Viernes Santo — pista NT` |
| Music | `no. N` | `no. 34` |
| Harmony of the Gospels | `evento N — "[Event Name]"` | `evento 45 — "La Última Cena"` |
| Bible Chronology | `período "[Period Name]" (~date)` | `período "Monarquía dividida" (~931 a.C.)` |

- **Year** — include in parentheses for materials that update regularly (CFM, seasonal plans, annual editions)

### When to include the author

| Include author | Omit author |
|---------------|-------------|
| Named doctrinal works (Talmage, Roberts) | Church-published manuals without individual authorship |
| Biographies with identified author | Come Follow Me, FSY, Seminary manuals |
| Works where attribution is the point | Hymns, Saints, Our Heritage |

### Title selection rule

Use the official title as published by the Church, in the language of the citation:
- ✅ `"Enseñanzas de los Presidentes de la Iglesia: José Smith"` (not "Enseñanzas: JS")
- ✅ `"Ven sígueme (2024)"` (not "Sígueme" or "CFM")
- ✅ `"Para la Fortaleza de la Juventud"` (not "FSY")
- ✅ `"Himnario"` / `"Hymns"` for the classic 1985 hymnal

## Two Citation Modes

### Inline

The reference flows naturally within a paragraph of commentary:

> El profeta Nefi declaró: "Iré y haré lo que el Señor ha mandado" (1 Nefi 3:7), expresando una fe que se convertiría en modelo para generaciones.

### Outline (Block)

A standalone quoted passage displayed as a blockquote. Rules:

- Text without verse numbers
- Each verse/paragraph on its own line (simple line break)
- Reference in parentheses at the end of the **last line** — same line, not a new one
- Blockquote formatting (`>`), never italics

> Y satisfará el Señor toda necesidad vuestra,
> conforme a sus riquezas en gloria en Cristo Jesús.
> A nuestro Dios y Padre sea la gloria por los siglos de los siglos. Amén. (Filipenses 4:19-20)

---

## 1. Scripture Passages (Standard Works)

### Format: `Book Chapter:Verse[-Verse]`

| Volume | English | Spanish |
|--------|---------|---------|
| Old Testament | Genesis 1:1-5 | Génesis 1:1-5 |
| New Testament | Matthew 5:14-16 | Mateo 5:14-16 |
| Book of Mormon | 1 Nephi 3:7 | 1 Nefi 3:7 |
| D&C | D&C 76:22-24 | DyC 76:22-24 |
| Pearl of Great Price | Moses 7:18 | Moisés 7:18 |
| Articles of Faith | Articles of Faith 1:10 | Artículos de Fe 1:10 |
| JS-History | JS—History 1:17 | JS—Historia 1:17 |
| JS-Matthew | JS—Matthew 1:37 | JS—Mateo 1:37 |

### Special cases

- **D&C sections** (not chapters): `D&C 132:19` / `DyC 132:19`
- **Official Declarations:** `Official Declaration 1` / `Declaración Oficial 1`
- **Verse ranges:** colon for chapter:verse, dash for range: `Alma 32:21-23`
- **Multiple references:** semicolon separator: `1 Nefi 3:7; Alma 32:21`

Full book name mappings are implemented in `src/alejandria/ingestion/scripture_meta.py`.

### Examples

**Inline:**

> El profeta Nefi declaró: "Iré y haré lo que el Señor ha mandado" (1 Nefi 3:7), expresando una fe que se convertiría en modelo para generaciones.

> The Lord promises that "if ye have faith as a grain of mustard seed... nothing shall be impossible unto you" (Matthew 17:20).

> El concepto de Sion aparece tanto en el Antiguo Testamento (Isaías 2:3) como en la Perla de Gran Precio (Moisés 7:18-19) y en Doctrina y Convenios (DyC 97:21).

**Outline:**

> Y satisfará el Señor toda necesidad vuestra,
> conforme a sus riquezas en gloria en Cristo Jesús.
> A nuestro Dios y Padre sea la gloria por los siglos de los siglos. Amén. (Filipenses 4:19-20)

> For God so loved the world, that he gave his only begotten Son,
> that whosoever believeth in him should not perish, but have everlasting life. (John 3:16)

---

## 2. Study Aids

### Abbreviations

| Material | EN abbrev | ES abbrev | Notes |
|----------|-----------|-----------|-------|
| Topical Guide | **TG** | — | EN only |
| Bible Dictionary | **BD** | — | EN only |
| Guide to the Scriptures | — | **GEE** | ES only; consolidates TG + BD + Index |
| JST Appendix | **JST** | **TJS** | Both languages |

### Format: `Abbreviation EntryName`

No quotes, no commas, no page numbers. Entry name as it appears in the heading.

**Examples EN:**
- `TG Faith`
- `TG Prophets, Mission of`
- `BD Melchizedek`
- `BD Idumea`

**Examples ES:**
- `GEE Fe`
- `GEE Profecía, profetizar`
- `GEE Nefi hijo de Lehi`
- `GEE Misericordia, misericordioso`

**Multiple entries** separated by semicolons:
- `TG Education; Family, Children, Responsibilities toward`
- `GEE Adversidad; Bendecir, bendecido, bendición`

### Examples

**Inline:**

> The Topical Guide groups over 30 references under "Faith" (TG Faith), connecting Old Testament, New Testament, and Restoration scripture in a single thread.

> La GEE define la expiación como "el sufrimiento y la muerte de Jesucristo, por medio de los cuales se hace posible la resurrección y la vida eterna" (GEE Expiación, expiar).

> The Bible Dictionary explains that Melchizedek was "king of Salem, a city later known as Jerusalem" (BD Melchizedek), adding context not explicit in the Genesis account.

**Outline:**

> A temple is literally a house of the Lord, a holy sanctuary in which sacred ceremonies and ordinances of the gospel are performed by and for the living and also in behalf of the dead. A place where the Lord may come, it is the most holy of any place of worship on the earth. (BD Temple)

> El sacerdocio mayor, que se confiere a hombres fieles a fin de que puedan tener poder y autoridad para oficiar en las ordenanzas del Evangelio. Se llama el Santo Sacerdocio según el Orden del Hijo de Dios, pero por respeto y reverencia al nombre de Dios, se le llamó el Sacerdocio de Melquisedec. (GEE Sacerdocio de Melquisedec)

### JST / TJS — Cited as scripture references

The JST Appendix follows scripture citation format, not dictionary format:

- `JST, Genesis 14:25-40` / `TJS, Génesis 14:25-40`
- `JST, Matthew 3:34-36` / `TJS, Mateo 3:34-36`

Note the comma after the abbreviation (Church convention).

**Inline:**

> In the Joseph Smith Translation, the Lord reveals a fuller picture of the priesthood order: "It being after the order of the Son of God; which order came, not by man, nor the will of man" (JST, Genesis 14:28).

> La Traducción de José Smith aclara que "la fe es la seguridad de las cosas que se esperan, la confirmación de lo que no se ve" (TJS, Hebreos 11:1).

**Outline:**

> And it was delivered unto men by the calling of his own voice,
> according to his own will, unto as many as believed on his name.
> For God having sworn unto Enoch and unto his seed with an oath by himself;
> that every one being ordained after this order and calling should have power,
> by faith, to break mountains, to divide the seas, to dry up waters,
> to turn them out of their course. (JST, Genesis 14:29-30)

---

## 3. Introductory Materials

Cited by full name — no standard abbreviation exists.

| Material | English | Spanish |
|----------|---------|---------|
| BOM title page | Title Page of the Book of Mormon | Portada del Libro de Mormón |
| BOM intro | Introduction to the Book of Mormon | Introducción al Libro de Mormón |
| Three Witnesses | The Testimony of Three Witnesses | El Testimonio de Tres Testigos |
| Eight Witnesses | The Testimony of Eight Witnesses | El Testimonio de Ocho Testigos |
| Joseph Smith | The Testimony of the Prophet Joseph Smith | El Testimonio del profeta José Smith |
| BOM explanation | A Brief Explanation about the Book of Mormon | Una breve explicación acerca del Libro de Mormón |
| D&C intro | Introduction to the Doctrine and Covenants | Introducción a Doctrina y Convenios |
| D&C chronology | Chronological Order of Contents | Tabla cronológica de materias |
| PGP intro | Introduction to the Pearl of Great Price | Introducción a la Perla de Gran Precio |
| KJV dedicatory | Epistle Dedicatory (KJV) | — (EN only) |

### Examples

**Inline:**

> La Introducción al Libro de Mormón invita a "preguntar a Dios, el Padre Eterno, en el nombre de Cristo, si el libro es verdadero" (Introducción al Libro de Mormón).

> The witnesses declared they had "seen the engravings which are upon the plates; and they have been shown unto us by the power of God, and not of man" (The Testimony of Three Witnesses).

**Outline:**

> Conste a todas las naciones, tribus, lenguas y pueblos a quienes llegare esta obra, que nosotros, por la gracia de Dios Padre y de nuestro Señor Jesucristo, hemos visto las planchas que contienen estos anales... Y declaramos con palabras solemnes que un ángel de Dios bajó del cielo, y él trajo y puso ante nuestros ojos, que vimos y contemplamos las planchas y las inscripciones en ellas. (El Testimonio de Tres Testigos)

---

## 4. General Conference Talks

### Format: `Author, "Title," Conference Session Year`

- `Dallin H. Oaks, "Cleansed by Repentance," October 2019 General Conference`
- `Russell M. Nelson, "El poder espiritual de nuestros convenios," Conferencia General de abril 2024`

When the corpus chunk already includes author/title metadata, the citation should use it.

### Examples

**Inline:**

> El presidente Nelson enseñó que "en los días venideros no será posible sobrevivir espiritualmente sin la influencia guiadora, dirigente, consoladora y constante del Espíritu Santo" (Russell M. Nelson, "Revelación para la Iglesia, revelación para nuestras vidas," Conferencia General de abril 2018).

> Elder Oaks reminded us that "the Final Judgment is not just an evaluation of a sum total of good and evil acts" (Dallin H. Oaks, "The Challenge to Become," October 2000 General Conference).

**Outline:**

> Mis queridos hermanos y hermanas, los convenios con Dios son de vital importancia. En una época futura no muy lejana, experimentaremos a la perfección el poder redentor, fortalecedor y santificador de los convenios. (Russell M. Nelson, "El poder espiritual de nuestros convenios," Conferencia General de abril 2024)

---

## 5. Other Corpus Materials

For manuals, biographies, histories, and web content — cite by title (in quotes), author when applicable, and the most specific locator available (chapter, lesson, section, week, day).

### 5a. Doctrinal Works by Named Authors

Format: `"Title", Author, capítulo/chapter N`

| Work | EN | ES |
|------|----|----|
| Jesus the Christ | `"Jesus the Christ", James E. Talmage, chapter N` | `"Jesús el Cristo", James E. Talmage, capítulo N` |
| The Articles of Faith | `"The Articles of Faith", James E. Talmage, chapter N` | `"Los Artículos de Fe", James E. Talmage, capítulo N` |

**Inline:**

> Talmage explica que la transfiguración fue "una manifestación especial de la gloria divina del Señor" ("Jesús el Cristo", James E. Talmage, capítulo 23).

**Outline:**

> La expiación de Cristo no fue solo para eliminar el pecado del arrepentido. Fue también para absorber toda pena y sufrimiento humano, para que Él supiera cómo socorrer a su pueblo según las enfermedades de ellos. ("Jesús el Cristo", James E. Talmage, capítulo 35)

---

### 5b. Teachings of Presidents of the Church

Format: `"Enseñanzas de los Presidentes de la Iglesia: [President Name]", capítulo N`

The full series title is always included — never abbreviate to "Enseñanzas" alone.

| EN | ES |
|----|-----|
| `"Teachings of Presidents of the Church: Joseph Smith", chapter 4` | `"Enseñanzas de los Presidentes de la Iglesia: José Smith", capítulo 4` |
| `"Teachings of Presidents of the Church: Brigham Young", chapter 11` | `"Enseñanzas de los Presidentes de la Iglesia: Brigham Young", capítulo 11` |

**Inline:**

> El presidente Smith enseñó que "la fe viene al escuchar la palabra de Dios" ("Enseñanzas de los Presidentes de la Iglesia: José Smith", capítulo 4).

---

### 5c. Church History (Saints, Our Heritage)

Format: `"Title", vol. N, capítulo/chapter N`

| EN | ES |
|----|-----|
| `"Saints", vol. 1, chapter 12` | `"Santos", vol. 1, capítulo 12` |
| `"Our Heritage", chapter 5` | `"Nuestra Herencia", capítulo 5` |

**Inline:**

> En los días de Nauvoo, la hermana Emma Smith fue elegida primera presidenta de la Sociedad de Socorro ("Santos", vol. 2, capítulo 4).

---

### 5d. Come Follow Me

Format: `"Ven sígueme (YYYY)"` or `"Come, Follow Me (YYYY)"`, `semana del [date] — [Scripture range]`

Year is always included in parentheses in the title — the manual changes annually.

**Inline:**

> El manual señala que Abraham "mostró una fe inquebrantable al ser probado" ("Ven sígueme (2025)", semana del 3 de febrero — Génesis 12–17).

> Come, Follow Me invites us to consider how faith is "a principle of power" ("Come, Follow Me (2025)", week of February 3 — Genesis 12–17).

---

### 5e. Seminary and Institute Manuals

Format: `"[Manual Title] (YYYY)", lección/lesson N`

| EN | ES |
|----|-----|
| `"Doctrine and Covenants Seminary Teacher Manual (2025)", lesson 45` | `"Seminario D&C — Manual del Maestro (2025)", lección 45` |
| `"Book of Mormon Seminary Student Manual (2024)", lesson 12` | `"Libro de Mormón — Manual del Estudiante (2024)", lección 12` |
| `"The Eternal Family", lesson 8` | `"La Familia Eterna", lección 8` |

**Inline:**

> El manual señala que "la revelación continua es evidencia del sacerdocio restaurado" ("Seminario D&C — Manual del Maestro (2025)", lección 45).

---

### 5f. For the Strength of Youth

Format: `"Para la Fortaleza de la Juventud" (YYYY), "[Section Name]"`

Section name matches the heading of the topic. Year in parentheses after the title (not inside quotes) since this pamphlet has editions.

**Inline:**

> El folleto enseña que la castidad "protege y prepara para las ordenanzas del templo" ("Para la Fortaleza de la Juventud" (2022), "Castidad").

> The pamphlet explains that the Sabbath is "a weekly covenant renewal through the sacrament" ("For the Strength of Youth" (2022), "Sabbath Day").

---

### 5g. Missionary Preparation Manual

Format: `"Preparación Misional" (YYYY), lección N` / `"Missionary Preparation" (YYYY), lesson N`

**Inline:**

> El manual establece D&C 4 como "la escritura fundamental del servicio misional" ("Preparación Misional" (2025), lección 1).

---

### 5h. Seasonal Study Plans

**Christmas Study Plan** — year-specific slug; include year:

Format: `"Plan de Estudio de Navidad YYYY", día N` / `"Christmas Study Plan YYYY", day N`

> El plan invita a reflexionar sobre "la noche sin oscuridad en las Américas" como cumplimiento de la profecía ("Plan de Estudio de Navidad 2024", día 5 — "23 de diciembre").

**Easter / Holy Week Study Plan** — permanent slug; include track for dual-track content:

Format: `"Plan de Semana Santa", [Day Name] — pista NT/BoM` / `"Holy Week Study Plan", [Day Name] — NT/BoM track`

> El plan muestra que el mismo Jueves Santo se instituyó el Sacramento tanto en Palestina como en las Américas ("Plan de Semana Santa", Jueves Santo — pista BoM).

---

## 6. Music

Cite by hymn/song title (in quotes), collection name, and number when available.

### 6a. Classic Hymnbook (1985)

Format: `"Hymn Title" (Hymns, no. N)` / `"Título del Himno" (Himnario, no. N)`

Numbers are stable in the 1985 edition.

**Inline:**

> El himno proclama que "la verdad eterna fue enviada, proclamad el gozoso son" ("Alta en la Montaña", Himnario, no. 5).

> The hymn declares that "truth eternal, truth divine, in these last days now shines" ("Truth Eternal," Hymns, no. 4).

### 6b. Hymns for Home and Church (2024–)

Format: `"Hymn Title" (Himnos para el Hogar y la Iglesia, no. N)` / `"Hymn Title" (Hymns for Home and Church, no. N)`

Numbers in this collection are provisional pending full publication; use the number published at time of citation.

**Inline:**

> El nuevo himnario canta: "Somos hijos de la luz, llamados a reunir" ("Gather Israel," Himnos para el Hogar y la Iglesia, no. 1127).

### 6c. Children's Songbook

Format: `"Song Title" (Canciones para los Niños)` / `"Song Title" (Children's Songbook)`

Numbers are less commonly cited; use title alone unless the number aids disambiguation.

**Inline:**

> La canción afirma que "soy hijo de Dios, y Él me ama como soy" ("Soy Hijo de Dios", Canciones para los Niños).

### 6d. Youth Music

Format: `"Song Title" (Música para los Jóvenes, YYYY)` / `"Song Title" (Youth Music, YYYY)`

Include year because albums are annual releases tied to the youth theme of that year.

**Inline:**

> El álbum del año refleja el llamado a "juntar a Israel en los últimos días" ("Gather Israel," Música para los Jóvenes, 2026).

### 6e. Hymn Helps / About the Hymns

Format: `"About [Hymn Title]" (Ayudas para los Himnos)` / `"About [Hymn Title]" (Hymn Helps)`

**Inline:**

> El recurso señala que "Alta en la Montaña" alude directamente a Isaías 2:2 ("Acerca de 'Alta en la Montaña'", Ayudas para los Himnos).

---

## 7. Harmony of the Gospels and Bible Chronology

These are scripture study aids published in the official Quad — cite without author.

### Harmony of the Gospels

Format: `Harmonía de los Evangelios, evento N — "[Event Name]"` / `Harmony of the Gospels, event N — "[Event Name]"`

No abbreviation established (unlike TG/BD). Cite by event number and name.

**Inline:**

> La Harmonía registra que tanto Mateo como Lucas ubican la entrada triunfal el mismo domingo (Harmonía de los Evangelios, evento 127 — "La entrada triunfal").

### Bible Chronology

Format: `Cronología Bíblica, período "[Period Name]" (~date)` / `Bible Chronology, period "[Period Name]" (~date)`

Include approximate date range when available — it is the primary locator in this material.

**Inline:**

> La cronología sitúa el ministerio de Isaías durante el reinado de cuatro reyes de Judá (Cronología Bíblica, período "Profetas del siglo VIII a.C." — ~760–700 a.C.).

---

## 8. Independent Web Sources

External websites by independent authors that contribute to the corpus. Each citation must include a URL to enable proper attribution and linking in published articles.

### Format: `Author, "Article Title," Site Name (URL)`

The URL is the original permalink of the article. In digital publications (blog, WordPress), URLs become clickable links; in print, the URL serves as a locator.

### Registered Sources

| Site | Author | Corpus path | Authority | Rigor | Notes |
|------|--------|-------------|-----------|-------|-------|
| Women in the Scriptures | Heather Farrell | `corpus/en/web/womeninthescriptures/` | 20 | 50 | 75+ scriptural woman profiles + thematic essays |

### Examples

**Inline:**

> Farrell observa que Abigail "is one of the most remarkable women in the Old Testament" y analiza su papel como tipo de Cristo (Heather Farrell, "Abigail," Women in the Scriptures, womeninthescriptures.com/2012/06/abigail.html).

> The profile notes that the Shunamite woman "exercised extraordinary faith in seeking out the prophet" (Heather Farrell, "The Shunamite Woman," Women in the Scriptures, womeninthescriptures.com/2009/04/shunamite-woman.html).

**Outline:**

> Abigail's story teaches us that sometimes the bravest thing a woman can do is to step between two opposing forces and plead for mercy. She is, in many ways, a type of Christ — an intercessor who prevents bloodshed through her own courage and wisdom. (Heather Farrell, "Abigail," Women in the Scriptures, womeninthescriptures.com/2012/06/abigail.html)

**In bibliography ("Fuentes citadas"):**

> - Heather Farrell, "Abigail," *Women in the Scriptures*, https://www.womeninthescriptures.com/2012/06/abigail.html

### Rules for new web sources

1. Each source must be registered in the table above before use — no ad-hoc web citations
2. The source must have a clear, identifiable author and a persistent URL structure
3. Authority and rigor are assessed per the authority model; web sources default to `official: false`
4. The `meta.json` for each downloaded article must include: `source_url` (original permalink), `author`, `site_name`

---

## Implementation Notes

- Scripture reference generation: `src/alejandria/ingestion/scripture_meta.py`
- Cross-reference patterns: `src/alejandria/ingestion/cross_references.py`
- RAG citation rules: `src/alejandria/chat/rag.py` (SYSTEM_PROMPT)
- Abbreviation parsing: `scripts/parse_cross_references.py`
