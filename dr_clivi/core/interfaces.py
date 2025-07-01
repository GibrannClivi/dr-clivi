"""
Core Interfaces and Abstractions
Defines contracts that must be implemented by concrete classes
Follows Interface Segregation Principle (ISP) and Dependency Inversion Principle (DIP)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# Value Objects and Data Transfer Objects
# =============================================================================

@dataclass(frozen=True)
class PatientId:
    """Value object for patient identification"""
    value: str
    
    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("PatientId must be a non-empty string")


@dataclass(frozen=True)
class SessionId:
    """Value object for session identification"""
    value: str
    
    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("SessionId must be a non-empty string")


@dataclass
class HealthMeasurement:
    """Domain entity for health measurements"""
    patient_id: PatientId
    measurement_type: str
    value: float
    unit: str
    timestamp: str
    notes: Optional[str] = None


@dataclass
class Appointment:
    """Domain entity for medical appointments"""
    id: str
    patient_id: PatientId
    specialty: str
    doctor_name: str
    date: str
    status: str
    is_virtual: bool = True
    meeting_link: Optional[str] = None


@dataclass
class UserMessage:
    """Domain entity for user messages"""
    user_id: str
    content: str
    timestamp: str
    message_type: str = "text"


@dataclass
class BotResponse:
    """Domain entity for bot responses"""
    content: str
    response_type: str
    metadata: Dict[str, Any]


# =============================================================================
# Core Interfaces (Following ISP - Interface Segregation Principle)
# =============================================================================

class IPatientRepository(ABC):
    """Repository interface for patient data persistence"""
    
    @abstractmethod
    async def get_patient(self, patient_id: PatientId) -> Optional[Dict[str, Any]]:
        """Retrieve patient by ID"""
        pass
    
    @abstractmethod
    async def save_patient(self, patient_data: Dict[str, Any]) -> bool:
        """Save or update patient data"""
        pass


class IMeasurementRepository(ABC):
    """Repository interface for health measurements"""
    
    @abstractmethod
    async def save_measurement(self, measurement: HealthMeasurement) -> bool:
        """Save a health measurement"""
        pass
    
    @abstractmethod
    async def get_measurements(self, patient_id: PatientId, 
                             measurement_type: Optional[str] = None) -> List[HealthMeasurement]:
        """Get measurements for a patient"""
        pass


class IAppointmentRepository(ABC):
    """Repository interface for appointments"""
    
    @abstractmethod
    async def get_appointments(self, patient_id: PatientId) -> List[Appointment]:
        """Get patient appointments"""
        pass
    
    @abstractmethod
    async def schedule_appointment(self, appointment: Appointment) -> bool:
        """Schedule a new appointment"""
        pass
    
    @abstractmethod
    async def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment"""
        pass


class IMessageRenderer(ABC):
    """Interface for rendering messages in different formats"""
    
    @abstractmethod
    def render_menu(self, menu_data: Dict[str, Any]) -> BotResponse:
        """Render a menu for the user"""
        pass
    
    @abstractmethod
    def render_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> BotResponse:
        """Render plain text response"""
        pass


class IPageRouter(ABC):
    """Interface for page navigation and routing"""
    
    @abstractmethod
    def get_next_page(self, current_page: str, user_selection: str) -> Optional[str]:
        """Determine next page based on current page and user selection"""
        pass
    
    @abstractmethod
    def validate_transition(self, from_page: str, to_page: str) -> bool:
        """Validate if transition between pages is allowed"""
        pass


class IAgentTool(ABC):
    """Interface for agent tools (following Single Responsibility Principle)"""
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute the tool with given context"""
        pass
    
    @abstractmethod
    def get_tool_name(self) -> str:
        """Get the name of this tool"""
        pass
    
    @abstractmethod
    def get_tool_description(self) -> str:
        """Get description of what this tool does"""
        pass


class IHealthValidator(ABC):
    """Interface for health data validation"""
    
    @abstractmethod
    def validate_glucose_reading(self, value: float, measurement_type: str) -> Dict[str, Any]:
        """Validate glucose measurement and provide medical feedback"""
        pass
    
    @abstractmethod
    def validate_weight(self, value: float) -> Dict[str, Any]:
        """Validate weight measurement"""
        pass
    
    @abstractmethod
    def is_emergency_value(self, measurement_type: str, value: float) -> bool:
        """Check if measurement indicates medical emergency"""
        pass


class INotificationService(ABC):
    """Interface for sending notifications"""
    
    @abstractmethod
    async def send_appointment_reminder(self, patient_id: PatientId, appointment: Appointment) -> bool:
        """Send appointment reminder"""
        pass
    
    @abstractmethod
    async def send_emergency_alert(self, patient_id: PatientId, measurement: HealthMeasurement) -> bool:
        """Send emergency alert for critical measurements"""
        pass


class IReportGenerator(ABC):
    """Interface for generating medical reports"""
    
    @abstractmethod
    async def generate_glucose_report(self, patient_id: PatientId, days: int = 30) -> Dict[str, Any]:
        """Generate glucose trends report"""
        pass
    
    @abstractmethod
    async def generate_full_report(self, patient_id: PatientId, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        pass


class IBackendClient(ABC):
    """Interface for backend communication (Dependency Inversion Principle)"""
    
    @abstractmethod
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request to backend"""
        pass
    
    @abstractmethod
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to backend"""
        pass
    
    @abstractmethod
    async def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PUT request to backend"""
        pass
    
    @abstractmethod
    async def delete(self, endpoint: str) -> bool:
        """Make DELETE request to backend"""
        pass


# =============================================================================
# Service Interfaces (Application Layer Contracts)
# =============================================================================

class IPatientService(ABC):
    """Service interface for patient operations"""
    
    @abstractmethod
    async def get_patient_profile(self, patient_id: PatientId) -> Dict[str, Any]:
        """Get complete patient profile"""
        pass
    
    @abstractmethod
    async def update_patient_info(self, patient_id: PatientId, updates: Dict[str, Any]) -> bool:
        """Update patient information"""
        pass


class IAppointmentService(ABC):
    """Service interface for appointment management"""
    
    @abstractmethod
    async def schedule_appointment(self, patient_id: PatientId, specialty: str, 
                                 preferred_date: Optional[str] = None) -> Appointment:
        """Schedule a new appointment"""
        pass
    
    @abstractmethod
    async def get_patient_appointments(self, patient_id: PatientId) -> List[Appointment]:
        """Get all patient appointments"""
        pass
    
    @abstractmethod
    async def cancel_appointment(self, appointment_id: str, reason: Optional[str] = None) -> bool:
        """Cancel an appointment"""
        pass


class IMeasurementService(ABC):
    """Service interface for health measurements"""
    
    @abstractmethod
    async def record_measurement(self, patient_id: PatientId, measurement_type: str,
                               value: float, unit: str) -> Dict[str, Any]:
        """Record a health measurement with validation"""
        pass
    
    @abstractmethod
    async def get_measurement_history(self, patient_id: PatientId, 
                                    measurement_type: Optional[str] = None) -> List[HealthMeasurement]:
        """Get measurement history for patient"""
        pass


class ISessionService(ABC):
    """Service interface for session management"""
    
    @abstractmethod
    def create_session(self, session_id: SessionId, patient_id: Optional[PatientId] = None,
                      platform: str = "whatsapp") -> Any:
        """Create a new user session"""
        pass
    
    @abstractmethod
    def get_session(self, session_id: SessionId) -> Optional[Any]:
        """Get existing session by ID"""
        pass
    
    @abstractmethod
    def update_session_state(self, session_id: SessionId, current_page: str,
                           context_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update session conversation state"""
        pass
    
    @abstractmethod
    def end_session(self, session_id: SessionId) -> bool:
        """End and remove session"""
        pass


# =============================================================================
# Protocol Definitions (Structural Typing)
# =============================================================================

class Renderable(Protocol):
    """Protocol for objects that can be rendered"""
    
    def render(self, context: Dict[str, Any]) -> BotResponse:
        """Render the object to a bot response"""
        ...


class Validatable(Protocol):
    """Protocol for objects that can be validated"""
    
    def validate(self) -> bool:
        """Validate the object"""
        ...
    
    def get_validation_errors(self) -> List[str]:
        """Get validation error messages"""
        ...
