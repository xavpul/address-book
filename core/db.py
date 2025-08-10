from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from core.config import settings

engine: AsyncEngine = create_async_engine(
    str(settings.DB_URL),
    echo=True,
    connect_args={
        "check_same_thread": False,
        "detect_types": 0,
        "timeout": 30,
        "uri": True,
    },
    future=True,
    pool_size=10,
    max_overflow=20,
)


def _enable_spatialite(dbapi_conn, _):
    dbapi_conn.enable_load_extension(True)
    dbapi_conn.load_extension("/usr/lib/sqlite3/pmod_spatialite.so")


event.listen(engine.sync_engine, "connect", _enable_spatialite)

SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
