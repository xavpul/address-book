import asyncio
import os
import shutil
import subprocess
from contextlib import asynccontextmanager
import sys
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Ensure test env is used BEFORE importing the app
os.environ["DB_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["DB_MIGRATION_URL"] = "sqlite:///./test.db"

# Import after env vars are set
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from main import app  # noqa: E402
from core.db import engine, SessionLocal  # noqa: E402


@pytest.fixture(scope="session")
def event_loop():
    # Use a single event loop for the whole test session
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def prepare_test_db():
    # Remove any existing test db file/folder
    if os.path.exists("test.db"):
        os.remove("test.db")

    # Ensure alembic env uses DB_MIGRATION_URL and run migrations to head
    # This will create test.db and apply schema
    subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        check=True,
        env={**os.environ},
    )

    yield

    # Teardown: remove test db after test session
    if os.path.exists("test.db"):
        os.remove("test.db")
    # Optional: clean alembic caches if any
    if os.path.exists("__pycache__"):
        shutil.rmtree("__pycache__", ignore_errors=True)


# Optional: if you prefer explicit commit control in tests, you can manage session here.
@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async_session: async_sessionmaker[AsyncSession] = SessionLocal
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Override get_db dependency to use the same session factory
async def _override_get_db():
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
async def client():
    from core.db import get_db
    from httpx import AsyncClient, ASGITransport

    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
