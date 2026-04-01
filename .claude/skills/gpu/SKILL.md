---
name: gpu
description: Manage the GPU Docker stack (Ubuntu WSL native Docker Engine) — start, stop, status, test, logs. Independent from Rancher Desktop.
---

# GPU Docker Stack Management

Manage Alejandría's GPU-accelerated Docker stack running on the native Docker Engine in Ubuntu-20.04 WSL. This stack is **completely independent** from Rancher Desktop.

## Architecture

- **Docker Engine:** Native in Ubuntu-20.04 WSL (NOT Rancher Desktop)
- **GPU:** NVIDIA RTX PRO 500 Blackwell, 6GB VRAM, CUDA 13.0
- **PyTorch:** Nightly cu128 (required for Blackwell sm_120)
- **Ports:** Same as Rancher stack (4300, 6333, 7474, 7687) — cannot run simultaneously

## Commands

All commands run via the `gpu-up.sh` script from Windows:

### Start GPU stack
```bash
wsl -d Ubuntu-20.04 -e bash //mnt/c/own/alejandria/scripts/gpu-up.sh up
```

### Stop GPU stack
```bash
wsl -d Ubuntu-20.04 -e bash //mnt/c/own/alejandria/scripts/gpu-up.sh down
```

### Check status
```bash
wsl -d Ubuntu-20.04 -e bash //mnt/c/own/alejandria/scripts/gpu-up.sh status
```

### Test GPU passthrough
```bash
wsl -d Ubuntu-20.04 -e bash //mnt/c/own/alejandria/scripts/gpu-up.sh test
```

### View API logs
```bash
wsl -d Ubuntu-20.04 -e bash //mnt/c/own/alejandria/scripts/gpu-up.sh logs
```

## Important Notes

- **Port conflict:** Stop Rancher Desktop Alejandría containers before starting GPU stack, or vice versa.
- **Separate volumes:** GPU stack has its own Qdrant/Neo4j volumes — data is NOT shared with Rancher Desktop.
- **Rancher Desktop safety:** This skill NEVER touches Rancher Desktop. All commands target Ubuntu-20.04 WSL only.
- **Credential helper:** The script strips Rancher paths from PATH to avoid `docker-credential-secretservice` conflicts.

## Troubleshooting

If Docker Engine is not running:
```bash
wsl -d Ubuntu-20.04 -u root -e bash -c "systemctl start docker"
```

If GPU is not visible:
```bash
wsl -d Ubuntu-20.04 -e bash -c "nvidia-smi"
```
