#!/bin/bash
set -euo pipefail
cd /mnt/c/capstone/mlops-platform
echo '=== services ==='
docker compose ps
echo '=== experiment ==='
EXP=$(docker compose exec -T api python -c "import urllib.request; r=urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/experiments',data=b'{\"name\":\"demo\",\"description\":\"smoke\"}',headers={'Content-Type':'application/json'},method='POST'),timeout=10); print(r.read().decode())")
echo "$EXP"
echo '=== snapshot ==='
SNAP=$(docker compose exec -T api python -c "import urllib.request; r=urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/snapshots',data=b'{\"python_version\":\"3.11.9\",\"packages\":{\"fastapi\":\"0.115.6\"},\"image_digest\":null,\"config\":{\"lr\":0.001}}',headers={'Content-Type':'application/json'},method='POST'),timeout=10); print(r.read().decode())")
echo "$SNAP"
echo '=== dashboard ==='
docker compose exec -T dashboard wget -qO- http://127.0.0.1/ | head -c 200; echo
echo '=== search health ==='
docker compose exec -T search curl -sf http://127.0.0.1:8003/health; echo
echo '=== telemetry health ==='
docker compose exec -T telemetry curl -sf http://127.0.0.1:8002/health; echo