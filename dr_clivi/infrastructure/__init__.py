"""
Infrastructure Layer - External Dependencies and Data Access
Contains implementations for repositories, database connections, and external services
"""

from .patient_repository import (
    BackendPatientRepository,
    InMemoryPatientRepository
)
from .database import (
    DatabaseConfig,
    DatabaseManager,
    AsyncPGManager,
    Base
)

__all__ = [
    # Repositories
    "BackendPatientRepository",
    "InMemoryPatientRepository",
    
    # Database
    "DatabaseConfig",
    "DatabaseManager", 
    "AsyncPGManager",
    "Base"
]
