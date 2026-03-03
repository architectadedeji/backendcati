# FastAPI Backend

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine, Base, AsyncSessionLocal
from app.routers import auth_router
from app.routers.contacts import router as contacts_router
from app.routers.interviews import router as interviews_router
from app.routers.analytics import router as analytics_router
from app.routers.config import router as config_router
from app.enums import ContactStatus


async def normalize_contact_statuses():
    """Normalize contact status values on startup to fix mixed-case data."""
    status_mapping = {
        "ROUND_1": ContactStatus.ROUND_1.value,
        "ROUND_2": ContactStatus.ROUND_2.value,
        "ROUND_3": ContactStatus.ROUND_3.value,
        "ROUND_4": ContactStatus.ROUND_4.value,
        "ALL_ROUNDS_COMPLETED": ContactStatus.ALL_ROUNDS_COMPLETED.value,
    }
    async with AsyncSessionLocal() as session:
        total_updated = 0
        for old_status, new_status in status_mapping.items():
            result = await session.execute(
                text("UPDATE contacts SET status = :new_status WHERE status = :old_status"),
                {"new_status": new_status, "old_status": old_status}
            )
            total_updated += result.rowcount
        await session.commit()
        if total_updated > 0:
            print(f"[STARTUP] Normalized {total_updated} contact status values to lowercase enum values")


async def backfill_interview_counts():
    """Backfill interview_count from actual Interview records for data integrity."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                UPDATE contacts
                SET interview_count = (
                    SELECT COUNT(*)
                    FROM interviews
                    WHERE interviews.contact_id = contacts.id
                    AND interviews.completed_at IS NOT NULL
                )
            """)
        )
        updated = result.rowcount
        await session.commit()
        if updated > 0:
            print(f"[STARTUP] Backfilled interview_count for {updated} contacts from Interview records")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: run startup tasks."""
    await normalize_contact_statuses()
    await backfill_interview_counts()
    yield


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
