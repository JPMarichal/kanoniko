# Podman Migration (2026-07-01)

## Status: COMPLETE (RESOLVED 2026-07-04)

Alejandría containers (`alejandria-api`, `alejandria-ollama`) migrated from native Docker Engine (Ubuntu-20.04 WSL) to Podman Desktop (`podman-machine-default`).

## What was done

1. **Created `docker/docker-compose.podman.yml`** — Podman-specific compose override:
   - Uses pre-built `docker-api:latest` image (migrated from native Docker)
   - GPU via CDI (`nvidia.com/gpu=all`)
   - Volumes mapped to `/mnt/c/...` paths
   - `host.containers.internal` for Postgres tunnel access
   - Ollama with GPU support

2. **Migrated `docker-api:latest` image** (8.7 GB) from native Docker to Podman
   - Saved from native Docker context, loaded into Podman context
   - Image was built 2026-05-23 from `Dockerfile.gpu` (CUDA nightly, Blackwell support)

3. **Deployed both containers** on Podman:
   - `alejandria-api` — running and healthy
   - `alejandria-ollama` — running and healthy, GPU confirmed:
     - NVIDIA RTX PRO 500 Blackwell, CUDA 12.0, 6GB VRAM

4. **Created `scripts/gpu-podman.sh`** — management script for Podman deployment
   - Usage: `bash scripts/gpu-podman.sh [up|down|status|test|logs|ollama]`
   - Uses `docker --context podman-machine-default` for all operations
   - GPU test, SSH tunnel management, repo sync, model pulling
   - Updated 2026-07-04: SSH tunnel starts from Podman machine (not Windows/WSL)

## Resolved issues

### SSH tunnel to IONOS Postgres (RESOLVED 2026-07-04)
- Root SSH + console password recovery via IONOS GParted rescue DVD
- SSH key `id_ed25519` (`alejandria-laptop-wsl`) authorized in `/root/.ssh/authorized_keys`
- SSH tunnel now runs inside the Podman machine (`podman machine ssh`) not from Windows host
- `host.containers.internal:15432` reachable from containers because tunnel is in the same VM
- `scripts/gpu-podman.sh` `ensure_postgres_tunnel()` starts tunnel via `podman machine ssh`
- API health: full green (FTS + embeddings + KG)

### SSH + console password recovery (2026-07-04)
When both SSH and IONOS console root password are lost:
1. IONOS Cloud Panel → Infrastructure > Server → DVD drive → GParted latest_iso
2. Load DVD (server reboots into rescue)
3. Open remote console → Enter command line prompt
4. Identify root partition (`lsblk` → typically `/dev/vda1`)
5. `mount /dev/vda1 /mnt && chroot /mnt`
6. `passwd root` to set new password
7. `exit && sync && umount /mnt`
8. Eject DVD and restart via Cloud Panel
9. Authorize SSH key: add pubkey to `/root/.ssh/authorized_keys`
10. Note: `authorized_keys` may have `i` (immutable) and `a` (append-only) attributes — `chattr -ia` before editing

### Future considerations
- `docker/docker-compose.gpu.yml` — kept for reference
- Native Docker daemon override.conf — kept in WSL, can be removed when migration is stable
- Docker context `alejandria` — kept for reference, points to native Docker TCP socket

## Relevant files
- `docker/docker-compose.podman.yml` — Podman compose override
- `scripts/gpu-podman.sh` — Management script
- `scripts/gpu-up.sh` — Original script (still works for native Docker)
