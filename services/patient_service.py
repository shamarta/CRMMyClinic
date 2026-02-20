from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.models import Patient


class PatientService:
    def __init__(self, db: Session):
        self.db = db

    def create_patient(
        self,
        clinic_id: str,
        national_id: str,
        first_name: str,
        last_name: str,
        **kwargs,
    ) -> Patient:
        patient = Patient(
            clinic_id=clinic_id,
            national_id=national_id,
            first_name=first_name,
            last_name=last_name,
            **kwargs,
        )
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        return (
            self.db.query(Patient)
            .filter(Patient.id == patient_id, Patient.deleted_at.is_(None))
            .first()
        )

    def get_patient_by_national_id(self, national_id: str) -> Optional[Patient]:
        return (
            self.db.query(Patient)
            .filter(
                Patient.national_id == national_id, Patient.deleted_at.is_(None)
            )
            .first()
        )

    def get_patients(
        self, clinic_id: str, skip: int = 0, limit: int = 100
    ) -> List[Patient]:
        return (
            self.db.query(Patient)
            .filter(Patient.clinic_id == clinic_id, Patient.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_patients(self, clinic_id: str, query: str) -> List[Patient]:
        search_term = f"%{query}%"
        return (
            self.db.query(Patient)
            .filter(
                Patient.clinic_id == clinic_id,
                Patient.deleted_at.is_(None),
                or_(
                    Patient.first_name.ilike(search_term),
                    Patient.last_name.ilike(search_term),
                    Patient.national_id.ilike(search_term),
                    Patient.phone.ilike(search_term),
                    Patient.mobile.ilike(search_term),
                ),
            )
            .all()
        )

    def update_patient(self, patient_id: str, **kwargs) -> Optional[Patient]:
        patient = self.get_patient(patient_id)
        if not patient:
            return None

        for key, value in kwargs.items():
            if hasattr(patient, key):
                setattr(patient, key, value)

        patient.updated_at = datetime.utcnow()
        patient.sync_status = "pending"
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def delete_patient(self, patient_id: str) -> bool:
        patient = self.get_patient(patient_id)
        if not patient:
            return False

        patient.deleted_at = datetime.utcnow()
        patient.sync_status = "pending"
        self.db.commit()
        return True

    def get_patient_stats(self, clinic_id: str) -> dict:
        total_patients = (
            self.db.query(Patient)
            .filter(Patient.clinic_id == clinic_id, Patient.deleted_at.is_(None))
            .count()
        )

        return {"total_patients": total_patients}
