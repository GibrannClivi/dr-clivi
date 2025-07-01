"""
Domain Services - Medical Validation Logic
Implements business rules for health data validation
Follows Single Responsibility Principle
"""

from typing import Dict, Any
from ..core import IHealthValidator, ValidationError, EmergencyValueError


class MedicalValidationService(IHealthValidator):
    """
    Service for validating medical measurements according to clinical guidelines
    Implements domain-specific business rules
    """
    
    # Clinical reference ranges
    GLUCOSE_RANGES = {
        "fasting": {
            "normal": (70, 100),
            "prediabetes": (100, 125),
            "diabetes": (126, float('inf')),
            "emergency_low": 70,
            "emergency_high": 300
        },
        "post_meal": {
            "normal": (80, 140),
            "prediabetes": (140, 199),
            "diabetes": (200, float('inf')),
            "emergency_low": 70,
            "emergency_high": 300
        }
    }
    
    WEIGHT_RANGES = {
        "underweight": (0, 18.5),
        "normal": (18.5, 24.9),
        "overweight": (25, 29.9),
        "obese": (30, float('inf')),
        "emergency_low": 40,  # kg
        "emergency_high": 300  # kg
    }
    
    def validate_glucose_reading(self, value: float, measurement_type: str) -> Dict[str, Any]:
        """
        Validate glucose measurement and provide medical interpretation
        
        Args:
            value: Glucose value in mg/dL
            measurement_type: 'fasting' or 'post_meal'
            
        Returns:
            Dict with validation result, medical interpretation, and recommendations
        """
        if value <= 0:
            raise ValidationError("Glucose value must be positive", "glucose", value)
        
        # Check for emergency values
        if self.is_emergency_value("glucose", value):
            raise EmergencyValueError("glucose", value, 
                                    self.GLUCOSE_RANGES[measurement_type]["emergency_high"])
        
        ranges = self.GLUCOSE_RANGES.get(measurement_type, self.GLUCOSE_RANGES["fasting"])
        
        # Determine clinical category
        if value < ranges["normal"][0]:
            category = "low"
            status = "⚠️ Hipoglucemia"
            recommendation = "Consume carbohidratos de acción rápida y contacte a su médico"
            severity = "warning"
        elif ranges["normal"][0] <= value <= ranges["normal"][1]:
            category = "normal"
            status = "✅ Normal"
            recommendation = "Excelente control. Continúe con su plan actual"
            severity = "success"
        elif ranges["prediabetes"][0] <= value <= ranges["prediabetes"][1]:
            category = "prediabetes"
            status = "⚠️ Prediabetes"
            recommendation = "Considere ajustar dieta y ejercicio. Consulte con su médico"
            severity = "warning"
        else:
            category = "diabetes"
            status = "🔴 Diabetes/Hiperglucemia"
            recommendation = "Contacte a su médico. Revise medicación y dieta"
            severity = "danger"
        
        return {
            "is_valid": True,
            "value": value,
            "unit": "mg/dL",
            "category": category,
            "status": status,
            "recommendation": recommendation,
            "severity": severity,
            "reference_range": ranges["normal"],
            "measurement_type": measurement_type
        }
    
    def validate_weight(self, value: float) -> Dict[str, Any]:
        """
        Validate weight measurement
        
        Args:
            value: Weight in kg
            
        Returns:
            Dict with validation result and BMI category (if height available)
        """
        if value <= 0:
            raise ValidationError("Weight must be positive", "weight", value)
        
        if self.is_emergency_value("weight", value):
            if value < self.WEIGHT_RANGES["emergency_low"]:
                raise EmergencyValueError("weight", value, self.WEIGHT_RANGES["emergency_low"])
            else:
                raise EmergencyValueError("weight", value, self.WEIGHT_RANGES["emergency_high"])
        
        # Basic weight validation
        if value < 30:
            status = "⚠️ Peso muy bajo"
            recommendation = "Consulte con un nutriólogo"
            severity = "warning"
        elif value > 200:
            status = "⚠️ Peso elevado"
            recommendation = "Considere plan de control de peso con especialista"
            severity = "warning"
        else:
            status = "✅ Peso registrado"
            recommendation = "Mantenga hábitos saludables"
            severity = "success"
        
        return {
            "is_valid": True,
            "value": value,
            "unit": "kg",
            "status": status,
            "recommendation": recommendation,
            "severity": severity
        }
    
    def is_emergency_value(self, measurement_type: str, value: float) -> bool:
        """
        Check if a measurement value indicates a medical emergency
        
        Args:
            measurement_type: Type of measurement
            value: Measurement value
            
        Returns:
            True if emergency, False otherwise
        """
        if measurement_type == "glucose":
            return (value < 70 or value > 300)
        elif measurement_type == "weight":
            return (value < 40 or value > 300)
        elif measurement_type in ["systolic_bp"]:
            return (value < 70 or value > 180)
        elif measurement_type in ["diastolic_bp"]:
            return (value < 40 or value > 120)
        
        return False
    
    def get_measurement_insights(self, measurements: list, measurement_type: str) -> Dict[str, Any]:
        """
        Analyze trends in measurement history and provide insights
        
        Args:
            measurements: List of recent measurements
            measurement_type: Type of measurement
            
        Returns:
            Dict with trend analysis and recommendations
        """
        if not measurements:
            return {"trend": "insufficient_data", "message": "Necesita más mediciones para análisis"}
        
        values = [m.get("value") for m in measurements if m.get("value")]
        
        if len(values) < 2:
            return {"trend": "insufficient_data", "message": "Necesita más mediciones para análisis"}
        
        # Calculate trend
        recent_avg = sum(values[-3:]) / len(values[-3:])
        older_avg = sum(values[:-3]) / len(values[:-3]) if len(values) > 3 else values[0]
        
        if recent_avg > older_avg * 1.1:
            trend = "increasing"
            trend_message = "📈 Tendencia al alza"
        elif recent_avg < older_avg * 0.9:
            trend = "decreasing"
            trend_message = "📉 Tendencia a la baja"
        else:
            trend = "stable"
            trend_message = "📊 Estable"
        
        return {
            "trend": trend,
            "trend_message": trend_message,
            "recent_average": round(recent_avg, 1),
            "total_measurements": len(values),
            "recommendation": self._get_trend_recommendation(trend, measurement_type)
        }
    
    def _get_trend_recommendation(self, trend: str, measurement_type: str) -> str:
        """Get recommendation based on trend analysis"""
        recommendations = {
            "glucose": {
                "increasing": "Considere revisar dieta y medicación con su médico",
                "decreasing": "Buen progreso, continúe con el plan actual",
                "stable": "Mantenga sus hábitos actuales"
            },
            "weight": {
                "increasing": "Considere ajustar plan nutricional",
                "decreasing": "Buen progreso en control de peso",
                "stable": "Peso estable, continúe con hábitos actuales"
            }
        }
        
        return recommendations.get(measurement_type, {}).get(trend, "Continúe monitoreando")


class AppointmentDomainService:
    """
    Domain service for appointment business logic
    Implements rules for appointment scheduling and management
    """
    
    SPECIALTY_SCHEDULING_RULES = {
        "endocrinology": {
            "min_advance_days": 1,
            "max_advance_days": 90,
            "duration_minutes": 45,
            "follow_up_interval_days": 90
        },
        "nutrition": {
            "min_advance_days": 1,
            "max_advance_days": 60,
            "duration_minutes": 30,
            "follow_up_interval_days": 30
        },
        "psychology": {
            "min_advance_days": 1,
            "max_advance_days": 30,
            "duration_minutes": 60,
            "follow_up_interval_days": 14
        },
        "general": {
            "min_advance_days": 0,
            "max_advance_days": 30,
            "duration_minutes": 20,
            "follow_up_interval_days": 30
        }
    }
    
    def validate_appointment_request(self, specialty: str, requested_date: str = None) -> Dict[str, Any]:
        """
        Validate appointment scheduling request according to business rules
        
        Args:
            specialty: Medical specialty
            requested_date: Preferred date (optional)
            
        Returns:
            Validation result with scheduling recommendations
        """
        rules = self.SPECIALTY_SCHEDULING_RULES.get(specialty, self.SPECIALTY_SCHEDULING_RULES["general"])
        
        return {
            "is_valid": True,
            "specialty": specialty,
            "rules": rules,
            "estimated_duration": rules["duration_minutes"],
            "next_available": "Se asignará próxima fecha disponible",
            "advance_notice": f"Mínimo {rules['min_advance_days']} días de anticipación"
        }
    
    def can_cancel_appointment(self, appointment_date: str, current_date: str) -> tuple[bool, str]:
        """
        Check if appointment can be cancelled based on business rules
        
        Returns:
            Tuple of (can_cancel, reason)
        """
        # Simplified logic - in real implementation would parse dates
        return True, "Cancelación permitida con 24 horas de anticipación"
