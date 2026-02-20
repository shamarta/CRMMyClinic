from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    Numeric,
    Date,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    license_number = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    last_synced_at = Column(DateTime, nullable=True)
    sync_status = Column(String(20), default="pending")

    patients = relationship("Patient", back_populates="clinic")
    appointments = relationship("Appointment", back_populates="clinic")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, default=generate_uuid)
    clinic_id = Column(String, ForeignKey("clinics.id"), nullable=False)

    national_id = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date)
    gender = Column(String(10))
    phone = Column(String(20))
    mobile = Column(String(20))
    email = Column(String(100))
    address = Column(Text)

    medical_notes = Column(Text)
    allergies = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    last_synced_at = Column(DateTime, nullable=True)
    sync_status = Column(String(20), default="pending")

    clinic = relationship("Clinic", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String, primary_key=True, default=generate_uuid)
    clinic_id = Column(String, ForeignKey("clinics.id"), nullable=False)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)

    appointment_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    status = Column(String(20), default="scheduled")

    chief_complaint = Column(Text)
    diagnosis = Column(Text)
    treatment_plan = Column(Text)
    prescription = Column(Text)

    visit_fee = Column(Numeric(10, 2), default=0)
    paid_amount = Column(Numeric(10, 2), default=0)
    payment_status = Column(String(20), default="unpaid")

    reminder_sent = Column(Boolean, default=False)
    reminder_sent_at = Column(DateTime, nullable=True)

    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    last_synced_at = Column(DateTime, nullable=True)
    sync_status = Column(String(20), default="pending")

    clinic = relationship("Clinic", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String, nullable=False)
    operation = Column(String(20), nullable=False)
    sync_direction = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
