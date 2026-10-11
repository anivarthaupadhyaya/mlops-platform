#!/bin/bash
cd /mnt/c/capstone/mlops-platform
docker compose ps
echo '--- logs api ---'
docker compose logs --tail=40 api
echo '--- curl from host ---'
ss -lntp | head -40
curl -v --max-time 5 http://127.0.0.1:8000/health || true
echo '--- curl from container ---'
docker compose exec -T api curl -sf http://localhost:8000/health || true
echo
docker compose exec -T ingest curl -sf http://localhost:8001/health || true
echo