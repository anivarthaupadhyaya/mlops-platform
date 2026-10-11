import json
import time
import urllib.error
import urllib.request

API = "http://127.0.0.1:8000"
INGEST = "http://127.0.0.1:8001"


def req(method: str, url: str, payload: dict | list | None = None) -> tuple[int, object]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode()
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())


def main() -> None:
    status, health = req("GET", f"{API}/health")
    assert status == 200 and health["service"] == "api", health
    status, experiment = req("POST", f"{API}/experiments", {"name": "smoke", "description": "compose smoke"})
    assert status == 200, experiment
    status, snapshot = req(
        "POST",
        f"{API}/snapshots",
        {
            "python_version": "3.11.9",
            "packages": {"fastapi": "0.115.6"},
            "image_digest": None,
            "config": {"lr": 0.001},
        },
    )
    assert status == 200, snapshot
    status, run = req(
        "POST",
        f"{API}/runs",
        {"experiment_id": experiment["id"], "snapshot_id": snapshot["id"], "params": {"batch": 8}},
    )
    assert status == 200, run
    batch = [{"run_id": run["id"], "name": "loss", "value": 1.0 / (i + 1), "step": i} for i in range(8)]
    status, ingest = req("POST", f"{INGEST}/ingest", batch)
    assert status == 202, ingest
    time.sleep(3)
    status, finished = req("POST", f"{API}/runs/{run['id']}/finish")
    assert status == 200 and finished["status"] == "finished", finished
    status, metrics = req("GET", f"{API}/runs/{run['id']}/metrics")
    assert status == 200, metrics
    print(json.dumps({"experiment": experiment["id"], "run": run["id"], "snapshot": snapshot["id"], "metrics": metrics}, indent=2))


if __name__ == "__main__":
    main()
