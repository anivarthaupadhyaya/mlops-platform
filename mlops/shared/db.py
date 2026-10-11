from collections.abc import AsyncGenerator

from pgvector.asyncpg import register_vector
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from mlops.shared.config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)


@event.listens_for(engine.sync_engine, "connect")
def _register_vector(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
    dbapi_connection.run_async(register_vector)


SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
