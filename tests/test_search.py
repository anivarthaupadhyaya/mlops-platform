import asyncio

from fastapi.testclient import TestClient

from mlops.services.search.rewrite import rewrite_query


def test_search_health_without_model(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from mlops.services.search import main as search_main

    monkeypatch.setattr(search_main, "embed", lambda _text: [0.0] * 384)
    with TestClient(search_main.app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "search"


def test_rewrite_falls_back_without_key() -> None:
    assert asyncio.run(rewrite_query("loss curves")) == "loss curves"


def test_run_summary_includes_status_and_params() -> None:
    from types import SimpleNamespace

    from mlops.services.search.backfill import run_summary

    run = SimpleNamespace(status="finished", params={"lr": 0.01})
    summary = run_summary(run)  # type: ignore[arg-type]
    assert "finished" in summary
    assert "0.01" in summary
