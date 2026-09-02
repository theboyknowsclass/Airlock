from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from .db import close_pool, init_pool
from .queue import close_queue, init_queue
from .routes import packages, requests


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await init_pool()
    await init_queue()
    yield
    await close_queue()
    await close_pool()


app = FastAPI(title="Airlock API", lifespan=lifespan)
app.include_router(requests.router)
app.include_router(packages.router)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
