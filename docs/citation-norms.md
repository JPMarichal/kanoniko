# Citation Norms — FCD (Formato de Citas para Dilton)

Standards for citing all corpus materials in Alejandría — for RAG answers, search results, and any output that references corpus content.

## General Principles

1. **Language consistency:** Citations follow the language of the passage being cited. Never mix languages within a single citation.
2. **Literal quotes only:** Quote text exactly as it appears in the corpus. Never paraphrase a quoted passage.
3. **Reference in parentheses:** Always at the end of the quoted text, never on a separate line.
4. **Titles of works** in quotes: "Jesús el Cristo", "Liahona", not in italics.

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

For manuals, biographies, and web content — cite by title (in quotes) and author when available.

### Examples

**Inline:**

> Talmage explica que la transfiguración fue "una manifestación especial de la gloria divina del Señor" ("Jesús el Cristo", capítulo 23).

> El manual de instituto señala que "cada dispensación comienza con una revelación directa del cielo" ("Doctrina y Convenios — Manual del alumno", lección 2).

**Outline:**

> La expiación de Cristo no fue solo para eliminar el pecado del arrepentido. Fue también para absorber toda pena y sufrimiento humano, para que Él supiera cómo socorrer a su pueblo según las enfermedades de ellos. ("Jesús el Cristo", James E. Talmage, capítulo 35)

---

## Implementation Notes

- Scripture reference generation: `src/alejandria/ingestion/scripture_meta.py`
- Cross-reference patterns: `src/alejandria/ingestion/cross_references.py`
- RAG citation rules: `src/alejandria/chat/rag.py` (SYSTEM_PROMPT)
- Abbreviation parsing: `scripts/parse_cross_references.py`
