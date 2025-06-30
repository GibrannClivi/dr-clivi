"""
Diabetes Agent - Specialized agent for diabetes care workflows.
Based on analysis of exported Conversational Agents diabetes flow.
"""

import logging
from typing import Any, Dict, List, Optional

from .base_agent import BaseCliviAgent, SessionContext, PatientContext, tool
from ..config import Config


class DiabetesAgent(BaseCliviAgent):
    """
    Specialized agent for diabetes care based on exported flows analysis.
    
    Implements diabetes-specific flows:
    - diabetesPlans main menu
    - Glucose logging (fasting/post-meal) 
    - Medication tutorials (GLP-1)
    - Supplies management (glucometer, strips)
    - Endocrinology appointments
    """
    
    def get_agent_name(self) -> str:
        return self.config.diabetes_agent.name
    
    def get_system_instructions(self) -> str:
        return f"""
        Eres un asistente especializado en diabetes para la plataforma Dr. Clivi.

        Tu función principal es ayudar a pacientes con diabetes a:
        - Registrar mediciones de glucosa (en ayunas y postprandial)
        - Gestionar medicamentos GLP-1 (Ozempic, Saxenda, Wegovy)
        - Agendar citas con endocrinólogo
        - Consultar estado de suministros médicos (glucómetro, tiras)
        - Acceder a reportes de mediciones
        - Obtener tutoriales de medicamentos

        Configuración:
        - Idioma: {self.config.base_agent.default_language}
        - Zona horaria: {self.config.base_agent.timezone}
        - Modelo: {self.config.diabetes_agent.model}

        Siempre mantén un tono empático y profesional. Proporciona información médica 
        precisa pero recuerda que no reemplazas la consulta médica profesional.
        """
    
    def get_tools(self) -> List[str]:
        """Get diabetes-specific tools"""
        base_tools = super().get_tools()
        diabetes_tools = [
            "glucose_logging_flow",
            "medication_tutorial_flow", 
            "supplies_management_flow",
            "endocrinology_appointment_flow",
            "glucose_report_flow"
        ]
        return base_tools + diabetes_tools
    
    @tool
    async def main_menu_flow(self, user_id: str) -> Dict[str, Any]:
        """
        Diabetes main menu implementation.
        Based on diabetesPlans/pages/mainMenu.json analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "diabetesPlans"
        context.current_page = "mainMenu"
        
        patient_name = context.patient.name_display if context.patient else "Usuario"
        
        return {
            "action": "menu",
            "type": "diabetes_main_menu",
            "message": f"Hola {patient_name}, por favor utiliza el menú de opciones.",
            "menu_type": "SESSION_LIST",
            "sections": [
                {
                    "title": "Menú:",
                    "rows": [
                        {
                            "id": "APPOINTMENTS",
                            "title": "Citas",
                            "description": "Agenda/Re-agendamiento 🗓️"
                        },
                        {
                            "id": "MEASUREMENTS",
                            "title": "Mediciones",
                            "description": "Enviar mediciones 📏"
                        },
                        {
                            "id": "MEASUREMENTS_REPORT",
                            "title": "Reporte mediciones", 
                            "description": "Reporte de mediciones 📈"
                        },
                        {
                            "id": "INVOICE_LABS",
                            "title": "Facturas y estudios",
                            "description": "Facturación, estudios y órdenes📂"
                        },
                        {
                            "id": "MEDS_GLP",
                            "title": "Estatus de envíos",
                            "description": "Meds/Glucómetro/Tiras📦"
                        },
                        {
                            "id": "QUESTION_TYPE",
                            "title": "Enviar pregunta",
                            "description": "Enviar pregunta a agente/especialista ❔"
                        },
                        {
                            "id": "NO_NEEDED_QUESTION_PATIENT",
                            "title": "No es necesario",
                            "description": "No requiero apoyo 👍"
                        },
                        {
                            "id": "PATIENT_COMPLAINT", 
                            "title": "Presentar queja",
                            "description": "Enviar queja sobre el servicio 📣"
                        }
                    ]
                }
            ]
        }
    
    @tool
    async def glucose_logging_flow(self, user_id: str, measurement_type: str = None, 
                                 glucose_value: float = None, meal_time: str = None) -> Dict[str, Any]:
        """
        Enhanced glucose logging flow implementation.
        Based on glucoseValueLogFasting/PostMeal pages analysis.
        
        Supports both fasting and post-meal measurements with detailed validation.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "glucose_logging"
        
        # Step 1: Select measurement type if not provided
        if not measurement_type:
            await self._log_activity_event(user_id, "GLUCOSE_LOGGING_STARTED")
            return {
                "action": "request_selection",
                "message": "¿Qué tipo de medición de glucosa deseas registrar?",
                "selection_type": "glucose_measurement_type",
                "options": [
                    {
                        "id": "FASTING",
                        "title": "En ayunas",
                        "description": "Medición antes del desayuno 🌅",
                        "recommended_range": "70-100 mg/dL"
                    },
                    {
                        "id": "POST_MEAL",
                        "title": "Postprandial", 
                        "description": "Medición después de comer 🍽️",
                        "recommended_range": "< 140 mg/dL (2 horas post-comida)"
                    }
                ]
            }
        
        # Step 2: Request glucose value if not provided
        if not glucose_value:
            time_desc = "en ayunas" if measurement_type == "FASTING" else "después de comer"
            recommended_range = "70-100 mg/dL" if measurement_type == "FASTING" else "< 140 mg/dL"
            
            return {
                "action": "request_input",
                "message": f"Ingresa tu nivel de glucosa {time_desc}:",
                "input_type": "number",
                "unit": "mg/dL",
                "min_value": 50,
                "max_value": 500,
                "recommended_range": recommended_range,
                "measurement_type": measurement_type,
                "validation_tips": [
                    "Asegúrate de que el glucómetro esté calibrado",
                    "Lávate las manos antes de la medición",
                    "Usa una tira reactiva nueva"
                ]
            }
        
        # Step 3: For post-meal, ask about meal time if not provided
        if measurement_type == "POST_MEAL" and not meal_time:
            return {
                "action": "request_selection",
                "message": "¿Después de qué comida tomaste esta medición?",
                "selection_type": "meal_time",
                "options": [
                    {"id": "BREAKFAST", "title": "Desayuno 🥐", "description": "2 horas después del desayuno"},
                    {"id": "LUNCH", "title": "Comida 🍽️", "description": "2 horas después de la comida"},
                    {"id": "DINNER", "title": "Cena 🌙", "description": "2 horas después de la cena"},
                    {"id": "SNACK", "title": "Colación 🍎", "description": "Después de una colación"}
                ],
                "glucose_value": glucose_value,
                "measurement_type": measurement_type
            }
        
        # Step 4: Process and validate the measurement
        validation_result = self._validate_glucose_measurement(glucose_value, measurement_type)
        
        if not validation_result["is_valid"]:
            return {
                "action": "validation_error",
                "message": validation_result["error_message"],
                "suggested_action": "retry_measurement",
                "glucose_value": glucose_value
            }
        
        # Step 5: Save measurement and provide feedback
        result = await self._process_glucose_measurement(
            user_id, measurement_type, glucose_value, meal_time
        )
        
        # Get personalized feedback based on glucose levels and user history
        feedback = await self._get_enhanced_glucose_feedback(
            user_id, glucose_value, measurement_type, meal_time
        )
        
        await self._log_activity_event(user_id, "GLUCOSE_MEASUREMENT_RECORDED", {
            "measurement_type": measurement_type,
            "glucose_value": glucose_value,
            "meal_time": meal_time,
            "measurement_id": result["measurement_id"]
        })
        
        return {
            "action": "confirmation",
            "message": f"✅ Glucosa registrada: {glucose_value} mg/dL ({measurement_type.lower()})",
            "measurement_id": result["measurement_id"],
            "feedback": feedback,
            "trend_analysis": result.get("trend_analysis"),
            "next_actions": [
                {"id": "VIEW_REPORT", "title": "Ver reporte completo 📊"},
                {"id": "LOG_ANOTHER", "title": "Registrar otra medición ➕"},
                {"id": "SCHEDULE_CONSULTATION", "title": "Agendar consulta 👩‍⚕️"},
                {"id": "MAIN_MENU", "title": "Menú principal 🏠"}
            ]
        }
    
    @tool
    async def medication_tutorial_flow(self, user_id: str, medication: str = None) -> Dict[str, Any]:
        """
        Medication tutorial flow for GLP-1 medications.
        Based on tutorialMed page analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "medication_tutorial"
        
        if not medication:
            return {
                "action": "menu",
                "message": "Selecciona el medicamento para ver su tutorial:",
                "options": [
                    {
                        "id": "OZEMPIC",
                        "title": "Ozempic (Semaglutida)",
                        "description": "Tutorial de aplicación 💉"
                    },
                    {
                        "id": "SAXENDA", 
                        "title": "Saxenda (Liraglutida)",
                        "description": "Guía de uso 📋"
                    },
                    {
                        "id": "WEGOVY",
                        "title": "Wegovy (Semaglutida)",
                        "description": "Instrucciones de uso 📖"
                    },
                    {
                        "id": "GLP_GENERAL",
                        "title": "Información general GLP-1",
                        "description": "Conceptos básicos 📚"
                    }
                ]
            }
        
        tutorial_content = await self._get_medication_tutorial(medication)
        
        return {
            "action": "tutorial",
            "medication": medication,
            "content": tutorial_content,
            "media": {
                "video_url": tutorial_content.get("video_url"),
                "images": tutorial_content.get("images", []),
                "pdf_guide": tutorial_content.get("pdf_url")
            },
            "next_actions": [
                {"id": "SCHEDULE_REMINDER", "title": "Programar recordatorio"},
                {"id": "ASK_QUESTION", "title": "Hacer pregunta"},
                {"id": "MAIN_MENU", "title": "Menú principal"}
            ]
        }
    
    @tool
    async def supplies_management_flow(self, user_id: str) -> Dict[str, Any]:
        """
        Medical supplies management flow.
        Based on medsSuppliesStatus page analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "supplies_management"
        
        # Get supplies status from Clivi API
        supplies_status = await self._get_supplies_status(user_id)
        
        return {
            "action": "status_report",
            "message": "Estado actual de tus suministros médicos:",
            "supplies": [
                {
                    "item": "Glucómetro",
                    "status": supplies_status.get("glucometer", "active"),
                    "next_delivery": supplies_status.get("glucometer_delivery"),
                    "icon": "🩺"
                },
                {
                    "item": "Tiras reactivas",
                    "status": supplies_status.get("strips", "low_stock"),
                    "next_delivery": supplies_status.get("strips_delivery"),
                    "quantity_remaining": supplies_status.get("strips_remaining", 5),
                    "icon": "🧪"
                },
                {
                    "item": "Lancetas",
                    "status": supplies_status.get("lancets", "active"),
                    "next_delivery": supplies_status.get("lancets_delivery"),
                    "icon": "💉"
                }
            ],
            "actions": [
                {"id": "REQUEST_DELIVERY", "title": "Solicitar envío"},
                {"id": "TRACK_ORDER", "title": "Rastrear pedido"},
                {"id": "CONTACT_SUPPORT", "title": "Contactar soporte"},
                {"id": "MAIN_MENU", "title": "Menú principal"}
            ]
        }
    
    @tool
    async def endocrinology_appointment_flow(self, user_id: str, action: str = None) -> Dict[str, Any]:
        """
        Endocrinology appointment management.
        Based on DIABETES_ENDO intent analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "endocrinology_appointments"
        
        if not action:
            return {
                "action": "menu",
                "message": "¿Qué deseas hacer con tu cita de endocrinología?",
                "options": [
                    {
                        "id": "SCHEDULE_NEW",
                        "title": "Agendar cita",
                        "description": "Nueva cita con endocrinólogo 📅"
                    },
                    {
                        "id": "RESCHEDULE",
                        "title": "Reagendar cita",
                        "description": "Cambiar fecha de cita existente 🔄"
                    },
                    {
                        "id": "VIEW_UPCOMING",
                        "title": "Ver próximas citas",
                        "description": "Consultar citas programadas 📋"
                    },
                    {
                        "id": "CANCEL_APPOINTMENT",
                        "title": "Cancelar cita",
                        "description": "Cancelar cita programada ❌"
                    }
                ]
            }
        
        # Handle specific appointment actions
        if action == "SCHEDULE_NEW":
            return await self._schedule_endocrinology_appointment(user_id)
        elif action == "RESCHEDULE":
            return await self._reschedule_endocrinology_appointment(user_id)
        elif action == "VIEW_UPCOMING":
            return await self._view_upcoming_appointments(user_id, "endocrinology")
        elif action == "CANCEL_APPOINTMENT":
            return await self._cancel_appointment(user_id, "endocrinology")
    
    @tool
    async def glucose_report_flow(self, user_id: str, period: str = "week") -> Dict[str, Any]:
        """
        Glucose report generation flow.
        Based on GLUCOSE_REPORT_TEMPLATE_PAGE analysis.
        """
        context = self.get_session_context(user_id)
        context.current_flow = "glucose_report"
        
        # Generate glucose report
        report_data = await self._generate_glucose_report(user_id, period)
        
        return {
            "action": "report",
            "report_type": "glucose_levels",
            "period": period,
            "data": report_data,
            "statistics": {
                "average_fasting": report_data.get("avg_fasting"),
                "average_postprandial": report_data.get("avg_postprandial"),
                "readings_count": report_data.get("total_readings"),
                "in_range_percentage": report_data.get("in_range_pct")
            },
            "recommendations": report_data.get("recommendations", []),
            "export_options": [
                {"format": "PDF", "action": "EXPORT_PDF"},
                {"format": "Excel", "action": "EXPORT_EXCEL"},
                {"format": "Compartir", "action": "SHARE_REPORT"}
            ]
        }
    
    # Helper methods
    async def _process_glucose_measurement(self, user_id: str, measurement_type: str, 
                                         value: float, meal_time: str = None) -> Dict[str, Any]:
        """Process glucose measurement submission via Clivi platform"""
        # TODO: Integrate with Clivi measurement storage system via n8n webhook
        measurement_id = f"GLUC-{user_id[-4:]}-{hash(str(value)) % 10000:04d}"
        self.logger.info(f"Processing glucose measurement: {value} mg/dL ({measurement_type})")
        return {"measurement_id": measurement_id, "status": "success"}
    
    def _get_glucose_feedback(self, value: float, measurement_type: str) -> Dict[str, Any]:
        """Provide feedback based on glucose levels"""
        if measurement_type == "FASTING":
            if value < 70:
                return {"level": "low", "message": "Nivel bajo. Consulta con tu médico si es recurrente."}
            elif value <= 100:
                return {"level": "normal", "message": "Excelente control de glucosa en ayunas! 👍"}
            elif value <= 125:
                return {"level": "elevated", "message": "Ligeramente elevado. Mantén tu plan alimentario."}
            else:
                return {"level": "high", "message": "Nivel alto. Contacta a tu médico si persiste."}
        else:  # POST_MEAL
            if value < 70:
                return {"level": "low", "message": "Nivel bajo después de comer. Revisa tu alimentación."}
            elif value <= 140:
                return {"level": "normal", "message": "Muy buen control postprandial! 🎉"}
            elif value <= 200:
                return {"level": "elevated", "message": "Un poco elevado. Revisa las porciones de carbohidratos."}
            else:
                return {"level": "high", "message": "Nivel alto. Considera contactar a tu equipo médico."}
    
    async def _get_medication_tutorial(self, medication: str) -> Dict[str, Any]:
        """Get medication tutorial content"""
        # TODO: Integrate with Clivi content management system
        tutorials = {
            "OZEMPIC": {
                "title": "Tutorial Ozempic (Semaglutida)",
                "steps": [
                    "Verificar fecha de caducidad",
                    "Limpiar sitio de inyección", 
                    "Preparar pluma inyectora",
                    "Aplicar inyección subcutánea",
                    "Desechar aguja seguramente"
                ],
                "video_url": "https://clivi.com.mx/tutorials/ozempic",
                "pdf_url": "https://clivi.com.mx/guides/ozempic.pdf"
            }
        }
        return tutorials.get(medication, {"title": "Tutorial no disponible"})
    
    async def _get_supplies_status(self, user_id: str) -> Dict[str, Any]:
        """Get medical supplies status from Clivi API"""
        # TODO: Integrate with Clivi inventory API
        return {
            "glucometer": "active",
            "strips": "low_stock",
            "strips_remaining": 5,
            "strips_delivery": "2025-07-05",
            "lancets": "active"
        }
    
    async def _schedule_endocrinology_appointment(self, user_id: str) -> Dict[str, Any]:
        """Schedule new endocrinology appointment"""
        # TODO: Integrate with Clivi scheduling API
        return {
            "action": "appointment_scheduler",
            "specialty": "endocrinology",
            "message": "Selecciona fecha y hora para tu cita con el endocrinólogo"
        }
    
    async def _reschedule_endocrinology_appointment(self, user_id: str) -> Dict[str, Any]:
        """Reschedule existing endocrinology appointment"""
        return {
            "action": "appointment_reschedule",
            "message": "¿Cuál cita deseas reagendar?"
        }
    
    async def _view_upcoming_appointments(self, user_id: str, specialty: str) -> Dict[str, Any]:
        """View upcoming appointments"""
        return {
            "action": "appointments_list",
            "specialty": specialty,
            "appointments": []  # TODO: Get from API
        }
    
    async def _cancel_appointment(self, user_id: str, specialty: str) -> Dict[str, Any]:
        """Cancel appointment"""
        return {
            "action": "appointment_cancellation",
            "message": "¿Estás seguro de cancelar tu cita?"
        }
    
    async def _generate_glucose_report(self, user_id: str, period: str) -> Dict[str, Any]:
        """Generate glucose levels report"""
        # TODO: Integrate with Clivi analytics API
        return {
            "avg_fasting": 95.2,
            "avg_postprandial": 135.8,
            "total_readings": 28,
            "in_range_pct": 85.7,
            "recommendations": [
                "Mantén excelente control en ayunas",
                "Considera ajustar porciones en cenas"
            ]
        }
    
    # Enhanced helper methods based on exported flows analysis
    
    def _validate_glucose_measurement(self, value: float, measurement_type: str) -> Dict[str, Any]:
        """
        Validate glucose measurement values with enhanced logic.
        Based on medical guidelines and user safety.
        """
        if value < 30:
            return {
                "is_valid": False,
                "error_message": "⚠️ Valor muy bajo (< 30 mg/dL). Por favor verifica la medición o contacta emergencias si te sientes mal.",
                "severity": "critical"
            }
        elif value > 600:
            return {
                "is_valid": False,
                "error_message": "⚠️ Valor muy alto (> 600 mg/dL). Por favor verifica la medición o contacta a tu médico inmediatamente.",
                "severity": "critical"
            }
        elif value < 50:
            return {
                "is_valid": True,
                "warning_message": "⚠️ Valor bajo. Si te sientes mal, contacta a tu médico.",
                "severity": "warning"
            }
        elif value > 400:
            return {
                "is_valid": True,
                "warning_message": "⚠️ Valor alto. Considera contactar a tu equipo médico.",
                "severity": "warning"
            }
        else:
            return {"is_valid": True, "severity": "normal"}
    
    async def _get_enhanced_glucose_feedback(self, user_id: str, value: float, 
                                           measurement_type: str, meal_time: str = None) -> Dict[str, Any]:
        """
        Provide enhanced glucose feedback based on user history and context.
        """
        base_feedback = self._get_glucose_feedback(value, measurement_type)
        
        # Get user's glucose history for trend analysis
        history = await self._get_user_glucose_history(user_id, days=7)
        
        # Add trend analysis
        trend = self._analyze_glucose_trend(history, value, measurement_type)
        
        # Add personalized recommendations
        recommendations = self._generate_glucose_recommendations(
            value, measurement_type, meal_time, trend, history
        )
        
        return {
            **base_feedback,
            "trend": trend,
            "recommendations": recommendations,
            "historical_context": {
                "recent_average": history.get("recent_average"),
                "improvement_trend": trend.get("improving", False)
            }
        }
    
    async def _get_user_glucose_history(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get user's glucose measurement history"""
        # TODO: Implement actual API call to get user history
        # This would integrate with Clivi's measurement API
        return {
            "recent_average": 120.5,
            "measurements_count": 14,
            "last_week_avg_fasting": 105.2,
            "last_week_avg_postprandial": 135.8
        }
    
    def _analyze_glucose_trend(self, history: Dict, current_value: float, 
                              measurement_type: str) -> Dict[str, Any]:
        """Analyze glucose trends based on historical data"""
        if measurement_type == "FASTING":
            historical_avg = history.get("last_week_avg_fasting", 100)
        else:
            historical_avg = history.get("last_week_avg_postprandial", 140)
        
        difference = current_value - historical_avg
        
        if abs(difference) < 10:
            trend_status = "stable"
            trend_message = "Tus niveles se mantienen estables 📊"
        elif difference > 10:
            trend_status = "increasing"
            trend_message = "Tus niveles han aumentado comparado con la semana pasada 📈"
        else:
            trend_status = "decreasing"
            trend_message = "Tus niveles han mejorado comparado con la semana pasada 📉"
        
        return {
            "status": trend_status,
            "message": trend_message,
            "difference": difference,
            "improving": difference < 0 if measurement_type == "FASTING" else difference < 0
        }
    
    def _generate_glucose_recommendations(self, value: float, measurement_type: str,
                                        meal_time: str, trend: Dict, history: Dict) -> List[str]:
        """Generate personalized recommendations based on glucose data"""
        recommendations = []
        
        # Basic recommendations based on current value
        if measurement_type == "FASTING":
            if value > 130:
                recommendations.extend([
                    "💤 Considera revisar tu cena de anoche - evita carbohidratos simples",
                    "🚶‍♀️ Una caminata ligera después de cenar puede ayudar",
                    "💊 Verifica que estés tomando tu medicación según indicaciones"
                ])
            elif value < 70:
                recommendations.extend([
                    "🍎 Ten a la mano una colación con carbohidratos de rápida absorción",
                    "⏰ Revisa los horarios de tu medicación con tu médico"
                ])
        else:  # POST_MEAL
            if value > 180:
                recommendations.extend([
                    "🥗 Considera reducir las porciones de carbohidratos en tu próxima comida",
                    "🚶‍♀️ Una caminata de 10-15 minutos puede ayudar a bajar la glucosa",
                    "💧 Mantente bien hidratado con agua"
                ])
        
        # Trend-based recommendations
        if trend.get("status") == "increasing":
            recommendations.append("📊 Considera revisar tu plan alimentario con tu nutricionista")
        elif trend.get("status") == "decreasing":
            recommendations.append("🎯 ¡Excelente progreso! Continúa con tu rutina actual")
        
        return recommendations[:3]  # Limit to top 3 recommendations
