#!/bin/bash
set -euo pipefail
cd /mnt/c/capstone/mlops-platform
docker compose stop search || true
docker compose rm -f search || true
docker compose up -d postgres redis api ingest writer telemetry dashboard
echo waiting for api startup...
for i in $(seq 1 30); do
  if docker compose logs api 2>/dev/null | grep -q "Application startup complete"; then
    echo API_UP
    break
  fi
  sleep 2
done
docker compose logs --tail=15 api
docker compose exec -T api curl -sf http://127.0.0.1:8000/health
echo
docker compose exec -T ingest curl -sf http://127.0.0.1:8001/health
echo
docker compose exec -T writer curl -sf http://127.0.0.1:8004/health
echo
docker compose exec -T telemetry curl -sf http://127.0.0.1:8002/health
echo
docker compose ps