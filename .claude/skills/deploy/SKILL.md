---
name: deploy
description: Deploy current source code to the Alejandría Docker container and verify it's running.
---

# Deploy to Container

Deploy the current source code to the running Alejandría Docker container.

## Steps

1. Copy all modified Python files from `src/alejandria/` to the container:
```bash
MSYS_NO_PATHCONV=1 docker cp src/alejandria/ alejandria-api:/app/src/alejandria/
```

2. Restart the container:
```bash
docker restart alejandria-api
```

3. Wait for startup and verify health:
```bash
sleep 8 && curl -s http://localhost:4300/health
```

4. Check logs for errors:
```bash
docker logs alejandria-api --tail 10
```

Report the deployment status to the user.
