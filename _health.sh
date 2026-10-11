#!/bin/bash
set -e
for p in 8000 8001 8002 8004; do
  echo -n "$p: "
  curl -sf "http://127.0.0.1:$p/health"
  echo
done
echo "create experiment:"
curl -sf -X POST http://127.0.0.1:8000/experiments -H 'Content-Type: application/json' -d '{"name":"demo","description":"smoke"}'
echo
echo "dashboard:"
curl -sI http://127.0.0.1:80 | head -5