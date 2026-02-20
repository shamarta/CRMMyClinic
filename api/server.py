from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging

from app.config import settings
from app.database.local_db import local_db
from app.database.sync import sync_engine
from .dependencies import get_db
from .routes import auth, sync, appointments, patients, reports, clinic, navigation

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Lightweight CRM for Medical Clinics",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "mode": settings.app_mode,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/sync/trigger")
async def trigger_sync():
    try:
        result = await sync_engine.perform_sync()
        return {
            "success": True,
            "message": "Synchronization completed",
            "result": result,
        }
    except Exception as e:
        logger.error(f"Sync error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}",
        )


app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sync.router, prefix="/api/sync", tags=["Synchronization"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(patients.router, prefix="/api/patients", tags=["Patients"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(clinic.router, prefix="/api/clinic", tags=["Clinic"])
app.include_router(navigation.router, prefix="/api/navigation", tags=["Navigation"])
