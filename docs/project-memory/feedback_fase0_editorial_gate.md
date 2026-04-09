---
name: Fase 0 editorial research is a hard gate
description: Never mark material as researched without completing web-based editorial investigation first — authority and KG depend on it
type: feedback
---

The Fase 0 has two mandatory steps before a material can move to `researched`:

1. **Editorial investigation** (web research) — history, publisher context, Church position, editions
2. **Content/value analysis** — authority model, KG value, deduplication, risks

Technical analysis of the download source (HTML selectors, URL patterns, scraping tests, script design)
is NOT part of Fase 0 — it belongs to `prepared`.

**Why:** Without editorial research, authority levels are assigned by assumption and KG relations
are modeled without understanding the material's actual standing. A text that appears doctrinally
solid may have been published without correlation, later disavowed, or have a complex editorial
history that changes its authority entirely (e.g., Journal of Discourses — the Church has specific
statements about their reliability that directly affect authority modeling).

**How to apply:** When analyzing a new corpus material:
- Do NOT skip to technical scraping analysis
- Do NOT assign authority values without editorial evidence
- Do NOT mark as `researched` based on technical feasibility alone
- Always do web research first, then model authority and KG from those findings
- The technical analysis (selectors, scripts) comes after, as part of `prepared`
