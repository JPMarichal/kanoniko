---
name: Always include ETA in status updates
description: Every progress report must include an ETA — never make the user ask for it
type: feedback
---

Always include ETA in any progress/status report. Never report progress without an estimated time remaining.

**Why:** User had to explicitly ask for ETAs multiple times during indexing monitoring. It should be standard.

**How to apply:** Any time you report progress (indexing, downloads, long-running ops), include: current %, rate, and ETA. Format: `X% — rate Y/min — ETA ~Zm`
