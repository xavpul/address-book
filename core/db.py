import os
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from core.config import settings


# 1) Helper to peel off any async/adapter wrappers
def _unwrap_sqlite(dbapi_conn):
    conn = dbapi_conn
    for _ in range(5):
        if hasattr(conn, "enable_load_extension"):
            return conn
        for attr in ("_connection", "_conn", "connection", "_dbapi_connection"):
            if hasattr(conn, attr):
                conn = getattr(conn, attr)
                break
    raise RuntimeError("Could not find raw sqlite3.Connection")


# 2) Sync listener for the sync engine
def _enable_spatialite(dbapi_conn, connection_record):
    raw_conn = _unwrap_sqlite(dbapi_conn)
    raw_conn.enable_load_extension(True)
    raw_conn.load_extension("mod_spatialite")
    raw_conn.execute("SELECT InitSpatialMetaData(1);")


# 3) Create the async engine
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

# 4) Register the listener on the *sync* engine
event.listen(engine.sync_engine, "connect", _enable_spatialite)

# 5) Session factory
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 6) FastAPI dependency
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
