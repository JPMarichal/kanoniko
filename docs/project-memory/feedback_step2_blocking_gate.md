---
name: Step 2 research is a hard gate — produce Fase 0 before any config or download
description: NEVER register ManualConfig entries, assign authority, or prepare download scripts without first completing and WRITING the Fase 0 analysis file
type: feedback
---

Step 2 of the corpus addition procedure (Research the material) is a HARD BLOCKING GATE. No ManualConfig, no authority assignment, no download script work can proceed without it.

**Rule:** Before registering any new material in `download_manual.py` or any download script, you MUST first write a Fase 0 analysis file in `proj/P4-corpus-expansion/fase0/{slug}.md` covering: what it is, who produced it, when, for whom, how referenced, and KG relationships. The written file is the verifiable deliverable that proves the gate was passed.

**Why:** This has been violated multiple times. The pattern is: see a slug on the site, have the script handy, register a ManualConfig with authority guessed from the title alone. This produces incorrect authority values, superficial tags, and missed KG relationships. The procedure explicitly says "This step is BLOCKING — steps 3 through 8 cannot proceed without it" and "Verifying URL slugs and counting TOC entries is NOT research."

**How to apply:** When encountering new corpus material candidates:
1. STOP after identifying them (step 1: classify)
2. Research each one via web search (step 2) — understand nature, provenance, weight
3. Write a Fase 0 file in `proj/P4-corpus-expansion/fase0/{slug}.md` — this is the deliverable
4. Add item to `proj/P4-corpus-expansion/04-backlog.md` with status `researched`
5. ONLY THEN proceed to authority assignment (step 3), KG pre-seed (step 4), and config/script (step 5)

If you catch yourself writing ManualConfig before writing Fase 0, you have violated the gate. Back up and research first.
