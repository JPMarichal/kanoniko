---
name: CRITICAL — NEVER use docker commands; ALWAYS use podman
description: Running docker commands from C:\own\alejandria hits Rancher Desktop and corrupts its containers (C:\git). This project's containers run on Podman Desktop. Every docker command MUST be run as podman instead.
type: feedback
priority: critical
---

## CRITICAL RULE — JAMÁS USAR docker, SIEMPRE usar podman

**NUNCA ejecutar comandos `docker` (como `docker exec`, `docker ps`, `docker logs`, `docker compose`, etc.) desde `C:\own\alejandria` o sus subdirectorios.** Hacerlo corrompe los contenedores visibles en Rancher Desktop, los cuales pertenecen a `C:\git` y no deben mezclarse jamás con los de este proyecto.

**Los contenedores de Alejandría corren en Podman Desktop (`podman-machine-default`), no en Rancher Desktop ni en Docker Engine nativo de WSL.**

### Regla absoluta

> Todo comando `docker X` que pueda correrse como `podman X` DEBE correrse como `podman X`.

### Cómo aplicar

| Operación | Comando correcto | Comando incorrecto |
|-----------|-----------------|-------------------|
| Exec en contenedor | `podman exec -it alejandria-api bash` | `docker exec -it alejandria-api bash` |
| Listar contenedores | `podman ps` | `docker ps` |
| Ver logs | `podman logs alejandria-api` | `docker logs alejandria-api` |
| Compose | `podman compose -f docker/docker-compose.yml up` | `docker compose up` o `docker-compose up` |
| Construir imagen | `podman build -t foo .` | `docker build -t foo .` |
| Podman compose con override GPU | `podman compose -f docker/docker-compose.yml -f docker/docker-compose.podman.yml up -d` | cualquier `docker compose` |

### Scripts y herramientas

- `scripts/gpu-podman.sh` — usa `docker --context podman-machine-default` internamente (resuelve a Podman). Es la excepción permitida porque el binario `docker` apunta a Podman en ese contexto.
- Cualquier script, Justfile, o Makefile que invoque `docker` debe verificarse que realmente opera contra Podman antes de ejecutarse.
- Si hay duda: `podman ps` desde `C:\own\alejandria` — si ves `alejandria-api`, estás en el engine correcto. Si ves contenedores de `C:\git` (`web-shim`, `sso-api`, `mysql`), estás en el engine equivocado.

### Contexto técnico

- `docker` en esta máquina resuelve a Rancher Desktop (Moby/Docker Engine) que maneja los contenedores de `C:\git`.
- Los contenedores de Alejandría (`alejandria-api`, `alejandria-tunnel`, `alejandria-ollama`) corren en Podman Desktop.
- Mezclar los engines causa corrupción de contenedores de Rancher Desktop (se vuelven inestables, desaparecen, o se duplican).

### Historial

- Anteriormente (pre-2026-07-04) Alejandría corría en Docker Engine nativo de Ubuntu-20.04 WSL con GPU. Ese stack está deprecado.
- Desde 2026-07-04: Alejandría corre exclusivamente en Podman Desktop. Ver `project_podman_migration.md`.
