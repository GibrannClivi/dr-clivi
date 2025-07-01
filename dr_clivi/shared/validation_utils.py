"""
Validation Utilities
Common validation functions and decorators
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation operation"""
    is_valid: bool
    message: str = ""
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ValidationUtils:
    """Utility class for common validation operations"""
    
    # Regular expressions for common validations
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_MEXICO_REGEX = re.compile(r'^(\+52)?[1-9]\d{9}$')
    WHATSAPP_REGEX = re.compile(r'^521\d{10}$')
    
    @classmethod
    def validate_email(cls, email: str) -> ValidationResult:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return ValidationResult(False, "Email is required")
        
        email = email.strip().lower()
        if not cls.EMAIL_REGEX.match(email):
            return ValidationResult(False, "Invalid email format")
        
        return ValidationResult(True, "Valid email")
    
    @classmethod
    def validate_phone_mexico(cls, phone: str) -> ValidationResult:
        """Validate Mexican phone number"""
        if not phone or not isinstance(phone, str):
            return ValidationResult(False, "Phone number is required")
        
        # Clean phone number
        phone = re.sub(r'[^\d+]', '', phone)
        
        if not cls.PHONE_MEXICO_REGEX.match(phone):
            return ValidationResult(
                False, 
                "Invalid Mexican phone number format. Use +521234567890 or 1234567890"
            )
        
        return ValidationResult(True, "Valid Mexican phone number")
    
    @classmethod
    def validate_whatsapp_number(cls, whatsapp: str) -> ValidationResult:
        """Validate WhatsApp number format"""
        if not whatsapp or not isinstance(whatsapp, str):
            return ValidationResult(False, "WhatsApp number is required")
        
        # Clean number
        whatsapp = re.sub(r'[^\d]', '', whatsapp)
        
        # Add 521 prefix if missing
        if len(whatsapp) == 10:
            whatsapp = "521" + whatsapp
        
        if not cls.WHATSAPP_REGEX.match(whatsapp):
            return ValidationResult(False, "Invalid WhatsApp number format")
        
        return ValidationResult(True, "Valid WhatsApp number")
    
    @classmethod
    def validate_patient_id(cls, patient_id: str) -> ValidationResult:
        """Validate patient ID format"""
        if not patient_id or not isinstance(patient_id, str):
            return ValidationResult(False, "Patient ID is required")
        
        patient_id = patient_id.strip()
        
        # Check length (assuming 8-20 characters)
        if len(patient_id) < 8 or len(patient_id) > 20:
            return ValidationResult(False, "Patient ID must be between 8 and 20 characters")
        
        # Check alphanumeric
        if not re.match(r'^[a-zA-Z0-9_-]+$', patient_id):
            return ValidationResult(False, "Patient ID can only contain letters, numbers, underscore and dash")
        
        return ValidationResult(True, "Valid patient ID")
    
    @classmethod
    def validate_numeric_range(cls, value: Union[int, float], 
                             min_val: Optional[Union[int, float]] = None,
                             max_val: Optional[Union[int, float]] = None,
                             field_name: str = "Value") -> ValidationResult:
        """Validate numeric value within range"""
        if value is None:
            return ValidationResult(False, f"{field_name} is required")
        
        if not isinstance(value, (int, float)):
            return ValidationResult(False, f"{field_name} must be a number")
        
        if min_val is not None and value < min_val:
            return ValidationResult(False, f"{field_name} must be at least {min_val}")
        
        if max_val is not None and value > max_val:
            return ValidationResult(False, f"{field_name} must be at most {max_val}")
        
        return ValidationResult(True, f"Valid {field_name}")
    
    @classmethod
    def validate_string_length(cls, text: str, 
                             min_length: Optional[int] = None,
                             max_length: Optional[int] = None,
                             field_name: str = "Text") -> ValidationResult:
        """Validate string length"""
        if text is None:
            return ValidationResult(False, f"{field_name} is required")
        
        if not isinstance(text, str):
            return ValidationResult(False, f"{field_name} must be text")
        
        text = text.strip()
        length = len(text)
        
        if min_length is not None and length < min_length:
            return ValidationResult(False, f"{field_name} must be at least {min_length} characters")
        
        if max_length is not None and length > max_length:
            return ValidationResult(False, f"{field_name} must be at most {max_length} characters")
        
        return ValidationResult(True, f"Valid {field_name}")
    
    @classmethod
    def validate_required_fields(cls, data: Dict[str, Any], 
                                required_fields: List[str]) -> ValidationResult:
        """Validate that required fields are present"""
        errors = []
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                errors.append(f"{field} is required")
        
        if errors:
            return ValidationResult(False, "Missing required fields", errors)
        
        return ValidationResult(True, "All required fields present")
    
    @classmethod
    def sanitize_text_input(cls, text: str, max_length: int = 1000) -> str:
        """Sanitize user text input"""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove potentially dangerous characters (basic sanitization)
        text = re.sub(r'[<>\"\'&]', '', text)
        
        return text
    
    @classmethod
    def validate_measurement_value(cls, measurement_type: str, value: float) -> ValidationResult:
        """Validate measurement values based on type"""
        validation_rules = {
            'glucose_fasting': {'min': 50, 'max': 400, 'unit': 'mg/dL'},
            'glucose_post_meal': {'min': 50, 'max': 500, 'unit': 'mg/dL'},
            'weight': {'min': 20, 'max': 300, 'unit': 'kg'},
            'waist': {'min': 50, 'max': 200, 'unit': 'cm'},
            'hip': {'min': 50, 'max': 200, 'unit': 'cm'},
            'neck': {'min': 20, 'max': 60, 'unit': 'cm'},
            'systolic_bp': {'min': 70, 'max': 250, 'unit': 'mmHg'},
            'diastolic_bp': {'min': 40, 'max': 150, 'unit': 'mmHg'}
        }
        
        rules = validation_rules.get(measurement_type)
        if not rules:
            return ValidationResult(False, f"Unknown measurement type: {measurement_type}")
        
        return cls.validate_numeric_range(
            value, 
            rules['min'], 
            rules['max'], 
            f"{measurement_type} ({rules['unit']})"
        )


def validate_input(validator_func: Callable) -> Callable:
    """Decorator to validate function inputs"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Apply validation
            validation_result = validator_func(*args, **kwargs)
            if not validation_result.is_valid:
                raise ValueError(validation_result.message)
            
            # Call original function
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_fields(*required_fields: str) -> Callable:
    """Decorator to require specific fields in kwargs"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            validation_result = ValidationUtils.validate_required_fields(
                kwargs, list(required_fields)
            )
            if not validation_result.is_valid:
                raise ValueError(validation_result.message)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
