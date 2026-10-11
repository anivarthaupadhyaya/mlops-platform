from fastapi.testclient import TestClient

from mlops.services.ingest.main import app


def test_ingest_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "ingest"
