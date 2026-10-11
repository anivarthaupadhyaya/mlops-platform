#!/bin/bash
cd /mnt/c/capstone/mlops-platform
echo '=== ps -a ==='
docker compose ps -a
echo '=== dmesg oom ==='
dmesg -T 2>/dev/null | tail -30
echo '=== free ==='
free -h
echo '=== docker info mem ==='
docker info 2>/dev/null | grep -i -E 'Memory|CPUs|Operating'
echo '=== events last ==='
docker events --since 15m --until 0s --filter type=container 2>/dev/null | tail -40
echo '=== search logs ==='
docker compose logs --tail=40 search || true
echo '=== api logs ==='
docker compose logs --tail=20 api || true