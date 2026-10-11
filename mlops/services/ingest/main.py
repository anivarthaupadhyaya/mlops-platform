import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mlops.shared.config import settings
from mlops.shared.redis_client import close_redis, get_redis
from mlops.shared.schemas import MetricPoint


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    if os.getenv("SKIP_BG_TASKS") != "1":
        get_redis()
    yield
    await close_redis()


app = FastAPI(title="MLOps Ingest", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ingest"}


@app.post("/ingest", status_code=202)
async def ingest_metrics(batch: list[MetricPoint]) -> dict[str, int]:
    redis = get_redis()
    async with redis.pipeline(transaction=False) as pipe:
        for point in batch:
            pipe.xadd(
                settings.metrics_stream,
                {
                    "run_id": str(point.run_id),
                    "name": point.name,
                    "value": str(point.value),
                    "step": str(point.step),
                },
                maxlen=settings.stream_maxlen,
                approximate=True,
            )
        await pipe.execute()
    return {"accepted": len(batch)}
