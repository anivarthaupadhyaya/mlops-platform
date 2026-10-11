from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    runs: Mapped[list[Run]] = relationship(back_populates="experiment")


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    python_version: Mapped[str] = mapped_column(String(32), nullable=False)
    packages: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    image_digest: Mapped[str | None] = mapped_column(String(255), nullable=True)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    runs: Mapped[list[Run]] = relationship(back_populates="snapshot")


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("experiments.id"), nullable=False, index=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshots.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="running")
    params: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    experiment: Mapped[Experiment] = relationship(back_populates="runs")
    snapshot: Mapped[Snapshot] = relationship(back_populates="runs")
    embedding: Mapped[RunEmbedding | None] = relationship(back_populates="run")


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    step: Mapped[int] = mapped_column(Integer, nullable=False)


class RunEmbedding(Base):
    __tablename__ = "run_embeddings"

    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id"), primary_key=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)

    run: Mapped[Run] = relationship(back_populates="embedding")
