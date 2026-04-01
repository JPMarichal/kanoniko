---
name: deploy
description: Deploy current source code to the Alejandría Docker container and verify it's running. Uses native Docker Engine in Ubuntu WSL.
---

# Deploy to Container

Deploy the current source code to the running Alejandría container on the native Docker Engine (Ubuntu-20.04 WSL).

## Environment Setup

All docker commands must run through WSL with Rancher Desktop paths stripped:

```bash
WSL_DOCKER="wsl -d Ubuntu-20.04 -u root -e bash -c"
DOCKER_ENV='export PATH=$(echo "$PATH" | tr ":" "\n" | grep -v -i "rancher" | tr "\n" ":") && export DOCKER_CONFIG=/tmp/alejandria-docker-config && mkdir -p $DOCKER_CONFIG && echo "{}" > $DOCKER_CONFIG/config.json'
```

## Steps

1. Verify the GPU stack is running:
```bash
wsl -d Ubuntu-20.04 -u root -e bash -c 'export PATH=$(echo "$PATH" | tr ":" "\n" | grep -v -i "rancher" | tr "\n" ":") && export DOCKER_CONFIG=/tmp/alejandria-docker-config && /usr/bin/docker ps --filter name=alejandria --format "table {{.Names}}\t{{.Status}}"'
```
If not running, start it first with `/gpu up`.

2. Copy all modified Python files to the container:
```bash
wsl -d Ubuntu-20.04 -u root -e bash -c 'export PATH=$(echo "$PATH" | tr ":" "\n" | grep -v -i "rancher" | tr "\n" ":") && export DOCKER_CONFIG=/tmp/alejandria-docker-config && /usr/bin/docker cp /mnt/c/own/alejandria/src/alejandria/ alejandria-api:/app/src/alejandria/'
```

3. Restart the container:
```bash
wsl -d Ubuntu-20.04 -u root -e bash -c 'export PATH=$(echo "$PATH" | tr ":" "\n" | grep -v -i "rancher" | tr "\n" ":") && export DOCKER_CONFIG=/tmp/alejandria-docker-config && /usr/bin/docker restart alejandria-api'
```

4. Wait for startup and verify health:
```bash
sleep 10 && curl -s http://localhost:4300/health
```

5. Check logs for errors:
```bash
wsl -d Ubuntu-20.04 -u root -e bash -c 'export PATH=$(echo "$PATH" | tr ":" "\n" | grep -v -i "rancher" | tr "\n" ":") && export DOCKER_CONFIG=/tmp/alejandria-docker-config && /usr/bin/docker logs alejandria-api --tail 15'
```

Report the deployment status to the user, including whether `ALEJANDRIA_EMBEDDING_DEVICE=cuda` is active in the logs.
