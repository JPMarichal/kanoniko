---
name: On disambiguation pending
description: On (city/Heliopolis) vs On (son of Pelet) — gazetteer should contain both, KG should detect dual membership
type: project
---

"On" is two distinct biblical entities: On the city (Heliopolis, Egypt — Genesis 41:45) and On son of Pelet (Numbers 16:1). The gazetteer currently has On only as person. Both should exist so the KG can build correct relations for each.

**Why:** Correct disambiguation enables proper relationship mapping — On-city connects to Egypt/Joseph/Potipherah, On-person connects to Reuben/Korah's rebellion.

**How to apply:** Lower priority. When working on gazetteer expansion or disambiguation improvements, add On (place) entry with aliases ["Heliopolis", "Heliópolis"] and ensure the extractor/profile system can handle both.
