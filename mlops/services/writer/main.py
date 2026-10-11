from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.exceptions import ResponseError
from sqlalchemy import insert

from mlops.services.writer.parse import parse_stream_entry
from mlops.shared.config import settings
from mlops.shared.db import SessionLocal
from mlops.shared.models import Metric
from mlops.shared.redis_client import close_redis, get_redis

CONSUMER = os.getenv("HOSTNAME", "writer-1")


async def ensure_group() -> None:
    redis = get_redis()
    try:
        await redis.xgroup_create(settings.metrics_stream, settings.writer_group, id="0", mkstream=True)
    except ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise


async def flush_entries(entries: list[tuple[str, dict[str, str]]]) -> list[str]:
    metrics = []
    ids: list[str] = []
    for entry_id, fields in entries:
        metric = parse_stream_entry(fields)
        if metric is None:
            ids.append(entry_id)
            continue
        metrics.append(
            {"run_id": metric.run_id, "name": metric.name, "value": metric.value, "step": metric.step}
        )
        ids.append(entry_id)
    if metrics:
        async with SessionLocal() as session:
            await session.execute(insert(Metric), metrics)
            await session.commit()
    return ids


async def consume_forever() -> None:
    redis = get_redis()
    await ensure_group()
    while True:
        try:
            try:
                claimed = await redis.xautoclaim(
                    settings.metrics_stream,
                    settings.writer_group,
                    CONSUMER,
                    min_idle_time=30_000,
                    start_id="0-0",
                    count=500,
                )
                pending_entries = claimed[1] if claimed else []
            except Exception:
                pending_entries = []
            streams = await redis.xreadgroup(
                settings.writer_group,
                CONSUMER,
                {settings.metrics_stream: ">"},
                count=500,
                block=2000,
            )
            entries: list[tuple[str, dict[str, str]]] = list(pending_entries)
            if streams:
                for _name, msgs in streams:
                    entries.extend(msgs)
            if not entries:
                continue
            ack_ids = await flush_entries(entries)
            if ack_ids:
                await redis.xack(settings.metrics_stream, settings.writer_group, *ack_ids)
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    task = None
    if os.getenv("SKIP_BG_TASKS") != "1":
        task = asyncio.create_task(consume_forever())
    yield
    if task is not None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    await close_redis()


app = FastAPI(title="MLOps Writer", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "writer", "consumer": CONSUMER}
