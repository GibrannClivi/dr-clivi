"""
Backend Integration Service for Dr. Clivi
Mock implementation demonstrating integration patterns
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

import aiohttp
from aiohttp import ClientTimeout

from ..core.exceptions import DrCliviException, BackendError
from ..core.interfaces import IBackendClient, PatientId
from ..domain.entities import (
    AppointmentStatus,
    MeasurementType,
    Patient,
    HealthMeasurement,
    MedicalAppointment
)

logger = logging.getLogger(__name__)


class BackendIntegrationService:
    """
    Service for integrating with external Dr. Clivi backend
    Implements async HTTP client with error handling and retries
    """
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = ClientTimeout(total=timeout)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_session()
    
    async def _ensure_session(self):
        """Ensure HTTP session is initialized"""
        if self._session is None or self._session.closed:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'DrClivi-TelegramBot/1.0'
            }
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=self.timeout
            )
    
    async def _close_session(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def _make_request(self, method: str, endpoint: str, 
                          data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request with error handling and retries"""
        await self._ensure_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            async with self._session.request(method, url, json=data) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    self.logger.error(f"Backend error {response.status}: {response_data}")
                    raise BackendError(f"API request failed: {response_data.get('message', 'Unknown error')}")
                
                return response_data
                
        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP client error: {e}")
            raise BackendError(f"Connection error: {str(e)}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response: {e}")
            raise BackendError("Invalid response format")
    
    # ==================== PATIENT MANAGEMENT ====================
    
    async def get_patient(self, patient_id: str) -> Patient:
        """Get patient information"""
        response = await self._make_request('GET', f'/api/patients/{patient_id}')
        return Patient(**response['data'])
    
    async def update_patient(self, patient_id: str, updates: Dict[str, Any]) -> Patient:
        """Update patient information"""
        response = await self._make_request('PUT', f'/api/patients/{patient_id}', updates)
        return Patient(**response['data'])
    
    # ==================== APPOINTMENT MANAGEMENT ====================
    
    async def get_patient_appointments(self, patient_id: str, 
                                     status: Optional[AppointmentStatus] = None) -> List[MedicalAppointment]:
        """Get patient's appointments, optionally filtered by status"""
        endpoint = f'/api/appointments/{patient_id}'
        if status:
            endpoint += f'?status={status.value}'
        
        response = await self._make_request('GET', endpoint)
        
        appointments = []
        for appt_data in response['data']:
            # Convert date string to datetime
            appt_data['date'] = datetime.fromisoformat(appt_data['date'])
            appt_data['status'] = AppointmentStatus(appt_data['status'])
            appointments.append(MedicalAppointment(**appt_data))
        
        return appointments
    
    async def schedule_appointment(self, patient_id: str, specialty: str, 
                                 preferred_date: Optional[datetime] = None) -> MedicalAppointment:
        """Schedule a new appointment"""
        data = {
            'patient_id': patient_id,
            'specialty': specialty,
            'preferred_date': preferred_date.isoformat() if preferred_date else None
        }
        
        response = await self._make_request('POST', '/api/appointments', data)
        
        appt_data = response['data']
        appt_data['date'] = datetime.fromisoformat(appt_data['date'])
        appt_data['status'] = AppointmentStatus(appt_data['status'])
        
        return MedicalAppointment(**appt_data)
    
    async def reschedule_appointment(self, appointment_id: str, 
                                   new_date: datetime) -> MedicalAppointment:
        """Reschedule an existing appointment"""
        data = {'new_date': new_date.isoformat()}
        response = await self._make_request('PUT', f'/api/appointments/{appointment_id}', data)
        
        appt_data = response['data']
        appt_data['date'] = datetime.fromisoformat(appt_data['date'])
        appt_data['status'] = AppointmentStatus(appt_data['status'])
        
        return MedicalAppointment(**appt_data)
    
    async def cancel_appointment(self, appointment_id: str, reason: Optional[str] = None) -> bool:
        """Cancel an appointment"""
        data = {'reason': reason} if reason else {}
        response = await self._make_request('DELETE', f'/api/appointments/{appointment_id}', data)
        return response.get('success', False)
    
    # ==================== MEASUREMENTS ====================
    
    async def save_measurement(self, patient_id: str, measurement_type: MeasurementType,
                             value: float, unit: str, notes: Optional[str] = None) -> HealthMeasurement:
        """Save a patient measurement"""
        data = {
            'patient_id': patient_id,
            'type': measurement_type.value,
            'value': value,
            'unit': unit,
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        }
        
        response = await self._make_request('POST', '/api/measurements', data)
        
        measurement_data = response['data']
        measurement_data['timestamp'] = datetime.fromisoformat(measurement_data['timestamp'])
        measurement_data['type'] = MeasurementType(measurement_data['type'])
        
        return HealthMeasurement(**measurement_data)
    
    async def get_measurements(self, patient_id: str, 
                             measurement_type: Optional[MeasurementType] = None,
                             days: int = 30) -> List[HealthMeasurement]:
        """Get patient measurements for specified period"""
        endpoint = f'/api/measurements/{patient_id}?days={days}'
        if measurement_type:
            endpoint += f'&type={measurement_type.value}'
        
        response = await self._make_request('GET', endpoint)
        
        measurements = []
        for measurement_data in response['data']:
            measurement_data['timestamp'] = datetime.fromisoformat(measurement_data['timestamp'])
            measurement_data['type'] = MeasurementType(measurement_data['type'])
            measurements.append(HealthMeasurement(**measurement_data))
        
        return measurements
    
    # ==================== REPORTS ====================
    
    async def generate_glucose_report(self, patient_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate glucose trends report"""
        endpoint = f'/api/reports/glucose/{patient_id}?days={days}'
        response = await self._make_request('GET', endpoint)
        return response['data']
    
    async def generate_full_report(self, patient_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        endpoint = f'/api/reports/full/{patient_id}?days={days}'
        response = await self._make_request('GET', endpoint)
        return response['data']
    
    # ==================== FILES & DOCUMENTS ====================
    
    async def get_latest_file(self, patient_id: str, file_type: Optional[str] = None) -> Dict[str, Any]:
        """Get patient's latest file (lab results, prescriptions, etc.)"""
        endpoint = f'/api/files/latest/{patient_id}'
        if file_type:
            endpoint += f'?type={file_type}'
        
        response = await self._make_request('GET', endpoint)
        return response['data']
    
    async def get_invoices(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get patient's invoices"""
        response = await self._make_request('GET', f'/api/invoices/{patient_id}')
        return response['data']


class MockBackendService(BackendIntegrationService):
    """
    Mock implementation for testing and development
    Simulates backend responses without actual HTTP calls
    """
    
    def __init__(self):
        # Skip parent initialization for mock
        self.logger = logging.getLogger(self.__class__.__name__)
        self._mock_data = self._generate_mock_data()
    
    def _generate_mock_data(self) -> Dict[str, Any]:
        """Generate mock data for testing"""
        now = datetime.now()
        return {
            'patients': {
                'patient_123': Patient(
                    id='patient_123',
                    name='Juan Pérez',
                    email='juan.perez@email.com',
                    phone='+5215551234567',
                    date_of_birth=datetime(1980, 5, 15),
                    diabetes_type='Type 2',
                    last_hba1c=7.2
                )
            },
            'appointments': [
                MedicalAppointment(
                    id='appt_001',
                    patient_id='patient_123',
                    specialty='endocrinology',
                    doctor_name='Dra. María González',
                    date=now + timedelta(days=7),
                    status=AppointmentStatus.SCHEDULED,
                    meeting_link='https://meet.drclivi.com/room/appt_001'
                )
            ],
            'measurements': [
                HealthMeasurement(
                    id='meas_001',
                    patient_id='patient_123',
                    type=MeasurementType.GLUCOSE_FASTING,
                    value=125.0,
                    unit='mg/dL',
                    timestamp=now - timedelta(days=1)
                ),
                HealthMeasurement(
                    id='meas_002',
                    patient_id='patient_123',
                    type=MeasurementType.WEIGHT,
                    value=78.5,
                    unit='kg',
                    timestamp=now - timedelta(days=2)
                )
            ]
        }
    
    async def get_patient(self, patient_id: str) -> Patient:
        """Mock: Get patient information"""
        await asyncio.sleep(0.1)  # Simulate network delay
        patient = self._mock_data['patients'].get(patient_id)
        if not patient:
            raise BackendError(f"Patient {patient_id} not found")
        return patient
    
    async def get_patient_appointments(self, patient_id: str, 
                                     status: Optional[AppointmentStatus] = None) -> List[MedicalAppointment]:
        """Mock: Get patient appointments"""
        await asyncio.sleep(0.2)
        appointments = [
            appt for appt in self._mock_data['appointments']
            if appt.patient_id == patient_id
        ]
        
        if status:
            appointments = [appt for appt in appointments if appt.status == status]
        
        return appointments
    
    async def schedule_appointment(self, patient_id: str, specialty: str, 
                                 preferred_date: Optional[datetime] = None) -> MedicalAppointment:
        """Mock: Schedule new appointment"""
        await asyncio.sleep(0.3)
        
        appointment = MedicalAppointment(
            id=f'appt_{len(self._mock_data["appointments"]) + 1:03d}',
            patient_id=patient_id,
            specialty=specialty,
            doctor_name=self._get_doctor_for_specialty(specialty),
            date=preferred_date or (datetime.now() + timedelta(days=14)),
            status=AppointmentStatus.SCHEDULED,
            meeting_link=f'https://meet.drclivi.com/room/new_appt'
        )
        
        self._mock_data['appointments'].append(appointment)
        return appointment
    
    def _get_doctor_for_specialty(self, specialty: str) -> str:
        """Get doctor name based on specialty"""
        doctors = {
            'endocrinology': 'Dra. María González',
            'nutrition': 'Lic. Ana Martínez',
            'psychology': 'Dr. Carlos Ruiz',
            'general': 'Dr. Luis Hernández'
        }
        return doctors.get(specialty, 'Dr. Especialista')
    
    async def save_measurement(self, patient_id: str, measurement_type: MeasurementType,
                             value: float, unit: str, notes: Optional[str] = None) -> HealthMeasurement:
        """Mock: Save measurement"""
        await asyncio.sleep(0.2)
        
        measurement = HealthMeasurement(
            id=f'meas_{len(self._mock_data["measurements"]) + 1:03d}',
            patient_id=patient_id,
            type=measurement_type,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            notes=notes
        )
        
        self._mock_data['measurements'].append(measurement)
        return measurement
    
    async def generate_glucose_report(self, patient_id: str, days: int = 30) -> Dict[str, Any]:
        """Mock: Generate glucose report"""
        await asyncio.sleep(0.5)
        
        glucose_measurements = [
            m for m in self._mock_data['measurements']
            if m.patient_id == patient_id and m.type in [
                MeasurementType.GLUCOSE_FASTING, 
                MeasurementType.GLUCOSE_POST_MEAL
            ]
        ]
        
        return {
            'patient_id': patient_id,
            'period_days': days,
            'total_measurements': len(glucose_measurements),
            'average_fasting': 118.5,
            'average_post_meal': 156.2,
            'in_range_percentage': 78.3,
            'recommendations': [
                "Mantener horarios regulares de medición",
                "Continuar con dieta actual",
                "Revisar medicación con endocrinólogo"
            ],
            'report_url': f'https://reports.drclivi.com/glucose/{patient_id}'
        }
