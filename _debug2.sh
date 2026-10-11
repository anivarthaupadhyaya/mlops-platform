#!/bin/bash
cd /mnt/c/capstone/mlops-platform
docker compose ps -a
echo '=== api ==='
docker compose logs --tail=80 api
echo '=== writer ==='
docker compose logs --tail=40 writer
echo '=== ingest ==='
docker compose logs --tail=20 ingest
echo '=== all containers ==='
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'