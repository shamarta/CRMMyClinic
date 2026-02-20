from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database.local_db import local_db
from app.services.clinic_service import ClinicService
from app.database.models import Clinic
from app.api.dependencies import get_db

router = APIRouter()


class ClinicResponse(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    license_number: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/default", response_model=ClinicResponse)
def get_default_clinic(db: Session = Depends(get_db)):
    service = ClinicService(db)
    clinic = service.ensure_default_clinic()
    return clinic


@router.get("/{clinic_id}", response_model=ClinicResponse)
def get_clinic(
    clinic_id: str,
    db: Session = Depends(get_db),
):
    service = ClinicService(db)
    clinic = service.get_clinic(clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="مطب یافت نشد")
    return clinic
