# MLOps Platform (mini W&B)

Experiment tracking with async FastAPI services, Redis Streams metric ingest, a scalable Postgres writer, live host telemetry, and pgvector semantic search.

## Architecture

```
host agent  --pubsub telemetry:{node}--> Redis --> telemetry WS --> dashboard
training job --POST /ingest----------> ingest --XADD metrics--> Redis Stream
                                                   writer (consumer group) --bulk insert--> Postgres
dashboard / client --REST--> api (experiments, runs, snapshots)
search --embed MiniLM + optional Haiku rewrite--> pgvector HNSW
```

- **api** — experiments, runs, immutable SHA-256 snapshots, Alembic migrations on boot
- **ingest** — batched metric XADD (`maxlen≈1M`) via Redis pipeline, HTTP 202
- **writer** — `XREADGROUP` count=500, bulk insert, `XACK` only after commit (scale with `docker compose up --scale writer=2`)
- **telemetry** — `PSUBSCRIBE telemetry:*`, WebSocket fan-out, drop dead sockets
- **search** — `all-MiniLM-L6-v2` embeddings, HNSW cosine, optional `claude-haiku-5-5` query rewrite
- **dashboard** — nginx static UI; proxies `/api/` and `/ws/`
- **agent** — runs on the host (not in Compose); psutil + optional pynvml

## Setup

```bash
cp .env.example .env
# set ANTHROPIC_API_KEY for LLM query rewrite (optional)
docker compose up --build
```

Dashboard: http://localhost:8088  
API: http://localhost:8000/health  
Ingest: http://localhost:8001/health  
Search: http://localhost:8003/health

Host telemetry agent:

```bash
pip install psutil nvidia-ml-py redis
set REDIS_URL=redis://localhost:6379/0
set NODE_ID=%COMPUTERNAME%
python -m mlops.agent
```

Capture a snapshot from a training process:

```python
from mlops.client import capture_env
snapshot_id = capture_env({"lr": 3e-4}, image_digest=None)
```

## Tests

```bash
pip install -r requirements.txt pytest pytest-asyncio
pytest -q
```

Load test (50-metric batches):

```bash
docker compose --profile load up --abort-on-container-exit locust
```

## Load-test results

Measured against local Docker Compose (20 Locust users, 45s, 50 metrics/request):

| Metric | Value |
| --- | --- |
| Requests | 5775 POST `/ingest` (0 failures) |
| Requests/s | 129.08 overall (steady ~145–149) |
| p95 latency | 51 ms |
| Stream drain | writer kept up: Redis lag 0, pending 0, 288758 stream entries = 288758 Postgres rows |
