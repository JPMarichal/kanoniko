#!/usr/bin/env bash
# Run the Postgres migration benchmark inside a transient Python 3.12 container
# that can reach the alejandria-pg-bench service on the compose network.
set -euo pipefail

cd "$(dirname "$0")"

NETWORK="postgres-migration_default"
IMAGE="python:3.12-slim"

docker run --rm \
  --network "${NETWORK}" \
  -v "$(pwd)":/app \
  -v "$(pwd)":/out \
  -e PG_HOST=postgres \
  -e PG_PORT=5432 \
  -e PG_USER=bench \
  -e PG_PASSWORD=bench \
  -e PG_DB=alejandria_bench \
  -e N_CHUNKS="${N_CHUNKS:-30000}" \
  -e N_ENTITIES="${N_ENTITIES:-5000}" \
  -e N_RELATIONS="${N_RELATIONS:-500000}" \
  -e EMBED_DIM="${EMBED_DIM:-384}" \
  -e Q_ITERATIONS="${Q_ITERATIONS:-100}" \
  -e REPORT_PATH=/out/report.json \
  "${IMAGE}" \
  bash -c "pip install -q 'psycopg[binary]>=3.1' numpy && python /app/benchmark.py"
