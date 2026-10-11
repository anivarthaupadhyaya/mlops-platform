from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from mlops.services.search.backfill import backfill_run_embeddings
from mlops.services.search.embedder import embed
from mlops.services.search.rewrite import rewrite_query
from mlops.shared.db import SessionLocal
from mlops.shared.models import Run, RunEmbedding
from mlops.shared.schemas import IndexRequest, SearchHit


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    if os.getenv("SKIP_BG_TASKS") != "1":
        await asyncio.to_thread(embed, "warmup")
        await backfill_run_embeddings()
    yield


app = FastAPI(title="MLOps Search", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "search"}


@app.post("/index/{run_id}")
async def index_run(run_id: UUID, body: IndexRequest) -> dict[str, str]:
    async with SessionLocal() as session:
        if await session.get(Run, run_id) is None:
            raise HTTPException(status_code=404, detail="run not found")
        vector = embed(body.summary)
        stmt = insert(RunEmbedding).values(run_id=run_id, summary=body.summary, embedding=vector)
        stmt = stmt.on_conflict_do_update(
            index_elements=[RunEmbedding.run_id],
            set_={"summary": body.summary, "embedding": vector},
        )
        await session.execute(stmt)
        await session.commit()
    return {"status": "indexed", "run_id": str(run_id)}


@app.get("/search", response_model=list[SearchHit])
async def search_runs(q: str = Query(min_length=1), k: int = Query(default=5, ge=1, le=50)) -> list[SearchHit]:
    rewritten = await rewrite_query(q)
    vector = embed(rewritten)
    async with SessionLocal() as session:
        distance = RunEmbedding.embedding.cosine_distance(vector)
        result = await session.execute(
            select(RunEmbedding.run_id, RunEmbedding.summary, distance.label("distance")).order_by(distance).limit(k)
        )
        rows = result.all()
    return [
        SearchHit(run_id=row.run_id, summary=row.summary, score=1.0 - float(row.distance))
        for row in rows
    ]
