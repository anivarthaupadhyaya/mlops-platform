from __future__ import annotations

import os
import uuid

import httpx
from locust import HttpUser, between, events, task

API_URL = os.getenv("API_URL", "http://localhost:8000")
RUN_ID = os.getenv("LOADTEST_RUN_ID")


@events.test_start.add_listener
def _ensure_run(_environment, **_kwargs) -> None:  # type: ignore[no-untyped-def]
    global RUN_ID
    if RUN_ID:
        return
    with httpx.Client(timeout=30.0) as client:
        experiment = client.post(f"{API_URL}/experiments", json={"name": "locust", "description": "load test"}).json()
        snapshot = client.post(
            f"{API_URL}/snapshots",
            json={
                "python_version": "3.11.0",
                "packages": {"locust": "2.32.6"},
                "image_digest": None,
                "config": {"source": "locust"},
            },
        ).json()
        run = client.post(
            f"{API_URL}/runs",
            json={"experiment_id": experiment["id"], "snapshot_id": snapshot["id"], "params": {"batch": 50}},
        ).json()
        RUN_ID = run["id"]


class IngestUser(HttpUser):
    wait_time = between(0.05, 0.2)

    @task
    def ingest_batch(self) -> None:
        batch = [
            {"run_id": RUN_ID or str(uuid.uuid4()), "name": "loss", "value": 1.0 / (i + 1), "step": i}
            for i in range(50)
        ]
        self.client.post("/ingest", json=batch, name="/ingest")
