from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.database.models import Appointment, Patient


class AppointmentService:
    def __init__(self, db: Session):
        self.db = db

    def create_appointment(
        self,
        clinic_id: str,
        patient_id: str,
        appointment_date: datetime,
        **kwargs,
    ) -> Appointment:
        appointment = Appointment(
            clinic_id=clinic_id,
            patient_id=patient_id,
            appointment_date=appointment_date,
            **kwargs,
        )
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        return (
            self.db.query(Appointment)
            .filter(
                Appointment.id == appointment_id,
                Appointment.deleted_at.is_(None),
            )
            .first()
        )

    def get_appointments_by_date(
        self, clinic_id: str, target_date: date
    ) -> List[Appointment]:
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        return (
            self.db.query(Appointment)
            .filter(
                Appointment.clinic_id == clinic_id,
                Appointment.deleted_at.is_(None),
                Appointment.appointment_date >= start_of_day,
                Appointment.appointment_date <= end_of_day,
            )
            .order_by(Appointment.appointment_date)
            .all()
        )

    def get_patient_appointments(
        self, patient_id: str, skip: int = 0, limit: int = 50
    ) -> List[Appointment]:
        return (
            self.db.query(Appointment)
            .filter(
                Appointment.patient_id == patient_id,
                Appointment.deleted_at.is_(None),
            )
            .order_by(Appointment.appointment_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_upcoming_appointments(
        self, clinic_id: str, days: int = 7
    ) -> List[Appointment]:
        now = datetime.utcnow()
        future = now + timedelta(days=days)

        return (
            self.db.query(Appointment)
            .filter(
                Appointment.clinic_id == clinic_id,
                Appointment.deleted_at.is_(None),
                Appointment.appointment_date >= now,
                Appointment.appointment_date <= future,
                Appointment.status == "scheduled",
            )
            .order_by(Appointment.appointment_date)
            .all()
        )

    def update_appointment(
        self, appointment_id: str, **kwargs
    ) -> Optional[Appointment]:
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return None

        for key, value in kwargs.items():
            if hasattr(appointment, key):
                setattr(appointment, key, value)

        appointment.updated_at = datetime.utcnow()
        appointment.sync_status = "pending"
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def cancel_appointment(self, appointment_id: str) -> bool:
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return False

        appointment.status = "cancelled"
        appointment.updated_at = datetime.utcnow()
        appointment.sync_status = "pending"
        self.db.commit()
        return True

    def complete_appointment(self, appointment_id: str, **kwargs) -> bool:
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return False

        appointment.status = "completed"
        for key, value in kwargs.items():
            if hasattr(appointment, key):
                setattr(appointment, key, value)

        appointment.updated_at = datetime.utcnow()
        appointment.sync_status = "pending"
        self.db.commit()
        return True

    def delete_appointment(self, appointment_id: str) -> bool:
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return False

        appointment.deleted_at = datetime.utcnow()
        appointment.sync_status = "pending"
        self.db.commit()
        return True

    def check_availability(
        self, clinic_id: str, appointment_date: datetime, duration: int = 30
    ) -> bool:
        end_time = appointment_date + timedelta(minutes=duration)

        conflicting = (
            self.db.query(Appointment)
            .filter(
                Appointment.clinic_id == clinic_id,
                Appointment.deleted_at.is_(None),
                Appointment.status == "scheduled",
                Appointment.appointment_date < end_time,
                func.datetime(
                    Appointment.appointment_date,
                    f"+{Appointment.duration_minutes} minutes",
                )
                > appointment_date,
            )
            .first()
        )

        return conflicting is None
