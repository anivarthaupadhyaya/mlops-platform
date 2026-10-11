#!/bin/bash
set -euo pipefail
cat > ~/.docker/config.json <<'EOF'
{
  "auths": {}
}
EOF
cd /mnt/c/capstone/mlops-platform
cp -n .env.example .env || true
docker compose up --build -d