---
name: Alejandría always runs on GPU Docker stack
description: ALL Alejandría operations (indexing, containers, docker) MUST use the GPU stack in Ubuntu-20.04 WSL — never Rancher, never optional.
type: feedback
---

ALL Alejandría work MUST go through the GPU Docker stack. This is the default, not a choice.

NEVER run `docker stats`, `docker ps`, or any docker command from Windows for Alejandría. That hits Rancher Desktop and shows k8s_* pods — completely irrelevant.

**CRITICAL: The SQLite DB on Windows (`data/sqlite/alejandria.db`) is NOT the source of truth.** The authoritative DB lives inside the GPU container (`/app/data/sqlite/alejandria.db`). The local Windows copy can be severely outdated (e.g., 19,770 docs vs 30,757 real). **Any query about indexed content, corpus status, or pending files MUST go through the container**, never through the local file.

**Why:** User has corrected this multiple times. Alejandría containers run on Docker Engine nativo (with NVIDIA GPU) in Ubuntu-20.04 WSL, not Rancher Desktop. The GPU stack is always the target — there is no "non-GPU" option for Alejandría. Querying the local DB caused a false report of 22K pending files when only 51 were actually pending.

**How to apply:**
- For ANY Alejandría container/indexing operation, always use: `wsl -d Ubuntu-20.04 bash -c "docker ..."`
- To query the DB: `wsl -d Ubuntu-20.04 bash -c "docker exec alejandria-api python -c '...'"`
- To check API: `wsl -d Ubuntu-20.04 bash -c "curl -s http://localhost:4300/..."`
- Never query `C:/own/alejandria/data/sqlite/alejandria.db` directly for status — it's stale
- Never ask "should we use GPU?" — the answer is always yes
- This includes `docker stats`, `docker ps`, `docker compose`, `docker logs`, indexing, everything
- Use `scripts/gpu-up.sh` for stack management
