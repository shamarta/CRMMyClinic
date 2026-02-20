from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database.local_db import local_db
from app.services.report_service import ReportService
from app.api.dependencies import get_db

router = APIRouter()


@router.get("/daily")
def get_daily_revenue(
    clinic_id: str,
    target_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    if not target_date:
        target_date = date.today()
    service = ReportService(db)
    return service.get_daily_revenue(clinic_id, target_date)


@router.get("/monthly")
def get_monthly_revenue(
    clinic_id: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
):
    service = ReportService(db)
    return service.get_monthly_revenue(clinic_id, year=year, month=month)


@router.get("/stats")
def get_clinic_stats(
    clinic_id: str,
    db: Session = Depends(get_db),
):
    service = ReportService(db)
    return service.get_clinic_stats(clinic_id)


@router.get("/patient/{patient_id}/history")
def get_patient_visit_history(
    patient_id: str,
    db: Session = Depends(get_db),
):
    service = ReportService(db)
    return service.get_patient_visit_history(patient_id)
