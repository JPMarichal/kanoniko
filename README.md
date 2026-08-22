# Alejandría

> **Regla de entorno:** este proyecto vive en `C:\own\alejandria` y opera exclusivamente sobre **Podman**. No uses `docker` ni `docker compose` desde esta carpeta, porque en este host `docker` apunta a Rancher Desktop/Moby y tocaría contenedores de `C:\git`.

## Documentación

- `CLAUDE.md` — Reglas de proyecto, stack, running, backups y memoria.
- `docs/README.md` — Índice de documentación técnica.
- `docker/docker-compose.yml` — Stack base.
- `docker/docker-compose.podman.yml` — Override para Podman Desktop / GPU.
- `Justfile` — Recetas de tareas del proyecto.

## Contenedores esperados

| Contenedor | Rol |
|------------|-----|
| `alejandria-api` | API REST + MCP |
| `alejandria-tunnel` | Túnel SSH autocurativo a Postgres IONOS |
| `alejandria-ollama` | Ollama local para modelos |

## Comandos rápidos

```bash
# Levantar stack base
cd docker && podman compose -f docker-compose.yml up -d --build

# Levantar stack con GPU (Podman Desktop)
cd docker && podman compose -f docker-compose.yml -f docker-compose.podman.yml up -d --no-build

# Bajar stack
cd docker && podman compose down

# Ver logs
cd docker && podman compose logs -f
```

## Nota

Si necesitás acceder a los contenedores de Rancher Desktop (`C:\git`), usá `docker ps` desde una terminal ubicada fuera de `C:\own\alejandria` y sus subdirectorios. Dentro del proyecto, solo `podman`.
