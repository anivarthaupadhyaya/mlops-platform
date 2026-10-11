from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from mlops.shared.db import get_session
from mlops.shared.models import Snapshot
from mlops.shared.schemas import SnapshotCreate, SnapshotOut
from mlops.shared.snapshots import snapshot_id

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.post("", response_model=SnapshotOut)
async def create_snapshot(body: SnapshotCreate, session: AsyncSession = Depends(get_session)) -> Snapshot:
    sid = snapshot_id(body.python_version, body.packages, body.image_digest, body.config)
    stmt = (
        insert(Snapshot)
        .values(
            id=sid,
            python_version=body.python_version,
            packages=body.packages,
            image_digest=body.image_digest,
            config=body.config,
        )
        .on_conflict_do_nothing(index_elements=["id"])
        .returning(Snapshot)
    )
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    await session.commit()
    if row is None:
        existing = await session.get(Snapshot, sid)
        if existing is None:
            raise HTTPException(status_code=500, detail="snapshot insert failed")
        return existing
    return row


@router.get("/{snapshot_id}", response_model=SnapshotOut)
async def get_snapshot(snapshot_id: str, session: AsyncSession = Depends(get_session)) -> Snapshot:
    snapshot = await session.get(Snapshot, snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="snapshot not found")
    return snapshot
