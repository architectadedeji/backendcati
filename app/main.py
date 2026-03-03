# FastAPI Backend

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth_router
from app.routers.analytics import router as analytics_router
from app.routers.config import router as config_router
from app.routers.contacts import router as contacts_router
from app.routers.interviews import router as interviews_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Keep startup fast so Render can boot the service successfully."""
    print("[STARTUP] FastAPI app starting")
    try:
        yield
    finally:
        print("[SHUTDOWN] FastAPI app stopping")


app = FastAPI(
    title="StreamCATI API",
    version="1.0.0",
    root_path="",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics_router)
app.include_router(auth_router)
app.include_router(contacts_router)
app.include_router(interviews_router)
app.include_router(config_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}