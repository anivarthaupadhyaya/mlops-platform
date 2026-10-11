from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ExperimentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ExperimentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime


class SnapshotCreate(BaseModel):
    python_version: str
    packages: dict[str, str]
    image_digest: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class SnapshotOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    python_version: str
    packages: dict[str, Any]
    image_digest: str | None
    config: dict[str, Any]
    created_at: datetime


class RunCreate(BaseModel):
    experiment_id: uuid.UUID
    snapshot_id: str
    params: dict[str, Any] = Field(default_factory=dict)


class RunOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    experiment_id: uuid.UUID
    snapshot_id: str
    status: str
    params: dict[str, Any]
    started_at: datetime


class MetricPoint(BaseModel):
    run_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    value: float
    step: int = Field(ge=0)


class MetricSeriesPoint(BaseModel):
    step: int
    value: float


class IndexRequest(BaseModel):
    summary: str = Field(min_length=1)


class SearchHit(BaseModel):
    run_id: uuid.UUID
    summary: str
    score: float
