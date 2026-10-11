FROM python:3.11-slim
ARG SERVICE=api
ENV SERVICE=${SERVICE}
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN if [ "$SERVICE" = "search" ]; then \
      pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
      pip install --no-cache-dir sentence-transformers==3.3.1; \
    fi
COPY mlops /app/mlops
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
EXPOSE 8000 8001 8002 8003 8004
CMD ["sh", "-c", "python -m mlops.services.${SERVICE}"]
