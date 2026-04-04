# P7 — Deep Disambiguation — Project Plan

## Phases

### Phase 1 — Rule-Based Disambiguation ✅ Complete

**Goal:** Three-level disambiguation engine integrated into the extraction pipeline.

**Deliverables:**

1. ✅ **Level 1 — Person identity** (`disambiguator.py`):
   - 8 core ambiguous entities: Judas, James/Santiago, Mary/María, John/Juan, Joseph/José, Nephi/Nefi, Alma, Moroni
   - 16+ bilingual name variants in `_DISAMBIGUATION_RULES` registry
   - Modifier detection (regex in ~200-char window) + source-file path matching
   - Confidence tiers: high / medium / low with human-readable evidence
   - **Alias resolution** (same person, multiple names):
     - Peter / Cephas / Simon Peter / Pedro / Cefas / Simón Pedro
     - Matthew / Levi / Mateo / Leví (with NT vs OT Levi disambiguation)
     - Saul / Paul / Saúl / Saulo / Pablo (with King Saul vs apostle)
     - Jacob / Israel (patriarch) / Jacobo (ES composite: James or Jacob)

2. ✅ **Level 2 — Entity-type disambiguation**:
   - **Judah/Judá** → person (patriarch), people (tribe), polity (kingdom), place (territory)
     - Bilingual asymmetry: EN "Judah" covers all; ES "Judá" = patriarch/tribe/kingdom/territory, "Judas" = NT persons only
     - KJV genealogy quirk: "Judas" in Matt 1:2 = patriarch Judah
   - **Israel** → person (Jacob), nation (people), covenant concept, kingdom (polity), land (place)
   - **Bethlehem/Belén** → Bethlehem of Judah (Ephratah) vs Bethlehem of Zebulun (Galilee, Ibzan)
   - Returns `entity_type_resolved` field to override original entity type

3. ✅ **Level 3 — Temporal/dispensational meaning**:
   - **Gentiles** → non-Hebrews (Abraham) → non-Israelites (Moses) → non-Jews (post-exile) → non-members (Restoration) → European peoples (BofM 1 Nephi 13)
   - **Zion/Sión** → City of David → City of Enoch → pure in heart (D&C 97:21) → New Jerusalem/Missouri → the Church
   - **Priesthood/Sacerdocio** → Melchizedek vs Aaronic, plus conferral context
   - **Temple/Templo** → Tabernacle of Moses, Solomon's Temple, Herod's Temple, latter-day temples, body as temple
   - **Ark/Arca** → Noah's Ark vs Ark of the Covenant
   - **Law/Ley** → Law of Moses vs Law of the Gospel

4. ✅ **Noise handling**: `_clean_window()` strips HTML tags, control chars, footnote markers, HTML entities, stray braces, and zero-width characters before regex matching

5. ✅ **Generative syntactic patterns** (fallback for ANY entity name):
   - 19 EN patterns + 19 ES patterns that detect entity type from surrounding syntax
   - Categories: people (tribe/descendants/demonym), place (land/territory/geography), polity (kingdom/ruler), person (genealogy/kinship/verbs/aliases)
   - Covers hundreds of multi-type entities (Esau/Edom, Ephraim, Dan, Manasseh, Moab, Ammon, Gad, Asher, Naphtali, Reuben, Simeon, Gilead, etc.) without per-name rules
   - `_try_generative()` fires as fallback when no name-specific rule exists in the registry
   - Confidence ranking: picks highest-confidence match; short-circuits on "high"
   - `resolve()` flow: name-specific rules → generative fallback → None

6. ✅ **Gazetteer alias cleanup** (`scripts/cleanup_gazetteer_aliases.py`):
   - Removed 134 redundant entries (existed as both top-level and alias of same entity in same type)
   - Fixed 31 bad alias relationships (different entities incorrectly linked: Judah≠Hodevah, Sarah≠Serah, Moroni≠Captain Moroni, Sargon≠Sennacherib, etc.)
   - Transferred 35 bilingual aliases (ES variants) to primary entries before removal
   - 2805 → 2671 entries; 4 minor overlaps remain (Eliphelet, Heldai, Rosh — need biblical research)

7. ✅ **Pipeline integration**:
   - `ExtractionResult.disambiguations` — original_name → resolved_name
   - `ExtractionResult.disambiguated_types` — original_name → resolved entity type (Level 2)
   - `DisambiguatedMention.entity_type_resolved` — new field for type overrides
   - All 3 pipeline locations (incremental, legacy, rebuild_kg) pass disambiguation results to `batch_link_entities_to_document()` including resolved type
   - `MENTIONED_IN` edges carry `resolved_name` and `confidence` properties

### Phase 2 — LLM-Assisted Resolution (deferred)

**Goal:** LLM handles hard cases that rules cannot resolve.

**Tasks:**
1. Design LLM prompt: passage + candidates → resolved entity + confidence
2. Identify mentions that rules couldn't resolve (no match or low confidence)
3. Batch LLM calls for unresolved mentions
4. Store results and update graph links

**Deferred** — same as P6/P10 LLM extraction; will run when Sonnet tier is available.

### Phase 3 — Profile & Graph Update (deferred)

**Goal:** Profiles reflect disambiguated counts.

**Tasks:**
1. Update `build_metadata_profiles()` to use resolved entity names
2. Regenerate affected profiles with specific mention counts
3. Validation: Judas Iscariot has accurate count, not inflated by other Judases

**Deferred** — depends on Phase 2 LLM pass for full coverage.

## Entity Coverage Summary

| Category | Entities | Variants |
|----------|----------|----------|
| Level 1 — Person identity | 22 core + alias groups | ~80 registry entries |
| Level 2 — Entity type | Judah, Israel, Bethlehem | 3 entities × 4-5 types each |
| Level 3 — Temporal meaning | Gentiles, Zion, Priesthood, Temple, Ark, Law | 6 entities × 3-6 meanings each |
| Generative fallback | ANY entity name | 19 EN + 19 ES syntactic patterns |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Rules become complex and hard to maintain | Medium | Keep rules simple; LLM handles edge cases in Phase 2 |
| LLM costs for corpus-wide disambiguation | High | Rule-based first; LLM only for unresolved |
| Incorrect disambiguation degrades quality | Medium | Confidence scoring; only apply high/medium resolutions |
| Corpus noise (HTML, footnotes, control chars) | Medium | `_clean_window()` strips noise before matching |
| Bilingual asymmetry mishandled | High | Separate rules per language; EN/ES-aware registry |

## Success Criteria

1. "Judas Iscariot" has accurate mention count (not inflated by other Judases)
2. "Judah" in Genesis resolves to patriarch; in Kings to kingdom; in geographic context to territory
3. "Gentiles" in 1 Nephi 13 resolves to "European peoples", in NT to "non-Jews"
4. "Zion" in D&C resolves to "pure in heart" or "New Jerusalem", in Psalms to "Mount Zion"
5. Peter/Cephas/Simon Peter all resolve to the same canonical "Peter"
6. Bethlehem in Judges 12 resolves to Zebulun, elsewhere to Judah
