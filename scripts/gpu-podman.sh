#!/bin/bash
# gpu-podman.sh — Start Alejandría with GPU acceleration on Podman
# Usage: bash scripts/gpu-podman.sh [up|down|status|test|logs|ollama]
set -euo pipefail

DOCKER="docker --context podman-machine-default"
COMPOSE="$DOCKER compose"
PROJECT_DIR=/mnt/c/own/alejandria/docker
COMPOSE_FILES="-f $PROJECT_DIR/docker-compose.yml -f $PROJECT_DIR/docker-compose.podman.yml"
TUNNEL_PORT=15432
TUNNEL_SSH_TARGET=root@212.227.243.210
TUNNEL_PATTERN="ssh.*${TUNNEL_PORT}:localhost:5432"

check_podman() {
    if ! $DOCKER info >/dev/null 2>&1; then
        echo "ERROR: Podman not reachable. Is Podman Desktop running?"
        exit 1
    fi
    echo "Podman: OK ($($DOCKER info --format '{{.ServerVersion}}'))"
}

check_gpu() {
    if ! nvidia-smi >/dev/null 2>&1; then
        echo "WARNING: nvidia-smi not available — GPU check skipped"
        return
    fi
    echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | head -1) MiB"
}

PODMAN_SSH="MSYS_NO_PATHCONV=1 podman machine ssh podman-machine-default"

tunnel_bound_to_all_interfaces() {
    $PODMAN_SSH "ss -tln 2>/dev/null" 2>/dev/null | grep -Eq "0\.0\.0\.0:${TUNNEL_PORT}|\[::\]:${TUNNEL_PORT}"
}

ensure_postgres_tunnel() {
    if tunnel_bound_to_all_interfaces; then
        echo "Postgres tunnel: OK on 0.0.0.0:${TUNNEL_PORT}"
        return
    fi
    echo "Postgres tunnel: down — attempting to start from Podman machine..."
    $PODMAN_SSH "ssh -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes \
        -i ~/.ssh/id_ed25519 \
        -L '*:${TUNNEL_PORT}:localhost:5432' -N -f $TUNNEL_SSH_TARGET" 2>&1 || true
    sleep 2
    if tunnel_bound_to_all_interfaces; then
        echo "Postgres tunnel: OK on 0.0.0.0:${TUNNEL_PORT}"
    else
        echo "WARNING: Postgres tunnel could not be established."
        echo "API will start but health checks will fail until tunnel is up."
    fi
}

show_postgres_tunnel_status() {
    if tunnel_bound_to_all_interfaces; then
        echo "Postgres tunnel: OK on 0.0.0.0:${TUNNEL_PORT}"
    else
        echo "Postgres tunnel: down"
    fi
}

sync_repo() {
    echo "NOTE: repo sync not needed — containers access files via bind mount"
}

cmd=${1:-up}

case "$cmd" in
    up)
        check_podman
        check_gpu
        ensure_postgres_tunnel
        sync_repo
        echo "Starting Alejandría with GPU (Podman)..."
        cd "$PROJECT_DIR"
        $COMPOSE $COMPOSE_FILES up -d --no-build
        echo ""
        echo "Waiting for containers..."
        sleep 5
        $COMPOSE $COMPOSE_FILES ps
        echo ""
        echo "API: http://localhost:4300/health"
        echo "Ollama: http://localhost:11434"
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
        check_podman
        cd "$PROJECT_DIR"
        $COMPOSE $COMPOSE_FILES down
        echo "Alejandría Podman stack stopped."
        ;;
    status)
        check_podman
        check_gpu
        show_postgres_tunnel_status
        cd "$PROJECT_DIR"
        $COMPOSE $COMPOSE_FILES ps
        echo ""
        if curl -s http://localhost:4300/health >/dev/null 2>&1; then
            echo "API health: $(curl -s http://localhost:4300/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:4300/health)"
        else
            echo "API: not responding"
        fi
        ;;
    test)
        check_podman
        check_gpu
        echo "Testing GPU from Podman container..."
        $DOCKER run --rm --device nvidia.com/gpu=all nvidia/cuda:12.6.3-base-ubuntu22.04 nvidia-smi
        echo ""
        echo "GPU Podman test: PASSED"
        ;;
    logs)
        check_podman
        cd "$PROJECT_DIR"
        $COMPOSE $COMPOSE_FILES logs -f --tail=50 api
        ;;
    ollama)
        shift
        ollama_cmd=${1:-list}
        $DOCKER exec alejandria-ollama ollama "$ollama_cmd" "${@:2}"
        ;;
    *)
        echo "Usage: bash $0 {up|down|status|test|logs|ollama}"
        exit 1
        ;;
esac
