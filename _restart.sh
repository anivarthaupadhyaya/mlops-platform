#!/bin/bash
set -euo pipefail
cd /mnt/c/capstone/mlops-platform
docker compose down -v --remove-orphans || true
docker compose up -d --build postgres redis api ingest writer telemetry dashboard
echo 'waiting for healthy core...'
for i in $(seq 1 40); do
  api=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' mlops-platform-api-1 2>/dev/null || echo missing)
  ingest=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' mlops-platform-ingest-1 2>/dev/null || echo missing)
  writer=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' mlops-platform-writer-1 2>/dev/null || echo missing)
  echo "t=$i api=$api ingest=$ingest writer=$writer"
  if [ "$api" = healthy ] && [ "$ingest" = healthy ] && [ "$writer" = healthy ]; then
    echo CORE_READY
    docker compose logs --tail=25 api
    docker compose exec -T api curl -sf http://127.0.0.1:8000/health; echo
    docker compose exec -T ingest curl -sf http://127.0.0.1:8001/health; echo
    docker compose exec -T postgres psql -U mlops -d mlops -c '\dt'
    exit 0
  fi
  sleep 5
done
echo FAILED
docker compose ps -a
docker compose logs --tail=50 api
exit 1