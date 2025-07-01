"""
Modern Diabetes Agent - Refactored for SOLID Architecture
Leverages the new modular structure for better maintainability and testing
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from .base_agent import BaseCliviAgent, SessionContext, PatientContext, tool
from ..config import Config

# New modular imports using SOLID architecture
from ..core.interfaces import IPatientService, ISessionService, PatientId, SessionId
from ..core.exceptions import DrCliviException, ValidationError, PatientNotFoundError
from ..domain.entities import (
    Patient, 
    HealthMeasurement, 
    MedicalAppointment,
    MeasurementType,
    AppointmentStatus
)
from ..application import PatientService, SessionService
from ..infrastructure import InMemoryPatientRepository, BackendPatientRepository
from ..domain.medical_validation import MedicalValidationService
from ..shared import DateTimeUtils, ValidationUtils


class ModernDiabetesAgent(BaseCliviAgent):
    """
    Modernized Diabetes Agent using SOLID architecture
    
    Benefits of new architecture:
    - Clean separation of concerns
    - Easy testing with dependency injection
    - Extensible through interfaces
    - Consistent error handling
    - Reusable business logic
    """
    
    def __init__(self, config: Config, use_mock_backend: bool = True):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Dependency injection using SOLID principles
        self._setup_services(use_mock_backend)
    
    def _setup_services(self, use_mock_backend: bool):
        """Initialize services using dependency injection"""
        try:
            # Repository layer (Infrastructure)
            if use_mock_backend:
                self.patient_repository = InMemoryPatientRepository()
            else:
                # Real backend integration
                from ..services import BackendIntegrationService
                backend_service = BackendIntegrationService(
                    base_url=self.config.backend.base_url,
                    api_key=self.config.backend.api_key
                )
                self.patient_repository = BackendPatientRepository(backend_service)
            
            # Domain services
            self.medical_validator = MedicalValidationService()
            
            # Application services  
            self.patient_service = PatientService(
                self.patient_repository,
                self.medical_validator
            )
            self.session_service = SessionService()
            
            self.logger.info("Services initialized successfully with SOLID architecture")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {e}")
            raise DrCliviException(f"Service initialization failed: {e}")
    
    def get_agent_name(self) -> str:
        return "ModernDiabetesAgent"
    
    def get_system_instructions(self) -> str:
        return """
        Eres Dr. Clivi, un asistente médico especializado en diabetes usando arquitectura moderna.
        
        CAPACIDADES MEJORADAS:
        - Validación médica robusta
        - Gestión de sesiones avanzada  
        - Integración backend confiable
        - Manejo de errores consistente
        - Logging estructurado
        """
    
    # =============================================================================
    # GLUCOSE MANAGEMENT - Using new architecture
    # =============================================================================
    
    @tool
    async def log_glucose_fasting(
        self, 
        session: SessionContext, 
        glucose_value: float,
        measurement_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log fasting glucose using modern architecture
        
        Benefits:
        - Domain validation ensures medical accuracy
        - Repository pattern enables easy testing
        - Consistent error handling
        - Automatic emergency detection
        """
        try:
            # Convert session to domain objects
            patient_id = PatientId(session.patient.patient_id)
            session_id = SessionId(session.session_id)
            
            # Parse measurement time or use current
            if measurement_time:
                timestamp = DateTimeUtils.parse_date_string(measurement_time)
                if not timestamp:
                    raise ValidationError("Invalid measurement time format")
            else:
                timestamp = DateTimeUtils.now_mexico()
            
            # Use application service for business logic
            measurement = await self.patient_service.save_measurement(
                patient_id=patient_id,
                measurement_type=MeasurementType.GLUCOSE_FASTING,
                value=glucose_value,
                unit="mg/dL",
                notes=f"Logged via {self.get_agent_name()}"
            )
            
            # Format response using shared utilities
            formatted_time = DateTimeUtils.format_date_friendly(timestamp)
            
            # Check if emergency intervention needed
            if self.medical_validator.is_emergency_value("glucose_fasting", glucose_value):
                emergency_response = self._handle_glucose_emergency(glucose_value, "fasting")
                return emergency_response
            
            # Normal response with interpretation
            interpretation = self._interpret_glucose_reading(glucose_value, "fasting")
            
            response = f"""
✅ Glucosa en ayunas registrada exitosamente

📊 **Valor registrado:** {glucose_value} mg/dL
🕐 **Tiempo:** {formatted_time}
💡 **Interpretación:** {interpretation}

{self._get_glucose_recommendations(glucose_value, "fasting")}
            """.strip()
            
            return {
                "response_type": "measurement_logged",
                "response": response,
                "measurement_id": measurement.id,
                "value": glucose_value,
                "interpretation": interpretation
            }
            
        except ValidationError as e:
            return self._create_error_response(f"Error de validación: {e.message}")
        except PatientNotFoundError:
            return self._create_error_response("Paciente no encontrado. Por favor, registre sus datos primero.")
        except Exception as e:
            self.logger.error(f"Error logging glucose: {e}")
            return self._create_error_response("Error interno. Por favor, intente nuevamente.")
    
    @tool
    async def log_glucose_postmeal(
        self, 
        session: SessionContext, 
        glucose_value: float,
        hours_after_meal: float = 2.0,
        meal_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log post-meal glucose with enhanced validation"""
        try:
            patient_id = PatientId(session.patient.patient_id)
            
            # Validate timing
            if hours_after_meal < 1.0 or hours_after_meal > 4.0:
                raise ValidationError("Medición debe ser entre 1-4 horas después de comer")
            
            # Create measurement with additional context
            notes = f"Medición {hours_after_meal}h después de comer"
            if meal_description:
                notes += f". Comida: {meal_description}"
            
            measurement = await self.patient_service.save_measurement(
                patient_id=patient_id,
                measurement_type=MeasurementType.GLUCOSE_POST_MEAL,
                value=glucose_value,
                unit="mg/dL",
                notes=notes
            )
            
            # Emergency check
            if self.medical_validator.is_emergency_value("glucose_post_meal", glucose_value):
                return self._handle_glucose_emergency(glucose_value, "postprandial")
            
            interpretation = self._interpret_glucose_reading(glucose_value, "postmeal")
            
            response = f"""
✅ Glucosa postprandial registrada

📊 **Valor:** {glucose_value} mg/dL ({hours_after_meal}h después de comer)
💡 **Interpretación:** {interpretation}
{f"🍽️ **Comida:** {meal_description}" if meal_description else ""}

{self._get_glucose_recommendations(glucose_value, "postmeal")}
            """.strip()
            
            return {
                "response_type": "measurement_logged",
                "response": response,
                "measurement_id": measurement.id,
                "value": glucose_value,
                "timing": f"{hours_after_meal}h postprandial"
            }
            
        except ValidationError as e:
            return self._create_error_response(f"Error: {e.message}")
        except Exception as e:
            self.logger.error(f"Error logging post-meal glucose: {e}")
            return self._create_error_response("Error registrando medición.")
    
    # =============================================================================
    # APPOINTMENT MANAGEMENT - Enhanced with new architecture  
    # =============================================================================
    
    @tool
    async def schedule_endocrinology_appointment(
        self,
        session: SessionContext,
        preferred_date: Optional[str] = None,
        preferred_time: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Schedule endocrinology appointment using modern services"""
        try:
            patient_id = PatientId(session.patient.patient_id)
            
            # Parse preferred datetime
            appointment_datetime = None
            if preferred_date:
                if preferred_time:
                    datetime_str = f"{preferred_date} {preferred_time}"
                else:
                    datetime_str = preferred_date
                
                appointment_datetime = DateTimeUtils.parse_date_string(datetime_str)
                if not appointment_datetime:
                    raise ValidationError("Formato de fecha/hora inválido")
            
            # Check if within business hours
            if appointment_datetime and not DateTimeUtils.is_business_hours(appointment_datetime):
                available_slots = DateTimeUtils.get_available_appointment_slots()
                next_slot = available_slots[0] if available_slots else DateTimeUtils.next_business_day()
                
                return {
                    "response_type": "appointment_suggestion",
                    "response": f"""
⏰ El horario solicitado está fuera del horario de consultas.

🏥 **Horarios disponibles:** Lunes a Viernes, 9:00 AM - 5:00 PM
📅 **Próximo disponible:** {DateTimeUtils.format_date_friendly(next_slot)}

¿Te gustaría agendar para este horario?
                    """.strip(),
                    "suggested_datetime": next_slot.isoformat()
                }
            
            # Schedule appointment
            appointment = await self.patient_service.schedule_appointment(
                patient_id=patient_id,
                specialty="endocrinology",
                preferred_date=appointment_datetime,
                notes=reason
            )
            
            formatted_date = DateTimeUtils.format_date_friendly(appointment.date)
            
            response = f"""
✅ Cita con endocrinólogo agendada exitosamente

📅 **Fecha y hora:** {formatted_date}
👨‍⚕️ **Doctor:** {appointment.doctor_name}
🖥️ **Modalidad:** Consulta virtual
🆔 **ID de cita:** {appointment.id}

📋 **Recordatorios:**
• Recibirás el enlace de videollamada 30 minutos antes
• Ten listos tus últimos estudios de laboratorio
• Prepara una lista de tus medicamentos actuales

¿Necesitas reprogramar o tienes alguna pregunta sobre la cita?
            """.strip()
            
            return {
                "response_type": "appointment_scheduled",
                "response": response,
                "appointment_id": appointment.id,
                "appointment_date": appointment.date.isoformat(),
                "doctor": appointment.doctor_name
            }
            
        except ValidationError as e:
            return self._create_error_response(f"Error: {e.message}")
        except Exception as e:
            self.logger.error(f"Error scheduling appointment: {e}")
            return self._create_error_response("Error agendando cita. Intente nuevamente.")
    
    @tool
    async def get_upcoming_appointments(self, session: SessionContext) -> Dict[str, Any]:
        """Get patient's upcoming appointments"""
        try:
            patient_id = PatientId(session.patient.patient_id)
            appointments = await self.patient_service.get_patient_appointments(patient_id)
            
            # Filter upcoming appointments
            now = DateTimeUtils.now_mexico()
            upcoming = [apt for apt in appointments if apt.date > now]
            
            if not upcoming:
                return {
                    "response_type": "no_appointments",
                    "response": "No tienes citas próximas agendadas. ¿Te gustaría agendar una consulta?"
                }
            
            # Format appointments list
            appointments_text = []
            for apt in upcoming[:3]:  # Show max 3 upcoming
                formatted_date = DateTimeUtils.format_date_friendly(apt.date)
                appointments_text.append(
                    f"• **{apt.specialty.title()}** - {formatted_date} (Dr. {apt.doctor_name})"
                )
            
            response = f"""
📅 **Tus próximas citas:**

{chr(10).join(appointments_text)}

¿Necesitas reprogramar alguna cita o agendar una nueva consulta?
            """.strip()
            
            return {
                "response_type": "appointments_list",
                "response": response,
                "appointment_count": len(upcoming),
                "appointments": [apt.id for apt in upcoming]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting appointments: {e}")
            return self._create_error_response("Error consultando citas.")
    
    # =============================================================================
    # HEALTH INSIGHTS - Using domain services
    # =============================================================================
    
    @tool
    async def get_glucose_summary(
        self, 
        session: SessionContext, 
        days: int = 7
    ) -> Dict[str, Any]:
        """Get glucose readings summary using domain services"""
        try:
            patient_id = PatientId(session.patient.patient_id)
            
            # Get measurements from service
            fasting_measurements = await self.patient_service.get_patient_measurements(
                patient_id, MeasurementType.GLUCOSE_FASTING, days
            )
            postmeal_measurements = await self.patient_service.get_patient_measurements(
                patient_id, MeasurementType.GLUCOSE_POST_MEAL, days
            )
            
            if not fasting_measurements and not postmeal_measurements:
                return {
                    "response_type": "no_data",
                    "response": f"No hay registros de glucosa en los últimos {days} días. ¡Comienza a registrar tus mediciones!"
                }
            
            # Calculate insights using domain service
            insights = self._calculate_glucose_insights(fasting_measurements, postmeal_measurements, days)
            
            return {
                "response_type": "glucose_summary",
                "response": insights["summary_text"],
                "statistics": insights["stats"],
                "recommendations": insights["recommendations"]
            }
            
        except Exception as e:
            self.logger.error(f"Error generating glucose summary: {e}")
            return self._create_error_response("Error generando resumen.")
    
    # =============================================================================
    # HELPER METHODS - Private implementation details
    # =============================================================================
    
    def _handle_glucose_emergency(self, value: float, measurement_type: str) -> Dict[str, Any]:
        """Handle emergency glucose values"""
        if value < 70:
            emergency_text = f"""
🚨 **ALERTA: Hipoglucemia Severa** 🚨

Tu glucosa está muy baja ({value} mg/dL). Esto requiere atención INMEDIATA.

⚡ **ACCIONES INMEDIATAS:**
1. Consume 15-20g de carbohidratos rápidos:
   • 4 tabletas de glucosa
   • 1/2 taza de jugo de frutas
   • 1 cucharada de miel

2. Espera 15 minutos y vuelve a medirte
3. Si sigue bajo 70 mg/dL, repite el paso 1

🏥 **BUSCA AYUDA MÉDICA SI:**
• Te sientes muy mal o confundido
• No mejoras después de dos tratamientos
• Tienes vómitos o no puedes comer

📞 **Emergencias:** 911
            """
        else:  # > 300
            emergency_text = f"""
🚨 **ALERTA: Hiperglucemia Severa** 🚨

Tu glucosa está muy alta ({value} mg/dL). Requiere atención médica urgente.

⚡ **ACCIONES INMEDIATAS:**
1. Bebe agua abundante (sin azúcar)
2. NO hagas ejercicio intenso
3. Contacta a tu médico AHORA
4. Considera ir a urgencias

🏥 **BUSCA AYUDA INMEDIATA SI TIENES:**
• Vómitos o náuseas
• Dificultad para respirar
• Dolor abdominal
• Aliento con olor a frutas

📞 **Emergencias:** 911
            """
        
        return {
            "response_type": "emergency_alert",
            "response": emergency_text,
            "emergency_level": "high",
            "glucose_value": value
        }
    
    def _interpret_glucose_reading(self, value: float, reading_type: str) -> str:
        """Interpret glucose reading using medical validation"""
        if reading_type == "fasting":
            if value < 70:
                return "🔴 Hipoglucemia - Peligrosamente bajo"
            elif value <= 100:
                return "🟢 Normal - Excelente control"
            elif value <= 125:
                return "🟡 Prediabetes - Ligeramente elevado"
            elif value <= 200:
                return "🟠 Diabetes - Elevado"
            else:
                return "🔴 Muy elevado - Requiere atención"
        else:  # postmeal
            if value < 70:
                return "🔴 Hipoglucemia - Muy bajo"
            elif value <= 140:
                return "🟢 Normal - Buen control postprandial"
            elif value <= 180:
                return "🟡 Ligeramente elevado"
            elif value <= 250:
                return "🟠 Elevado - Revisar alimentación"
            else:
                return "🔴 Muy elevado - Atención médica"
    
    def _get_glucose_recommendations(self, value: float, reading_type: str) -> str:
        """Get personalized recommendations"""
        if reading_type == "fasting" and 70 <= value <= 100:
            return "💚 ¡Excelente! Mantén tu rutina actual de alimentación y medicamentos."
        elif reading_type == "fasting" and 100 < value <= 125:
            return "💛 Considera revisar tu cena de anoche y horario de medicamentos."
        elif reading_type == "postmeal" and value <= 140:
            return "💚 ¡Buena respuesta a los alimentos! Tu metabolismo está funcionando bien."
        elif reading_type == "postmeal" and value > 140:
            return "💛 Considera reducir carbohidratos en esta comida o aumentar actividad física."
        else:
            return "📋 Registra este valor y compártelo con tu médico en la próxima consulta."
    
    def _calculate_glucose_insights(self, fasting: List[HealthMeasurement], 
                                  postmeal: List[HealthMeasurement], days: int) -> Dict[str, Any]:
        """Calculate comprehensive glucose insights"""
        stats = {}
        
        if fasting:
            fasting_values = [m.value for m in fasting]
            stats["fasting"] = {
                "count": len(fasting_values),
                "average": sum(fasting_values) / len(fasting_values),
                "min": min(fasting_values),
                "max": max(fasting_values)
            }
        
        if postmeal:
            postmeal_values = [m.value for m in postmeal]
            stats["postmeal"] = {
                "count": len(postmeal_values),
                "average": sum(postmeal_values) / len(postmeal_values),
                "min": min(postmeal_values),
                "max": max(postmeal_values)
            }
        
        # Generate summary text
        summary_parts = [f"📊 **Resumen de glucosa ({days} días):**\n"]
        
        if "fasting" in stats:
            avg_fasting = stats["fasting"]["average"]
            summary_parts.append(
                f"🌅 **En ayunas:** {stats['fasting']['count']} mediciones, "
                f"promedio {avg_fasting:.1f} mg/dL"
            )
        
        if "postmeal" in stats:
            avg_postmeal = stats["postmeal"]["average"]
            summary_parts.append(
                f"🍽️ **Postprandial:** {stats['postmeal']['count']} mediciones, "
                f"promedio {avg_postmeal:.1f} mg/dL"
            )
        
        return {
            "stats": stats,
            "summary_text": "\n".join(summary_parts),
            "recommendations": self._generate_insights_recommendations(stats)
        }
    
    def _generate_insights_recommendations(self, stats: Dict) -> List[str]:
        """Generate personalized recommendations based on patterns"""
        recommendations = []
        
        if "fasting" in stats:
            avg_fasting = stats["fasting"]["average"]
            if avg_fasting > 130:
                recommendations.append("💡 Tu glucosa en ayunas está elevada. Considera revisar tu cena y medicamentos nocturnos.")
            elif avg_fasting < 80:
                recommendations.append("💡 Excelente control en ayunas. ¡Sigue así!")
        
        if "postmeal" in stats:
            avg_postmeal = stats["postmeal"]["average"]
            if avg_postmeal > 180:
                recommendations.append("💡 Considera reducir carbohidratos en las comidas o aumentar actividad física después de comer.")
        
        if not recommendations:
            recommendations.append("💡 Mantén tu rutina actual y continúa monitoreando regularmente.")
        
        return recommendations
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "response_type": "error",
            "response": f"❌ {message}",
            "error": True
        }
    
    async def main_menu_flow(self, session: SessionContext) -> Dict[str, Any]:
        """Main menu using modern architecture"""
        try:
            # Use session service to track navigation
            session_id = SessionId(session.session_id)
            self.session_service.update_session_state(session_id, "main_menu")
            
            # Get patient summary using new services
            patient_id = PatientId(session.patient.patient_id)
            health_summary = await self.patient_service.get_health_summary(patient_id)
            
            return {
                "response_type": "main_menu",
                "response": "Menú principal del agente de diabetes modernizado",
                "health_summary": health_summary
            }
            
        except Exception as e:
            self.logger.error(f"Error in main menu: {e}")
            return self._create_error_response("Error cargando menú principal")
