"""NanaHouse Backend API - FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle: database init and cleanup."""
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(v1_router, prefix=settings.api_prefix)


@app.get("/")
async def root() -> dict:
    """Root endpoint returning API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
