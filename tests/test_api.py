from fastapi.testclient import TestClient

from mlops.services.api.main import app
from mlops.shared.snapshots import snapshot_id


def test_api_health() -> None:
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "api"


def test_snapshot_hash_is_stable() -> None:
    first = snapshot_id("3.11.0", {"fastapi": "0.115.0"}, "sha256:abc", {"lr": 0.01})
    second = snapshot_id("3.11.0", {"fastapi": "0.115.0"}, "sha256:abc", {"lr": 0.01})
    assert first == second
    assert len(first) == 64
