#!/bin/sh
# Self-healing SSH tunnel to the IONOS Postgres, run as a dedicated sidecar.
#
# Reads connection settings from the environment (ALEJANDRIA_SSH_TUNNEL_*,
# injected via env_file: ../.env) and keeps the tunnel up with autossh.
set -eu

# The private key is bind-mounted read-only from ../docker/ssh. Windows bind
# mounts break Unix permissions (SSH refuses a world-readable key), so copy it
# to /tmp and lock it down to 0600.
if [ -f /keys/tunnel_key ]; then
  cp /keys/tunnel_key /tmp/tunnel_key
  chmod 600 /tmp/tunnel_key
else
  echo "FATAL: /keys/tunnel_key not found. Mount ../docker/ssh:/keys:ro" >&2
  exit 1
fi

: "${ALEJANDRIA_SSH_TUNNEL_HOST:?ALEJANDRIA_SSH_TUNNEL_HOST is required}"
: "${ALEJANDRIA_SSH_TUNNEL_USER:?ALEJANDRIA_SSH_TUNNEL_USER is required}"
SSH_PORT="${ALEJANDRIA_SSH_TUNNEL_PORT:-22}"
REMOTE_PORT="${ALEJANDRIA_SSH_TUNNEL_REMOTE_PORT:-5432}"
LISTEN_PORT="${TUNNEL_LISTEN_PORT:-5432}"

echo "autossh: 0.0.0.0:${LISTEN_PORT} -> ${ALEJANDRIA_SSH_TUNNEL_USER}@${ALEJANDRIA_SSH_TUNNEL_HOST}:${SSH_PORT} -> 127.0.0.1:${REMOTE_PORT}"

# AUTOSSH_GATETIME=0: restart the tunnel even if the very first connection
# fails quickly (e.g. VPS momentarily unreachable at boot).
export AUTOSSH_GATETIME=0

# -M 0 disables autossh's legacy monitoring port; we rely on SSH keepalives
# (ServerAliveInterval/CountMax) + ExitOnForwardFailure so a dead session is
# detected and autossh respawns ssh automatically.
exec autossh -M 0 -N \
  -o "ServerAliveInterval=30" \
  -o "ServerAliveCountMax=3" \
  -o "ExitOnForwardFailure=yes" \
  -o "StrictHostKeyChecking=accept-new" \
  -o "UserKnownHostsFile=/tmp/known_hosts" \
  -o "TCPKeepAlive=yes" \
  -i /tmp/tunnel_key \
  -p "${SSH_PORT}" \
  -L "0.0.0.0:${LISTEN_PORT}:127.0.0.1:${REMOTE_PORT}" \
  "${ALEJANDRIA_SSH_TUNNEL_USER}@${ALEJANDRIA_SSH_TUNNEL_HOST}"
