from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.export import router as export_router
from app.routes.extract import router as extract_router
from app.routes.health import router as health_router
from app.routes.templates import router as templates_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.ensure_base_directories()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = "/api"

app.include_router(health_router, prefix=api_prefix)
app.include_router(extract_router, prefix=api_prefix)
app.include_router(export_router, prefix=api_prefix)
app.include_router(templates_router, prefix=api_prefix)


@app.get("/")
def root() -> dict[str, object]:
    return {
        "message": f"Bienvenue dans {settings.APP_NAME}",
        "health": "/api/health",
        "docs": "/docs",
        "frontend_origins": settings.FRONTEND_ORIGINS,
        "debug": settings.DEBUG,
    }