from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from typing import List, Optional

from app.database.local_db import local_db
from app.services.patient_service import PatientService
from app.database.models import Patient
from app.api.dependencies import get_db

router = APIRouter()


class PatientCreate(BaseModel):
    national_id: str
    first_name: str
    last_name: str
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    medical_notes: Optional[str] = None
    allergies: Optional[str] = None


class PatientUpdate(BaseModel):
    national_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    medical_notes: Optional[str] = None
    allergies: Optional[str] = None


class PatientResponse(BaseModel):
    id: str
    clinic_id: str
    national_id: str
    first_name: str
    last_name: str
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    medical_notes: Optional[str] = None
    allergies: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PatientResponse])
def list_patients(
    clinic_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    service = PatientService(db)
    return service.get_patients(clinic_id, skip=skip, limit=limit)


@router.get("/search", response_model=List[PatientResponse])
def search_patients(
    clinic_id: str,
    q: str,
    db: Session = Depends(get_db),
):
    if not q or len(q.strip()) == 0:
        service = PatientService(db)
        return service.get_patients(clinic_id, limit=50)
    service = PatientService(db)
    return service.search_patients(clinic_id, q.strip())


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
):
    service = PatientService(db)
    patient = service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="بیمار یافت نشد")
    return patient


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    clinic_id: str,
    patient: PatientCreate,
    db: Session = Depends(get_db),
):
    service = PatientService(db)
    try:
        return service.create_patient(
            clinic_id=clinic_id,
            national_id=patient.national_id,
            first_name=patient.first_name,
            last_name=patient.last_name,
            birth_date=patient.birth_date,
            gender=patient.gender,
            phone=patient.phone,
            mobile=patient.mobile,
            email=patient.email,
            address=patient.address,
            medical_notes=patient.medical_notes,
            allergies=patient.allergies,
        )
    except Exception as e:
        if "unique" in str(e).lower() or "national_id" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="کد ملی تکراری است",
            )
        raise


@router.patch("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: str,
    patient: PatientUpdate,
    db: Session = Depends(get_db),
):
    service = PatientService(db)
    updated = service.update_patient(
        patient_id,
        **patient.model_dump(exclude_unset=True),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="بیمار یافت نشد")
    return updated


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
):
    service = PatientService(db)
    if not service.delete_patient(patient_id):
        raise HTTPException(status_code=404, detail="بیمار یافت نشد")
    return None
