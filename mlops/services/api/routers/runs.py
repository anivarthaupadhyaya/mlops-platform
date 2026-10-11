from collections import defaultdict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mlops.shared.db import get_session
from mlops.shared.models import Experiment, Metric, Run, Snapshot
from mlops.shared.schemas import MetricSeriesPoint, RunCreate, RunOut

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunOut)
async def create_run(body: RunCreate, session: AsyncSession = Depends(get_session)) -> Run:
    if await session.get(Experiment, body.experiment_id) is None:
        raise HTTPException(status_code=404, detail="experiment not found")
    if await session.get(Snapshot, body.snapshot_id) is None:
        raise HTTPException(status_code=404, detail="snapshot not found")
    run = Run(experiment_id=body.experiment_id, snapshot_id=body.snapshot_id, params=body.params, status="running")
    session.add(run)
    await session.commit()
    await session.refresh(run)
    return run


@router.get("/{run_id}", response_model=RunOut)
async def get_run(run_id: UUID, session: AsyncSession = Depends(get_session)) -> Run:
    run = await session.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return run


@router.post("/{run_id}/finish", response_model=RunOut)
async def finish_run(run_id: UUID, session: AsyncSession = Depends(get_session)) -> Run:
    run = await session.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    run.status = "finished"
    await session.commit()
    await session.refresh(run)
    return run


@router.get("/{run_id}/metrics")
async def get_run_metrics(run_id: UUID, session: AsyncSession = Depends(get_session)) -> dict[str, list[MetricSeriesPoint]]:
    run = await session.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    result = await session.execute(select(Metric).where(Metric.run_id == run_id).order_by(Metric.step.asc()))
    series: dict[str, list[MetricSeriesPoint]] = defaultdict(list)
    for metric in result.scalars().all():
        series[metric.name].append(MetricSeriesPoint(step=metric.step, value=metric.value))
    return series
