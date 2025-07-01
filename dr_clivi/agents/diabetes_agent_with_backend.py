"""
Updated Diabetes Agent with Backend Integration
Demonstrates how to integrate the mock backend service with existing tools
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from .base_agent import BaseCliviAgent, SessionContext, PatientContext, tool
from ..config import Config
from ..services.backend_integration import (
    MockBackendService, 
    BackendIntegrationService,
    BackendError,
    AppointmentStatus,
    MeasurementType
)


class DiabetesAgentWithBackend(BaseCliviAgent):
    """
    Enhanced Diabetes Agent with backend integration
    Demonstrates integration patterns for all tools
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize backend service (mock for demo, real for production)
        if hasattr(config, 'backend') and config.backend.use_mock:
            self.backend = MockBackendService()
        else:
            self.backend = BackendIntegrationService(
                base_url=getattr(config.backend, 'base_url', 'https://api.drclivi.com'),
                api_key=getattr(config.backend, 'api_key', ''),
                timeout=getattr(config.backend, 'timeout', 30)
            )
    
    def get_agent_name(self) -> str:
        return "DiabetesAgentWithBackend"
    
    async def main_menu_flow(self, session: SessionContext) -> Dict[str, Any]:
        """Main menu flow implementation for demo"""
        return {
            "response_type": "general_response",
            "response": "Demo backend integration agent - main menu not implemented for this demo"
        }
    
    def get_system_instructions(self) -> str:
        return """
        Eres Dr. Clivi, un asistente médico especializado en diabetes tipo 2 con acceso a sistema backend.
        
        CAPACIDADES AVANZADAS:
        - Acceso a datos persistentes de pacientes
        - Gestión de citas en tiempo real
        - Registro y análisis de mediciones
        - Generación de reportes dinámicos
        
        FUNCIONES PRINCIPALES:
        1. GESTIÓN DE CITAS (con backend):
           - Consultar citas reales del paciente
           - Agendar con disponibilidad real
           - Re-agendar y cancelar en sistema
           
        2. MEDICIONES (con persistencia):
           - Guardar en base de datos
           - Validar rangos médicos
           - Generar alertas automáticas
           
        3. REPORTES (dinámicos):
           - Gráficos basados en datos reales
           - Tendencias y recomendaciones
           - Exportación automática
        """
    
    # ==================== ENHANCED TOOLS WITH BACKEND ====================
    
    @tool
    async def APPOINTMENT_CONFIRM(self, session: SessionContext, **kwargs) -> str:
        """
        Enhanced appointment confirmation with real backend data
        Replaces static messages with dynamic appointment information
        """
        try:
            patient_id = session.patient.patient_id
            
            # Get real appointments from backend
            appointments = await self.backend.get_patient_appointments(
                patient_id, 
                status=AppointmentStatus.SCHEDULED
            )
            
            if not appointments:
                return (
                    "📅 **No tienes citas programadas actualmente.**\n\n"
                    "¿Te gustaría agendar una cita con uno de nuestros especialistas?\n\n"
                    "Especialidades disponibles:\n"
                    "🩺 Endocrinología\n"
                    "🥗 Nutrición\n"
                    "🧠 Psicología\n"
                    "👨‍⚕️ Medicina General"
                )
            
            # Format appointments information
            response = "📋 **Tus Citas Programadas:**\n\n"
            
            for i, appt in enumerate(appointments[:3], 1):  # Show max 3 upcoming
                date_str = appt.date.strftime("%d de %B, %Y")
                time_str = appt.date.strftime("%I:%M %p")
                
                response += f"🔹 **Cita {i}:** {appt.specialty.title()}\n"
                response += f"📅 Fecha: {date_str}\n"
                response += f"🕐 Hora: {time_str}\n"
                response += f"👩‍⚕️ {appt.doctor_name}\n"
                response += f"💻 Modalidad: {'Virtual' if appt.is_virtual else 'Presencial'}\n"
                
                if appt.meeting_link:
                    response += f"🔗 [Enlace de videollamada]({appt.meeting_link})\n"
                
                response += f"✅ Estado: {appt.status.value.title()}\n\n"
            
            if len(appointments) > 3:
                response += f"... y {len(appointments) - 3} citas más\n\n"
            
            response += (
                "📝 **Preparación:**\n"
                "- Ten lista tu glucómetro\n"
                "- Lleva tu registro de glucosas\n"
                "- Prepara tus medicamentos actuales\n\n"
                "¿Te gustaría modificar alguna cita?"
            )
            
            return response
            
        except BackendError as e:
            self.logger.error(f"Backend error in APPOINTMENT_CONFIRM: {e}")
            return (
                "⚠️ **Temporalmente no podemos acceder a tu información de citas.**\n\n"
                "Por favor, contacta a nuestro equipo:\n"
                "📞 +52 55 8840 9477\n\n"
                "Nuestro sistema se encuentra en mantenimiento."
            )
        except Exception as e:
            self.logger.error(f"Unexpected error in APPOINTMENT_CONFIRM: {e}")
            return "❌ Ocurrió un error. Por favor intenta de nuevo más tarde."
    
    @tool
    async def SCHEDULE_NEW_APPOINTMENT(self, session: SessionContext, specialty: str = None, **kwargs) -> str:
        """
        New tool for scheduling appointments with backend integration
        """
        try:
            patient_id = session.patient.patient_id
            
            if not specialty:
                return (
                    "📅 **Agendar Nueva Cita**\n\n"
                    "¿Qué tipo de especialista necesitas?\n\n"
                    "🩺 Endocrinólogo - Para manejo de diabetes\n"
                    "🥗 Nutriólogo - Para plan alimentario\n"
                    "🧠 Psicólogo - Para apoyo emocional\n"
                    "👨‍⚕️ Medicina General - Para consulta general\n\n"
                    "Responde con el nombre de la especialidad."
                )
            
            # Map specialty names to backend values
            specialty_map = {
                'endocrinólogo': 'endocrinology',
                'endocrinologia': 'endocrinology',
                'nutriólogo': 'nutrition',
                'nutricion': 'nutrition',
                'psicólogo': 'psychology',
                'psicologia': 'psychology',
                'medicina general': 'general',
                'general': 'general'
            }
            
            backend_specialty = specialty_map.get(specialty.lower())
            if not backend_specialty:
                return f"❌ Especialidad '{specialty}' no reconocida. Por favor elige una de las opciones disponibles."
            
            # Schedule appointment with backend
            appointment = await self.backend.schedule_appointment(
                patient_id=patient_id,
                specialty=backend_specialty
            )
            
            date_str = appointment.date.strftime("%d de %B, %Y")
            time_str = appointment.date.strftime("%I:%M %p")
            
            response = (
                f"✅ **Cita Programada Exitosamente**\n\n"
                f"📋 **Detalles de tu cita:**\n"
                f"🔹 Especialidad: {appointment.specialty.title()}\n"
                f"👩‍⚕️ Doctor: {appointment.doctor_name}\n"
                f"📅 Fecha: {date_str}\n"
                f"🕐 Hora: {time_str}\n"
                f"💻 Modalidad: {'Virtual' if appointment.is_virtual else 'Presencial'}\n"
                f"🆔 ID de cita: {appointment.id}\n\n"
                f"📞 **Próximos pasos:**\n"
                f"1. Recibirás confirmación por correo\n"
                f"2. Te enviaremos el enlace 30 min antes\n"
                f"3. Recordatorio 1 día antes\n\n"
                f"¿Necesitas algo más?"
            )
            
            # Log the event
            await self._log_appointment_event(session, "APPOINTMENT_SCHEDULED", {
                "appointment_id": appointment.id,
                "specialty": backend_specialty,
                "scheduled_date": appointment.date.isoformat()
            })
            
            return response
            
        except BackendError as e:
            self.logger.error(f"Backend error in SCHEDULE_NEW_APPOINTMENT: {e}")
            return (
                "⚠️ **No pudimos agendar tu cita en este momento.**\n\n"
                "Por favor contacta directamente:\n"
                "📞 +52 55 8840 9477\n"
                "💬 WhatsApp disponible 24/7\n\n"
                "Nuestro equipo te ayudará personalmente."
            )
    
    @tool
    async def SAVE_MEASUREMENT(self, session: SessionContext, 
                             measurement_type: str, value: str, **kwargs) -> str:
        """
        Enhanced measurement saving with backend persistence and validation
        """
        try:
            patient_id = session.patient.patient_id
            
            # Parse and validate measurement
            try:
                numeric_value = float(value)
            except ValueError:
                return f"❌ Valor inválido '{value}'. Por favor ingresa un número válido."
            
            # Map measurement types
            type_map = {
                'peso': (MeasurementType.WEIGHT, 'kg'),
                'weight': (MeasurementType.WEIGHT, 'kg'),
                'glucosa_ayunas': (MeasurementType.GLUCOSE_FASTING, 'mg/dL'),
                'glucose_fasting': (MeasurementType.GLUCOSE_FASTING, 'mg/dL'),
                'glucosa_postcomida': (MeasurementType.GLUCOSE_POST_MEAL, 'mg/dL'),
                'glucose_post_meal': (MeasurementType.GLUCOSE_POST_MEAL, 'mg/dL'),
                'cintura': (MeasurementType.WAIST, 'cm'),
                'waist': (MeasurementType.WAIST, 'cm'),
                'cadera': (MeasurementType.HIP, 'cm'),
                'hip': (MeasurementType.HIP, 'cm'),
                'cuello': (MeasurementType.NECK, 'cm'),
                'neck': (MeasurementType.NECK, 'cm')
            }
            
            if measurement_type.lower() not in type_map:
                return f"❌ Tipo de medición '{measurement_type}' no reconocido."
            
            backend_type, unit = type_map[measurement_type.lower()]
            
            # Validate ranges
            validation_result = self._validate_measurement(backend_type, numeric_value)
            if not validation_result['valid']:
                return f"⚠️ {validation_result['message']}"
            
            # Save to backend
            measurement = await self.backend.save_measurement(
                patient_id=patient_id,
                measurement_type=backend_type,
                value=numeric_value,
                unit=unit,
                notes=kwargs.get('notes')
            )
            
            # Generate response with feedback
            response = f"✅ **Medición guardada exitosamente**\n\n"
            response += f"📊 **{backend_type.value.replace('_', ' ').title()}:** {numeric_value} {unit}\n"
            response += f"🕐 **Registrado:** {measurement.timestamp.strftime('%d/%m/%Y %H:%M')}\n\n"
            
            # Add medical feedback
            if validation_result.get('feedback'):
                response += f"📋 **Evaluación médica:**\n{validation_result['feedback']}\n\n"
            
            response += "📈 **¿Te gustaría ver tu progreso?**\nPuedes solicitar un reporte de tus mediciones."
            
            # Log the event
            await self._log_measurement_event(session, measurement)
            
            return response
            
        except BackendError as e:
            self.logger.error(f"Backend error in SAVE_MEASUREMENT: {e}")
            return (
                "⚠️ **No pudimos guardar tu medición.**\n\n"
                "Tu información es importante. Por favor intenta de nuevo en unos minutos "
                "o contáctanos si el problema persiste."
            )
    
    @tool
    async def GENERATE_GLUCOSE_REPORT(self, session: SessionContext, days: int = 30, **kwargs) -> str:
        """
        Generate dynamic glucose report from backend data
        """
        try:
            patient_id = session.patient.patient_id
            
            # Get report from backend
            report = await self.backend.generate_glucose_report(patient_id, days)
            
            response = f"📈 **Reporte de Glucosa - Últimos {days} días**\n\n"
            
            if report['total_measurements'] == 0:
                return (
                    "📊 **No hay mediciones de glucosa registradas**\n\n"
                    "Para generar un reporte, necesitamos que registres tus mediciones:\n"
                    "🔹 Glucosa en ayunas\n"
                    "🔹 Glucosa post comida\n\n"
                    "¿Te gustaría registrar una medición ahora?"
                )
            
            # Format statistics
            response += f"📊 **Estadísticas:**\n"
            response += f"🔹 Total de mediciones: {report['total_measurements']}\n"
            response += f"🔹 Promedio en ayunas: {report['average_fasting']:.1f} mg/dL\n"
            response += f"🔹 Promedio post comida: {report['average_post_meal']:.1f} mg/dL\n"
            response += f"🔹 En rango objetivo: {report['in_range_percentage']:.1f}%\n\n"
            
            # Color coding for ranges
            if report['in_range_percentage'] >= 80:
                response += "✅ **¡Excelente control glucémico!**\n"
            elif report['in_range_percentage'] >= 60:
                response += "⚠️ **Control aceptable, puede mejorar**\n"
            else:
                response += "🚨 **Requiere atención médica urgente**\n"
            
            response += "\n🎯 **Recomendaciones:**\n"
            for i, rec in enumerate(report['recommendations'], 1):
                response += f"{i}. {rec}\n"
            
            if report.get('report_url'):
                response += f"\n📋 [Ver reporte completo]({report['report_url']})"
            
            response += "\n\n¿Te gustaría agendar una cita para revisar estos resultados?"
            
            return response
            
        except BackendError as e:
            self.logger.error(f"Backend error in GENERATE_GLUCOSE_REPORT: {e}")
            return (
                "⚠️ **No pudimos generar tu reporte en este momento.**\n\n"
                "Nuestro sistema está procesando datos. "
                "Por favor intenta de nuevo en unos minutos."
            )
    
    # ==================== HELPER METHODS ====================
    
    def _validate_measurement(self, measurement_type: MeasurementType, value: float) -> Dict[str, Any]:
        """Validate measurement values and provide medical feedback"""
        
        if measurement_type == MeasurementType.GLUCOSE_FASTING:
            if value < 70:
                return {
                    'valid': False,
                    'message': (
                        f"⚠️ Glucosa en ayunas muy baja ({value} mg/dL).\n"
                        "Valor normal: 70-130 mg/dL\n"
                        "🚨 **Si sientes síntomas de hipoglucemia, busca atención médica inmediata.**"
                    )
                }
            elif value > 200:
                return {
                    'valid': False,
                    'message': (
                        f"🚨 Glucosa en ayunas muy alta ({value} mg/dL).\n"
                        "Valor normal: 70-130 mg/dL\n"
                        "**Contacta a tu médico inmediatamente.**"
                    )
                }
            elif 70 <= value <= 130:
                return {
                    'valid': True,
                    'feedback': f"✅ Excelente! Tu glucosa ({value} mg/dL) está en rango objetivo."
                }
            else:
                return {
                    'valid': True,
                    'feedback': f"⚠️ Glucosa elevada ({value} mg/dL). Rango objetivo: 70-130 mg/dL."
                }
        
        elif measurement_type == MeasurementType.GLUCOSE_POST_MEAL:
            if value > 250:
                return {
                    'valid': False,
                    'message': (
                        f"🚨 Glucosa post comida muy alta ({value} mg/dL).\n"
                        "**Contacta a tu médico inmediatamente.**"
                    )
                }
            elif value <= 180:
                return {
                    'valid': True,
                    'feedback': f"✅ Excelente control post comida ({value} mg/dL)."
                }
            else:
                return {
                    'valid': True,
                    'feedback': f"⚠️ Un poco elevada ({value} mg/dL). Meta: <180 mg/dL después de comer."
                }
        
        elif measurement_type == MeasurementType.WEIGHT:
            if value < 30 or value > 300:
                return {
                    'valid': False,
                    'message': f"❌ Peso fuera de rango válido ({value} kg). Por favor verifica."
                }
            return {'valid': True}
        
        # Default validation for other measurements
        return {'valid': True}
    
    async def _log_appointment_event(self, session: SessionContext, event_type: str, data: Dict[str, Any]):
        """Log appointment-related events for analytics"""
        try:
            # This would integrate with analytics/logging backend
            self.logger.info(f"Appointment event: {event_type}", extra={
                'patient_id': session.patient.patient_id,
                'event_data': data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Failed to log appointment event: {e}")
    
    async def _log_measurement_event(self, session: SessionContext, measurement):
        """Log measurement events for analytics"""
        try:
            self.logger.info(f"Measurement saved: {measurement.type.value}", extra={
                'patient_id': session.patient.patient_id,
                'measurement_id': measurement.id,
                'value': measurement.value,
                'timestamp': measurement.timestamp.isoformat()
            })
        except Exception as e:
            self.logger.error(f"Failed to log measurement event: {e}")


# ==================== EXAMPLE USAGE ====================

async def demo_backend_integration():
    """
    Demonstration of backend integration capabilities
    """
    from ..config import Config
    
    # Mock configuration
    config = Config()
    config.backend = type('BackendConfig', (), {
        'use_mock': True,
        'base_url': 'https://api.drclivi.com',
        'api_key': 'demo_key'
    })()
    
    # Initialize agent
    agent = DiabetesAgentWithBackend(config)
    
    # Create mock session
    session = SessionContext(
        user_context="PATIENT",
        patient=PatientContext(
            patient_id="patient_123",
            name_display="Juan Pérez",
            preferred_language="es"
        ),
        current_flow="diabetes_care"
    )
    
    print("=== Demo: Backend-Integrated Dr. Clivi ===\n")
    
    # Demo 1: Check appointments
    print("1. Checking appointments...")
    result = await agent.APPOINTMENT_CONFIRM(session)
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Demo 2: Schedule new appointment
    print("2. Scheduling new appointment...")
    result = await agent.SCHEDULE_NEW_APPOINTMENT(session, specialty="endocrinólogo")
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Demo 3: Save glucose measurement
    print("3. Saving glucose measurement...")
    result = await agent.SAVE_MEASUREMENT(session, "glucosa_ayunas", "125")
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Demo 4: Generate report
    print("4. Generating glucose report...")
    result = await agent.GENERATE_GLUCOSE_REPORT(session)
    print(result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_backend_integration())
