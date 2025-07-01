"""
Patient Management Service
Application service for patient-related operations
Coordinates between domain logic and infrastructure
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..core.interfaces import (
    IPatientRepository, 
    IPatientService,
    PatientId,
    SessionId
)
from ..core.exceptions import PatientNotFoundError, ValidationError
from ..domain.entities import Patient, HealthMeasurement, MedicalAppointment, MeasurementType
from ..domain.medical_validation import MedicalValidationService


logger = logging.getLogger(__name__)


class PatientService(IPatientService):
    """
    Application service for patient management
    Implements business workflows and validation
    """
    
    def __init__(self, 
                 patient_repository: IPatientRepository,
                 validation_service: MedicalValidationService):
        self.patient_repository = patient_repository
        self.validation_service = validation_service
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get_patient_profile(self, patient_id: PatientId) -> Patient:
        """Get complete patient profile"""
        try:
            patient = await self.patient_repository.get_patient(patient_id)
            self.logger.info(f"Retrieved patient profile for {patient_id.value}")
            return patient
        except PatientNotFoundError:
            self.logger.warning(f"Patient not found: {patient_id.value}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get patient profile: {e}")
            raise
    
    async def get_patient_measurements(self, 
                                     patient_id: PatientId,
                                     measurement_type: Optional[MeasurementType] = None,
                                     days: int = 30) -> List[HealthMeasurement]:
        """Get patient measurements with optional filtering"""
        try:
            measurements = await self.patient_repository.get_patient_measurements(
                patient_id, days
            )
            
            # Filter by measurement type if specified
            if measurement_type:
                measurements = [
                    m for m in measurements 
                    if m.type == measurement_type
                ]
            
            self.logger.info(
                f"Retrieved {len(measurements)} measurements for {patient_id.value}"
            )
            return measurements
            
        except Exception as e:
            self.logger.error(f"Failed to get measurements: {e}")
            raise
    
    async def save_measurement(self, 
                             patient_id: PatientId,
                             measurement_type: MeasurementType,
                             value: float,
                             unit: str,
                             notes: Optional[str] = None) -> HealthMeasurement:
        """Save a health measurement with validation"""
        try:
            # Validate measurement value
            validation_result = self.validation_service.validate_measurement(
                measurement_type, value, unit
            )
            
            if not validation_result.is_valid:
                raise ValidationError(
                    f"Invalid measurement: {validation_result.message}",
                    field=measurement_type.value,
                    value=value
                )
            
            # Create measurement entity
            measurement = HealthMeasurement(
                id="",  # Will be assigned by repository
                patient_id=patient_id.value,
                type=measurement_type,
                value=value,
                unit=unit,
                timestamp=datetime.now(),
                notes=notes
            )
            
            # Save to repository
            saved_measurement = await self.patient_repository.save_measurement(measurement)
            
            self.logger.info(
                f"Saved {measurement_type.value} measurement for {patient_id.value}: {value} {unit}"
            )
            
            # Check for emergency values
            if validation_result.is_emergency:
                self.logger.warning(
                    f"Emergency value detected: {measurement_type.value}={value} for {patient_id.value}"
                )
                # TODO: Trigger emergency notification system
            
            return saved_measurement
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to save measurement: {e}")
            raise
    
    async def get_patient_appointments(self, patient_id: PatientId) -> List[MedicalAppointment]:
        """Get patient appointments"""
        try:
            appointments = await self.patient_repository.get_patient_appointments(patient_id)
            self.logger.info(f"Retrieved {len(appointments)} appointments for {patient_id.value}")
            return appointments
        except Exception as e:
            self.logger.error(f"Failed to get appointments: {e}")
            raise
    
    async def schedule_appointment(self,
                                 patient_id: PatientId,
                                 specialty: str,
                                 preferred_date: Optional[datetime] = None,
                                 notes: Optional[str] = None) -> MedicalAppointment:
        """Schedule a new appointment"""
        try:
            # Validate patient exists
            await self.get_patient_profile(patient_id)
            
            # Create appointment entity
            appointment = MedicalAppointment(
                id="",  # Will be assigned by repository
                patient_id=patient_id.value,
                specialty=specialty,
                doctor_name="",  # Will be assigned by backend
                date=preferred_date or datetime.now() + timedelta(days=7),
                status=None,  # Will be set by backend
                is_virtual=True,
                meeting_link=None,
                notes=notes
            )
            
            # Save to repository
            saved_appointment = await self.patient_repository.schedule_appointment(appointment)
            
            self.logger.info(
                f"Scheduled {specialty} appointment for {patient_id.value}"
            )
            
            return saved_appointment
            
        except Exception as e:
            self.logger.error(f"Failed to schedule appointment: {e}")
            raise
    
    async def get_health_summary(self, patient_id: PatientId, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive health summary for patient"""
        try:
            # Get patient profile
            patient = await self.get_patient_profile(patient_id)
            
            # Get recent measurements
            measurements = await self.get_patient_measurements(patient_id, days=days)
            
            # Get upcoming appointments
            appointments = await self.get_patient_appointments(patient_id)
            upcoming_appointments = [
                appt for appt in appointments
                if appt.date > datetime.now()
            ]
            
            # Group measurements by type
            measurements_by_type = {}
            for measurement in measurements:
                measurement_type = measurement.type.value
                if measurement_type not in measurements_by_type:
                    measurements_by_type[measurement_type] = []
                measurements_by_type[measurement_type].append({
                    'value': measurement.value,
                    'unit': measurement.unit,
                    'timestamp': measurement.timestamp.isoformat(),
                    'notes': measurement.notes
                })
            
            # Calculate basic statistics
            glucose_measurements = measurements_by_type.get('glucose_fasting', [])
            avg_glucose = None
            if glucose_measurements:
                avg_glucose = sum(m['value'] for m in glucose_measurements) / len(glucose_measurements)
            
            summary = {
                'patient': {
                    'id': patient.id,
                    'name': patient.name,
                    'diabetes_type': patient.diabetes_type
                },
                'measurements': measurements_by_type,
                'statistics': {
                    'total_measurements': len(measurements),
                    'average_glucose_fasting': avg_glucose,
                    'measurement_period_days': days
                },
                'appointments': {
                    'upcoming_count': len(upcoming_appointments),
                    'next_appointment': upcoming_appointments[0].date.isoformat() if upcoming_appointments else None
                }
            }
            
            self.logger.info(f"Generated health summary for {patient_id.value}")
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate health summary: {e}")
            raise
