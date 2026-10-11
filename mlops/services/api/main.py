import asyncio
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mlops.services.api.migrate import run_migrations
from mlops.services.api.routers import experiments, runs, snapshots


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    if os.getenv("SKIP_BG_TASKS") != "1":
        await asyncio.to_thread(run_migrations)
    yield


app = FastAPI(title="MLOps API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(experiments.router)
app.include_router(runs.router)
app.include_router(snapshots.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "api"}
