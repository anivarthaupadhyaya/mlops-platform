from __future__ import annotations

import asyncio
import json

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from mlops.services.search.embedder import embed
from mlops.shared.db import SessionLocal
from mlops.shared.models import Run, RunEmbedding


def run_summary(run: Run) -> str:
    return json.dumps({"status": run.status, "params": run.params}, sort_keys=True, default=str)


async def backfill_run_embeddings() -> int:
    async with SessionLocal() as session:
        existing = set((await session.execute(select(RunEmbedding.run_id))).scalars().all())
        runs = list((await session.execute(select(Run))).scalars().all())
    indexed = 0
    for run in runs:
        if run.id in existing:
            continue
        summary = run_summary(run)
        vector = await asyncio.to_thread(embed, summary)
        async with SessionLocal() as session:
            stmt = (
                insert(RunEmbedding)
                .values(run_id=run.id, summary=summary, embedding=vector)
                .on_conflict_do_nothing(index_elements=[RunEmbedding.run_id])
            )
            await session.execute(stmt)
            await session.commit()
        indexed += 1
    return indexed
