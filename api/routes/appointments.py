from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional

from app.database.local_db import local_db
from app.services.appointment_service import AppointmentService
from app.database.models import Appointment
from app.api.dependencies import get_db

router = APIRouter()


class AppointmentCreate(BaseModel):
    clinic_id: str
    patient_id: str
    appointment_date: datetime
    duration_minutes: int = 30
    visit_fee: float = 0


class AppointmentResponse(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    appointment_date: datetime
    status: str
    visit_fee: float
    patient_name: Optional[str] = None
    duration_minutes: Optional[int] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_patient(cls, apt):
        return cls(
            id=apt.id,
            clinic_id=apt.clinic_id,
            patient_id=apt.patient_id,
            appointment_date=apt.appointment_date,
            status=apt.status,
            visit_fee=float(apt.visit_fee or 0),
            duration_minutes=apt.duration_minutes,
            patient_name=f"{apt.patient.first_name} {apt.patient.last_name}" if apt.patient else None,
        )


@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate, db: Session = Depends(get_db)
):
    service = AppointmentService(db)
    new_appointment = service.create_appointment(
        clinic_id=appointment.clinic_id,
        patient_id=appointment.patient_id,
        appointment_date=appointment.appointment_date,
        duration_minutes=appointment.duration_minutes,
        visit_fee=appointment.visit_fee,
    )
    return new_appointment


@router.get("/date/{clinic_id}/{target_date}", response_model=List[AppointmentResponse])
def get_appointments_by_date(
    clinic_id: str, target_date: date, db: Session = Depends(get_db)
):
    service = AppointmentService(db)
    appointments = service.get_appointments_by_date(clinic_id, target_date)
    return [AppointmentResponse.from_orm_with_patient(apt) for apt in appointments]


@router.get("/upcoming/{clinic_id}", response_model=List[AppointmentResponse])
def get_upcoming_appointments(
    clinic_id: str, days: int = 7, db: Session = Depends(get_db)
):
    service = AppointmentService(db)
    appointments = service.get_upcoming_appointments(clinic_id, days)
    return [AppointmentResponse.from_orm_with_patient(apt) for apt in appointments]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
):
    service = AppointmentService(db)
    apt = service.get_appointment(appointment_id)
    if not apt:
        raise HTTPException(status_code=404, detail="نوبت یافت نشد")
    return AppointmentResponse.from_orm_with_patient(apt)


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
):
    service = AppointmentService(db)
    apt = service.complete_appointment(appointment_id)
    if not apt:
        raise HTTPException(status_code=404, detail="نوبت یافت نشد")
    return AppointmentResponse.from_orm_with_patient(apt)


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
):
    service = AppointmentService(db)
    apt = service.cancel_appointment(appointment_id)
    if not apt:
        raise HTTPException(status_code=404, detail="نوبت یافت نشد")
    return AppointmentResponse.from_orm_with_patient(apt)
