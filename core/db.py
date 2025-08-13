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

SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
