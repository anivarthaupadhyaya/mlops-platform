from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://mlops:mlops@localhost:5432/mlops"
    redis_url: str = "redis://localhost:6379/0"
    anthropic_api_key: str = ""
    node_id: str = "local"
    api_url: str = "http://localhost:8000"
    metrics_stream: str = "metrics"
    writer_group: str = "writers"
    stream_maxlen: int = 1_000_000
    anthropic_model: str = "claude-haiku-5-5"


settings = Settings()
