"""
Domain Entities - Core Business Objects
Represents the main business entities in the healthcare domain
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from ..core import PatientId


class MeasurementType(Enum):
    """Types of health measurements"""
    GLUCOSE_FASTING = "glucose_fasting"
    GLUCOSE_POST_MEAL = "glucose_post_meal"
    WEIGHT = "weight"
    WAIST = "waist"
    HIP = "hip"
    NECK = "neck"
    BLOOD_PRESSURE_SYSTOLIC = "systolic_bp"
    BLOOD_PRESSURE_DIASTOLIC = "diastolic_bp"


class AppointmentStatus(Enum):
    """Appointment status values"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class PatientPlan(Enum):
    """Patient subscription plans"""
    BASIC = "basic"
    PLUS = "plus"
    PRO = "pro"
    CLUB = "club"


@dataclass
class Patient:
    """
    Patient domain entity
    Represents a patient in the Dr. Clivi system
    """
    id: PatientId
    name_display: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[str] = None
    plan: PatientPlan = PatientPlan.BASIC
    plan_status: str = "ACTIVE"
    diabetes_type: Optional[str] = None
    last_hba1c: Optional[float] = None
    emergency_contact: Optional[str] = None
    preferred_language: str = "es"
    timezone: str = "America/Mexico_City"
    registration_date: Optional[str] = None
    last_activity_date: Optional[str] = None
    
    def is_plan_active(self) -> bool:
        """Check if patient's plan is active"""
        return self.plan_status == "ACTIVE"
    
    def has_premium_features(self) -> bool:
        """Check if patient has access to premium features"""
        return self.plan in [PatientPlan.PRO, PatientPlan.CLUB]
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get patient information for display"""
        return {
            "name": self.name_display,
            "plan": self.plan.value.upper(),
            "plan_status": self.plan_status,
            "diabetes_type": self.diabetes_type,
            "language": self.preferred_language
        }


@dataclass
class HealthMeasurement:
    """
    Health measurement domain entity
    Represents a single health measurement taken by a patient
    """
    id: Optional[str]
    patient_id: PatientId
    measurement_type: MeasurementType
    value: float
    unit: str
    timestamp: str
    notes: Optional[str] = None
    validated: bool = False
    validation_result: Optional[Dict[str, Any]] = None
    emergency_flagged: bool = False
    
    def mark_as_validated(self, validation_result: Dict[str, Any]):
        """Mark measurement as validated with results"""
        self.validated = True
        self.validation_result = validation_result
        
        # Check if emergency was flagged
        if validation_result.get("severity") == "emergency":
            self.emergency_flagged = True
    
    def is_normal_range(self) -> bool:
        """Check if measurement is in normal range"""
        if not self.validated or not self.validation_result:
            return False
        
        return self.validation_result.get("category") == "normal"
    
    def get_clinical_interpretation(self) -> str:
        """Get clinical interpretation of the measurement"""
        if not self.validated or not self.validation_result:
            return "Pendiente de validación"
        
        return self.validation_result.get("status", "Sin interpretación")


@dataclass
class MedicalAppointment:
    """
    Medical appointment domain entity
    Represents a scheduled appointment between patient and healthcare provider
    """
    id: str
    patient_id: PatientId
    specialty: str
    doctor_name: str
    scheduled_date: str
    status: AppointmentStatus
    is_virtual: bool = True
    meeting_link: Optional[str] = None
    duration_minutes: int = 30
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def can_be_cancelled(self) -> bool:
        """Check if appointment can be cancelled"""
        return self.status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
    
    def can_be_rescheduled(self) -> bool:
        """Check if appointment can be rescheduled"""
        return self.status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
    
    def cancel(self, reason: Optional[str] = None):
        """Cancel the appointment"""
        if not self.can_be_cancelled():
            raise ValueError(f"Cannot cancel appointment with status: {self.status.value}")
        
        self.status = AppointmentStatus.CANCELLED
        self.cancellation_reason = reason
        self.updated_at = datetime.now().isoformat()
    
    def confirm(self):
        """Confirm the appointment"""
        if self.status != AppointmentStatus.SCHEDULED:
            raise ValueError(f"Cannot confirm appointment with status: {self.status.value}")
        
        self.status = AppointmentStatus.CONFIRMED
        self.updated_at = datetime.now().isoformat()
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get appointment information for display"""
        return {
            "id": self.id,
            "specialty": self.specialty,
            "doctor": self.doctor_name,
            "date": self.scheduled_date,
            "status": self.status.value,
            "is_virtual": self.is_virtual,
            "meeting_link": self.meeting_link,
            "duration": self.duration_minutes
        }


@dataclass
class PatientSession:
    """
    Patient session domain entity
    Represents an interaction session between patient and the system
    """
    session_id: str
    patient_id: PatientId
    channel: str  # "telegram", "whatsapp", etc.
    started_at: str
    last_activity: str
    current_flow: Optional[str] = None
    current_page: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now().isoformat()
    
    def add_interaction(self, interaction_type: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add interaction to conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "content": content,
            "metadata": metadata or {}
        })
        self.update_activity()
    
    def set_current_context(self, flow: str, page: str):
        """Set current navigation context"""
        self.current_flow = flow
        self.current_page = page
        self.update_activity()
    
    def get_session_duration_minutes(self) -> float:
        """Calculate session duration in minutes"""
        start = datetime.fromisoformat(self.started_at.replace('Z', '+00:00'))
        last = datetime.fromisoformat(self.last_activity.replace('Z', '+00:00'))
        return (last - start).total_seconds() / 60


@dataclass
class MedicalReport:
    """
    Medical report domain entity
    Represents a generated health report for a patient
    """
    id: str
    patient_id: PatientId
    report_type: str  # "glucose", "full", "weight", etc.
    generated_at: str
    period_days: int
    data_points: int
    metrics: Dict[str, Any]
    recommendations: List[str]
    report_url: Optional[str] = None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get report summary for display"""
        return {
            "type": self.report_type,
            "period": f"{self.period_days} días",
            "data_points": self.data_points,
            "generated": self.generated_at,
            "url": self.report_url
        }
