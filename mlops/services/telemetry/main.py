from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from mlops.shared.redis_client import close_redis, get_redis

clients: set[WebSocket] = set()


async def fanout(payload: str) -> None:
    dead: list[WebSocket] = []
    for ws in list(clients):
        try:
            await ws.send_text(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.discard(ws)


async def redis_listener() -> None:
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.psubscribe("telemetry:*")
    try:
        async for message in pubsub.listen():
            if message.get("type") not in {"pmessage", "message"}:
                continue
            data = message.get("data")
            if data is None:
                continue
            await fanout(data if isinstance(data, str) else str(data))
    finally:
        await pubsub.aclose()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    task = None
    if os.getenv("SKIP_BG_TASKS") != "1":
        task = asyncio.create_task(redis_listener())
    yield
    if task is not None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    await close_redis()


app = FastAPI(title="MLOps Telemetry", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str | int]:
    return {"status": "ok", "service": "telemetry", "clients": len(clients)}


@app.websocket("/ws/telemetry")
async def telemetry_ws(ws: WebSocket) -> None:
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(ws)
