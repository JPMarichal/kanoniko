# Authority Model

The authority model defines how Alejandría weighs and classifies corpus materials. Every document carries metadata across three independent axes plus a boolean official flag.

**Granularity:** Authority is assigned at the **article/chunk level**, not at the publication level. This is critical for mixed-authority publications like Church magazines (Liahona, Ensign, New Era, Friend), where a single issue contains First Presidency messages (80), reprinted Conference talks (70–80), staff-written doctrinal articles (60), and personal testimonials (50–55).

## Axes

### 1. Doctrinal Authority (1–100)

Measures the weight a source carries for establishing LDS doctrine. Fixed per document based on its category.

| Range | Category | Examples |
|-------|----------|----------|
| **100** | Canon | Standard Works + Official Declarations 1–2 (sustained by vote as part of D&C) |
| **90** | Quasi-canonical | The Family Proclamation, The Living Christ (placed in scriptures section of Church website, issued by united FP+Q12, cited as doctrine, but not formally canonized by sustaining vote) |
| **80** | Prophetic — First Presidency / Q12 | General Conference talks by apostles and prophets (individual) |
| **70** | Prophetic — other General Authorities | Talks by Seventies, General Presidency members |
| **65** | Normative | Church Handbook (official policy/governance; evolves over time) |
| **60** | Correlated | Manuals, curriculum (Come Follow Me, institute manuals, etc.) |
| **57** | Study aids — explanatory | Guide to the Scriptures (GEE) — correlated, explanatory content |
| **55** | Study aids — referential | Topical Guide, Bible Dictionary (carry explicit disclaimer: "not intended as an official or revealed endorsement") |
| **55** | Official communications | Bulletins, official letters, press releases |
| **45** | GA as private author — adopted officially | *Jesus the Christ*, *Articles of Faith* (Talmage) |
| **35** | GA as private author — unofficial (with disclaimer) | *Mormon Doctrine*, *Doctrinal New Testament Commentary* |
| **30** | Institutional LDS scholarship | BYU Studies, FARMS / Maxwell Institute |
| **25** | LDS apologetics / outreach | FairMormon, Book of Mormon Central |
| **20** | Independent LDS scholarship | LDS authors with credentials, no institutional backing |
| **15** | General scholarly reference | Bible dictionaries, commentaries (Anchor Bible, etc.) |
| **10** | Historical / patristic | Apostolic Fathers, ancient documents, manuscripts |
| **5** | Interdenominational / non-LDS | Evangelical, Catholic, secular academic authors |

Gaps between ranges are intentional — they allow future sub-levels (e.g., speaker-calling stratification in the 70–80 range) without renumbering.

**Key distinctions:**
- **OD 1–2 at 100:** They were added to the D&C by sustaining vote (1908 and 1981) — they are canon, not quasi-canonical.
- **Study aids split (57/55):** The GEE contains explanatory doctrinal content; the TG is an index and the BD carries an explicit "not official" disclaimer. Neither should be at the same level as Come Follow Me manuals.
- **Consensus modifier:** Based on the principle of common accord (D&C 107:27 — "every decision made by either of these quorums must be by the unanimous voice of the same"), united statements carry more weight than individual ones. See Consensus Modifier section below.

### 2. Rigor (1–100)

Measures how well-supported and verifiable the claims in a document are, independent of doctrinal authority. A FARMS paper (authority 30) may score higher in rigor than a correlated manual (authority 60).

#### Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Primary sources** | High | Does it cite original sources, or is it secondhand/thirdhand? |
| **Verifiability** | High | Can claims be checked? Are references traceable? |
| **Scholarly apparatus** | Medium | Footnotes, bibliography, original-language analysis |
| **Review process** | Medium | Peer-reviewed, correlation-reviewed, or unreviewed? |
| **Internal consistency** | Medium | Is it coherent within its own framework? |
| **Temporal proximity** | Low | How close to the event is the source? Eyewitness > 200-year-old tradition |
| **Fact vs. opinion distinction** | Low | Does the text separate what it knows from what it speculates? |

#### Default Values by Category

| Category | Rigor default | Rationale |
|----------|---------------|-----------|
| Scriptures | 100 | Revelation is the ultimate primary source within the framework of faith |
| Peer-reviewed academic papers | 85 | Full scholarly apparatus, peer review |
| General Conference talks | 70 | Correlation-reviewed, not peer-reviewed |
| Study aids (GEE, TG, BD) | 70 | Researched, reviewed, with disclaimer |
| Correlated manuals | 65 | Correlation-reviewed, simplified for audience |
| GA books — official | 60 | Researched but not peer-reviewed |
| Apologetics (Fair, BMC) | 60 | Researched, sometimes peer-reviewed |
| GA books — unofficial | 50 | Variable quality, no institutional review |
| News | 45 | Journalistic standards, not academic |
| Oral tradition / folk | 15 | Secondhand or worse, unverifiable |

These are defaults; individual documents may override based on their actual content. Partial automation is possible: parsers can detect presence of footnotes, bibliography, and citations as rigor indicators.

#### The Scripture Special Case

Scriptures receive rigor 100 not by academic criteria but by theological axiom: within the faith framework, divine revelation is the primary source par excellence. This avoids the need for exceptions in the RAG formula.

### 3. The Four I's (Importance)

A spiritual-practical classification of a document's value:

| Category | Definition | Stability |
|----------|-----------|-----------|
| **Imprescindible** | Directly helps gain eternal life | Most stable, easiest to determine |
| **Importante** | Helps live this life better | May degrade to Interesante |
| **Interesante** | Sparks engagement and curiosity | May degrade to Irrelevante |
| **Irrelevante** | Dispensable | — |

The scale has downward gravity — items tend to fall, not rise. The anchor is soteriological: what saves is imprescindible; everything else is ordered from there.

This is a **base value per document**. The RAG pipeline applies a contextual degradation layer (never promotion) based on query type:

#### Contextual Degradation

The base importance can only go **down**, never up — respecting the scale's downward gravity.

| Base | Doctrinal | Soteriological | Historical | Teaching/Preparation | Exploratory |
|------|-----------|---------------|------------|---------------------|-------------|
| **Imprescindible** | Imprescindible | Imprescindible | Imprescindible | Imprescindible | Imprescindible |
| **Importante** | Importante | → Interesante | Importante | Importante | Importante |
| **Interesante** | → Irrelevante | → Irrelevante | Interesante | **Interesante** | Interesante |
| **Irrelevante** | Filtered out | Filtered out | Filtered out | Filtered out | Filtered out |

**Rules:**
- **Imprescindible never degrades** — it is the soteriological anchor.
- **Irrelevante is always filtered** — it never enters the ranking.
- **Importante and Interesante shift down** based on query type, helping filter speculation and low-relevance content.
- **Teaching/Preparation preserves Interesante** — in this context, Interesante content has high pedagogical value: it serves as illustration, engages attention, provides structural thread, anchors memory, and shows practical application. A good talk or lesson needs Interesante material as the vehicle that makes doctrine tangible and memorable. This category includes talks, lessons, articles, and outreach content. Articles fall under teaching and outreach — their purpose is to make scholarship accessible. Reverent humor also applies here as a legitimate pedagogical tool.
- The degradation connects to `chat_classify`, which already determines query type.

## Official Flag

Boolean attribute: `official: true/false`.

**Rule:** Gospel Library content is official by default. External sources are unofficial by default. Exceptions are marked explicitly.

The distinction matters because most unofficial books by General Authorities and independent authors carry an explicit disclaimer. The presence or absence of the disclaimer is a clean, verifiable criterion.

### Current Flag

Boolean attribute: `current: true/false`. Indicates whether the document is still in active use or circulation.

This separates two independent concepts:

| official | current | Example |
|----------|---------|---------|
| true | true | Current Come Follow Me manual |
| true | false | Retired Gospel Principles manual |
| false | true | *Mormon Doctrine* 2nd ed. (unofficial but still circulating and widely cited) |
| false | false | *Mormon Doctrine* 1st ed. (superseded by 2nd edition) |

**Note on authority over time:** Authority reflects the document's current standing, not its original standing. A book adopted officially (*Jesus the Christ*) carries its current authority (45), not its original (~35). If a document's standing changes, the authority value is updated — no history is maintained in metadata. Historical context for such changes belongs in the KG or in metadata notes.

## News Sources

News content requires per-source evaluation for the official flag:

| Source | Official | Notes |
|--------|----------|-------|
| Church Newsroom (newsroom.churchofjesuschrist.org) | Yes | Official institutional communications |
| Church News (thechurchnews.com) | Yes | Owned by Deseret News, closely tied to the Church |
| Más Fe | No | Independent Spanish-language LDS news |
| Deseret News (religion section) | No | Church-owned newspaper but editorial independence |
| LDS Living | No | Popular LDS media, independent editorial |
| Meridian Magazine | No | Independent LDS publication |
| BYU Speeches / BYU News | No | Institutional but not Church-correlated |

**Criteria for evaluating new sources:** A news source is official only if it meets at least one:
1. Is owned by or under the editorial direction of the Church
2. Publishes content reviewed/approved by the Church

Sources with editorial independence are not official, even if Church-owned (e.g., Deseret News). Most sources outside this list either replicate news from official sources or are fully independent — adding a new official source is unlikely.

## Document Metadata Schema

```json
{
  "authority": 80,
  "rigor": 70,
  "importance": "imprescindible",
  "official": true,
  "current": true,
  "context": "general-conference",
  "consensus": "individual",
  "audience": "adult",
  "speaker_calling": "q12",
  "source": "gospel-library"
}
```

Optional fields for specific content types:
```json
{
  "hymn_doctrinal": "credal"
}
```

### Delivery Context Modifier

The authority of a General Authority's statement depends on the forum in which it was delivered. A prophet "is a prophet only when he was acting as such" (Joseph Smith, HC 5:265). The delivery context is one indicator of when a leader is acting in their prophetic capacity.

| Context | Modifier | Rationale |
|---------|----------|-----------|
| `general-conference` | ×1.0 | Most official regular forum; talks are reviewed and correlated |
| `official-letter` | ×1.0 | First Presidency letters, official declarations |
| `stake-conference` | ×0.9 | Official setting, but regional scope |
| `devotional` | ×0.85 | BYU devotionals, CES firesides — institutional but not correlated |
| `book-official` | ×0.8 | Book written by GA, adopted officially |
| `book-unofficial` | ×0.7 | Book written by GA, with disclaimer |
| `interview` | ×0.5 | Press interviews, media appearances |

The modifier applies to the base authority of the speaker's calling level. For example, an apostle (base 80) giving a BYU devotional: 80 × 0.85 = 68.

### Consensus Modifier

Based on the principle of common accord (D&C 107:27 — "every decision made by either of these quorums must be by the unanimous voice of the same"), united statements carry more weight than individual ones.

| Voice | Modifier | Examples |
|-------|----------|----------|
| United FP + Q12 | ×1.15 | Proclamations, official declarations, joint statements |
| United First Presidency (3) | ×1.10 | First Presidency letters, official messages |
| Individual (default) | ×1.0 | Single apostle's conference talk |

The consensus modifier stacks with the delivery context modifier. For example, a First Presidency letter (base 80 × context 1.0 × consensus 1.10 = 88).

### Hymns Doctrinal Scale

Hymns are official and correlated (base authority 60), but their individual doctrinal weight varies significantly. Each hymn carries an individual doctrinal classification:

| Classification | Description | Examples |
|----------------|-------------|----------|
| **Credal** | Expresses core doctrine directly; near-scriptural weight | "I Know That My Redeemer Lives," "The Spirit of God" |
| **Doctrinal** | Teaches specific doctrine clearly | "A Child's Prayer," "I Am a Child of God" |
| **Devotional** | Expresses worship, gratitude, commitment — doctrinally neutral | "How Great Thou Art," "Be Still My Soul" |
| **Seasonal/Topical** | Tied to an occasion or theme, minimal doctrinal content | Holiday hymns, processional hymns |

This classification is assigned per hymn as a metadata attribute (`hymn_doctrinal: "credal" | "doctrinal" | "devotional" | "seasonal"`).

### Audience Attribute

Audience is a metadata attribute that informs the RAG pipeline about the precision level of doctrinal content. Correlated materials for all audiences pass through the same Correlation process, but simplification for younger audiences may reduce doctrinal precision.

| Audience | Precision | Examples |
|----------|-----------|----------|
| `adult` | Full | Ensign/Liahona, institute manuals, General Conference |
| `youth` | Moderate | New Era, For the Strength of Youth, seminary |
| `children` | Simplified | Friend, Primary manuals |
| `leadership` | Full + policy | Church Handbook, leadership training |
| `general` | Default | Most materials without specific audience |

The audience does not change the authority score but is available as a filter or signal for the RAG pipeline (e.g., prefer `adult` or `leadership` precision for doctrinal questions).

### Speaker-Calling Stratification

The base authority for a General Authority's statement depends on the calling they held **at the time of the statement**, not their highest lifetime calling. When the calling at the time is unknown, use the closest known calling.

#### Current Callings

| Base | Calling |
|------|---------|
| **85** | President of the Church |
| **83** | Counselors in the First Presidency |
| **80** | Members of the Quorum of the Twelve Apostles |
| **75** | Presidency of the Seventy |
| **73** | Members of the First Quorum of the Seventy |
| **71** | Members of the Second Quorum of the Seventy |
| **70** | Presiding Bishop / counselors |
| **68** | General presidencies (Relief Society, Young Men, Young Women, Primary, Sunday School) |

**Notes:**
- Area Seventies are **not** General Authorities — they fall outside this table.
- The base authority is then modified by the delivery context and consensus modifiers.
- Example: President of the Church (85) in General Conference (×1.0) = 85. The same person speaking as an apostle (80) in a BYU devotional (×0.85) in 1995 = 68.

#### Historical Callings

Callings that no longer exist but appear in historical corpus materials:

| Base | Calling | Years | Rationale |
|------|---------|-------|-----------|
| **78** | Presiding Patriarch of the Church | 1833–1979 | Sustained as prophet, seer, and revelator (D&C 124:91-94); sustained before Q12 in conference order; hereditary (Smith line); limited governing authority. Last holder: Eldred G. Smith (emeritus 1979, d. 2013) |
| **76** | Assistant to the Quorum of the Twelve | 1941–1976 | General Authorities; ranked above Seventies in conference order; Kimball equated their function to the First Quorum of the Seventy when absorbing them in 1976. 38 men served. |
| **75** | First Council of the Seventy (7 presidents) | 1835–1976 | Presided over all quorums of Seventy; only Seventies who were General Authorities. Function maps to current Presidency of the Seventy. Rank-and-file Seventy members were local leaders, not GAs. |

**Notes:**
- **Church Historian and Recorder** — not a separate authority level; derives from the holder's underlying calling (apostle, seventy, etc.).
- **Regional Representative of the Twelve** (1967–1995) — were **not** General Authorities; no authority level assigned.
- **Presiding Bishop** — still exists; historical prominence was broader but doctrinal authority level (70) remains appropriate.

**Doctrinal foundation:** D&C 68:4 establishes that what leaders speak "when moved upon by the Holy Ghost" is scripture. The conditional "when" means the promise is not automatic — it depends on the Spirit's influence at the moment of speaking. The delivery context helps approximate the likelihood that a statement was made in the leader's prophetic capacity, not as a personal opinion. This is complementary to, not in tension with, the principle that the living prophet can speak for God — it simply acknowledges that he does not always choose to do so in every setting (as Joseph Smith himself taught).

## Impact on RAG Ranking

The three axes feed into the reranking formula:

```
score = semantic_similarity × w1
      + authority × w2
      + rigor × w3
      + importance_boost(4i)
```

Weights vary by query type (determined by `chat_classify`):
- **Doctrinal question** → higher `w2` (authority)
- **Historical question** → higher `w3` (rigor), lower `w2`
- **Exploratory question** → balanced weights

## Pending Design Decisions

*No pending design decisions remain. All axes, modifiers, and attributes are fully defined.*

## Design Decisions Made

- **Authority is not language-dependent.** A Spanish translation has the same authority as the English original. However, language can provide historical traceability in some contexts.
- **Always latest edition.** Scriptures and manuals use the most recent edition. Prior editions have historical value but are out of scope for now.
- **Church Handbook is normative (65)**, above correlated materials (60) — it is the governing policy reference and its content evolves over time.
- **Official communications (55)** — bulletins and official letters are official, placed between institutional news and correlated materials.
- **Delivery context modifier** — forum of delivery modifies base authority (×1.0 for General Conference down to ×0.5 for interviews). Based on Joseph Smith's principle that a prophet acts as such conditionally, complemented by D&C 68:4's "when moved upon by the Holy Ghost."
- **Consensus modifier** — united voice (FP+Q12 ×1.15, FP ×1.10) outweighs individual statements. Based on D&C 107:27 (common accord principle).
- **Rigor axis fully defined** — 7 evaluation criteria, default values by category, scriptures at 100 by theological axiom.
- **Hymns doctrinal scale** — per-hymn classification: credal, doctrinal, devotional, seasonal.
- **Audience attribute** — metadata field (adult, youth, children, leadership, general) informs precision level; does not change authority score.
- **Speaker-calling stratification** — base authority by calling at time of statement (85 President → 68 general presidencies). Temporal rule: calling at date of statement, not highest lifetime calling. Area Seventies excluded (not GA).
- **Historical callings resolved** — Presiding Patriarch (78), Assistant to Q12 (76), First Council of the Seventy (75). Church Historian derives from underlying calling. Regional Representatives were not GAs.
- **News source criteria resolved** — official if Church-owned/directed or Church-approved content. Most sources outside the established list either replicate or are independent; adding a new official source is unlikely.
- **Contextual 4 I's resolved** — base importance can degrade by query type (never promote). Imprescindible never degrades; Irrelevante always filtered; middle categories shift down for doctrinal/soteriological queries. Connects to `chat_classify`.
