"""
Domain Layer - Business Logic and Entities
Contains the core business logic, entities, and domain services
"""

from .entities import (
    Patient,
    HealthMeasurement,
    MedicalAppointment,
    MeasurementType,
    AppointmentStatus,
    PatientPlan,
    PatientSession
)
from .medical_validation import MedicalValidationService

__all__ = [
    # Entities
    "Patient",
    "HealthMeasurement", 
    "MedicalAppointment",
    "MeasurementType",
    "AppointmentStatus",
    "PatientPlan",
    "PatientSession",
    
    # Services
    "MedicalValidationService"
]
