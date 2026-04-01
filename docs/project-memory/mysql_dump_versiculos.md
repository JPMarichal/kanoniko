---
name: mysql_dump_versiculos
description: MySQL dump contains 42,699 verses extracted from official Church site in Spanish — covers all 5 standard works, can fill missing ES corpus (AT, NT, D&C, PGP)
type: project
---

The MySQL dump at `proj/P1-scripture-structure/recursos/dump-scriptures_db-202603281925.sql` contains a `versiculos` table with 42,699 verse records extracted directly from the official Church website in Spanish.

**Why:** The Spanish corpus currently only has Book of Mormon (239 files). AT, NT, D&C, and PGP are missing in Spanish. The dump's verse data is the ready-made source to fill this gap.

**How to apply:** When working on corpus expansion or Spanish content tasks, use the `versiculos` table as the authoritative source for ES scripture text. The verses are already linked to chapters via `PericopaId` → `CapituloId`, so they can be reassembled into chapter files matching the corpus format (`corpus/es/scriptures/{volume}/{book}/{chapter}.txt`).
