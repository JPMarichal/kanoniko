---
name: project_disambiguation_depth
description: Three levels of disambiguation — person identity, entity type, temporal/dispensational meaning shifts — plus noise handling and alias resolution
type: project
---

P7 disambiguation requires three distinct levels, not just person-identity resolution:

**Level 1 — Person identity:** Which Judas? Which Mary? Which Nephi? (~8-20 variants per name)
- Also includes **alias resolution**: Peter/Cephas/Simon Peter, Matthew/Levi, Saul/Paul, Jacob/Israel, Emma Smith/Emma Hale Smith
- **Demonyms count**: Mary Magdalene = Mary of Magdala = María Magdalena (handled by modifier detection)
- **Genealogy names**: Judas in Matt 1:2 = Judah the patriarch (KJV English quirk), resolved by source+chapter context

**Level 2 — Entity type:** Judá = person (patriarch), tribe, kingdom, territory. These map differently EN↔ES ("Judah" in KJV Matthew 1:2 = patriarch, same word as kingdom; in Spanish "Judá" vs "Judas" are distinct).
- Bethlehem: two distinct places (Judah and Zebulun/Galilee)
- Israel: person (Jacob) → nation → covenant people → land → modern state

**Level 3 — Temporal/dispensational meaning:** Terms whose meaning shifts across covenant eras:
- Gentiles: non-Hebrews (Abraham) → non-Israelites (Moses) → non-Jews (post-exile) → non-members (Restoration) → European peoples (BofM 1 Nephi 13) → descendants of Japheth
- Zion: City of David → Enoch's city → the pure in heart (D&C 97:21) → New Jerusalem/Missouri → the Church/gathered saints
- Priesthood: Melchizedek vs Aaronic, but also evolving administrative meaning in LDS context
- Israel: person (Jacob) → nation → covenant people → scattered remnant
- Temple: Tabernacle of Moses → Solomon's → Herod's → latter-day → body as temple (metaphor)
- Ark: Noah's Ark vs Ark of the Covenant
- Law: Law of Moses vs Law of the Gospel
- **Objects and concepts shift meaning through time/context** — the same word can be a different thing in a different era

**Noise handling:** Corpus files may contain HTML tags, control chars, footnote markers, stray braces, BOM, etc. The `_clean_window()` function strips these before regex matching to prevent false negatives.

**Bilingual key insight:** ES "Jacobo" = James/Santiago (NT), NOT Jacob the patriarch. Jacob the patriarch is "Jacob" in both EN and ES.

**Why:** The user emphasized that a naive disambiguator misses these. Canonical acceptions need: bilingual name, entity type, applicable period/dispensation, and contextual signals (keywords, books, chapters).

**How to apply:** The disambiguator module supports all three levels. Level 1 is regex+path rules. Level 2 requires type-aware matching (returns entity_type_resolved). Level 3 requires dispensational context awareness (which book/era the passage is in).
