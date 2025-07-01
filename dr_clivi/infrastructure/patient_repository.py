"""
Patient Repository Implementation
Data access layer for patient information
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta

from ..core.interfaces import IPatientRepository, PatientId, SessionId
from ..core.exceptions import PatientNotFoundError, BackendError
from ..domain.entities import Patient, HealthMeasurement, MedicalAppointment
from ..services.backend_integration import BackendIntegrationService, MockBackendService


logger = logging.getLogger(__name__)


class BackendPatientRepository(IPatientRepository):
    """
    Patient repository using backend service
    Implements data access patterns with error handling
    """
    
    def __init__(self, backend_service: BackendIntegrationService):
        self.backend_service = backend_service
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get_patient(self, patient_id: PatientId) -> Patient:
        """Get patient by ID"""
        try:
            return await self.backend_service.get_patient(patient_id.value)
        except Exception as e:
            self.logger.error(f"Failed to get patient {patient_id.value}: {e}")
            raise PatientNotFoundError(patient_id.value)
    
    async def get_patient_measurements(self, patient_id: PatientId, 
                                     days: int = 30) -> List[HealthMeasurement]:
        """Get patient measurements for specified period"""
        try:
            return await self.backend_service.get_measurements(
                patient_id.value, days=days
            )
        except Exception as e:
            self.logger.error(f"Failed to get measurements for {patient_id.value}: {e}")
            raise BackendError(f"Could not retrieve measurements: {e}")
    
    async def get_patient_appointments(self, patient_id: PatientId) -> List[MedicalAppointment]:
        """Get patient appointments"""
        try:
            return await self.backend_service.get_patient_appointments(patient_id.value)
        except Exception as e:
            self.logger.error(f"Failed to get appointments for {patient_id.value}: {e}")
            raise BackendError(f"Could not retrieve appointments: {e}")
    
    async def save_measurement(self, measurement: HealthMeasurement) -> HealthMeasurement:
        """Save a health measurement"""
        try:
            return await self.backend_service.save_measurement(
                measurement.patient_id,
                measurement.type,
                measurement.value,
                measurement.unit,
                measurement.notes
            )
        except Exception as e:
            self.logger.error(f"Failed to save measurement: {e}")
            raise BackendError(f"Could not save measurement: {e}")
    
    async def schedule_appointment(self, appointment: MedicalAppointment) -> MedicalAppointment:
        """Schedule a new appointment"""
        try:
            return await self.backend_service.schedule_appointment(
                appointment.patient_id,
                appointment.specialty,
                appointment.date
            )
        except Exception as e:
            self.logger.error(f"Failed to schedule appointment: {e}")
            raise BackendError(f"Could not schedule appointment: {e}")


class InMemoryPatientRepository(IPatientRepository):
    """
    In-memory patient repository for testing
    Implements the same interface with mock data
    """
    
    def __init__(self):
        self.mock_service = MockBackendService()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get_patient(self, patient_id: PatientId) -> Patient:
        """Get patient by ID"""
        return await self.mock_service.get_patient(patient_id.value)
    
    async def get_patient_measurements(self, patient_id: PatientId, 
                                     days: int = 30) -> List[HealthMeasurement]:
        """Get patient measurements for specified period"""
        return await self.mock_service.get_measurements(patient_id.value, days=days)
    
    async def get_patient_appointments(self, patient_id: PatientId) -> List[MedicalAppointment]:
        """Get patient appointments"""
        return await self.mock_service.get_patient_appointments(patient_id.value)
    
    async def save_measurement(self, measurement: HealthMeasurement) -> HealthMeasurement:
        """Save a health measurement"""
        return await self.mock_service.save_measurement(
            measurement.patient_id,
            measurement.type,
            measurement.value,
            measurement.unit,
            measurement.notes
        )
    
    async def schedule_appointment(self, appointment: MedicalAppointment) -> MedicalAppointment:
        """Schedule a new appointment"""
        return await self.mock_service.schedule_appointment(
            appointment.patient_id,
            appointment.specialty,
            appointment.date
        )
