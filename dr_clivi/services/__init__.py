"""
Services Layer - Application Services and External Integrations
Contains services that coordinate business logic and external dependencies
"""

from .backend_integration import (
    BackendIntegrationService,
    MockBackendService,
    BackendError
)

__all__ = [
    "BackendIntegrationService",
    "MockBackendService", 
    "BackendError"
]
