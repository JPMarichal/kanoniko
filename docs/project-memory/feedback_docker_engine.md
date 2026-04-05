---
name: Alejandría runs on native Docker Engine, NOT Rancher
description: NEVER use plain docker commands from Windows for Alejandría — they hit Rancher Desktop. Always use wsl -d Ubuntu-20.04.
type: feedback
---

NEVER run `docker stats`, `docker ps`, or any docker command from Windows to check Alejandría containers. That hits Rancher Desktop and shows k8s_* pods — completely irrelevant.

**Why:** User has had to correct this multiple times across sessions. Alejandría containers run on Docker Engine nativo in Ubuntu-20.04 WSL, not Rancher Desktop.

**How to apply:** For ANY Alejandría container operation, always use:
```
wsl -d Ubuntu-20.04 bash -c "docker ..."
```
This includes `docker stats`, `docker ps`, `docker compose`, `docker logs`, everything.
