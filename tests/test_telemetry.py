from fastapi.testclient import TestClient

from mlops.services.telemetry.main import app


def test_telemetry_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "telemetry"
