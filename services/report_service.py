from typing import Dict, List
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.database.models import Appointment, Patient


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def get_daily_revenue(self, clinic_id: str, target_date: date = None) -> Dict:
        if not target_date:
            target_date = date.today()

        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        appointments = (
            self.db.query(Appointment)
            .filter(
                Appointment.clinic_id == clinic_id,
                Appointment.deleted_at.is_(None),
                Appointment.appointment_date >= start_of_day,
                Appointment.appointment_date <= end_of_day,
            )
            .all()
        )

        total_revenue = sum(
            float(apt.visit_fee or 0) for apt in appointments
        )
        total_paid = sum(
            float(apt.paid_amount or 0) for apt in appointments
        )
        total_pending = total_revenue - total_paid

        return {
            "date": target_date.isoformat(),
            "total_appointments": len(appointments),
            "completed_appointments": len(
                [a for a in appointments if a.status == "completed"]
            ),
            "cancelled_appointments": len(
                [a for a in appointments if a.status == "cancelled"]
            ),
            "total_revenue": total_revenue,
            "total_paid": total_paid,
            "total_pending": total_pending,
        }

    def get_monthly_revenue(
        self, clinic_id: str, year: int = None, month: int = None
    ) -> Dict:
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month

        appointments = (
            self.db.query(Appointment)
            .filter(
                Appointment.clinic_id == clinic_id,
                Appointment.deleted_at.is_(None),
                extract("year", Appointment.appointment_date) == year,
                extract("month", Appointment.appointment_date) == month,
            )
            .all()
        )

        total_revenue = sum(
            float(apt.visit_fee or 0) for apt in appointments
        )
        total_paid = sum(
            float(apt.paid_amount or 0) for apt in appointments
        )

        daily_breakdown = {}
        for apt in appointments:
            day = apt.appointment_date.date().isoformat()
            if day not in daily_breakdown:
                daily_breakdown[day] = {
                    "appointments": 0,
                    "revenue": 0,
                    "paid": 0,
                }
            daily_breakdown[day]["appointments"] += 1
            daily_breakdown[day]["revenue"] += float(apt.visit_fee or 0)
            daily_breakdown[day]["paid"] += float(apt.paid_amount or 0)

        return {
            "year": year,
            "month": month,
            "total_appointments": len(appointments),
            "total_revenue": total_revenue,
            "total_paid": total_paid,
            "total_pending": total_revenue - total_paid,
            "daily_breakdown": daily_breakdown,
        }

    def get_patient_visit_history(self, patient_id: str) -> Dict:
        appointments = (
            self.db.query(Appointment)
            .filter(
                Appointment.patient_id == patient_id,
                Appointment.deleted_at.is_(None),
            )
            .order_by(Appointment.appointment_date.desc())
            .all()
        )

        total_visits = len(appointments)
        total_spent = sum(
            float(apt.paid_amount or 0) for apt in appointments
        )

        last_visit = appointments[0].appointment_date if appointments else None

        return {
            "patient_id": patient_id,
            "total_visits": total_visits,
            "total_spent": total_spent,
            "last_visit": last_visit.isoformat() if last_visit else None,
            "appointments": [
                {
                    "id": apt.id,
                    "date": apt.appointment_date.isoformat(),
                    "status": apt.status,
                    "fee": float(apt.visit_fee or 0),
                    "paid": float(apt.paid_amount or 0),
                }
                for apt in appointments
            ],
        }

    def get_clinic_stats(self, clinic_id: str) -> Dict:
        total_patients = (
            self.db.query(Patient)
            .filter(Patient.clinic_id == clinic_id, Patient.deleted_at.is_(None))
            .count()
        )

        total_appointments = (
            self.db.query(Appointment)
            .filter(
                Appointment.clinic_id == clinic_id,
                Appointment.deleted_at.is_(None),
            )
            .count()
        )

        today = date.today()
        today_appointments = (
            self.db.query(Appointment)
            .filter(
                Appointment.clinic_id == clinic_id,
                Appointment.deleted_at.is_(None),
                func.date(Appointment.appointment_date) == today,
            )
            .count()
        )

        upcoming_week = today + timedelta(days=7)
        upcoming_appointments = (
            self.db.query(Appointment)
            .filter(
                Appointment.clinic_id == clinic_id,
                Appointment.deleted_at.is_(None),
                Appointment.status == "scheduled",
                func.date(Appointment.appointment_date) > today,
                func.date(Appointment.appointment_date) <= upcoming_week,
            )
            .count()
        )

        return {
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "today_appointments": today_appointments,
            "upcoming_appointments": upcoming_appointments,
        }
