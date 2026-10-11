from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mlops.shared.db import get_session
from mlops.shared.models import Experiment, Run
from mlops.shared.schemas import ExperimentCreate, ExperimentOut, RunOut

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("", response_model=ExperimentOut)
async def create_experiment(body: ExperimentCreate, session: AsyncSession = Depends(get_session)) -> Experiment:
    experiment = Experiment(name=body.name, description=body.description)
    session.add(experiment)
    await session.commit()
    await session.refresh(experiment)
    return experiment


@router.get("", response_model=list[ExperimentOut])
async def list_experiments(session: AsyncSession = Depends(get_session)) -> list[Experiment]:
    result = await session.execute(select(Experiment).order_by(Experiment.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{experiment_id}", response_model=ExperimentOut)
async def get_experiment(experiment_id: UUID, session: AsyncSession = Depends(get_session)) -> Experiment:
    experiment = await session.get(Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="experiment not found")
    return experiment


@router.get("/{experiment_id}/runs", response_model=list[RunOut])
async def list_experiment_runs(experiment_id: UUID, session: AsyncSession = Depends(get_session)) -> list[Run]:
    experiment = await session.get(Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="experiment not found")
    result = await session.execute(select(Run).where(Run.experiment_id == experiment.id).order_by(Run.started_at.desc()))
    return list(result.scalars().all())
