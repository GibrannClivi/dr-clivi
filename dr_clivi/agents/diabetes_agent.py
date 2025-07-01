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
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_agent_name(self) -> str:
        return self.config.diabetes_agent.name
    
    def get_system_instructions(self) -> str:
        return f"""
        Eres Dr. Clivi, un asistente médico especializado en diabetes tipo 2 para la plataforma Dr. Clivi.

        OBJETIVO PRINCIPAL:
        Identificar con precisión las solicitudes del usuario usando el parámetro `userRequest` y enrutarlas según las 
        instrucciones proporcionadas. Siempre terminar la sesión después de responder al usuario en español.

        FUNCIONES PRINCIPALES:
        1. GESTIÓN DE CITAS:
           - Agendar, reprogramar y cancelar citas con endocrinólogo
           - Confirmar citas programadas
           - Aclarar que las citas son virtuales (en línea)
           - Enviar enlaces de videollamada 30 minutos antes

        2. MEDICIONES DE GLUCOSA:
           - Registrar glucosa en ayunas (70-130 mg/dL normal)
           - Registrar glucosa postprandial (menos de 180 mg/dL normal)
           - Asesorar sobre horarios de medición
           - Interpretar resultados y recomendar acciones

        3. MANEJO DE MEDICAMENTOS:
           - GLP-1 (Ozempic, Trulicity): Instrucciones de inyección
           - Metformina: Horarios y efectos secundarios
           - Insulina: Tipos, dosificación y técnicas

        4. SUMINISTROS MÉDICOS:
           - Glucómetros: Configuración y uso
           - Tiras reactivas: Almacenamiento y caducidad
           - Lancetas: Técnica correcta de punción

        5. EDUCACIÓN DIABETOLÓGICA:
           - Conteo de carbohidratos
           - Ejercicio y diabetes
           - Manejo de hipoglucemia
           - Cuidado de pies diabéticos

        CASOS DE USO REALES:
        - "Mi glucosa salió en 200" → Evaluar urgencia, recomendar acciones
        - "¿Cómo me inyecto Ozempic?" → Tutorial paso a paso
        - "Se me acabaron las tiras" → Gestionar pedido de suministros
        - "Tengo cita mañana" → Confirmar y enviar enlace

        PROTOCOLOS DE EMERGENCIA:
        - Glucosa >300 mg/dL: Atención inmediata
        - Síntomas de cetoacidosis: Llamar 911
        - Hipoglucemia severa: Protocolo de emergencia

        LIMITACIONES:
        - No soy médico, sino asistente digital
        - Siempre recomendar consulta médica para cambios de tratamiento
        - En emergencias, derivar a servicios de urgencia
        """

    # ========================================
    # DIABETES AGENT TOOLS (from Dialogflow CX)
    # ========================================

    @tool
    async def SEND_MESSAGE(self, user_id: str, message: str, template_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Send message tool - equivalent to Dialogflow CX SEND_MESSAGE function.
        Used for sending structured messages to users.
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
    async def ONBOARDING_SEND_LINK(self, user_id: str, link_type: str = "diabetes_onboarding") -> Dict[str, Any]:
        """
        Send onboarding link tool - equivalent to Dialogflow CX ONBOARDING_SEND_LINK function.
        Used for diabetes patient onboarding process.
        """
        await self._log_activity_event(user_id, "ONBOARDING_LINK_SENT", {
            "link_type": link_type
        })
        
        onboarding_links = {
            "diabetes_onboarding": "https://drclivi.com/diabetes/onboarding",
            "glucose_tutorial": "https://drclivi.com/diabetes/glucose-tutorial",
            "medication_guide": "https://drclivi.com/diabetes/medications"
        }
        
        return {
            "action": "SEND_LINK",
            "link": onboarding_links.get(link_type, onboarding_links["diabetes_onboarding"]),
            "message": f"Aquí tienes el enlace para {link_type.replace('_', ' ')}",
            "should_end_session": True
        }

    @tool
    async def APPOINTMENT_CONFIRM(self, user_id: str, appointment_id: str, appointment_type: str = "endocrinology") -> Dict[str, Any]:
        """
        Appointment confirmation tool - equivalent to Dialogflow CX APPOINTMENT_CONFIRM function.
        Used for confirming diabetes-related medical appointments.
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
                "Prepara tu lista de medicamentos actuales",
                "Ten a mano tu glucómetro para la consulta"
            ],
            "should_end_session": True
        }

    @tool
    async def QUESTION_SET_LAST_MESSAGE(self, user_id: str, message: str, context_type: str = "diabetes") -> Dict[str, Any]:
        """
        Set last message tool - equivalent to Dialogflow CX QUESTION_SET_LAST_MESSAGE function.
        Used for tracking the last message in diabetes consultations.
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
        Used for updating patient properties and session parameters.
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
    async def Ask_OpenAI(self, user_id: str, query: str, context: str = "diabetes_consultation") -> Dict[str, Any]:
        """
        Ask OpenAI tool - equivalent to Dialogflow CX Ask OpenAI function.
        Used for getting AI-powered responses for diabetes-related queries.
        """
        # Use the existing generative AI tool from the config
        from ..tools import generative_ai
        
        ai_prompt = f"""
        Contexto: Consulta de diabetes para paciente
        Consulta del usuario: {query}
        
        Proporciona una respuesta médica informativa pero segura sobre diabetes,
        recordando siempre recomendar consulta médica profesional.
        """
        
        try:
            ai_response = await generative_ai.ask_generative_ai(
                user_id=user_id,
                prompt=ai_prompt,
                context={"agent_type": "diabetes", "query_type": context}
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

    async def process_diabetes_query(self, user_request: str, user_id: str, 
                                    session_context: SessionContext, 
                                    patient_context: PatientContext) -> Dict[str, Any]:
        """
        Process diabetes-related queries with full scenario coverage from original Dialogflow CX flows.
        Implements all scenarios from MASTER_AGENT and EXERCISE_AI_AGENT instructions.
        """
        self.logger.info(f"Processing diabetes query for user {user_id}: {user_request}")
        
        # Set session context
        context = self.get_session_context(user_id)
        if session_context:
            # Update with provided session context data
            context.current_flow = session_context.current_flow or "diabetes_specialist"
            context.current_page = session_context.current_page or "diabetes_consultation"
            context.patient = patient_context or session_context.patient
        elif patient_context:
            context.patient = patient_context
        
        # Normalize query for pattern matching
        query_lower = user_request.lower().strip()
        
        # ONBOARDING PROCESS
        if any(keyword in query_lower for keyword in [
            "onboarding", "iniciar tratamiento", "validar datos", "comenzar", "empezar"
        ]):
            return {
                "response": "Soy Dr. Clivi. Parece que quieres iniciar con tu tratamiento. Déjame ayudarte con eso.",
                "action": "CALL_FUNCTION",
                "function_name": "ONBOARDING_SEND_LINK",
                "should_end_session": True
            }
        
        # APPOINTMENT BOOKING
        if any(keyword in query_lower for keyword in [
            "cita", "agendar", "consulta", "appointment", "médico", "endocrinólogo"
        ]):
            return {
                "response": "Soy Dr. Clivi. Parece que quieres agendar una cita. Es correcto?",
                "action": "SEND_MESSAGE", 
                "template_name": "booking_catcher_ai_menu",
                "should_end_session": True,
                "followup_expected": "booking_confirmation"
            }
        
        # APPOINTMENT TYPE CLARIFICATION
        if any(keyword in query_lower for keyword in [
            "en línea", "presencial", "hospital", "virtual", "online", "videollamada"
        ]):
            return {
                "response": "Tu cita es en línea. Te enviaremos la liga 30 minutos antes.",
                "action": "SEND_MESSAGE",
                "template_name": "px_appt_list", 
                "should_end_session": True
            }
        
        # APPOINTMENT RESCHEDULING
        if any(keyword in query_lower for keyword in [
            "reprogramar", "reagendar", "cambiar cita", "mover cita", "reschedule"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres reprogramar una cita. Puedo ayudarte.",
                "action": "SEND_MESSAGE",
                "template_name": "reschedule_appt_ai_menu",
                "should_end_session": True
            }
        
        # APPOINTMENT CANCELLATION
        if any(keyword in query_lower for keyword in [
            "cancelar cita", "cancel", "anular cita"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres cancelar una cita. Puedo ayudarte.",
                "action": "SEND_MESSAGE", 
                "template_name": "cancel_appt_catcher_ai",
                "should_end_session": True
            }
        
        # APPOINTMENT CONFIRMATION
        if any(keyword in query_lower for keyword in [
            "confirmar cita", "confirmación", "confirm"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres confirmar tu cita. Puedo ayudarte.",
                "action": "CALL_FUNCTION",
                "function_name": "APPOINTMENT_CONFIRM",
                "should_end_session": True
            }
        
        # GLUCOSE MEASUREMENTS (NUMBERS ONLY)
        if query_lower.replace(".", "").isdigit() or any(char.isdigit() for char in query_lower):
            return {
                "response": "Soy tu Dr. Clivi, creo que quieres enviar una medida. Déjame ayudarte con eso.",
                "action": "SEND_MESSAGE",
                "template_name": "px_sends_numbers_ai_no_context",
                "should_end_session": True
            }
        
        # BODY MEASUREMENTS - SPECIFIC QUERIES
        if any(keyword in query_lower for keyword in [
            "medición", "medir", "glucosa", "peso", "cintura", "cadera", "measurement"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres enviarnos una medición. Puedo ayudarte.",
                "action": "SEND_MESSAGE",
                "template_name": "px_sends_numbers_ai_no_context", 
                "should_end_session": True
            }
        
        # HOW TO TAKE MEASUREMENTS
        if any(keyword in query_lower for keyword in [
            "cómo medir", "how to", "tutorial medición", "instrucciones"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres instrucciones para mediciones. Puedo ayudarte.",
                "action": "SEND_MESSAGE",
                "template_name": "px_sends_numbers_ai_no_context",
                "should_end_session": True
            }
        
        # LAB RESULTS / MEDICAL FILES
        if any(keyword in query_lower for keyword in [
            "resultados", "laboratorio", "recetas", "prescription", "archivos", "estudios"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres ver los archivos disponibles. Puedo ayudarte.",
                "action": "SEND_MESSAGE",
                "template_name": "last_ai_file_available",
                "should_end_session": True
            }
        
        # VIDEO CALL PLATFORM QUESTIONS
        if any(keyword in query_lower for keyword in [
            "aplicación", "app", "videollamada", "plataforma", "software"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres actualizar tu aplicación. Puedo ayudarte.",
                "action": "SEND_MESSAGE",
                "template_name": "update_videocall",
                "should_end_session": True
            }
        
        # EXERCISE QUERIES - WITH SAFETY PROTOCOL
        if any(keyword in query_lower for keyword in [
            "ejercicio", "exercise", "actividad física", "rutina", "entrenamiento"
        ]):
            return {
                "response": "Por tu propia seguridad, antes de responderte necesitamos asegurarnos con un par de preguntas. Gracias.",
                "action": "EXERCISE_SAFETY_CHECK",
                "questions": [
                    "¿Tienes alguna limitación física como problemas articulares?",
                    "¿Has tenido problemas cardiovasculares como dolor en el pecho, falta de aire o mareos durante o después de actividad física?"
                ],
                "context": "You are an AI exercise specialist focused on managing type 2 diabetes. Provide personalized exercise plans and evidence-based advice to help control blood sugar levels.",
                "should_end_session": False
            }
        
        # COMPLAINTS ABOUT SERVICE
        if any(keyword in query_lower for keyword in [
            "queja", "mal servicio", "problema", "complaint", "insatisfecho"
        ]):
            return {
                "response": "Lamento mucho tu mala experiencia. Estoy escalando tu caso con un agente de soporte. Dame unos momentos. Por favor.",
                "action": "CALL_FUNCTION", 
                "function_name": "QUESTION_SET_LAST_MESSAGE",
                "parameters": {
                    "sendToHelpdesk": True,
                    "isKnownQuestion": True
                },
                "should_end_session": True
            }
        
        # GENERAL QUESTIONS
        if any(keyword in query_lower for keyword in [
            "pregunta", "duda", "consulta", "question", "ayuda"
        ]):
            return {
                "response": "Hola, con gusto te puedo ayudar con el envío de una pregunta a nuestro equipo",
                "action": "SEND_MESSAGE",
                "template_name": "master_general_question_ai",
                "should_end_session": True
            }
        
        # INVOICING QUERIES
        if any(keyword in query_lower for keyword in [
            "factura", "facturación", "invoice", "billing", "pago"
        ]):
            return {
                "response": "Soy Dr. Clivi, me parece que quieres apoyo con tus facturas. Yo te puedo ayudar.",
                "action": "SEND_MESSAGE",
                "template_name": "invoicing_ai_catcher",
                "should_end_session": True
            }
        
        # PAYMENT QUERIES
        if any(keyword in query_lower for keyword in [
            "pago", "payment", "cobro", "tarjeta"
        ]):
            return {
                "response": "Hola, me parece que quieres apoyo con tus pagos. Yo te puedo ayudar.",
                "action": "SEND_MESSAGE",
                "template_name": "payment_ai_catcher", 
                "should_end_session": True
            }
        
        # SHIPMENT STATUS
        if any(keyword in query_lower for keyword in [
            "envío", "shipment", "glucómetro", "tiras", "medicamento", "supplies"
        ]):
            return {
                "response": "Me parece que quieres apoyo con tus envíos. Yo te puedo ayudar",
                "action": "SEND_MESSAGE",
                "template_name": "supplies_ai_catcher",
                "should_end_session": True
            }
        
        # PHYSICAL SYMPTOMS - EMERGENCY PROTOCOL
        if any(keyword in query_lower for keyword in [
            "me siento mal", "síntomas", "dolor", "mareo", "nausea", "emergency"
        ]):
            return {
                "response": "Comprendo tu preocupación. Te voy a conectar con nuestro servicio de especialistas.",
                "action": "SEND_MESSAGE",
                "template_name": "call_specialists_ai",
                "should_end_session": True
            }
        
        # MENTAL HEALTH CONCERNS
        if any(keyword in query_lower for keyword in [
            "depresión", "ansiedad", "mental", "psychological", "psicológico"
        ]):
            return {
                "response": "Tu bienestar mental es importante. Te conectaré con nuestro servicio de apoyo psicológico.",
                "action": "SEND_MESSAGE", 
                "template_name": "psycho_emergency_call_ai_requested",
                "should_end_session": True
            }
        
        # GRATITUDE EXPRESSIONS
        if any(keyword in query_lower for keyword in [
            "gracias", "thank", "thanks", "agradezco"
        ]):
            return {
                "response": "Gracias a ti",
                "action": "END_SESSION",
                "should_end_session": True
            }
        
        # REFERRALS
        if any(keyword in query_lower for keyword in [
            "referir", "recomendar", "referral", "amigo"
        ]):
            return {
                "response": "Soy Dr. Clivi, parece que quieres referir. Es muy sencillo compártenos su contacto por este WhatsApp.",
                "action": "END_SESSION",
                "should_end_session": True
            }
        
        # EMOJIS IN MESSAGE
        import re
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001F1FF]"
        )
        if emoji_pattern.search(user_request):
            return {
                "response": "Soy Dr. Clivi, solo para estar seguro. Por favor, utiliza el siguiente menú. Gracias",
                "action": "SEND_MESSAGE",
                "template_name": "master_general_question_ai",
                "should_end_session": True
            }
        
        # SUBSCRIPTION CANCELLATION
        if any(keyword in query_lower for keyword in [
            "cancelar suscripción", "cancel subscription", "dar de baja", "discontinuar"
        ]):
            return {
                "response": "Lamentamos tu experiencia. Estamos escalando tu caso con alta prioridad. Un agente de soporte te contactará.",
                "action": "CALL_FUNCTION",
                "function_name": "QUESTION_SET_LAST_MESSAGE",
                "parameters": {
                    "category": "PAGOS",
                    "sendToHelpdesk": True,
                    "isKnownQuestion": True
                },
                "should_end_session": True
            }
        
        # SPECIFIC MEDICAL QUESTIONS - ROUTE TO SPECIALIST
        if any(keyword in query_lower for keyword in [
            "diabetes", "glucosa alta", "insulina", "hemoglobina", "a1c", "complications"
        ]):
            return {
                "response": "Lo lamento, no entendí tu petición voy a escalar tu caso con un especialista. Gracias por tu paciencia.",
                "action": "CALL_FUNCTION", 
                "function_name": "QUESTION_SET_LAST_MESSAGE",
                "parameters": {
                    "category": "DIABETES",
                    "sendToHelpdesk": True,
                    "isKnownQuestion": True
                },
                "should_end_session": True
            }
        
        # SINGLE WORD RESPONSES
        if len(query_lower.split()) == 1 and query_lower.isalpha():
            return {
                "response": "Por favor utiliza el siguiente menú para mejor asistencia.",
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
        Main menu flow for diabetes patients based on diabetesPlans/mainMenu.json analysis.
        
        Provides access to:
        - Glucose measurements (fasting and post-meal)
        - Medication tutorials 
        - Supplies management
        - Endocrinology appointments
        - Educational content
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
        
        await self._log_activity_event(user_id, "DIABETES_MAIN_MENU_ACCESS", {
            "plan": patient.plan,
            "plan_status": patient.plan_status
        })
        
        # TODO: Implement plan access validation if needed
        # plan_access = await self._check_plan_access(patient.plan, patient.plan_status)
        # if plan_access["action"] == "error":
        #     return plan_access
            
        # Build main menu options based on plan
        menu_options = []
        
        # Core diabetes options available to all plans
        menu_options.extend([
            {
                "id": "glucose_logging",
                "title": "📊 Registrar Glucosa",
                "description": "Registra tus mediciones de glucosa",
                "action": "measurements_menu"
            },
            {
                "id": "appointments", 
                "title": "👩‍⚕️ Citas Médicas",
                "description": "Agendar o gestionar citas con endocrinólogo",
                "action": "appointment_flow"
            },
            {
                "id": "education",
                "title": "📚 Educación",
                "description": "Aprende sobre el manejo de la diabetes",
                "action": "education_menu"
            }
        ])
        
        # Plan-specific options
        if patient.plan in ["PRO", "PLUS"]:
            menu_options.extend([
                {
                    "id": "medication_tutorials",
                    "title": "💊 Tutoriales de Medicamentos", 
                    "description": "Aprende a usar GLP-1 y otros medicamentos",
                    "action": "medication_tutorials"
                },
                {
                    "id": "supplies",
                    "title": "🔬 Suministros",
                    "description": "Gestiona glucómetro y tiras reactivas",
                    "action": "supplies_management"
                }
            ])
            
        if patient.plan == "PRO":
            menu_options.append({
                "id": "premium_support",
                "title": "⭐ Soporte Premium",
                "description": "Acceso prioritario a especialistas",
                "action": "premium_support"
            })
        
        return {
            "response": f"¡Hola {patient.name_display or 'Paciente'}! 👋\n\nBienvenido a tu asistente de diabetes Dr. Clivi.\n\n¿En qué puedo ayudarte hoy?",
            "action": "show_menu",
            "menu_type": "diabetes_main",
            "options": menu_options,
            "plan_info": {
                "plan": patient.plan,
                "status": patient.plan_status,
                "features_available": len(menu_options)
            }
        }
