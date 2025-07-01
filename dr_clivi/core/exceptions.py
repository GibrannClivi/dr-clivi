"""
Core Exceptions and Error Handling
Centralized exception handling for the Dr. Clivi application
"""

class DrCliviException(Exception):
    """Base exception for all Dr. Clivi specific errors"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(DrCliviException):
    """Raised when data validation fails"""
    
    def __init__(self, message: str, field: str = None, value: any = None):
        super().__init__(message, "VALIDATION_ERROR", {"field": field, "value": value})


class PatientNotFoundError(DrCliviException):
    """Raised when patient is not found"""
    
    def __init__(self, patient_id: str):
        super().__init__(f"Patient not found: {patient_id}", "PATIENT_NOT_FOUND", {"patient_id": patient_id})


class AppointmentError(DrCliviException):
    """Raised when appointment operations fail"""
    pass


class MeasurementError(DrCliviException):
    """Raised when measurement operations fail"""
    pass


class BackendConnectionError(DrCliviException):
    """Raised when backend connection fails"""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message, "BACKEND_ERROR", {"status_code": status_code})


class EmergencyValueError(DrCliviException):
    """Raised when a health measurement indicates emergency"""
    
    def __init__(self, measurement_type: str, value: float, threshold: float):
        message = f"Emergency value detected: {measurement_type}={value} (threshold: {threshold})"
        super().__init__(message, "EMERGENCY_VALUE", {
            "measurement_type": measurement_type,
            "value": value,
            "threshold": threshold
        })


class BackendError(DrCliviException):
    """Raised when backend integration fails"""
    
    def __init__(self, message: str, endpoint: str = None, status_code: int = None):
        super().__init__(message, "BACKEND_ERROR", {
            "endpoint": endpoint, 
            "status_code": status_code
        })


class PageNavigationError(DrCliviException):
    """Raised when page navigation fails"""
    pass


class ToolExecutionError(DrCliviException):
    """Raised when agent tool execution fails"""
    pass
