"""Clinic management service - مدیریت مطب."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.models import Clinic


class ClinicService:
    def __init__(self, db: Session):
        self.db = db

    def create_clinic(
        self,
        name: str,
        address: str = "",
        phone: str = "",
        email: str = "",
        license_number: str = "",
    ) -> Clinic:
        clinic = Clinic(
            name=name,
            address=address,
            phone=phone,
            email=email,
            license_number=license_number,
        )
        self.db.add(clinic)
        self.db.commit()
        self.db.refresh(clinic)
        return clinic

    def get_clinic(self, clinic_id: str) -> Optional[Clinic]:
        return (
            self.db.query(Clinic)
            .filter(Clinic.id == clinic_id, Clinic.deleted_at.is_(None))
            .first()
        )

    def get_first_clinic(self) -> Optional[Clinic]:
        """Returns the first active clinic (for single-clinic usage)."""
        return (
            self.db.query(Clinic)
            .filter(Clinic.deleted_at.is_(None))
            .order_by(Clinic.created_at)
            .first()
        )

    def get_all_clinics(self) -> List[Clinic]:
        return (
            self.db.query(Clinic)
            .filter(Clinic.deleted_at.is_(None))
            .order_by(Clinic.name)
            .all()
        )

    def update_clinic(self, clinic_id: str, **kwargs) -> Optional[Clinic]:
        clinic = self.get_clinic(clinic_id)
        if not clinic:
            return None
        for key, value in kwargs.items():
            if hasattr(clinic, key):
                setattr(clinic, key, value)
        clinic.sync_status = "pending"
        self.db.commit()
        self.db.refresh(clinic)
        return clinic

    def ensure_default_clinic(self) -> Clinic:
        """Creates a default clinic if none exists. Returns the active clinic."""
        clinic = self.get_first_clinic()
        if clinic:
            return clinic
        clinic = self.create_clinic(
            name="مطب من",
            address="",
            phone="",
            email="",
            license_number="",
        )
        return clinic
