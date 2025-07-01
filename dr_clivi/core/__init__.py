"""
Core module initialization
Exports main interfaces and exceptions
"""

from .interfaces import (
    # Value Objects
    PatientId,
    SessionId,
    HealthMeasurement,
    Appointment,
    UserMessage,
    BotResponse,
    
    # Repository Interfaces
    IPatientRepository,
    IMeasurementRepository,
    IAppointmentRepository,
    
    # Service Interfaces
    IPatientService,
    IAppointmentService,
    IMeasurementService,
    
    # Component Interfaces
    IMessageRenderer,
    IPageRouter,
    IAgentTool,
    IHealthValidator,
    INotificationService,
    IReportGenerator,
    IBackendClient,
    
    # Protocols
    Renderable,
    Validatable,
)

from .exceptions import (
    DrCliviException,
    ValidationError,
    PatientNotFoundError,
    AppointmentError,
    MeasurementError,
    BackendConnectionError,
    EmergencyValueError,
    PageNavigationError,
    ToolExecutionError,
)

__all__ = [
    # Value Objects
    "PatientId",
    "SessionId", 
    "HealthMeasurement",
    "Appointment",
    "UserMessage",
    "BotResponse",
    
    # Repository Interfaces
    "IPatientRepository",
    "IMeasurementRepository", 
    "IAppointmentRepository",
    
    # Service Interfaces
    "IPatientService",
    "IAppointmentService",
    "IMeasurementService",
    
    # Component Interfaces
    "IMessageRenderer",
    "IPageRouter",
    "IAgentTool",
    "IHealthValidator",
    "INotificationService",
    "IReportGenerator",
    "IBackendClient",
    
    # Protocols
    "Renderable",
    "Validatable",
    
    # Exceptions
    "DrCliviException",
    "ValidationError",
    "PatientNotFoundError",
    "AppointmentError",
    "MeasurementError",
    "BackendConnectionError",
    "EmergencyValueError",
    "PageNavigationError",
    "ToolExecutionError",
]
