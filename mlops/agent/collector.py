from __future__ import annotations

import asyncio
import json
import socket
import time

import psutil

from mlops.shared.config import settings
from mlops.shared.redis_client import close_redis, get_redis


def read_gpu() -> tuple[float | None, float | None]:
    try:
        import pynvml

        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
        gpu_mem = (mem.used / mem.total) * 100.0 if mem.total else 0.0
        return float(util.gpu), float(gpu_mem)
    except Exception:
        return None, None


async def publish_loop() -> None:
    redis = get_redis()
    node_id = settings.node_id or socket.gethostname()
    channel = f"telemetry:{node_id}"
    while True:
        gpu, gpu_mem = read_gpu()
        payload = {
            "node_id": node_id,
            "ts": time.time(),
            "cpu": psutil.cpu_percent(interval=None),
            "ram": psutil.virtual_memory().percent,
            "gpu": gpu,
            "gpu_mem": gpu_mem,
        }
        await redis.publish(channel, json.dumps(payload))
        await asyncio.sleep(1)


def main() -> None:
    psutil.cpu_percent(interval=None)
    try:
        asyncio.run(publish_loop())
    except KeyboardInterrupt:
        asyncio.run(close_redis())
