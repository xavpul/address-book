from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.db import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="Address Book",
    lifespan=lifespan,
)
