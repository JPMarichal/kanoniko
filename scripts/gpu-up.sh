#!/bin/bash
# gpu-up.sh — Start Alejandría with GPU acceleration in Ubuntu WSL
# Usage from Windows:  wsl -d Ubuntu-20.04 -- bash /mnt/c/own/alejandria/scripts/gpu-up.sh [up|down|status|test]
# Usage from WSL:      bash /mnt/c/own/alejandria/scripts/gpu-up.sh [up|down|status|test]
set -euo pipefail

DOCKER=/usr/bin/docker
COMPOSE="$DOCKER compose"
PROJECT_DIR=/mnt/c/own/alejandria/docker
COMPOSE_FILES="-f $PROJECT_DIR/docker-compose.yml -f $PROJECT_DIR/docker-compose.gpu.yml"
TUNNEL_PORT=15432
TUNNEL_SSH_TARGET=root@212.227.243.210
TUNNEL_PATTERN="ssh.*${TUNNEL_PORT}:localhost:5432"

# Ensure we use native Docker, not Rancher Desktop
export DOCKER_HOST=unix:///var/run/docker.sock
export DOCKER_CONFIG=/tmp/alejandria-docker-config
mkdir -p "$DOCKER_CONFIG"
echo '{}' > "$DOCKER_CONFIG/config.json"
rm -rf "$DOCKER_CONFIG/buildx" 2>/dev/null || true

# Strip Rancher Desktop paths from PATH to prevent its credential helpers
# from interfering with BuildKit (docker-credential-secretservice via /mnt/c/...)
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v -i 'rancher' | tr '\n' ':')

check_docker() {
    if ! $DOCKER info >/dev/null 2>&1; then
        echo "Docker Engine not running. Starting..."
        sudo systemctl start docker
        sleep 2
        if ! $DOCKER info >/dev/null 2>&1; then
            echo "ERROR: Could not start Docker Engine in Ubuntu WSL"
            exit 1
        fi
    fi
    echo "Docker Engine: OK"
}

check_gpu() {
    if ! nvidia-smi >/dev/null 2>&1; then
        echo "ERROR: nvidia-smi not available — GPU not visible in WSL"
        exit 1
    fi
    echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | head -1) MiB"
}

tunnel_bound_to_all_interfaces() {
    ss -tln 2>/dev/null | grep -Eq "0\.0\.0\.0:${TUNNEL_PORT}|\[::\]:${TUNNEL_PORT}"
}

tunnel_bound_to_loopback_only() {
    ss -tln 2>/dev/null | grep -Eq "127\.0\.0\.1:${TUNNEL_PORT}|\[::1\]:${TUNNEL_PORT}"
}

ensure_postgres_tunnel() {
    if tunnel_bound_to_all_interfaces; then
        echo "Postgres tunnel: OK on 0.0.0.0:${TUNNEL_PORT}"
        return
    fi

    if tunnel_bound_to_loopback_only; then
        echo "Postgres tunnel is bound to loopback only; restarting on all interfaces..."
        pkill -f "$TUNNEL_PATTERN" 2>/dev/null || true
        sleep 1
    else
        echo "Starting Postgres SSH tunnel on :${TUNNEL_PORT}..."
    fi

    ssh -o ExitOnForwardFailure=yes -L "*:${TUNNEL_PORT}:localhost:5432" -N -f "$TUNNEL_SSH_TARGET"

    if ! tunnel_bound_to_all_interfaces; then
        echo "ERROR: Postgres tunnel did not come up on 0.0.0.0:${TUNNEL_PORT}"
        exit 1
    fi

    echo "Postgres tunnel: OK on 0.0.0.0:${TUNNEL_PORT}"
}

show_postgres_tunnel_status() {
    if tunnel_bound_to_all_interfaces; then
        echo "Postgres tunnel: OK on 0.0.0.0:${TUNNEL_PORT}"
    elif tunnel_bound_to_loopback_only; then
        echo "Postgres tunnel: loopback-only on 127.0.0.1:${TUNNEL_PORT} (Docker bridge cannot use it)"
    else
        echo "Postgres tunnel: down"
    fi
}

REPO_DIR=/home/jpmarichal/alejandria-repo

sync_repo() {
    echo "Syncing repo on Linux FS..."
    if [ -d "$REPO_DIR/.git" ]; then
        cd "$REPO_DIR"
        git fetch /mnt/c/own/alejandria --quiet 2>/dev/null
        git reset --hard FETCH_HEAD --quiet
        echo "Repo synced: $(git log --oneline -1)"
    else
        echo "ERROR: Repo not found at $REPO_DIR — run: git clone /mnt/c/own/alejandria $REPO_DIR"
        exit 1
    fi
}

cmd=${1:-up}

case "$cmd" in
    up)
        check_docker
        check_gpu
        ensure_postgres_tunnel
        sync_repo
        echo "Starting Alejandría with GPU..."
        cd "$PROJECT_DIR"
        $COMPOSE $COMPOSE_FILES up --build -d
        echo ""
        echo "Waiting for health check..."
        sleep 5
        $COMPOSE $COMPOSE_FILES ps
        echo ""
        echo "API: http://localhost:4300/health"
        # Pull default Ollama model if not already present
        if $DOCKER ps --format '{{.Names}}' | grep -q alejandria-ollama; then
            echo ""
            echo "Checking Ollama model..."
            if ! $DOCKER exec alejandria-ollama ollama list 2>/dev/null | grep -q "qwen2.5:7b"; then
                echo "Pulling qwen2.5:7b-instruct-q4_K_M (first time only, ~4.4 GB)..."
                $DOCKER exec alejandria-ollama ollama pull qwen2.5:7b-instruct-q4_K_M
            else
                echo "Ollama model: qwen2.5:7b ready"
            fi
        fi
        ;;
    down)
        check_docker
        cd "$PROJECT_DIR"
        $COMPOSE $COMPOSE_FILES down
        echo "Alejandría GPU stack stopped."
        ;;
    status)
        check_docker
        check_gpu
        show_postgres_tunnel_status
        cd "$PROJECT_DIR"
        $COMPOSE $COMPOSE_FILES ps
        echo ""
        # Check if API is responding and which device it uses
        if curl -s http://localhost:4300/health >/dev/null 2>&1; then
            echo "API health: $(curl -s http://localhost:4300/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:4300/health)"
        else
            echo "API: not responding"
        fi
        ;;
    test)
        check_docker
        check_gpu
        echo "Testing GPU from Docker container..."
        $DOCKER run --rm --gpus all nvidia/cuda:12.6.3-base-ubuntu22.04 nvidia-smi
        echo ""
        echo "GPU Docker test: PASSED"
        ;;
    logs)
        check_docker
        cd "$PROJECT_DIR"
        $COMPOSE $COMPOSE_FILES logs -f --tail=50 api
        ;;
    ollama)
        check_docker
        shift
        ollama_cmd=${1:-list}
        $DOCKER exec alejandria-ollama ollama "$ollama_cmd" "${@:2}"
        ;;
    *)
        echo "Usage: $0 {up|down|status|test|logs|ollama}"
        exit 1
        ;;
esac
