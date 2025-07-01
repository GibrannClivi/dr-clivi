"""
Obesity Agent - Specialized agent for obesity care workflows.
Based on analysis of exported Conversational Agents obesity flow.
"""

import logging
from typing import Any, Dict, List, Optional

from .base_agent import BaseCliviAgent, SessionContext, PatientContext, tool
from ..config import Config


class ObesityAgent(BaseCliviAgent):
    """
    Specialized agent for obesity care based on exported flows analysis.
    
    Implements obesity-specific flows:
    - obesityPlan main menu
    - Weight logging and body measurements
    - Workout signup categories
    - Nutrition hotline
    - Sports medicine appointments
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_agent_name(self) -> str:
        return self.config.obesity_agent.name
    
    def get_system_instructions(self) -> str:
        return f"""
        Eres Dr. Clivi, un asistente médico especializado en manejo de obesidad para la plataforma Dr. Clivi.

        OBJETIVO PRINCIPAL:
        Identificar con precisión las solicitudes del usuario y enrutarlas correctamente. Tu meta principal es 
        identificar con precisión la solicitud del usuario y enrutarla correctamente. Siempre responder al usuario 
        en español y luego terminar la sesión.

        FUNCIONES PRINCIPALES:
        1. GESTIÓN DE CITAS:
           - Agendar, reprogramar y cancelar citas con especialistas en obesidad
           - Medicina deportiva y endocrinología 
           - Confirmar citas programadas
           - Aclarar que las citas son virtuales (en línea)

        2. MEDICIONES CORPORALES:
           - Peso corporal y seguimiento de tendencias
           - Circunferencia de cintura, cadera y cuello
           - IMC y análisis de progreso
           - Reportes de mediciones y gráficas de tendencias

        3. NUTRICIÓN ESPECIALIZADA (según NUTRITION_AI_AGENT):
           - Planes de comidas personalizados para obesidad
           - Verificar alergias alimentarias antes de recomendar
           - Conocimiento extenso en manejo de obesidad a través de nutrición personalizada
           - Respuestas directas basadas en evidencia, específicas para obesidad
           - Evitar sugerir consultar con nutricionista (dar respuestas directas)

        4. EJERCICIO ESPECIALIZADO (según EXERCISE_AI_AGENT):
           - Planes de ejercicio enfocados en manejo de obesidad
           - Planes personalizados y consejos adaptados a las necesidades del usuario
           - Orientación directa basada en evidencia sobre ejercicio relacionado con obesidad
           - Verificar limitaciones físicas y problemas cardiovasculares antes de recomendar
           - Evitar sugerir consultar con especialistas (dar orientación directa)

        5. SUMINISTROS Y MEDICAMENTOS:
           - Estado de envíos de medicamentos para obesidad
           - Tutoriales de inyección (GLP-1, otros)
           - Seguimiento de tratamientos

        PROTOCOLOS DE SEGURIDAD:
        - Para nutrición: preguntar sobre alergias alimentarias
        - Para ejercicio: verificar limitaciones físicas y problemas cardiovasculares 
        - Para síntomas graves: derivar a emergencias
        - Para consultas médicas complejas: escalar a especialista humano

        RESPUESTAS ESTÁNDAR:
        - "Soy Dr. Clivi. Parece que quieres [acción]. Déjame ayudarte con eso."
        
        CASOS DE USO REALES:
        - "Quiero bajar de peso" → Plan personalizado de nutrición y ejercicio
        - "¿Cómo me inyecto Ozempic?" → Tutorial paso a paso para GLP-1
        - "Mi peso no baja" → Análisis de progreso y ajustes
        - "¿Qué puedo comer?" → Recomendaciones nutricionales específicas
        - "¿Qué ejercicio puedo hacer?" → Plan de actividad física seguro

        LIMITACIONES:
        - No soy médico, sino asistente digital especializado
        - Siempre verificar alergias y limitaciones antes de recomendar
        - En casos complejos, escalar a especialista humano
        """

    # ========================================
    # OBESITY AGENT TOOLS (from Dialogflow CX)
    # ========================================

    @tool
    async def SEND_MESSAGE(self, user_id: str, message: str, template_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Send message tool - equivalent to Dialogflow CX SEND_MESSAGE function.
        Used for sending structured messages to users about obesity management.
        """
        await self._log_activity_event(user_id, "SEND_MESSAGE_TOOL_USED", {
            "template_name": template_name,
            "message_length": len(message)
        })
        
        return {
            "action": "SEND_MESSAGE",
            "message": message,
            "template_name": template_name,
            "should_end_session": True
        }

    @tool
    async def ONBOARDING_SEND_LINK(self, user_id: str, link_type: str = "obesity_onboarding") -> Dict[str, Any]:
        """
        Send onboarding link tool - equivalent to Dialogflow CX ONBOARDING_SEND_LINK function.
        Used for obesity patient onboarding process.
        """
        await self._log_activity_event(user_id, "ONBOARDING_LINK_SENT", {
            "link_type": link_type
        })
        
        onboarding_links = {
            "obesity_onboarding": "https://drclivi.com/obesity/onboarding",
            "weight_tracking": "https://drclivi.com/obesity/weight-tracking",
            "nutrition_guide": "https://drclivi.com/obesity/nutrition",
            "exercise_plan": "https://drclivi.com/obesity/exercise"
        }
        
        return {
            "action": "SEND_LINK",
            "link": onboarding_links.get(link_type, onboarding_links["obesity_onboarding"]),
            "message": f"Aquí tienes el enlace para {link_type.replace('_', ' ')}",
            "should_end_session": True
        }

    @tool
    async def APPOINTMENT_CONFIRM(self, user_id: str, appointment_id: str, appointment_type: str = "obesity_specialist") -> Dict[str, Any]:
        """
        Appointment confirmation tool - equivalent to Dialogflow CX APPOINTMENT_CONFIRM function.
        Used for confirming obesity-related medical appointments.
        """
        await self._log_activity_event(user_id, "APPOINTMENT_CONFIRMED", {
            "appointment_id": appointment_id,
            "appointment_type": appointment_type
        })
        
        return {
            "action": "APPOINTMENT_CONFIRMED",
            "appointment_id": appointment_id,
            "confirmation_message": f"Tu cita de {appointment_type} ha sido confirmada. Te enviaremos el enlace de videollamada 30 minutos antes.",
            "next_steps": [
                "Recibirás un recordatorio 24 horas antes",
                "Prepara tu historial de peso reciente",
                "Ten a mano tu lista de medicamentos actuales"
            ],
            "should_end_session": True
        }

    @tool
    async def QUESTION_SET_LAST_MESSAGE(self, user_id: str, message: str, context_type: str = "obesity") -> Dict[str, Any]:
        """
        Set last message tool - equivalent to Dialogflow CX QUESTION_SET_LAST_MESSAGE function.
        Used for tracking the last message in obesity consultations.
        """
        context = self.get_session_context(user_id)
        context.last_message = message
        context.last_intent = f"{context_type}_question"
        
        await self._log_activity_event(user_id, "LAST_MESSAGE_SET", {
            "message_preview": message[:50] + "..." if len(message) > 50 else message,
            "context_type": context_type
        })
        
        return {
            "action": "MESSAGE_STORED",
            "stored_message": message,
            "context_updated": True
        }

    @tool
    async def PROPERTY_UPDATER(self, user_id: str, property_name: str, property_value: str) -> Dict[str, Any]:
        """
        Property updater tool - equivalent to Dialogflow CX PROPERTY_UPDATER function.
        Used for updating patient properties and session parameters for obesity management.
        """
        context = self.get_session_context(user_id)
        
        # Update patient context properties
        if hasattr(context, 'patient') and context.patient:
            if hasattr(context.patient, property_name):
                setattr(context.patient, property_name, property_value)
        
        await self._log_activity_event(user_id, "PROPERTY_UPDATED", {
            "property_name": property_name,
            "property_value": property_value
        })
        
        return {
            "action": "PROPERTY_UPDATED",
            "property_name": property_name,
            "property_value": property_value,
            "update_successful": True
        }

    @tool
    async def DR_CLIVI_HOW_IT_WORKS(self, user_id: str, topic: str = "obesity_program") -> Dict[str, Any]:
        """
        Dr. Clivi How It Works tool - equivalent to Dialogflow CX DR_CLIVI_HOW_IT_WORKS data store.
        Used for explaining how Dr. Clivi's obesity management program works.
        """
        await self._log_activity_event(user_id, "HOW_IT_WORKS_ACCESSED", {
            "topic": topic
        })
        
        explanations = {
            "obesity_program": """
            🏥 **Cómo funciona el programa de manejo de obesidad Dr. Clivi:**
            
            1. **Evaluación inicial**: Análisis completo de tu estado actual
            2. **Plan personalizado**: Nutrición y ejercicio adaptados a ti
            3. **Seguimiento continuo**: Monitoreo de peso y medidas corporales
            4. **Apoyo médico**: Acceso a especialistas cuando lo necesites
            5. **Medicamentos**: GLP-1 y otros tratamientos según indicación médica
            """,
            "weight_tracking": """
            📊 **Sistema de seguimiento de peso:**
            
            - Registro semanal de peso y medidas
            - Gráficas de progreso automáticas
            - Alertas de tendencias importantes
            - Reportes mensuales para tu médico
            """,
            "nutrition_plan": """
            🥗 **Plan nutricional personalizado:**
            
            - Menús adaptados a tus preferencias y alergias
            - Conteo de calorías y macronutrientes
            - Recetas saludables y fáciles de preparar
            - Ajustes según tu progreso
            """
        }
        
        return {
            "action": "EXPLANATION_PROVIDED",
            "topic": topic,
            "explanation": explanations.get(topic, explanations["obesity_program"]),
            "should_end_session": True
        }

    @tool
    async def Ask_OpenAI(self, user_id: str, query: str, context: str = "obesity_consultation") -> Dict[str, Any]:
        """
        Ask OpenAI tool - equivalent to Dialogflow CX Ask OpenAI function.
        Used for getting AI-powered responses for obesity-related queries.
        """
        # Use the existing generative AI tool from the config
        from ..tools import generative_ai
        
        ai_prompt = f"""
        Contexto: Consulta de manejo de obesidad para paciente
        Consulta del usuario: {query}
        
        Proporciona una respuesta médica informativa pero segura sobre manejo de obesidad,
        incluyendo aspectos nutricionales y de ejercicio cuando sea apropiado.
        Siempre verificar alergias alimentarias y limitaciones físicas.
        Recordar recomendar consulta médica profesional para casos complejos.
        """
        
        try:
            ai_response = await generative_ai.ask_generative_ai(
                user_id=user_id,
                prompt=ai_prompt,
                context={"agent_type": "obesity", "query_type": context}
            )
            
            return {
                "action": "AI_RESPONSE",
                "response": ai_response,
                "source": "generative_ai",
                "context": context
            }
        except Exception as e:
            self.logger.error(f"Error in Ask_OpenAI for user {user_id}: {str(e)}")
            return {
                "action": "AI_ERROR",
                "error": "No pude procesar tu consulta en este momento. ¿Te gustaría hablar con un especialista?",
                "fallback": True
            }

    # ========================================
    # OBESITY AGENT PROCESSING METHODS
    # ========================================

    async def process_obesity_query(self, user_id: str, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process obesity-related queries with comprehensive logic from Dialogflow CX flows.
        Covers all real scenarios: weight management, GLP-1, nutrition, exercise, appointments.
        """
        query_lower = query.lower().strip()
        
        self.logger.info(f"Processing obesity query for user {user_id}: {query}")
        
        # WEIGHT MEASUREMENTS - HIGH PRIORITY
        if any(keyword in query_lower for keyword in [
            "peso", "pesé", "mi peso", "peso corporal", "medición", "balanza", "báscula"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres enviarnos una medición. Puedo ayudarte.",
                "action": "SEND_MESSAGE",
                "template_name": "weight_measurement_catcher",
                "should_end_session": True
            }
        
        # GLP-1 MEDICATION MANAGEMENT
        if any(keyword in query_lower for keyword in [
            "ozempic", "trulicity", "glp-1", "glp1", "inyección", "medicamento", "medicina"
        ]):
            return {
                "response": "Te ayudo con tu medicamento GLP-1. ¿Necesitas información sobre cómo inyectarte o tienes dudas sobre efectos secundarios?",
                "action": "SEND_MESSAGE", 
                "template_name": "glp1_support",
                "should_end_session": True
            }
        
        # NUTRITION AND DIET QUERIES
        if any(keyword in query_lower for keyword in [
            "dieta", "comida", "alimentación", "qué comer", "menú", "nutrición", "calorías"
        ]):
            return {
                "response": "Puedo ayudarte con recomendaciones nutricionales para el manejo de peso. ¿Tienes alguna alergia alimentaria que deba considerar?",
                "action": "SEND_MESSAGE",
                "template_name": "nutrition_consultation", 
                "should_end_session": True
            }
        
        # EXERCISE AND PHYSICAL ACTIVITY
        if any(keyword in query_lower for keyword in [
            "ejercicio", "actividad física", "rutina", "entrenamiento", "deporte", "caminar"
        ]):
            return {
                "response": "Te puedo recomendar ejercicios seguros para manejo de peso. ¿Tienes alguna limitación física o problema cardiovascular?",
                "action": "SEND_MESSAGE",
                "template_name": "exercise_consultation",
                "should_end_session": True
            }
        
        # APPOINTMENT MANAGEMENT
        if any(keyword in query_lower for keyword in [
            "cita", "consulta", "doctor", "médico", "especialista", "agendar", "programar"
        ]):
            return {
                "response": "Te ayudo con tu cita médica. ¿Necesitas agendar, reprogramar o confirmar una cita con nuestros especialistas en obesidad?",
                "action": "SEND_MESSAGE",
                "template_name": "appointment_obesity",
                "should_end_session": True
            }
        
        # PROGRESS TRACKING
        if any(keyword in query_lower for keyword in [
            "progreso", "avance", "resultados", "bajé", "subí", "estancado", "no bajo"
        ]):
            return {
                "response": "Entiendo tu preocupación sobre el progreso. Revisemos tu seguimiento de peso y ajustemos el plan si es necesario.",
                "action": "SEND_MESSAGE",
                "template_name": "progress_review",
                "should_end_session": True
            }
        
        # SUPPLY MANAGEMENT
        if any(keyword in query_lower for keyword in [
            "envío", "pedido", "medicamento", "suministros", "entrega"
        ]):
            return {
                "response": "Me parece que quieres apoyo con tus envíos. Yo te puedo ayudar",
                "action": "SEND_MESSAGE",
                "template_name": "supplies_obesity_catcher",
                "should_end_session": True
            }
        
        # PHYSICAL SYMPTOMS - EMERGENCY PROTOCOL
        if any(keyword in query_lower for keyword in [
            "me siento mal", "síntomas", "dolor", "mareo", "nausea", "emergency"
        ]):
            return {
                "response": "Si sientes síntomas preocupantes, es importante que busques atención médica. ¿Es una situación de emergencia?",
                "action": "EMERGENCY_PROTOCOL",
                "should_end_session": True
            }
        
        # COMPLAINTS AND FEEDBACK
        if any(keyword in query_lower for keyword in [
            "queja", "problema", "mal servicio", "insatisfecho", "molesto"
        ]):
            return {
                "response": "Lamento que hayas tenido una mala experiencia. Tu opinión es importante para nosotros.",
                "action": "SEND_MESSAGE", 
                "template_name": "complaint_handler",
                "should_end_session": True
            }
        
        # GENERAL WEIGHT LOSS HELP
        if any(keyword in query_lower for keyword in [
            "bajar de peso", "perder peso", "adelgazar", "obesidad", "sobrepeso"
        ]):
            return {
                "response": "Estoy aquí para ayudarte con tu plan de manejo de peso. ¿Te interesa información sobre nutrición, ejercicio o nuestros tratamientos médicos?",
                "action": "SEND_MESSAGE",
                "template_name": "weight_loss_general",
                "should_end_session": True
            }
        
        # HELP AND SUPPORT
        if any(keyword in query_lower for keyword in [
            "ayuda", "support", "no entiendo", "como funciona", "información"
        ]):
            return {
                "response": "Por favor, utiliza el siguiente menú para mejor asistencia.",
                "action": "FLOW_REDIRECT",
                "flow_name": "helpDeskSubMenu",
                "should_end_session": True
            }
        
        # DEFAULT CASE - ROUTE TO HELP DESK
        return {
            "response": "Por favor, utiliza el siguiente menú para mejor asistencia.",
            "action": "FLOW_REDIRECT",
            "flow_name": "helpDeskSubMenu", 
            "should_end_session": True
        }

    async def main_menu_flow(self, user_id: str) -> Dict[str, Any]:
        """
        Main menu flow for obesity patients based on obesity agent analysis.
        
        Provides access to:
        - Weight and body measurements logging
        - GLP-1 medication tutorials and management
        - Nutritionist appointments
        - Educational content for weight management
        - Progress tracking and goals
        """
        context = self.get_session_context(user_id)
        patient = context.patient
        
        # Initialize or convert patient context
        if patient is None:
            from .base_agent import PatientContext
            patient = PatientContext(
                name_display="Paciente",
                plan="PRO",  # Default for testing
                plan_status="ACTIVE"
            )
            context.patient = patient
        elif isinstance(patient, dict):
            # Convert dict to PatientContext object
            from .base_agent import PatientContext
            patient = PatientContext(**patient)
            context.patient = patient
        
        await self._log_activity_event(user_id, "OBESITY_MAIN_MENU_ACCESS", {
            "plan": patient.plan,
            "plan_status": patient.plan_status
        })
        
        # TODO: Implement plan access validation if needed
        # plan_access = await self._check_plan_access(patient.plan, patient.plan_status)
        # if plan_access["action"] == "error":
        #     return plan_access
            
        # Build main menu options based on plan
        menu_options = []
        
        # Core obesity management options available to all plans
        menu_options.extend([
            {
                "id": "weight_logging",
                "title": "⚖️ Registrar Peso",
                "description": "Registra tu peso y medidas corporales",
                "action": "weight_measurements"
            },
            {
                "id": "appointments", 
                "title": "👩‍⚕️ Citas con Nutricionista",
                "description": "Agendar o gestionar citas nutricionales",
                "action": "nutritionist_appointment"
            },
            {
                "id": "nutrition_education",
                "title": "🥗 Educación Nutricional",
                "description": "Aprende sobre alimentación saludable",
                "action": "nutrition_education"
            }
        ])
        
        # Plan-specific options
        if patient.plan in ["PRO", "PLUS"]:
            menu_options.extend([
                {
                    "id": "glp1_management",
                    "title": "💉 Manejo de GLP-1", 
                    "description": "Tutoriales y seguimiento de medicamento",
                    "action": "glp1_tutorials"
                },
                {
                    "id": "progress_tracking",
                    "title": "📈 Seguimiento de Progreso",
                    "description": "Revisa tu progreso y establece metas",
                    "action": "progress_tracking"
                },
                {
                    "id": "meal_planning",
                    "title": "🍽️ Planificación de Comidas",
                    "description": "Planes de alimentación personalizados",
                    "action": "meal_planning"
                }
            ])
            
        if patient.plan == "PRO":
            menu_options.append({
                "id": "premium_coaching",
                "title": "⭐ Coaching Premium",
                "description": "Sesiones personalizadas con especialistas",
                "action": "premium_coaching"
            })
        
        return {
            "response": f"¡Hola {patient.name_display or 'Paciente'}! 👋\n\nBienvenido a tu asistente de manejo de peso Dr. Clivi.\n\n¿En qué puedo ayudarte hoy?",
            "action": "show_menu",
            "menu_type": "obesity_main",
            "options": menu_options,
            "plan_info": {
                "plan": patient.plan,
                "status": patient.plan_status,
                "features_available": len(menu_options)
            }
        }
