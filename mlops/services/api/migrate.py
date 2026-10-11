from alembic import command
from alembic.config import Config

from mlops.shared.config import settings


def run_migrations() -> None:
    cfg = Config("alembic.ini")
    cfg.set_main_option(
        "sqlalchemy.url",
        settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://"),
    )
    command.upgrade(cfg, "head")
