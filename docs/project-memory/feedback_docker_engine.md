---
name: Alejandría always runs on GPU Docker stack
description: ALL Alejandría operations (indexing, containers, docker) MUST use the GPU stack in Ubuntu-20.04 WSL — never Rancher, never optional.
type: feedback
---

ALL Alejandría work MUST go through the GPU Docker stack. This is the default, not a choice.

NEVER run `docker stats`, `docker ps`, or any docker command from Windows for Alejandría. That hits Rancher Desktop and shows k8s_* pods — completely irrelevant.

**Why:** User has corrected this multiple times. Alejandría containers run on Docker Engine nativo (with NVIDIA GPU) in Ubuntu-20.04 WSL, not Rancher Desktop. The GPU stack is always the target — there is no "non-GPU" option for Alejandría.

**How to apply:**
- For ANY Alejandría container/indexing operation, always use: `wsl -d Ubuntu-20.04 bash -c "docker ..."`
- Never ask "should we use GPU?" — the answer is always yes
- This includes `docker stats`, `docker ps`, `docker compose`, `docker logs`, indexing, everything
- Use `scripts/gpu-up.sh` for stack management
