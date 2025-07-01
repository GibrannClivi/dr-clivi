# Copyright 2025 Clivi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Dr. Clivi - Multi-Agent Healthcare Assistant
Migrated from Dialogflow CX to ADK for enhanced agent orchestration

Modular Architecture with SOLID Principles:
- Core: Interfaces, exceptions, and value objects
- Domain: Business entities and domain services  
- Application: Application services and use cases
- Infrastructure: Data access and external services
- Presentation: UI rendering and formatting
- Flows: Conversation flows and page definitions
- Shared: Common utilities and helpers
"""

__version__ = "0.1.0"

# Core exports for easy access
from .core.interfaces import (
    PatientId,
    SessionId,
    IPatientRepository,
    IPatientService,
    ISessionService
)
from .core.exceptions import (
    DrCliviException,
    ValidationError,
    PatientNotFoundError,
    BackendError
)

# Main application components
from .application import (
    PatientService,
    SessionService,
    PageRouter
)

# Domain entities
from .domain import (
    Patient,
    HealthMeasurement,
    MedicalAppointment,
    MeasurementType,
    AppointmentStatus,
    PatientPlan
)

# Infrastructure
from .infrastructure import (
    BackendPatientRepository,
    InMemoryPatientRepository,
    DatabaseConfig
)

# Services
from .services import (
    BackendIntegrationService,
    MockBackendService
)

# Utilities
from .shared import (
    DateTimeUtils,
    ValidationUtils,
    ValidationResult
)

__all__ = [
    # Core
    "PatientId",
    "SessionId", 
    "IPatientRepository",
    "IPatientService",
    "ISessionService",
    "DrCliviException",
    "ValidationError",
    "PatientNotFoundError",
    "BackendError",
    
    # Application
    "PatientService",
    "SessionService",
    "PageRouter",
    
    # Domain
    "Patient",
    "HealthMeasurement", 
    "MedicalAppointment",
    "MeasurementType",
    "AppointmentStatus",
    "PatientPlan",
    
    # Infrastructure
    "BackendPatientRepository",
    "InMemoryPatientRepository",
    "DatabaseConfig",
    
    # Services
    "BackendIntegrationService",
    "MockBackendService",
    
    # Utilities
    "DateTimeUtils",
    "ValidationUtils",
    "ValidationResult"
]
__author__ = "Clivi Team"
