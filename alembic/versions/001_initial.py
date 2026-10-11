"""initial schema with pgvector and immutable snapshots

Revision ID: 001_initial
Revises:
Create Date: 2026-10-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "experiments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "snapshots",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("python_version", sa.String(32), nullable=False),
        sa.Column("packages", postgresql.JSONB(), nullable=False),
        sa.Column("image_digest", sa.String(255), nullable=True),
        sa.Column("config", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("experiment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("experiments.id"), nullable=False),
        sa.Column("snapshot_id", sa.String(64), sa.ForeignKey("snapshots.id"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="running"),
        sa.Column("params", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_runs_experiment_id", "runs", ["experiment_id"])
    op.create_table(
        "metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("step", sa.Integer(), nullable=False),
    )
    op.create_index("ix_metrics_run_id", "metrics", ["run_id"])
    op.create_table(
        "run_embeddings",
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("runs.id"), primary_key=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=False),
    )
    op.execute(
        "CREATE INDEX run_embeddings_hnsw ON run_embeddings USING hnsw (embedding vector_cosine_ops)"
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION deny_snapshot_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
          RAISE EXCEPTION 'snapshots are immutable';
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER snapshots_no_update
        BEFORE UPDATE ON snapshots
        FOR EACH ROW EXECUTE FUNCTION deny_snapshot_mutation();
        """
    )
    op.execute(
        """
        CREATE TRIGGER snapshots_no_delete
        BEFORE DELETE ON snapshots
        FOR EACH ROW EXECUTE FUNCTION deny_snapshot_mutation();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS snapshots_no_delete ON snapshots")
    op.execute("DROP TRIGGER IF EXISTS snapshots_no_update ON snapshots")
    op.execute("DROP FUNCTION IF EXISTS deny_snapshot_mutation()")
    op.drop_table("run_embeddings")
    op.drop_index("ix_metrics_run_id", table_name="metrics")
    op.drop_table("metrics")
    op.drop_index("ix_runs_experiment_id", table_name="runs")
    op.drop_table("runs")
    op.drop_table("snapshots")
    op.drop_table("experiments")
